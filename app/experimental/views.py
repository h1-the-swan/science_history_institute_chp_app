from __future__ import unicode_literals
import os
from flask import Blueprint, render_template, url_for, redirect, current_app, jsonify, flash
from flask_login import current_user, login_required

from app.models import EditableHTML, OralHistory
from app.wikipedia import search_wikipedia

from app.experimental.forms import SelectOralHistory

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
    for oh in oral_histories:
        form.choice.choices.append((oh.id, full_name(oh)))
    if form.validate_on_submit():
        oh = OralHistory.query.get(form.choice.data)
        flash(full_name(oh), 'info')
        data = search_wikipedia(full_name(oh))
        # return render_template('experimental/wikipedia.html', form=form, data=data)
    return render_template(
        'experimental/wikipedia.html', form=form, data=data)
