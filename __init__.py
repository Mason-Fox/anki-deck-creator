from anki.hooks import addHook
from .deck_creator import pdf_prompt
from aqt.qt import QAction
from aqt import mw

# Register your menu item
action = QAction("Upload PDF", mw)
action.triggered.connect(pdf_prompt)
mw.form.menuTools.addAction(action)