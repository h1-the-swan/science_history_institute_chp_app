from app import db

class Entity(db.Model):
    __tablename__ = 'entities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)

    def __repr__(self):
        return "<Entity '{}'>".format(self.name)

class WikipediaSuggest(db.Model):
    __tablename__ = 'wikipedia_suggest'
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer)
    wikipedia_page_id = db.Column(db.BigInteger)
    wikipedia_page_title = db.Column(db.String(128))

    entity = db.relationship('Entity', foreign_keys=[entity_id], primaryjoin='Entity.id == WikipediaSuggest.entity_id', backref='wikipedia_suggest', uselist=False, lazy=True)

