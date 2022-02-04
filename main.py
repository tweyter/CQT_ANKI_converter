# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

"""
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
for page_layout in extract_pages("test.pdf"):
    for element in page_layout:
        if isinstance(element, LTTextContainer):
            print(element.get_text())
"""
from pathlib import Path

import fitz
from fitz import Page
import io
from PIL import Image
import genanki
from bs4 import BeautifulSoup
from cssutils import parseStyle

with open('style.css') as style_css:
    STYLE = style_css.read()

MEDIA_MODEL = genanki.Model(
    1607392319,
    "Media Model",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
        {"name": "MyMedia"},
    ],
    templates=[
        {
            "name": 'Media Card',
            "qfmt": '{{MyMedia}}<br>{{Question}}',
            "afmt": '{{FrontSide}}<br id="answer">{{Answer}}',
        },
    ],
    css=STYLE,
)

NO_MEDIA_MODEL = genanki.Model(
    1607392320,
    "Simple Model",
    fields=[
        {"name": "Question"},
        {"name": "Answer"},
    ],
    templates=[
        {
            "name": 'Card 1',
            "qfmt": '{{Question}}',
            "afmt": '{{FrontSide}}<br id="answer">{{Answer}}',
        },
    ],
    css=STYLE,
)

BASE_PATH = Path(__file__).parent
IMAGE_PATH = BASE_PATH / 'images'


def pdf_test(file_path):
    pdf_file = fitz.Document(file_path)
    # question = ""
    # answer = ""
    media_files = []
    processed_notes = 0
    my_deck = genanki.Deck(
        2059400110,
        "SPV Questions"
    )

    for page_index in range(len(pdf_file)):
        page = pdf_file[page_index]  # type: Page
        image_list = page.get_images()

        # if page_index != 31:
        #     continue

        soup = BeautifulSoup(page.get_text("html", sort=True), 'html.parser')
        # text = page.get_text("html", sort=True).splitlines()  # type: str
        question = ""
        answer = ""
        for paragraph in soup.find_all('p'):
            if paragraph.span:
                spans = paragraph.find_all('span')
                if isinstance(spans, list):
                    css = parseStyle(spans[-1]['style'])
                    if css['color'] == "#001f5b":
                        question += spans[-1].string.lstrip()
                        question += '\n'
                    elif css['color'] == "#00319f":
                        answer += spans[-1].string.lstrip()
                        answer += '\n'
        if not answer:
            continue
        if len(image_list) <= 1:
            note = genanki.Note(
                model=NO_MEDIA_MODEL,
                fields=[question, answer]
            )
            # my_deck.add_note(note)
            # processed_notes += 1
        else:
            # xref = image_list[-1][0]
            # base_image = pdf_file.extract_image(xref)
            # image_bytes = base_image["image"]
            # img = Image.open(io.BytesIO(image_bytes))
            # rgb_img = img.convert("RGB")
            # file_path = IMAGE_PATH / f"image_{page_index}.jpg"
            # rgb_img.save(file_path)

            file_name = f"image_{page_index}.jpg"
            fp = Path('images', file_name)
            last_image = Image.new("RGB", (120, 60), (0, 0, 0))
            if not IMAGE_PATH.exists():
                IMAGE_PATH.mkdir()
            for image_index, img in enumerate(image_list, start=1):
                if image_index < 2:
                    continue
                xref = img[0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                img = Image.open(io.BytesIO(image_bytes))
                if len(set(img.histogram())) > len(set(last_image.histogram())):
                    last_image = img
            rgb_img = last_image.convert("RGB")
            rgb_img.save(fp)
            my_note = genanki.Note(
                model=MEDIA_MODEL,
                # do not include paths in <img src> only the filename.
                fields=[question, answer, f'<img src="{file_name}">']
            )
            media_files.append(fp)
            my_deck.add_note(my_note)
            processed_notes += 1
    pkg = genanki.Package(my_deck, media_files)
    pkg.write_to_file('test_anki.apkg')
    print(f"Notes processed: {processed_notes}")
    return


def anki_note(question, answer):

    my_model = genanki.Model(
        1607392319,
        "Simple Model",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
            {"name": "MyMedia"},
        ],
        templates=[
            {
                "name": 'Card 1',
                "qfmt": '{{MyMedia}}<br>{{Question}}',
                "afmt": '{{FrontSide}}<br id="answer">{{Answer}}',
            },
        ],
        css=STYLE,
    )

    my_note = genanki.Note(
        model=my_model,
        fields=[question, answer, r'<img src="image.jpg">']
    )

    my_deck = genanki.Deck(
        2059400110,
        "SPV Questions"
    )

    my_deck.add_note(my_note)

    pkg = genanki.Package(my_deck, ['image.jpg'])
    pkg.write_to_file('test_anki.apkg')


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    pdf_test(r'C:\Users\tweyt\Downloads\A320_SPV_Home_Study.pdf')
