from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from app.models import Teacher, Subject, User
from app.forms import TeacherForm

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		existing_user = User.query.filter_by(username=form.username.data).first()
		if existing_user:
			flash('Username already exists. Please choose another.', 'danger')
			return redirect(url_for('register'))

		hashed_password = generate_password_hash(form.password.data)
		new_user = User(username=form.username.data, hashed_password=hashed_password, role='admin')
		db.session.add(new_user)
		db.session.commit()
		flash('Account created! You can now log in.', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user and check_password_hash(user.hashed_password, form.password.data):
			login_user(user)
			flash('Logged in successfully!', 'success')
			return redirect(url_for('dashboard'))
		else:
			flash('Invalid username or password', 'danger')
	return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.', 'info')
	return redirect(url_for('login'))

@app.route('/teachers')
@login_required
def teacher_list():
	teachers = Teacher.query.all()
	return (render_template("teacher_list.html", teachers = teachers))

@app.route('/add-teacher', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
def subject_list():
	subjects = Subject.query.all()
	return render_template(subject_list.html, subjects=subjects)

@app.route('/add-subject', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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
