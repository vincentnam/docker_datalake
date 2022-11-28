from flask import Blueprint, jsonify, request, current_app
from ..services import swift, mongo


similarity_bp = Blueprint('similarity_bp', __name__)
@similarity_bp.route('/exemple', methods=['GET', 'POST'])
def get_all_measurements():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: Exemple
        responses:
            '200':
                description: call successful
        tags:
            - similarity_router
    """
    exemple = "OK"
    return exemple