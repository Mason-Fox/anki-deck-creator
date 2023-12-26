from anki.hooks import addHook
from .deck_creator import deck_creator
from aqt.qt import QAction
from aqt import mw

def on_upload_pdf_triggered():
    deck_creator()

# Register your menu item
action = QAction("Upload PDF", mw)
action.triggered.connect(on_upload_pdf_triggered)
mw.form.menuTools.addAction(action)