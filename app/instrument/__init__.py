from flask import Blueprint

instrument = Blueprint('instrument', __name__)

from . import views
