from flask import request

def get_registration_data():
    return {
        'username': request.form['username'],
        'email': request.form['email'],
        'password': request.form['password']
    }
