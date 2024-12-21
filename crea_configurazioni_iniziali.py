import os
import random
import json
from heapq import heappop, heappush

def print_configuration(tiles, rows, cols):
    """
    Stampa la configurazione a schermo, 'rows' righe e 'cols' colonne.
    """
    for r in range(rows):
        # Estrae la porzione da r*cols a (r+1)*cols
        print(tiles[r*cols:(r+1)*cols])
    print()

def save_configuration_to_file(tiles, rows, cols):
    """
    Salva la configurazione in un file JSON del tipo ./3x3/3x3.json, ./3x4/3x4.json, ecc.
    Se la cartella non esiste, la crea.
    """
    directory = f"./{rows}x{cols}"
    filename  = f"{rows}x{cols}.json"

    # Assicuriamoci che la directory esista
    os.makedirs(directory, exist_ok=True)

    filepath = os.path.join(directory, filename)

    try:
        with open(filepath, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.append(tiles)

    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def find_zero(tiles):
    """
    Trova l'indice in cui si trova lo spazio vuoto (0).
    """
    return tiles.index(0)

def valid_moves(zero_pos, rows, cols):
    """
    Restituisce un elenco di spostamenti validi (in termini di delta sull'indice 'zero_pos').
    Per esempio, -cols vuol dire "muovi in alto" (se possibile), +cols "muovi in basso", ecc.
    """
    moves = []
    row, col = divmod(zero_pos, cols)

    # Su
    if row > 0:
        moves.append(-cols)
    # Giù
    if row < rows - 1:
        moves.append(cols)
    # Sinistra
    if col > 0:
        moves.append(-1)
    # Destra
    if col < cols - 1:
        moves.append(1)

    return moves

def make_move(tiles, zero_pos, move):
    """
    Dato l'array 'tiles', scambia la posizione zero con la nuova (zero_pos + move).
    Restituisce un nuovo array con la modifica.
    """
    new_tiles = tiles[:]
    new_zero_pos = zero_pos + move
    new_tiles[zero_pos], new_tiles[new_zero_pos] = new_tiles[new_zero_pos], new_tiles[zero_pos]
    return new_tiles

def manhattan_distance(tiles, rows, cols):
    """
    Calcola la distanza di Manhattan tra la configurazione corrente e la configurazione finale.
    In questa variante, consideriamo come configurazione finale l'array:
    [ (rows*cols - 1), (rows*cols - 2), ..., 1, 0 ]
    """
    distance = 0
    total = rows * cols

    for i, tile in enumerate(tiles):
        if tile != 0:
            # Posizione corretta (invertita) del tassello tile
            correct_pos = (total - 1) - tile
            curr_row, curr_col = divmod(i, cols)
            goal_row, goal_col = divmod(correct_pos, cols)
            distance += abs(curr_row - goal_row) + abs(curr_col - goal_col)

    return distance

def generate_solution_tiles(rows, cols):
    """
    Genera la configurazione finale (risolta) invertita, del tipo:
    [rows*cols - 1, rows*cols - 2, ..., 0].
    Ad esempio, per 3x3 = [8, 7, 6, 5, 4, 3, 2, 1, 0].
    """
    total = rows * cols
    return list(range(total - 1, -1, -1))

def generate_configuration_from_solution(rows, cols, num_moves=10):
    """
    Partendo dalla configurazione finale (soluzione), esegue 'num_moves' mosse casuali
    per ottenere una configurazione iniziale sicuramente risolvibile.
    """
    tiles = generate_solution_tiles(rows, cols)
    zero_pos = find_zero(tiles)

    for _ in range(num_moves):
        moves = valid_moves(zero_pos, rows, cols)
        move = random.choice(moves)
        tiles = make_move(tiles, zero_pos, move)
        zero_pos += move

    return tiles

def solve_puzzle(start_tiles, rows, cols):
    """
    Risolve il puzzle usando l'algoritmo A*. Restituisce il percorso di configurazioni (tiles)
    dalla partenza fino alla soluzione (esclusa la configurazione di partenza, se vuoi puoi includerla).
    """
    zero_pos = find_zero(start_tiles)
    frontier = []
    # Frontiera: heap di tuple (priorità, tiles, zero_pos, costo, path)
    heappush(frontier, (0, start_tiles, zero_pos, 0, []))
    explored = set()

    # Configurazione finale di riferimento
    solution_tiles = generate_solution_tiles(rows, cols)

    while frontier:
        _, current_tiles, z_pos, cost, path = heappop(frontier)

        # Se è la configurazione finale, ritorniamo il percorso
        if current_tiles == solution_tiles:
            return path

        explored.add(tuple(current_tiles))

        # Espandiamo i vicini
        for move in valid_moves(z_pos, rows, cols):
            new_tiles = make_move(current_tiles, z_pos, move)
            new_path = path + [new_tiles]

            if tuple(new_tiles) not in explored:
                priority = cost + 1 + manhattan_distance(new_tiles, rows, cols)
                heappush(frontier, (priority, new_tiles, z_pos + move, cost + 1, new_path))

    return None

def main(rows, cols, num_moves=10, do_solve=False):
    """
    Funzione principale che:
      1) Genera una configurazione casuale e sicuramente risolvibile (num_moves).
      2) La stampa a video.
      3) La salva in ./{rows}x{cols}/{rows}x{cols}.json
      4) Eventualmente esegue la risoluzione (opzionale) e ne stampa il percorso.
    """
    # 1) Genera configurazione
    initial_tiles = generate_configuration_from_solution(rows, cols, num_moves)
    print(f"Configurazione iniziale generata a partire dalla soluzione finale ({rows}x{cols}):")
    print_configuration(initial_tiles, rows, cols)

    # 2) Salva la configurazione
    save_configuration_to_file(initial_tiles, rows, cols)

    # 3) Opzionale: risolvi il puzzle
    if do_solve:
        solution_path = solve_puzzle(initial_tiles, rows, cols)
        if solution_path:
            print("Risoluzione del puzzle:")
            for step, tiles in enumerate(solution_path):
                print(f"Passo {step + 1}:")
                print_configuration(tiles, rows, cols)
        else:
            print("Nessuna soluzione trovata.")

# Esempio di esecuzione diretta
if __name__ == "__main__":
    # Esempio 1: puzzle 3x3 con 15 mosse casuali. Salva in ./3x3/3x3.json
    main(3, 3, num_moves=15, do_solve=False)

    # Esempio 2: puzzle 3x4 con 20 mosse casuali. Salva in ./3x4/3x4.json
    main(3, 4, num_moves=20, do_solve=False)

    # Esempio 3: puzzle 4x4 con 30 mosse casuali. Salva in ./4x4/4x4.json
    main(4, 4, num_moves=30, do_solve=False)
