import sys, os, re
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))

from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from anki.notes import Note

from pypdf import PdfReader
from openai import OpenAI

failed_openai_call = False

class Worker(QThread):
    finished = pyqtSignal()
    data_returned = pyqtSignal(object)  # Signal to emit returned data
    error_occurred = pyqtSignal(str)  # Signal to emit error messages

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.function(*self.args, **self.kwargs)
            self.data_returned.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            self.finished.emit()

def pdf_prompt():
    # Open a file dialog to get the path of the selected PDF file
    file_path, _ = QFileDialog.getOpenFileName(
        mw,
        "Select PDF File",
        "",
        "PDF Files (*.pdf);;All Files (*)"
    )

    if file_path:
        process_pdf(file_path)
    else:
        # Display a message if the user cancels the file dialog
        show_info("PDF processing canceled.")
        return

def show_processing_and_run(function, *args, **kwargs):
    processing_dialog = QProgressDialog("Processing, this may take some time...", "Abort", 0, 0, mw)
    processing_dialog.setWindowTitle("Please Wait")
    processing_dialog.setWindowModality(Qt.WindowModal)

    worker = Worker(function, *args, **kwargs)
    # Call create_deck with successful card return, show_info if error
    worker.data_returned.connect(create_deck)
    worker.error_occurred.connect(show_info)

    worker.finished.connect(processing_dialog.close)
    processing_dialog.canceled.connect(worker.terminate)

    worker.start()
    processing_dialog.exec_()

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

def call_openai(api_key, text, model):
    """
    Call OpenAI for card creation

    Parameters:
        text (str): PDF text content

    Returns:
        list: List of font\tback cards
    """
    client = OpenAI(api_key=api_key)

    # Instructions for GPT-3.5 to create flashcards
    system_message = (
        "Create flashcards from the provided text. For each flashcard, "
        "identify a key phrase, word, or equation from the text and place it on the front. "
        "On the back, provide definitions, explanitory information or relevant context. "
        "Format each flashcard as 'front\\tback\\n'."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": text}
        ],
        max_tokens=10000,
        temperature=0.05 # Low Randomness
    )

    flashcards_raw = response.choices[0].message.content.strip()
    # Split the string into cards
    cards = flashcards_raw.split('\n')

    return cards

def create_deck(cards):
    collection = mw.col
    additional_info = "Enter an existing deck name to add to a deck, or enter a unique Deck name to create a new Deck"
    deck_name = prompt_user("Deck Name", additional_info)
    if deck_name is None:
        show_info("Invalid Deck Name")
        return

    # Get or create the deck
    deck_id = collection.decks.id(deck_name, create=True)
    note_type = mw.col.models.by_name("Basic")

    for card in cards:
        try:
            front, back = card.split('\\t', 1)
            new_note = mw.col.new_note(note_type)
            new_note["Front"] = front
            new_note["Back"] = back
            new_note.note_type()["did"] = deck_id
            
            # Add the note to the current deck
            mw.col.add_note(new_note, deck_id)

        except ValueError:
            print(f"Invalid format for card: {card}")

    # Refresh UI
    mw.reset()

def prompt_user(item, additional_info=None):
    dialog = QDialog(mw)
    dialog.resize(450, 200)  # Set the window dimensions (width, height)

    layout = QVBoxLayout(dialog)

    if additional_info is not None:
        # Additional Infomration section
        info_text_edit = QTextEdit()
        info_text_edit.setReadOnly(True)
        info_text_edit.setText(f"{additional_info}")
        info_text_edit.setStyleSheet("QTextEdit { background-color: #9ca6b8; }")
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

def retrieve_validate_api_key(config):

    additional_info= (
        "An OpenAI Account and API key are required, and will be used to communicate with OpenAI."
        "For more information and instructions, see: https://platform.openai.com/docs/quickstart"
    )
    api_key = prompt_user("API Key", additional_info)

    if not api_key:
        return 
    
    client = OpenAI(api_key=api_key)
    try:
        # Simple API call to check the API key validity
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "This is a test",
                }
            ],
        )
    except Exception as e:
        show_info(f"OpenAI connection failed, please validate API key. \n\nError: {e}")
        return False

    config["api_key"] = api_key
    mw.addonManager.writeConfig(__name__, config)
    return True

def process_pdf(file_path):
    #show_info(f"Processing PDF: {file_path}")

    raw_text = extract_text_from_pdf(file_path)
    #clean_text = clean_and_preprocess_text(raw_text)

    config = mw.addonManager.getConfig(__name__)

    # Retrieve API Key if not set, if validation fails, exit
    if not config["api_key"]:
        if not retrieve_validate_api_key(config):
            return

    # Use the same processing window for different functions
    cards = show_processing_and_run(call_openai, config["api_key"], raw_text, config["model"])