from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from models import Student

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    email = request.form.get('email')
    password = request.form.get('password')
    student = Student.query.filter_by(email=email).first()
    if student and check_password_hash(student.password, password):
        flash('Login Successful', category='success')
        login_user(student)
        return redirect(url_for('public.welcome'))
    else:
        flash('Check again email and password', category='error')
        return render_template("login.html")


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
    return "Logout"

