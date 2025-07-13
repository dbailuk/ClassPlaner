from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectMultipleField, widgets, TimeField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo, Optional

class RegisterForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')
	
class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')


class TeacherForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    week_hours = IntegerField('Weekly Hours', validators=[DataRequired(), NumberRange(min=1)])

    preferred_days = SelectMultipleField(
        'Preferred Days (Optional)',
        choices=[
            (1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'),
            (4, 'Thursday'), (5, 'Friday')
        ],
        coerce=int,
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        validators=[Optional()]
    )

    preferred_periods = SelectMultipleField(
        'Preferred Periods (Optional)',
        coerce=int,
        choices=[],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        validators=[Optional()]
    )

    submit = SubmitField('Save Teacher')

class SubjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    default_hours_per_week = IntegerField(
        'Default Hours per Week', validators=[DataRequired(), NumberRange(min=1)]
    )
    default_room_id = SelectField(
        'Default Room (Optional)',
        coerce=int,
        choices=[],
        validators=[Optional()]
    )
    submit = SubmitField('Save Subject')

class ClassGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(min=1, max=50)])
    default_room_id = SelectField(
        'Default Room (Optional)',
        coerce=int,
        choices=[],
        validators=[Optional()]
    )
    allowed_periods = SelectMultipleField(
        'Allowed Periods',
        coerce=int,
        choices=[],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        validators=[Optional()]
    )
    submit = SubmitField('Save Class Group')

class ScheduleAssignmentForm(FlaskForm):
    class_group_id = SelectField(
        'Class Group', coerce=int, validators=[DataRequired()]
    )
    subject_id = SelectField(
        'Subject', coerce=int, validators=[DataRequired()]
    )
    teacher_id = SelectField(
        'Teacher',
        coerce=int,
        choices=[],
        validators=[Optional()]
    )
    hours_per_week = IntegerField(
        'Hours per Week', validators=[DataRequired(), NumberRange(min=1)]
    )
    room_id = SelectField(
        'Room (Optional)',
        coerce=int,
        choices=[],
        validators=[Optional()]
    )
    submit = SubmitField('Save Assignment')

class RoomForm(FlaskForm):
    name = StringField('Room Name', validators=[DataRequired(), Length(min=1, max=50)])
    type = StringField('Room Type (Optional)', validators=[Optional(), Length(max=50)])
    capacity = IntegerField('Capacity (Optional)', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Save Room')

class PeriodForm(FlaskForm):
    name = StringField('Period Name', validators=[DataRequired(), Length(min=1, max=50)])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    submit = SubmitField('Save Period')

class TimetableEntryForm(FlaskForm):
    class_group_id = SelectField(
        'Class Group', coerce=int, validators=[DataRequired()]
    )
    subject_id = SelectField(
        'Subject', coerce=int, validators=[DataRequired()]
    )
    teacher_id = SelectField(
        'Teacher (Optional)',
        coerce=int,
        choices=[],
        validators=[Optional()]
    )
    room_id = SelectField(
        'Room (Optional)',
        coerce=int,
        choices=[],
        validators=[Optional()]
    )
    period_id = SelectField(
        'Period', coerce=int, validators=[DataRequired()]
    )
    weekday = SelectField(
        'Weekday', coerce=int,
        choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday')],
        validators=[DataRequired()]
    )
    is_locked = BooleanField('Lock this entry')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Entry')
