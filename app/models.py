from app import db
from flask_login import UserMixin

class_group_teacher = db.Table(
    'class_group_teacher',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('class_group_id', db.Integer, db.ForeignKey('class_group.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    week_hours = db.Column(db.Integer, nullable=False)
    preferred_days = db.Column(db.Text, nullable=True)
    preferred_periods = db.Column(db.Text, nullable=True)

    user = db.relationship('User', backref=db.backref('teachers', lazy=True))

class ClassGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    default_room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    allowed_periods = db.Column(db.Text, nullable=True)
    user = db.relationship('User', backref='class_groups')
    default_room = db.relationship('Room', backref='default_class_groups')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    default_hours_per_week = db.Column(db.Integer, nullable=False)
    default_room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)

    user = db.relationship('User', backref=db.backref('subjects', lazy=True))
    default_room = db.relationship('Room', backref=db.backref('default_subjects', lazy=True))

class ScheduleAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    hours_per_week = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)

    class_group = db.relationship('ClassGroup', backref=db.backref('schedule_assignments', lazy=True))
    teacher = db.relationship('Teacher', backref=db.backref('schedule_assignments', lazy=True))
    user = db.relationship('User', backref=db.backref('schedule_assignments', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('schedule_assignments', lazy=True))
    room = db.relationship('Room', backref=db.backref('subject_assignments', lazy=True))

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)

    user = db.relationship('User', backref=db.backref('rooms', lazy=True))

class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    user = db.relationship('User', backref=db.backref('periods', lazy=True))

class TimetableEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=True)
    period_id = db.Column(db.Integer, db.ForeignKey('period.id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 1-5 (Mon-Fri)
    is_locked = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)

    class_group = db.relationship('ClassGroup', backref=db.backref('timetable_entries', lazy=True))
    subject = db.relationship('Subject', backref=db.backref('timetable_entries', lazy=True))
    teacher = db.relationship('Teacher', backref=db.backref('timetable_entries', lazy=True))
    room = db.relationship('Room', backref=db.backref('timetable_entries', lazy=True))
    period = db.relationship('Period', backref=db.backref('timetable_entries', lazy=True))
    user = db.relationship('User', backref=db.backref('timetable_entries', lazy=True))

