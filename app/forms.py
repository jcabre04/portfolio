from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import (
    BooleanField,
    DateTimeField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    FormField,
)

from wtforms.validators import DataRequired, Optional, ValidationError

import pytz


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class ProjectForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ProjectOptionForm(FlaskForm):
    new_project = StringField("New Project", validators=[Optional()])
    old_project = SelectField(
        "Existing Projects",
        validate_choice=False,
        coerce=int,
    )


class SessionForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    duration = IntegerField("Total Minutes", validators=[DataRequired()])
    level = SelectField(
        "Level",
        validators=[DataRequired()],
        choices=["untrained", "basic", "intermediate", "advanced", "master"],
    )
    explanation = TextAreaField("[optional] Explanation")
    timezone = SelectField(
        "Timezone", validators=[DataRequired()], choices=pytz.common_timezones
    )
    project = FormField(ProjectOptionForm)
    created = DateTimeField(
        "[optional] Date Completed (YYYY-MM-DD)",
        format="%Y-%m-%d",
        validators=[Optional()],
    )
    edited = DateTimeField(
        "[optional] Date Last Edited (YYYY-MM-DD)",
        format="%Y-%m-%d",
        validators=[Optional()],
    )
    starttime = DateTimeField(
        "Start Time (HH:MM)",
        format="%H:%M",
        validators=[DataRequired()],
    )
    endtime = DateTimeField(
        "End Time (HH:MM)",
        format="%H:%M",
        validators=[DataRequired()],
    )
    private = BooleanField("Private")
    skills = StringField("Skills", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_endtime(form, field):
        need_both_msg = "Either, fill out both Start and End time, or neither."
        end_smaller_msg = "End Time must not be earlier than Start Time."
        if field.data is None and form.starttime.data is not None:
            raise ValidationError(need_both_msg)
        elif field.data is not None and form.starttime.data is None:
            raise ValidationError(need_both_msg)
        elif field.data is not None and form.starttime.data is not None:
            if field.data < form.starttime.data:
                raise ValidationError(end_smaller_msg)


class SkillForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    explanation = TextAreaField("[optional] Explanation")
    submit = SubmitField("Submit")


class ImportBackupForm(FlaskForm):
    file = FileField("Backup File")
    submit = SubmitField("Submit")
