from flask import url_for
from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    TextAreaField,
    SubmitField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import Email, EqualTo, InputRequired, Length

from app.models import User

class UpdateProfileForm(FlaskForm):
    bio = TextAreaField('Bio', validators=[Length(0, 20000)])
    website = StringField('Personal Website', validators=[Length(0, 128)])
    submit = SubmitField('Update Profile')

class LoginForm(FlaskForm):
    # email = EmailField(
    #     'Email or username', validators=[InputRequired(),
    #                          Length(1, 128),
    #                          Email()])
    email = StringField(
        'Email or username', validators=[InputRequired(),
                             Length(1, 128),
                             ])
    password = PasswordField('Password', validators=[InputRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm):
    # first_name = StringField(
    #     'First name', validators=[InputRequired(),
    #                               Length(1, 64)])
    # last_name = StringField(
    #     'Last name', validators=[InputRequired(),
    #                              Length(1, 64)])
    username = StringField(
        'Username', validators=[InputRequired(),
                                 Length(1, 64)])
    full_name = StringField(
        'Full name', validators=[InputRequired(),
                                 Length(1, 128)])
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 128),
                             Email()])
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match')
        ])
    password2 = PasswordField('Confirm password', validators=[InputRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered. (Did you mean to '
                                  '<a href="{}">log in</a> instead?)'.format(
                url_for('account.login')))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken!')


class RequestResetPasswordForm(FlaskForm):
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 128),
                             Email()])
    submit = SubmitField('Reset password')

    # We don't validate the email address so we don't confirm to attackers
    # that an account with the given email exists.


class ResetPasswordForm(FlaskForm):
    email = EmailField(
        'Email', validators=[InputRequired(),
                             Length(1, 128),
                             Email()])
    new_password = PasswordField(
        'New password',
        validators=[
            InputRequired(),
            EqualTo('new_password2', 'Passwords must match.')
        ])
    new_password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Reset password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')


class CreatePasswordForm(FlaskForm):
    password = PasswordField(
        'Password',
        validators=[
            InputRequired(),
            EqualTo('password2', 'Passwords must match.')
        ])
    password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Set password')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[InputRequired()])
    new_password = PasswordField(
        'New password',
        validators=[
            InputRequired(),
            EqualTo('new_password2', 'Passwords must match.')
        ])
    new_password2 = PasswordField(
        'Confirm new password', validators=[InputRequired()])
    submit = SubmitField('Update password')


class ChangeEmailForm(FlaskForm):
    email = EmailField(
        'New email', validators=[InputRequired(),
                                 Length(1, 128),
                                 Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Update email')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
