import re
import matplotlib.pyplot as plt
import os
import argparse
import imageio.v2 as imageio

def parse_holds(holds_text, height, width):
    """
    Parsea il testo 'holds.txt' contenente fatti di tipo:
        holds(posizione_tessera(Tess, Pos), T).
    e li organizza in un dizionario time_states, dove
    time_states[t] e' una griglia di dimensioni (height x width).
    """
    # Nuovo pattern: cattura (tessera, pos, tempo)
    # holds(posizione_tessera(5,1,1),0)
    pattern = r"holds\(posizione_tessera\((\d+),\s*(\d+)\),\s*(\d+)\)"
    matches = re.findall(pattern, holds_text)

    time_states = {}
    for tile_str, pos_str, t_str in matches:
        tile = int(tile_str)
        pos = int(pos_str)
        t = int(t_str)

        # Converte l'indice lineare 'pos' in (row, col)
        row = pos // width
        col = pos % width

        # Inizializza la matrice se non esiste per il tempo T
        if t not in time_states:
            time_states[t] = [[0]*width for _ in range(height)]

        # Assegna la tessera nella cella corrispondente
        time_states[t][row][col] = tile

    return time_states

def draw_grid(state, t, height, width):
    """
    Disegna la griglia per lo stato 'state' (matrix di dimensioni (height x width))
    e la salva come immagine.
    """
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_title(f"Tempo {t}")
    ax.axis('off')

    # Se tile == 0, visualizziamo una cella vuota
    table_data = [[cell if cell != 0 else '' for cell in row] for row in state]

    table = ax.table(cellText=table_data, loc='center', cellLoc='center', edges='closed')
    table.scale(1, 4)

    # Format delle celle
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('black')
        cell.set_linewidth(2)
        cell.set_height(1/height)
        cell.set_text_props(fontsize=16, weight='bold', ha='center', va='center')

    output_path = f"output_images/puzzle_time_{t}.png"
    plt.savefig(output_path)
    plt.close()

def print_grid(state, t):
    """
    Stampa a schermo la griglia di uno stato
    (sostituendo tile=0 con '0' per evidenziare lo spazio vuoto).
    """
    print(f"Tempo {t}:")
    for row in state:
        row_repr = [str(cell) if cell != 0 else '0' for cell in row]
        print('[' + ', '.join(row_repr) + ']')
    print()

def main():
    parser = argparse.ArgumentParser(description="Crea immagini e video di una griglia.")
    parser.add_argument('-s', action='store_true', help='Stampa la griglia a schermo per ogni mossa (invece di generare immagini).')
    parser.add_argument('-a', '--altezza', type=int, default=3, help='Altezza della griglia.')
    parser.add_argument('-l', '--larghezza', type=int, default=3, help='Larghezza della griglia.')
    args = parser.parse_args()

    # Legge il file 'holds.txt'
    with open('holds.txt', 'r') as f:
        holds_text = f.read()

    # Parsea e ricostruisce gli stati
    time_states = parse_holds(holds_text, args.altezza, args.larghezza)

    # Crea una cartella per le immagini (se non esiste)
    output_dir = 'output_images'
    os.makedirs(output_dir, exist_ok=True)

    # Per ogni tempo in ordine crescente, stampiamo/disegniamo
    for t in sorted(time_states.keys()):
        state = time_states[t]
        if args.s:
            # Stampa in console
            print_grid(state, t)
        else:
            # Disegna e salva come PNG
            draw_grid(state, t, args.altezza, args.larghezza)

    # Se non stiamo stampando, creiamo il video
    if not args.s:
        print("Immagini generate con successo.")

        images = []
        for t in sorted(time_states.keys()):
            image_path = f"{output_dir}/puzzle_time_{t}.png"
            images.append(imageio.imread(image_path))
        imageio.mimsave('output_images/puzzle_evolution.mp4', images, fps=1, format='ffmpeg')
        print("Video generato con successo.")

if __name__ == "__main__":
    main()
