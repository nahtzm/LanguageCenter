from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user

from app import db
from logic import get_enrolled_classes, send_enroll_success_email
from models import Course, Class, Level, Enrollment, Invoice, Student

student_routes = Blueprint('student', __name__)

@student_routes.route('/dashboard')
def dashboard():
    classes = get_enrolled_classes(current_user.id)
    return render_template("dashboard/student/student.html", classes=classes)

@student_routes.route('/class_list')
def class_list():
    course_id = request.args.get("course_id")
    level_id = request.args.get("level_id")

    query = Class.query

    if course_id:
        query = query.filter_by(course_id=course_id)
    if level_id:
        query = query.filter_by(level_id=level_id)

    enrolled_class_ids = {
        e.class_id
        for e in Enrollment.query.filter_by(
            student_id=current_user.id,
        ).all()
    }

    classes = query.all()

    return render_template(
        "dashboard/student/class_list.html",
        enrolled_class_ids=enrolled_class_ids,
        courses=classes,
        course_list=Course.query.all(),
        level_list=Level.query.all()
    )


@student_routes.route("/enroll/<int:class_id>", methods=["POST"])
def enroll(class_id):
    cls = Class.query.get_or_404(class_id)
    student = Student.query.get_or_404(current_user.id)

    if cls.current_students >= cls.max_students:
        raise ValueError("Lớp đã đủ học viên")

    exists = Enrollment.query.filter_by(
        student_id=current_user.id,
        class_id=class_id
    ).first()

    if exists:
        raise ValueError("Bạn đã đăng ký lớp này")

    enrollment = Enrollment(
        student_id=current_user.id,
        class_id=class_id,
    )
    db.session.add(enrollment)

    cls.current_students += 1

    # 5. Tạo hóa đơn
    # invoice = Invoice(
    #     enrollment_id=enrollment.id,
    #     amount=cls.level.tuition_fee,
    #     status="unpaid"
    # )
    # db.session.add(invoice)
    db.session.commit()
    # send_enroll_success_email(student, cls)
    flash("Đăng ký thành công. Bạn sẽ nhận được email xác nhận", "success")
    return redirect(url_for("student.class_list"))
