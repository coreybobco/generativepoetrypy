import random
from typing import List, TypeVar, Optional
import pronouncing
from datamuse import datamuse
from .utils import *

api = datamuse.Datamuse()
str_or_list_of_str = TypeVar('str_or_list_of_str', str, List[str])


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
        random.shuffle(ff_words)
    if sample_size and sample_size > 4:
        # Pick 3 at random from the top X rarest and the rest from the whole
        # Slice one list of api results using the default order and another using a rarity baeed order
        if not datamuse_api_max:
            ending_index = 20
        elif datamuse_api_max % 2 == 1:
            ending_index = datamuse_api_max + 1
        else:
            ending_index = datamuse_api_max
        return extract_sample(ff_words[:ending_index], sample_size=sample_size - 3) + \
            extract_sample(sort_by_rarity(ff_words)[:ending_index], sample_size=3)
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


def phonetically_related_words(input_val: str_or_list_of_str, sample_size=None, datamuse_api_max=50,
                               limit_results_per_input_word: Optional[int] = None) -> list:
    """Returns a list of rhymes and similar sounding words to a word or list of words.

    :param input_val: the word or words in relation to which this function is looking up phonetically related words
    :param sample_size: If provided, pass this argument to the functions rhymes and similar_sounding_words so that
                         twice this number of elements are returned by this function. If not provided, the function
                         will return all rhymes plus however many API results similar_sounding_words.
    :param datamuse_api_max: specifies how many API results can be returned by the API client when fetching similar
                        meaning words.
    """
    input_words = validate_str_or_list_of_str(input_val)
    results: List[str] = []
    for word in input_words:
        results.extend(rhymes(word, sample_size=limit_results_per_input_word))
        exclude_words = results.copy()
        nonrhymes = filter_word_list(similar_sounding_words(
            word, sample_size=sample_size, datamuse_api_max=datamuse_api_max), exclude_words=exclude_words)
        results.extend(nonrhymes[:limit_results_per_input_word])
    results = extract_sample(results, sample_size=sample_size)
    return results


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