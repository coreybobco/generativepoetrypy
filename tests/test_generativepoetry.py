import itertools
import re
import unittest
from unittest.mock import patch
from generativepoetry.lexigen import *
from generativepoetry.pdf import *
from generativepoetry.poemgen import *
from generativepoetry.utils import *


class TestUtils(unittest.TestCase):

    def test_setup_spellchecker(self):
        self.assertIsNotNone(setup_spellchecker())

    def test_get_random_color(self):
        for i in range(4):
            rgb = get_random_color()
            red_over = rgb[0] >= .85
            green_over = rgb[1] >= .85
            blue_over = rgb[2] >= .85
            self.assertFalse(red_over and green_over) or (red_over and blue_over) or (green_over and blue_over)
        for i in range(4):
            threshold = .25
            rgb = get_random_color()
            red_over = rgb[0] >= threshold
            green_over = rgb[1] >= threshold
            blue_over = rgb[2] >= threshold
            self.assertFalse(red_over and green_over) or (red_over and blue_over) or (green_over and blue_over)

    def test_get_input_words(self):
        test_input = 'trout mask replica'
        with patch('builtins.input', return_value=test_input):
            self.assertEqual(get_input_words(), ['trout', 'mask', 'replica'])
        test_input = 'fish,paperclip,atom,benign'
        with patch('builtins.input', return_value=test_input):
            self.assertEqual(get_input_words(), ['fish', 'paperclip', 'atom', 'benign'])
        test_input = 'fish, paperclip, atom, benign'
        with patch('builtins.input', return_value=test_input):
            self.assertEqual(get_input_words(), ['fish', 'paperclip', 'atom', 'benign'])

    def test_validate_str(self):
        self.assertRaises(ValueError, lambda: validate_str(2))
        self.assertRaises(ValueError, lambda: validate_str(2.5))
        self.assertRaises(ValueError, lambda: validate_str(False))
        self.assertRaises(ValueError, lambda: validate_str(None))
        validate_str('lingo')

    def test_validate_str_list(self):
        self.assertRaises(ValueError, lambda: validate_str_list(2))
        self.assertRaises(ValueError, lambda: validate_str_list(2.5))
        self.assertRaises(ValueError, lambda: validate_str_list(False))
        self.assertRaises(ValueError, lambda: validate_str_list(None))
        self.assertRaises(ValueError, lambda: validate_str_list('not a list'))
        self.assertRaises(ValueError, lambda: validate_str_list(['a', 'b', None]))
        validate_str_list(['a', 'b', 'c'])

    def test_validate_str_or_list_of_str(self):
        self.assertRaises(ValueError, lambda: validate_str_list(2))
        self.assertRaises(ValueError, lambda: validate_str_list(2.5))
        self.assertRaises(ValueError, lambda: validate_str_list(False))
        self.assertRaises(ValueError, lambda: validate_str_list(None))
        self.assertRaises(ValueError, lambda: validate_str_list(['a', 'b', None]))
        validate_str('deciduous')
        validate_str_list(['anodyne', 'bolo', 'cdrkssdjak'])

    def test_has_invalid_characters(self):
        self.assertTrue(has_invalid_characters('gh0st'))
        self.assertTrue(has_invalid_characters('compound word'))
        self.assertTrue(has_invalid_characters('compound-word'))
        self.assertTrue(has_invalid_characters("apostrophe'"))
        self.assertFalse(has_invalid_characters('espousal'))

    def test_too_similar(self):
        self.assertRaises(ValueError, lambda: too_similar(None, 25.2))
        self.assertRaises(ValueError, lambda: too_similar('string', 25))
        self.assertRaises(ValueError, lambda: too_similar(list(), 'beans'))
        self.assertFalse(too_similar('self', 'other'))
        self.assertTrue(too_similar('dog', 'dog'))
        self.assertTrue(too_similar('dog', 'dogs'))
        self.assertTrue(too_similar('dogs', 'dog'))
        self.assertTrue(too_similar('spherical', 'spherically'))
        self.assertTrue(too_similar('spherically', 'spherical'))
        self.assertTrue(too_similar('riposte', 'riposted'))
        self.assertTrue(too_similar('riposted', 'riposte'))
        self.assertTrue(too_similar('riposte', ['dogs', 'mushroom', 'riposted']))
        self.assertFalse(too_similar('riposte', ['dogs', 'mushroom', 'quails']))
        self.assertTrue(too_similar('thee', 'the'))
        self.assertTrue(too_similar('thee', 'the'))

    def test_filter_word(self):
        self.assertFalse(filter_word('an'))
        self.assertFalse(filter_word('nonexistentword'))
        self.assertFalse(filter_word('errantry'))  # 1.51e-08 so below threshold
        self.assertTrue(filter_word('crepuscular'))  # 7.41e-08 so OK
        self.assertTrue(filter_word('puppy'))
        self.assertFalse(filter_word('thew'))  # from the annoying words list

    def test_filter_word_list(self):
        word_list = ['the', 'crepuscular', 'dogs']
        self.assertEqual(filter_word_list(word_list), word_list) ## All spelled correctly
        word_list = ['the', 'underworld', 'gh0st', 'errantry', 'an']
        valid_words = ['the', 'underworld']
        self.assertEqual(filter_word_list(word_list), valid_words)
        word_list = ['araignment', 'arraignment', 'dynosaur', 'dinosaur']
        correctly_spelled_word_list = ['arraignment', 'dinosaur']
        self.assertEqual(filter_word_list(word_list), correctly_spelled_word_list)
        exclude_words = ['diamond', 'dinosaur']
        self.assertEqual(filter_word_list(word_list, exclude_words=exclude_words), ['arraignment'])

    def test_sort_by_rarity(self):
        unsorted_words = ['cat', 'catabasis', 'hue', 'corncob',  'the', 'Catalan', 'errant']
        correctly_sorted_words = ['catabasis', 'corncob', 'errant', 'hue', 'Catalan', 'cat', 'the']
        self.assertEqual(sort_by_rarity(unsorted_words), correctly_sorted_words)


