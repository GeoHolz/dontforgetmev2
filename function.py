import os.path
import sqlite3
import os
import json
import json
import smtplib
from email.mime.text import MIMEText
import requests
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
# Basic configuration settings (user replaceable)

config_dir = 'config'
config_path = os.path.join(config_dir, 'config.json')

# Si le config.json n'existe pas, le créer
if not os.path.exists(config_path):
    print("[INFO] config.json non trouvé, création du fichier...")
    os.makedirs(config_dir, exist_ok=True)
    default_config = {
        "displayTZ": "Europe/Paris",
        "email_sender": "XXX@gmail.com",
        "email_password": "MY_PASSWORD_APP"
    }
    with open(config_path, 'w') as f:
        json.dump(default_config, f, indent=4)

# Maintenant on peut ouvrir sans problème
with open(config_path) as configFile:
    config = json.load(configFile)

def get_db_connection():
    conn = sqlite3.connect('db/app.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_user(name, email,whatsapp,gotify,telegram):
  conn = get_db_connection()
  conn.execute('INSERT INTO users (name ,email ,whatsapp ,gotify,telegram ) VALUES (?,?,?,?,?)',(name, email,whatsapp,gotify,telegram))
  conn.commit()
  conn.close()
  
def list_user():
  conn = get_db_connection()
  results=conn.execute('SELECT * FROM users').fetchall()
  conn.close()  
  return results
def list_db():
  conn = get_db_connection()
  results=conn.execute('SELECT * FROM birthday').fetchall()
  conn.close()
  return results

def list_db_date(search_data):
  conn = get_db_connection()
  

 #print("Variable search_data dans la fonction list_db_date =",search_data)
  results=conn.execute('SELECT * FROM birthday WHERE birthday_day_month = ?',(search_data,)).fetchall()
  conn.close()
  return results
def list_db_googleid_for_user(search_data):
  conn = get_db_connection()
  results=conn.execute('SELECT birthday.googleid FROM birthday JOIN users_birthday ON birthday.googleid = users_birthday.birthday_id WHERE users_birthday.user_id = ?;',(search_data,)).fetchall()
  conn.close()
  tmp_list=[] 
  for z in results:
      tmp_list.append(z[0] )  
  
  return tmp_list
def get_birthday():
  now = date.today()
  
  list_date=(0,1,2,3,4,5,6,7)
  list_notify=[]
  for search_date in  list_date:
    search=(now + timedelta(days=search_date)).strftime("%d-%m")
    results=list_db_date(search)
    for result in results:
      #print(result["name"])
      #print(result["date"])           
      end_date=datetime.strptime(result["date"],"%d-%m-%Y")
      delta=relativedelta.relativedelta(now,end_date)
      #print(delta.years+1)
      if search_date== 0:
        list_notify.append("\nAujourd'hui : {} fête ses {} ans".format(result["name"],str(delta.years)))
      else:
        list_notify.append("\nA venir : {} fêtera ses {} ans dans {} jour(s). ({})".format(result["name"],str(delta.years+1),str(search_date),str(result["birthday_day_month"])))
  text_notify = "Bonjour, pense à ces anniversaires :"
  if len(list_notify) > 0:
    for x in list_notify:
        text_notify += x
    return text_notify
  else:
      return "STOP"
def get_birthday_user(user):
  now = date.today()
 #print("Variable now = ?",now)
  list_date=(0,3,7,6,8,14)
  list_notify=[]
  user_googleid_list=list_db_googleid_for_user(user)
  for search_date in  list_date:
    search=(now + timedelta(days=search_date)).strftime("%d-%m")
    print("Variable search = ?",search)
    results=list_db_date(search)
    print("Variable result = ?",results)
    for result in results:
      
      end_date=datetime.strptime(result["date"],"%d-%m-%Y")
      delta=relativedelta.relativedelta(now,end_date)

      print(result["googleid"])
      if result["googleid"] in user_googleid_list:
        if search_date== 0:
          list_notify.append("\nAujourd'hui : {} fête ses {} ans".format(result["name"],str(delta.years)))
        else:
          list_notify.append("\nA venir : {} fêtera ses {} ans dans {} jour(s). ({})".format(result["name"],str(delta.years+1),str(search_date),str(result["birthday_day_month"])))
  text_notify = "Bonjour, pense à ces anniversaires :"
  if len(list_notify) > 0:
    for x in list_notify:
        text_notify += x
    text_notify += "\n Message envoyé automatiquement.V2S"
    return text_notify
  else:
      return "STOP"

def notify_users():

  
  
  users=list_user()
  for user in users:
    text_notify=get_birthday_user(user["id"] )
    if text_notify != "STOP":
        print("text_notify =",text_notify," pour l'utilisateur =",user)

        
        if user["email"] != "":
          send_email(text_notify,user["email"])

        if user["whatsapp"] != "":
          send_whatsapp(text_notify,user["whatsapp"]) 
        if user["gotify"] != "":
          send_gotify(text_notify,user["gotify"]) 
    else:
       print("Rien à envoyer")

def notify_users_test():
  conn = get_db_connection()
  user=conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
  conn.close()    


  text_notify=get_birthday_user(user["id"] )
  if text_notify != "STOP":
      print("text_notify =",text_notify," pour l'utilisateur =",user["name"] )

      
      if user["email"] != "":
        send_email(text_notify,user["email"])

      if user["whatsapp"] != "":
        send_whatsapp(text_notify,user["whatsapp"]) 
      if user["gotify"] != "":
        send_gotify(text_notify,user["gotify"]) 
  else:
      print("Rien à envoyer")

def send_email(body,recipients):
    msg = MIMEText(body)
    msg['Subject'] = "Rappel des anniversaires"
    msg['From'] = config['email_sender']
    msg['To'] = recipients
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(config['email_sender'], config['email_password'])
       smtp_server.sendmail(config['email_sender'], recipients, msg.as_string())
       smtp_server.quit()
    
def send_whatsapp(body,recipients):
    """
    Send message to chat_id.
    :param chat_id: Phone number + "@c.us" suffix - 1231231231@c.us
    :param text: Message for the recipient
    """
    # Send a text back via WhatsApp HTTP API
    response = requests.post(
        "http://192.168.80.151:3216/api/sendText",
        json={
            "chatId": recipients,
            "text": body,
            "session": "default",
        },
    )
    response.raise_for_status()


def send_gotify(text,url):
        requests.post(url, json={
        "message": text,
        "priority": 2,
        "title": "Anniversaire"
        })