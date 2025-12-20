from collections import defaultdict

from flask import Blueprint, render_template, abort, flash, url_for, redirect, request
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from models import UserRole, Enrollment, Student, Invoice, Course, Class
from datetime import date

from utils import calculate_average

cashier_routes = Blueprint('cashier', __name__)


@cashier_routes.route('/dashboard')
def dashboard():
    return render_template("dashboard/cashier/cashier.html", UserRole=UserRole)


@cashier_routes.route('/enrollments')
@login_required
def pending_enrollments():
    if current_user.role != UserRole.CASHIER:
        abort(403)

    enrollments = (
        Enrollment.query
        .filter_by(status='pending')
        .join(Student)
        .order_by(Student.fullname)
        .all()
    )

    return render_template(
        'dashboard/cashier/pending_enrollments.html',
        enrollments=enrollments,
        UserRole=UserRole,
        current_user=current_user
    )


@cashier_routes.route('/create_invoice/<int:enrollment_id>', methods=['GET', 'POST'])
@login_required
def create_invoice(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    if enrollment.status != 'pending':
        flash('Enrollment không hợp lệ', 'error')
        return redirect(url_for('cashier.pending_enrollments'))

    if request.method == 'POST':
        payment_status = request.form.get('payment_status')

        invoice = Invoice(
            enrollment_id=enrollment.id,
            amount=enrollment.class_ref.level.tuition_fee,
            payment_date=date.today(),
            status=payment_status
        )

        db.session.add(invoice)

        if payment_status == 'paid':
            enrollment.status = 'confirmed'

        db.session.commit()

        flash('Tạo hóa đơn thành công', 'success')
        return redirect(url_for('cashier.pending_enrollments'))

    return render_template(
        'dashboard/cashier/create_invoice.html',
        enrollment=enrollment,
        date = date.today(),
        UserRole=UserRole,
    )


@cashier_routes.route('/invoices')
@login_required
def invoice_list():
    if current_user.role != UserRole.CASHIER:
        abort(403)

    invoices = (
        Invoice.query
        .join(Enrollment)
        .join(Student)
        .order_by(Invoice.issue_date.desc())
        .all()
    )

    return render_template(
        'dashboard/cashier/invoice_list.html',
        invoices=invoices,
        current_user=current_user,
        UserRole=UserRole
    )

@cashier_routes.route('/reports')
@login_required
def reports():
    # ========= 1. SỐ HỌC VIÊN THEO KHÓA =========
    students_by_course = (
        db.session.query(
            Course.name.label('course'),
            func.count(Enrollment.id).label('count')
        )
        .join(Class, Class.course_id == Course.id)
        .join(Enrollment, Enrollment.class_id == Class.id)
        .filter(Enrollment.status == 'confirmed')
        .group_by(Course.name)
        .all()
    )

    # ========= 2. TỶ LỆ ĐẠT THEO KHÓA =========
    pass_stats = defaultdict(lambda: {"total": 0, "pass": 0})

    enrollments = Enrollment.query.filter_by(status='confirmed').all()
    for e in enrollments:
        avg = calculate_average(e)
        course_name = e.class_ref.course.name

        pass_stats[course_name]["total"] += 1
        if avg >= 5:
            pass_stats[course_name]["pass"] += 1

    pass_rate_by_course = []
    for course, v in pass_stats.items():
        rate = round(v["pass"] / v["total"] * 100, 2) if v["total"] else 0
        pass_rate_by_course.append({
            "course": course,
            "rate": rate
        })

    # ========= 3. DOANH THU THEO THÁNG =========
    revenue_raw = (
        db.session.query(
            func.date_format(Invoice.payment_date, "%Y-%m").label("month"),
            func.sum(Invoice.amount).label("total")
        )
        .filter(Invoice.status == 'paid')
        .group_by(func.date_format(Invoice.payment_date, "%Y-%m"))
        .order_by("month")
        .all()
    )
    revenue_db = {
        r.month: float(r.total)
        for r in revenue_raw
    }
    sample_months = [
        {"month": "2025-08", "total": 18000000},
        {"month": "2025-09", "total": 25000000},
        {"month": "2025-10", "total": 32000000},
        {"month": "2025-11", "total": 41000000},
        {"month": "2025-12", "total": 50000000},
    ]

    revenue_by_month = []

    for item in sample_months:
        month = item["month"]
        total = revenue_db.get(month, item["total"])
        revenue_by_month.append({
            "month": month,
            "total": total
        })

    revenue_labels = [r["month"] for r in revenue_by_month]
    revenue_values = [float(r["total"]) for r in revenue_by_month]

    return render_template(
        'dashboard/cashier/reports.html',
        students_by_course=students_by_course,
        pass_rate_by_course=pass_rate_by_course,
        revenue_labels=revenue_labels,
        revenue_values=revenue_values,
        UserRole=UserRole,
    )