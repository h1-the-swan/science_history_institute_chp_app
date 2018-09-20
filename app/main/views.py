from __future__ import unicode_literals
import os, json
from flask import Blueprint, render_template, url_for, redirect, current_app, jsonify, request
from flask_login import current_user, login_required

from app.models import EditableHTML, OralHistory, Entity, WikipediaSuggest
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

@main.route('/histories/entitycounts/<entity_id>', methods=['GET', 'POST'])
@login_required
def histories_entitycounts(entity_id):
    service_url = current_app.hypothesis_client.service
    # hypothesis_api_url = "https://hypothes.is/api/"
    hypothesis_api_url = service_url + '/api/'
    hypothesis_username = "acct:{username}@{authority}".format(username=current_user.username, authority=os.environ.get('HYPOTHESIS_AUTHORITY'))

    entity = Entity.query.get(entity_id)
    # load counts data
    mentions_data = {}

    entities_with_mentions = set()
    with open(os.path.join(current_app.static_folder, "oral_history_company_mentions.tsv"), 'r') as f:
        for i, line in enumerate(f):
            # skip header
            if i == 0:
                continue
            line_split = line.strip().split('\t')
            row = {
                'oh_id': int(line_split[0]),
                'entity_id': int(line_split[1]),
                'entity_name': line_split[2],
                'num_mentions': int(line_split[3]),
            }
            entities_with_mentions.add(row['entity_id'])
            if entity.id == row['entity_id']:
                mentions_data[row['oh_id']] = row['num_mentions']
    data = OralHistory.query.all()
    histories_base_url = url_for("main.histories", _external=True)


    form = SelectEntity()
    entities = Entity.query.filter(Entity.description.in_(['biotech_company', 'pharma_company'])).all()
    form.choice.choices = []
    for e in entities:
        if e.id in entities_with_mentions:
            form.choice.choices.append((e.id, e.name))
    form.choice.choices.sort(key=lambda x: x[1])
    if form.validate_on_submit():
        selected_entity_id = form.choice.data
        return redirect(url_for('main.histories_entitycounts', entity_id=selected_entity_id))
    return render_template('main/oralhistories_entitycounts.html', data=data, mentions_data=mentions_data, entity=entity, form=form, hypothesis_api_url=hypothesis_api_url, hypothesis_username=hypothesis_username, histories_base_url=histories_base_url)

@main.route('/entities')
@login_required
def entities():
    entities = Entity.query.all()
    return render_template('main/entities.html', entities=entities)

@main.route('/_login_fake')
def _login_fake():
    return render_template('main._login_fake.html')
