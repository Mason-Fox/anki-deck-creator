import sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from anki.notes import Note

from pypdf import PdfReader
from openai import OpenAI

def pdf_prompt():
    # Open a file dialog to get the path of the selected PDF file
    file_path, _ = QFileDialog.getOpenFileName(
        mw,
        "Select PDF File",
        "",
        "PDF Files (*.pdf);;All Files (*)"
    )

    if file_path:
        return file_path
    else:
        # Display a message if the user cancels the file dialog
        show_info("PDF processing canceled.")
    

def process_pdf(file_path):
    show_info(f"Processing PDF: {file_path}")

    raw_text = extract_text_from_pdf(file_path)
    #clean_text = clean_and_preprocess_text(raw_text)

    return raw_text

def show_info(message):
    # Display an information message to the user
    QMessageBox.information(mw, "Information", message)

def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file.

    Parameters:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text content.
    """
    text = ""
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            # Iterate through pages
            for page_number in range(len(pdf_reader.pages)):
                # Extract text from the page
                text += pdf_reader.pages[page_number].extract_text()

    except Exception as e:
        print({e})

    return text

def clean_and_preprocess_text(raw_text):
    """
    Clean and preprocess text content.

    Parameters:
        raw_text (str): Raw text content.

    Returns:
        str: Cleaned and preprocessed text.
    """
    # Remove non-alphanumeric characters and extra whitespaces
    cleaned_text = re.sub(r"[^a-zA-Z0-9\s]", "", raw_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    return cleaned_text

def call_openai(text, key):
    client = OpenAI(api_key=key)

    # Instructions for GPT-3.5 to create flashcards
    show_info("Generating Cards, this may take some time...")
    system_message = "You are a flashcard generation assistant. You will be given a string of text that has been pulled from a presentation. Create a deck of flashcards based on the text content. Cards should be in the following format:\\nFront\\tBack\\nFront\\tBack\\n\n\nThis will be parsed by python, so keep that in mind when creating card formatting"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": text}
        ],
        max_tokens=1000,
        temperature=0.05 # Low Randomness
    )

    flashcards_raw = response.choices[0].message.content.strip()
    # Split the string into cards
    cards = flashcards_raw.split('\n')
    return cards

def create_deck(cards):
    collection = mw.col
    deck_name = prompt_user("Deck Name", additional_info="Enter an existing deck name to add to a deck, or enter a unique Deck name to create a new Deck")

    # Get or create the deck
    deck_id = collection.decks.id(deck_name, create=True)
    note_type = mw.col.models.by_name("Basic")

    for card in cards:
        try:
            front, back = card.split('\\t', 1)
            new_note = mw.col.new_note(note_type)
            new_note["Front"] = front  # Front of the card
            new_note["Back"] = back   # Back of the card
            new_note.note_type()["did"] = deck_id
            
            # Add the note to the current deck
            mw.col.add_note(new_note, deck_id)

        except ValueError:
            print(f"Invalid format for card: {card}")

def prompt_user(item, additional_info=None):
    dialog = QDialog(mw)
    dialog.resize(450, 200)  # Set the window dimensions (width, height)

    layout = QVBoxLayout(dialog)

    if additional_info is not None:
        # Additional Infomration section
        info_text_edit = QTextEdit()
        info_text_edit.setReadOnly(True)  # Make the text edit read-only
        info_text_edit.setText(f"{additional_info}")
        info_text_edit.setStyleSheet("QTextEdit { background-color: #9ca6b8; }")  # Light grey background
        layout.addWidget(info_text_edit)

    # Prompt Text
    text_label = QLabel(f"Enter your {item}:", dialog)
    text_edit = QLineEdit(dialog)
    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)

    layout.addWidget(text_label)
    layout.addWidget(text_edit)
    layout.addWidget(button_box)

    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)

    result = dialog.exec_()

    if result == QDialog.Accepted:
        return text_edit.text()
    else:
        show_info(f"{item} Entry canceled.")

def deck_creator():
    config = mw.addonManager.getConfig(__name__)

    pdf_path = pdf_prompt()
    text = process_pdf(pdf_path)

    api_key = config.get("api_key")
    if not api_key:
        api_key = prompt_user("API Key", "An OpenAI Account and API key are required, and will be used to communicate with OpenAI. For more information and instructions, see: https://platform.openai.com/docs/quickstart")
        config["api_key"] = api_key

    cards = call_openai(text, api_key)
    create_deck(cards)
    mw.reset()