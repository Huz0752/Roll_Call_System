import base64
import csv
import io
import os
import random
import socket
from datetime import datetime, timedelta

import pytz
import qrcode
from flask import (
    Flask, request, jsonify, send_from_directory, redirect, url_for, 
    make_response, render_template, session
)
from flask_cors import CORS
from flask_login import (
    LoginManager, login_user, login_required, logout_user, 
    UserMixin, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, Student, Teacher, Course, Attendance

# set up secret key and timezone
secret_key = os.urandom(24)
taipei_timezone = pytz.timezone('Asia/Taipei')

# initialize Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
db.init_app(app)
CORS(app)

# set up LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'student.login'
login_manager.login_view = 'teacher.login'

# create all database tables
with app.app_context():
    db.create_all()

# user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Load user by ID prefix(student or teacher)
    if user_id.startswith('student-'):
        user = Student.query.get(int(user_id.split('-')[1]))
        return user
    elif user_id.startswith('teacher-'):
        user = Teacher.query.get(int(user_id.split('-')[1]))
        return user
    return None

# define UserMixin class for additional properties
class UserMixin:
    # property to check if user is authenticated
    @property
    def is_authenticated(self):
        return True
    
    # property to check if user is active
    @property
    def is_active(self):
        return True

    # get unique ID for user
    def get_id(self):
        return str(self.id)

# extend Student and Teacher classes with UserMixin properties
Student.__bases__ += (UserMixin,)
Teacher.__bases__ += (UserMixin,)

# routes for student registration and login
@app.route('/student/register')
def student_register_page():
    # render the student registration and page
    return render_template('student_register.html')


@app.route('/student/login')
def student_login_page():
    # render the student login page
    return render_template('student_login.html')


@app.route('/student/dashboard')
@login_required
def student_dashboard_page():
    # ensure current user is a Student before rendering dashboard
    if not isinstance(current_user, Student):
        return redirect(url_for('student_login_page'))
    return render_template('student_dashboard.html')


# routes for teacher registration and login
@app.route('/teacher/register')
def teacher_register_page():
    # render the teacher registration page
    return render_template('teacher_register.html')


@app.route('/teacher/login')
def teacher_login_page():
    # render the teacher login page
    return render_template('teacher_login.html')


@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard_page():
    # ensure current user is a Teacher before rendering dashboard
    if not isinstance(current_user, Teacher):
        return redirect(url_for('teacher_login_page'))
    return render_template('teacher_dashboard.html')


# route for student registration
@app.route('/student/register', methods=['POST'])
def student_register():
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')

    # check if student ID is already registered
    if Student.query.filter_by(student_id=student_id).first():
        return jsonify({'message': '學生ID已被註冊'}), 400

    # create new student and store password hash
    student = Student(student_id=student_id)
    student.set_password(password)
    db.session.add(student)
    db.session.commit()
    return jsonify({'message': '註冊成功'})


# route for student login
@app.route('/student/login', endpoint='student.login', methods=['POST'])
def student_login():
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')

    # check if student exists and passwrod is correct
    student = Student.query.filter_by(student_id=student_id).first()
    if student and student.check_password(password):
        login_user(student)
        return jsonify({'message': '登入成功'})
    else:
        return jsonify({'message': '學生ID或密碼錯誤'}), 400


# route for teacher registration
@app.route('/teacher/register', methods=['POST'])
def teacher_register():
    data = request.get_json()
    teacher_name = data.get('teacher_name')
    password = data.get('password')

    # check if teacher name is already registered
    if Teacher.query.filter_by(teacher_name=teacher_name).first():
        return jsonify({'message': '教師名稱已被註冊'}), 400

    # create new teacher and store password hash
    teacher = Teacher(teacher_name=teacher_name)
    teacher.set_password(password)
    db.session.add(teacher)
    db.session.commit()
    return jsonify({'message': '註冊成功'})


# route for teacher login
@app.route('/teacher/login', endpoint='teacher.login', methods=['POST'])
def teacher_login():
    data = request.get_json()
    teacher_name = data.get('teacher_name')
    password = data.get('password')

    # check if teacher exists and apssword is correct
    teacher = Teacher.query.filter_by(teacher_name=teacher_name).first()
    if teacher and teacher.check_password(password):
        login_user(teacher)
        return jsonify({'message': '登入成功'})
    else:
        return jsonify({'message': '教師名稱或密碼錯誤'}), 400


# route for user logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    # log out the current user
    logout_user()
    return jsonify({'message': '登出成功'})


# store valid PIN codes for attendance
valid_pins = {}


# route for student submitting PIN code for attendance
@app.route('/student/submit_pin', methods=['POST'])
@login_required
def submit_pin():
    if not isinstance(current_user, Student):
        return jsonify({'message': '未經授權'}), 401

    data = request.get_json()
    pin_code = data.get('pin_code')
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)

    # check if PIN code ia valid and not expired
    if pin_code in valid_pins:
        pin_info = valid_pins[pin_code]
        if datetime.now(taipei_timezone) < pin_info['expires_at']:
            # check if student has already attended
            existing_attendance = Attendance.query.filter_by(
                student_id=current_user.id,
                course_id=pin_info['course_id'], 
            ).first()
            if existing_attendance:
                return jsonify({'message': '您已經簽到過了'}), 400

            # record attendance
            attendance = Attendance(
                student_id=current_user.id,
                course_id=pin_info['course_id'],
                ip_address=ip_address, 
            )
            db.session.add(attendance)
            db.session.commit()
            return jsonify({'message': '點名成功'})
        else:
            return jsonify({'message': 'PIN碼已過期'}), 400
    else:
        return jsonify({'message': '無效的PIN碼'}), 400


