from flask import Blueprint, render_template, abort, flash, url_for, redirect, request
from flask_login import login_required, current_user

from app import db
from models import UserRole, Enrollment, Student, Invoice
from datetime import date

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
