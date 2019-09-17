import platform
import re
import random
from typing import List, TypeVar
import pronouncing
import hunspell
from wordfreq import word_frequency
from datamuse import datamuse

__author__ = 'Corey Bobco'
__email__ = 'corey.bobco@gmail.com'
__version__ = '0.1.3'

__all__ = ['rhymes', 'rhyme', 'similar_sounding_word', 'similar_sounding_words', 'similar_meaning_word',
           'similar_meaning_words', 'contextually_linked_word', 'contextually_linked_words', 'related_rare_words',
           'related_rare_word', 'sort_by_rarity', 'frequently_following_words', 'frequently_following_word',
           'poem_line_from_markov', 'phonetically_related_words', 'poem_line_from_word_list',
           'poem_from_word_list', 'print_poem']

api = datamuse.Datamuse()
default_connectors = [' ', '   ', '...   ', random.choice([' & ', ' and ']), '  or  ', ' or ']
line_enders = ['.', ', ', '!', '?', '', ' or', '...']
line_indents = ['', '    ', '         ']
common_words = ["the", "with", "in", "that", "not", "a", "an"]
word_frequency_threshold = 4e-08
input_type = TypeVar('input_type', str, List[str])  # Must be str or list of strings

if platform.system() == 'Windows':
    raise Exception('Your OS is not currently supported.')
elif platform.system() == 'Darwin':
    try:
        hobj = hunspell.HunSpell('/Library/Spelling/en_US.dic', '/Library/Spelling/en_US.aff')
    except Exception:
        raise Exception('This module requires the installation of the hunspell dictionary.')
else:
    try:
        hobj = hunspell.HunSpell('/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')
    except Exception:
        raise Exception('This module requires the installation of the hunspell dictionary.')


def validate_str(input_val, msg='Not a string'):
    """Validate the input argument by checking if it is a string."""
    if not isinstance(input_val, str):
        raise ValueError(msg)


def validate_str_list(input_val, msg='Not a list'):
    """Validate the input argument by checking if it is a list of strings."""
    if not isinstance(input_val, list):
        raise ValueError(msg)
    for i, elem in enumerate(input_val):
        if not isinstance(elem, str):
            raise ValueError(f'Element {i + 1} not a string')


def validate_str_or_list_of_str(input_val):
    if isinstance(input_val, str):
        return [input_val]
    elif isinstance(input_val, list):
        validate_str_list(input_val, msg='Must provide a string or list of strings')
        return input_val
    else:
        raise ValueError('Must provide a string or list of strings')


def has_invalid_characters(string):
    """Check if the string has unpermitted characters: whitespace, digits, and hyphens."""
    return bool(re.search(r"[\s\d\-\']", string))


def validate_word(input_val):
    """Check whether the input argument is a word."""
    validate_str(input_val)
    if has_invalid_characters(input_val):
        raise ValueError('Word may not contain digits, spaces, or special characters.')


def too_similar(word1, val2):
    """Check whether or not two words are too similar to follow one another in a poem, e.g. if one is the other plus s.
    """
    comparison_words = validate_str_or_list_of_str(val2)
    for word2 in comparison_words:
        if not isinstance(word1, str) or not isinstance(word2, str) or len(word1) == 0 or len(word2) == 0:
            return False
        if word1 == word2:
            return True
        if word1 + 's' == word2 or word2 + 's' == word1:
            return True
        if word1 + 'ly' == word2 or word2 + 'ly' == word1:
            return True
        if (len(word1) > 2 and len(word2) > 2) and ((word1[-2] == 'e' and word2 + 'd' == word1) or
            (word2[-2] == 'e' and word1 + 'd' == word1)):
            return True
    return False


def filter_word(string, spellcheck=True, exclude_words=[]):
    """Filter out a word if it is too short, has invalid characters, is too archaic, or (optionally) cannot be found in
    a spelling dictionary.

       Keyword arguments:
       spellcheck (bool) -- Use a spelling dictionary as filter (helps eliminate abbreviations and Internet slang).
    """
    validate_str(string)
    if len(string) < 3:
        return False
    if has_invalid_characters(string):
        return False
    if word_frequency(string, 'en') < word_frequency_threshold:
        return False
    if spellcheck and not hobj.spell(string):
        return False
    if string in exclude_words:
        return False
    return True


