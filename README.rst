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

.. image:: example.png

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

.. code-block::

   # Import the module's functions first.
   from generativepoetry import *

Writing a Poem
""""""""""""""
Poem from word list requires a list of words--for non-programmers that means the list must have brackets, and each word must be surrounded by strings. I find using at least six words to be create more dynamic and interesting results using the same poem *recipe*.

.. code-block::

   # Print_poem just prints newlines before and after the poem so you can also use Python's print function.
   print_poem(poem_from_word_list(['crypt', 'lost', 'ghost', 'time', 'raven', 'ether']))
   # You can also control the number of lines and their width with the lines and max_line_length_arguments.
   # Lines defaults to 6 and max_line_length defaults to 35 characters, excluding line-ending punctuation
   # or conjunctions.
   print_poem(poem_from_word_list(['crypt', 'lost', 'ghost', 'time'], lines=9, max_line_length=25))
   # The following option makes it so each line uses only the phonetically related words of one input word
   print(poem_from_word_list(['crypt', 'lost', 'ghost', 'time'], link_line_to_input_word=True))

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
