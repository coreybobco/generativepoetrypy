import random
from .lexigen import *
from .lexigen import has_invalid_characters, too_similar
from typing import List, Optional


class Poem:
    lines: List[str] = []

    def __init__(self, input_words, words_for_sampling):
        self.input_words = input_words
        self.words_for_sampling = words_for_sampling

    def __str__(self):
        return self.raw_text

    def update(self):
        self.raw_text = '\n'.join(lines)

    @property
    def previous_line(self):
        if len(self.lines):
            return self.lines[-1]
        return ''


class PoemGenerator:
    connectors = [' ', '   ', '...   ', random.choice([' & ', ' and ']), '  or  ', ' or ']
    line_enders = ['.', ', ', '!', '?', '', ' or', '...']
    line_indents = ['', '    ', '         ']
    common_words = ["the", "with", "in", "that", "not", "a", "an"]
    last_algorithms_used_to_reach_next_word = (None, None)
    currently_generating_poem = None
    last_poem = None

    def random_nonrhyme(self, previous_words: List[str]) -> str:
        """Return a random result of a random function that hits Project Datamuse API (rhyme function excluded)

        This function is primarily designed for use by the poem_line_from_markov function, but it may have other
        interesting uses. This is why it is designed to take all the previous words of a line, rather than just the
        last word. Some words do not have many/any result values for some of these API calls because they are
        too weird "weird" input values (i.e. proper nouns or slang), so to ensure the function returns a value,
        the function will try different random functions from the lexigen module with different words until a word is
        found that is both not too similar to preceding words and not too similar to the last line's last word.

        :param previous_words: an ordered list of previous words of generated poem line
        """
        result = None
        while result is None:
            # Randomly choose up to two algorithms the next word - one's repeated in this list for increased probability
            next_word_algorithms = [similar_sounding_word, similar_meaning_word, contextually_linked_word,
                                    frequently_following_word, frequently_following_word]
            nw_algorithms_copy = next_word_algorithms.copy()
            if self.last_algorithms_used_to_reach_next_word and self.last_algorithms_used_to_reach_next_word[0]:
                # Don't use the same algorithm for picking two successive words
                next_word_algorithms.remove(self.last_algorithms_used_to_reach_next_word[0])
            random_algorithm = random.choice(next_word_algorithms)
            input_word = previous_words[-1] if random.random() <=.75 else random.choice(previous_words)
            if random_algorithm != frequently_following_word and random.random() <= .25:
                if self.last_algorithms_used_to_reach_next_word and self.last_algorithms_used_to_reach_next_word[1]:
                    # Same goe for the 2nd algorithm used though this should be pretty rare
                    nw_algorithms_copy.remove(self.last_algorithms_used_to_reach_next_word[1])
                second_random_algorithm = random.choice(nw_algorithms_copy)
                possible_result = random_algorithm(input_word)
                possible_result = second_random_algorithm(possible_result) if possible_result else \
                    second_random_algorithm(input_word)
                self.last_algorithms_used_to_reach_next_word = (random_algorithm, second_random_algorithm)
            else:
                possible_result = random_algorithm(input_word)
                self.last_algorithms_used_to_reach_next_word = (random_algorithm, None)
            if possible_result and not too_similar(possible_result, previous_words) and \
                    not(len(self.currently_generating_poem.lines) > 0 and
                        too_similar(possible_result, self.currently_generating_poem.previous_line.split(' ')) and
                        not has_invalid_characters(possible_result)):
                # Is the word too similar to another word in the line or the previous line?
                # Does the word have numbers or spaces for some reason? (extremely rare)
                # If so, keep trying; otherwise exit the loop and return the word
                result = possible_result
        return result

    def last_word_of_markov_line(self, previous_words, rhyme_with=None) -> str:
        """Get the last word of a poem line generated by the markov algorithm and optionally try to make it rhyme.

        :param previous_words: an ordered list of previous words of generated poem line
        :param rhyme_with: the last word of the last line of the poem, if it exists
        """
        last_word = None
        if rhyme_with and rhyme_with not in self.common_words:
            last_word = rhyme(rhyme_with)
            if not last_word:
                while last_word is None or too_similar(last_word, previous_words):
                    last_word = self.random_nonrhyme(previous_words)
        else:
            while last_word is None or too_similar(last_word, previous_words):
                last_word = self.random_nonrhyme(previous_words)
        return last_word

    def nonlast_word_of_markov_line(self, previous_words: List[str], rhyme_with: Optional[str] = None,
                                    words_for_sampling: List[str] = []) -> str:
        """Get the next word of a poem line generated by the markov algorithm.

        :param previous_words: an ordered list of previous words of generated poem line
        :param rhyme_with: the last word of the last line of the poem, if it exists
        :param param words_for_sampling: a list of other words to throw in to the poem.
        """
        word = None
        if previous_words[-1] in self.common_words:
            if random.random() >= .66:
                word = self.random_nonrhyme(previous_words)
            else:
                while word is None or too_similar(word, previous_words):
                    word = random.choice(words_for_sampling)
        else:
            if len(words_for_sampling):
                threshold1, threshold2 = .66, 1
            else:
                threshold1, threshold2 = .5, 1
            while word is None or too_similar(word,  previous_words[-1]):
                randfloat = random.random()
                if randfloat > threshold1:
                    word = self.random_nonrhyme(previous_words)
                elif randfloat > threshold2:
                    word = random.choice(words_for_sampling)
                else:
                    word = frequently_following_word(previous_words[-1])
        return word

    def poem_line_from_markov(self, starting_word: str, num_words: int = 4, rhyme_with: Optional[str] = None,
                              words_for_sampling: List[str] = [], max_line_length: Optional[int] = 35) -> str:
        """Generate a line of poetry using a markov chain that optionally tries to make a line rhyme with the last one

        Different algorithms handle the last word and all the other words: both algorithms use a mix of random
        probability and process stopwords differently to keep the generated text interesting and non-repetitive.

        :param starting_word: the input word for the Markov algorithm, which hence is also the poem line's first word
        :param num_words: the number of words to write in the poem line
        :param rhyme_with: an optional word to try to make the poem line rhyme with. The algorithm will try something
                           else  if this word is a common stopword or if it can't find a rhyme though.
        :param words_for_sampling: a list of other words to throw in to the poem. If you don't know what to pass here,
                                   phonetically related words to the starting word probably adds some sonority.
        :param max_line_legnth: an upper limit in characters for the line -- important for PDF generation to keep
                                everything on the page.
        """
        output_words, previous_word = [starting_word], starting_word
        for i in range(num_words - 1):
            if (i == num_words - 2) or (max_line_length and len(' '.join(output_words)) >= max_line_length - 6):
                #  If the last word must rhyme with something
                word = self.last_word_of_markov_line(output_words, rhyme_with=rhyme_with)
            else:
                word = self.nonlast_word_of_markov_line(output_words, rhyme_with, words_for_sampling=words_for_sampling)
            output_words.append(word)
        return " ".join(output_words)

    def poem_from_markov(self, input_words, num_lines=10, min_line_words: int=5, max_line_words: int=9,
                         max_line_length: Optional[int] = 35) -> str:
        words_for_sampling = input_words + phonetically_related_words(input_words)
        self.currently_generating_poem = Poem(input_words, words_for_sampling)
        last_line_last_word = ''
        random.shuffle(words_for_sampling)
        print(words_for_sampling)
        for i in range(num_lines):
            rhyme_with = last_line_last_word if i % 2 == 1 else None
            line = self.poem_line_from_markov(words_for_sampling.pop(), words_for_sampling=words_for_sampling,
                                              num_words=random.randint(min_line_words, max_line_words),
                                              rhyme_with=rhyme_with, max_line_length=max_line_length)
            self.currently_generating_poem.lines.append(line)
            last_line_last_word = line.split(' ')[-1]
        self.last_poem = self.currently_generating_poem
        self.currently_generating_poem = None
        return self.last_poem

    def poem_line_from_word_list(self, word_list: List[str], max_line_length=35, connectors: List[str] = []) -> str:
        """Generate a line of a visual poem from a list of words by gluing them together with random connectors
           (whitespace, conjunctions, punctuation, and symbols).

        :param word_list: the words that will be used (in order, not randomly) that will form a visual poem
        :param max_line_length: upper limit on the length of the return value in characters
        :param connectors (list): list of glue strings
        """
        connectors = self.connectors if not len(connectors) else connectors
        output, last_word = word_list[0], word_list[0]
        last_connector = ''
        for word in word_list[1:]:
            if random.random() < (
                    .2 + len(output) / 100):  # Increasing probability of line termination as line gets longer
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

    def poem_from_word_list(self, input_word_list: List[str], num_lines: int = 6, max_line_length: int = 35,
                            connectors: List[str] = [], limit_line_to_one_input_word: bool = False):
        """Generate a visual poem from a list of words by taking a given input word list, adding the phonetically
           related words to that word list, and then using those words to create a visual/concrete poem.

        :param input_word_list: the list of user-provided words that will be used, along with phonetically related
                                words, to generate a poem
        :param max_line_length: upper limit on the length of the return value in characters
        :param max_line_length: upper limit on length of poem lines (excluding line ending punctuation) in characters
        :param connectors: list of glue strings
        :param limit_line_to_one_input_word: If true, when generating a line of poetry, only use words that are
                                             phonetically related to one input word.
        """
        connectors = self.connectors if not len(connectors) else connectors
        output, line_indent = '', ''
        if limit_line_to_one_input_word:
            for i in range(num_lines - 1):
                linked_word = random.choice(input_word_list)
                output += self.poem_line_from_word_list(phonetically_related_words(linked_word), connectors=connectors,
                                                        max_line_length=max_line_length)
                line_indent = random.choice(self.line_indents) if line_indent == '' else \
                    random.choice([li for li in self.line_indents if li is not line_indent])  # Don't repeat the same indent 2x
                output += random.choice(self.line_enders) + '\n' + line_indent
        else:
            word_list = input_word_list.copy()
            for word in input_word_list:
                word_list.extend(phonetically_related_words(word))
            for i in range(num_lines - 1):
                random.shuffle(word_list)
                output += self.poem_line_from_word_list(word_list, connectors=connectors,
                                                        max_line_length=max_line_length)
                # Don't repeat the same indent 2x
                line_indent = random.choice(self.line_indents) if line_indent == '' else \
                    random.choice([li for li in self.line_indents if li is not line_indent])
                output += random.choice(self.line_enders) + '\n' + line_indent

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