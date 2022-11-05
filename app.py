from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'twitter'
 
mysql = MySQL(app)


cursor = mysql.connection.cursor()

cursor.execute(''' insert into users values (1, 'leron', 'james', 'ohio') ''')

mysql.connection.commit()

cursor.close()

@app.route("/")
def index():
    return render_template("index.html")
