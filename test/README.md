# 測試說明

```
需先把app.py line 22:
'from models import db, Student, Teacher, Course, Attendance'
改成
'from .models import db, Student, Teacher, Course, Attendance'
```

測試執行:
'pytest test/test_user_login.py'
'pytest test/test_attendance.py'
'pytest test/test_report_generation.py'