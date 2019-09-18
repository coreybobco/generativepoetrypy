import platform
import re
import random
from typing import List, TypeVar, Optional
import pronouncing
import hunspell
from wordfreq import word_frequency
from datamuse import datamuse

__author__ = 'Corey Bobco'
__email__ = 'corey.bobco@gmail.com'
__version__ = '0.1.3'

__all__ = ['sort_by_rarity', 'rhymes', 'rhyme', 'similar_sounding_word', 'similar_sounding_words',
           'similar_meaning_word', 'similar_meaning_words', 'contextually_linked_word', 'contextually_linked_words',
           'frequently_following_words', 'frequently_following_word', 'phonetically_related_words',
           'related_rare_words', 'related_rare_word']

api = datamuse.Datamuse()
word_frequency_threshold = 4e-08
str_or_list_of_str = TypeVar('str_or_list_of_str', str, List[str])
unfitting_words = ['thew', 'iii', 'arr', 'atty', 'haj', 'pao', 'gea', 'ning', 'mor', 'mar', 'iss', 'eee']

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
        if word1 + 'ly' == word2 or word2 + 'ly' == word1:  # Adverb form of an adjective
            return True
        if (len(word1) > 2 and len(word2) > 2) and ((word1[-2] == 'e' and word2 + 'd' == word1) or
            (word2[-2] == 'e' and word1 + 'd' == word2)):  # Past tense
            return True
        too_similar_case = ['the', 'thee', 'them']
        if word1 in too_similar_case and word2 in too_similar_case:
            return True
    return False


