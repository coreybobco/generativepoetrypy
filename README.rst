Generative Poetry
=================


.. image:: https://travis-ci.org/coreybobco/generativepoetry-py.svg?branch=master
   :target: https://travis-ci.org/coreybobco/generativepoetry-py
   :alt: Build Status

.. image:: https://coveralls.io/repos/github/coreybobco/generativepoetry-py/badge.svg?branch=master
   :target: https://coveralls.io/github/coreybobco/generativepoetry-py?branch=master
   :alt: Coverage Status

.. image:: https://badge.fury.io/py/generativepoetry.svg
   :target: https://badge.fury.io/py/generativepoetry

What is this?
^^^^^^^^^^^^^

This is primarily a library for procedurally generating `concrete poetry <https://en.wikipedia.org/wiki/Concrete_poetry>`_ (a.k.a. visual poetry).

When provided a list of input words, a poem is generated using these words plus a broader group of words that are phonetically related to the list of input words. The words are joined by conjunctions and punctuation that is generally agnostic as to the surrounding word's part of speech, and spacing and indentation is randomized to emulate the characteristics visual poetry.

Using the `Datamuse API <https://pypi.org/project/python-datamuse/>`_ and a rhyme dictionary, this library also can find one or several rhymes, similar sounding words, similar meaning words, or intratextually statistically associated words (i.e. words that appears a lot within documents also containing word X). Because the sources return many extremely archaic words as well as abbreviations, some words are also filtered out. It allows for control of random sampling by both letting you choose the sample population size (# of API results returned, which are always returned by order of relevancy) and the sample size against that population.

Consequently, this library requires an internet connection to work properly.

Why should I care about mechanically generated poems? Is this really art?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The visual poems this produces are interesting for two reasons. As readers, we are trained to read horizontally and sometimes vertically, so we draw connections based on the spatial proximity of words on a page or on a screen. We also draw connections between words with similar meanings or similar sounds to one another.

When reading these procedurally generated poems, it is easy to suspend one's disbelief and invent a context or reading for what is happening, or try to find a meaning or intention between a seemingly enigmatic or ambiguous word choice or phrasing when there is none. In this sense, these poems are similar to abstract paintings in which paint is thrown onto the canvas, or to a Rorschach test. They are, for the most part, suggestive optical illusions, engineered by chance and a choice palette of words rather than paints.

In this sense, these poems are similar to abstract paintings in which paint is thrown onto the canvas, or to a Rorschach test. They are, for the most part, suggestive optical illusions, engineered by chance and a choice palette of paints or words.

By way of example, here are five concrete poems from the same recipe I collaged together using the same *recipe*: the words *paranoid*, *marinate*, *hysteria*, *radio*, *waves*, and *reverie*.

    .. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/collage.png

And here is an example of a generated Futurist visual poem (Futurism as in 1909 & F.T. Marinetti, not transhumanism -- see below).

    .. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/futurist_pdf.png

And here is a poem produced using Markov chain text generation using the various word sampling methods in this package's "lexigen" submodule.

    .. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/markov_pdf.png

This one's more abstract, or perhaps more concrete, and by that I mean concrete poetry, which deals more with spatial arrangement and usually lacked syntax:

    .. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/chaotic_concrete_pdf.png

But not as chaotic as this method of making "character soup":

.. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/character_soup_pdf.png

And this last one does the same thing but using stop words from NLTK along with "verbal stop words" like "um" and "ahem."

.. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/stopword_soup_pdf.png

Installation
^^^^^^^^^^^^

Windows
"""""""

Because this library currently relies on the Python package hunspell, which does not support Windows, use Docker to launch a Linux-based container, then use pip to install, and enter the Python interactive shell within:

.. code-block::

   docker run -t -d python python3 -m pip install generativepoetry && python3

OSX
"""

OSX users must install hunspell beforehand:

.. code-block::

   brew install hunspell

Then download the en_US dictionary from http://wordlist.aspell.net/dicts/ and unzip it to /Library/Spelling/.
Then install using pip with:

.. code-block::

   python3 -m pip install generativepoetry

Linux
"""""

Ubuntu/Debian users should install hunspell-en-us and libhunspell-dev beforehand:

.. code-block::

   sudo apt-get install hunspell-en-us libhunspell-dev

Then install using pip with:

.. code-block::

   python3 -m pip install generativepoetry

Things to try:
^^^^^^^^^^^^^^

Visual Poems Generated to PDF
"""""""""""""""""""""""""""""

Import the relevant submodule first.

.. code-block::

   from generativepoetry.lexigen import *

Markov Chain Based Poem PDF
"""""""""""""""""""""""""""

This method of poem generation asks the user for words as input, gets phonetically related words to those, and then uses both as ways to start lines, then using a probabilistic custom Markov chain based on previous words in a given line to derive the rest of the line.

.. code-block::

   mppgen = MarkovPoemPDFGenerator()
   mpgen.generate_pdf()  # This will ask for input words as input. 5 to 8 words is ideal.
   # Expected filename: word1,word2,word3,word4,word5,word6.pdf or the same with (1).pdf instead, etc.

Futurist Poem Generator
"""""""""""""""""""""""

In F.T. Marinetti's 1912 `Technical Manifesto of Futurist Literature <http://greeninteger.com/pdfs/marinetti-technical-manifesto-of-futurist-literature.pdf>`_, he proposes replacing conjunctios in language and poetry with mathematical operators and eliminating most parts of speech. In many ways this manifesto anticipates the syntax of programming languages. This method of poem generation connects random phonetically related words together with mathematical operators.

.. code-block::

   fpgen = FuturistPoemPDFGenerator()
   fpgen.generate_pdf()  # This will ask for input words as input. 5 to 8 words is ideal.
   # Expected filename: word1,word2,word3,word4,word5,word6.pdf or the same with (1).pdf instead, etc.

Chaos Poem PDF
""""""""""""""

This method of poem generation asks the user for words as input, gets phonetically related words to those to, and then draws those words at random X,Y coordinates on the page.

.. code-block::

   ccppgen = ChaoticConcretePoemPDFGenerator()
   ccppgen.generate_pdf()  # This will ask for input words as input. 5 to 8 words is ideal.
   # Expected filename: word1,word2,word3,word4,word5,word6.pdf or the same with (1).pdf instead, etc.

Character Soup Poem
"""""""""""""""""""

This method of poem generation draws characters (letters, numbers, special characters) at random X,Y coordinates on the page.

.. code-block::

   csppgen = CharacterSoupPoemPDFGenerator()
   csppgen.generate_pdf()  # No input required
   # Expected filename: character_soup.pdf

Stop Word Soup Poem
""""""""""""""""""

This method of poem generation draws stop words from NLTK's list (ex: the, and, of) as well as "verbal" stopwords (hmm, ah, umm, etc.) at random XY coordiantes on the page.

.. code-block::

   ssppgen = StopWordSoupPoemPDFGenerator()
   spppgen.generate_pdf()  # No input required
   # Expected filename: stopword_soup.pdf


Sonorous Visual Poem (Non-PDF)
""""""""""""""""""""""""""""""
This kind of poem requires a list of words as input--for non-programmers that means the list must have brackets, and each word must be surrounded by strings. I find using at least six words to be create more dynamic and interesting results using the same poem *recipe*.

.. code-block::

   # Import the module's functions first and instantiate a poem generator.
   from generativepoetry.poemgen import *
   pgen = PoemGenerator()
   # Print_poem just prints newlines before and after the poem so you can also use Python's print function.
   print_poem(poem_from_word_list(['crypt', 'lost', 'ghost', 'time', 'raven', 'ether']))
   # You can also control the number of lines and their width with the lines and max_line_length_arguments.
   # Lines defaults to 6 and max_line_length defaults to 35 characters, excluding line-ending punctuation
   # or conjunctions.
   print_poem(poem_from_word_list(['crypt', 'lost', 'ghost', 'time'], lines=9, max_line_length=25))
   # The following option makes it so each line uses only the phonetically related words of one input word
   print(poem_from_word_list(['crypt', 'lost', 'ghost', 'time'], link_line_to_input_word=True))

Word Sampling
"""""""""""""

Import the relevant submodule first.

.. code-block::

   from generativepoetry.lexigen import *

Rhymes
""""""

.. code-block::

   rhymes('cool')  # all words that rhyme with cool
   rhymes('cool', sample_size=6)  # 6 random words that rhyme with cool
   rhyme('cool')  # 1 at random

Similar sounding words
""""""""""""""""""""""

A similar sounding word is a word that does not rhyme with a word but sounds similar.

.. code-block::

   # To get all of the similar sounding words according to Project Datamuse:
   similar_sounding_word('cool', sample_size=None, datamuse_api_max=None)
   # To get the top 10 similar sounding words and then randomly select 5 from that:
   similar_sounding_words('cool', sample_size=5, datamuse_api_max=10)
   # When not provided, sample_size defaults to 6, and datamuse_api_max defaults to 20.
   # The same arguments can be optionally supplied to similar_sounding_word, which draws one word at random:
   similar_sounding_word('cool', sample_size=3, datamuse_api_max=15)
   similar_sounding_word('cool')

Phonetically related words
""""""""""""""""""""""""""
Phonetically related words are all of the rhymes and similar sounding words for a word or for a list of words

.. code-block::

   # It optionally accepts sample_size and datamuse_api_max to help the user control random sampling.
   # Note that datamuse_api_max will only be used to control the number of similar meaning words
   # initially fetched by the Datamuse API, however.
   phonetically_related_words('slimy')
   phonetically_related_words('slimy', sample_size=5, datamuse_api_max=15)
   phonetically_related_words(['word', 'list'])
   phonetically_related_words(['word', 'list'], sample_size=5, datamuse_api_max=15)

Similar meaning words
"""""""""""""""""""""
These include but aren't limited to synonyms; for example, spatula counts for spoon.

.. code-block::

   # To get all of the similar sounding words according to Project Datamuse:
   similar_meaning_words('vampire', sample_size=None, datamuse_api_max=None)
   # To get the top 10 similar sounding words and then randomly select 5 from that:
   similar_meaning_words('vampire', sample_size=5, datamuse_api_max=10)
   # When not provided, sample_size defaults to 6, and datamuse_api_max defaults to 20.
   # The same arguments can be optionally supplied to similar_meaning_word, which draws one word at random:
   similar_meaning_word('vampire', sample_size=8, datamuse_api_max=12)
   similar_meaning_word('vampire')

Contextually linked words
"""""""""""""""""""""""""

These are words that are often found in the same documents as a given word but don't necessarily have a related meaning. For example, metamorphosis and Kafka.

.. code-block::

   # To get all of the contextually linked words according to Project Datamuse:
   contextually_linked_words('metamorphosis', sample_size=None, datamuse_api_max=None)
   # To get the top 10 contextually linked words and then randomly select 5 from that:
   contextually_linked_words('metamorphosis', sample_size=5, datamuse_api_max=10)
   # When not provided, sample_size defaults to 6, and datamuse_api_max defaults to 20.
   # The same arguments can be optionally supplied to contextually_linked_word, which draws one word at random:
   contextually_linked_word('metamorphosis', sample_size=8, datamuse_api_max=12)
   contextually_linked_word('metamorphosis')

Related rare words
""""""""""""""""""

Finds a random sample of the rarest words that are related to a given input word, either phonetically, contextually, or by meaning.

.. code-block::

   # To get all of the related words to a given word:
   related_rare_words('spherical', sample_size=None, rare_word_population_max=None)
   # To get the top 10 rarest words and then randomly select 5 from that:
   related_rare_words('spherical', sample_size=5, rare_word_population_max=16)
   # When not provided, sample_size defaults to 8, and rare_word_population_max defaults to 20.
   # The same arguments can be optionally supplied to related_rare_word, which draws one word at random:
   related_rare_word('spherical', sample_size=8, rare_word_population_max=12)
   related_rare_word('spherical')

Frequently following words
""""""""""""""""""""""""""

These are words that frequently follow a given word in Project Datamuse's corpora.

.. code-block::

   # To get all of the frequently following words according to Project Datamuse:
   frequently_following_words('metamorphosis', sample_size=None, datamuse_api_max=None)
   # To get the top 10 frequently following words and then randomly select 5 from that:
   frequently_following_words('metamorphosis', sample_size=5, datamuse_api_max=10)
   # When not provided, sample_size defaults to 6, and datamuse_api_max defaults to 20.
   # The same arguments can be optionally supplied to frequently_following_word, which draws one word at random:
   frequently_following_word('metamorphosis', sample_size=8, datamuse_api_max=12)
   frequently_following_word('metamorphosis')