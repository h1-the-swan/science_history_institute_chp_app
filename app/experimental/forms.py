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
