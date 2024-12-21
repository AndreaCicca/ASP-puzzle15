import json
import os

def convert_to_initial_state(array, rows, cols):
    """
    Converte un array in configurazioni iniziali formattate, seguendo l'ordine specificato.
    """
    lines = []
    for i, value in enumerate(array):
        row, col = divmod(i, cols)
        row += 1  # Le righe iniziano da 1
        col += 1  # Le colonne iniziano da 1
        lines.append(f"initially(posizione_tessera({value}, {row}, {col})).")
    return "\n".join(lines)

def create_initial_state_files(input_dir):
    """
    Legge i file JSON nelle sottocartelle, converte gli array in configurazioni iniziali
    e salva ogni configurazione in un file separato nella rispettiva cartella 'initial_state'.
    """
    for subdir in os.listdir(input_dir):
        subpath = os.path.join(input_dir, subdir)
        if not os.path.isdir(subpath):
            continue

        json_file = os.path.join(subpath, f"{subdir}.json")
        if not os.path.isfile(json_file):
            print(f"File JSON non trovato: {json_file}")
            continue

        # Determina le dimensioni della griglia dalla cartella (ad esempio '3x3' -> 3 righe, 3 colonne)
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
            formatted_state = convert_to_initial_state(array, rows, cols)
            output_file = os.path.join(output_dir, f"state_{index + 1}.pl")
            with open(output_file, "w") as file:
                file.write(formatted_state)
            print(f"Configurazione salvata in: {output_file}")

# Esempio di utilizzo
if __name__ == "__main__":
    input_dir = "."  # Cartella principale (contiene sottocartelle come 3x3, 4x4, ecc.)
    create_initial_state_files(input_dir)
