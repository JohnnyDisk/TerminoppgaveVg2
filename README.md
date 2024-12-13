# Nettbutikk Webapplikasjon

En fullstendig nettbutikkløsning bygget med Flask, med funksjoner for brukerautentisering, produktkatalog, handlekurv og betalingssystem. Applikasjonen støtter både gjestekjøp og innloggede brukere.

## Funksjoner

### Brukerautentisering
- Sikker brukerregistrering og innloggingssystem
- Passordhashing med SHA-256
- Øktadministrasjon med 7-dagers varighet
- Mulighet for gjestekjøp

### Produkthåndtering
- Dynamisk produktkatalog
- Detaljerte produktsider med bilder
- Produktinformasjon inkludert navn og pris
- Produktbildeintegrasjon

### Handlekurv
- Legg til/fjern produkter
- Mengdehåndtering
- Vedvarende handlekurv for både gjester og innloggede brukere
- Sanntids totalberegning
- Databasebasert handlekurv for innloggede brukere
- Øktbasert handlekurv for gjester

### Betalingssystem
- Sikker utsjekkingsprosess
- Ordresammendrag
- Tømming av handlekurv etter vellykket kjøp
- Beregning av totalpris

## Teknisk Stack

- **Backend**: Python Flask
- **Database**: SQLite3
- **Frontend**: HTML, CSS
- **Øktadministrasjon**: Flask Session
- **Sikkerhet**: SHA-256 passordhashing

## Prosjektstruktur

```
TerminoppgaveVg2/
│
├── app.py                 # Hoved Flask-applikasjon
├── cart.db               # SQLite-database
│
├── static/               # Statiske filer
│   ├── styles.css        # CSS-stiler
│   └── images/           # Produktbilder
│       └── product_*.jpg # Produktbilder
│
├── templates/            # HTML-maler
│   ├── base.html         # Basemalen
│   ├── home.html         # Hjemmeside
│   ├── login.html        # Innloggingsside
│   ├── signup.html       # Registreringsside
│   ├── product.html      # Produktdetaljer
│   ├── cart.html         # Handlekurv
│   └── checkout.html     # Utsjekkingsside
│
└── README.md             # Prosjektdokumentasjon
```

## Databaseskjema

