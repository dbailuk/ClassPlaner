from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from app.models import Teacher, Subject, User, ClassGroup, Room, Period, TimetableEntry, ClassGroupSubject
from app.forms import TeacherForm, SubjectForm, RegisterForm, LoginForm, ClassGroupForm, RoomForm, PeriodForm, TimetableEntryForm, ClassGroupSubjectForm

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    return redirect(url_for('dashboard'))

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
		new_user = User(username=form.username.data, hashed_password=hashed_password)
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

@app.route('/logout', methods=['POST'])
@login_required
def logout():
	logout_user()
	flash('You have been logged out.', 'info')
	return redirect(url_for('login'))

@app.route('/teachers')
@login_required
def teacher_list():
    teachers = Teacher.query.filter_by(user_id=current_user.id).all()
    return render_template('teacher_list.html', teachers=teachers)

@app.route('/add-teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    form = TeacherForm()
    form.subjects.choices = [(s.id, s.name) for s in Subject.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        teacher = Teacher(
            user_id=current_user.id,
            name=form.name.data,
            week_hours=form.week_hours.data,
            availability=form.availability.data
        )

        selected_subjects = Subject.query.filter(Subject.id.in_(form.subjects.data), Subject.user_id == current_user.id).all()
        teacher.subjects = selected_subjects

        db.session.add(teacher)
        db.session.commit()

        flash('Teacher added successfully!', 'success')
        return redirect(url_for('teacher_list'))

    return render_template('add_teacher.html', form=form)

@app.route('/edit-teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    teacher = Teacher.query.filter_by(id=teacher_id, user_id=current_user.id).first_or_404()
    form = TeacherForm(obj=teacher)

    form.subjects.choices = [(s.id, s.name) for s in Subject.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        teacher.name = form.name.data
        teacher.week_hours = form.week_hours.data
        teacher.availability = form.availability.data

        selected_subjects = Subject.query.filter(Subject.id.in_(form.subjects.data), Subject.user_id == current_user.id).all()
        teacher.subjects = selected_subjects

        db.session.commit()
        flash('Teacher updated successfully!', 'success')
        return redirect(url_for('teacher_list'))

    form.subjects.data = [s.id for s in teacher.subjects]
    return render_template('add_teacher.html', form=form, editing=True)


@app.route('/delete-teacher/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.filter_by(id=teacher_id, user_id=current_user.id).first_or_404()
    try:
        TimetableEntry.query.filter_by(teacher_id=teacher_id, user_id=current_user.id).delete()

        teacher.subjects.clear()

        db.session.delete(teacher)
        db.session.commit()
        flash('Teacher deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting teacher: {e}', 'danger')

    return redirect(url_for('teacher_list'))


@app.route('/subjects')
@login_required
def subject_list():
	subjects = Subject.query.filter_by(user_id=current_user.id).all()
	return render_template('subject_list.html', subjects=subjects)

@app.route('/add-subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    form = SubjectForm()

    form.default_room_id.choices = [(r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        subject = Subject(
            user_id=current_user.id,
            name=form.name.data,
            default_hours_per_week=form.default_hours_per_week.data,
            default_room_id=form.default_room_id.data[0] if form.default_room_id.data else None
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('subject_list'))

    return render_template('add_subject.html', form=form)

@app.route('/edit-subject/<int:subject_id>', methods=['GET', 'POST'])
@login_required
def edit_subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    form = SubjectForm(obj=subject)

    form.default_room_id.choices = [(r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        subject.name = form.name.data
        subject.default_hours_per_week = form.default_hours_per_week.data
        subject.default_room_id = form.default_room_id.data[0] if form.default_room_id.data else None

        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('subject_list'))

    if subject.default_room_id:
        form.default_room_id.data = [subject.default_room_id]

    return render_template('add_subject.html', form=form, editing=True)

@app.route('/delete-subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    try:
        TimetableEntry.query.filter_by(subject_id=subject_id, user_id=current_user.id).delete()

        # Remove this subject from any associated teachers
        subject.teachers.clear()

        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting subject: {e}', 'danger')
    return redirect(url_for('subject_list'))

@app.route('/class-groups')
@login_required
def class_group_list():
	groups = ClassGroup.query.filter_by(user_id=current_user.id).all()
	return render_template('class_group_list.html', groups=groups)

@app.route('/add-class-group', methods=['GET', 'POST'])
@login_required
def add_class_group():
    form = ClassGroupForm()

    form.default_room_id.choices = [(r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        group = ClassGroup(
            user_id=current_user.id,
            name=form.name.data,
            default_room_id=form.default_room_id.data[0] if form.default_room_id.data else None
        )
        db.session.add(group)
        db.session.commit()
        flash('Class group added successfully!', 'success')
        return redirect(url_for('class_group_list'))

    return render_template('add_class_group.html', form=form)

@app.route('/edit-class-group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def edit_class_group(group_id):
    group = ClassGroup.query.filter_by(id=group_id, user_id=current_user.id).first_or_404()
    form = ClassGroupForm(obj=group)

    form.default_room_id.choices = [(r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        group.name = form.name.data
        group.default_room_id = form.default_room_id.data[0] if form.default_room_id.data else None

        db.session.commit()
        flash('Class group updated successfully!', 'success')
        return redirect(url_for('class_group_list'))

    if group.default_room_id:
        form.default_room_id.data = [group.default_room_id]

    return render_template('add_class_group.html', form=form, editing=True)


@app.route('/delete-class-group/<int:group_id>', methods=['POST'])
@login_required
def delete_class_group(group_id):
    group = ClassGroup.query.filter_by(id=group_id, user_id=current_user.id).first_or_404()
    try:
        TimetableEntry.query.filter_by(class_group_id=group_id, user_id=current_user.id).delete()
        # Remove any subject assignments for this class group
        ClassGroupSubject.query.filter_by(class_group_id=group_id, user_id=current_user.id).delete()

        # Clear associations with teachers
        group.teachers.clear()

        db.session.delete(group)
        db.session.commit()
        flash('Class group deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting class group: {e}', 'danger')

    return redirect(url_for('class_group_list'))


@app.route('/rooms')
@login_required
def room_list():
	rooms = Room.query.filter_by(user_id=current_user.id).all()
	return render_template('room_list.html', rooms=rooms)

@app.route('/add-room', methods=['GET', 'POST'])
@login_required
def add_room():
    form = RoomForm()
    
    if form.validate_on_submit():
        room = Room(
            user_id=current_user.id,
            name=form.name.data,
            type=form.type.data,
            capacity=form.capacity.data
        )
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('room_list'))

    return render_template('add_room.html', form=form)

@app.route('/edit-room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = Room.query.filter_by(id=room_id, user_id=current_user.id).first_or_404()
    form = RoomForm(obj=room)

    if form.validate_on_submit():
        room.name = form.name.data
        room.type = form.type.data
        room.capacity = form.capacity.data

        db.session.commit()
        flash('Room updated successfully!', 'success')
        return redirect(url_for('room_list'))

    return render_template('add_room.html', form=form, editing=True)

@app.route('/delete-room/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    room = Room.query.filter_by(id=room_id, user_id=current_user.id).first_or_404()
    try:
        TimetableEntry.query.filter_by(room_id=room_id, user_id=current_user.id).delete()

        # Remove this room as a default room for any class groups
        ClassGroup.query.filter_by(default_room_id=room_id, user_id=current_user.id).update({"default_room_id": None})

        # Remove this room as a default room for any subjects
        Subject.query.filter_by(default_room_id=room_id, user_id=current_user.id).update({"default_room_id": None})

        # Remove this room from any class group subject overrides
        ClassGroupSubject.query.filter_by(room_id=room_id, user_id=current_user.id).update({"room_id": None})

        db.session.delete(room)
        db.session.commit()
        flash('Room deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting room: {e}', 'danger')
    return redirect(url_for('room_list'))

@app.route('/periods')
@login_required
def period_list():
    periods = Period.query.filter_by(user_id=current_user.id).order_by(Period.start_time).all()
    return render_template('period_list.html', periods=periods)

@app.route('/add-period', methods=['GET', 'POST'])
@login_required
def add_period():
    form = PeriodForm()
    
    if form.validate_on_submit():
        period = Period(
            user_id=current_user.id,
            name=form.name.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data
        )
        db.session.add(period)
        db.session.commit()
        flash('Period added successfully!', 'success')
        return redirect(url_for('period_list'))
    return render_template('add_period.html', form=form)


@app.route('/edit-period/<int:period_id>', methods=['GET', 'POST'])
@login_required
def edit_period(period_id):
    period = Period.query.filter_by(id=period_id, user_id=current_user.id).first_or_404()
    form = PeriodForm(obj=period)

    if form.validate_on_submit():
        period.name = form.name.data
        period.start_time = form.start_time.data
        period.end_time = form.end_time.data
        db.session.commit()
        flash('Period updated successfully!', 'success')
        return redirect(url_for('period_list'))
    return render_template('add_period.html', form=form, editing=True)

@app.route('/delete-period/<int:period_id>', methods=['POST'])
@login_required
def delete_period(period_id):
    period = Period.query.filter_by(id=period_id, user_id=current_user.id).first_or_404()

    try:
         # Delete all timetable entries using this period
        TimetableEntry.query.filter_by(period_id=period_id, user_id=current_user.id).delete()

        db.session.delete(period)
        db.session.commit()
        flash('Period deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting period: {e}', 'danger')
    return redirect(url_for('period_list'))

@app.route('/class-group-subjects')
@login_required
def class_group_subject_list():
    assignments = ClassGroupSubject.query.filter_by(user_id=current_user.id).all()
    return render_template('class_group_subject_list.html', assignments=assignments)

@app.route('/add-class-group-subject', methods=['GET', 'POST'])
@login_required
def add_class_group_subject():
    form = ClassGroupSubjectForm()

    # Populate choices
    form.class_group_id.choices = [(cg.id, cg.name) for cg in ClassGroup.query.filter_by(user_id=current_user.id).all()]
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.filter_by(user_id=current_user.id).all()]
    form.room_id.choices = [(0, "Default Group Room")] + [(r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id).all()]
    form.teacher_id.choices = [(t.id, t.name) for t in Teacher.query.filter_by(user_id=current_user.id).all()]

    if form.validate_on_submit():
        assignment = ClassGroupSubject(
            user_id=current_user.id,
            class_group_id=form.class_group_id.data,
            subject_id=form.subject_id.data,
            teacher_id=form.teacher_id.data if form.teacher_id.data != 0 else None,
            hours_per_week=form.hours_per_week.data,
            room_id=form.room_id.data if form.room_id.data else None
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Class group subject assignment added successfully!', 'success')
        return redirect(url_for('class_group_subject_list'))

    return render_template('add_class_group_subject.html', form=form)

@app.route('/edit-class-group-subject/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def edit_class_group_subject(assignment_id):
    assignment = ClassGroupSubject.query.filter_by(id=assignment_id, user_id=current_user.id).first_or_404()
    form = ClassGroupSubjectForm(obj=assignment)

    # Populate choices
    form.class_group_id.choices = [(cg.id, cg.name) for cg in ClassGroup.query.filter_by(user_id=current_user.id).all()]
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.filter_by(user_id=current_user.id).all()]
    form.room_id.choices = [(0, "Default Group Room")] + [(r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id).all()]
    form.teacher_id.choices = [(t.id, t.name) for t in Teacher.query.filter_by(user_id=current_user.id).all()]

    # Set the current values for the assignment
    form.teacher_id.data = assignment.teacher_id if assignment.teacher_id else 0

    if form.validate_on_submit():
        assignment.class_group_id = form.class_group_id.data
        assignment.subject_id = form.subject_id.data
        assignment.teacher_id = form.teacher_id.data if form.teacher_id.data != 0 else None
        assignment.hours_per_week = form.hours_per_week.data
        assignment.room_id = form.room_id.data if form.room_id.data else None

        db.session.commit()
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('class_group_subject_list'))

    return render_template('add_class_group_subject.html', form=form, editing=True)

@app.route('/delete-class-group-subject/<int:assignment_id>', methods=['POST'])
@login_required
def delete_class_group_subject(assignment_id):
    assignment = ClassGroupSubject.query.filter_by(id=assignment_id, user_id=current_user.id).first_or_404()

    try:
        db.session.delete(assignment)
        db.session.commit()
        flash('Assignment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting assignment: {e}', 'danger')

    return redirect(url_for('class_group_subject_list'))

@app.route('/timetable')
@login_required
def timetable_list():
    entries = TimetableEntry.query.filter_by(user_id=current_user.id).order_by(TimetableEntry.weekday, TimetableEntry.period_id).all()
    return render_template('timetable_list.html', entries=entries)

@app.route('/add-timetable-entry', methods=['GET', 'POST'])
@login_required
def add_timetable_entry():
    form = TimetableEntryForm()

    form.class_group_id.choices = [(c.id, c.name) for c in ClassGroup.query.filter_by(user_id=current_user.id).all()]
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.filter_by(user_id=current_user.id).all()]
    form.teacher_id.choices = [(t.id, t.name) for t in Teacher.query.filter_by(user_id=current_user.id).all()]
    form.room_id.choices = [(r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id).all()]
    form.period_id.choices = [(p.id, f"{p.start_time.strftime('%H:%M')} - {p.end_time.strftime('%H:%M')}") for p in Period.query.filter_by(user_id=current_user.id).order_by(Period.start_time).all()]

    if form.validate_on_submit():
        entry = TimetableEntry(
            user_id=current_user.id,
            class_group_id=form.class_group_id.data[0],
            subject_id=form.subject_id.data[0],
            teacher_id=form.teacher_id.data[0],
            room_id=form.room_id.data[0],
            period_id=form.period_id.data[0],
            weekday=form.weekday.data,
            notes=form.notes.data,
            is_locked=form.is_locked.data[0] if form.is_locked.data else False
        )

        db.session.add(entry)
        db.session.commit()
        flash('Timetable entry added successfully!', 'success')
        return redirect(url_for('timetable_list'))

    return render_template('add_timetable_entry.html', form=form)

@app.route('/edit-timetable-entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_timetable_entry(entry_id):
    # Ensure the entry belongs to the current user
    entry = TimetableEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()
    form = TimetableEntryForm(obj=entry)

    # Populate choices
    form.class_group_id.choices = [(c.id, c.name) for c in ClassGroup.query.filter_by(user_id=current_user.id).all()]
    form.subject_id.choices = [(s.id, s.name) for s in Subject.query.filter_by(user_id=current_user.id).all()]
    form.teacher_id.choices = [(t.id, t.name) for t in Teacher.query.filter_by(user_id=current_user.id).all()]
    form.room_id.choices = [(r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id).all()]
    form.period_id.choices = [(p.id, f"{p.start_time.strftime('%H:%M')} - {p.end_time.strftime('%H:%M')}") for p in Period.query.filter_by(user_id=current_user.id).order_by(Period.start_time).all()]

    if form.validate_on_submit():
        entry.class_group_id = form.class_group_id.data[0]
        entry.subject_id = form.subject_id.data[0]
        entry.teacher_id = form.teacher_id.data[0]
        entry.room_id = form.room_id.data[0]
        entry.period_id = form.period_id.data[0]
        entry.weekday = form.weekday.data
        entry.notes = form.notes.data
        entry.is_locked = form.is_locked.data[0] if form.is_locked.data else False

        db.session.commit()
        flash('Timetable entry updated successfully!', 'success')
        return redirect(url_for('timetable_list'))

    # Pre-select the current lock status
    form.is_locked.data = [entry.is_locked]

    return render_template('add_timetable_entry.html', form=form, editing=True)

@app.route('/delete-timetable-entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_timetable_entry(entry_id):
    entry = TimetableEntry.query.filter_by(id=entry_id, user_id=current_user.id).first_or_404()

    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Timetable entry deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting entry: {e}', 'danger')

    return redirect(url_for('timetable_list'))
