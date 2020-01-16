from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem, SubmenuItem, CommandItem
from generativepoetry.pdf import *

menu = ConsoleMenu("Generative Poetry Menu", "What kind of poem would you like to generate?")

def futurist_poem_action():
    fppg = FuturistPoemPDFGenerator()
    fppg.generate_pdf()

def markov_poem_action():
    mppg = MarkovPoemPDFGenerator()
    mppg.generate_pdf()

def chaotic_concrete_poem_action():
    ccppg = ChaoticConcretePoemPDFGenerator()
    ccppg.generate_pdf()

def character_soup_poem_action():
    csppg = CharacterSoupPoemPDFGenerator()
    csppg.generate_pdf()

def stopword_soup_poem_action():
    ssppg = StopwordSoupPoemPDFGenerator()
    ssppg.generate_pdf()

#Create menu items for each choice you need:
futurist_function_item = FunctionItem("Futurist Poem", futurist_poem_action)
markov_function_item = FunctionItem("Stochastic Jolatic (Markov) Poem", markov_poem_action)
chaotic_concrete_function_item = FunctionItem("Chaotic Concrete Poem", chaotic_concrete_poem_action)
character_soup_function_item = FunctionItem("Character Soup Poem", character_soup_poem_action)
stopword_soup_function_item = FunctionItem("Stop Word Soup Poem", stopword_soup_poem_action)

#Add the items to the menu:
menu.append_item(futurist_function_item)
menu.append_item(markov_function_item)
menu.append_item(chaotic_concrete_function_item)
menu.append_item(character_soup_function_item)
menu.append_item(stopword_soup_function_item)

menu.start()
menu.join()