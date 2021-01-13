from flask import Flask, render_template, url_for, request, redirect, g, session, jsonify
from flask_mysqldb import MySQL
import datetime
import os
from functions import SeleniumWS, amazCateg, getPandas, getValUser, amazonRecomend, homeScrap, getPriceAmaz, defaultTipos, getItemFromUsers
import pandas as pd
from recomendation_system import getRecomendations, getRecomUser, getRecomendationsSVD, getRecomendationsSVDpp

defaultTiposSet = set(defaultTipos.keys())

app = Flask(__name__)
app.secret_key = 'somesecretkeythatonlyishouldknowasdasd'

app.config['MYSQL_USER'] = 'b5d3dc83d57112'
app.config['MYSQL_PASSWORD'] = '49504a27'
app.config['MYSQL_HOST'] = 'eu-cdbr-west-03.cleardb.net'
app.config['MYSQL_DB'] = 'heroku_ab41830ce9d6747'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
tipo_ = ''

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        g.user = session['user_id']

@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user != None:
        cur = mysql.connection.cursor()
        print(g.user)
        sections = homeScrap()
        itemsS = []
        for _, value in sections.items():
            itemsS += value
        cur.execute('SELECT description, tipo FROM favoritos WHERE usuario = "' + g.user + '";')
        getData = cur.fetchall()
        for item in itemsS:
            itemCap = {'description': item['description'], 'tipo': item['tipo']}
            if itemCap in getData:
                item['fav'] = 'fav'
            else:
                item['fav'] = 'nofav'
        return render_template('home.html', sections=sections)
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
            return redirect(url_for('index'))
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

        username_ = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        cur.execute('''SELECT * FROM usuarios''')
        pairUserPass = cur.fetchall()
        user = [usr for usr in pairUserPass if usr['username'] == username_]
        if len(user) == 0 and password1 == password2:
            cur.execute('''INSERT INTO usuarios (username, password) VALUES (%s, %s)''', [username_, password1])
            session['user_id'] = username_
            mysql.connection.commit()
            return redirect(url_for('busqueda'))
        else:
            return redirect(url_for('register'))
    else:
        return render_template('register.html')

@app.route('/busqueda', methods=['GET', 'POST'])
def busqueda():
    if not g.user:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        itemName = request.form['itemName']
        items, tipo_ = SeleniumWS(itemName)
        if tipo_ not in defaultTiposSet:
            tipo_ = 'Todos los departamentos'
        cur.execute('''INSERT INTO busquedas (name, tipo, usuario) VALUES (%s, %s, %s)''', (itemName, tipo_, g.user))
        mysql.connection.commit()
        cur.execute('SELECT name, description, price FROM favoritos WHERE usuario = "' + g.user + '";')
        getData = cur.fetchall()
        for item in items:
            item['tipo'] = tipo_
            itemCap = {'name': item['name'], 'description': item['description'], 'price': item['price']}
            if itemCap in getData:
                item['fav'] = 'fav'
            else:
                item['fav'] = 'nofav'

        return render_template('busqueda.html', items=items)
    else:
        return render_template('busqueda.html', items=[])

@app.route('/favorite', methods=['POST'])
def favorite():
    cur = mysql.connection.cursor()
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    fotoSrc = request.form['fotoSrc']
    linkGS = request.form['linkGS']
    tipo = request.form['tipo']
    if name != 'NoName':
        res = amazCateg(name)
        if res and res in defaultTiposSet:
            tipo = res
    else:
        res = amazCateg(description)
        if res and res in defaultTiposSet:
            tipo = res
    if tipo not in defaultTiposSet:
        tipo = 'Todos los departamentos'
    print(tipo)
    cur.execute('''INSERT INTO favoritos (name, description, price, linkGS, usuario, tipo) VALUES (%s, %s, %s, %s, %s, %s);''', 
        (name, description, price, linkGS, g.user, tipo))
    mysql.connection.commit()
    return jsonify({'nice': 'nice'})

@app.route('/favoriteHome', methods=['POST'])
def favoriteHome():
    cur = mysql.connection.cursor()
    name = request.form['name']
    description = request.form['description']
    fotoSrc = request.form['fotoSrc']
    linkGS = request.form['linkGS']
    tipo = request.form['tipo']
    if tipo not in defaultTiposSet:
        tipo = 'Todos los departamentos'
    print(tipo)
    price = getPriceAmaz(linkGS)
    cur.execute('''INSERT INTO favoritos (name, description, price, linkGS, usuario, tipo) VALUES (%s, %s, %s, %s, %s, %s);''', 
        (name, description, price, linkGS, g.user, tipo))
    mysql.connection.commit()
    return jsonify({'nice': 'nice'})

