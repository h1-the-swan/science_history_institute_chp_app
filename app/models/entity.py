from app import db

class Entity(db.Model):
    __tablename__ = 'entities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    description = db.Column(db.Text, index=True)

    def __repr__(self):
        return "<Entity '{}'>".format(self.name)

class WikipediaSuggest(db.Model):
    __tablename__ = 'wikipedia_suggest'
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, index=True)
    wikipedia_page_id = db.Column(db.BigInteger)
    wikipedia_page_title = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    entity = db.relationship('Entity', foreign_keys=[entity_id], primaryjoin='Entity.id == WikipediaSuggest.entity_id', backref='wikipedia_suggest', uselist=False, lazy=True)

    @property
    def wikipedia_url(self):
        return "https://en.wikipedia.org/wiki/{}".format(self.wikipedia_page_title)

class EntityMeta(db.Model):
    __tablename__ = 'entities_meta'
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer)
    type_ = db.Column(db.String(64), index=True)
    description = db.Column(db.Text)
    entity = db.relationship('Entity', foreign_keys=[entity_id], primaryjoin='Entity.id == EntityMeta.entity_id', backref='entity_meta', uselist=False, lazy=True)


