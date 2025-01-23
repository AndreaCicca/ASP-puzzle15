import re
import matplotlib.pyplot as plt
import os
import argparse
import imageio.v2 as imageio

def parse_holds(holds_text, height, width):
    pattern = r"holds\(posizione_tessera\((\d+),(\d+),(\d+)\),(\d+)\)"
    matches = re.findall(pattern, holds_text)
    time_states = {}
    for tile, x, y, t in matches:
        t = int(t)
        tile = int(tile)
        x = int(x) - 1  # Le coordinate partono da 1
        y = int(y) - 1
        if t not in time_states:
            time_states[t] = [[0]*width for _ in range(height)]  # Griglia di altezza x larghezza
        time_states[t][x][y] = tile
    return time_states

def draw_grid(state, t, height, width):
    fig, ax = plt.subplots(figsize=(width, height))
    ax.set_title(f"Tempo {t}")
    ax.axis('off')
    table_data = [[cell if cell != 0 else '' for cell in row] for row in state]
    table = ax.table(cellText=table_data, loc='center', cellLoc='center', edges='closed')
    table.scale(1, 4)
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('black')
        cell.set_linewidth(2)
        cell.set_height(1/height)
        # Modifica stile testo
        if (i, j) != (0, -1):  # Ignora le intestazioni (non presenti in questo caso)
            cell.set_text_props(fontsize=16, weight='bold', ha='center', va='center')
    plt.savefig(f"output_images/puzzle_time_{t}.png")
    plt.close()

def print_grid(state, t):
    print(f"Tempo {t}:")
    for row in state:
        row_repr = [str(cell) if cell != 0 else '0' for cell in row]
        print('[' + ', '.join(row_repr) + ']')
    print()

def main():
    parser = argparse.ArgumentParser(description="Crea immagini e video di una griglia.")
    parser.add_argument('-s', action='store_true', help='Stampa la griglia a schermo per ogni mossa')
    parser.add_argument('-a', '--altezza', type=int, default=3, help='Altezza della griglia.')
    parser.add_argument('-l', '--larghezza', type=int, default=3, help='Larghezza della griglia.')
    args = parser.parse_args()

    with open('holds.txt', 'r') as f:
        holds_text = f.read()
    time_states = parse_holds(holds_text, args.altezza, args.larghezza)
    output_dir = 'output_images'
    os.makedirs(output_dir, exist_ok=True)
    for t in sorted(time_states.keys()):
        state = time_states[t]
        if args.s:
            print_grid(state, t)
        else:
            draw_grid(state, t, args.altezza, args.larghezza)
    if not args.s:
        print("Immagini generate con successo.")
        
        # Creazione del video
        images = []
        for t in sorted(time_states.keys()):
            images.append(imageio.imread(f"{output_dir}/puzzle_time_{t}.png"))
        imageio.mimsave('output_images/puzzle_evolution.mp4', images, fps=1, format='ffmpeg')
        print("Video generato con successo.")

if __name__ == "__main__":
    main()