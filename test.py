from aqt import mw
from aqt.utils import showInfo
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import re

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

def callOpenAI():
    client = OpenAI()
    return None