import sqlite3
import time
import os
import pandas as pd
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from dotenv import load_dotenv
from fileinput import filename
from werkzeug.utils import secure_filename
import function

from datetime import datetime
load_dotenv()

from flask_apscheduler import APScheduler
scheduler = APScheduler()
@scheduler.task('cron', id='do_job_2', minute="6",hour="6",misfire_grace_time=3600)
def job2():
    function.notify_users()
scheduler.start() 

 
# Define allowed files
ALLOWED_EXTENSIONS = {'csv'}

def get_db_connection():
    conn = sqlite3.connect('db/app.db')
    conn.row_factory = sqlite3.Row
    return conn
def get_birthday(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM birthday WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post
def get_settings():
    conn = get_db_connection()
    post = conn.execute('SELECT config FROM tinyud_config WHERE name ="GotifyURL" ').fetchone()
    conn.close()
    if post is None:
        return ""
    else:
        return post[0]
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
# Upload folder
UPLOAD_FOLDER = 'db'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER
app.config["DEBUG"] = True
@app.template_filter('ctime')
def timectime(s):
    return time.ctime(s) # datetime.datetime.fromtimestamp(s)

@app.route('/')
def index():
    conn = get_db_connection()
    NbBirthday = conn.execute('SELECT COUNT(id) FROM birthday').fetchone()
    NbUser= conn.execute('SELECT COUNT(id) FROM users').fetchone()
    conn.close()
    return render_template('index.html', NbBirthday=NbBirthday,NbUser=NbUser)

@app.route('/birthday')
def birthday():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM birthday ORDER BY name ASC').fetchall()
    conn.close()
    return render_template('birthday.html', posts=posts)

@app.route('/test')
def test_not():
    function.notify_users()
    return redirect(url_for('index'))
@app.route('/test_admin')
def test_admin():
    function.notify_users_test()
    return redirect(url_for('index'))

@app.route('/users')
def list_users():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('users.html', posts=posts)

@app.route('/create_users', methods=('GET', 'POST'))
def create_users():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        whatsapp = request.form['whatsapp']
        telegram = request.form['telegram']
        gotify = request.form['gotify']



        if not name:
            flash('Title is required!')
        else:
            function.add_user(name,email,whatsapp,gotify,telegram)
            return redirect(url_for('list_users'))
    
    return render_template('create_users.html')
@app.route('/import_csv', methods=('GET', 'POST'))
def import_csv():
    if request.method == 'POST':
        print("ok")
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], "db.csv" )
            # set the file path
            uploaded_file.save(file_path)
            # save the file
        conn = get_db_connection()
        # Use Pandas to parse the CSV file
        csvData = pd.read_csv("db/db.csv")
        # Loop through the Rows
        for i,row in csvData.iterrows():
                if pd.notnull(row['Birthday']):
                    name=row['First Name']+" "+row['Last Name']
                    print(name)
                    print(row['Birthday'])
                    date_obj=datetime.strptime(row['Birthday'],"%Y-%m-%d")
                    birthday=date_obj.strftime("%d-%m-%Y")
                    birthday_day_month=date_obj.strftime("%d-%m")
                    id=row['First Name'][:2]+row['Last Name'][:2]+date_obj.strftime("%d-%m-%Y")
                    conn.execute('INSERT OR IGNORE INTO birthday (name ,date,birthday_day_month,googleid ) VALUES (?,?,?,?)',(name, birthday,birthday_day_month,id))

        
        conn.commit()
        conn.close()
    return render_template('importcsv.html')

@app.route('/settings', methods=('GET', 'POST'))
def settings():
    settings=get_settings()
    
    if request.method == 'POST':
        Gotify = request.form['settings']
        if not Gotify:
            flash('Gotify URL is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE tinyud_config SET config = ? WHERE name = ?',(Gotify,"GotifyURL"))
            conn.commit()
            conn.close()
            flash('"{}" was successfully added!'.format(Gotify))
            return redirect(url_for('index'))
    
    return render_template('settings.html', settings=settings)


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM users WHERE id = ?',(id,)).fetchone()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        whatsapp = request.form['whatsapp']
        gotify = request.form['gotify']
        telegram = request.form['telegram']
        conn = get_db_connection()
        post = conn.execute('UPDATE users SET name = ?, email = ?, whatsapp = ?, gotify = ?, telegram = ? WHERE id = ?',(name, email, whatsapp, gotify, telegram,id,))
        conn.commit()
        conn.close()
        return redirect(url_for('list_users'))
    
    return render_template('edit_users.html', post=post)
@app.route('/<int:id>/edit_notify_user', methods=('GET', 'POST'))
def edit_notify_user(id):
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM birthday ORDER BY name ASC').fetchall()
    birthday_list_user = conn.execute('SELECT birthday_id FROM users_birthday WHERE user_id = ?',(id,)).fetchall()
    birthdaylist=[] 
    for z in birthday_list_user:
        birthdaylist.append(z[0] )
    conn.close()

    if request.method == 'POST':
        conn = get_db_connection()
        id_selected = request.form.getlist('id_selected')
        conn.execute('DELETE FROM users_birthday WHERE user_id IN (?)', (id,))
        conn.commit()       
        for id_select in id_selected:
            conn.execute('INSERT INTO users_birthday (user_id ,birthday_id ) VALUES (?,?)',(id,id_select))
            
        conn.commit()
        conn.close()
        return redirect(url_for('list_users'))
    
    return render_template('edit_notify_user.html', posts=posts,birthday_list_user=birthdaylist)
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.execute('DELETE FROM users_birthday WHERE user_id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('list_users'))

