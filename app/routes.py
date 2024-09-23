from app import app
from flask import render_template, request, redirect, url_for
import mysql.connector

# conectar BD
def dbconnect():
    return mysql.connector.connect(
    host= 'localhost',
    user= 'root',
    password= '1234', 
    database='pycrud',

    )

@app.route('/')
@app.route('/home')
def home():
   
    return render_template('home.html')

# CREATE    
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        nome_produto = request.form['nome_produto']
        valor_produto = request.form['valor_produto']
        quantidade_produto = request.form['quantidade_produto']
        categoria_produto = request.form['categoria_produto']
        validade = request.form['validade']

        conn = dbconnect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vendas (nome_produto, valor_produto, quantidade_produto,categoria, validade) VALUES (%s, %s, %s, %s, %s)", (nome_produto, valor_produto, quantidade_produto, categoria_produto, validade))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('home')

    return render_template('create.html')

# READ
@app.route('/recovery')
def recovery():
    conn = dbconnect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vendas")
    produtos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('recovery.html', produtos=produtos)

# Update 
@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        idvendas = request.form['id']
        nome_produto = request.form['nome_produto']
        valor_produto = request.form['valor_produto']
        quantidade_produto = request.form['quantidade_produto']
        categoria_produto = request.form['categoria_produto']
        validade = request.form['validade']

        conn = dbconnect()
        cursor = conn.cursor()
        cursor.execute("UPDATE vendas SET nome_produto=%s, valor_produto=%s, quantidade_produto=%s, categoria=%s, validade=%s WHERE idvendas=%s", (nome_produto, valor_produto, quantidade_produto, categoria_produto, validade, idvendas))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('home')

    return render_template('update.html')

# Delete 
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        idvendas = request.form['id']

        conn = dbconnect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vendas WHERE idvendas=%s", [idvendas])
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('home')
    else:
        return render_template('delete.html')

if __name__ == '__main__':
    app.run(debug=True)
