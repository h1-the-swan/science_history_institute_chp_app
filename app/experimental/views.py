from __future__ import unicode_literals
import os
import json
from flask import Blueprint, render_template, url_for, redirect, current_app, jsonify, flash, request
from flask_login import current_user, login_required

from app import db
from app.models import EditableHTML, OralHistory, WikipediaSuggest, Entity
from app.wikipedia import search_wikipedia

from app.experimental.forms import SelectOralHistory, AddNewEntityForm

experimental = Blueprint('experimental', __name__)

def full_name(oral_history):
    return "{} {}".format(oral_history.first_name, oral_history.last_name)

@experimental.route('/wikipedia', methods=['GET', 'POST'])
@login_required
def wikipedia():
    # data = search_wikipedia('Julia Levy')
    data = []
    form = SelectOralHistory()
    oral_histories = OralHistory.query.all()
    form.choice.choices = []
    oh_id = None
    for oh in oral_histories:
        if (not oh.entity.wikipedia_suggest) or (any([ws.confirmed==False for ws in oh.entity.wikipedia_suggest])):
            form.choice.choices.append((oh.id, full_name(oh)))
    if form.validate_on_submit():
        oh = OralHistory.query.get(form.choice.data)
        oh_id = oh.id
        flash(full_name(oh), 'info')
        data = search_wikipedia(full_name(oh))
        # return render_template('experimental/wikipedia.html', form=form, data=data)
    return render_template(
        'experimental/wikipedia.html', form=form, data=data, oh_id=oh_id)

@experimental.route('/wikipedia/_change_confirm', methods=['POST'])
@login_required
def wikipedia_change_confirm():
    oh_id = request.values.get('oh_id')
    oh = OralHistory.query.get(oh_id)
    ws = WikipediaSuggest.query.filter_by(entity_id=oh.entity.id).one_or_none()
    checked = request.values.get('checked') == 'true'
    wikipedia_page_id = request.values.get('wikipedia_page_id')
    wikipedia_page_title = request.values.get('wikipedia_page_title')
    if ws:
        ws.wikipedia_page_id = wikipedia_page_id
        ws.wikipedia_page_title = wikipedia_page_title
        ws.checked = checked
    else:
        ws = WikipediaSuggest(entity_id=oh.entity.id,
                                wikipedia_page_id=wikipedia_page_id,
                                wikipedia_page_title=wikipedia_page_title,
                                confirmed=checked)
    db.session.add(ws)
    db.session.commit()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@experimental.route('/wikipedia_suggest', methods=['GET', 'POST'])
@login_required
def wikipedia_suggest():
    wss = WikipediaSuggest.query.filter_by(confirmed=False).all()
    return render_template(
        'experimental/wikipedia_suggest.html', wss=wss)

@experimental.route('/wikipedia_suggest/_change_confirm', methods=['POST'])
@login_required
def wikipedia_suggest_change_confirm():
    ws_id = request.values.get('wikipedia_suggest_id')
    checked = request.values.get('checked') == 'true'
    ws = WikipediaSuggest.query.get(ws_id)
    ws.confirmed = checked
    db.session.add(ws)
    db.session.commit()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@experimental.route('/add_new_entity', methods=['GET', 'POST'])
@login_required
def add_new_entity():
    form = AddNewEntityForm()
    if form.validate_on_submit():
        if Entity.query.filter_by(name=form.name.data).one_or_none():
            flash('entity with that name already exists', 'error')
        else:
            entity = Entity(name=form.name.data, description=form.description.data)
            db.session.add(entity)
            db.session.flush()
            entity_id = entity.id
            entity_name = entity.name
            wikipedia_page_title = form.wikipedia_page_title.data
            # if the user entered a url, just get the page title
            if wikipedia_page_title.startswith('http'):
                wikipedia_page_title = wikipedia_page_title.split('/')[-1]
            ws = WikipediaSuggest(entity_id=entity_id, wikipedia_page_title=wikipedia_page_title, confirmed=True)
            db.session.add(ws)
            db.session.commit()
            flash('added entity {} (id {})'.format(entity_name, entity_id), 'info')
    return render_template('experimental/add_new_entity.html', form=form)

@experimental.route('/scratch')
def scratch():
    data = WikipediaSuggest.query.all()
    return render_template('experimental/scratch.html', data=data)
