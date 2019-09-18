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

__all__ = ['rhymes', 'rhyme', 'similar_sounding_word', 'similar_sounding_words', 'similar_meaning_word',
           'similar_meaning_words', 'contextually_linked_word', 'contextually_linked_words', 'phonetically_related_words',
           'related_rare_words', 'related_rare_word', 'sort_by_rarity', 'frequently_following_words',
           'frequently_following_word', 'poem_line_from_word_list', 'poem_line_from_markov', 'random_nonrhyme',
           'poem_from_word_list', 'print_poem']

api = datamuse.Datamuse()
default_connectors = [' ', '   ', '...   ', random.choice([' & ', ' and ']), '  or  ', ' or ']
line_enders = ['.', ', ', '!', '?', '', ' or', '...']
line_indents = ['', '    ', '         ']
common_words = ["the", "with", "in", "that", "not", "a", "an"]
word_frequency_threshold = 4e-08
str_or_list_of_str = TypeVar('str_or_list_of_str', str, List[str])
annoying_words = ['thew', 'iii', 'arr']

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
    exclude_words.extend(annoying_words)  # Some words Datamuse tends to return that disruptive poetic flow
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


def contextually_linked_words(input_val: str_or_list_of_str, sample_size: Optional[int] = 6, datamuse_api_max: Optional[int] = 20) \
        -> list:
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


def frequently_following_words(input_val: str_or_list_of_str, sample_size: Optional[int] = 6, datamuse_api_max: Optional[int] = 20) \
        -> list:
    """Return a list of words that frequently follow the given word, in randomized order, if at least one can be found
    using the Datamuse API.

    :param input_val: the word or words in relation to which this function is looking up frequently following words
    :param sample_size: If provided, return a random sample of this many elements. If this number is greater than
                             the length of the API results, then just return a shuffled copy of the filtered API
                             results.
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's
                                  results are always sorted from most to least frequently coappearing (according to a
                                  numeric score provided by Datamuse), hence by using both parameters, one can control the
                                  size of both the sample pool and the sample size.
    """
    input_words = validate_str_or_list_of_str(input_val)
    ff_words: List[str] = []
    for input_word in input_words:
        response = api.words(lc=input_word, max=datamuse_api_max) if datamuse_api_max else api.words(lc=input_word)
        # Filter but don't use spellcheck -- it removes important words (for the markov chain use case) like 'of'
        exclude_words = ff_words.copy()
        ff_words.extend(filter_word_list([obj['word'] for obj in response], spellcheck=False,
                                         exclude_words=exclude_words))
    return extract_sample(ff_words, sample_size=sample_size)


def frequently_following_word(input_word, datamuse_api_max=10, weight_by_rarity: bool = False) -> Optional[str]:
    """Return a random word that frequently follows the given word if at least one can be found using the Datamuse API.

    :param input_word: the word which this function is looking up a frequently following word of
    :param datamuse_api_max: specifies the maximum number of results returned by the API. The API client's results are
                             always sorted from most to least similar sounding (according to a numeric score provided
                             by Datamuse).
    :param weight_by_rarity: If true, select from the top 4 rarest words of the frequently following words results
    """
    word: Optional[str]
    if weight_by_rarity:
        word = random.choice(sort_by_rarity(frequently_following_words(
            input_word, sample_size=None, datamuse_api_max=20))[:4])
    else:
        word = next(iter(frequently_following_words(
            input_word, sample_size=1,datamuse_api_max=datamuse_api_max)), None)
    return word


def phonetically_related_words(input_val: str_or_list_of_str, sample_size=None, datamuse_api_max=50) -> list:
    """Get a list of rhymes and similar sounding words to a word or list of words.

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


def poem_line_from_word_list(word_list: List[str], max_line_length=35, connectors=default_connectors) -> str:
    """Generate a line of a visual poem from a list of words by gluing them together with random connectors (whitespace,
       conjunctions, punctuation, and symbols).

    :param word_list: the words that will be used (in order, not randomly) that will form a visual poem
    :param max_line_length: upper limit on the length of the return value in characters
    :param connectors (list): list of glue strings
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


def last_word_of_markov_line(previous_words, rhyme_with=None) -> str:
    """Get the last word of a poem line generated by the markov algorithm and optionally try to make it rhyme.

    :param previous_words: an ordered list of previous words of generated poem line
    :param rhyme_with: the last word of the last line of the poem, if it exists
    """
    last_word = None
    if rhyme_with and rhyme_with not in common_words:
        last_word = rhyme(rhyme_with)
        if not last_word:
            while last_word is None:
                last_word = random_nonrhyme(previous_words, rhyme_with)
    else:
        while last_word is None:
            last_word = random_nonrhyme(previous_words, rhyme_with)
    return last_word


def nonlast_word_of_markov_line(previous_words: List[str], rhyme_with: Optional[str] = None,
                                words_for_sampling: List[str] = []) -> str:
    """Get the next word of a poem line generated by the markov algorithm.

    :param previous_words: an ordered list of previous words of generated poem line
    :param rhyme_with: the last word of the last line of the poem, if it exists
    :param param words_for_sampling: a list of other words to throw in to the poem.
    """
    word = None
    if previous_words[-1] in common_words:
        if random.random() >= .66:
            word = random_nonrhyme(previous_words, rhyme_with)
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
                word = random_nonrhyme(previous_words, rhyme_with)
            elif randfloat > threshold2:
                word = random.choice(words_for_sampling)
            else:
                word = frequently_following_word(previous_words[-1], weight_by_rarity=False)
    return word


