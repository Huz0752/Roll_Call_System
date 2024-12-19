# test_attendance.py
import pytest
from datetime import datetime, timedelta
from Roll_Call_System.app import app, db, Student, Teacher, Course, Attendance, valid_pins
from flask_login import login_user
import pytz

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # 建立測試用教師、學生與課程
            teacher = Teacher(teacher_name='t1')
            teacher.set_password('pass')
            db.session.add(teacher)
            db.session.commit()

            course = Course(course_name='TestCourse', teacher_id=teacher.id)
            db.session.add(course)
            db.session.commit()

            student = Student(student_id='s1')
            student.set_password('pass')
            db.session.add(student)
            db.session.commit()

            # 建立一個有效的 PIN 碼
            pin_code = '123456'
            expires_at = datetime.now(pytz.timezone('Asia/Taipei')) + timedelta(minutes=5)
            valid_pins[pin_code] = {'course_id': course.id, 'expires_at': expires_at}

        yield client
        with app.app_context():
            db.drop_all()
            valid_pins.clear()

def login_student(client):
    client.post('/student/login', json={'student_id': 's1', 'password': 'pass'})

def test_submit_valid_pin(client):
    # 學生登入
    login_student(client)
    # 提交有效的PIN碼
    response = client.post('/student/submit_pin', json={'pin_code': '123456'})
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == '點名成功'
    with app.app_context():
        attendance_record = Attendance.query.first()
        assert attendance_record is not None

def test_submit_same_pin_twice(client):
    # 學生登入並第一次提交PIN碼
    login_student(client)
    client.post('/student/submit_pin', json={'pin_code': '123456'})
    # 第二次提交同一PIN碼
    response = client.post('/student/submit_pin', json={'pin_code': '123456'})
    data = response.get_json()
    assert response.status_code == 400
    assert data['message'] == '您已經簽到過了'

def test_submit_invalid_pin(client):
    # 學生登入
    login_student(client)
    response = client.post('/student/submit_pin', json={'pin_code': '999999'})
    data = response.get_json()
    assert response.status_code == 400
    assert data['message'] == '無效的PIN碼'
