Generative Poetry
=================
A library primarily for procedurally generating visual poems

.. image:: https://travis-ci.org/coreybobco/generativepoetry-py.svg?branch=master
   :target: https://travis-ci.org/coreybobco/generativepoetry-py
   :alt: Build Status

.. image:: https://coveralls.io/repos/github/coreybobco/generativepoetry-py/badge.svg?branch=master
   :target: https://coveralls.io/github/coreybobco/generativepoetry-py?branch=master
   :alt: Coverage Status

.. image:: https://badge.fury.io/py/generativepoetry.svg
   :target: https://badge.fury.io/py/generativepoetry

Acknowledgements
^^^^^^^^^^^^^^^^
Conceptual writing handled by code is a fairly recent emergent field, so I would like to thank and acknowledge the following fellow travelers:

* Thanks to Allison Parrish, whose `pronouncing <https://github.com/aparrish/pronouncingpy>`_ package I used. Parrish's poetic computation projects and poetry, such as `Articulations <http://counterpathpress.org/articulations-allison-parrish>`_, have also been highly inspiring.
* Leonard Richardson's `olipy <https://github.com/leonardr/olipy/>`_ is another generative text software library with similar (Oulipian) concerns to my own which experiments with Markov chains, Queneau assembly, and has other fun miscellaneous functions like swapping letters in a text with corrupt ASCII versions.
* Riley Wong's `poetry theremin <https://github.com/rileynwong/rpi-poetry-generator>`_ transforms light sensor values into visual poems composed from words sampled from the poetry of the great modernist Mina Loy as well as Allen Ginsberg and William Carlos Williams, among others.

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

Then download the en_US dictionary from http://wordlist.aspell.net/dicts/ and unzip it to /Library/Spelling/ and install using pip:

.. code-block::

   python3 -m pip install generativepoetry

You will also need Microsoft's core font TTF files in /Library/Fonts/.

