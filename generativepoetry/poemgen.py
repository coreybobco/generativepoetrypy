import itertools
from typing import List, Optional
from .lexigen import *
from .markov import MarkovWordGenerator
from .utils import too_similar


class Poem:

    def __init__(self, input_words, words_for_sampling):
        self.input_words = input_words
        self.words_for_sampling = words_for_sampling
        self.title = "'".join(input_words)
        self.lines: List[str] = []

    def __str__(self):
        return self.raw_text

    def update(self):
        self.raw_text = '\n'.join(self.lines)

    @property
    def previous_line(self):
        if len(self.lines):
            return self.lines[-1]
        return ''


class PoemGenerator:

    def __init__(self):
        self.default_connectors = [' ', '   ', '...   ', random.choice([' & ', ' and ']), '  or  ', ' or ']
        self.line_enders = ['.', ', ', '!', '?', '', ' or', '...']
        self.markov_line_enders = ['', '', ',', ',', '!', '.', '?']
        self.line_indents = ['', '    ', '         ']
        self.poem = None


    def poem_line_from_markov(self, starting_word: str, num_words: int = 4, rhyme_with: Optional[str] = None,
                              words_for_sampling: List[str] = [], max_line_length: Optional[int] = 35) -> str:
        """Generate a line of poetry using a markov chain that optionally tries to make a line rhyme with the last one

        Different algorithms handle the last word and all the other words: both algorithms use a mix of random
        probability and process stopwords differently to keep the generated text interesting and non-repetitive.

        :param starting_word: the input word for the Markov algorithm, which hence is also the poem line's first word
        :param num_words: the number of words to write in the poem line
        :param rhyme_with: an optional word to try to make the poem line rhyme with. The algorithm will try something
                           else if this word is a common stopword or if it can't find a rhyme though.
        :param words_for_sampling: a list of other words to throw in to the poem. If you don't know what to pass here,
                                   phonetically related words to the starting word probably adds some sonority.
        :param max_line_length: an upper limit in characters for the line -- important for PDF generation to keep
                                everything on the page.
        """
        output_words, previous_word = [starting_word], starting_word
        markovgen = MarkovWordGenerator(previous_lines=self.poem.lines)
        for i in range(num_words - 1):
            if (i == num_words - 2) or (max_line_length and (max_line_length > 14 and
                                                             len(' '.join(output_words)) >= max_line_length - 14)):
                # Checks if if it's the last word--the limit can be determined by either word count or character count
                max_word_length = 12 if max_line_length else None
                word = markovgen.last_word_of_markov_line(output_words, rhyme_with=rhyme_with,
                                                          max_length=max_word_length)
                output_words.append(word)
                break
            else:
                word = markovgen.nonlast_word_of_markov_line(output_words, words_for_sampling=words_for_sampling)
                output_words.append(word)
        return " ".join(output_words)

    def poem_from_markov(self, input_words, num_lines=10, min_line_words: int = 5, max_line_words: int = 9,
                         max_line_length: Optional[int] = 35) -> str:
        """Generate a line of poetry using a markov chain that optionally tries to make a line rhyme with the last one
            Different algorithms handle the last word and all the other words: both algorithms use a mix of random
            probability and process stopwords differently to keep the generated text interesting and non-repetitive.

        :param input words: the user provided words to try making a poem from
        :param num_lines: the number of lines the poem will have
        :param max_line_words: the maximum number of words a line may have
        :param words_for_sampling: a list of other words to throw in to the poem. If you don't know what to pass here,
                                   phonetically related words to the starting word probably adds some sonority.
        :param max_line_length: an upper limit in characters for the line -- important for PDF generation to keep
                                everything on the page.
            """
        self.poem = None
        words_for_sampling = input_words + phonetically_related_words(input_words, limit_results_per_input_word=20)
        # Check for undesirable similarity overlap in the words for sampling list
        similarity_checks = list(itertools.combinations(words_for_sampling, 2))
        words_removed = []
        for word_pair in similarity_checks:
            if not(word_pair[0] in words_removed or word_pair[1] in words_removed) and \
                    too_similar(word_pair[0], word_pair[1]):
                words_removed.append(random.choice([word_pair[0], word_pair[1]]))
                words_for_sampling.remove(words_removed[-1])

        self.poem = Poem(input_words, words_for_sampling)
        last_line_last_word = ''
        random.shuffle(words_for_sampling)
        line_enders = []
        for i in range(num_lines):
            rhyme_with = last_line_last_word if i % 2 == 1 else None
            # 67.5 % chance the line starts with an input word or something relate, 32.5% with a common word
            line_starter = words_for_sampling.pop() if random.random() > .4 else \
                    random.choice(MarkovWordGenerator.common_words)
            while i >= 1 and too_similar(line_starter, self.poem.lines[i - 1].split(' ')[0]):
                # while statement prevents repetition of line starters
                line_starter = words_for_sampling.pop() if random.random() > .4 else \
                    random.choice(MarkovWordGenerator.common_words)
            line = self.poem_line_from_markov(line_starter, words_for_sampling=words_for_sampling,
                                              num_words=random.randint(min_line_words, max_line_words),
                                              rhyme_with=rhyme_with, max_line_length=max_line_length)
            self.poem.lines.append(line)
            last_line_last_word = line.split(' ')[-1]
            # Directly adding line ender to line now will screw up rhyme pairs so save it & add it in another iteration
            line_enders.append(random.choice(self.markov_line_enders))
            print(line + line_enders[-1])
        for i, line in enumerate(self.poem.lines):
            self.poem.lines[i] += line_enders[i]
        poem = self.poem
        return poem

    def poem_line_from_word_list(self, word_list: List[str], max_line_length=35, connectors: List[str] = []) -> str:
        """Generate a line of a visual poem from a list of words by gluing them together with random connectors
           (whitespace, conjunctions, punctuation, and symbols).

        :param word_list: the words that will be used (in order, not randomly) that will form a visual poem
        :param max_line_length: upper limit on the length of the return value in characters
        :param connectors (list): list of glue strings
        """
        connectors = connectors if len(connectors) else self.default_connectors
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
        connectors = self.default_connectors if not len(connectors) else connectors
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