from __future__ import unicode_literals
import os, json
from flask import Blueprint, render_template, url_for, redirect, current_app, jsonify
from flask_login import current_user, login_required

from app.models import EditableHTML, OralHistory
from app.load_oral_histories import preprocess_oral_history

main = Blueprint('main', __name__)


@main.route('/')
def index():
    # return render_template('main/index.html')
    return redirect(url_for('main.histories'))


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
        return render_template('main/oralhistories.html', data=data, hypothesis_api_url=hypothesis_api_url, hypothesis_username=hypothesis_username)

    oral_hist = OralHistory.query.get(hist_id)
    document = oral_hist.parse()
    # data = [p.text for p in document.paragraphs]
    data = preprocess_oral_history(document)
    # hypothesis_username = "{}_{}".format(current_user.first_name.lower(), current_user.last_name.lower())
    hypothesis_grant_token = current_app.hypothesis_client.grant_token(username=current_user.username)

    # # get embed.js from the hypothesis service
    # try:
    #     from urllib.request import urlretrieve
    # except ImportError:
    #     from urllib import urlretrieve
    # embedjs_fname = os.path.join(current_app.static_folder, "embed.js")
    # urlretrieve(os.environ['HYPOTHESIS_SERVICE'] + "/embed.js", embedjs_fname)
    return render_template('main/display_oral_history.html', data=data, oral_hist=oral_hist, hypothesis_api_url=hypothesis_api_url, hypothesis_grant_token=hypothesis_grant_token.decode(), service_url=service_url)

@main.route('/_login_fake')
def _login_fake():
    return render_template('main._login_fake.html')