def filter_word(string, spellcheck=True, exclude_words=[]):
    """Filter out a word if it is too short, has invalid characters, is too archaic, or (optionally) cannot be found in
    a spelling dictionary.

    :param string: the string to check against
    :param spellcheck: Use a spelling dictionary as filter. This helps eliminate abbreviations, proper nouns, and
                       Internet slang--sometimes this is not desirable. It also eliminates many short stopwords like
                       'of' for some reason.
    :param exclude_words: list of words to filter out
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
    sort_by_rarity([word for word in word_list[1:] if word_frequency(word, 'en') >= word_frequency(word_list[0], 'en')])


def rhymes(input_val: str_or_list_of_str, sample_size=None) -> List[str]:
    """Return a list of rhymes in randomized order for a given word if at least one can be found using the pronouncing
    module (which uses the CMU rhyming dictionary).

    :param input_val: the word or words in relation to which this function is looking up rhymes
    :param sample size: If provided, return a random sample of this many elements. If this number is greater than
                        the length of the rhyme list, then just return a shuffled copy of the rhyme list.
    """
    input_words = validate_str_or_list_of_str(input_val)
    rhyme_words: List[str] = []
    for input_word in input_words:
        rhyme_words.extend(filter_word_list([word for word in set(pronouncing.rhymes(input_word))]))
    return extract_sample(rhyme_words, sample_size=sample_size)


def rhyme(input_word: str) -> Optional[str]:
    """Return a random rhyme for a given word if at least one can be found using the pronouncing module (which uses
    the CMU rhyming dictionary).

    :param input_word: the word which this function is looking up a rhyme of
    """
    rhyme_list = rhymes(input_word)
    if len(rhyme_list):
        return next(iter(rhyme_list), None)
    return None


def extract_sample(word_list: list, sample_size: Optional[int] = None) -> list:
    """Returns a random sample from the word list or a shuffled copy of the word list.

    :param word_list: the list of words to extract the random sample of k
    :param sample_size: If this number is greater than the length of the word list, then just return a shuffled
                        copy of the word list.
    """
    if not sample_size or len(word_list) <= sample_size:
        return random.sample(word_list, k=len(word_list))
    else:
        sample: List[str] = []
        while len(sample) < sample_size and len(word_list) > 0:
            sample += [word for word in random.sample(word_list, k=sample_size) if word not in sample]
            word_list = [word for word in word_list if word not in sample]
        if sample_size < len(sample):
            return random.sample(sample, k=sample_size)
        return sample


def similar_sounding_words(input_val: str_or_list_of_str, sample_size: Optional[int] = 6,
                           datamuse_api_max: Optional[int] = 50) -> list:
    """Return a list of similar sounding words to a given word, in randomized order, if at least one can be found using
    Datamuse API.

    :param input_val: the word or words in relation to which this function is looking up similar sounding words
    :param sample_size: If provided, return a random sample of this many elements. If this number is greater than the
                        length of the API results, then just return a shuffled copy of the filtered API results.
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's results
                             are always sorted from most to least similar sounding (according to a numeric score
                             provided by Datamuse), hence by using both parameters, one can control the size of both
                             the sample pool and the sample size.
    """
    input_words = validate_str_or_list_of_str(input_val)
    ss_words: List[str] = []
    for input_word in input_words:
        response = api.words(sl=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(sl=input_word)
        exclude_words = input_words + ss_words
        ss_words.extend(filter_word_list([obj['word'] for obj in response], exclude_words=exclude_words))
    return extract_sample(ss_words, sample_size=sample_size)


def similar_sounding_word(input_word: str, datamuse_api_max: Optional[int] = 20) -> Optional[str]:
    """Return a random similar sounding word for a given word if at least one can be found using the Datamuse API.

    :param input_word: the word which this function is looking up a similar sounding words of
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's results are
                             always sorted from most to least similar sounding (according to a numeric score provided
                             by Datamuse).
    """
    return next(iter(similar_sounding_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def similar_meaning_words(input_val: str_or_list_of_str, sample_size: Optional[int] = 6,
                          datamuse_api_max: Optional[int] = 20) -> list:
    """Return a list of similar meaning words to a given word, in randomized order, if at least one can be found using
    Datamuse API.

    :param input_val: the word or words in relation to which this function is looking up similar meaning words
    :param sample_size: If provided, return a random sample of this many elements. If this number is greater than the
                        length of the API results, then just return a shuffled copy of the filtered API results.
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's results
                             are always sorted from most to least similar meaning (according to a numeric score
                             provided by Datamuse), hence by using both parameters, one can control the size of both
                             the sample pool and the sample size.
    """
    input_words = validate_str_or_list_of_str(input_val)
    sm_words: List[str] = []
    for input_word in input_words:
        response = api.words(ml=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(ml=input_word)
        exclude_words = sm_words.copy()
        sm_words.extend(filter_word_list([obj['word'] for obj in response], spellcheck=False,
                                         exclude_words=exclude_words))
    return extract_sample(sm_words, sample_size=sample_size)


def similar_meaning_word(input_word: str, datamuse_api_max: Optional[int] = 10) -> Optional[str]:
    """Return a random similar meaning word for a given word if at least one can be found using the Datamuse API.

    :param input_word: the word which this function is looking up a similar meaning words of
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's results are
                             always sorted from most to least similar meaning (according to a numeric score provided
                             by Datamuse).
    """
    return next(iter(similar_meaning_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def contextually_linked_words(input_val: str_or_list_of_str, sample_size: Optional[int] = 6,
                              datamuse_api_max: Optional[int] = 20) -> list:
    """Return a list of words that frequently appear within the same document as a given word, in randomized order,
    if at least one can be found using the Datamuse API.

    :param input_val: the word or words in relation to which this function is looking up contextually linked words
    :param sample_size: If provided, return a random sample of this many elements. If this number is greater than the
                        length of the API results, then just return a shuffled copy of the filtered API results.
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's results
                             are always sorted from most to least frequently coappearing (according to a numeric score
                             provided by Datamuse), hence by using both parameters, one can control the size of both
                             the sample pool and the sample size.
    """
    input_words = validate_str_or_list_of_str(input_val)
    cl_words: List[str] = []
    for input_word in input_words:
        validate_word(input_word)
        response = api.words(rel_trg=input_word, max=datamuse_api_max) if datamuse_api_max else \
            api.words(rel_trg=input_word)
        exclude_words = cl_words.copy()
        # Spellcheck removes proper nouns so don't.
        cl_words.extend(filter_word_list([obj['word'] for obj in response], spellcheck=False,
                                         exclude_words=exclude_words))
    return extract_sample(cl_words, sample_size=sample_size)


def contextually_linked_word(input_word: str, datamuse_api_max: Optional[int] = 10) -> Optional[str]:
    """Return a random word that frequently appear within the same document as a given word if at least one can be found
    using the Datamuse API.

    :param input_word: the word which this function is looking up a contextually linked words to
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's results are
                             always sorted from most to least similar sounding (according to a numeric score provided
                             by Datamuse).
    """
    return next(iter(contextually_linked_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)


def frequently_following_words(input_val: str_or_list_of_str, sample_size: Optional[int] = 8,
                               datamuse_api_max: Optional[int] = None) -> list:
    """Return a list of words that frequently follow the given word, in randomized order, if at least one can be found
    using the Datamuse API.

    :param input_val: the word or words in relation to which this function is looking up frequently following words
    :param sample_size: If provided, return a random sample of this many elements. If this number is greater than
                             the length of the API results, then just return a shuffled copy of the filtered API
                             results.
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's
                                  results are always sorted from most to least frequently coappearing (according to a
                                  numeric score provided by Datamuse), hence by using both parameters, one can control
                                  the size of both the sample pool and the sample size.
    """
    input_words = validate_str_or_list_of_str(input_val)
    ff_words: List[str] = []
    for input_word in input_words:
        response = api.words(lc=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(lc=input_word)
        # Filter but don't use spellcheck -- it removes important words (for the markov chain use case) like 'of'
        exclude_words = ff_words.copy()
        ff_words.extend(filter_word_list([obj['word'] for obj in response], spellcheck=False,
                                         exclude_words=exclude_words))
    if sample_size and sample_size > 4:
        # Pick 4 at random from the whole and the rest from the top X rarest following words
        # Slice one list of api results using the default order and another using a rarity baeed order
        if not datamuse_api_max:
            ending_index = 20
        elif datamuse_api_max % 2 == 1:
            ending_index = datamuse_api_max + 1
        else:
            ending_index = datamuse_api_max
        return extract_sample(ff_words[:ending_index], sample_size=sample_size - 3) + \
               extract_sample(sort_by_rarity(ff_words)[:ending_index], sample_size=sample_size - 3)
    return extract_sample(ff_words, sample_size=sample_size)  # Standard sampling


def frequently_following_word(input_word, datamuse_api_max=10) -> Optional[str]:
    """Return a random word that frequently follows the given word if at least one can be found using the Datamuse API.

    :param input_word: the word which this function is looking up a frequently following word of
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's results are
                             always sorted from most to least similar sounding (according to a numeric score provided
                             by Datamuse).
    """
    result: Optional[str] = next(iter(frequently_following_words(input_word, sample_size=1,
                                                                 datamuse_api_max=datamuse_api_max)), None)
    return result
    # if weight_by_rarity:
    #     word = random.choice(sort_by_rarity(frequently_following_words(
    #         input_word, sample_size=None, datamuse_api_max=20))[:4])
    # else:
    # word = next(iter(frequently_following_words(input_word, sample_size=1, datamuse_api_max=datamuse_api_max)), None)
    # return word


def phonetically_related_words(input_val: str_or_list_of_str, sample_size=None, datamuse_api_max=50) -> list:
    """Returns a list of rhymes and similar sounding words to a word or list of words.

    :param input_val: the word or words in relation to which this function is looking up phonetically related words
    :param sample_size: If provided, pass this argument to the functions rhymes and similar_sounding_words so that
                         twice this number of elements are returned by this function. If not provided, the function
                         will return all rhymes plus however many API results similar_sounding_words.
    :param datamuse_api_max: specifies how many API results can be returned by the API client when fetching similar
                        meaning words.
    """
    input_words = validate_str_or_list_of_str(input_val)
    pr_words: List[str] = []
    for word in input_words:
        pr_words.extend(rhymes(word, sample_size=sample_size))
        exclude_words = pr_words.copy()
        pr_words.extend(filter_word_list(similar_sounding_words(
            word, sample_size=sample_size, datamuse_api_max=datamuse_api_max), exclude_words=exclude_words))
        if sample_size and sample_size - 1 < len(pr_words):
            pr_words = random.sample(pr_words, k=sample_size)
    return pr_words


def related_rare_words(input_val: str_or_list_of_str, sample_size: Optional[int] = 8,
                       rare_word_population_max: int = 20) -> list:
    """Return a random sample of rare related words to a given word. The words can be related phonetically,
    contextually, or by meaning).

    :param input_val: the word or words in relation to which this function is looking up related rare words
    :param sample_size: If provided, return a random sample of this many elements. If this number is greater than
                        the length of rare word population size, then just return a shuffled copy of that.
    :param rare_word_population_max: specifies the maximum number of related words to subsample from per word.
    `                                The rare word population is sorted from rarest to most common. If sample_size is
                                     null, the max results returned by this function is 2 times this number.
    """
    input_words = validate_str_or_list_of_str(input_val)
    results: List[str] = []
    for input_word in input_words:
        related_words = phonetically_related_words(input_word)
        related_words.extend(word for word in contextually_linked_words(
            input_word, sample_size=None, datamuse_api_max=100) if word not in related_words)
        related_words.extend(word for word in similar_meaning_words(
            input_word, sample_size=None, datamuse_api_max=100) if word not in related_words)
        related_words = [word for word in related_words if not too_similar(input_word, word)]
        results.extend(sort_by_rarity(related_words)[:rare_word_population_max])
    return extract_sample(results, sample_size=sample_size)


def related_rare_word(input_word: str, rare_word_population_max: int = 10) -> Optional[str]:
    """Return a random rare related word to a given word. The word can be related phonetically, contextually, or by
    meaning).

    :param input_word: the word which this function is looking up related rare words to
    :param rare_word_population_max: specifies the maximum number of related words to subsample from. The rare word
                                    population is sorted from rarest to most common.
    """
    return next(iter(related_rare_words(input_word, sample_size=1,
                                        rare_word_population_max=rare_word_population_max)), None)