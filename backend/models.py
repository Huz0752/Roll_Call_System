from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash

# initialize the SQLAlchemy object
# this wiil be used to interact with the database
# and manage all model classes

db = SQLAlchemy()

# define the student model, which represents students in the system
class Student(db.Model, UserMixin):
    # primary key for the Student table
    id = db.Column(db.Integer, primary_key=True)
    # unique student identifier, cannot be null
    student_id = db.Column(db.String(9), unique=True, nullable=False)
    # password hash for storing the student's password securely
    password_hash = db.Column(db.String(128), nullable=False)

    # method to set the password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
   
   # method to chekc if the provided password matches the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # method to get a unique ID for the student (used by Flask-login)
    def get_id(self):
        return f'student-{self.id}'

# define the Teadcher model, which represents teachers in the system
class Teacher(db.Model, UserMixin):
    # primary key for the Teacher table
    id = db.Column(db.Integer, primary_key=True)
    # teacher's name, cannot be null and must be unique
    teacher_name = db.Column(db.String(50), unique=True, nullable=False)
    # password hash for strogin the teacher's password securely
    password_hash = db.Column(db.String(128), nullable=False)

    # method to set the password hash
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
   
   # method to check if the provided password matches the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # method to get a unique ID for the teacher (used by Flask-login)
    def get_id(self):
        return f'teacher-{self.id}'

# define the Course model, which represents courses taught by teachers
class Course(db.Model):
    # primary key for the Course table
    id = db.Column(db.Integer, primary_key=True)
    # name of the course, cannot be null
    course_name = db.Column(db.String(100), nullable=False)
    # foreign key linking the course to the teacher who teaches it
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    # relationship to access the teacher object associated with the course
    teacher = db.relationship('Teacher', backref=db.backref('courses', lazy=True))

# define the Attendance model, which represents attendance records for students in course
class Attendance(db.Model):
    # primary key for the attendance table
    id = db.Column(db.Integer, primary_key=True)
    # foreign key linking the attendance record to a student
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    # foreign key linking the attendance record to a course
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    # timestamp for when the attendance was recorded, defaults to the current time
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Taipei')))
    # IP address of the student at the time of attendance
    ip_address = db.Column(db.String(45))
    # relationship to access the Student object associated with the attendance record
    student = db.relationship('Student', backref=db.backref('attendances', lazy=True))
    # relationship to access the Course object associated with the attendance record
    course = db.relationship('Course', backref=db.backref('attendances', lazy=True))