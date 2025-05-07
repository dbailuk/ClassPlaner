from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectMultipleField, widgets, TimeField, SelectField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo, Optional
from app.models import Subject

class TeacherForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	availability = StringField('Availability')
	week_hours = IntegerField('Weekly Hours', validators=[DataRequired(), NumberRange(min=1)])
	subjects = SelectMultipleField(
	'Subjects',
	coerce=int,
	option_widget=widgets.CheckboxInput(),
	widget=widgets.ListWidget(prefix_label=False)
)
	submit = SubmitField('Add Teacher')

class SubjectForm(FlaskForm):
	name = StringField('Subject Name', validators=[DataRequired()])
	hours_per_week = IntegerField('Hours per Week', validators=[DataRequired(), NumberRange(min=1)])
	submit = SubmitField('Save Subject')

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
    class_id = SelectField('Class Group', coerce=int, validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int, validators=[DataRequired()])
    teacher_id = SelectField('Teacher', coerce=int, validators=[DataRequired()])
    room_id = SelectField('Room', coerce=int, validators=[DataRequired()])
    period_id = SelectField('Period', coerce=int, validators=[DataRequired()])
    weekday = SelectField('Weekday', coerce=int, choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday')], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Entry')