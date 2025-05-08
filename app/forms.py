from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectMultipleField, widgets, TimeField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo, Optional
from app.models import Subject

class TeacherForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	week_hours = IntegerField('Weekly Hours', validators=[DataRequired(), NumberRange(min=1)])
	subjects = SelectMultipleField(
	'Subjects',
	coerce=int,
	option_widget=widgets.CheckboxInput(),
	widget=widgets.ListWidget(prefix_label=False)
)
	availability = TextAreaField("Availability(Optional)")
	submit = SubmitField('Add Teacher')

class SubjectForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    default_hours_per_week = IntegerField('Default Hours per Week', validators=[DataRequired(), NumberRange(min=1)])
    default_room_id = SelectMultipleField('Default Room (Optional)', coerce=int, choices=[])
    submit = SubmitField('Save Subject')

class ClassGroupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    default_room_id = SelectMultipleField('Default Room (Optional)', coerce=int, choices=[])
    submit = SubmitField('Save Class Group')

class ClassGroupSubjectForm(FlaskForm):
    class_group_id = SelectMultipleField('Class Group', coerce=int, choices=[])
    subject_id = SelectMultipleField('Subject', coerce=int, choices=[])
    hours_per_week = IntegerField('Hours per Week', validators=[DataRequired(), NumberRange(min=1)])
    room_id = SelectMultipleField('Room (Optional, for overrides)', coerce=int, choices=[])
    submit = SubmitField('Save Assignment')

class RegisterForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')
	
class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')

class ClassGroupForm(FlaskForm):
	name = StringField('Group Name', validators=[DataRequired(), Length(min=1, max=50)])
	default_room_id = SelectMultipleField('Default Room (Optional)', coerce=int, choices=[])
	submit = SubmitField('Save Group')

class RoomForm(FlaskForm):
	name = StringField('Room Name', validators=[DataRequired(), Length(min=1, max=50)])
	type = StringField('Room Type (optional)', validators=[Optional(), Length(max=50)])
	capacity = IntegerField('Capacity (optional)', validators=[Optional(), NumberRange(min=1)])
	submit = SubmitField('Save Room')

class PeriodForm(FlaskForm):
    name = StringField('Period Name', validators=[DataRequired(), Length(min=1, max=50)])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    submit = SubmitField('Save Period')

class TimetableEntryForm(FlaskForm):
    class_group_id = SelectMultipleField('Class Group', coerce=int, choices=[])
    subject_id = SelectMultipleField('Subject', coerce=int, choices=[])
    teacher_id = SelectMultipleField('Teacher', coerce=int, choices=[])
    room_id = SelectMultipleField('Room', coerce=int, choices=[])
    period_id = SelectMultipleField('Period', coerce=int, choices=[])
    weekday = IntegerField('Weekday (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    notes = TextAreaField('Notes')
    is_locked = SelectMultipleField('Lock this Entry?', coerce=bool, choices=[(False, 'No'), (True, 'Yes')])
    submit = SubmitField('Save Entry')