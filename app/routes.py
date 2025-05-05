from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Teacher, Subject
from app.forms import TeacherForm

@app.route('/')
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

@app.route('/edit_teacher/<int:teacher_id>', methods=["GET", "POST"])
def edit_teacher(teacher_id):
	teacher = Teacher.query.get_or_404(teacher_id)
	form = TeacherForm(obj=Teacher)
	form.subject.choices = [(s.id, s.name) for s in Subject.query.all()]
	form.subject.data = [s.id for s in teacher.subjects]

	if form.validate_on_submit():
		teacher.name = form.name.data
		teacher.availability = form.availability.data
		teacher.week_hours = form.week_hours.data

		selected_subjects = Subject.query.filter(Subject.id.in_(form.subject.data)).all()
		teacher.subject = selected_subjects

		db.session.commit()
		flash('Teacher updated successfully!')

	return redirect(url_for('teacher_list'))

@app.route('/delete-teacher/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
	teacher = Teacher.query.get_or_404(teacher_id)
	try:
		db.session.delete(teacher)
		db.session.commit()
		flash('Teacher deleted successfully.')
	except Exception as e:
		db.session.rollback()
		flash('Could not delete teacher. Error: {}'.format(e), 'danger')
	return redirect(url_for('teacher_list'))

@app.route('/subjects')
def subject_list():
	subjects = Subject.query.all()
	return render_template(subject_list.html, subjects=subjects)

@app.route('/add-subject', methods=['GET', 'POST'])
def add_subject():
    form = SubjectForm()

    if form.validate_on_submit():
        new_subject = Subject(
            name=form.name.data,
            hours_per_week=form.hours_per_week.data
        )
        db.session.add(new_subject)
        db.session.commit()

        flash('Subject added successfully!')
    return redirect(url_for('subject_list'))

    return render_template('add_subject.html', form=form)

@app.route('/edit-subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = SubjectForm(obj=subject)

    if form.validate_on_submit():
        subject.name = form.name.data
        subject.hours_per_week = form.hours_per_week.data

        db.session.commit()
        flash('Subject updated successfully!')
        return redirect(url_for('subject_list'))

    return render_template('add_subject.html', form=form, editing=True)

@app.route('/delete-subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    try:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully.')
    except Exception as e:
        db.session.rollback()
        flash('Could not delete subject. Error: {}'.format(e), 'danger')
    return redirect(url_for('subject_list'))