class TestLexigen(unittest.TestCase):
    def test_rhymes(self):
        self.assertEqual(rhymes('metamorphosis'), [])
        rhymes_with_clouds = ['crowds', 'shrouds']
        results = rhymes('clouds')
        self.assertEqual(sorted(results), rhymes_with_clouds)
        rhymes_with_sprouting = ['doubting', 'flouting', 'grouting', 'outing', 'pouting', 'rerouting', 'routing',
                                 'scouting', 'shouting', 'spouting', 'touting']
        self.assertEqual(sorted(rhymes('sprouting', sample_size=None)), rhymes_with_sprouting)
        results = rhymes('sprouting')
        self.assertNotIn('sprouting', results)
        self.assertEqual(sorted(results), rhymes_with_sprouting)
        results = rhymes('sprouting', sample_size=6)
        self.assertEqual(len(results), 6)
        self.assertTrue(set(rhymes_with_sprouting).issuperset(set(results)))
        rhymes_with_either = sorted(rhymes_with_clouds + rhymes_with_sprouting)
        self.assertEqual(sorted(rhymes(['sprouting', 'clouds'], sample_size=None)), rhymes_with_either)
        results = rhymes(['clouds', 'sprouting'], sample_size=6)
        self.assertEqual(len(results), 6)
        self.assertTrue(set(rhymes_with_either).issuperset(set(results)))

    def test_rhyme(self):
        self.assertIsNone(rhyme('metamorphosis'))
        self.assertIn(rhyme('sprouting'), rhymes('sprouting'))

    def test_extract_sample(self):
        self.assertEqual(extract_sample([], sample_size=100), [])
        self.assertEqual(extract_sample(['a'], sample_size=100), ['a'])
        self.assertEqual(sorted(extract_sample(['a','b','c'], sample_size=3)), ['a','b','c'])
        sample = extract_sample(['a','b','c','d','e','f'], sample_size=4)
        self.assertNotEqual(sorted(sample), ['a','b','c','d','e','f'])
        self.assertTrue(set(['a','b','c','d','e','f']).issuperset(set(sample)))

    def test_similar_sounding_words(self):
        similar_sounding_to_homonym_words = ['hastening', 'heightening', 'hominid', 'hominy', 'homonyms', 'summoning',
                                             'synonym']
        self.assertEqual(sorted(similar_sounding_words('homonym', sample_size=None)), similar_sounding_to_homonym_words)
        results = similar_sounding_words('homonym')
        self.assertEqual(len(results), 6)
        self.assertTrue(set(similar_sounding_to_homonym_words).issuperset(set(results)))
        similar_sounding_to_ennui_words = ['anew', 'any', 'emcee', 'empty']
        all_similar_sounding_words = sorted(similar_sounding_to_homonym_words + similar_sounding_to_ennui_words)
        self.assertEqual(sorted(similar_sounding_words(['homonym', 'ennui'], sample_size=None)),
                         all_similar_sounding_words)
        results = similar_sounding_words(['homonym', 'ennui'])
        self.assertEqual(len(results), 6)
        self.assertTrue(set(all_similar_sounding_words).issuperset(set(results)))

    def test_similar_sounding_word(self):
        self.assertIsNone(similar_sounding_word('voodoo'))
        all_similar_sounding_words = ['hastening', 'heightening', 'hominid', 'hominy', 'homonym', 'homonyms',
                                      'summoning', 'synonym']  # Using this to save API call in test
        self.assertIn(similar_sounding_word('homonym'), all_similar_sounding_words)

    def test_similar_meaning_words(self):
        self.assertEqual(similar_meaning_words('nonexistentword'), [])
        similar_meaning_to_vampire_words = ['bats', 'bloodsucker', 'clan', 'demon', 'ghoul', 'james', 'kind', 'lamia',
                                            'lycanthrope', 'lycanthropy', 'shane', 'shapeshifter', 'succubus', 'undead',
                                            'vamp', 'vampirism', 'werewolf', 'witch', 'wolfman', 'zombie']
        results = similar_meaning_words('vampire', sample_size=None)
        self.assertEqual(len(results), 20)
        self.assertEqual(sorted(results), similar_meaning_to_vampire_words)
        results = similar_meaning_words('vampire', sample_size=None, datamuse_api_max=None)
        self.assertGreater(len(results), 20)
        self.assertTrue(set(results).issuperset(set(similar_meaning_to_vampire_words)))
        results = similar_meaning_words('vampire', sample_size=6)
        self.assertEqual(len(results), 6)
        self.assertTrue(set(similar_meaning_to_vampire_words).issuperset(set(results)))
        similar_meaning_to_gothic = ['goth', 'hard', 'eldritch', 'unusual', 'spooky', 'rococo', 'minimalist', 'folky',
                                     'lovecraftian', 'strange', 'baroque', 'creepy', 'medieval', 'mediaeval']
        similar_meaning_to_either = sorted(similar_meaning_to_vampire_words + similar_meaning_to_gothic)
        self.assertEqual(sorted(similar_meaning_words(['vampire', 'gothic'], sample_size=None)),
                         similar_meaning_to_either)
        results = similar_meaning_words(['vampire', 'gothic'])
        self.assertEqual(len(results), 6)
        self.assertTrue(set(similar_meaning_to_either).issuperset(set(results)))

    def test_similar_meaning_word(self):
        self.assertIsNone(similar_meaning_word('nonexistentword'))
        similar_meaning_to_vampire_words = ['bats', 'bloodsucker', 'clan', 'demon', 'ghoul', 'james', 'kind', 'lamia',
                                            'lycanthrope', 'lycanthropy', 'shane', 'shapeshifter', 'succubus', 'undead',
                                            'vamp', 'vampirism', 'werewolf', 'witch', 'wolfman', 'zombie']
        self.assertIn(similar_meaning_word('vampire'), similar_meaning_to_vampire_words)

    def test_contextually_linked_words(self):
        self.assertEqual(contextually_linked_words('nonexistentword'), [])
        contextually_linked_to_metamorphosis = ['budding', 'cocoon', 'duff', 'frogs', 'gills', 'hatching', 'juvenile',
                                                'kafka', 'lamprey', 'larva', 'metamorphose', 'narcissus', 'nymph',
                                                'polyp', 'polyps', 'pupa', 'pupal', 'salamander', 'starfish', 'tadpole']
        results = contextually_linked_words('metamorphosis', sample_size=None)
        self.assertEqual(len(results), 20)
        self.assertEqual(sorted(results), contextually_linked_to_metamorphosis)
        results = contextually_linked_words('metamorphosis', sample_size=None, datamuse_api_max=None)
        self.assertGreater(len(results), 20)
        self.assertTrue(set(results).issuperset(set(contextually_linked_to_metamorphosis)))
        results = contextually_linked_words('metamorphosis', sample_size=6)
        self.assertEqual(len(results), 6)
        self.assertTrue(set(contextually_linked_to_metamorphosis).issuperset(set(results)))
        contextually_linked_to_crepuscular = ['foraging', 'dusk', 'habits', 'twilight', 'diurnal', 'rays', 'dens',
                                              'forage', 'insects', 'nocturnal', 'overcast', 'predation', 'skipper',
                                              'sunset', 'moths', 'dawn', 'rodents', 'daylight', 'mating']
        contextually_linked_to_either = sorted(contextually_linked_to_crepuscular +
                                               contextually_linked_to_metamorphosis)
        self.assertEqual(sorted(contextually_linked_words(['crepuscular', 'metamorphosis'], sample_size=None)),
                         contextually_linked_to_either)
        results = contextually_linked_words(['crepuscular', 'metamorphosis'])
        self.assertEqual(len(results), 6)
        self.assertTrue(set(contextually_linked_to_either).issuperset(set(results)))

    def test_contextually_linked_word(self):
        self.assertIsNone(contextually_linked_word('nonexistentword'))
        contextually_linked_to_metamorphosis = ['kafka', 'lamprey', 'larva', 'metamorphose', 'narcissus', 'polyp',
                                                'polyps', 'pupa', 'pupal', 'tadpole']
        self.assertIn(contextually_linked_word('metamorphosis'), contextually_linked_to_metamorphosis)

    def test_frequently_following_words(self):
        self.assertEqual(frequently_following_words('nonexistentword'), [])
        frequently_following_magic = ['about', 'against', 'among', 'and', 'angle', 'are', 'art', 'arts', 'box',
                                      'bullet', 'bullets', 'but', 'can', 'carpet', 'charm', 'charms', 'circle', 'city',
                                      'could', 'flute', 'for', 'formula', 'formulas', 'from', 'had', 'has', 'influence',
                                      'into', 'johnson', 'key', 'kingdom', 'lamp', 'lantern', 'marker', 'markers',
                                      'may', 'mirror', 'moment', 'mountain', 'name', 'number', 'numbers', 'potion',
                                      'power', 'powers', 'realism', 'ring', 'rites', 'school', 'show',  'spell',
                                      'spells', 'square', 'squares', 'sword', 'than', 'that', 'the', 'touch', 'trick',
                                      'tricks', 'wand', 'was', 'were', 'when', 'which', 'will', 'with', 'word', 'words',
                                      'world', 'would']
        results = frequently_following_words('magic', sample_size=None)
        self.assertEqual(sorted(results), frequently_following_magic)
        results = frequently_following_words('magic', sample_size=None, datamuse_api_max=None)
        self.assertGreater(len(results), 20)
        self.assertTrue(set(results).issuperset(set(frequently_following_magic)))
        results = frequently_following_words('magic', sample_size=6)
        self.assertEqual(len(results), 6)
        self.assertTrue(set(frequently_following_magic).issuperset(set(results)))
        frequently_following_Dadaist = ['activities', 'and', 'art', 'artist', 'artists', 'collage', 'collages',
                                        'experiments', 'group', 'hugo', 'influence', 'kurt', 'manifesto', 'marcel',
                                        'movement', 'nihilism', 'painter', 'performance', 'play', 'poem', 'poems',
                                        'poet', 'poetry', 'poets', 'raoul', 'review', 'spirit', 'tradition', 'tristan',
                                        'who', 'work', 'works']
        ff_either = sorted(frequently_following_magic + [word for word in frequently_following_Dadaist
                                                         if word not in frequently_following_magic])
        self.assertEqual(sorted(frequently_following_words(['magic', 'Dadaist'], sample_size=None)), ff_either)
        results = frequently_following_words(['magic', 'Dadaist'])
        self.assertEqual(len(results), 8)
        self.assertTrue(set(ff_either).issuperset(set(results)))

    def test_frequently_following_word(self):
        self.assertIsNone(contextually_linked_word('nonexistentword'))
        frequently_following_Dadaist = ['activities', 'and', 'art', 'artist', 'artists', 'collage', 'collages',
                                        'experiments', 'group', 'hugo', 'influence', 'kurt', 'manifesto', 'marcel',
                                        'movement', 'nihilism', 'painter', 'performance', 'play', 'poem', 'poems',
                                        'poet', 'poetry', 'poets', 'raoul', 'review', 'spirit', 'tradition', 'tristan',
                                        'who', 'work', 'works']
        self.assertIn(frequently_following_word('Dadaist'), frequently_following_Dadaist)

    def test_phonetically_related_words(self):
        self.assertRaises(ValueError, lambda: phonetically_related_words(2))
        self.assertRaises(ValueError, lambda: phonetically_related_words(2.5))
        self.assertRaises(ValueError, lambda: phonetically_related_words(False))
        self.assertRaises(ValueError, lambda: phonetically_related_words(None))
        self.assertRaises(ValueError, lambda: phonetically_related_words(['a', 'b', None]))
        pr_to_poet = ['inchoate', 'opiate', 'payout', 'pet', 'peyote', 'pit', 'poached', 'poets', 'poked', 'post',
                      'putt']
        self.assertEqual(sorted(phonetically_related_words('poet', sample_size=None)), pr_to_poet)
        results = phonetically_related_words('poet', sample_size=5)
        self.assertEqual(len(sorted(results)), 5)
        self.assertTrue(set(sorted(pr_to_poet)).issuperset(set(results)))
        expected_pr_words = sorted(pr_to_poet + ['eon', 'gnawing', 'knowing', 'kneeing', 'naan', 'non', 'noun'])
        self.assertEqual(sorted(phonetically_related_words(['poet', 'neon'], sample_size=None)), expected_pr_words)

    def test_related_rare_words(self):
        self.assertRaises(ValueError, lambda: related_rare_words(2))
        self.assertRaises(ValueError, lambda: related_rare_words(2.5))
        self.assertRaises(ValueError, lambda: related_rare_words(False))
        self.assertRaises(ValueError, lambda: related_rare_words(None))
        rr_to_comical = ['absurdist', 'antic', 'artless', 'campy', 'canticle', 'cliched', 'clownish', 'cockle',
                         'cringeworthy', 'hackneyed', 'histrionic', 'humourous', 'jokey', 'parodic', 'puerile',
                         'risible', 'sophomoric', 'surrealistic', 'uneconomical', 'uproarious']
        results = related_rare_words('comical', sample_size=None)
        self.assertEqual(len(results), 20)
        self.assertEqual(sorted(results), rr_to_comical)
        results = related_rare_words('comical', sample_size=None, rare_word_population_max=None)
        self.assertGreater(len(results), 20)
        self.assertTrue(set(results).issuperset(set(rr_to_comical)))
        results = related_rare_words('comical', sample_size=6)
        self.assertEqual(len(results), 6)
        self.assertTrue(set(results).issuperset(set(results)))

        rr_to_dinosaur = ['allosaurus', 'apatosaurus', 'archaeopteryx', 'brachiosaurus', 'clade', 'crocodilian',
                          'diplodocus', 'dodos', 'humidor', 'ichthyosaur', 'iguanodon', 'megafauna', 'peccary',
                          'pterosaur', 'robustus', 'sauropod', 'stevedore', 'theropod', 'trilobite', 'tyrannosaur']
        rr_to_either = sorted(rr_to_comical + rr_to_dinosaur)
        self.assertEqual(sorted(related_rare_words(['comical', 'dinosaur'], sample_size=None)), rr_to_either)
        results = related_rare_words(['comical', 'dinosaur'])
        self.assertEqual(len(results), 8)
        self.assertTrue(set(rr_to_either).issuperset(set(results)))

    def test_related_rare_word(self):
        result_possibilities = ['artless', 'canticle', 'clownish', 'histrionic', 'humourous', 'parodic', 'risible',
                                'sophomoric', 'uneconomical', 'uproarious']
        self.assertIn(related_rare_word('comical'), result_possibilities)


