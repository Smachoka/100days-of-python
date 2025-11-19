from flask import Flask, render_template, request, jsonify
import sqlite3
app = Flask(__name__)


def get_db_coneection():
    conn=sqlite3.connect('database.db')
    conn.row_factory=sqlite3.Row
    return conn

@app.route('/')
def home():       
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/users/api',methods=['GET'])
def get_users():
    conn=get_db_coneection()
    users=conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    users_list=[dict(user) for user in users]
    return jsonify(users_list)                          

#post request to add users
@app.route('/users/api',methods=['POST'])
def add_user():
    new_user=request.get_json()
    conn =get_db_coneection()
    conn.execute("INSERT INTO users (fname,sname, email) VALUES (?,?,?)",
                 (new_user['fname'],new_user['sname'],new_user['email']))
    conn.commit()
    conn.close()
    return jsonify({'message':'user added successfully'}), 201
if __name__ == '__main__':
   conn = get_db_coneection()
   conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,fname TEXT NOT NULL,sname TEXT NOT NULL,email)")
   conn.close()
   app.run(debug=True)