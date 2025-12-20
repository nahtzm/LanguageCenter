from flask import Blueprint, render_template, url_for, redirect
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user, login_required
from flask import abort

from models import UserRole, Level, Class

admin_routes = Blueprint('admin_route', __name__)


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == UserRole.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        abort(403)



class ClassAdminView(AdminModelView):
    form_columns = ['max_students']

    column_list = ['id', 'name', 'max_students']
    column_labels = {
        'max_students': 'Số học viên tối đa'
    }

    can_create = False
    can_delete = False

class LevelAdminView(AdminModelView):
    form_columns = ['tuition_fee']
    can_create = False
    can_delete = False


