from __future__ import unicode_literals
import sys, os, json
from flask import Blueprint, render_template, url_for, redirect, current_app, jsonify, request
from flask_login import current_user, login_required

from app.models import EditableHTML, OralHistory, Entity, WikipediaSuggest, EntityMeta
from app.load_oral_histories import preprocess_oral_history

from app.main.forms import SelectEntity

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/about')
@login_required
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template(
        'main/about.html', editable_html_obj=editable_html_obj)

@main.route('/histories')
@main.route('/histories/<hist_id>')
@login_required
def histories(hist_id=None):
    service_url = current_app.hypothesis_client.service
    # hypothesis_api_url = "https://hypothes.is/api/"
    hypothesis_api_url = service_url + '/api/'
    hypothesis_username = "acct:{username}@{authority}".format(username=current_user.username, authority=os.environ.get('HYPOTHESIS_AUTHORITY'))
    if hist_id is None:
        data = OralHistory.query.all()
        histories_base_url = url_for("main.histories", _external=True)
        return render_template('main/oralhistories.html', data=data, hypothesis_api_url=hypothesis_api_url, hypothesis_username=hypothesis_username, histories_base_url=histories_base_url)

    oral_hist = OralHistory.query.get(hist_id)
    document = oral_hist.parse()
    # data = [p.text for p in document.paragraphs]
    data = preprocess_oral_history([p.text for p in document.paragraphs])
    # hypothesis_username = "{}_{}".format(current_user.first_name.lower(), current_user.last_name.lower())
    hypothesis_grant_token = current_app.hypothesis_client.grant_token(username=current_user.username)

    # # get embed.js from the hypothesis service
    # try:
    #     from urllib.request import urlretrieve
    # except ImportError:
    #     from urllib import urlretrieve
    # embedjs_fname = os.path.join(current_app.static_folder, "embed.js")
    # urlretrieve(os.environ['HYPOTHESIS_SERVICE'] + "/embed.js", embedjs_fname)

    keyword = request.args.get('mark', None)
    return render_template('main/display_oral_history.html', data=data, oral_hist=oral_hist, keyword=keyword, hypothesis_api_url=hypothesis_api_url, hypothesis_grant_token=hypothesis_grant_token.decode(), service_url=service_url)

@main.route('/histories/entitycounts/<entity_name>', methods=['GET', 'POST'])
@login_required
def histories_entitycounts(entity_name):
    service_url = current_app.hypothesis_client.service
    # hypothesis_api_url = "https://hypothes.is/api/"
    hypothesis_api_url = service_url + '/api/'
    hypothesis_username = "acct:{username}@{authority}".format(username=current_user.username, authority=os.environ.get('HYPOTHESIS_AUTHORITY'))

    # entity = Entity.query.get(entity_id)

    # load counts data
    mentions_data = {}

    entities_with_mentions = set()
    with open(os.path.join(current_app.static_folder, "entities_counts.tsv"), 'r') as f:
        for i, line in enumerate(f):
            # skip header
            if i == 0:
                continue
            line_split = line.strip().split('\t')
            row = {
                'term': line_split[0],
                'oral_history_id': int(line_split[1]),
                'oral_history_fname_base': line_split[2],
                'num_mentions': int(line_split[3]),
            }
            # entities_with_mentions.add(row['entity_id'])
            entities_with_mentions.add(row['term'])
            if entity_name.lower() == row['term'].lower():
                mentions_data[row['oral_history_id']] = row['num_mentions']
    data = OralHistory.query.all()
    histories_base_url = url_for("main.histories", _external=True)

    form = SelectEntity()
    # entities = Entity.query.filter(Entity.description.in_(['biotech_company', 'pharma_company'])).all()
    form.choice.choices = []
    # for e in entities:
    #     if e.id in entities_with_mentions:
    #         form.choice.choices.append((e.id, e.name))
    for term in entities_with_mentions:
        form.choice.choices.append((term.lower(), term))
    # sort alphabetically by name
    form.choice.choices.sort(key=lambda x: x[1])
    if form.validate_on_submit():
        selected_entity = form.choice.data
        return redirect(url_for('main.histories_entitycounts', entity_name=selected_entity))

    entities_cats = {}
    with open(os.path.join(current_app.static_folder, "entities_searchterms.tsv"), 'r') as f:
        for line in f:
            row = line.strip().split('\t')
            entities_cats[row[0].lower()] = row[1]
    form_categories = SelectEntity()
    form_categories.choice.choices = [(cat, cat) for cat in set(entities_cats.values())]
    return render_template('main/oralhistories_entitycounts.html', data=data, mentions_data=mentions_data, entity_name=entity_name, form=form, form_categories=form_categories, entities_cats=entities_cats, hypothesis_api_url=hypothesis_api_url, hypothesis_username=hypothesis_username, histories_base_url=histories_base_url)

@main.route('/entities')
@login_required
def entities():
    entities = Entity.query.all()
    return render_template('main/entities.html', entities=entities)

@main.route('/media')
@main.route('/media/<entity_id>')
@login_required
def media(entity_id=None):
    service_url = current_app.hypothesis_client.service
    # hypothesis_api_url = "https://hypothes.is/api/"
    hypothesis_api_url = service_url + '/api/'
    hypothesis_username = "acct:{username}@{authority}".format(username=current_user.username, authority=os.environ.get('HYPOTHESIS_AUTHORITY'))
    if entity_id is None:
        media_base_url = url_for("main.media", _external=True)
        entities_media = Entity.query.filter(Entity.description.like('media:%')).all()
        return render_template('main/media.html', data=entities_media, hypothesis_api_url=hypothesis_api_url, hypothesis_username=hypothesis_username, media_base_url=media_base_url)

    if sys.version_info[0] < 3:
        import opengraph
    else:
        import opengraph_py3 as opengraph
    entity_meta = EntityMeta.query \
                    .filter_by(entity_id=entity_id) \
                    .filter(EntityMeta.type_.like("opengraph_url")) \
                    .all()
    if not entity_meta:
        data = None
    else:
        entity_meta = entity_meta[-1]
        url = entity_meta.description
        data = opengraph.OpenGraph(url=url)

    hypothesis_grant_token = current_app.hypothesis_client.grant_token(username=current_user.username)

    keyword = request.args.get('mark', None)
    return render_template('main/display_media.html', data=data, entity_meta=entity_meta, hypothesis_api_url=hypothesis_api_url, hypothesis_grant_token=hypothesis_grant_token.decode(), service_url=service_url)

@main.route('/_login_fake')
def _login_fake():
    return render_template('main._login_fake.html')
