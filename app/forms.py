from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import IntegerField, SelectField, TextAreaField, DateTimeField
from wtforms.validators import DataRequired, ValidationError, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SessionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    duration = IntegerField('Total Minutes', validators=[DataRequired()])
    level = SelectField('Level', validators=[DataRequired()],
        choices=["untrained", "basic", "intermediate", "advanced", "master"])
    explanation = TextAreaField('[optional] Explanation')
    starttime = DateTimeField('[optional] Start Time (HH:MM)',
        format='%H:%M', validators=[Optional()])
    endtime = DateTimeField('[optional] End Time (HH:MM)',
        format='%H:%M', validators=[Optional()])
    private = BooleanField('Private')
    skills = StringField('Skills', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_endtime(form, field):
        if field.data is None and form.starttime.data is not None:
            raise ValidationError("Either, fill out both Start and End time, or neither.")
        elif field.data is not None and form.starttime.data is None:
            raise ValidationError("Either, fill out both Start and End time, or neither.")
        elif field.data is not None and form.starttime.data is not None:
            if field.data < form.starttime.data:
                raise ValidationError("End Time must not be earlier than Start Time.")