# route for teacher publishing a new PIN code for attendance
@app.route('/teacher/publish_pin', methods=['POST'])
@login_required
def publish_pin():
    if not isinstance(current_user, Teacher):
        return jsonify({'message': '未經授權'}), 401

    data = request.get_json()
    course_name = data.get('course_name')
    duration = data.get('duration', 5)  

    # check if course exists or create a new one
    course = Course.query.filter_by(
        course_name=course_name,
        teacher_id=current_user.id
    ).first()
    if not course:
        course = Course(course_name=course_name, teacher_id=current_user.id)
        db.session.add(course)
        db.session.commit()

    # generate a unique PIN code
    while True:
        pin_code = str(random.randint(100000, 999999))
        if pin_code not in valid_pins:
            break

    # set expiration time for the PIN code
    expires_at = datetime.now(taipei_timezone) + timedelta(minutes=(int(duration)))
    valid_pins[pin_code] = {'course_id': course.id, 'expires_at': expires_at}

    # generate QR code with attendance URL
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    
    post = '8081'
    qr_data = f'http://{host}:{post}/student/auto_submit?pin_code={pin_code}'
    qr = qrcode.QRCode()
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image()
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return jsonify({'pin_code': pin_code, 'qr_code': image_base64, 'expires_at':expires_at.timestamp()})


# route for auto submittin PIN code for attendance
@app.route('/student/auto_submit', methods=['GET'])
def auto_submit():
    pin_code = request.args.get('pin_code')
    session['pin_code'] = pin_code 

    # redirect based on authentication status
    if current_user.is_authenticated and isinstance(current_user, Student):
        return redirect(url_for('student_dashboard_page'))
    else:
        return redirect(url_for('student_login_page'))


# route for get the current PIN code from session
@app.route('/get_pin_code', methods=['GET'])
def get_pin_code():
    pin_code = session.get('pin_code')
    return jsonify({'pin_code': pin_code})


# route to clear the PIN code from session
@app.route('/clear_pin_code', methods=['POST'])
def clear_pin_code():
    session.pop('pin_code', None)
    return jsonify({'message': 'PIN code cleared'})


# route for teacher to upload course roster
@app.route('/teacher/upload_roster', methods=['POST'])
@login_required
def upload_roster():
    if not isinstance(current_user, Teacher):
        return jsonify({'message': '未經授權'}), 401

    file = request.files['file']
    course_name = request.form.get('course_name')

    # check if course exists
    course = Course.query.filter_by(
        course_name=course_name,
        teacher_id=current_user.id
    ).first()
    if not course:
        return jsonify({'message': '課程未找到'}), 400

    # parse uploaded file for student IDs
    filename = file.filename
    if filename.endswith('.csv'):
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        roster_student_ids = [row[0] for row in csv_input]
    elif filename.endswith('.txt'):
        content = file.stream.read().decode('utf-8')
        roster_student_ids = content.strip().splitlines()
    else:
        return jsonify({'message': '僅支持 CSV 或 TXT 文件'}), 400

    # get list of students who attended and calculate absentees
    attendances = Attendance.query.filter_by(course_id=course.id).all()
    attended_student_ids = [attendance.student.student_id for attendance in attendances]

    absent_student_ids = set(roster_student_ids) - set(attended_student_ids)
    return jsonify({'absent_students': list(absent_student_ids)})


# route for teacher to export attendance records
@app.route('/teacher/export_attendance', methods=['GET'])
@login_required
def export_attendance():
    if not isinstance(current_user, Teacher):
        return jsonify({'message': '未經授權'}), 401

    course_name = request.args.get('course_name')

    # check if course exists
    course = Course.query.filter_by(
        course_name=course_name,
        teacher_id=current_user.id
    ).first()
    if not course:
        return jsonify({'message': '課程未找到'}), 400

    # get all attendance records for the course
    attendances = Attendance.query.filter_by(course_id=course.id).all()

    # create CSV output of attendance records
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Student ID', 'Timestamp', 'IP Address'])
    for attendance in attendances:
        cw.writerow([
            attendance.student.student_id,
            attendance.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            attendance.ip_address
        ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={course_name}_attendance.csv"
    output.headers["Content-type"] = "text/csv"

    Attendance.query.filter_by(course_id=course.id).delete()
    db.session.delete(course)
    db.session.commit()
    return output


# route to check user login status
@app.route('/check_login', methods=['GET'])
def check_login():
    if current_user.is_authenticated:
        # determine user type based on current user
        if isinstance(current_user, Student):
            user_type = 'student'
        elif isinstance(current_user, Teacher):
            user_type = 'teacher'
        else:
            user_type = 'unknown'
        return jsonify({'logged_in': True, 'user_type': user_type})
    else:
        return jsonify({'logged_in': False})


# route for rendering index page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # run the Flask application
    app.run(host='0.0.0.0', port=8081, debug=True)