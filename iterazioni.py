import tkinter as tk
from tkinter import messagebox


def genera_lista():
    testo = entry_stringa.get()
    try:
        numero = int(entry_numero.get())
        if numero < 1:
            raise ValueError("Il numero deve essere positivo")
    except ValueError:
        messagebox.showerror("Errore", "Inserisci un numero intero valido maggiore di 0")
        return

    risultato = [f"{testo}_{i:02d}" for i in range(1, numero + 1)]
    text_output.delete("1.0", tk.END)
    text_output.insert(tk.END, "\n".join(risultato))


# Finestra principale
root = tk.Tk()
root.title("Generatore di stringhe numerate")

# Input stringa
tk.Label(root, text="Stringa:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_stringa = tk.Entry(root, width=20)
entry_stringa.grid(row=0, column=1, padx=5, pady=5)  

# Input numero
tk.Label(root, text="Numero:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_numero = tk.Entry(root, width=20)
entry_numero.grid(row=0, column=3, padx=5, pady=5)

# Input parametro
tk.Label(root, text="Parametro:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_parametro = tk.Entry(root, width=20)
entry_parametro.grid(row=1, column=1, padx=5, pady=5)

# Bottone genera
btn_genera = tk.Button(root, text="Genera Lista", command=genera_lista)
btn_genera.grid(row=2, column=0, columnspan=2, pady=10)

# Output
tk.Label(root, text="Risultato:").grid(row=3, column=0, padx=5, pady=5, sticky="ne")
text_output = tk.Text(root, width=30, height=10)
text_output.grid(row=3, column=1, padx=5, pady=5)

root.mainloop()
