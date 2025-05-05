from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, NumberRange, Length, EqualTo
from app.models import Subject

class TeacherForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	availability = StringField('Availability (e.g., Mon:1-3, Tue:2-4)')
	week_hours = IntegerField('Weekly Hours', validators=[DataRequired(), NumberRange(min=1)])
	subject = SelectMultipleField('Subject', coerce=int)
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