class TestMarkovWordGenerator(unittest.TestCase):

    def test_random_nonrhyme(self):
        with open('tests/random_nonrhyme_possible_results.txt') as f:
            # There are over 5000 possible results even with rare words as input since this function sometimes calls
            # a random lexigen function on the result of a random lexigen function (and there are already ~70 possible
            # results even if only one function is called.
            possible_results = f.read().splitlines()
        markovgen = MarkovWordGenerator()
        for i in range(6):
            result = markovgen.random_nonrhyme(['pataphysics', 'Dadaist'])
            self.assertIn(result, possible_results)

    def test_nonlast_word(self):
        with open('tests/random_nonrhyme_possible_results.txt') as f:
            possible_randalg_results = f.read().splitlines()
        words_for_sampling = ['fervent', 'mutants', 'dazzling', 'flying', 'saucer', 'milquetoast']
        markovgen = MarkovWordGenerator()
        input_words = ['pataphysics', 'Dadaist']
        for i in range(2):
            result = markovgen.nonlast_word_of_markov_line(input_words[i:], words_for_sampling)
            self.assertTrue(result in possible_randalg_results or result in words_for_sampling or
                            result in markovgen.connector_choices)
            self.assertIn(markovgen.nonlast_word_of_markov_line(input_words[i:]), possible_randalg_results)

    def test_last_word(self):
        with open('tests/random_nonrhyme_possible_results.txt') as f:
            possible_randalg_results = f.read().splitlines()
        markovgen = MarkovWordGenerator()
        input_words = ['pataphysics', 'Dadaist']
        for i in range(2):
            result = markovgen.last_word_of_markov_line(input_words[i:], max_length=6)
            self.assertIn(result, possible_randalg_results)
            self.assertLessEqual(len(result), 6)
            rhyming_result = markovgen.last_word_of_markov_line(input_words[i:], rhyme_with='shudder', max_length=10)
            self.assertLessEqual(len(rhyming_result), 10)
            self.assertIn(rhyming_result, rhymes('shudder', sample_size=None))

