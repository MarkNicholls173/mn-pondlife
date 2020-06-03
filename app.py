from flask import Flask, redirect, url_for, request, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

#config
DEBUG = True
SECRET_KEY = "random string here"
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres123@localhost/pondlife'
SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(__name__)

db = SQLAlchemy(app)

class pondlife(db.Model):
    id = db.Column('entry_id', db.Integer, primary_key = True)
    date = db.Column(db.String(9))
    temp = db.Column(db.Float(4))
    ammonia = db.Column(db.Float(4))
    nitrites = db.Column(db.Float(4))
    nitrates = db.Column(db.Float(4))
    ph = db.Column(db.Float(4))
    g_hardness = db.Column(db.Float(4))
    c_hardness = db.Column(db.Float(4))

#def __init__(self, date, temp, ammonia, nitrites, nitrates, ph, hardness):
#    self.date = date
#    self.temp = temp
#    self.ammonia = ammonia
#    self.nitrites = nitrites
#    self.nitrates = nitrates
#    self.ph = ph
#    self.hardness = hardness


@app.route('/')
def index():
    return redirect(url_for('result'))


@app.route('/login', methods = ['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'stel' or \
           request.form['password'] != 'stel':
            error = 'Invalid username or password'
        else:
            session['username'] = request.form['username'] + " by POST"
            flash('you were successfully logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error = error)
        
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/input', methods = ['POST', 'GET'])
def input():
    if request.method == 'POST':
        entry = pondlife(
            date = request.form['date'], 
            temp = request.form['temp'],
            ammonia = request.form['amm'],
            nitrites = request.form['nitri'],
            nitrates = request.form['nitra'],
            ph = request.form['ph'],
            g_hardness = request.form['g_hard'],
            c_hardness = request.form['c_hard']          
            )
        db.session.add(entry)
        db.session.commit()
        flash('entry was added successfully!')
        return redirect(url_for('result'))
    return render_template('input.html')

@app.route('/edit/<id>', methods = ['POST', 'GET'])
def edit(id):
    entry = pondlife.query.get(id)
    if request.method == 'POST':
        entry.date = request.form['date'], 
        entry.temp = request.form['temp'],
        entry.ammonia = request.form['amm'],
        entry.nitrites = request.form['nitri'],
        entry.nitrates = request.form['nitra'],
        entry.ph = request.form['ph'],
        entry.g_hardness = request.form['g_hard'],
        entry.c_hardness = request.form['c_hard'] 
        db.session.commit()
        flash('updated record successfully')
        return redirect(url_for('result'))
    return render_template('edit.html', entry = entry)

@app.route('/delete/<id>')
def delete(id):
    entry = pondlife.query.get(id)
    db.session.delete(entry)
    db.session.commit()
    flash("entry deleted")
    return redirect(url_for('result'))

@app.route('/result')
def result():
    return render_template('result.html', results = pondlife.query.all())
    
if __name__ == '__main__':
    app.run()