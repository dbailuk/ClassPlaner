from app import db
from flask_login import UserMixin

# Association table for Teacher-Subject many-to-many
teacher_subject = db.Table('teacher_subject',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

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
    availability = db.Column(db.Text)
    subjects = db.relationship('Subject', secondary=teacher_subject, backref='teachers')
    user = db.relationship('User', backref='teachers')

class ClassGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    default_room_id = db.Column(db.Integer, db.ForeignKey('room.id'))

    user = db.relationship('User', backref='class_groups')
    default_room = db.relationship('Room', backref='default_class_groups')
    subjects = db.relationship('ClassGroupSubject', backref='parent_class_group', cascade="all, delete-orphan")

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    default_hours_per_week = db.Column(db.Integer, nullable=False)
    default_room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    user = db.relationship('User', backref='subjects')
    default_room = db.relationship('Room', backref='default_subjects')

class ClassGroupSubject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    hours_per_week = db.Column(db.Integer, nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))  # Optional room override
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)

    class_group = db.relationship('ClassGroup', backref='class_group_subjects')
    teacher = db.relationship('Teacher', backref='class_group_subjects')
    user = db.relationship('User', backref='class_group_subjects')
    subject = db.relationship('Subject', backref='class_group_subjects')
    room = db.relationship('Room', backref='subject_assignments')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50))
    capacity = db.Column(db.Integer)
    user = db.relationship('User', backref='rooms')

class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    user = db.relationship('User', backref='periods')

class TimetableEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_group_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    period_id = db.Column(db.Integer, db.ForeignKey('period.id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 1-5 (Mon-Fri)
    is_locked = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    class_group = db.relationship('ClassGroup', backref='timetable_entries')
    subject = db.relationship('Subject', backref='timetable_entries')
    teacher = db.relationship('Teacher', backref='timetable_entries')
    room = db.relationship('Room', backref='timetable_entries')
    period = db.relationship('Period', backref='timetable_entries')
    user = db.relationship('User', backref='timetable_entries')