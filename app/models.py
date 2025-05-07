from app import db
from flask_login import UserMixin

# Association table (many-to-many) for Teacher Subject
teacher_subject = db.Table('teacher_subject',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subject.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), nullable=False)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.Text)  # Custom format or JSON string
    week_hours = db.Column(db.Integer, nullable=False)
    subjects = db.relationship('Subject', secondary=teacher_subject, backref='teachers')
    timetable_entries = db.relationship('TimetableEntry', backref='teacher', lazy=True)
    user = db.relationship('User', backref='teachers')

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hours_per_week = db.Column(db.Integer, nullable=False)
    timetable_entries = db.relationship('TimetableEntry', backref='subject', lazy=True)
    user = db.relationship('User', backref='subjects')

class ClassGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    timetable_entries = db.relationship('TimetableEntry', backref='class_group', lazy=True)
    user = db.relationship('User', backref='class_groups')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50))
    capacity = db.Column(db.Integer)
    timetable_entries = db.relationship('TimetableEntry', backref='room', lazy=True)
    user = db.relationship('User', backref='rooms')

class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    timetable_entries = db.relationship('TimetableEntry', backref='period', lazy=True)
    user = db.relationship('User', backref='periods')

class TimetableEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class_group.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    period_id = db.Column(db.Integer, db.ForeignKey('period.id'), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    is_manual = db.Column(db.Boolean, default=False)
    user = db.relationship('User', backref='timetable_entries')
	
