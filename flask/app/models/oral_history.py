from app import db

class OralHistory(db.Model):
    __tablename__ = 'oral_histories'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.Text)

    def __repr__(self):
        return "OralHistory '{}'>".format(self.fname)

    @staticmethod
    def insert_oral_histories():
        from app.load_oral_histories import ORAL_HISTORY_FNAMES
        for fname in ORAL_HISTORY_FNAMES:
            oral_hist = OralHistory(fname=fname)
            db.session.add(oral_hist)
        db.session.commit()

    def parse(self):
        """TODO: Docstring for parse.
        :returns: TODO

        """
        from docx import Document
        return Document(self.fname)