### Brukertabell
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
```

### Handlekurvtabell
```sql
CREATE TABLE cart (
    product_id INTEGER,
    user_id INTEGER,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (product_id, user_id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```

## Lokal Oppsett og Installasjon

1. Sørg for at Python er installert på systemet ditt
2. Klon prosjektet
3. Installer nødvendige avhengigheter:
   ```bash
   pip install flask
   ```
4. Kjør applikasjonen:
   ```bash
   python app.py
   ```
5. Åpne applikasjonen i nettleseren på `http://localhost:5000`

## Produksjonsoppsett og Drift

### Server Oppsett (Ubuntu/Debian)

1. Oppdater systemet:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. Installer nødvendig programvare:
   ```bash
   sudo apt install python3 python3-pip nginx supervisor -y
   ```

3. Installer Python-avhengigheter:
   ```bash
   pip3 install flask gunicorn
   ```

### Nginx Konfigurasjon

1. Opprett Nginx konfigurasjonsfil:
   ```bash
   sudo nano /etc/nginx/sites-available/nettbutikk
   ```

2. Legg til følgende konfigurasjon:
   ```nginx
   server {
       listen 80;
       server_name din-domene.no;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /static {
           alias /path/to/your/static/folder;
       }
   }
   ```

3. Aktiver konfigurasjonen:
   ```bash
   sudo ln -s /etc/nginx/sites-available/nettbutikk /etc/nginx/sites-enabled
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Supervisor Konfigurasjon

1. Opprett Supervisor konfigurasjonsfil:
   ```bash
   sudo nano /etc/supervisor/conf.d/nettbutikk.conf
   ```

2. Legg til følgende konfigurasjon:
   ```ini
   [program:nettbutikk]
   directory=/path/to/your/app
   command=gunicorn app:app -w 4 -b 127.0.0.1:8000
   user=www-data
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/nettbutikk/err.log
   stdout_logfile=/var/log/nettbutikk/out.log
   ```

3. Opprett loggmapper og start tjenesten:
   ```bash
   sudo mkdir -p /var/log/nettbutikk
   sudo supervisorctl reread
   sudo supervisorctl update
   ```

### SSL/HTTPS Oppsett

1. Installer Certbot:
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   ```

2. Generer SSL-sertifikat:
   ```bash
   sudo certbot --nginx -d din-domene.no
   ```

### Sikkerhetsoppsett

1. Konfigurer brannmur:
   ```bash
   sudo ufw allow 'Nginx Full'
   sudo ufw allow OpenSSH
   sudo ufw enable
   ```

2. Sikre Nginx-konfigurasjon:
   ```nginx
   # Legg til i server-blokken
   add_header X-Frame-Options "SAMEORIGIN";
   add_header X-XSS-Protection "1; mode=block";
   add_header X-Content-Type-Options "nosniff";
   ```

### Backup og Vedlikehold

1. Sett opp automatisk database backup:
   ```bash
   # Opprett backup-script
   nano /path/to/backup.sh
   ```
   ```bash
   #!/bin/bash
   DATE=$(date +%Y%m%d)
   BACKUP_DIR="/path/to/backups"
   
   # Database backup
   cp /path/to/cart.db "$BACKUP_DIR/cart_$DATE.db"
   
   # Behold kun siste 7 dager
   find $BACKUP_DIR -name "cart_*.db" -mtime +7 -delete
   ```

2. Legg til i crontab:
   ```bash
   0 3 * * * /path/to/backup.sh
   ```

### Overvåking

1. Installer og konfigurer Prometheus og Grafana for overvåking:
   ```bash
   sudo apt install prometheus grafana -y
   ```

2. Legg til Flask-metrics:
   ```python
   from prometheus_flask_exporter import PrometheusMetrics
   metrics = PrometheusMetrics(app)
   ```

### Vedlikeholdsrutiner

1. Daglig:
   - Sjekk loggfiler for feil
   - Overvåk diskplass
   - Verifiser backup

2. Ukentlig:
   - Oppdater systemet
   - Sjekk sikkerhetsoppdateringer
   - Analyser ytelsesmetrikker

3. Månedlig:
   - Gjennomgå sikkerhetsinnstillinger
   - Test gjenoppretting av backup
   - Optimaliser database

## Sikkerhetsfunksjoner

- Passordhashing med SHA-256
- Øktbasert autentisering
- Beskyttelse mot SQL-injeksjon ved bruk av parametriserte spørringer
- CSRF-beskyttelse gjennom Flask sin øktadministrasjon
- Inputvalidering for brukerregistrering

## Brukerveiledning

### Registrering
- Brukernavn må være minst 3 tegn langt
- Passord må være mer enn 6 tegn langt
- Passordene må stemme overens ved bekreftelse

### Handling
1. Bla gjennom produkter på hjemmesiden
2. Klikk på produkter for å se detaljer
3. Legg produkter i handlekurven med ønsket antall
4. Se gjennom handlekurvens innhold
5. Gå videre til utsjekking

### Handlekurvadministrasjon
- Legg til produkter med spesifikt antall
- Fjern produkter fra handlekurven
- Se sanntids handlekurvtotal
- Handlekurven bevares i 7 dager

## Utviklingsnotater

- Feilsøkingsmodus er aktivert i utvikling
- Serveren kjører på vert '0.0.0.0' og port 5000
- Gjestehandlekurvdata lagres i økten
- Innloggede brukeres handlekurvdata lagres i SQLite-databasen

## Feilsøking og Vanlige Problemer

### Database Tilkoblingsproblemer
```bash
# Sjekk databaserettigheter
sudo chown www-data:www-data /path/to/cart.db
sudo chmod 664 /path/to/cart.db
```

### Nginx 502 Bad Gateway
1. Sjekk Gunicorn status:
   ```bash
   sudo supervisorctl status nettbutikk
   ```
2. Sjekk loggfiler:
   ```bash
   tail -f /var/log/nettbutikk/err.log
   ```

### Minneproblemer
1. Sjekk minnebruk:
   ```bash
   free -m
   ```
2. Juster Gunicorn workers:
   ```bash
   # Endre i supervisor config
   command=gunicorn app:app -w 2 -b 127.0.0.1:8000