@app.route('/delfavorite', methods=['POST'])
def delfavorite():
    cur = mysql.connection.cursor()
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']

    cur.execute('''DELETE FROM favoritos
        WHERE name = %s AND description = %s AND price = %s AND usuario = "''' + g.user + '";', 
        (name, description, price))
    mysql.connection.commit()
    return jsonify({'nice': 'nice'})

@app.route('/delfavoriteHome', methods=['POST'])
def delfavoriteHome():
    cur = mysql.connection.cursor()
    name = request.form['name']
    description = request.form['description']
    linkGS = request.form['linkGS']

    cur.execute('''DELETE FROM favoritos
        WHERE name = %s AND description = %s AND linkGS = %s AND usuario = "''' + g.user + '";', 
        (name, description, linkGS))
    mysql.connection.commit()
    return jsonify({'nice': 'nice'})

@app.route('/misfavoritos', methods=['GET', 'POST'])
def misfavoritos():
    cur = mysql.connection.cursor()
    if not g.user:
        return redirect(url_for('login'))
    cur.execute('SELECT * FROM favoritos WHERE usuario = "' + g.user + '";')
    itemsFav = cur.fetchall()
    return render_template('favoritos.html', items=itemsFav)

@app.route('/recomendaciones', methods=['GET', 'POST'])
def recomendaciones():
    cur = mysql.connection.cursor()
    if not g.user:
        return redirect(url_for('login'))
    cur.execute('SELECT * FROM usuarios')
    usuarios = cur.fetchall()
    cur.execute('SELECT * FROM favoritos')
    itemsFav = cur.fetchall()
    cur.execute('SELECT * FROM busquedas')
    busquedas = cur.fetchall()
    getRecomendations(getPandas(usuarios, itemsFav, busquedas))
    usuariosVecinos = getRecomUser(g.user)
    itemsRecomendados = getItemFromUsers(itemsFav, usuariosVecinos, g.user)
    return render_template('favoritos.html', items=itemsRecomendados)

@app.route('/recomendacionesSVD', methods=['GET', 'POST'])
def recomendacionesSVD():
    cur = mysql.connection.cursor()
    if not g.user:
        return redirect(url_for('login'))
    cur.execute('SELECT * FROM usuarios')
    usuarios = cur.fetchall()
    cur.execute('SELECT * FROM favoritos')
    itemsFav = cur.fetchall()
    cur.execute('SELECT * FROM busquedas')
    busquedas = cur.fetchall()
    getRecomendationsSVD(getPandas(usuarios, itemsFav, busquedas))
    # usuariosVecinos = getRecomUser(g.user)
    # itemsRecomendados = getItemFromUsers(itemsFav, usuariosVecinos, g.user)
    return render_template('favoritos.html', items=[])#itemsRecomendados)

@app.route('/recomendacionesSVDpp', methods=['GET', 'POST'])
def recomendacionesSVDpp():
    cur = mysql.connection.cursor()
    if not g.user:
        return redirect(url_for('login'))
    cur.execute('SELECT * FROM usuarios')
    usuarios = cur.fetchall()
    cur.execute('SELECT * FROM favoritos')
    itemsFav = cur.fetchall()
    cur.execute('SELECT * FROM busquedas')
    busquedas = cur.fetchall()
    getRecomendationsSVDpp(getPandas(usuarios, itemsFav, busquedas, busqAct=False))
    # usuariosVecinos = getRecomUser(g.user)
    # itemsRecomendados = getItemFromUsers(itemsFav, usuariosVecinos, g.user)
    return render_template('favoritos.html', items=[])#itemsRecomendados)

@app.route('/recomendacionIndv', methods=['GET', 'POST'])
def recomendacionIndv():
    cur = mysql.connection.cursor()
    if not g.user:
        return redirect(url_for('login'))
    cur.execute('SELECT * FROM favoritos WHERE usuario="' + g.user + '";')
    itemsFav = cur.fetchall()
    cur.execute('SELECT * FROM busquedas WHERE usuario="' + g.user + '";')
    busquedas = cur.fetchall()
    items = amazonRecomend(getValUser(itemsFav, busquedas))
    cur.execute('SELECT name, description, price FROM favoritos WHERE usuario = "' + g.user + '";')
    getData = cur.fetchall()
    for item in items:
        itemCap = {'name': item['name'], 'description': item['description'], 'price': item['price']}
        if itemCap in getData:
            item['fav'] = 'fav'
        else:
            item['fav'] = 'nofav'
    return render_template('busqueda.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)
