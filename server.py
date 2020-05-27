import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"

@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_books = cur.execute('SELECT * FROM books;').fetchall()
    return jsonify(all_books)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/api/v1/resources/bookz', methods=['GET']) #example request "curl 0.0.0.0:5000/api/v1/resources/bookz?id=123"
def api_id():
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specifiy an ID."

    results = []

    for book in books:
        if book['id'] == id:
            results.append(book)

    return jsonify(results)

@app.route('/api/v1/resources/books', methods=['GET']) #example request "curl 127.0.0.1:5000/api/v1/resources/books?author=Connie+Willis", "curl 127.0.0.1:5000/api/v1/resources/books?published=2010", "curl 127.0.0.1:5000/api/v1/resources/books?author=Connie+Willis&published=1999"
def api_filter():

    print('**********************************')
    print('hi, you just reached api_filter :)')
    print(request.form)
    print(request.data) #here's where you can see data passed like in this request "curl --header "Content-Type: application/json"   --request GET   --data '{"KEY1":"VAL1","KEY2":"VAL2"}'   127.0.0.1:5000/api/v1/resources/books?author=Connie+Willis&published=1999"
    print('**********************************')

    query_parameters = request.args

    id = query_parameters.get('id')
    published = query_parameters.get('published')
    author = query_parameters.get('author')

    query = "SELECT * FROM books WHERE"
    to_filter = []

    if id:
        query += ' id=? AND'
        to_filter.append(id)
    if published:
        query += ' published=? AND'
        to_filter.append(published)
    if author:
        query += ' author=? AND'
        to_filter.append(author)
    if not (id or published or author):
        return page_not_found(404)

    query = query[:-4] + ';'

    conn = sqlite3.connect('books.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()

    return jsonify(results)

app.run()
