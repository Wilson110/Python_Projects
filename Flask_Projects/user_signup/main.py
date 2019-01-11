from flask import Flask, request, render_template
import re
import os


app = Flask(__name__)
app.config['DEBUG'] = True

# Testing function for input validation
def input_validation(input):
    if " " in input:
        return False
    if len(input) > 20:
        return False 
    if len(input) < 3:
        return False
    return True

# Testing function for email validation
def email_validation(email):
    if email == " " or re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    return False

@app.route('/', methods=['POST'])
def form_validation():

    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    password_confirm = request.form['password_confirm']

    username_error = ""
    password_error = ""
    pswdconfirm_error = ""
    email_error = ""
    error = True

    if not input_validation(username):
        username_error = "Please enter a username."
        error = False
    if not input_validation(password):
        password_error = "Password cannot be left blank."
        error = False
    if not input_validation(password_confirm):
        pswdconfirm_error = "Password cannot be left blank."
        error = False
    if password != password_confirm:
        pswdconfirm_error = "Passwords must match. Please enter a valid password."
        error = False
    if not email_validation(email):
        email_error = "Please enter a valid email."
        error = False

    #if error is true after passing conditions
    if error:
        return render_template('welcome.html', username=username)    
    return render_template('form.html', username=username, password=password, 
                            password_confirm=password_confirm,
                            email=email, username_error=username_error,
                            password_error=password_error, pswdconfirm_error=pswdconfirm_error, email_error=email_error)

@app.route('/')
def index():
    return render_template('form.html')

app.run()