Linux
"""""

Ubuntu/Debian users should install hunspell-en-us and libhunspell-dev beforehand and then install with pip:

.. code-block::

   sudo apt-get install hunspell-en-us libhunspell-dev
   python3 -m pip install generativepoetry

What is this?
^^^^^^^^^^^^^
This software library contains various constraint-based procedures for stochastically generating `concrete poetry <https://en.wikipedia.org/wiki/Concrete_poetry>`_ (a.k.a. visual poetry) as a PDF or to the terminal. Most of these procedures are interactive and designed to be used and re-used once you learn to "play the game" by exploiting the rules of the procedure. All these procedures rely on common building blocks, after all. When you provide a list of input words, hidden algorithms find words related to those: phonetically or by way of meaning or context (more on this below). The words are then joined with various connectors depending on the procedure: random conjunctions and punctuation, related words (often creating stochastically generated puns and prosody as well as aberrations of syntax), mathematical symbols, uniform space, variable space.

The visual poems this produces are interesting for two reasons. As readers, we are trained to read horizontally and sometimes vertically, so we draw connections based on the spatial proximity of words on a page or on a screen. We also draw connections between words with similar meanings or similar sounds to one another. When reading many of these procedurally generated poems, it is easy to suspend one's disbelief and invent a context or reading for what is happening, or try to find a meaning or intention in a seemingly enigmatic or ambiguous word choice or phrasing when the execution of the code, which is not a human author, had no ascribed intents. In this sense, these poems are similar to abstract paintings in which paint is thrown onto the canvas, or to a Rorschach test. They are, for the most part, suggestive optical illusions, engineered by chance and a choice palette of words rather than paints. Nonetheless, the way some lines weave between prosody, pun, meaning, syntax and all these elements' destruction in pure nonsense creates an amusing and unique 21st century voice that reflects the chaotic nature of the Internet itself, home to literary gems and templated spam alike, and the questionable faith of many in the eventual emergence of a sentient artificial intelligence capable of thought and writing which adopts human concerns, style, and syntax.

This project was heavily inspired by Oulipo, the literary movement founded in 1960 short for a phrase best translated as "workshop of potential literature" whose ranks included Raymond Queneau, Italo Calvino, and Georges Perec. According to Marjorie Perloff, whose work on concrete poetry and copying Unoriginal Genius was also a great inspiration for this project, "the Oulipo constraint is a generative device:  it creates a formal structure whose rules of composition are internalized so that the constraint in question is not only a rule but a thematic property of the poem." Due respect also must be given to Alastair Brotchie's `Book Of Surrealist Games <https://monoskop.org/images/e/e0/Brotchie_Alastair_Gooding_Mel_eds_A_Book_of_Surrealist_Games_1995.pdf>`_, which has taught me to keep experimenting and combining procedures, just as the Surrealist Groups have done in practice. The conceptual artist is often stereotyped as too wedded to the pure product of the procedure, but I find this attitude unhelpful; sometimes algorithmic output needs an edit, a remix, or some other medium touched by human hands to shine.

By way of example, here are five concrete poems from the same recipe I digitally collaged together using the same *procedure*: the words *paranoid*, *marinate*, *hysteria*, *radio*, *waves*, and *reverie*.

.. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/collage.png

How do these procedures find related words, utilize random sampling, and filter out stuff like acronyms?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
This project uses the CMU rhyming dictionary along with `Datamuse API <https://pypi.org/project/python-datamuse/>`_, which can find similar sounding words, similar meaning words, frequently following words, or contextually linked words for a given word. (A contextually linked word is a word that appears frequently on the Internet in the same document as another word: metamorphosis is contextually linked to the word Kafka, for example. However, CMU and Datamuse return many *extremely* archaic words (e.g. medieval English variants of words) as well as abbreviations, extremely uncommon words and abbreviations are mostly filtered out when the words are fetched.

This all occurs in the package's lexigen submodule, where, if you decide to import this to make your own generative text project, you can also tweak function parameters to have more or less Datamuse API results returned. Since Project Datamuse always orders their API results by relevancy (e.g. most to least similar sounding), it is possible to tweak the number of API results returned before this package randomly samples one of those words or a subset of those words in order to adjust the level of dynamism/chaos and structure/repetition in generated output.

What are these artistic procedures and what can one make with them?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Technical Implementation of Futurist Literature
"""""""""""""""""""""""""""""""""""""""""""""""

In F.T. Marinetti's 1912 `Technical Manifesto of Futurist Literature <http://greeninteger.com/pdfs/marinetti-technical-manifesto-of-futurist-literature.pdf>`_, he proposes replacing conjunctions in language with mathematical operators and eliminating most parts of speech to make a poetry of becoming and shifting velocities. In many ways this manifesto anticipates the syntax of programming languages. This method of poem generation connects random phonetically related words together with mathematical operators.

Marinetti took himself far too seriously, however. This project is more in the spirit of pataphysics which Alfred Jarry defined as "the science of imaginary solutions, which symbolically attributes the properties of objects, described by their virtuality, to their lineaments" (c.f. `Exploits and Opinions of Doctor Faustroll, Pataphysician <http://libgen.is/book/index.php?md5=213C8D9CFDF94D5CB849372FEE7D9C77>`_). This original 1894 meaning of 'virtuality' did not carry connotations of computation but instead those of the philosophy of his professor Henri Bergson, who attempted to rethink the metaphysics of space and time in terms of "matter and memory," e.g. the matter of the world as we perceive it vs. the layers of connotations and relationships of meaning we inevitably bring into any act of perception, linguistic creatures that we are. Nonetheless today virtuality comprises the digital world as well, and it is fitting that Jarry also wrote: "'Pataphysics will be, above all, the science of the particular, despite the common opinion that the only science is that of the general. 'Pataphysics will examine the laws governing exceptions, and will explain the universe supplementary to this one." I assure you this project implements exception handling. For more on the relationship between pataphysics and computation, see Andrew Hugill's `Pataphysics And Computing <http://andrewhugill.com/writings/Pataphysics%20and%20Computing.pdf>`_.

