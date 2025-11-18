from flask import Flask, render_template, request, jsonify
import sqlite3
app = Flask(__name__)


def get_db_coneection():
    conn=sqlite3.connect('database.db')
    conn.row_factory=sqlite3.Row
    return conn

@app.route('/')
def index():
    return '<h1>Welcome to the Home Page</h1>'
@app.route('/home')
def home():       
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')