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
        user_id = retrieve_query_single(f'''select uid from user where ip = "{ip}"''')
    return user_id

def render_tweets(tweets):
    tweet_status = []
    id_checked = {}
    for i in tweets:
        if i[3] not in id_checked.keys():
            if retrieve_query_single(f'''select follower from follows where uid = {i[3]} and follower = {get_uid()}''') == None:
                tweet_status.append((i[3], i[1], i[2],'Follow'))
                id_checked[i[3]] = 'Follow'
            else:
                tweet_status.append((i[3], i[1], i[2], 'Unfollow'))
                id_checked[i[3]] = 'Unfollow'
        else:
            status = id_checked[i[3]]
            tweet_status.append((i[3], i[1], i[2],status))
    return tweet_status

def render_tweets_followers():
    user_id = get_uid()
    tweets = retrieve_query(f'''select * from tweet where uid in (select uid from follows where follower = {user_id}) order by date desc''')
    tweet_status = render_tweets(tweets)

    return tweet_status

def render_tweets_non_followers():
    user_id = get_uid()
    tweets = retrieve_query(f'''select * from tweet where uid not in (select uid from follows where follower = {user_id}) order by date desc''')
    tweet_status = render_tweets(tweets)

    return tweet_status

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/form")
def form():
    tweet_status = render_tweets()
    follower_tweet_status = render_tweets_followers()
    return render_template("form.html", tweet_status=tweet_status, follower_tweet_status=follower_tweet_status)

@app.route("/post", methods= ['GET', 'POST'])
def post():
    user_id= get_uid()
    try:
        tweet = request.form.get('tweet')
        if tweet != None:
            submit_query(f'''insert into tweet(uid, post) values ('{user_id}', '{tweet}')''')
    except Exception:
        pass

    return render_template("post.html")

@app.route("/feed", methods= ['GET', 'POST'])
def feed(): 
    user_id = get_uid()
    try:
        unfollow_id = request.args.get('unfollow')
        submit_query(f'''delete from follows where uid = {unfollow_id} and follower = {user_id}''')
    except Exception:
        pass
    follower_tweet_status = render_tweets_followers()
    return render_template("feed.html", tweet_status=follower_tweet_status)

@app.route("/explore", methods= ['GET', 'POST'])
def explore():
    user_id = get_uid()
    try:
        follow_id = request.args.get('follow')
        following = retrieve_query_single(f'''select follower from follows where uid = {follow_id} and follower = {user_id}''')
        if following == None:
            submit_query(f'''insert into follows(uid,follower) values ({follow_id}, {user_id}) ''')
    except Exception:
        pass
    non_follower_tweet_status = render_tweets_non_followers()
    return render_template("explore.html", tweet_status=non_follower_tweet_status)

@app.route("/tweet", methods = ['POST', 'GET'])
def tweet():
    if request.method == 'GET':
        follow_id = request.args.get('follow')
        unfollow_id = request.args.get('unfollow')

        user_id = get_uid()
        if unfollow_id == None:
            following = retrieve_query_single(f'''select follower from follows where uid = {follow_id} and follower = {user_id}''')
            if following == None:
                submit_query(f'''insert into follows(uid,follower) values ({follow_id}, {user_id}) ''')
        else:
            submit_query(f'''delete from follows where uid = {unfollow_id} and follower = {user_id}''')
        
        tweet_status = render_tweets()
        follower_tweet_status = render_tweets_followers()
        return render_template("form.html", tweet_status=tweet_status, follower_tweet_status=follower_tweet_status)
        
    if request.method == 'POST':
        tweet = request.form['tweet']
        
        user_id= get_uid()
        submit_query(f'''insert into tweet(uid, post) values ('{user_id}', '{tweet}')''')
        
        tweet_status = render_tweets()
        follower_tweet_status = render_tweets_followers()
                
        return render_template("form.html", tweet_status=tweet_status, follower_tweet_status=follower_tweet_status)


if __name__ == '__main__':
    app.run(debug=True)