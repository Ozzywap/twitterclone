from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import mysql.connector

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'twitter'


cnx = mysql.connector.connect(user = 'root', database = 'twitter')

cursor = cnx.cursor()

cursor.execute(''' insert into users values (1, 'leron', 'james', 'ohio') ''')


cnx.commit()

cursor.close()

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)