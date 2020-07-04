from flask import Blueprint
from flask_admin import Admin

admin = Admin(name='att')
bp = Blueprint('admin_bp', __name__)

from src.admin_app import routes
