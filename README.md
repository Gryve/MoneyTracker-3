# 💎 MoneyTracker 3.0

**Un tracker moderno di entrate e uscite, con un'interfaccia dark curata nei dettagli.**

MoneyTracker è un'applicazione desktop per tenere sotto controllo le proprie finanze personali: registra entrate e spese, le visualizza in calendario, definisce budget annuali per categoria e mostra l'andamento del saldo — tutto **localmente**, senza account né servizi cloud.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![UI](https://img.shields.io/badge/UI-CustomTkinter-4D8BFF.svg)](https://github.com/TomSchimansky/CustomTkinter)
[![Database](https://img.shields.io/badge/DB-SQLite-lightgrey.svg)](https://www.sqlite.org/)

---

## Indice

- [Funzionalità](#funzionalità)
- [Avvio rapido](#avvio-rapido)
- [Build dell'eseguibile Windows](#build-delleseguibile-windows)
- [Struttura del progetto](#struttura-del-progetto)
- [Dati e privacy](#dati-e-privacy)
- [Tech stack](#tech-stack)

---

## ✨ Funzionalità

### 📊 Dashboard
- Card riepilogative di **entrate**, **spese** e **saldo** del mese
- Grafici a torta della ripartizione per categoria (spese ed entrate)
- Riepilogo del budget annuale con barra di avanzamento

### 📝 Transazioni
- Elenco delle transazioni filtrato per mese, con selettore rapido
- Aggiunta, modifica e cancellazione in un click
- Azione rapida "Add Transaction" sempre visibile nella sidebar

### 📅 Calendario
- Griglia mensile con indicatori giornalieri di entrate (+) e spese (−)
- Click su un giorno per aprire il pannello di dettaglio con le sue transazioni
- Evidenziazione del giorno corrente e del giorno selezionato

### 🎯 Budget
- **Budget annuali per categoria di spesa**, editabili inline direttamente dalla lista
- Barre di avanzamento a colori: blu → arancione → rosso quando si supera il limite
- Stato "rimasto / superato" calcolato in tempo reale

### 📆 Year Overview
- Riepilogo dei 12 mesi dell'anno: entrate, spese e saldo per ogni mese
- Navigazione tra gli anni con un solo click

### E altro ancora
- Categorie personalizzabili (con emoji), con set di default già pronto all'uso
- **Saldo storico** sempre visibile in fondo alla sidebar
- Tema dark coerente su tutta l'app, con palette e tipografia dedicate

---

## 🚀 Avvio rapido

### Requisiti
- Python **3.10+** (testato con 3.14)
- Tkinter (incluso nelle installazioni standard di Python)

### Installazione ed esecuzione

```bash
# Clona il repository
git clone https://github.com/<tuo-username>/MoneyTracker.git
cd MoneyTracker

# Crea un ambiente virtuale (consigliato)
python -m venv .venv

# Attiva l'ambiente virtuale
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux

# Installa le dipendenze
pip install customtkinter

# Avvia l'applicazione
python main.py
```

Al primo avvio viene creato automaticamente il database locale in `data/moneytracker.db`.

---

## 📦 Build dell'eseguibile Windows

Il progetto include già la configurazione PyInstaller (`MoneyTracker3.spec`):

```bash
pip install pyinstaller
pyinstaller MoneyTracker3.spec
```

L'eseguibile standalone viene generato in `dist/MoneyTracker3.exe`. Il database viene creato automaticamente accanto al file `.exe` al primo avvio: per la distribuzione basta condividere un unico eseguibile.

---

## 🗂 Struttura del progetto

| File | Descrizione |
| --- | --- |
| [`main.py`](main.py) | Punto di ingresso dell'applicazione |
| [`app.py`](app.py) | Finestra principale e viste (dashboard, transazioni, calendario, budget, anno) |
| [`data_manager.py`](data_manager.py) | Layer di persistenza: database SQLite, query e migrazione dai vecchi file JSON |
| [`theme.py`](theme.py) | Tema dark: palette colori, font e dimensioni |
| [`ui_components.py`](ui_components.py) | Widget riutilizzabili (card, righe transazione, grafici a torta…) |
| [`ui_dialogs.py`](ui_dialogs.py) | Dialogo di aggiunta/modifica transazioni |
| [`ui_categories.py`](ui_categories.py) | Dialogo di gestione categorie |

---

## 💾 Dati e privacy

- Tutti i dati sono salvati **localmente** in `data/moneytracker.db` (SQLite), creato automaticamente al primo avvio.
- Se nella cartella `data/` sono presenti file JSON legacy (`transactions.json`, `categories.json`), vengono importati nel database una sola volta, al primo avvio.
- Nessuna connessione di rete: i tuoi dati finanziari non lasciano mai il tuo computer.

---

## 🛠 Tech stack

| Tecnologia | Ruolo |
| --- | --- |
| **Python 3** | Logica dell'applicazione |
| **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** | Interfaccia grafica moderna in tema dark |
| **SQLite** (stdlib) | Persistenza locale, zero configurazione |
| **PyInstaller** | Packaging in eseguibile standalone `.exe` |

---

## 📸 Screenshots

> Le immagini delle varie viste verranno aggiunte nella cartella `assets/`.
