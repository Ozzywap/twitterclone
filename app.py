from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import mysql.connector

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'twitter'

def submit_query(query):
    # helper function to establish connection and submit queries
    cnx = mysql.connector.connect(user = 'root', database = 'twitter')
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    cursor.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"
    if request.method == 'POST':
        tweet = request.form['tweet']
        ip = request.environ['REMOTE_ADDR']
        query = f'''insert into tweet(ip, post) values ('{ip}', '{tweet}')'''
        submit_query(query)
        return render_template("form.html")


if __name__ == '__main__':
    app.run(debug=True)