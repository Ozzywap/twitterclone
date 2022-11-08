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
    if data == None:
        return None
    return data[0]

def get_uid():
    ip = request.environ['REMOTE_ADDR']
    user_id = retrieve_query_single(f'''select uid from user where ip = "{ip}"''')
    if user_id == None:
        submit_query(f'''insert into user (ip) value ('{ip}')''')
        user_id = retrieve_query_single(f'''select uid from user where ip = {ip}''')
    return user_id

def follow_status():
    tweets = retrieve_query(f'''select * from tweet order by date desc''')
    tweet_status = []
    # id_checked = []
    for i in tweets:
    # if i[3] not in id_checked:
        if retrieve_query_single(f'''select follower from follows where uid = {i[3]} and follower = {get_uid()}''') == None:
            tweet_status.append((i[3], i[1], i[2],'Follow'))
        else:
            tweet_status.append((i[3], i[1], i[2], 'Following'))
    # id_checked.append(i[3])
    return tweet_status

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/form")
def form():
    tweet_status = follow_status()
    return render_template("form.html", tweet_status=tweet_status)


@app.route("/tweet", methods = ['POST', 'GET'])
def tweet():
    if request.method == 'GET':
        follow_id = request.args['follow']

        user_id = get_uid()
        following = retrieve_query_single(f'''select follower from follows where uid = {follow_id} and follower = {user_id}''')
        if following == None:
            submit_query(f'''insert into follows(uid,follower) values ({follow_id}, {user_id}) ''')
        
        tweet_status = follow_status()
        return render_template("form.html", tweet_status=tweet_status)
        
    if request.method == 'POST':
        tweet = request.form['tweet']
        
        user_id= get_uid()
        submit_query(f'''insert into tweet(uid, post) values ('{user_id}', '{tweet}')''')
        
        tweet_status = follow_status()
                
        return render_template("form.html", tweet_status=tweet_status)


if __name__ == '__main__':
    app.run(debug=True)