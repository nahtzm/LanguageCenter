from app import db
from datetime import datetime, UTC
from flask_login import UserMixin
from sqlalchemy.dialects.mysql import DECIMAL


class Student(db.Model, UserMixin):
    __tablename__ = 'student'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    enrollments = db.relationship('Enrollment', backref='student', lazy=True)

    # def get_id(self):
    #     return str(self.id)  # cần cho Flask-Login


class Staff(db.Model, UserMixin):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'teacher', 'cashier', 'admin'

    taught_classes = db.relationship('Class', backref='teacher', lazy=True)
    issued_invoices = db.relationship('Invoice', backref='cashier', lazy=True)

    # def get_id(self):
    #     return str(self.id)


class Level(db.Model):
    __tablename__ = 'level'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Beginner, Intermediate, Advanced
    tuition_fee = db.Column(DECIMAL(12, 2), nullable=False)  # học phí

    classes = db.relationship('Class', backref='level', lazy=True)


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    classes = db.relationship('Class', backref='course', lazy=True)


class Class(db.Model):
    __tablename__ = 'class_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # ví dụ: IELTS-B01
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    max_students = db.Column(db.Integer, nullable=False, default=25)
    current_students = db.Column(db.Integer, default=0)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    level_id = db.Column(db.Integer, db.ForeignKey('level.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('staff.id'))  # nullable

    enrollments = db.relationship('Enrollment', backref='class_ref', lazy=True, cascade="all, delete-orphan")


class Enrollment(db.Model):
    __tablename__ = 'enrollment'

    id = db.Column(db.Integer, primary_key=True)
    enroll_date = db.Column(db.DateTime, default=datetime.now(UTC))
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('class_table.id'), nullable=False)

    invoice = db.relationship('Invoice', backref='enrollment', uselist=False, lazy=True)
    scores = db.relationship('Score', backref='enrollment', lazy=True, cascade="all, delete-orphan")
    attendances = db.relationship('Attendance', backref='enrollment', lazy=True, cascade="all, delete-orphan")


class ScoreConfig(db.Model):
    __tablename__ = 'score_config'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    auto_calculated = db.Column(db.Boolean, default=False)

    scores = db.relationship('Score', backref='config', lazy=True)


class Score(db.Model):
    __tablename__ = 'score'

    id = db.Column(db.Integer, primary_key=True)
    score_value = db.Column(db.Float, nullable=False)

    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'), nullable=False)
    score_config_id = db.Column(db.Integer, db.ForeignKey('score_config.id'), nullable=False)


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    session_date = db.Column(db.Date, nullable=False)
    is_present = db.Column(db.Boolean, default=False)

    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'), nullable=False)


class Invoice(db.Model):
    __tablename__ = 'invoice'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(DECIMAL(12, 2), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.now(UTC))
    payment_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending')

    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'), nullable=False)
    cashier_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
