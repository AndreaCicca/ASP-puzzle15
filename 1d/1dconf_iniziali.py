import json
import os

def convert_to_initial_state_linear(array):
    """
    Converte un array in configurazioni iniziali formattate con indice lineare.
    Esempio di output per un valore 3 alla posizione 5:
        initially(posizione_tessera(3, 5)).
    """
    lines = []
    for i, value in enumerate(array):
        lines.append(f"initially(posizione_tessera({value}, {i})).")
    return "\n".join(lines)

def create_initial_state_files(input_dir):
    """
    Legge i file JSON nelle sottocartelle, converte gli array in configurazioni iniziali
    usando la nuova rappresentazione lineare, e salva ogni configurazione in un file separato.
    """
    valid_dirs = {'3x3', '4x4', '3x4'}
    for subdir in os.listdir(input_dir):
        if subdir not in valid_dirs:
            continue

        subpath = os.path.join(input_dir, subdir)
        if not os.path.isdir(subpath):
            continue

        json_file = os.path.join(subpath, f"{subdir}.json")
        if not os.path.isfile(json_file):
            print(f"File JSON non trovato: {json_file}")
            continue

        # Determina le dimensioni della griglia dalla cartella (ad esempio '3x3' -> 3 righe, 3 colonne)
        # (Se vuoi utilizzare rows e cols per eventuali controlli, ecc. altrimenti non servono più)
        try:
            rows, cols = map(int, subdir.split('x'))
        except ValueError:
            print(f"Formato della cartella non valido: {subdir}. Deve essere del tipo 'NxM'.")
            continue

        # Assicurati che la sottocartella 'initial_state/' esista
        output_dir = os.path.join(subpath, "initial_state")
        os.makedirs(output_dir, exist_ok=True)

        # Leggi il file JSON
        with open(json_file, "r") as file:
            data = json.load(file)

        # Processa ogni array
        for index, array in enumerate(data):
            # Genera la configurazione iniziale in formato "lineare"
            formatted_state = convert_to_initial_state_linear(array)
            
            # Salva su file .pl
            output_file = os.path.join(output_dir, f"state_{index + 1}.pl")
            with open(output_file, "w") as file:
                file.write(formatted_state)
            print(f"Configurazione salvata in: {output_file}")

# Esempio di utilizzo
if __name__ == "__main__":
    input_dir = "."  # Cartella principale (contiene sottocartelle come 3x3, 4x4, ecc.)
    create_initial_state_files(input_dir)
