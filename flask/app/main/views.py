from __future__ import unicode_literals
import os
from flask import Blueprint, render_template, url_for, redirect, current_app, jsonify
from flask_login import current_user

from app.models import EditableHTML, OralHistory

main = Blueprint('main', __name__)


@main.route('/')
def index():
    # return render_template('main/index.html')
    return redirect(url_for('main.histories'))


@main.route('/about')
def about():
    editable_html_obj = EditableHTML.get_editable_html('about')
    return render_template(
        'main/about.html', editable_html_obj=editable_html_obj)

@main.route('/histories')
@main.route('/histories/<hist_id>')
def histories(hist_id=None):
    if hist_id is None:
        data = OralHistory.query.all()
        return render_template('main/oralhistories.html', data=data)

    oral_hist = OralHistory.query.get(hist_id)
    document = oral_hist.parse()
    data = [p.text for p in document.paragraphs]
    service_url = current_app.hypothesis_client.service
    # hypothesis_api_url = "https://hypothes.is/api/"
    hypothesis_api_url = service_url + '/api/'
    hypothesis_username = "{}_{}".format(current_user.first_name.lower(), current_user.last_name.lower())
    hypothesis_grant_token = current_app.hypothesis_client.grant_token(username=hypothesis_username)
    return render_template('main/display_oral_history.html', data=data, hypothesis_api_url=hypothesis_api_url, hypothesis_grant_token=hypothesis_grant_token.decode(), service_url=service_url)

@main.route('/_login_fake')
def _login_fake():
    return render_template('main._login_fake.html')
