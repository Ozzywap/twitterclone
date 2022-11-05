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

def retrieve_query(query):
    # helper function to establish connection and retrieve queries
    cnx = mysql.connector.connect(user = 'root', database = 'twitter')
    cursor = cnx.cursor(buffered=True)
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return data

def retrieve_query_single(query):
    # helper function to establish connection and retrieve queries
    cnx = mysql.connector.connect(user = 'root', database = 'twitter')
    cursor = cnx.cursor(buffered=True)
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    return data[0]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/tweet", methods = ['POST', 'GET'])
def tweet():
    if request.method == 'GET':
        return "Login via the login Form"
    if request.method == 'POST':
        tweet = request.form['tweet']
        ip = request.environ['REMOTE_ADDR']
        
        user_id = retrieve_query_single(f'''select uid from user where ip = "{ip}"''')
        if user_id == None:
            submit_query(f'''insert into user (ip) value ('{ip}')''')
            user_id = retrieve_query_single(f'''select uid from user where ip = {ip}''')
        submit_query(f'''insert into tweet(uid, post) values ('{user_id}', '{tweet}')''')
        tweets = retrieve_query(f'''select * from tweet order by date desc''')
        return render_template("form.html", tweets=tweets)


if __name__ == '__main__':
    app.run(debug=True)