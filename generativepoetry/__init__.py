import re
import random
import pronouncing
import hunspell
from wordfreq import word_frequency
from datamuse import datamuse
import platform

__author__ = 'Corey Bobco'
__email__ = 'corey.bobco@gmail.com'
__version__ = '0.1.0'

__all__ = ['rhymes', 'rhyme', 'similar_sounding_word', 'similar_sounding_words', 'similar_meaning_word',
           'similar_meaning_words', 'contextually_linked_word', 'contextually_linked_words',
           'phonetically_related_words', 'poem_line_from_word_list', 'poem_from_word_list', 'print_poem']

api = datamuse.Datamuse()
default_connectors = [' ', '   ', '...   ', random.choice([' & ', ' and ']), '  or  ', ' or ']
line_enders = ['.', ', ', '!', '?', '', ' or', '...']
line_indents = ['', '    ', '         ']
word_frequency_threshold = 4e-08

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


def has_invalid_characters(string):
    """Check if the string has unpermitted characters: whitespace, digits, and hyphens."""
    return bool(re.search(r"[\s\d\-\']", string))


def validate_word(input_val):
    """Check whether the input argument is a word."""
    validate_str(input_val)
    if has_invalid_characters(input_val):
        raise ValueError('Word may not contain digits, spaces, or special characters.')


def too_similar(word1, word2):
    """Check whether or not two words are too similar to follow one another in a poem, e.g. if one is the other plus s.
    """
    if not isinstance(word1, str) or not isinstance(word2, str) or len(word1) == 0 or len(word2) == 0:
        return False
    if word1 == word2:
        return True
    if word1 + 's' == word2 or word2 + 's' == word1:
        return True
    return False


def filter_word(string, spellcheck=True):
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
    return True


def filter_word_list(word_list, spellcheck=True):
    """Filter a list of words using the filter_word method.

    Keyword arguments:
       spellcheck (bool) -- Use a spelling dictionary as filter (helps eliminate abbreviations and Internet slang).
    """
    word_list = list(
        filter(
            lambda word: filter_word(word, spellcheck=spellcheck), word_list
        )
    )
    return word_list

def rhymes(word, sample_size=None):
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

def extract_sample(word_list, sample_size=None):
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


def similar_sounding_words(input_word, sample_size=6, datamuse_api_max=50):
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
    validate_word(input_word)
    response = api.words(sl=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(sl=input_word)
    word_list = filter_word_list([obj['word'] for obj in response])
    if input_word in word_list:
        word_list.remove(input_word)
    return extract_sample(word_list, sample_size=sample_size)


def similar_sounding_word(input_word, datamuse_api_max=20):
    """Return a random similar sounding word for a given word if at least one can be found using the Datamuse API.

    Keyword arguments:
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API's results are
                                  always sorted from most to least similar sounding (according to a numeric score
                                  provided by Datamuse).
    """
    return next(iter(similar_sounding_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def similar_meaning_words(input_word, sample_size=6, datamuse_api_max=20):
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
    validate_word(input_word)
    response = api.words(ml=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(ml=input_word)
    word_list = filter_word_list([obj['word'] for obj in response], spellcheck=False)
    return extract_sample(word_list, sample_size=sample_size)


def similar_meaning_word(input_word, datamuse_api_max=10):
    """Return a random similar meaning word for a given word if at least one can be found using the Datamuse API.

    Keyword arguments:
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API's results are
                                  always sorted from most to least similar meaning (according to a numeric score
                                  provided by Datamuse).
    """
    return next(iter(similar_meaning_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def contextually_linked_words(input_word, sample_size=6, datamuse_api_max=20):
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
    validate_word(input_word)
    response = api.words(rel_trg=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(rel_trg=input_word)
    word_list = filter_word_list([obj['word'] for obj in response], spellcheck=False)  # Spellcheck removes proper nouns
    return extract_sample(word_list, sample_size=sample_size)


def contextually_linked_word(input_word, datamuse_api_max=10):
    """Return a random word that frequently appear within the same document as a given word if at least one can be found
    using the Datamuse API.

    Keyword arguments:
        datamuse_api_max (int) -- specifies the maximum number of results returned by the API. The API's results are
                                  always sorted from most to least similar sounding (according to a numeric score
                                  provided by Datamuse).
    """
    return next(iter(contextually_linked_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def phonetically_related_words(input_val, sample_size=None, datamuse_api_max=50):
    """Get a list of rhymes and similar sounding words to a word or list of words.

    sample_size (int) -- If provided, pass this argument to the functions rhymes and similar_sounding_words so that
                         twice this number of elements are returned by this function. If not provided, the function
                         will return all rhymes plus however many API results similar_sounding_words.
    datamuse_api_max -- specifies how many API results can be returned by the API client when fetching similar
                        meaning words.
    """
    if isinstance(input_val, str):
        input_words = [input_val]
    elif isinstance(input_val, list):
        validate_str_list(input_val, msg='Must provide a string or list of strings')
        input_words = input_val
    else:
        raise ValueError('Must provide a string or list of strings')

    pr_words = []
    for word in input_words:
        pr_words.extend(rhymes(word, sample_size=sample_size))
        pr_words.extend(w for w in similar_sounding_words(word, sample_size=sample_size,
                                                          datamuse_api_max=datamuse_api_max)
                        if w not in pr_words)  # eliminate overlap
        if sample_size and sample_size - 1 < len(pr_words):
            pr_words = random.sample(pr_words, k=sample_size)
    return pr_words


def poem_line_from_word_list(word_list, max_line_length=35, connectors=default_connectors):
    """Generate a line of a visual poem from a list of words by gluing them together with random connectors (whitespace,
       conjunctions, punctuation, and symbols).

    Keyword arguments:
        max_line_length (int) -- upper limit on the length of the return value in characters
        connectors (list) -- list of glue strings
    """
    output, last_word = word_list[0], None
    for word in word_list[1:]:
        if random.random() < (.2 + len(output)/100):  # Increasing probability of line termination as line gets longer
            break
        if too_similar(last_word, word):
            continue
        connector = random.choice(connectors)
        if len(output + connector + word) <= max_line_length:
            output += connector + word
        last_word = word
    return output


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