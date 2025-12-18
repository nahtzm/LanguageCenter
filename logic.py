from app import db
from models import Class, Enrollment


def enroll_class(student_id, class_id):
    cls = Class.query.get_or_404(class_id)

    # 1. Check còn chỗ
    if cls.current_students >= cls.max_students:
        raise ValueError("Lớp đã đủ học viên")

    # 2. Check đã đăng ký chưa
    exists = Enrollment.query.filter_by(
        student_id=student_id,
        class_id=class_id
    ).first()

    if exists:
        raise ValueError("Bạn đã đăng ký lớp này")

    # 3. Tạo enrollment
    enrollment = Enrollment(
        student_id=student_id,
        class_id=class_id,
        status="enrolled"
    )
    db.session.add(enrollment)

    # 4. Tăng sĩ số
    cls.current_students += 1

    # 5. Tạo hóa đơn
    # invoice = Invoice(
    #     enrollment_id=enrollment.id,
    #     amount=cls.level.tuition_fee,
    #     status="unpaid"
    # )
    # db.session.add(invoice)
    db.session.commit()