from flask import url_for
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    TextAreaField,
    SubmitField,
    SelectField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length

class SelectOralHistory(FlaskForm):
    choice = SelectField(coerce=int)

class AddNewEntityForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    description = StringField('Description')
    wikipedia_page_title = StringField('Wikipedia page title')

    submit = SubmitField('Submit')