def filter_word_list(word_list, spellcheck=True, exclude_words=[]):
    """Filter a list of words using the filter_word method.

    Keyword arguments:
       spellcheck (bool) -- Use a spelling dictionary as filter (helps eliminate abbreviations and Internet slang).
    """
    word_list = list(
        filter(
            lambda word: filter_word(word, spellcheck=spellcheck, exclude_words=exclude_words), word_list
        )
    )
    return word_list

def sort_by_rarity(word_list):
    if len(word_list) <= 1:
        return word_list
    return sort_by_rarity(
        [word for word in word_list[1:] if word_frequency(word, 'en') < word_frequency(word_list[0], 'en')]
    ) + [word_list[0]] + \
    sort_by_rarity([word for word in word_list[1:] if word_frequency(word, 'en') >= word_frequency(word_list[0], 'en')])

def rhymes(word, sample_size=None) -> list:
    """Return a list of rhymes in randomized order for a given word if at least one can be found using the pronouncing
    module (which uses the CMU rhyming dictionary).

    Keyword arguments:
        sample size (int) -- If provided, return a random sample of this many elements. If this number is greater than
                            the length of the rhyme list, then just return a shuffled copy of the rhyme list.
    """
    rhymes = filter_word_list([word for word in set(pronouncing.rhymes(word))])
    if isinstance(sample_size, int) and sample_size < len(rhymes):
        rhymes = random.sample(rhymes, k=sample_size)
    random.shuffle(rhymes)
    return rhymes


def rhyme(word):
    """Return a random rhyme for a given word if at least one can be found using the pronouncing module (which uses
    the CMU rhyming dictionary).
    """
    rhyme_list = rhymes(word)
    if len(rhyme_list):
        return next(iter(rhyme_list), None)
    return None

def extract_sample(word_list, sample_size=None) -> list:
    """Returns a random sample from the word list or a shuffled copy of the word list.

    Keyword arguments:
        sample size (int)-- If this number is greater than the length of the word list, then just return a shuffled
        copy of the word list.
    """
    if not sample_size or len(word_list) <= sample_size:
        return random.sample(word_list, k=len(word_list))
    else:
        sample = []
        while len(sample) < sample_size and len(word_list) > 0:
            sample += [word for word in random.sample(word_list, k=sample_size) if word not in sample]
            word_list = [word for word in word_list if word not in sample]
        if sample_size < len(sample):
            return random.sample(sample, k=sample_size)
        return sample


