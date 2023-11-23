from anki.hooks import addHook
from .test import process_pdf
from aqt.qt import QAction
from aqt import mw

addHook('profileLoaded', process_pdf)
def setup():
    # Add any setup code here
    pass

# The following line is necessary for Anki to recognize this as a valid add-on
# and to execute the setup function when Anki starts.
addHook('profileLoaded', setup)

# Register your menu item
action = QAction("Upload PDF", mw)
action.triggered.connect(process_pdf)
mw.form.menuTools.addAction(action)