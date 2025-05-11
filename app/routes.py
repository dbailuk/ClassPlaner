from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, login_manager
from app.schedule_generator import generate_schedule
from app.models import Teacher, Subject, User, ClassGroup, Room, Period, TimetableEntry, ScheduleAssignment
from app.forms import TeacherForm, SubjectForm, RegisterForm, LoginForm, ClassGroupForm, RoomForm, PeriodForm, TimetableEntryForm, ScheduleAssignmentForm

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
    # get the periods in time‐order
    periods = Period.query.filter_by(user_id=current_user.id).order_by(Period.start_time).all()
    # build a lookup: (weekday, period_id) → TimetableEntry
    entries = TimetableEntry.query.filter_by(user_id=current_user.id).all()
    # build a list of entries per (weekday,period)
    grid = {}
    for e in entries:
        key = (e.weekday, e.period_id)
        grid.setdefault(key, []).append(e)
    return render_template('dashboard.html', periods=periods, grid=grid)

@app.route('/move-entry', methods=['POST'])
@login_required
def move_timetable_entry():
    data = request.get_json()
    e = TimetableEntry.query.filter_by(
          id=data["entry_id"], user_id=current_user.id
        ).first_or_404()

    # apply the change
    e.weekday   = data["weekday"]
    e.period_id = data["period_id"]
    try:
        db.session.commit()
        return {"success": True}
    except Exception as ex:
        db.session.rollback()
        return {"success": False, "error": str(ex)}, 400


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
    periods = Period.query.filter_by(user_id=current_user.id).all()
    periods_dict = {p.id: p for p in periods}

    return render_template('teacher_list.html', teachers=teachers, periods_dict=periods_dict)

