import random
import string
from os.path import isfile
from typing import List, TypeVar, Tuple
from reportlab.pdfgen import canvas
from generativepoetry.poemgen import *
from reportlab.pdfbase.pdfmetrics import registerFont, registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import letter, landscape
from nltk.corpus import stopwords
from .utils import filter_word_list

rgb_tuple = Tuple[float]


class VisualPoemString():
    """The text drawn by reportlab at an XY coordinate--can be a line, a word, or just a character."""

    def __init__(self, text, x: int, y: int, font: str, font_size: int, rgb: Optional[Tuple] = None):
        self.text = text
        self.x = x
        self.y = y
        self.font = font
        self.font_size = font_size
        self.rgb = rgb


class PDFGenerator:
    default_font_sizes = [12, 14, 16, 18, 24, 32]
    font_choices = ['arial', 'arial-bold', 'arial-italic', 'arial-bolditalic',
                    'Courier-Bold', 'Courier-Bold', 'Courier-BoldOblique','Courier-BoldOblique',
                    'Helvetica', 'Helvetica-BoldOblique', 'Helvetica-Bold', 'Helvetica-Oblique',
                    'Times-Bold', 'Times-BoldItalic', 'Times-Italic', 'Times-Roman',
                    'Vera', 'VeraBd', 'VeraBI', 'VeraIt']

    def __init__(self):
        registerFont(TTFont('arial', 'arial.ttf'))
        registerFont(TTFont('arial-bold', 'arialbd.ttf'), )
        registerFont(TTFont('arial-italic', 'ariali.ttf'), )
        registerFont(TTFont('arial-bolditalic', 'arialbi.ttf'), )
        registerFont(TTFont('Vera', 'Vera.ttf'))
        registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
        registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
        registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
        self.orientation = 'landscape'
        self.drawn_strings: List[VisualPoemString] = []

    def get_font_size(self, line):
        if len(line) > 30:
            return 16
        elif len(line) >= 24:
            return random.choice([16, 18, 20])
        else:
            return random.choice(self.default_font_sizes)

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


class ChaoticConcretePoemPDFGenerator(PDFGenerator):

    def generate_pdf(self, max_words=Optional[int]):
        self.drawn_strings = []
        input_words = get_input_words()
        output_words = input_words + phonetically_related_words(input_words)
        random.shuffle(output_words)
        filename = self.get_filename(input_words)
        c = canvas.Canvas(filename)
        for word in output_words[:200]:
            word = random.choice([word, word, word, word.upper()])
            x = random.randint(15,440)
            y = random.randint(15, 800)
            font_choice = random.choice(self.font_choices)
            font_size = random.choice(self.default_font_sizes)
            rgb = get_random_color()
            vp_string = VisualPoemString(word, x=x, y=y, font=font_choice, font_size=font_size, rgb=rgb)
            c.setFont(vp_string.font, vp_string.font_size)
            c.setFillColorRGB(*vp_string.rgb)
            c.drawString(vp_string.x, vp_string.y, vp_string.text)
            self.drawn_strings.append(vp_string)
        c.showPage()
        c.save()


class CharacterSoupPoemPDFGenerator(PDFGenerator):

    def generate_pdf(self):
        c = canvas.Canvas("character_soup.pdf")
        for i in range(20):
            char_sequence = random.choice([string.ascii_lowercase, string.digits, string.punctuation])
            for char in char_sequence:
                char = random.choice([char, char, char.upper(), char.upper()]) \
                    if char_sequence == string.ascii_lowercase else char
                font_choice = random.choice(self.font_choices)
                font_size = random.randint(6, 72)
                x = random.randint(10, 560)
                y = random.randint(10, 790)
                rgb = get_random_color()
                vp_string = VisualPoemString(char, x=x, y=y, font=font_choice, font_size=font_size, rgb=rgb)
                c.setFillColorRGB(*rgb)
                c.setFont(vp_string.font, vp_string.font_size)
                c.drawString(vp_string.x, vp_string.y, vp_string.text)
                self.drawn_strings.append(vp_string)
        c.showPage()
        c.save()


