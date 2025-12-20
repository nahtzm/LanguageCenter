from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from models import Student, Staff, UserRole

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    role = request.form.get('role')
    email = request.form.get('email')
    password = request.form.get('password')

    user = None

    # ====== LOGIN STAFF ======
    if role == 'staff':
        user = Staff.query.filter_by(email=email).first()

        if user and user.password == password:
            login_user(user)

            if user.role == UserRole.ADMIN:
                return redirect('/admin')
            elif user.role == UserRole.CASHIER:
                return redirect(url_for('cashier.dashboard'))
            elif user.role == UserRole.TEACHER:
                return redirect(url_for('teacher.dashboard'))

    # ====== LOGIN STUDENT ======
    else:
        user = Student.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('student.dashboard'))

    # ====== LOGIN FAIL ======
    flash("Sai email hoặc mật khẩu", "error")
    return redirect(url_for('auth.login'))



@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    # ====== POST ======
    email = request.form.get('email')
    password = request.form.get('password')
    fullname = request.form.get('fullname')
    phone = request.form.get('phone')

    # 1. Check email tồn tại
    if Student.query.filter_by(email=email).first():
        flash('Email already registered', 'error')
        return render_template("register.html")

    # 2. Sinh mã học viên (HV)
    last_student = (
        Student.query
        .filter(Student.code.isnot(None))
        .order_by(Student.id.desc())
        .first()
    )

    if last_student:
        number = int(last_student.code.replace("HV", ""))
        code = f"HV{number + 1}"
    else:
        code = "HV1"

    # 3. Tạo học viên mới
    new_student = Student(
        email=email,
        password=generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        ),
        fullname=fullname,
        phone=phone,
        code=code
    )

    db.session.add(new_student)
    db.session.commit()

    # 4. Đăng nhập sau đăng ký
    login_user(new_student)
    flash('Student registered successfully', 'success')

    return redirect(url_for('student.dashboard'))


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.welcome'))

