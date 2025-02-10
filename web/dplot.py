import re
import matplotlib.pyplot as plt
import os
import imageio.v2 as imageio
import shutil
import tempfile

def determine_puzzle_dimensions(holds_text):
    # Find all tile numbers
    pattern = r"holds\(posizione_tessera\((\d+),\d+,\d+\),\d+\)"
    matches = re.findall(pattern, holds_text)
    if not matches:
        return 3, 3  # Default dimensions if no matches found
    
    # Get highest tile number
    max_tile = max(int(tile) for tile in matches)
    
    # Determine dimensions based on highest tile
    if max_tile <= 8:
        return 3, 3  # 3x3 puzzle
    elif max_tile <= 11:
        return 3, 4  # 3x4 puzzle
    else:
        return 4, 4  # 4x4 puzzle

def parse_holds(holds_text, height=None, width=None):
    # If dimensions not provided, determine them automatically
    if height is None or width is None:
        height, width = determine_puzzle_dimensions(holds_text)
        
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
    return time_states, height, width

def draw_grid(state, t, height, width, output_dir):
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
    plt.savefig(f"{output_dir}/puzzle_time_{t}.png")
    plt.close()

def print_grid(state, t):
    print(f"Tempo {t}:")
    for row in state:
        row_repr = [str(cell) if cell != 0 else '0' for cell in row]
        print('[' + ', '.join(row_repr) + ']')
    print()

def create_puzzle_gif(holds_text, height=None, width=None):
    # Create a temporary directory for the images
    temp_dir = tempfile.mkdtemp()
    output_file = os.path.join(temp_dir, 'puzzle_evolution.gif')
    
    try:
        # Get time states and dimensions
        time_states, height, width = parse_holds(holds_text, height, width)
        
        # Generate images
        for t in sorted(time_states.keys()):
            state = time_states[t]
            draw_grid(state, t, height, width, temp_dir)
        
        # Create GIF
        images = []
        for t in sorted(time_states.keys()):
            images.append(imageio.imread(f"{temp_dir}/puzzle_time_{t}.png"))
        
        imageio.mimsave(output_file, images, fps=4, format='gif')
        
        # Read the gif file
        with open(output_file, 'rb') as f:
            gif_data = f.read()
            
        # Clean up
        shutil.rmtree(temp_dir)
        
        return gif_data
        
    except Exception as e:
        # Clean up in case of error
        shutil.rmtree(temp_dir)
        raise e

if __name__ == "__main__":
    print("This script is now meant to be used as a module for the web application.")