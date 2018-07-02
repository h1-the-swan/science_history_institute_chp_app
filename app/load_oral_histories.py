import os
from glob import glob

from app import basedir

from docx import Document

ORAL_HISTORY_FNAMES = glob(os.path.join(basedir,  'static/LSF_oral_histories/*'))

def test():
    test_history = 'static/LSF_oral_histories/Addario AE-GP.docx'
    test_history = os.path.join(basedir, test_history)
    # data = os.path.exists(test_history)
    document = Document(test_history)
    data = [p.text for p in document.paragraphs]
    return data
