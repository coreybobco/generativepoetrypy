import random
import string
from os.path import isfile
from reportlab.pdfgen import canvas
from generativepoetry.poemgen import *
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, landscape
from nltk.corpus import stopwords
from prosedecomposer import *
from .utils import filter_word_list


class VisualPoemString():
    text = ''
    x = Nonetext = ''
    x = None
    y = None
    font = None
    font_size = None
    rgb = None
    y = None
    font = None
    font_size = None
    rgb = None

    def __init__(self):
        pass


class PDFGenerator:
    standard_font_sizes = [12, 14, 16, 18, 24, 32]
    font_choices = ['arial', 'arial-bold', 'arial-italic', 'arial-bolditalic',
                    'Courier-Bold', 'Courier-Bold', 'Courier-BoldOblique','Courier-BoldOblique',
                    'Helvetica', 'Helvetica-BoldOblique', 'Helvetica-Bold', 'Helvetica-Oblique',
                    'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman',
                    'Vera', 'VeraBd', 'VeraBI', 'VeraIt']
    orientation = 'landscape'

    def __init__(self):
        registerFont(TTFont('arial', 'arial.ttf'))
        registerFont(TTFont('arial-bold', 'arialbd.ttf'), )
        registerFont(TTFont('arial-italic', 'ariali.ttf'), )
        registerFont(TTFont('arial-bolditalic', 'arialbi.ttf'), )
        registerFont(TTFont('Vera', 'Vera.ttf'))
        registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
        registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
        registerFont(TTFont('VeraBI', 'VeraBI.ttf'))

    def get_font_size(self, line, font_sizes):
        if len(line) > 30:
            return 16
        elif len(line) >= 24:
            return random.choice([16, 18, 20])
        else:
            return random.choice(font_sizes)

    def get_max_x_coordinate(self, line, font_choice, font_size):
        if (font_size >= 23 and len(line) >= 17) or (font_size >= 20 and len(line) > 30) or \
                font_choice.startswith('Courier'):  # Courier is the widest
            return 30 if self.orientation == 'portrait' else 60
        elif (font_size == 23 and len(line) > 14) or (font_size >= 20 and len(line) > 16) or len(line) > 20:
            return 100 if self.orientation == 'portrait' else 130
        else:
            return 250 if self.orientation == 'portrait' else 280

    def get_filename(self, input_words, file_extension='pdf'):
        sequence = ""
        filename = f"{','.join(input_words)}{sequence}.{file_extension}"
        while isfile(filename):
            sequence = int(sequence or 0) + 1
            filename = f"{','.join(input_words)}({sequence}).{file_extension}"
        return filename

class ChaosPoemGenerator(PDFGenerator):

    def generate_pdf(self):
        input_words = get_input_words()
        output_words = input_words + phonetically_related_words(input_words)
        c = canvas.Canvas(f"{','.join(input_words)}.pdf")
        for word in output_words:
            word = random.choice([word, word, word, word.upper()])
            c.setFont(random.choice(self.font_choices), random.choice(self.standard_font_sizes))
            c.drawString(random.randint(15,450),random.randint(1,800), word)
        c.showPage()
        c.save()


class CharacterSoupPDFGenerator(PDFGenerator):
    standard_font_sizes = [6, 16, 32, 56, 64, 96]

    def generate_pdf(self):
        c = canvas.Canvas("character_soup.pdf")
        for i in range(20):
            c.setFillColorRGB(*self.get_random_color())
            char_sequence = random.choice([string.ascii_lowercase, string.ascii_lowercase, string.digits,
                                           string.punctuation])
            for char in char_sequence:
                char = random.choice([char, char, char.upper(), char.upper()]) \
                    if char_sequence == string.ascii_lowercase else char
                c.setFont(random.choice(self.font_choices), random.choice(self.standard_font_sizes))
                c.drawString(random.randint(15, 550), random.randint(1, 780), char)
        c.showPage()
        c.save()


