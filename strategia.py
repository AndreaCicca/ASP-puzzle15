#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

# Legge il file CSV con il delimitatore ';'
df = pd.read_csv("strategia.csv", 
                 delimiter=";", 
                 converters={"time": lambda x: float(x.rstrip('s'))})

# Visualizza il DataFrame per controllare che i dati siano stati caricati correttamente
print(df)

# Imposta la dimensione della figura
plt.figure(figsize=(8, 4))

# Crea un grafico a barre: asse x per le configurazioni, asse y per i tempi
plt.bar(df['configuration'], df['time'], color="skyblue")

# Aggiunge etichette agli assi e un titolo
plt.xlabel("Configurazione")
plt.ylabel("Tempo (s)")
plt.title("Ottimizzazione")

# Aggiunge una griglia orizzontale per facilitare la lettura del grafico
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Aggiunge le etichette con il valore di ciascuna barra
for i, tempo in enumerate(df['time']):
    plt.text(i, tempo + 2, f"{tempo:.2f}", ha='center', va='bottom')

# Ottimizza il layout e salva il grafico in un file PNG
plt.tight_layout()
plt.savefig("ottimizzazione.png")

# Mostra il grafico a schermo (opzionale)
plt.show()
