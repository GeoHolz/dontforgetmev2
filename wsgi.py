import os
import json
import sqlite3
from app import app

# Chemins
db_path = '/app/db/app.db'


# Vérifie si la base de données existe
if not os.path.exists(db_path):
    print("Base de données non trouvée, création...")
    os.makedirs('/app/db', exist_ok=True)

    database = sqlite3.connect(db_path)
    database.execute('''
        CREATE TABLE IF NOT EXISTS birthday (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            date VARCHAR(20),
            birthday_day_month VARCHAR(20),
            googleid VARCHAR(100)
        );
    ''')
    database.execute('CREATE UNIQUE INDEX birthday_googleid ON birthday (googleid)')
    database.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100),
            whatsapp VARCHAR(100),
            gotify VARCHAR(100),
            telegram VARCHAR(100)
        );
    ''')
    database.execute('''
        CREATE TABLE IF NOT EXISTS users_birthday (
            id INTEGER PRIMARY KEY,
            user_id INT(10),
            birthday_id VARCHAR(100)
        );
    ''')
    database.commit()
    database.close()
    print("Base de données créée avec succès.")



# Lancer l'application
if __name__ == '__main__':
    app.run(debug=False)
