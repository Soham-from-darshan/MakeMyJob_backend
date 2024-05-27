from flask import Blueprint, jsonify
from Application.controllers.authentication import login_required
from flask_jwt_extended import get_jwt_identity
from Application import db
from Application.models import User


bp = Blueprint('Account',__name__,url_prefix='/account')


@bp.route('/getUser')
@login_required()
def get_user():
    return db.get_or_404(User, get_jwt_identity()).serialize()


@bp.route('/deleteUser')
@login_required()
def delete_user():
    User.query.filter_by(id=get_jwt_identity()).delete()
    db.session.commit()
    return jsonify(f'User has been deleted'), 200


def delete_inactive_accounts():
    pass
