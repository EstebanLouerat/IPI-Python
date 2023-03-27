from flask import Blueprint
from . import db

app = Blueprint('app', __name__)

@app.route('/')
def index():
    return 'Index'

@app.route('/profile')
def profile():
    return 'Profile'
