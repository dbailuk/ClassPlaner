from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo
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
	username = StringField('Username', validators=[DataRequired(), Length(min = 3, max = 50)])
	password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=30)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')
	
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

