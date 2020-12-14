from flask import Flask, render_template, url_for, request, redirect, g, session
from flask_restful import Api, Resource, reqparse, abort
from flask_mysqldb import MySQL
import os
from functions import SeleniumWS


app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknow'

app.config['MYSQL_USER'] = 'b5d3dc83d57112'
app.config['MYSQL_PASSWORD'] = '49504a27'
app.config['MYSQL_HOST'] = 'eu-cdbr-west-03.cleardb.net'
app.config['MYSQL_DB'] = 'heroku_ab41830ce9d6747'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        g.user = session['user_id']

@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user != None:
        print(g.user)
        return redirect(url_for('busqueda'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        cur.execute('''SELECT * FROM usuarios''')
        pairUserPass = cur.fetchall()
        user = [usr for usr in pairUserPass if usr['username'] == username and usr['password'] == password]
        if len(user) != 0:
            session['user_id'] = user[0]['username']
            return redirect(url_for('busqueda'))
        else:
            return redirect(url_for('login'))
    else:
        session.pop('user_id', None)
        return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        cur.execute('''SELECT * FROM usuarios''')
        pairUserPass = cur.fetchall()
        user = [usr for usr in pairUserPass if usr['username'] == username]
        if len(user) == 0 and password1 == password2:
            cur.execute('''INSERT INTO usuarios (username, password) VALUES (%s, %s)''', (username, password1))
            session['user_id'] = username
            mysql.connection.commit()
            return redirect(url_for('busqueda'))
        else:
            return redirect(url_for('register'))
    else:
        return render_template('register.html')

@app.route('/busqueda', methods=['GET', 'POST'])
def busqueda():
    if request.method == 'POST':
        itemName = request.form['itemName']
        items = SeleniumWS(itemName)
        return render_template('busqueda.html', items=items)
    else:
        return render_template('busqueda.html', items=[])

if __name__ == '__main__':
    app.run(debug=True)
