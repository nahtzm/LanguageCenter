from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required

from app import db
from utils import get_enrolled_classes
from models import Course, Class, Level, Enrollment, Invoice, Student, UserRole

student_routes = Blueprint('student', __name__)


@student_routes.route('/dashboard')
@login_required
def dashboard():
    classes = get_enrolled_classes(current_user.id)
    return render_template(
        "dashboard/student/student.html",
        classes=classes,
        UserRole=UserRole,
        current_user=current_user
    )

@student_routes.route('/class_list')
@login_required
def class_list():
    course_id = request.args.get("course_id", type=int)
    level_id = request.args.get("level_id", type=int)

    query = Class.query

    if course_id:
        query = query.filter_by(course_id=course_id)
    if level_id:
        query = query.filter_by(level_id=level_id)

    classes = query.all()

    enrolled_class_ids = {
        e.class_id
        for e in Enrollment.query.filter_by(
            student_id=current_user.id
        ).all()
    }

    return render_template(
        "dashboard/student/class_list.html",
        classes=classes,
        enrolled_class_ids=enrolled_class_ids,
        courses=Course.query.all(),
        levels=Level.query.all(),
        UserRole=UserRole
    )


@student_routes.route("/enroll/<int:class_id>", methods=["POST"])
@login_required
def enroll(class_id):
    cls = Class.query.get_or_404(class_id)
    student = Student.query.get_or_404(current_user.id)

    # 1. Check sĩ số
    if cls.current_students >= cls.max_students:
        flash("Lớp đã đủ học viên", "error")
        return redirect(url_for("student.class_list"))

    # 2. Check đã đăng ký chưa
    exists = Enrollment.query.filter_by(
        student_id=student.id,
        class_id=cls.id
    ).first()

    if exists:
        flash("Bạn đã đăng ký lớp này", "warning")
        return redirect(url_for("student.class_list"))

    try:
        # 3. Tạo enrollment
        enrollment = Enrollment(
            student_id=student.id,
            class_id=cls.id
        )
        db.session.add(enrollment)

        # 4. Cập nhật sĩ số
        cls.current_students += 1

        # 5. Tạo hóa đơn
        invoice = Invoice(
            enrollment=enrollment,
            amount=cls.level.tuition_fee
        )
        db.session.add(invoice)

        db.session.commit()

        flash(
            "Đăng ký thành công. Bạn sẽ nhận được email xác nhận",
            "success"
        )

    except Exception as e:
        db.session.rollback()
        flash("Có lỗi xảy ra khi đăng ký lớp", "error")

    return redirect(url_for("student.class_list"))