class TestPoemGenerator(unittest.TestCase):

    def get_possible_word_list(self, input_word_list):
        possible_line_enders = ['.', ',', '!', '?', '...']
        possible_words = input_word_list.copy()
        for line_ender in possible_line_enders:
            for word in input_word_list:
                # Since we are testing using .split(), the list of possible words should include f'{word + line ender}'
                possible_words.append(word + line_ender)
        return possible_words

    def test_poem_line_from_word_list(self):
        input_word_list = ['crypt', 'crypts', 'crypt', 'ghost', 'ghosts', 'lost', 'time', 'times']
        possible_words = self.get_possible_word_list(input_word_list)
        possible_connectors = [',', '...', '&', 'and', 'or', '->']
        pgen = PoemGenerator()
        for i in range(5):  # Generate 5 random lines of poetry and test them.
            max_line_length = 35 + 5 * i
            poem_line = pgen.poem_line_from_word_list(input_word_list, max_line_length=max_line_length)
            # First character of line should not be a space as indents are handled by the poem_from_word_list function
            self.assertNotEqual(poem_line[0], ' ')
            # Should not have newlines as these are handled by the poem_from_word_list function
            self.assertNotIn('\n', poem_line)
            # When split, everything should derive from the possible word list
            self.assertTrue(set(possible_words + possible_connectors).issuperset(set(poem_line.split())))
            word, last_word = None, None
            for text in poem_line.split():
                word = re.match(r'[a-zA-Z]*', text).group()
                #  No word should be too similar to the preceding word
                if word and last_word:
                    self.assertFalse(too_similar(word, last_word))
                last_word = word
            # Line length should not exceed maximum line length
            self.assertTrue(len(poem_line) <= max_line_length)

    def test_poem_from_word_list(self):
        input_word_list = ['crypt', 'sleep', 'ghost', 'time']
        pgen = PoemGenerator()
        poems = [pgen.poem_from_word_list(input_word_list, limit_line_to_one_input_word=True),
                 pgen.poem_from_word_list(input_word_list, num_lines=8)]
        expected_newlines_in_poem = [5, 7]
        for i, poem in enumerate(poems):
            # 5 lines = 5 newline characters since one ends the poem
            self.assertEqual(poem.count('\n'), expected_newlines_in_poem[i])
            poem_lines = poem.split('\n')
            for string in poem_lines:
                indent_length = len(string) - len(string.lstrip())
                if indent_length != 0:
                    # Indent length should not repeat... unless there's no indent
                    self.assertNotEqual(indent_length, last_indent_length)
                last_indent_length = indent_length
            last_line_words = [word for word in poem_lines[-1].split(' ') if word != '']
            self.assertEqual(len(last_line_words), 2)
            self.assertIn(last_line_words[0], input_word_list[:-1])
            self.assertEqual(last_line_words[1], 'time')

    def test_poem_from_markov(self):
        input_words = ['chalice', 'crime', 'coins', 'spectacular', 'dazzle', 'enigma']
        pgen = PoemGenerator()
        poem = pgen.poem_from_markov(input_words=input_words, min_line_words=7, max_line_words=10, num_lines=8,
                                     max_line_length=66)
        self.assertEqual(len(poem.lines), 8)
        for line in poem.lines:
            words = line.split(" ")
            self.assertGreaterEqual(len(words), 7)
            self.assertLessEqual(len(words), 10)
            self.assertLessEqual(len(line), 71)