def similar_sounding_words(input_val, sample_size=6, datamuse_api_max=50) -> list:
    """Return a list of similar sounding words to a given word, in randomized order, if at least one can be found using
    Datamuse API.

    Keyword arguments:
        sample_size (int) -- If provided, return a random sample of this many elements. If this number is greater than
                             the length of the API results, then just return a shuffled copy of the filtered API
                             results.
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API client's
                                  results are always sorted from most to least similar sounding (according to a numeric
                                  score provided by Datamuse), hence by using both kwargs, one can control the size of
                                  both the sample pool and the sample size.
    """
    input_words = validate_str_or_list_of_str(input_val)
    ss_words = []
    for input_word in input_words:
        response = api.words(sl=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(sl=input_word)
        ss_words.extend(filter_word_list([obj['word'] for obj in response], exclude_words=input_words))
    return extract_sample(ss_words, sample_size=sample_size)


def similar_sounding_word(input_word, datamuse_api_max=20) -> str:
    """Return a random similar sounding word for a given word if at least one can be found using the Datamuse API.

    Keyword arguments:
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API's results are
                                  always sorted from most to least similar sounding (according to a numeric score
                                  provided by Datamuse).
    """
    return next(iter(similar_sounding_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def similar_meaning_words(input_val: input_type, sample_size=6, datamuse_api_max=20) -> list:
    """Return a list of similar meaning words to a given word, in randomized order, if at least one can be found using
    Datamuse API.

    Keyword arguments:
        sample_size (int) -- If provided, return a random sample of this many elements. If this number is greater than
                             the length of the API results, then just return a shuffled copy of the filtered API
                             results.
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API client's
                                  results are always sorted from most to least similar meaning (according to a numeric
                                  score provided by Datamuse), hence by using both kwargs, one can control the size of
                                  both the sample pool and the sample size.
    """
    input_words = validate_str_or_list_of_str(input_val)
    sm_words = []
    for input_word in input_words:
        response = api.words(ml=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(ml=input_word)
        sm_words.extend(filter_word_list([obj['word'] for obj in response], spellcheck=False))
    return extract_sample(sm_words, sample_size=sample_size)


def similar_meaning_word(input_word, datamuse_api_max=10) -> str:
    """Return a random similar meaning word for a given word if at least one can be found using the Datamuse API.

    Keyword arguments:
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API's results are
                                  always sorted from most to least similar meaning (according to a numeric score
                                  provided by Datamuse).
    """
    return next(iter(similar_meaning_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def contextually_linked_words(input_val: input_type, sample_size=6, datamuse_api_max=20):
    """Return a list of words that frequently appear within the same document as a given word, in randomized order,
    if at least one can be found using the Datamuse API.

    Keyword arguments:
        sample_size (int) -- If provided, return a random sample of this many elements. If this number is greater than
                             the length of the API results, then just return a shuffled copy of the filtered API
                             results.
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API client's
                                  results are always sorted from most to least frequently coappearing (according to a
                                  numeric score provided by Datamuse), hence by using both kwargs, one can control the
                                  size of both the sample pool and the sample size.
    """
    input_words = validate_str_or_list_of_str(input_val)
    cl_words = []
    for input_word in input_words:
        validate_word(input_word)
        response = api.words(rel_trg=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(rel_trg=input_word)
        cl_words.extend(filter_word_list([obj['word'] for obj in response], spellcheck=False))  # Spellcheck removes proper nouns
    return extract_sample(cl_words, sample_size=sample_size)


def contextually_linked_word(input_word, datamuse_api_max=10) -> str:
    """Return a random word that frequently appear within the same document as a given word if at least one can be found
    using the Datamuse API.

    Keyword arguments:
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API's results are
                                  always sorted from most to least similar sounding (according to a numeric score
                                  provided by Datamuse).
    """
    return next(iter(contextually_linked_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def frequently_following_words(input_word, sample_size=6, datamuse_api_max=20) -> list:
    """Return a list of words that frequently follow the given word, in randomized order,
    if at least one can be found using the Datamuse API.

    Keyword arguments:
        sample_size (int) -- If provided, return a random sample of this many elements. If this number is greater than
                             the length of the API results, then just return a shuffled copy of the filtered API
                             results.
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API client's
                                  results are always sorted from most to least frequently coappearing (according to a
                                  numeric score provided by Datamuse), hence by using both kwargs, one can control the
                                  size of both the sample pool and the sample size.
    """
    validate_word(input_word)
    response = api.words(lc=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(lc=input_word)
    # Filter but don't use spellcheck -- it removes important words like 'of'
    word_list = filter_word_list([obj['word'] for obj in response], spellcheck=False)
    return extract_sample(sort_by_rarity(word_list), sample_size=sample_size)


def frequently_following_word(input_word, datamuse_api_max=10, weight_by_rarity=False) -> str:
    """Return a random word that frequently follows the given word if at least one can be found using the Datamuse API.

    Keyword arguments:
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API's results are
                                  always sorted from most to least similar sounding (according to a numeric score
                                  provided by Datamu
                                  se).
    """
    if weight_by_rarity:
        return random.choice(sort_by_rarity(frequently_following_words(
            input_word, sample_size=None, datamuse_api_max=20))[:4])
    return next(iter(frequently_following_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def related_rare_words(input_val: input_type, sample_size=8, rare_word_population_max=20) -> list:
    """Return a random sample of rare related words to a given word. The words can be related phonetically,
    contextually, or by meaning).

    Keyword arguments:
        sample_size (int) -- If provided, return a random sample of this many elements. If this number is greater than
                             the length of rare word population size, then just return a shuffled copy of that.
        rare_word_population_max (int) -- specifies the maximum number of related words to subsample from. The rare word
                                          population is sorted from rarest to most common.
    """
    input_words = validate_str_or_list_of_str(input_val)
    results = []
    for input_word in input_words:
        related_words = phonetically_related_words(input_word) + \
                        contextually_linked_words(input_word, sample_size=None, datamuse_api_max=100) + \
                        similar_meaning_words(input_word, sample_size=None, datamuse_api_max=100)
        results.extend([word for word in related_words if not too_similar(input_word, word)])
        random.shuffle(results)
    return extract_sample(sort_by_rarity(results)[:rare_word_population_max], sample_size=sample_size)


def related_rare_word(input_word, rare_word_population_max=10):
    """Return a random rare related word to a given word. The word can be related phonetically, contextually, or by
    meaning).

    Keyword arguments:
        rare_word_population_max (int) -- specifies the maximum number of related words to subsample from. The rare word
                                          population is sorted from rarest to most common.
    """
    return next(iter(related_rare_words(input_word, sample_size=1,
                                        rare_word_population_max=rare_word_population_max)), None)


def phonetically_related_words(input_val: input_type, sample_size=None, datamuse_api_max=50) -> list:
    """Get a list of rhymes and similar sounding words to a word or list of words.

    sample_size (int) -- If provided, pass this argument to the functions rhymes and similar_sounding_words so that
                         twice this number of elements are returned by this function. If not provided, the function
                         will return all rhymes plus however many API results similar_sounding_words.
    datamuse_api_max -- specifies how many API results can be returned by the API client when fetching similar
                        meaning words.
    """
    input_words = validate_str_or_list_of_str(input_val)
    pr_words = []
    for word in input_words:
        pr_words.extend(rhymes(word, sample_size=sample_size))
        pr_words.extend(w for w in similar_sounding_words(word, sample_size=sample_size,
                                                          datamuse_api_max=datamuse_api_max)
                        if w not in pr_words)  # eliminate overlap
        if sample_size and sample_size - 1 < len(pr_words):
            pr_words = random.sample(pr_words, k=sample_size)
    return pr_words


def poem_line_from_word_list(word_list, max_line_length=35, connectors=default_connectors) -> list:
    """Generate a line of a visual poem from a list of words by gluing them together with random connectors (whitespace,
       conjunctions, punctuation, and symbols).

    Keyword arguments:
        max_line_length (int) -- upper limit on the length of the return value in characters
        connectors (list) -- list of glue strings
    """
    output, last_word = word_list[0], word_list[0]
    last_connector = ''
    for word in word_list[1:]:
        if random.random() < (.2 + len(output)/100):  # Increasing probability of line termination as line gets longer
            break
        if too_similar(last_word, word):
            continue
        connector = random.choice(connectors)
        while connector == last_connector:
            connector = random.choice(connectors)
        if len(output + connector + word) <= max_line_length:
            output += connector + word
        last_word = word
        last_connector = connector
    return output


def last_word_of_markov_line(previous_words, last_line_last_word=None):
    last_word = None
    if last_line_last_word and last_line_last_word not in common_words:
        while last_word is None:
            last_word = rhyme(previous_words[-1])
            last_word = random_nonrhyme(previous_words, last_line_last_word)
    else:
        while last_word is None:
            last_word = random_nonrhyme(previous_words, last_line_last_word)
    return last_word


def nonlast_word_of_markov_line(previous_words, last_line_last_word=None, words_for_sampling=[]):
    word = None
    if previous_words[-1] in common_words:
        if random.random() >= .66:
            word = random_nonrhyme(previous_words, last_line_last_word)
        else:
            while word is None or too_similar(word, previous_words):
                word = random.choice(words_for_sampling)
    else:
        if len(words_for_sampling):
            threshold1, threshold2 = .66, 1
        else:
            threshold1, threshold2 = .5, 1
        while word is None or too_similar(word, previous_words):
            randfloat = random.random()
            if randfloat > threshold1:
                word = random_nonrhyme(previous_words, last_line_last_word)
            elif randfloat > threshold2:
                word = random.choice(words_for_sampling)
            else:
                word = frequently_following_word(previous_words[-1], weight_by_rarity=False)
    return word


def random_nonrhyme(previous_words, last_line_last_word):
    """Return a random nonrhyme"""
    result = None
    while result is None:
        if random.random() <= .7 and last_line_last_word:
            next_word_algorithms = [similar_sounding_word, similar_meaning_word, contextually_linked_word]
            possible_result = random.choice(next_word_algorithms)(last_line_last_word)
        else:
            if random.random() >= .5:
                possible_result = frequently_following_word(previous_words[-1], weight_by_rarity=True)
            else:
                possible_result = similar_sounding_word(random.choice(previous_words))
        if not too_similar(possible_result, previous_words) and \
                not(last_line_last_word and too_similar(possible_result, last_line_last_word)):
            result = possible_result
    return result


def poem_line_from_markov(starting_word, num_words=4, rhyme_with=None, words_for_sampling=[], max_line_length=35) -> list:
    output_words, previous_word = [starting_word], starting_word
    for i in range(num_words - 1):
        if (i == num_words - 2 and rhyme_with) or len(' '.join(output_words)) >= max_line_length - 6:
            #  If the last word must rhyme with something
            word = last_word_of_markov_line(output_words, last_line_last_word=rhyme_with)
        else:
            word = nonlast_word_of_markov_line(output_words, rhyme_with, words_for_sampling=words_for_sampling)
        output_words.append(word)
    return " ".join(output_words)


def poem_from_word_list(phonetic_input_word_list, lines=6, max_line_length=35, limit_line_to_one_input_word=False):
    """Generate a visual poem from a list of words by finding some random phonetically related

    Keyword arguments:
        max_line_length (int) -- upper limit on the length of the return value in characters
        connectors (list) -- list of glue strings
        max_line_length (int) -- upper limit on length of poem lines (excluding line ending punctuation) in characters
        limit_line_to_one_input_word (bool) -- If true, when generating a line of poetry, only use words that are
                                               phonetically related to one input word.
    """
    connectors = [' ', '   ', '...   ', random.choice([' & ', ' and ']), '  or  ', ' or ']
    output, line_indent = '', ''
    if limit_line_to_one_input_word:
        for i in range(lines - 1):
            linked_word = random.choice(phonetic_input_word_list)
            output += poem_line_from_word_list(phonetically_related_words(linked_word), connectors=connectors,
                                               max_line_length=max_line_length)
            line_indent = random.choice(line_indents) if line_indent == '' else \
                random.choice([li for li in line_indents if li is not line_indent])  # Don't repeat the same indent 2x
            output += random.choice(line_enders) + '\n' + line_indent
    else:
        word_list = phonetic_input_word_list.copy()
        for word in phonetic_input_word_list:
            word_list.extend(phonetically_related_words(word))
        for i in range(lines - 1):
            random.shuffle(word_list)
            output += poem_line_from_word_list(word_list, connectors=connectors, max_line_length=max_line_length)
            line_indent = random.choice(line_indents) if line_indent == '' else \
                random.choice([li for li in line_indents if li is not line_indent])   # Don't repeat the same indent 2x
            output += random.choice(line_enders) + '\n'+ line_indent

    output += random.choice(phonetic_input_word_list[:-1]) + ' ' + phonetic_input_word_list[-1]
    return output


def print_poem(poem):
    """Print the poem with a newline before and after so it's easy to take a screenshot of its 'recipe' and the poem
    in your terminal and share it. :)"""
    print('\n')
    print(poem)
    print('\n')