def random_nonrhyme(previous_words: List[str], rhyme_with: Optional[str] = None) -> str:
    """Return a random result of a random function that hits Project Datamuse API (rhyme function excluded)

    This function is primarily designed for use by the poem_line_from_markov function, but it may have other interesting
    uses, so it is public. This is why it is designed to take all the previous words of a line, rather than just the
    last word. Some words do not have many/any result values for some of these API calls because they are "weird" input
    values (i.e. proper nouns), so to ensure the function returns a value, it will try different random functions and
    different words until a word is found that is both not too similar to preceding words and not too similar to the
    last line's last word.

    :param previous_words: an ordered list of previous words of generated poem line
    :param rhyme_with: the last word of the last line of the poem, if it exists
    """
    result = None
    while result is None:
        if random.random() <= .7 and rhyme_with:
            next_word_algorithms = [similar_sounding_word, similar_meaning_word, contextually_linked_word]
            possible_result = random.choice(next_word_algorithms)(rhyme_with)
        else:
            if random.random() >= .5:
                possible_result = frequently_following_word(previous_words[-1], weight_by_rarity=True)
            else:
                possible_result = similar_sounding_word(random.choice(previous_words))
        if possible_result and not too_similar(possible_result, previous_words) and \
                not(rhyme_with and too_similar(possible_result, rhyme_with)):
            result = possible_result
    return result


def poem_line_from_markov(starting_word: str, num_words: int = 4, rhyme_with: Optional[str] = None,
                          words_for_sampling: List[str] = [], max_line_length: Optional[int] = 35) -> str:
    """Generate a line of poetry using a markov chain that optionally tries to make a line rhyme with the last one

    Different algorithms handle the last word and all the other words: both algorithms use a mix of random probability
    and process stopwords differently to keep the generated text interesting and non-repetitive.

    :param starting_word: the input word for the Markov algorithm, which hence is also the poem line's first word
    :param num_words: the number of words to write in the poem line
    :param rhyme_with: an optional word to try to make the poem line rhyme with. The algorithm will try something else
                       if this word is a common stopword or if it can't find a rhyme though.
    :param words_for_sampling: a list of other words to throw in to the poem. If you don't know what to pass here,
                               phonetically related words to the starting word probably adds some sonority.
    :param max_line_legnth: an upper limit in characters for the line -- important for PDF generation to keep everything
                            on the page.
    """
    output_words, previous_word = [starting_word], starting_word
    for i in range(num_words - 1):
        if (i == num_words - 2) or (max_line_length and len(' '.join(output_words)) >= max_line_length - 6):
            #  If the last word must rhyme with something
            word = last_word_of_markov_line(output_words, rhyme_with=rhyme_with)
        else:
            word = nonlast_word_of_markov_line(output_words, rhyme_with, words_for_sampling=words_for_sampling)
        output_words.append(word)
    return " ".join(output_words)


def poem_from_word_list(input_word_list: List[str], lines: int = 6, max_line_length: int = 35,
                        connectors: list = default_connectors, limit_line_to_one_input_word: bool = False):
    """Generate a visual poem from a list of words by taking a given input word list, adding the phonetically related
       words to that word list, and then using those words to create a visual/concrete poem.

    :param input_word_list: the list of user-provided words that will be used, along with phonetically related
                            words, to generate a poem
    :param max_line_length: upper limit on the length of the return value in characters
    :param max_line_length: upper limit on length of poem lines (excluding line ending punctuation) in characters
    :param connectors: list of glue strings
    :param limit_line_to_one_input_word: If true, when generating a line of poetry, only use words that are
                                         phonetically related to one input word.
    """
    output, line_indent = '', ''
    if limit_line_to_one_input_word:
        for i in range(lines - 1):
            linked_word = random.choice(input_word_list)
            output += poem_line_from_word_list(phonetically_related_words(linked_word), connectors=connectors,
                                               max_line_length=max_line_length)
            line_indent = random.choice(line_indents) if line_indent == '' else \
                random.choice([li for li in line_indents if li is not line_indent])  # Don't repeat the same indent 2x
            output += random.choice(line_enders) + '\n' + line_indent
    else:
        word_list = input_word_list.copy()
        for word in input_word_list:
            word_list.extend(phonetically_related_words(word))
        for i in range(lines - 1):
            random.shuffle(word_list)
            output += poem_line_from_word_list(word_list, connectors=connectors, max_line_length=max_line_length)
            line_indent = random.choice(line_indents) if line_indent == '' else \
                random.choice([li for li in line_indents if li is not line_indent])   # Don't repeat the same indent 2x
            output += random.choice(line_enders) + '\n'+ line_indent

    output += random.choice(input_word_list[:-1]) + ' ' + input_word_list[-1]
    return output


def print_poem(poem: str):
    """Print the poem with a newline before and after so it's easy to take a screenshot of its 'recipe' and the poem
    in your terminal and share it. :)

    :param poem: the poem, as a string, to be printed
    """
    print('\n')
    print(poem)
    print('\n')