class StopwordSoupPDFGenerator(PDFGenerator):
    standard_font_sizes = [6, 16, 24, 32, 48]

    def generate_pdf(self):
        c = canvas.Canvas("stopword_soup.pdf")
        punctuation = [char for char in string.punctuation]
        words_to_use = filter_word_list(stopwords.words('english')) + punctuation  # filter removes 1/2s of contractions
        for word in ['him', 'her', 'his', 'they', 'won']:
            words_to_use.remove(word)
        words_to_use.extend(['hmm', 'ah', 'umm', 'uh', 'ehh.', 'psst..', 'what?', 'oh?'])
        for word in words_to_use:
            c.setFillColorRGB(*self.get_random_color(threshold=.25))
            word = random.choice([word, word, word.upper(), word.upper()])
            font_size = random.choice(self.standard_font_sizes) if word in punctuation else \
                random.choice(self.standard_font_sizes)
            c.setFont(random.choice(self.font_choices), font_size)
            c.drawString(random.randint(15, 550), random.randint(1, 780), word)
            c.setFillColorRGB(*self.get_random_color(threshold=.25))
            complementary_punct = ''
            for char in word:
                complementary_punct += random.choice(punctuation)
            c.drawString(random.randint(15, 550), random.randint(1, 780), complementary_punct)
        c.showPage()
        c.save()


class MarkovPoemGenerator(PDFGenerator):

    def generate_pdf(self, orientation='landscape'):
        self.orientation = orientation
        if self.orientation.lower() == 'landscape':
            num_lines = 14
            y_coordinate = 550
            min_line_words = 6
            max_line_words = 10
            max_line_length = 66
            min_x_coordinate = 60
        elif self.orientation.lower() == 'portrait':
            num_lines = 24
            y_coordinate = 740
            min_line_words = 4
            max_line_words = 7
            max_line_length = 40
            min_x_coordinate = 15
        else:
            raise Exception('Must choose from the following orientations: portrait, landscape')
        regular_font_sizes = [15, 18, 21, 24, 28]
        input_words = get_input_words()
        poemgen = PoemGenerator()
        poem = poemgen.poem_from_markov(input_words=input_words, min_line_words=min_line_words, num_lines=num_lines,
                                        max_line_words=max_line_words, max_line_length=max_line_length)
        font_choice, last_font_choice = None, None
        filename = self.get_filename(input_words)
        if orientation == 'landscape':
            c = canvas.Canvas(filename, pagesize=landscape(letter))
        else:
            c = canvas.Canvas(filename)
        for line in poem.lines:
            line = random.choice([line, line, line, line.upper()])
            font_size = self.get_font_size(line, regular_font_sizes)
            while font_choice is None or last_font_choice == font_choice:
                font_choice = random.choice(self.font_choices)
            max_x_coordinate = self.get_max_x_coordinate(line, font_choice, font_size)
            c.setFont(font_choice, font_size)
            last_font_choice = font_choice
            x_coordinate = random.randint(min_x_coordinate, max_x_coordinate)
            c.drawString(x_coordinate, y_coordinate, line)
            y_coordinate -= 32
        c.showPage()
        c.save()


class FuturistPoemPDFGenerator():
    connectors = [' + ', ' - ', ' * ', ' % ', ' = ', ' != ', ' :: ']

    def generate(self):
        regular_font_sizes = [15, 18, 21, 24, 28]
        input_words = get_input_words()
        word_list = input_words + phonetically_related_words(input_words)
        poem_lines = []
        for i in range(25):
            random.shuffle(word_list)
            poem_lines.append(poem_line_from_word_list(word_list, connectors=self.connectors, max_line_length=40))
        c = canvas.Canvas(f"{','.join(input_words)}.pdf")
        y_coordinate = 60
        for line in poem_lines:
            line = random.choice([line, line, line, line.upper()])
            font_size = self.get_font_size(line, regular_font_sizes)
            max_x_coordinate = self.get_max_x_coordinate(line, font_size)
            c.setFont(random.choice(self.font_choices), font_size)
            c.drawString(random.randint(15, max_x_coordinate), y_coordinate, line)
            y_coordinate += 31
        c.showPage()
        c.save()


class VPoemFromListGenerator(PDFGenerator):

    def generate(poem_lines):
        regular_font_sizes = [15, 18, 21, 24, 28]
        word_list = input_words + phonetically_related_words(input_words)
        c = canvas.Canvas(f"{poem_lines[0]}.pdf")
        y_coordinate = 60
        for line in poem_lines:
            line = random.choice([line, line, line, line.upper()])
            font_size = self.get_font_size(line, regular_font_sizes)
            font_size = random.choice(font_sizes)
            max_x_coordinate = self.get_max_x_coordinate(line, font_size)
            c.setFont(random.choice(self.font_choices), font_size)
            c.drawString(random.randint(15, max_x_coordinate), y_coordinate, line)
            y_coordinate += 31
        c.showPage()
        c.save()