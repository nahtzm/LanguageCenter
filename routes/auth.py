from flask import Blueprint, render_template, redirect, url_for, request, flash, session
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
    if role == 'staff':
        user = Staff.query.filter_by(email=email).first()
        if user and user.password == password:
            login_user(user)
            if user.role == UserRole.ADMIN:
                return redirect(url_for('public.welcome'))
            elif user.role == UserRole.CASHIER:
                return redirect(url_for('public.welcome'))
            else:
                return redirect(url_for('teacher.dashboard'))
    else:
        user = Student.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('student.dashboard'))

    flash("Sai email hoặc mật khẩu")
    return redirect(url_for('login'))




@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    email = request.form.get('email')
    password = request.form.get('password')
    fullname = request.form.get('fullname')
    phone = request.form.get('phone')

    student = Student.query.filter_by(email=email).first()
    if student:
        flash('Email already registered', category='error')
        return render_template("register.html")

    new_student = Student(email=email,
                          password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8),
                          fullname=fullname, phone=phone)
    flash('Student registered', category='success')
    db.session.add(new_student)
    db.session.commit()
    login_user(new_student)
    return redirect(url_for('public.welcome'))

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('public.welcome'))

