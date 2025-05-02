from flask import render_template
from app import app

@app.route('/')
@app.route('/dashboard')

def dashboard():
	return render_template('dashboard.html')
