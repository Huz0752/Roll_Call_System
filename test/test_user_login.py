# test_user_login.py
import pytest
from Roll_Call_System.app import app, db, Student, Teacher
from werkzeug.security import generate_password_hash

@pytest.fixture
def client():
    # 使用測試配置
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # 記憶體中建立測試用DB
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # 建立測試用帳號 (學生)
            student = Student(student_id='s123456789')
            student.set_password('password')
            db.session.add(student)
            # 建立測試用帳號 (教師)
            teacher = Teacher(teacher_name='t123456789')
            teacher.set_password('password')
            db.session.add(teacher)
            db.session.commit()
        yield client
        # 測試結束後清理資料庫
        with app.app_context():
            db.drop_all()

def test_student_login_success(client):
    # 測試學生成功登入
    response = client.post('/student/login', json={
        'student_id': 's123456789',
        'password': 'password'
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == '登入成功'

def test_student_login_failure(client):
    # 測試學生登入失敗(密碼錯誤)
    response = client.post('/student/login', json={
        'student_id': 's123456789',
        'password': 'wrong_password'
    })
    data = response.get_json()
    assert response.status_code == 400
    assert data['message'] == '學生ID或密碼錯誤'

def test_teacher_login_success(client):
    # 測試教師成功登入
    response = client.post('/teacher/login', json={
        'teacher_name': 't123456789',
        'password': 'password'
    })
    data = response.get_json()
    assert response.status_code == 200
    assert data['message'] == '登入成功'

def test_teacher_login_failure(client):
    # 測試教師登入失敗(密碼錯誤)
    response = client.post('/teacher/login', json={
        'teacher_name': 'teacher1',
        'password': 'wrong_password'
    })
    data = response.get_json()
    assert response.status_code == 400
    assert data['message'] == '教師名稱或密碼錯誤'
