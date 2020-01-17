import hunspell
import platform
import random
import re
from typing import List, TypeVar
from wordfreq import word_frequency
from consolemenu.screen import Screen


def setup_spellchecker():
    if platform.system() == 'Windows':
        raise Exception('Your OS is not currently supported.')
    elif platform.system() == 'Darwin':
        try:
            return hunspell.HunSpell('/Library/Spelling/en_US.dic', '/Library/Spelling/en_US.aff')
        except Exception:
            raise Exception('This module requires the installation of the hunspell dictionary.')
    else:
        try:
            return hunspell.HunSpell('/usr/share/hunspell/en_US.dic', '/usr/share/hunspell/en_US.aff')
        except Exception:
            raise Exception('This module requires the installation of the hunspell dictionary.')


hobj = setup_spellchecker()
str_or_list_of_str = TypeVar('str_or_list_of_str', str, List[str])
unfitting_words = ['thew', 'iii', 'arr', 'atty', 'haj', 'pao', 'gea', 'ning', 'mor', 'mar', 'iss', 'eee', 'pls', 'fia',
                   'gar', 'ism', 'schwa', 'sor', 'bpa', 'saba', 'ria', 'nds', 'moi', 'esc', 'sabra', 'cim', 'rha',
                   'dist', 'nos', 'noes', 'brs', 'ltd', 'inc', 'gov', 'pis', 'lav', 'elev', 'ups', 'ms', 'srg', 'cas',
                   'dago', 'prob', 'sro', 'ccs', 'pas', 'sab', 'cscs', 'arv', 'uhf', 'var', 'obe', 'tid', 'cpd']
# Datamuse is built from webscraping and occasionally returns offensive and oppressive language, which I am here adding
# to filter out. Although there is an appropriate and even critical way for humans to write poetry using some of these
# words that might be considered edge cases (e.g. Hottentot), a stochastic text generator does not have a historical
# sense to do that, so I have decided to exclude these.
oppressive_words = ['beaner', 'blacks', 'coon', 'coloureds', 'dago', 'darkie', 'honky', 'hottentot',  'hottentots',
                    'injun', 'jap', 'kaffir', 'kike', 'kkk', 'mammy', 'negro', 'negrito', 'nigga', 'nigger', 'niggers',
                    'paki', 'pommy', 'racialist', 'swart', 'wetback', 'whitey', 'whities', 'wog', 'wop']
unfitting_words.extend(oppressive_words)

def get_input_words():
    prompt = 'To generate a poem, type some words separated by commas or spaces, and then press enter again.\n\n'

    input_words = []
    while len(input_words) == 0:
        inp = Screen().input(prompt=prompt)
        input_words = [word for word in re.split(r'[\s,]', inp) if word]
    return input_words


def get_random_color(threshold=.85):
    """Gets a random color -- 2/3 of the rgb values must be below the threshold value"""
    r, g, b = 1, 1, 1
    while (1 - r <= threshold and 1 - g <= threshold) or (1 - g <= threshold and 1 - b <= threshold) or \
            (1 - r <= threshold and 1 - b <= threshold):
        r, g, b = random.random(), random.random(), random.random()
    return r, g, b


def validate_str(input_val, msg='Not a string'):
    """Validate the input argument by checking if it is a string.

    :param input_val: the value to validate
    :param msg: the message to display if a ValueError is thrown
    """
    if not isinstance(input_val, str):
        raise ValueError(msg)


def validate_str_list(input_val, msg='Not a list'):
    """Validate the input parameter by checking if it is a list of strings.

    :param input_val: the value to validate
    :param msg: the message to display if a ValueError is thrown
    """
    if not isinstance(input_val, list):
        raise ValueError(msg)
    for i, elem in enumerate(input_val):
        if not isinstance(elem, str):
            raise ValueError(f'Element {i + 1} not a string')


