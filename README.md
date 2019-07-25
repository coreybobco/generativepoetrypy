# Generative Poetry

[![Build Status](https://travis-ci.org/coreybobco/generativepoetry-py.svg?branch=master)](https://travis-ci.org/coreybobco/generativepoetry-py)  [![Coverage Status](https://coveralls.io/repos/github/coreybobco/generativepoetry-py/badge.svg?branch=master)](https://coveralls.io/github/coreybobco/generativepoetry-py?branch=master)
### What is this? 

This is primarily a library for procedurally generating [concrete poetry](https://en.wikipedia.org/wiki/Concrete_poetry) (a.k.a. visual poetry).

When provided a list of input words, a poem is generated using these words plus a broader group of words that are phonetically related to the list of input words. The words are joined by conjunctions and punctuation that is generally agnostic as to the surrounding word's part of speech, and spacing and indentation is randomized to emulate the characteristics visual poetry.

Using the [Datamuse API](https://pypi.org/project/python-datamuse/) and a rhyme dictionary, this library also can find rhymes, similar sounding words, similar meaning words, or intratextually statistically associated words (i.e. words that appears a lot within documents also containing word X). Because the sources return many extremely archaic words as well as abbreviations, some words are also filtered out.

Consequently, this library requires an internet connection to work properly. 

### Why should I care about mechanically generated poems? Is this really art?

The visual poems this produces are interesting for two reasons. As readers, we are trained to read horizontally and sometimes vertically, so we draw connections based on the spatial proximity of words on a page or on a screen. We also draw connections between words with similar meanings or similar sounds to one another. 

When reading these procedurally generated poems, it is easy to suspend one's disbelief and invent a context or reading for what is happening, or try to find a meaning or intention between a seemingly enigmatic or ambiguous word choice or phrasing when there is none. In this sense, these poems are similar to abstract paintings in which paint is thrown onto the canvas, or to a Rorschach test. They are, for the most part, suggestive optical illusions, engineered by chance and a choice palette of paints or words.

In this sense, these poems are similar to abstract paintings in which paint is thrown onto the canvas, or to a Rorschach test. They are, for the most part, suggestive optical illusions, engineered by chance and a choice palette of paints or words.

### Installation

##### Windows
Because this library currently relies on the Python package hunspell, which does not support Windows, use Docker. See below.

##### OSX

OSX users must install hunspell beforehand: `brew install hunspell`
Then download the en_US dictionary from http://wordlist.aspell.net/dicts/ and unzip it to /Library/Spelling/.

##### Linux

Ubuntu/Debian users should install libhunspell-dev beforehand:  `sudo apt-get install libhunspell-dev`

##### Docker
Use docker-compose to launch a container in which the module is installed and enter the Python interactive shell within.

```
docker-compose build .
docker-compose up -d
docker-compose run app python
```


Things to try:
```
from utils import *
# When sample_size is not provided, all results are returned.
rhymes('cool', sample_size=6)  # 6 random rhymes with cool, defaults to all rhymes
['ghoul', 'misrule', 'drool', 'rule', 'uncool', 'spool']
rhyme('cool')  # 1 at random

similar_sounding_words('cool', sample_size=6) # 6 random non-rhymes that sound similar to cool
['cowl', 'coal', 'coil', 'call', 'keel', 'kale']
similar_sounding_word('cool')  # 1 at random

phonetically_related_words('slimy')
['grimy', 'stymie', 'slammed', 'slammer', 'slim', 'seamy', 'slimy', 'slams', 'slime', 'slam', 'samey', 'semi', 'salami']
phonetically_related_words(['word', 'list'])  # Lists also work as input

similar_meaning_words('vampire', sample_size=8)  # Synonyms and other words with related meanings
similar_meaning_word('vampire')  # 1 at random

frequently_intratextually_coappearing_words('metamorphosis', sample_size=10)  # Words that statistically frequently appear in the same text('metamorphosis', sample_size=10)  # Words that statistically frequently appear in the same text
frequently_intratextually_coappearing_word('metamorphosis')  # 1 at random

print_poem(poem) # Adds a couple newlines around the poem so you can screenshot your creation in the terminal

print(poem_from_word_list(['crypt', 'lost', 'ghost', 'time']))
laced kept crypts  or  corrupt...   toast?
embossed & most...   corrupt  or  ripped!
riposte...   glossed
        lawsuit!
toast -> tame
    groped & team
        kept.
lawsuit -> glossed cast toast
        rhyme.
ghost time

# Other options
print(poem_from_word_list(['crypt', 'lost', 'ghost', 'time'], lines=3))  # Control the number of lines (defaults to 6)
# The following option makes it so each line uses only the phonetically related words of one input word
print(poem_from_word_list(['crypt', 'lost', 'ghost', 'time'], link_line_to_input_word=True))

```