class StopwordSoupPoemPDFGenerator(PDFGenerator):
    default_font_sizes = [6, 16, 24, 32, 48]

    def generate_pdf(self):
        c = canvas.Canvas("stopword_soup.pdf")
        punctuation = [char for char in string.punctuation]
        words_to_use = filter_word_list(stopwords.words('english')) + punctuation  # filter removes 1/2s of contractions
        for word in ['him', 'her', 'his', 'they', 'won']:
            words_to_use.remove(word)
        for i in range(3):
            words_to_use.extend(['hmm', 'ah', 'umm', 'uh', 'ehh.', 'psst..', 'what?', 'oh?', 'ahem..'])
        random.shuffle(words_to_use)
        for word in words_to_use:
            word = random.choice([word, word, word.upper(), word.upper()])
            font_choice = random.choice(self.font_choices)
            font_size = random.randint(6, 40)
            x = random.randint(10, 490)
            y = random.randint(10, 790)
            rgb = get_random_color(threshold=.5)
            c.setFillColorRGB(*rgb)
            vp_string = VisualPoemString(word, x=x, y=y, font=font_choice, font_size=font_size, rgb=rgb)
            c.setFont(vp_string.font, vp_string.font_size)
            c.drawString(vp_string.x, vp_string.y, vp_string.text)
            self.drawn_strings.append(vp_string)
        c.showPage()
        c.save()


class MarkovPoemPDFGenerator(PDFGenerator):
    default_font_sizes = [15, 18, 21, 24, 28]

    def generate_pdf(self, orientation: string = 'landscape'):
        self.drawn_strings = []
        self.orientation = orientation
        if self.orientation.lower() == 'landscape':
            num_lines = 14
            y_coordinate = 550
            min_line_words = 7
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
            text = random.choice([line, line, line, line.upper()])
            font_size = self.get_font_size(line)
            while font_choice is None or last_font_choice == font_choice:
                font_choice = random.choice(self.font_choices)
            max_x_coordinate = self.get_max_x_coordinate(line, font_choice, font_size)
            last_font_choice = font_choice
            x_coordinate = random.randint(min_x_coordinate, max_x_coordinate)
            vp_string = VisualPoemString(line, x=x_coordinate, y=y_coordinate, font=font_choice, font_size=font_size)
            c.setFont(vp_string.font, vp_string.font_size)
            c.drawString(vp_string.x, vp_string.y, vp_string.text)
            y_coordinate -= 32
            self.drawn_strings.append(vp_string)
        c.showPage()
        c.save()


class FuturistPoemPDFGenerator(PDFGenerator):
    connectors = [' + ', ' - ', ' * ', ' % ', ' = ', ' != ', ' :: ']
    default_font_sizes = [15, 18, 21, 24, 28]

    def generate_pdf(self):
        self.drawn_strings = []
        input_words = get_input_words()
        word_list = input_words + phonetically_related_words(input_words)
        poem_lines = []
        pgen = PoemGenerator()
        for i in range(25):
            random.shuffle(word_list)
            poem_lines.append(pgen.poem_line_from_word_list(word_list, connectors=self.connectors, max_line_length=40))
        c = canvas.Canvas(f"{','.join(input_words)}.pdf")
        y_coordinate = 60
        for line in poem_lines:
            line = random.choice([line, line, line, line.upper()])
            font_choice = random.choice(self.font_choices)
            font_size = self.get_font_size(line)
            max_x_coordinate = self.get_max_x_coordinate(line, font_choice, font_size)
            x_coordinate = random.randint(15, max_x_coordinate)
            vp_string = VisualPoemString(line, x=x_coordinate, y=y_coordinate, font=font_choice, font_size=font_size)
            c.setFont(vp_string.font, vp_string.font_size)
            c.drawString(vp_string.x, vp_string.y, line)
            y_coordinate += 31
            self.drawn_strings.append(vp_string)
        c.showPage()
        c.save()