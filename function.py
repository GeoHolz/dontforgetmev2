import os.path
import sqlite3
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import smtplib
from email.mime.text import MIMEText
import requests
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
# Basic configuration settings (user replaceable)
configFile = open('config/configGH.json')
config = json.load(configFile)
birthday_calendars = config['birthday_calendars'] # Google Calendar IDs

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/contacts.readonly"]


def connect_google_api():
  """Shows basic usage of the People API.
  Prints the name of the first 10 connections.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("creds/token.json"):
    creds = Credentials.from_authorized_user_file("creds/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "creds/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("creds/token.json", "w") as token:
      token.write(creds.to_json())
    
  return creds

def get_db_connection():
    conn = sqlite3.connect('db/app.db')
    conn.row_factory = sqlite3.Row
    return conn

def add_user(name, email,whatsapp,gotify,telegram):
  conn = get_db_connection()
  conn.execute('INSERT INTO users (name ,email ,whatsapp ,gotify,telegram ) VALUES (?,?,?,?,?)',(name, email,whatsapp,gotify,telegram))
  conn.commit()
  conn.close()

def edit_user(name, email,whatsapp,gotify,telegram):
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
  
  if search_data[0] == "0":
     search_data=search_data[1:] 
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
  list_date=(0,3,7,14)
  list_notify=[]
  user_googleid_list=list_db_googleid_for_user(user)
  for search_date in  list_date:
    search=(now + timedelta(days=search_date)).strftime("%d-%m").replace("-0","-")
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
    text_notify += "\n Message envoyé automatiquement."
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

def sync_db():
  creds=connect_google_api()
  conn = get_db_connection()
  try:
    service = build("people", "v1", credentials=creds)

    # Call the People API
    results = (
        service.people()
        .connections()
        .list(
            resourceName="people/me",
            pageSize=2000,
            personFields="names,birthdays",
        )
        .execute()
    )
    connections = results.get("connections", [])
    for person in connections:
      names = person.get("names", [])
      
      birthdays = person.get("birthdays", [])
      if birthdays:
        birthday_day_month = str(birthdays[0].get("date")["day"])+ "-" + str(birthdays[0].get("date")["month"])
        birthday=str(birthdays[0].get("date")["day"])+ "-" + str(birthdays[0].get("date")["month"])  + "-" + str(birthdays[0].get("date")["year"]) 
        id=names[0].get("metadata")["source"]["id"]
        name = names[0].get("displayName")
        conn.execute('INSERT OR IGNORE INTO birthday (name ,date,birthday_day_month,googleid ) VALUES (?,?,?,?)',(name, birthday,birthday_day_month,id))

  except HttpError as err:
    print(err)
  conn.commit()
  print("SyncDB Google OK")
  conn.close()

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