def validate_str_or_list_of_str(input_val) -> List[str]:
    """Validate the input parameter by checking if it is a string or a list of strings.

    :param input_val: the value to validate
    """
    if isinstance(input_val, str):
        return [input_val]
    elif isinstance(input_val, list):
        validate_str_list(input_val, msg='Must provide a string or list of strings')
        return input_val
    else:
        raise ValueError('Must provide a string or list of strings')


def has_invalid_characters(string):
    """Check if the string has unpermitted characters: whitespace, digits, and hyphens.

    :param string: the string to check for invalid characters in
    """
    return bool(re.search(r"[\s\d\-\']", string))


def validate_word(input_val):
    """Check whether the input argument is a word.

    :param input_val: the word to validate
    """
    validate_str(input_val)
    if has_invalid_characters(input_val):
        raise ValueError('Word may not contain digits, spaces, or special characters.')


def filter_word(string, spellcheck=True, exclude_words=[], word_frequency_threshold=4e-08):
    """Filter out a word if it is too short, has invalid characters, is too archaic, or (optionally) cannot be found in
    a spelling dictionary.

    :param string: the string to check against
    :param spellcheck: Use a spelling dictionary as filter. This helps eliminate abbreviations, proper nouns, and
                       Internet slang--sometimes this is not desirable. It also eliminates many short stopwords like
                       'of' for some reason.
    :param exclude_words: list of words to filter out
    :param word_frequency_threshold: how frequently the word appears in the word_frequency package's corpus -- filter
                                     out word if less frequent than this threshold
    """
    exclude_words.extend(unfitting_words)  # Some words Datamuse tends to return that disruptive poetic flow
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


def filter_word_list(word_list: List[str], spellcheck: bool = True, exclude_words: List[str] = []) -> List[str]:
    """Filter a list of words using the filter_word method.

    :param word_list: list of words to filter
    :param spellcheck (bool) -- Use a spelling dictionary as filter (helps eliminate abbreviations and Internet slang).
    """
    results: List[str] = list(
        filter(
            lambda word: filter_word(word, spellcheck=spellcheck, exclude_words=exclude_words), word_list
        )
    )
    return results


def sort_by_rarity(word_list: List[str]) -> List[str]:
    if len(word_list) <= 1:
        return word_list
    return sort_by_rarity(
        [word for word in word_list[1:] if word_frequency(word, 'en') < word_frequency(word_list[0], 'en')]
    ) + [word_list[0]] + \
           sort_by_rarity(
               [word for word in word_list[1:] if word_frequency(word, 'en') >= word_frequency(word_list[0], 'en')])


def too_similar(word1: str, comparison_val: str_or_list_of_str) -> bool:
    """Check whether or not two words are too similar to follow one another in a poem, e.g. if one is the other plus s.
    :param word1: the first word to compare
    :param comparison_val: a word or list of words to compare against
    """
    validate_str(word1)
    comparison_words = validate_str_or_list_of_str(comparison_val)
    for word2 in comparison_words:
        if len(word1) == 0 or len(word2) == 0:
            return False
        if word1 == word2:
            return True
        if word1 + 's' == word2 or word2 + 's' == word1:  # Plural, probably
            return True
        if word1 + 'ly' == word2 or word2 + 'ly' == word1:  # Adverb form of an adjective
            return True
        # Perhaps the latter two checks could still be done efficiently with lemmatization
        if (len(word1) > 2 and len(word2) > 2) and ((word1[-2] == 'e' and word2 + 'd' == word1) or
            (word2[-2] == 'e' and word1 + 'd' == word2)):  # Past tense
            return True
        if ((len(word1) > 5 and len(word2) > 2) or (len(word2) > 5 and len(word1) > 2)) and \
                ((word1[-3:] == 'ing' and word2 + 'ing' == word1) or (word2[-3:] == 'ing' and word1 + 'ing' == word2)):
            # Gerunds
            return True
        too_similar_case = ['the', 'thee', 'them']
        if word1 in too_similar_case and word2 in too_similar_case:
            return True
    return False