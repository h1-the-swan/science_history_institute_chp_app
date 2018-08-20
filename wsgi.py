import os
import click

from app import create_app, db
URL_PREFIX = "/chp"
app = create_app(os.getenv('FLASK_CONFIG') or 'default', url_prefix=URL_PREFIX)
app.config['APPLICATION_ROOT'] = URL_PREFIX

from app.models import OralHistory, WikipediaSuggest, Entity
from app.wikipedia import search_wikipedia

# Command Line Interface

def full_name(oral_history):
    return "{} {}".format(oral_history.first_name, oral_history.last_name)

@app.cli.command()
def mytest():
    x = Entity.query.all()
    print(len(x))
    # for item in x:
    #     print(full_name(item))

@app.cli.command()
def wikipedia_suggest():
    entities = Entity.query.all()
    num_add = 0
    for ent in entities:
        results = search_wikipedia(ent.name)
        if results:
            first_result = results[0]
            suggest = WikipediaSuggest(entity_id=ent.id,
                                        wikipedia_page_id=first_result.get('pageid'),
                                        wikipedia_page_title=first_result.get('title'))
            db.session.add(suggest)
            num_add += 1
    db.session.commit()
    print("{} wikipedia suggestions added".format(num_add))


@app.cli.command()
def load_entities_from_oral_histories():
    oral_histories = OralHistory.query.all()
    for oh in oral_histories:
        entity = Entity(name=full_name(oh))
        entity.description = "Oral History ID: {}".format(oh.id)
        db.session.add(entity)
    db.session.commit()
