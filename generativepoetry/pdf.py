import random
import string
from prosedecomposer import *
from reportlab.pdfgen import canvas
from generativepoetry import *
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, landscape


class PDFGenerator:

    def __init__(self):
        registerFont(TTFont('arial', 'arial.ttf'))
        registerFont(TTFont('arial-bold', 'arialbd.ttf'), )
        registerFont(TTFont('arial-italic', 'ariali.ttf'), )
        registerFont(TTFont('arial-bolditalic', 'arialbi.ttf'), )
        registerFont(TTFont('Vera', 'Vera.ttf'))
        registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
        registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
        registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
        self.font_choices = ['arial', 'arial-bold', 'arial-italic', 'arial-bolditalic',
                             'Courier-Bold', 'Courier-Bold', 'Courier-BoldOblique','Courier-BoldOblique',
                             'Helvetica', 'Helvetica-BoldOblique', 'Helvetica-Bold', 'Helvetica-Oblique',
                             'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman',
                             'Vera', 'VeraBd', 'VeraBI', 'VeraIt']
        self.standard_font_sizes = [12, 14, 16, 18, 24, 32]

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
            return 30
        elif (font_size == 23 and len(line) > 14) or (font_size >= 20 and len(line) > 16) or len(line) > 20:
            return 100
        else:
            return 250

    def get_input_words(self):
        print("Type some words separated by commas to generate a poem.")
        return input().split(',')


class ChaosPoemGenerator(PDFGenerator):

    def generate_pdf(self):
        input_words = self.get_input_words()
        output_words = input_words + phonetically_related_words(input_words)
        c = canvas.Canvas(f"{','.join(input_words)}.pdf")
        for word in output_words:
            word = random.choice([word, word, word, word.upper()])
            c.setFont(random.choice(self.font_choices), random.choice(self.standard_font_sizes))
            c.drawString(random.randint(15,450),random.randint(1,800), word)
        c.showPage()
        c.save()


class AlphabetSoupPoemGenerator(PDFGenerator):

    def generate_pdf(self):
        c = canvas.Canvas("alphabet.pdf")
        for i in range(100):
            for line in string.ascii_lowercase:
                line = random.choice([line, line, line.upper(), line.upper()])
                c.setFont(random.choice(self.font_choices), random.choice(self.standard_font_sizes))
                c.drawString(random.randint(15, 650), random.randint(1, 800), line)
        c.showPage()
        c.save()


class MarkovPoemGenerator(PDFGenerator):

    def generate_pdf(self, orientation='landscape'):
        if orientation.lower() == 'landscape':
            num_lines = 16
            y_coordinate = 580
            min_line_words = 8
            max_line_words = 13
        elif orientation.lower() == 'portrait':
            num_lines = 24
            y_coordinate = 780
            min_line_words = 4
            max_line_words = 7
        else:
            raise Exception('Must choose from the following orientations: portrait, landscape')
        regular_font_sizes = [15, 18, 21, 24, 28]
        input_words = self.get_input_words()
        words_for_sampling = input_words + phonetically_related_words(input_words)
        poem_lines = []
        last_line_last_word = ''
        font_choice, last_font_choice = None, None
        random.shuffle(words_for_sampling)
        for i in range(num_lines):
            rhyme_with = last_line_last_word if i % 2 == 1 else None
            line = poem_line_from_markov(words_for_sampling.pop(), words_for_sampling=words_for_sampling,
                                         num_words=random.randint(min_line_words,max_line_words), rhyme_with=rhyme_with,
                                         max_line_length=40)
            print(line)
            poem_lines.append(line)
            last_line_last_word = line.split(' ')[-1]
        if orientation == 'landscape':
            c = canvas.Canvas(f"{','.join(input_words)}.pdf", pagesize=landscape(letter))
        else:
            c = canvas.Canvas(f"{','.join(input_words)}.pdf")
        for line in poem_lines:
            line = random.choice([line, line, line, line.upper()])
            font_size = self.get_font_size(line, regular_font_sizes)
            while font_choice is None or last_font_choice == font_choice:
                font_choice = random.choice(self.font_choices)
            max_x_coordinate = self.get_max_x_coordinate(line, font_choice, font_size)
            c.setFont(font_choice, font_size)
            last_font_choice = font_choice
            c.drawString(random.randint(15, max_x_coordinate), y_coordinate, line)
            y_coordinate -= 32
        c.showPage()
        c.save()


class FuturistPoemPDFGenerator():
    connectors = [' + ', ' - ', ' * ', ' % ', ' = ', ' != ', ' :: ']

    def generate(self):
        regular_font_sizes = [15, 18, 21, 24, 28]
        input_words = self.get_input_words()
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