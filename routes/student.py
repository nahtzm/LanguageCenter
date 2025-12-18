from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user

from app import db
from logic import enroll_class
from models import Course, Class, Level, Enrollment, Invoice

student_routes = Blueprint('student', __name__)

@student_routes.route('/dashboard')
def dashboard():
    return render_template("dashboard/student/student.html")

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
            status="enrolled"
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


# def enroll_class(student_id, class_id):
#     cls = Class.query.get_or_404(class_id)
#
#     # 1. Check còn chỗ
#     if cls.current_students >= cls.max_students:
#         raise ValueError("Lớp đã đủ học viên")
#
#     # 2. Check đã đăng ký chưa
#     exists = Enrollment.query.filter_by(
#         student_id=student_id,
#         class_id=class_id
#     ).first()
#
#     if exists:
#         raise ValueError("Bạn đã đăng ký lớp này")
#
#     # 3. Tạo enrollment
#     enrollment = Enrollment(
#         student_id=student_id,
#         class_id=class_id,
#         status="enrolled"
#     )
#     db.session.add(enrollment)
#
#     # 4. Tăng sĩ số
#     cls.current_students += 1
#
#     # 5. Tạo hóa đơn
#     # invoice = Invoice(
#     #     enrollment_id=enrollment.id,
#     #     amount=cls.level.tuition_fee,
#     #     status="unpaid"
#     # )
#     # db.session.add(invoice)
#     db.session.commit()
@student_routes.route("/enroll/<int:class_id>", methods=["POST"])
def enroll(class_id):
    enroll_class(current_user.id, class_id)
    flash("Đăng ký thành công", "success")
    return redirect(url_for("student.class_list"))
