import re
import matplotlib.pyplot as plt
import os
import argparse
import imageio.v2 as imageio

def parse_holds(holds_text):
    pattern = r"holds\(posizione_tessera\((\d+),(\d+),(\d+)\),(\d+)\)"
    matches = re.findall(pattern, holds_text)
    time_states = {}
    for tile, x, y, t in matches:
        t = int(t)
        tile = int(tile)
        x = int(x) - 1  # Le coordinate partono da 1
        y = int(y) - 1
        if t not in time_states:
            time_states[t] = [[0]*3 for _ in range(3)]  # 3x3 grid
        time_states[t][x][y] = tile
    return time_states

def draw_grid(state, t):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.set_title(f"Tempo {t}")
    ax.axis('off')
    table_data = [[cell if cell != 0 else '' for cell in row] for row in state]
    table = ax.table(cellText=table_data, loc='center', cellLoc='center', edges='closed')
    table.scale(1, 4)
    for (i, j), cell in table.get_celld().items():
        cell.set_edgecolor('black')
        cell.set_linewidth(2)
        cell.set_height(1/3)
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store_true', help='Stampa la griglia a schermo per ogni mossa')
    args = parser.parse_args()

    with open('holds.txt', 'r') as f:
        holds_text = f.read()
    time_states = parse_holds(holds_text)
    output_dir = 'output_images'
    os.makedirs(output_dir, exist_ok=True)
    for t in sorted(time_states.keys()):
        state = time_states[t]
        if args.s:
            print_grid(state, t)
        else:
            draw_grid(state, t)
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