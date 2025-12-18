from flask import Blueprint, render_template

public = Blueprint('public', __name__)

@public.route('/')
def welcome():
    return render_template("welcome.html")