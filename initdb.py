import sqlite3
database = sqlite3.connect('/app/db/app.db')
database.execute('CREATE TABLE IF NOT EXISTS birthday (	id INTEGER PRIMARY KEY ,	name VARCHAR(100),	date VARCHAR(20), birthday_day_month VARCHAR(20), googleid VARCHAR(100));')
database.execute('CREATE UNIQUE INDEX birthday_googleid on birthday (googleid)')
database.execute('CREATE TABLE IF NOT EXISTS users (	id INTEGER PRIMARY KEY ,	name VARCHAR(100),	email VARCHAR(100),	whatsapp VARCHAR(100), gotify VARCHAR(100), telegram VARCHAR(100));')
database.execute('CREATE TABLE IF NOT EXISTS users_birthday (id INTEGER PRIMARY KEY ,	user_id INT(10), birthday_id VARCHAR (100))')
database.commit()
database.close()