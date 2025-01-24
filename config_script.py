import pandas as pd
import matplotlib.pyplot as plt

# Definisci il nome del file CSV
file_csv = 'strategia.csv'  # Sostituisci con il percorso del tuo file CSV

# Leggi il CSV utilizzando il separatore punto e virgola
df = pd.read_csv(file_csv, sep=';')

# Funzione per convertire i valori della colonna 'time' in float
def convert_time(time_str):
    if isinstance(time_str, str):
        # Rimuovi eventuali caratteri non numerici come 's'
        time_str = time_str.replace('s', '').replace(',', '.')
    try:
        return float(time_str)
    except ValueError:
        return None  # O gestisci diversamente se necessario

# Applica la funzione di conversione alla colonna 'time'
df['time'] = df['time'].apply(convert_time)

# Rimuovi eventuali righe con valori NaN dopo la conversione
df = df.dropna(subset=['time'])

# Ordina i dati per una migliore visualizzazione (opzionale)
df = df.sort_values(by='time', ascending=False)

# Crea il grafico a barre
plt.figure(figsize=(10, 6))
plt.bar(df['configuration'], df['time'], color='skyblue')

# Aggiungi titoli e etichette
plt.title('Tempi per Configurazione')
plt.xlabel('Configurazione')
plt.ylabel('Tempo (secondi)')

# Ruota le etichette dell'asse x se necessario
plt.xticks(rotation=45, ha='right')

# Aggiungi etichette dei valori sopra le barre
for index, value in enumerate(df['time']):
    plt.text(index, value, f'{value}', ha='center', va='bottom')

# Migliora il layout
plt.tight_layout()

# Mostra il grafico
plt.savefig('ottimizzazione.png')