@app.route('/add-teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    form = TeacherForm()

    # Populate preferred periods choices
    form.preferred_periods.choices = [
        (p.id, f"{p.name} ({p.start_time.strftime('%H:%M')} - {p.end_time.strftime('%H:%M')})") 
        for p in Period.query.filter_by(user_id=current_user.id).all()
    ]

    if form.validate_on_submit():
        teacher = Teacher(
            user_id=current_user.id,
            name=form.name.data.strip(),
            week_hours=form.week_hours.data,
            preferred_days=','.join(map(str, form.preferred_days.data)) or None,
            preferred_periods=','.join(map(str, form.preferred_periods.data)) or None
        )

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

    # Populate preferred periods choices
    form.preferred_periods.choices = [
        (p.id, f"{p.name} ({p.start_time.strftime('%H:%M')} - {p.end_time.strftime('%H:%M')})") 
        for p in Period.query.filter_by(user_id=current_user.id).all()
    ]

    if form.validate_on_submit():
        teacher.name = form.name.data.strip()
        teacher.week_hours = form.week_hours.data
        teacher.preferred_days = ','.join(map(str, form.preferred_days.data)) or None
        teacher.preferred_periods = ','.join(map(str, form.preferred_periods.data)) or None

        db.session.commit()
        flash('Teacher updated successfully!', 'success')
        return redirect(url_for('teacher_list'))

    # Set initial selected values for periods and days after form submission check
    if teacher.preferred_days:
        form.preferred_days.data = list(map(int, teacher.preferred_days.split(',')))
    if teacher.preferred_periods:
        form.preferred_periods.data = list(map(int, teacher.preferred_periods.split(',')))

    return render_template('add_teacher.html', form=form, editing=True)


@app.route('/delete-teacher/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.filter_by(id=teacher_id, user_id=current_user.id).first_or_404()
    try:
        TimetableEntry.query.filter_by(teacher_id=teacher_id, user_id=current_user.id).delete()

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
    subjects = Subject.query.filter_by(user_id=current_user.id).order_by(Subject.name).all()
    return render_template('subject_list.html', subjects=subjects)

@app.route('/add-subject', methods=['GET', 'POST'])
@login_required
def add_subject():
    form = SubjectForm()
    # populate room choices as ints
    form.default_room_id.choices = [(0, "No Room")] + [
        (r.id, r.name)
        for r in Room.query.filter_by(user_id=current_user.id)
    ]

    if form.validate_on_submit():
        name = form.name.data.strip()
        default_hours = form.default_hours_per_week.data
        room_id = form.default_room_id.data if form.default_room_id.data != 0 else None

        # avoid duplicates
        if Subject.query.filter_by(user_id=current_user.id, name=name).first():
            flash(f'Subject "{name}" already exists.', 'danger')
        else:
            subject = Subject(
                user_id=current_user.id,
                name=name,
                default_hours_per_week=default_hours,
                default_room_id=room_id
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

    form.default_room_id.choices = [(0, "No Room")] + [
        (r.id, r.name)
        for r in Room.query.filter_by(user_id=current_user.id)
    ]

    if form.validate_on_submit():
        new_name = form.name.data.strip()
        new_hours = form.default_hours_per_week.data
        new_room = form.default_room_id.data if form.default_room_id.data != 0 else None

        dup = Subject.query.filter_by(user_id=current_user.id, name=new_name).first()
        if dup and dup.id != subject_id:
            flash(f'Subject "{new_name}" already exists.', 'danger')
        else:
            subject.name = new_name
            subject.default_hours_per_week = new_hours
            subject.default_room_id = new_room
            db.session.commit()
            flash('Subject updated successfully!', 'success')
            return redirect(url_for('subject_list'))

    # only after validate_on_submit do we seed the form
    form.default_room_id.data = subject.default_room_id or 0

    return render_template('add_subject.html', form=form, editing=True)


@app.route('/delete-subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.filter_by(id=subject_id, user_id=current_user.id).first_or_404()
    try:
        # clean up any timetable entries first
        TimetableEntry.query.filter_by(subject_id=subject_id, user_id=current_user.id).delete()
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
    periods = Period.query.filter_by(user_id=current_user.id).all()
    periods_dict = {p.id: p for p in periods}

    for group in groups:
        if group.allowed_periods:
            period_ids = map(int, group.allowed_periods.split(','))
            group.periods_list = [periods_dict[pid] for pid in period_ids if pid in periods_dict]
        else:
            group.periods_list = []

    return render_template('class_group_list.html', groups=groups)


@app.route('/add-class-group', methods=['GET', 'POST'])
@login_required
def add_class_group():
    form = ClassGroupForm()

    form.default_room_id.choices = [(0, "No Default Room")] + [(r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id).all()]
    
    form.allowed_periods.choices = [
        (p.id, f"{p.name} ({p.start_time.strftime('%H:%M')} - {p.end_time.strftime('%H:%M')})")
        for p in Period.query.filter_by(user_id=current_user.id).all()
    ]

    if form.validate_on_submit():
        group = ClassGroup(
            user_id=current_user.id,
            name=form.name.data.strip(),
            default_room_id=form.default_room_id.data if form.default_room_id.data != "0" else None,
            allowed_periods=','.join(map(str, form.allowed_periods.data)) or None
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
    form  = ClassGroupForm(obj=group)

    # populate choices
    form.default_room_id.choices = [(0, "No Room")] + [
        (r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id)
    ]
    form.allowed_periods.choices = [
        (p.id, f"{p.name} ({p.start_time.strftime('%H:%M')} - {p.end_time.strftime('%H:%M')})")
        for p in Period.query.filter_by(user_id=current_user.id)
    ]

    if form.validate_on_submit():
        group.name            = form.name.data.strip()
        group.default_room_id = form.default_room_id.data if form.default_room_id.data != 0 else None
        group.allowed_periods = ','.join(map(str, form.allowed_periods.data)) or None

        db.session.commit()
        flash('Class group updated successfully!', 'success')
        return redirect(url_for('class_group_list'))

    form.default_room_id.data = group.default_room_id if group.default_room_id else 0
    if group.allowed_periods:
        form.allowed_periods.data = list(map(int, group.allowed_periods.split(',')))

    return render_template('add_class_group.html', form=form, editing=True)

@app.route('/delete-class-group/<int:group_id>', methods=['POST'])
@login_required
def delete_class_group(group_id):
    group = ClassGroup.query.filter_by(id=group_id, user_id=current_user.id).first_or_404()
    try:
        TimetableEntry.query.filter_by(class_group_id=group_id, user_id=current_user.id).delete()
        ScheduleAssignment.query.filter_by(class_group_id=group_id, user_id=current_user.id).delete()
        group.allowed_periods = None
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
    # List all rooms, ordered alphabetically
    rooms = Room.query.filter_by(user_id=current_user.id).order_by(Room.name).all()
    return render_template('room_list.html', rooms=rooms)


@app.route('/add-room', methods=['GET', 'POST'])
@login_required
def add_room():
    form = RoomForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        type_ = form.type.data.strip() if form.type.data else None
        capacity = form.capacity.data

        # Prevent duplicate room names
        if Room.query.filter_by(user_id=current_user.id, name=name).first():
            flash(f'Room "{name}" already exists.', 'danger')
        else:
            room = Room(
                user_id=current_user.id,
                name=name,
                type=type_,
                capacity=capacity
            )
            db.session.add(room)
            db.session.commit()
            flash('Room added successfully!', 'success')
            return redirect(url_for('room_list'))

    # On GET or validation failure, fall through and re-render form
    return render_template('add_room.html', form=form)


@app.route('/edit-room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = Room.query.filter_by(id=room_id, user_id=current_user.id).first_or_404()
    form = RoomForm(obj=room)

    if form.validate_on_submit():
        new_name = form.name.data.strip()
        new_type = form.type.data.strip() if form.type.data else None
        new_capacity = form.capacity.data

        # Prevent renaming collision
        dup = Room.query.filter_by(user_id=current_user.id, name=new_name).first()
        if dup and dup.id != room_id:
            flash(f'Room "{new_name}" already exists.', 'danger')
        else:
            room.name = new_name
            room.type = new_type
            room.capacity = new_capacity
            db.session.commit()
            flash('Room updated successfully!', 'success')
            return redirect(url_for('room_list'))

    # On GET (or validation failure), WTForms will already have populated form via obj=room
    return render_template('add_room.html', form=form, editing=True)


@app.route('/delete-room/<int:room_id>', methods=['POST'])
@login_required
def delete_room(room_id):
    room = Room.query.filter_by(id=room_id, user_id=current_user.id).first_or_404()
    try:
        # Clean up references
        TimetableEntry.query.filter_by(room_id=room_id, user_id=current_user.id).delete()
        ClassGroup.query.filter_by(default_room_id=room_id, user_id=current_user.id)\
                  .update({"default_room_id": None})
        Subject.query.filter_by(default_room_id=room_id, user_id=current_user.id)\
               .update({"default_room_id": None})
        ScheduleAssignment.query.filter_by(room_id=room_id, user_id=current_user.id)\
                       .update({"room_id": None})

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
    periods = Period.query.filter_by(user_id=current_user.id)\
                          .order_by(Period.start_time).all()
    return render_template('period_list.html', periods=periods)


@app.route('/add-period', methods=['GET', 'POST'])
@login_required
def add_period():
    form = PeriodForm()
    if form.validate_on_submit():
        # ensure start is earlier than end
        if form.start_time.data >= form.end_time.data:
            flash('Start time must be before end time.', 'danger')
        else:
            period = Period(
                user_id=current_user.id,
                name=form.name.data.strip(),
                start_time=form.start_time.data,
                end_time=form.end_time.data
            )
            db.session.add(period)
            db.session.commit()
            flash('Period added successfully!', 'success')
            return redirect(url_for('period_list'))
    # on GET or validation failure:
    return render_template('add_period.html', form=form)


@app.route('/edit-period/<int:period_id>', methods=['GET', 'POST'])
@login_required
def edit_period(period_id):
    period = Period.query.filter_by(id=period_id, user_id=current_user.id).first_or_404()
    form = PeriodForm(obj=period)
    if form.validate_on_submit():
        if form.start_time.data >= form.end_time.data:
            flash('Start time must be before end time.', 'danger')
        else:
            period.name       = form.name.data.strip()
            period.start_time = form.start_time.data
            period.end_time   = form.end_time.data
            db.session.commit()
            flash('Period updated successfully!', 'success')
            return redirect(url_for('period_list'))
    # WTForms’ obj=period already pre‐fills on GET
    return render_template('add_period.html', form=form, editing=True)


@app.route('/delete-period/<int:period_id>', methods=['POST'])
@login_required
def delete_period(period_id):
    period = Period.query.filter_by(id=period_id, user_id=current_user.id).first_or_404()
    try:
        # remove any timetable entries using this period
        TimetableEntry.query.filter_by(period_id=period_id, user_id=current_user.id).delete()
        db.session.delete(period)
        db.session.commit()
        flash('Period deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting period: {e}', 'danger')
    return redirect(url_for('period_list'))



@app.route('/schedule-assignments')
@login_required
def schedule_assignment_list():
    assignments = ScheduleAssignment.query.filter_by(user_id=current_user.id).all()
    return render_template('schedule_assignment_list.html', assignments=assignments)


@app.route('/add-schedule-assignment', methods=['GET', 'POST'])
@login_required
def add_schedule_assignment():
    form = ScheduleAssignmentForm()

    # Populate dropdowns
    form.class_group_id.choices = [
        (cg.id, cg.name)
        for cg in ClassGroup.query.filter_by(user_id=current_user.id)
    ]
    form.subject_id.choices = [
        (s.id, s.name)
        for s in Subject.query.filter_by(user_id=current_user.id)
    ]
    form.teacher_id.choices = [(0, "No Specific Teacher")] + [
        (t.id, t.name)
        for t in Teacher.query.filter_by(user_id=current_user.id)
    ]
    form.room_id.choices = [(0, "Default Room")] + [
        (r.id, r.name)
        for r in Room.query.filter_by(user_id=current_user.id)
    ]

    if form.validate_on_submit():
        assignment = ScheduleAssignment(
            user_id=current_user.id,
            class_group_id=form.class_group_id.data,
            subject_id=form.subject_id.data,
            teacher_id=form.teacher_id.data or None,
            hours_per_week=form.hours_per_week.data,
            room_id=form.room_id.data or None
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Schedule assignment added successfully!', 'success')
        return redirect(url_for('schedule_assignment_list'))

    return render_template('add_schedule_assignment.html', form=form)


@app.route('/edit-schedule-assignment/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def edit_schedule_assignment(assignment_id):
    assignment = ScheduleAssignment.query.filter_by(
        id=assignment_id, user_id=current_user.id
    ).first_or_404()
    form = ScheduleAssignmentForm(obj=assignment)

    # Populate dropdowns
    form.class_group_id.choices = [
        (cg.id, cg.name)
        for cg in ClassGroup.query.filter_by(user_id=current_user.id)
    ]
    form.subject_id.choices = [
        (s.id, s.name)
        for s in Subject.query.filter_by(user_id=current_user.id)
    ]
    form.teacher_id.choices = [(0, "No Specific Teacher")] + [
        (t.id, t.name)
        for t in Teacher.query.filter_by(user_id=current_user.id)
    ]
    form.room_id.choices = [(0, "Default Room")] + [
        (r.id, r.name)
        for r in Room.query.filter_by(user_id=current_user.id)
    ]

    if form.validate_on_submit():
        assignment.class_group_id = form.class_group_id.data
        assignment.subject_id     = form.subject_id.data
        assignment.teacher_id     = form.teacher_id.data or None
        assignment.hours_per_week = form.hours_per_week.data
        assignment.room_id        = form.room_id.data or None

        db.session.commit()
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('schedule_assignment_list'))

    # pre‐fill form with existing values
    form.class_group_id.data = assignment.class_group_id
    form.subject_id.data     = assignment.subject_id
    form.teacher_id.data     = assignment.teacher_id or 0
    form.hours_per_week.data = assignment.hours_per_week
    form.room_id.data        = assignment.room_id    or 0

    return render_template('add_schedule_assignment.html', form=form, editing=True)


@app.route('/delete-schedule-assignment/<int:assignment_id>', methods=['POST'])
@login_required
def delete_schedule_assignment(assignment_id):
    assignment = ScheduleAssignment.query.filter_by(
        id=assignment_id, user_id=current_user.id
    ).first_or_404()
    try:
        db.session.delete(assignment)
        db.session.commit()
        flash('Assignment deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting assignment: {e}', 'danger')
    return redirect(url_for('schedule_assignment_list'))

@app.route('/timetable')
@login_required
def timetable_list():
    entries = (
        TimetableEntry.query
        .filter_by(user_id=current_user.id)
        .order_by(TimetableEntry.weekday, TimetableEntry.period_id)
        .all()
    )
    return render_template('timetable_list.html', entries=entries)


@app.route('/add-timetable-entry', methods=['GET', 'POST'])
@login_required
def add_timetable_entry():
    form = TimetableEntryForm()

    # 1) populate dropdowns
    form.class_group_id.choices = [
        (c.id, c.name)
        for c in ClassGroup.query.filter_by(user_id=current_user.id)
    ]
    form.subject_id.choices = [
        (s.id, s.name)
        for s in Subject.query.filter_by(user_id=current_user.id)
    ]
    form.teacher_id.choices = [(0, "No Specific Teacher")] + [
        (t.id, t.name)
        for t in Teacher.query.filter_by(user_id=current_user.id)
    ]
    form.room_id.choices = [(0, "Default Group Room")] + [
        (r.id, r.name)
        for r in Room.query.filter_by(user_id=current_user.id)
    ]
    form.period_id.choices = [
        (p.id, f"{p.name} ({p.start_time.strftime('%H:%M')}–{p.end_time.strftime('%H:%M')})")
        for p in Period.query.filter_by(user_id=current_user.id)
                        .order_by(Period.start_time)
    ]

    if form.validate_on_submit():
        entry = TimetableEntry(
            user_id=current_user.id,
            class_group_id = form.class_group_id.data,
            subject_id     = form.subject_id.data,
            teacher_id     = form.teacher_id.data or None,
            room_id        = form.room_id.data    or None,
            period_id      = form.period_id.data,
            weekday        = form.weekday.data,
            is_locked      = form.is_locked.data,
            notes          = form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(entry)
        db.session.commit()
        flash('Timetable entry added successfully!', 'success')
        return redirect(url_for('timetable_list'))

    return render_template('add_timetable_entry.html', form=form)


@app.route('/edit-timetable-entry/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def edit_timetable_entry(entry_id):
    entry = TimetableEntry.query.filter_by(
        id=entry_id, user_id=current_user.id
    ).first_or_404()
    form = TimetableEntryForm(obj=entry)

    # 1) populate dropdowns
    form.class_group_id.choices = [
        (c.id, c.name) for c in ClassGroup.query.filter_by(user_id=current_user.id)
    ]
    form.subject_id.choices = [
        (s.id, s.name) for s in Subject.query.filter_by(user_id=current_user.id)
    ]
    form.teacher_id.choices = [(0, "No Specific Teacher")] + [
        (t.id, t.name) for t in Teacher.query.filter_by(user_id=current_user.id)
    ]
    form.room_id.choices = [(0, "Default Group Room")] + [
        (r.id, r.name) for r in Room.query.filter_by(user_id=current_user.id)
    ]
    form.period_id.choices = [
        (p.id, f"{p.name} ({p.start_time.strftime('%H:%M')}–{p.end_time.strftime('%H:%M')})")
        for p in Period.query.filter_by(user_id=current_user.id)
                        .order_by(Period.start_time)
    ]

    if form.validate_on_submit():
        entry.class_group_id = form.class_group_id.data
        entry.subject_id     = form.subject_id.data
        entry.teacher_id     = form.teacher_id.data or None
        entry.room_id        = form.room_id.data    or None
        entry.period_id      = form.period_id.data
        entry.weekday        = form.weekday.data
        entry.is_locked      = form.is_locked.data
        entry.notes          = form.notes.data.strip() if form.notes.data else None

        db.session.commit()
        flash('Timetable entry updated successfully!', 'success')
        return redirect(url_for('timetable_list'))

    # 2) pre-fill existing values
    form.class_group_id.data = entry.class_group_id
    form.subject_id.data     = entry.subject_id
    form.teacher_id.data     = entry.teacher_id or 0
    form.room_id.data        = entry.room_id    or 0
    form.period_id.data      = entry.period_id
    form.weekday.data        = entry.weekday
    form.is_locked.data      = entry.is_locked
    form.notes.data          = entry.notes or ""

    return render_template('add_timetable_entry.html', form=form, editing=True)


@app.route('/delete-timetable-entry/<int:entry_id>', methods=['POST'])
@login_required
def delete_timetable_entry(entry_id):
    entry = TimetableEntry.query.filter_by(
        id=entry_id, user_id=current_user.id
    ).first_or_404()
    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Timetable entry deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting entry: {e}', 'danger')
    return redirect(url_for('timetable_list'))


@app.route('/generate-schedule', methods=['POST'])
@login_required
def generate_schedule_route():
    ok, sched = generate_schedule(current_user.id)
    if not ok:
        flash("Could not find a valid schedule. Try relaxing your constraints.", "danger")
        return redirect(url_for('dashboard'))

    # 1) clear out any old entries
    TimetableEntry.query.filter_by(user_id=current_user.id).delete()

    # 2) add new entries, mapping only valid columns
    for s in sched:
        entry = TimetableEntry(
            user_id=current_user.id,
            class_group_id = s['group_id'],
            subject_id     = s['subject_id'],
            teacher_id     = s.get('teacher_id'),
            room_id        = s.get('room_id'),
            period_id      = s['period_id'],
            weekday        = s['weekday'],
            notes          = None,
            is_locked      = False
        )
        db.session.add(entry)

    db.session.commit()
    flash("Schedule generated successfully!", "success")
    return redirect(url_for('dashboard'))


