import re
import unittest
from generativepoetry.lexigen import *
from generativepoetry.lexigen import validate_str, validate_str_list, has_invalid_characters, validate_word, \
                                     too_similar,  filter_word, filter_word_list, extract_sample, sort_by_rarity


class TestValidationAndFilters(unittest.TestCase):

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


class TestWordSampling(unittest.TestCase):
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
        pass

    def test_frequently_following_word(self):
        pass

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

    def test_sort_by_rarity(self):
        unsorted_words = ['cat', 'catabasis', 'hue', 'corncob',  'the', 'Catalan', 'errant']
        correctly_sorted_words = ['catabasis', 'corncob', 'errant', 'hue', 'Catalan', 'cat', 'the']
        self.assertEqual(sort_by_rarity(unsorted_words), correctly_sorted_words)

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


class TestBasicPoemGenerator(unittest.TestCase):

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
        poemgen = Poem()
        for i in range(5):  # Generate 5 random lines of poetry and test them.
            max_line_length = 35 + 5 * i
            poem_line = poemgen.poem_line_from_word_list(input_word_list, max_line_length=max_line_length)
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
        poemgen = Poem()
        poems = [poemgen.poem_from_word_list(input_word_list, limit_line_to_one_input_word=True),
                 poemgen.poem_from_word_list(input_word_list, lines=8)]
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


if __name__ == '__main__':
    unittest.main()