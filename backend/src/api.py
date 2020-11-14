import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)    


# uncomment the following line to initialize the datbase

db_drop_and_create_all()

# ROUTES

@app.route('/')
def handler():
    return jsonify({
        "success": True
    })

@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
    }), 

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = Drink.query.all()

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        "success": True,
        "drinks": [drink.long() for drink in drinks]
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(payload):
    data = request.get_json()
    title = data.get('title', None)
    recipe = str(json.dumps(data.get('recipe', None)))
    drink = Drink(title=title, recipe=recipe)
    try:
        drink.insert()
    except:
        abort(422)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    }), 200    


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id):
    drink = Drink.query.filter_by(id=drink_id).first()
    
    if drink is None:
        abort(404)
    
    data = request.get_json()
    title = data.get('title', None)
    recipe = str(json.dumps(data.get('recipe', None)))

    if title is not None:
        drink.title = title
    if recipe is not None:        
        drink.recipe = recipe

    try:
        drink.update()

    except:
        abort(422)

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    drink = Drink.query.filter_by(id=drink_id).first()

    if drink is None:
        abort(404)
    
    id = drink.long()['id']
     
    try:
        drink.delete()

    except Exception as e:
        print('EXCEPTION: ', str(e))
        abort(500)

    return jsonify({
        "success": True,
        "drinks": id
    })


## Error Handling
'''
Error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Unprocessable"
        }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404

@app.errorhandler(400)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response