#imports
from contextlib import closing
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

#config
#DATABASE = '.\\tmp\\flaskr.db'
SQLALCHEMY_DATABASE_URI='postgresql://postgres:postgres123@localhost/height_collector'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

#create app
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('SELECT id, title, text FROM entries ORDER BY id DESC')
    entries = [dict(id=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('INSERT INTO entries (title, text) VALUES (?, ?)', 
                 [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/delete', methods=['POST'])
def del_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('DELETE FROM entries WHERE id = ?', 
                 [request.form['id']])
    g.db.commit()
    flash('Entry deleted')
    return redirect(url_for('show_entries'))

@app.route('/edit-entry', methods=["POST"])
def edit_entry():
    if not session.get('logged_in'):
        abort(401)
    cur = g.db.execute('SELECT id, title, text FROM entries WHERE id =?',
                       [request.form['edit_id']])
    entries = [dict(id=row[0], title=row[1], text=row[2]) for row in cur.fetchall()]
    edit_id = request.form['edit_id']
    return render_template('edit_entry.html', entries=entries, edit_id=edit_id)

@app.route('/update-entry', methods=["POST"])
def update_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('UPDATE entries SET title=?, text=? WHERE id =?', 
                 [request.form['title'], request.form['text'], request.form['id']])
    g.db.commit()
    flash("Your entry has been updated")
    return redirect(url_for('show_entries'))
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid username"
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid password"
        else:
            session['logged_in'] = True
            flash('You were logged in successfully')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out successfully')
    return redirect(url_for('show_entries'))



if __name__ == '__main__':
    app.run()