from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    return "Login"

@auth.route('/register', methods=['GET', 'POST'])
def register():
    return "Register"

@auth.route('/logout')
def logout():
    return "Logout"