Below is an example "Futurist poem" concerning pataphysics and surrealism. The following words were given as input: *logic*, *dialectic*, *critical*, *surreal*, and *pataphysics*.

.. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/futurist_pdf.png

Stochastic Jolastic: Markov Generation by Way of (Per)Mutation
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

This is the most complex generative method--it takes user-provided words and first gets phonetically related words to those words. It then randomly selects one of these phonetically related words, finds all the phonetically related words to that word, and picks one of those twice-removed results to begin a poem line. As the algorithms continue writing the line, they apply word transformations to previous words in the poem line (e.g. randomly selected similar meaning word, similar sounding word, contextually linked word, or frequently following word--see below) and there is also a 25% chance that another one of these operations is applied to the intermediate result. This means that there are often tens of thousands of results for the next word in a poem. The poem generator also forces line endings to rhyme in couplets.

The resultant stochastic emergence of puns and plays on words and cycle between sense and nonsense along with syntactic structure and anarchy remind me of James Joyce's Finnegan's Wake but were moreso inspired by another less known manifesto by Joyce's publisher and defender, Eugene Jolas, whose short and moving 1929 `Revolution of the Word <http://jot101ok.blogspot.com/2015/06/revolution-of-word-modernist-manifesto.html>`_ argued the poet "has the right to use words of his own fashioning and to disregard existing grammatical and syntactical laws." The generative implementation this Python package employs also occasionally switches world languages and makes cultural allusions (usually triggered by the frequently following word and contextually linked word functionality) which reminds me of Jolas' aspirations towards a Translatlantic multilingual poetry (for more on this, check out `this p+iece <http://writing.upenn.edu/epc/authors/perloff/jolas.html>`_ by Marjorie Perloff). Right now this occurs somewhat by accident--by errors in Project Datamuse's English vocabulary--but in the future this package will incorporate more world languages as Project Datamuse incorporates them, starting with Spanish, which was recently added to Project Datamuse.

This example poem was produced from the following input words: *anxious*, *spectacular*, *life*, *death*, *ascent*, *peace*, *tragedy*, and *love*.

.. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/markov_pdf.png

Chaotic Concrete Poem
"""""""""""""""""""""

This one's more abstract  but also more concrete, and by that I mean concrete poetry, which deals more with spatial arrangement and usually lacked syntax. The following words were given as input: *chaos*, *dissolve*, *fire*, *morph*, *devolve*, *shapeshifter*, *transient*, and *cluster*.

.. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/chaotic_concrete_pdf.png

Character Soup
""""""""""""""
But not as chaotic as this method of making "character soup". (This method of generation does not take input words.)

.. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/character_soup_pdf.png

Stop Word Soup
""""""""""""""
And this last one does the same thing but using stop words from NLTK along with "verbal stop words" like "um" and "ahem." (This method of generation does not take input words.)

.. image:: https://raw.githubusercontent.com/coreybobco/generativepoetry-py/master/example_images/stopword_soup_pdf.png

Things to try:
^^^^^^^^^^^^^^

Visual Poems Generated to PDF
"""""""""""""""""""""""""""""

Import the relevant submodule first.

.. code-block::

   from generativepoetry.pdf import *

Markov Chain Based Poem PDF
"""""""""""""""""""""""""""

.. code-block::

   mpgen = MarkovPoemPDFGenerator()
   mpgen.generate_pdf()  # This will ask for input words as input. 5 to 8 words is ideal.
   # Expected filename: word1,word2,word3,word4,word5,word6.pdf or the same with (1).pdf instead, etc.

Futurist Poem Generator
"""""""""""""""""""""""

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
"""""""""""""""""""

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
   print_poem(pgen.poem_from_word_list(['crypt', 'lost', 'ghost', 'time', 'raven', 'ether']))
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
