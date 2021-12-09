from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from ftc.auth import login_required, admin_required
from ftc.db import get_db

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@login_required
def index():
    #Shows Hallo World and Description What to find where
    return render_template('dashboard/index.html')

@bp.route('/standings')
@login_required
def standings():
    return render_template('dashboard/standings.html')

@bp.route('/schedule')
@login_required
def schedule():
    return render_template('dashboard/schedule.html')

@bp.route('/admintools')
@login_required
@admin_required
def admintools():
    return render_template('dashboard/admintools.html')