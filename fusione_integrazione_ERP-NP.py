import socket
import tkinter as tk
from tkinter import messagebox
import json
import logging
import time
import stomp  # pip install stomp.py

from datetime import datetime
from pathlib import Path

# ====== LETTURA CONFIG ======
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

BROKER_HOST = CONFIG["broker"]["host"]
BROKER_PORT = CONFIG["broker"]["port"]
BROKER_USER = CONFIG["broker"]["user"]
BROKER_PASS = CONFIG["broker"]["password"]
BROKER_QUEUE = CONFIG["broker"]["queue"]

# Carica template JSON da file esterno
with open(CONFIG["json_template"], "r", encoding="utf-8") as f:
    MY_JSON3_TEMPLATE = f.read()

# ====== LOGGING ======
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GUI-ERP-NP")

class MyListener(stomp.ConnectionListener):
    def on_error(self, frame):
        logger.error('Errore broker: %s', frame.body)
    def on_message(self, frame):
        logger.info('Messaggio ricevuto: %s', frame.body)

def get_today_iso():
    """Restituisce la data odierna in formato ISO 'YYYY-MM-DDT00:00:00Z'."""
    today = datetime.now()
    return today.strftime("%Y-%m-%dT00:00:00Z")

def _to_iso_midnight(date_str: str) -> str:
    """Converte 'YYYY-MM-DD' in 'YYYY-MM-DDT00:00:00Z'. Se vuoto o non valido, ritorna ''."""
    if not date_str:
        return ""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
        return d.strftime("%Y-%m-%dT00:00:00Z")
    except ValueError:
        return ""

def pulisci_log():
    txt_log.delete("1.0", tk.END)

def limita_ordine(s):
    return len(s) <= 8 and not any(ch.isspace() for ch in s)

def limita_cliente(s):
    return len(s) <= 20

def limita_descrizione(s):
    return len(s) <= 20

def build_payload_for_order(order_id: str, cliente: str = "", descrizione: str = "", part_number: str = "", frqduedate: str = "", frqstdate: str = "") -> str:
    payload = json.loads(MY_JSON3_TEMPLATE)
    row0 = payload["rows"][0]

    def _replace_ordine(columns_list):
        for c in columns_list:
            if isinstance(c, dict) and c.get("name") == "ordine":
                c["value"] = order_id
            if isinstance(c, dict) and c.get("name") == "fobject":
                c["value"] = order_id

    def _replace_cliente(columns_list):
        for c in columns_list:
            if isinstance(c, dict) and c.get("name") == "cliente":
                c["value"] = cliente

    def _replace_descrizione(columns_list):
        for c in columns_list:
            if isinstance(c, dict) and c.get("name") == "descrizione":
                c["value"] = descrizione

    def _replace_part_number(columns_list):
        for c in columns_list:
            if isinstance(c, dict) and c.get("name") == "part_number":
                c["value"] = part_number

    def _replace_frqduedate(columns_list):
        for c in columns_list:
            if isinstance(c, dict) and c.get("name") == "frqduedate" and frqduedate:
                c["value"] = frqduedate

    def _replace_frqstdate(columns_list):
        for c in columns_list:
            if isinstance(c, dict) and c.get("name") == "frqstdate" and frqstdate:
                c["value"] = frqstdate

    for r in row0.get("materiali_ordini", {}).get("rows", []):
        _replace_ordine(r.get("columns", []))
        _replace_cliente(r.get("columns", []))
        _replace_descrizione(r.get("columns", []))
        _replace_part_number(r.get("columns", []))
        _replace_frqduedate(r.get("columns", []))  # non farà nulla se il campo non esiste
        _replace_frqstdate(r.get("columns", []))  # non farà nulla se il campo non esiste


    for r in row0.get("operazioni", {}).get("rows", []):
        _replace_ordine(r.get("columns", []))
        _replace_cliente(r.get("columns", []))
        _replace_descrizione(r.get("columns", []))
        _replace_part_number(r.get("columns", []))
        _replace_frqduedate(r.get("columns", []))  # non farà nulla se il campo non esiste
        _replace_frqstdate(r.get("columns", []))  # non farà nulla se il campo non esiste


    ordini_cols = row0.get("ordini", {}).get("columns", [])
    _replace_ordine(ordini_cols)
    _replace_cliente(ordini_cols)
    _replace_descrizione(ordini_cols)
    _replace_part_number(ordini_cols)
    _replace_frqduedate(ordini_cols)
    _replace_frqstdate(ordini_cols)

    for c in row0.get("ordini", {}).get("columns", []):
        if c.get("name") == "descrizione":
            c["value"] = descrizione if descrizione else f"Ordine {order_id}"
        if c.get("name") == "cliente":  # nuovo campo cliente
            c["value"] = cliente
        if c.get("name") == "part_number":
            c["value"] = part_number
        if c.get("name") == "frqduedate" and frqduedate:
            c["value"] = frqduedate
        if c.get("name") == "frqstdate" and frqstdate:
            c["value"] = frqstdate

    return json.dumps(payload, ensure_ascii=False)

