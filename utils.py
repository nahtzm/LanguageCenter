from flask_mail import Message

from app import db
from app import mail
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


from models import Attendance, ScoreConfig


def calculate_attendance_score(enrollment_id):
    attended = Attendance.query.filter_by(
        enrollment_id=enrollment_id,
        is_present=True
    ).count()

    score = attended * 2
    print(score)
    return min(score, 10)


def calculate_average_and_result(enrollment, score_configs):
    total = 0
    weight_sum = 0

    for config in score_configs:
        if config.auto_calculated:
            value = calculate_attendance_score(enrollment.id)
        else:
            score = enrollment.scores.filter_by(
                score_config_id=config.id
            ).first()
            value = score.score_value if score else 0

        total += value * config.weight
        weight_sum += config.weight

    if weight_sum == 0:
        return None, None

    avg = round(total / weight_sum, 2)
    result = "Đạt" if avg >= 5 else "Rớt"
    return avg, result


def calculate_average(enrollment):
    total = 0
    total_weight = 0

    configs = ScoreConfig.query.filter_by(is_active=True).all()

    for config in configs:
        if config.auto_calculated:
            value = calculate_attendance_score(enrollment.id) or 0
        else:
            score = enrollment.scores.filter_by(
                score_config_id=config.id
            ).first()
            value = score.score_value if score else 0

        total += value * config.weight
        total_weight += config.weight

    if total_weight == 0:
        return 0

    return round(total / total_weight, 2)

