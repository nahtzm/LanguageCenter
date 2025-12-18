from flask import Blueprint, render_template
from flask_login import current_user

from models import Class, UserRole

teacher_routes = Blueprint('teacher', __name__)

@teacher_routes.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    classes = Class.query.filter_by(
        teacher_id=current_user.id
    ).all()
    print(current_user.role)
    return render_template(
        "dashboard/teacher/teacher.html",
        UserRole=UserRole,
        current_user=current_user,
        classes=classes
    )