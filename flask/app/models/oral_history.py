from app import db

class OralHistory(db.Model):
    __tablename__ = 'oral_histories'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.Text)
    fname_base = db.Column(db.Text)
    full_name = db.Column(db.String(64))
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    entity_id = db.Column(db.Integer)
    comment = db.Column(db.Text)

    entity = db.relationship('Entity', foreign_keys=[entity_id], primaryjoin='Entity.id == OralHistory.entity_id', backref='oral_history', uselist=False, lazy=True)

    def __repr__(self):
        return "<OralHistory '{}'>".format(self.fname)

    @staticmethod
    def insert_oral_histories():
        from app.load_oral_histories import load_oral_histories_fnames
        for r in load_oral_histories_fnames():
            oral_hist = OralHistory(fname=r['fname'],
                                    fname_base=r['fname_base'],
                                    full_name=r['interviewee_full_name'],
                                    first_name=r['interviewee_first_name'],
                                    last_name=r['interviewee_last_name'])
            db.session.add(oral_hist)
        db.session.commit()

    def parse(self):
        """TODO: Docstring for parse.
        :returns: TODO

        """
        from docx import Document
        return Document(self.fname)
