# test_report_generation.py
import pytest
import io
from Roll_Call_System.app import app, db, Teacher, Course, Student, Attendance
from datetime import datetime
import pytz

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # 建立教師與課程
            teacher = Teacher(teacher_name='t_report')
            teacher.set_password('pass')
            db.session.add(teacher)
            db.session.commit()

            course = Course(course_name='ReportCourse', teacher_id=teacher.id)
            db.session.add(course)
            db.session.commit()

            # 建立學生及出席紀錄
            student1 = Student(student_id='s2')
            student1.set_password('pass')
            db.session.add(student1)

            student2 = Student(student_id='s3')
            student2.set_password('pass')
            db.session.add(student2)
            db.session.commit()

            attendance = Attendance(
                student_id=student1.id, 
                course_id=course.id, 
                timestamp=datetime.now(pytz.timezone('Asia/Taipei')),
                ip_address='127.0.0.1'
            )
            db.session.add(attendance)
            db.session.commit()

        yield client
        with app.app_context():
            db.drop_all()

def login_teacher(client):
    client.post('/teacher/login', json={'teacher_name': 't_report', 'password': 'pass'})

def test_export_attendance(client):
    # 教師登入
    login_teacher(client)
    response = client.get('/teacher/export_attendance?course_name=ReportCourse')
    assert response.status_code == 200
    # 驗證回應標頭是否為CSV檔案
    assert 'text/csv' in response.headers.get('Content-type')
    # 驗證產生的CSV內容是否包含學生id
    csv_data = response.data.decode('utf-8')
    assert 's2' in csv_data
