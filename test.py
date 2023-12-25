from aqt import mw
from aqt.utils import showInfo
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import re
from aqt import mw
from anki.notes import Note

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from pypdf import PdfReader
from openai import OpenAI

def process_pdf():
    # Open a file dialog to get the path of the selected PDF file
    file_path, _ = QFileDialog.getOpenFileName(
        mw,
        "Select PDF File",
        "",
        "PDF Files (*.pdf);;All Files (*)"
    )

    if file_path:
        # Call a function to process the selected PDF file
        text = process_selected_pdf(file_path)
    else:
        # Display a message if the user cancels the file dialog
        show_info("PDF processing canceled.")
    
    callOpenAI(text)

def process_selected_pdf(file_path):
    # Placeholder function to process the selected PDF file
    show_info(f"Processing PDF: {file_path}")
    # Add your PDF processing logic here
    # For example, you can extract text, make API calls, etc.
    raw_text = extract_text_from_pdf(file_path)
    #clean_and_preprocess_text(raw_text)

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
            # Create a PDF reader object
            pdf_reader = PdfReader(file)

            # Iterate through pages
            for page_number in range(len(pdf_reader.pages)):
                # Extract text from the page
                text += pdf_reader.pages[page_number].extract_text()

    except Exception as e:
        print({e})


    with open("/Users/masonfox/Downloads/anki-raw.txt", "w", encoding="utf-8") as file:
        file.write(text)

    return text

def clean_and_preprocess_text(raw_text):
    """
    Clean and preprocess text content.

    Parameters:
        raw_text (str): Raw text content.

    Returns:
        str: Cleaned and preprocessed text.
    """
    # Example: Remove non-alphanumeric characters and extra whitespaces
    cleaned_text = re.sub(r"[^a-zA-Z0-9\s]", "", raw_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    with open("/Users/masonfox/Downloads/anki-clean.txt", "w", encoding="utf-8") as file:
        file.write(cleaned_text)

    return cleaned_text

def callOpenAI(text):
    # Your OpenAI API key
    client = OpenAI(api_key='example-key')

    # Instructions for GPT-3 to create flashcards
    system_message = "You are a flashcard generation assistant. You will be given a string of text that has been pulled from a presentation. Create a deck of flashcards based on the text content. Cards should be in the following format:\\nFront\\tBack\\nFront\\tBack\\n\n\nThis will be parsed by python, so keep that in mind when creating card formatting"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Select the appropriate model
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": text}
        ],
        max_tokens=1000, # Adjust based on your needs
        temperature=0.05 # Low Randomness
    )

    flashcards_raw = response.choices[0].message.content.strip()
    # Split the string into cards
    cards = flashcards_raw.split('\n')

    collection = mw.col
    deck_name = "test deck"
    # Get or create the deck
    deck_id = collection.decks.id(deck_name, create=True)
    note_type = mw.col.models.by_name("Basic")

    with open("/Users/masonfox/Downloads/openai-raw.txt", "w", encoding="utf-8") as file:
        file.write(flashcards_raw)

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