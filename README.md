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

## Oppsett og Installasjon

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