def test_poem_line_from_markov(self):
    pgen = PoemGenerator()
    pgen.currently_generating_poem = Poem(['pataphysics', 'Dadaist'], [])
    words_for_sampling = ['fervent', 'mutants', 'dazzling', 'flying', 'saucer', 'milquetoast']
    line = pgen.poem_line_from_markov('surrealist', num_words=8, rhyme_with=None,
                                      words_for_sampling=words_for_sampling, max_line_length=40)
    words = line.split(' ')
    self.assertLessEqual(len(line), 40)
    self.assertLessEqual(len(words), 8)
    markovgen = MarkovWordGenerator()
    self.assertNotIn(words[-1], markovgen.common_words)
    similarity_checks = list(itertools.combinations(words, 2))
    for word_pair in similarity_checks:
        self.assertFalse(too_similar(word_pair[0], word_pair[1]))
    line = pgen.poem_line_from_markov('surrealist', num_words=8, rhyme_with='bell',
                                      words_for_sampling=words_for_sampling, max_line_length=None)
    words = line.split(' ')
    self.assertEqual(len(words), 8)
    self.assertIn(words[-1], rhymes('bell', sample_size=None))
    self.assertNotIn(line.split(' ')[-1], markovgen.common_words)
    similarity_checks = list(itertools.combinations(words, 2))
    for word_pair in similarity_checks:
        self.assertFalse(too_similar(word_pair[0], word_pair[1]))
    line = pgen.poem_line_from_markov('surrealist', num_words=8, rhyme_with='unrhymable',
                                      words_for_sampling=words_for_sampling, max_line_length=None)
    words = line.split(' ')
    self.assertEqual(len(words), 8)
    self.assertNotIn(words[-1], markovgen.common_words)
    similarity_checks = list(itertools.combinations(words, 2))
    for word_pair in similarity_checks:
        self.assertFalse(too_similar(word_pair[0], word_pair[1]))


