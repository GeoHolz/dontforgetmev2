
# 🎉 Don't Forget Me v2

**Don't Forget Me v2** est une application web légère développée avec **Python Flask** pour **ne plus jamais oublier les anniversaires** de vos contacts !

- 📥 Import des contacts depuis un fichier **CSV Gmail**.
- 🎂 Notification automatique des anniversaires à venir.
- 📧 Notification par **Email**, **WhatsApp** (via API locale) et **Gotify**.
- 🕑 Envoi programmé chaque matin via **APScheduler**.

---

## 🚀 Fonctionnalités principales

- **Interface web** :
  - Ajouter des utilisateurs à notifier.
  - Importer les dates d'anniversaires.
  - Modifier les paramètres de notification.
  - Gérer quels anniversaires chaque utilisateur doit suivre.

- **Notifications automatiques** :
  - Rappel par email, WhatsApp, ou Gotify selon les préférences de chaque utilisateur.
  - Notification des anniversaires du jour et de ceux à venir dans quelques jours.

- **Planification** :
  - Les notifications sont envoyées automatiquement chaque matin grâce à **APScheduler**.

---

## 🛠️ Installation rapide (sans Docker)

1. **Cloner le dépôt** :
   ```bash
   git clone https://github.com/GeoHolz/dontforgetmev2.git
   cd dontforgetmev2
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer l'application** :
   - Remplir le fichier `config/configGH.json` avec votre adresse email et mot de passe d'envoi.
   - Créer un `.env` pour vos clés secrètes (optionnel mais recommandé).

4. **Initialiser la base de données** :
   ```bash
   python initdb.py
   ```

5. **Lancer l'application** :
   ```bash
   python wsgi.py
   ```
   Accéder ensuite à [http://localhost:5000](http://localhost:5000).

---

## 🐳 Utilisation avec Docker

L'image est disponible directement sur **DockerHub** :  
👉 **[GeoHolz/dontforgetme](https://hub.docker.com/r/geoholz/dontforgetme)**

### Lancer rapidement un conteneur :

```bash
docker run -d   -p 8765:8765   --name dontforgetme   geoholz/dontforgetme
```

### Avec volumes pour persister les données :

```bash
docker run -d   -p 8765:8765   --name dontforgetme   -v /path/local/db:/app/db   -v /path/local/config:/app/config   geoholz/dontforgetme
```

- `/path/local/db` : dossier local où sera stockée la base SQLite (`app.db`)
- `/path/local/config` : dossier local pour le fichier `config.json` de configuration

---

## 📝 Format du fichier CSV attendu

Le fichier doit venir de l'export de contacts Gmail.  
Les colonnes suivantes sont utilisées :
- **First Name**
- **Last Name**
- **Birthday** (`YYYY-MM-DD`)

---

## 📲 À propos de l'API WhatsApp locale

Pour envoyer des notifications WhatsApp, utilisez une API locale comme **[WaHA (WhatsApp HTTP API)](https://github.com/devlikeapro/waha)**.

---

## 🔒 Sécurité

- Le mot de passe email et l'URL de l'API WhatsApp doivent être protégés.
- Utiliser des fichiers `.env` ou des montages de volumes sécurisés en production.

---

## 📦 Technologies utilisées

- **Python** 3
- **Flask**
- **SQLite**
- **Pandas**
- **APScheduler**
- **SMTP (smtplib)** pour l'envoi d'emails
- **Gotify API**
- **WhatsApp HTTP API** (via WaHA)

---

## 👨‍💻 Auteur

- [GeoHolz](https://github.com/GeoHolz)

---

## 📜 Licence

Projet disponible sous licence **MIT**.  
Libre à vous de l'utiliser, le modifier et le partager !

---
