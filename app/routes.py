from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Teacher, Subject
from app.forms import TeacherForm

@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')

@app.route('/teachers')
def teacher_list():
	teachers = Teacher.query.all()
	return (render_template("teacher_list.html", teachers = teachers))

@app.route('/add-teacher', methods=['GET', 'POST'])
def add_teacher():
	form = TeacherForm()
	form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]

	if form.validate_on_submit():
		new_teacher = Teacher(
			name = form.name.data,
			availability = form.availability.data,
			week_hours = form.week_hours.data
		)

		selected_subjects = Subject.query.filter(Subject.id.in_(form.subject.data)).all()
		new_teacher.subject = selected_subjects

		db.session.add(new_teacher)
		db.session.commit()

		flash('Teacher added successfully!')
		return redirect(url_for('teacher_list'))

	return render_template('add_teacher.html', form=form)