def _fmt_exc(e: Exception) -> str:
    # tipo: messaggio (se presente), altrimenti repr
    cls = e.__class__.__name__
    msg = str(e).strip()
    if not msg:
        msg = repr(e)
    # se c’è una cause/chained exception, prova ad aggiungerla
    cause = getattr(e, "__cause__", None) or getattr(e, "__context__", None)
    if cause:
        c_cls = cause.__class__.__name__
        c_msg = str(cause).strip() or repr(cause)
        return f"{cls}: {msg}\nCausa: {c_cls}: {c_msg}"
    return f"{cls}: {msg}"

def send_to_activemq(messages):
    conn = stomp.Connection12([(BROKER_HOST, BROKER_PORT)], auto_content_length=False)
    try:
        try:
            conn.connect(BROKER_USER, BROKER_PASS, wait=True)
        except socket.gaierror as e:
            raise RuntimeError(f"Host non risolvibile ({BROKER_HOST}). {_fmt_exc(e)}") from e
        except ConnectionRefusedError as e:
            raise RuntimeError(f"Connessione rifiutata da {BROKER_HOST}:{BROKER_PORT}. {_fmt_exc(e)}") from e
        except TimeoutError as e:
            raise RuntimeError(f"Timeout durante la connessione a {BROKER_HOST}:{BROKER_PORT}. {_fmt_exc(e)}") from e
        except stomp.exception.ConnectFailedException as e:
            raise RuntimeError(f"Autenticazione fallita su {BROKER_HOST}:{BROKER_PORT}. {_fmt_exc(e)}") from e
        except Exception as e:
            raise RuntimeError(
                f"Connessione a ActiveMQ fallita (host={BROKER_HOST}, port={BROKER_PORT}, queue='{BROKER_QUEUE}'). {_fmt_exc(e)}"
            ) from e

        for body in messages:
            try:
                conn.send(
                    body=body,
                    destination=BROKER_QUEUE,
                    content_type='application/json',
                    headers={'persistent': 'true'}
                )
                time.sleep(0.02)
            except Exception as e:
                # se fallisce l’invio di un singolo messaggio, dai contesto e rilancia
                raise RuntimeError(f"Invio messaggio alla queue '{BROKER_QUEUE}' non riuscito. {_fmt_exc(e)}") from e
    finally:
        try:
            conn.disconnect()
        except Exception:
            # ignora errori in disconnect: non vogliamo sovrascrivere l’errore principale
            pass

# ====== GUI ======
root = tk.Tk()
root.title("Invio ordini a ActiveMQ (ERP-NP)")

# Variabile globale per payloads generati
payloads_generati = []

# Input prefisso e numero
tk.Label(root, text="Prefisso ordine (es. ODP-CUTT - max 8) ").grid(row=0, column=0, padx=6, pady=6, sticky="e")

vcmd = (root.register(limita_ordine), "%P")

entry_prefix = tk.Entry(root, width=24, validate="key", validatecommand=vcmd)
entry_prefix.grid(row=0, column=1, padx=6, pady=6)
entry_prefix.insert(0, "ODP-CUTT")