class TestPDFGeneration(unittest.TestCase):

    def test_get_font_sizes(self):
        pdfgen = PDFGenerator()
        font_size = pdfgen.get_font_size('abra cadabra hocus pocus bananas eating locusts')  # 47 characters
        self.assertEqual(font_size, 16)
        font_size = pdfgen.get_font_size('this line is 26 characters')
        self.assertIn(font_size, [16, 18, 20])
        font_size = pdfgen.get_font_size('this line is short')
        self.assertIn(font_size, pdfgen.default_font_sizes)

    def test_get_max_x_coordinate(self):
        pdfgen = PDFGenerator()
        x_coordinate = pdfgen.get_max_x_coordinate('this line is 26 characters', 'Arial', 24)
        self.assertEqual(x_coordinate, 60)
        x_coordinate = pdfgen.get_max_x_coordinate('this line is thirty-five characters', 'Arial', 21)
        self.assertEqual(x_coordinate, 60)
        x_coordinate = pdfgen.get_max_x_coordinate('this line short', 'Courier', 18)
        self.assertEqual(x_coordinate, 60)
        x_coordinate = pdfgen.get_max_x_coordinate('this line 18 chars', 'Arial', 20)
        self.assertEqual(x_coordinate, 130)
        x_coordinate = pdfgen.get_max_x_coordinate('this line is 21 chars', 'Arial', 15)
        self.assertEqual(x_coordinate, 130)
        x_coordinate = pdfgen.get_max_x_coordinate('short', 'Arial', 15)
        self.assertEqual(x_coordinate, 280)
        pdfgen.orientation = 'portrait'
        x_coordinate = pdfgen.get_max_x_coordinate('this line 18 chars', 'Arial', 24)
        self.assertEqual(x_coordinate, 30)
        x_coordinate = pdfgen.get_max_x_coordinate('this line is thirty-five characters', 'Arial', 21)
        self.assertEqual(x_coordinate, 30)
        x_coordinate = pdfgen.get_max_x_coordinate('this line short', 'Courier', 18)
        self.assertEqual(x_coordinate, 30)
        x_coordinate = pdfgen.get_max_x_coordinate('this line 18 chars', 'Arial', 20)
        self.assertEqual(x_coordinate, 100)
        x_coordinate = pdfgen.get_max_x_coordinate('this line is 21 chars', 'Arial', 15)
        self.assertEqual(x_coordinate, 100)
        x_coordinate = pdfgen.get_max_x_coordinate('short', 'Arial', 15)
        self.assertEqual(x_coordinate, 250)

    def test_get_filename(self):
        pdfgen = PDFGenerator()
        input_words = ['chalice', 'crime', 'coins', 'spectacular', 'dazzle', 'enigma']
        self.assertEqual(pdfgen.get_filename(input_words), 'chalice,crime,coins,spectacular,dazzle,enigma.pdf')
        self.assertEqual(pdfgen.get_filename(input_words, file_extension='png'),
                         'chalice,crime,coins,spectacular,dazzle,enigma.png')