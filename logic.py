from app import db
from models import Class, Enrollment


def get_enrolled_classes(student_id):
    return (
        db.session.query(Class)
        .join(Enrollment)
        .filter(
            Enrollment.student_id == student_id,
        )
        .all()
    )


from flask_mail import Message
from app import mail


def send_enroll_success_email(student, cls):
    msg = Message(
        subject="Xác nhận đăng ký khóa học thành công",
        recipients=[student.email]
    )

    msg.body = f"""
Xin chào {student.fullname},

Bạn đã đăng ký thành công khóa học:

- Khóa học: {cls.course.name}
- Cấp độ: {cls.level.name}
- Thời gian: {cls.start_date} → {cls.end_date}
- Học phí: {cls.level.tuition_fee:,} VNĐ

Vui lòng thanh toán học phí đúng hạn.

Trân trọng,
Language Center
"""

    mail.send(msg)