# Campo Cliente
tk.Label(root, text="Cliente (max 20)").grid(row=0, column=2, padx=6, pady=6, sticky="e")

vcmd_cliente = (root.register(limita_cliente), "%P")
entry_cliente = tk.Entry(root, width=24, validate="key", validatecommand=vcmd_cliente)
entry_cliente.grid(row=0, column=3, padx=6, pady=6)

# Campo Descrizione
tk.Label(root, text="Descrizione (max 20)").grid(row=0, column=4, padx=6, pady=6, sticky="e")

vcmd_descrizione = (root.register(limita_descrizione), "%P")
entry_descrizione = tk.Entry(root, width=24, validate="key", validatecommand=vcmd_descrizione)
entry_descrizione.grid(row=0, column=5, padx=6, pady=6)

tk.Label(root, text="Quantità ordini (N)").grid(row=0, column=6, padx=6, pady=6, sticky="e")
entry_n = tk.Entry(root, width=8)
entry_n.grid(row=0, column=7, padx=6, pady=6)
entry_n.insert(0, "3")

# Output log
tk.Label(root, text="Log esecuzione").grid(row=1, column=0, padx=6, pady=6, sticky="ne")
txt_log = tk.Text(root, width=80, height=16)
txt_log.grid(row=1, column=1, columnspan=3, padx=6, pady=6, sticky="w")

def log_line(s: str):
    txt_log.insert(tk.END, s + "\n")
    txt_log.see(tk.END)
    root.update_idletasks()

def genera_ordini():
    global payloads_generati
    prefix = entry_prefix.get().strip()
    cliente = entry_cliente.get().strip()
    descrizione = entry_descrizione.get().strip()

    part_number = CONFIG.get("part_number", CONFIG.get("part_number", ""))
    prefix = entry_prefix.get().strip()
    if any(ch.isspace() for ch in prefix):
        messagebox.showerror("Errore", "Il campo ordine non può contenere spazi.")
        return

    try:
        n = int(entry_n.get())
        if n < 1:
            raise ValueError()
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un numero intero N >= 1")
        return

    ordini = [f"{prefix}_{i:02d}" for i in range(1, n + 1)]
    datetimeNow = get_today_iso()
    payloads_generati = [build_payload_for_order(oid, cliente, descrizione, part_number, datetimeNow, datetimeNow ) for oid in ordini]

    log_line(f"Generati {len(ordini)} ordini:")
    for oid in ordini:
        log_line(f" - {oid}")
    log_line(f"Cliente : {cliente}")
    log_line(f"Descrizione: {descrizione}")
    log_line(f"Articolo   : {part_number}")

def invia_ordini():
    global payloads_generati
    if not payloads_generati:
        messagebox.showwarning("Attenzione", "Prima genera gli ordini, poi invia.")
        return
    try:
        send_to_activemq(payloads_generati)
        log_line(f"✅ Inviati {len(payloads_generati)} messaggi alla queue '{BROKER_QUEUE}' su {BROKER_HOST}:{BROKER_PORT}")
        payloads_generati = []  # svuota dopo invio
    except Exception as e:
        logger.exception("Errore invio")
        msg = _fmt_exc(e)
        messagebox.showerror("Errore invio a ActiveMQ", msg)
        log_line(f"❌ Errore invio: {msg}")

# Pulsanti separati
btn_genera = tk.Button(root, text="Genera ordini", command=genera_ordini)
btn_genera.grid(row=2, column=0, columnspan=2, pady=10)

btn_invia = tk.Button(root, text="Invia ordini", command=invia_ordini)
btn_invia.grid(row=2, column=1, columnspan=2, pady=10)

btn_pulisci = tk.Button(root, text="Pulisci log", command=pulisci_log)
btn_pulisci.grid(row=2, column=3, columnspan=4, pady=10)

# ====== VERSIONE IN BASSO A DESTRA ======
VERSION = "v1.1.0"  # <-- cambia qui la versione dell’app
lbl_version = tk.Label(root, text=f"Versione {VERSION}", font=("Arial", 8), fg="gray")
lbl_version.grid(row=99, column=7, padx=6, pady=4, sticky="se")  # posizionato in basso a destra

root.mainloop()
