from datetime import datetime

from flask import Blueprint, render_template, request, flash, url_for, redirect, abort
from flask_login import current_user, login_required

from app import db
from models import Class, UserRole, ScoreConfig, Enrollment, Student, Attendance, Score
from utils import calculate_attendance_score, calculate_average_and_result

teacher_routes = Blueprint('teacher', __name__)


@teacher_routes.route('/dashboard')
@login_required
def dashboard():
    classes = Class.query.filter_by(
        teacher_id=current_user.id
    ).all()
    return render_template(
        "dashboard/teacher/teacher.html",
        UserRole=UserRole,
        current_user=current_user,
        classes=classes
    )


@teacher_routes.route('/enter_score')
@login_required
def enter_score():
    class_id = request.args.get('class_id', type=int)
    selected_class = None
    enrollments = []
    score_configs = ScoreConfig.query.filter_by(is_active=True).all()
    result_map = {}

    if class_id:
        selected_class = Class.query.get_or_404(class_id)
        if selected_class.teacher_id != current_user.id:
            abort(403)

        enrollments = Enrollment.query.filter_by(
            class_id=selected_class.id
        ).all()

        for e in enrollments:
            avg, result = calculate_average_and_result(e, score_configs)
            result_map[e.id] = {
                "avg": avg,
                "result": result
            }

    return render_template(
        "dashboard/teacher/enter_score.html",
        selected_class=selected_class,
        enrollments=enrollments,
        score_configs=score_configs,
        result_map=result_map,
        current_user=current_user,
        UserRole=UserRole
    )



@teacher_routes.route('/save_scores', methods=['POST'])
@login_required
def save_scores():
    class_id = request.form.get('class_id', type=int)
    enrollments = Enrollment.query.filter_by(class_id=class_id).all()
    score_configs = ScoreConfig.query.filter_by(is_active=True).all()

    for enrollment in enrollments:
        for config in score_configs:

            if config.auto_calculated:
                value = calculate_attendance_score(enrollment.id)
            else:
                field = f"score_{enrollment.id}_{config.id}"
                raw = request.form.get(field)
                if not raw:
                    continue
                value = float(raw)

            score = Score.query.filter_by(
                enrollment_id=enrollment.id,
                score_config_id=config.id
            ).first()

            if score:
                score.score_value = value
            else:
                score = Score(
                    enrollment_id=enrollment.id,
                    score_config_id=config.id,
                    score_value=value
                )
                db.session.add(score)

    db.session.commit()
    flash("Lưu điểm thành công", "success")
    return redirect(request.referrer)


@teacher_routes.route('/roll_call', methods=['GET', 'POST'])
@login_required
def roll_call():
    # ===== 1. Lấy tham số =====
    class_id = request.args.get('class_id', type=int)
    session_date_str = request.args.get('session_date')

    # ===== 2. Xử lý ngày =====
    if session_date_str:
        try:
            session_date = datetime.strptime(session_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Ngày không hợp lệ', 'error')
            session_date = datetime.today().date()
    else:
        session_date = datetime.today().date()

    # ===== 3. Lấy lớp =====
    selected_class = Class.query.get(class_id) if class_id else None

    enrollments = []
    attendance_map = {}

    # ===== 4. Lấy danh sách học viên + điểm danh (GET) =====
    if selected_class:
        enrollments = (
            Enrollment.query
            .filter_by(class_id=selected_class.id)
            .join(Student)
            .order_by(Student.fullname)
            .all()
        )

        for enrollment in enrollments:
            attendance = Attendance.query.filter_by(
                enrollment_id=enrollment.id,
                session_date=session_date
            ).first()

            attendance_map[enrollment.id] = (
                attendance.is_present if attendance else None
            )

    # ===== 5. XỬ LÝ POST – LƯU ĐIỂM DANH =====
    if request.method == 'POST':
        if not selected_class:
            flash('Vui lòng chọn lớp', 'error')
            return redirect(request.url)

        saved_count = 0

        for enrollment in enrollments:
            radio_value = request.form.get(f'attendance_{enrollment.id}')
            is_present = (radio_value == 'present')

            attendance = Attendance.query.filter_by(
                enrollment_id=enrollment.id,
                session_date=session_date
            ).first()

            if attendance:
                attendance.is_present = is_present
            else:
                attendance = Attendance(
                    enrollment_id=enrollment.id,
                    session_date=session_date,
                    is_present=is_present
                )
                db.session.add(attendance)

            saved_count += 1

        db.session.commit()

        flash(
            f'Điểm danh thành công cho {saved_count} học viên ngày {session_date.strftime("%d/%m/%Y")}',
            'success'
        )

        return redirect(url_for(
            'teacher.roll_call',
            class_id=class_id,
            session_date=session_date.strftime('%Y-%m-%d')
        ))

    # ===== 6. RENDER =====
    return render_template(
        'dashboard/teacher/roll_call.html',
        current_user=current_user,
        UserRole=UserRole,
        selected_class=selected_class,
        enrollments=enrollments,
        attendance_map=attendance_map,
        session_date=session_date
    )

