import flask
import json
from flask import request, jsonify
import sqlite3
from sqlite3 import Error
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

DB_FILE = 'messages.db'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

#example curl 0.0.0.0:5000/
@app.route('/', methods=['GET']) 
def home():
    return "<h1>Fayad's Messaging App</h1><p>This site provides the APIs needed for messaging in the app.</p>"

#curl 0.0.0.0:5000/messages/all
@app.route('/messages/all', methods=['GET'])
def show_all_messages():
    cur = getCursor()
    all_messages = cur.execute('SELECT * FROM messages;').fetchall()
    return jsonify(all_messages)

#curl --request POST 0.0.0.0:5000/create-messages-table
@app.route('/create-messages-table', methods=['POST']) 
def create_messages_table():
    cur = getCursor()
    cur.execute('CREATE TABLE messages (message TEXT, sender TEXT, receiver TEXT);')
    return "Sucessfully created messages table!"

#example request "curl --header "Content-Type: application/json" --request POST --data '{"from":"daniel", "to":"jess", "message":"loveu"}' 0.0.0.0:5000/messages/send"
@app.route('/messages/send', methods=['POST']) 
def send_message():
    print(request.data)
    try:
        sender, receiver, msg = parseMesssageInfo(request.data)
    except:
        return "Please send message in expected format", 400

    task = (msg, sender, receiver)
    sql = ''' INSERT INTO messages(message, sender, receiver)
          VALUES(?,?,?) '''

    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = dict_factory
        cur = conn.cursor()
        cur.execute(sql, task)
        conn.commit()
        cur.close()
        return "Message sent!"

    except Error as e: 
        return "Message could not be sent due to the following error {}".format(e), 500

#example request "curl --header "Content-Type: application/json"   --request GET  http://0.0.0.0:5000/messages?user=daniel"
@app.route('/messages', methods=['GET']) 
def get_my_messages():
    if 'user' in request.args:
        user = request.args['user']
    else:
        return "Error: No id field provided. Please specifiy an ID."

    query = "SELECT * FROM messages WHERE receiver=?"
    task = (user,)

    try: 
        cur = getCursor()
        messages = cur.execute(query, task).fetchall()
        parsed = parseMessagesToShow(messages)
        response = jsonify(parsed)
        return response
    except Error as e:
        return "Could not get messages due to the following error {}".format(e)

#only for debugging
#curl --request POST 0.0.0.0:5000/delete-messages-table
# @app.route('/delete-messages-table', methods=['POST']) 
# def delete_table():
#     conn = sqlite3.connect(DB_FILE)
#     conn.row_factory = dict_factory
#     cur = conn.cursor()
#     cur.execute('DROP TABLE messages;')
#     return "sucessfully deleted messages table"

def parseMessagesToShow(messages):
    parsed = []
    for message in messages:
        msg = message['message']
        sender = message['sender']
        parsed_msg = '"{}" -{}'.format(msg, sender)
        parsed.append(parsed_msg)
    return parsed

def parseMesssageInfo(rawData):
    body = json.loads(request.data)
    sender = body["from"]
    receiver = body["to"]
    msg = body["message"]
    return sender, receiver, msg

def getCursor():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = dict_factory
    return conn.cursor()


app.run()