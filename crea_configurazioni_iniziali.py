import os
import sys
import random
import json
from heapq import heappop, heappush

# --------------------------------------------------------------
# Sezione flag da terminale
# --------------------------------------------------------------
RANDOM_MODE = False
MIXED_MODE = False

if "--random" in sys.argv:
    RANDOM_MODE = True
    sys.argv.remove("--random")

if "--mixed" in sys.argv:
    MIXED_MODE = True
    sys.argv.remove("--mixed")

# --------------------------------------------------------------
# Funzioni di utility per stampa e salvataggio
# --------------------------------------------------------------
def print_configuration(tiles, rows, cols):
    """
    Stampa la configurazione a schermo, 'rows' righe e 'cols' colonne.
    """
    for r in range(rows):
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

# --------------------------------------------------------------
# Funzioni base per manipolare e valutare lo stato del puzzle
# --------------------------------------------------------------
def find_zero(tiles):
    """
    Trova l'indice in cui si trova lo spazio vuoto (0).
    """
    return tiles.index(0)

def valid_moves(zero_pos, rows, cols):
    """
    Restituisce un elenco di spostamenti validi (in termini di delta sull'indice 'zero_pos').
    Per esempio, -cols vuol dire "muovi in alto", +cols "muovi in basso", ecc.
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
    Calcola la distanza di Manhattan tra la configurazione corrente e la configurazione finale,
    intesa come [1, 2, 3, ..., (rows*cols - 1), 0].
    """
    distance = 0
    for i, tile in enumerate(tiles):
        if tile != 0:
            correct_pos = tile - 1
            goal_row, goal_col = divmod(correct_pos, cols)
            curr_row, curr_col = divmod(i, cols)
            distance += abs(curr_row - goal_row) + abs(curr_col - goal_col)
    return distance

def generate_solution_tiles(rows, cols):
    """
    Genera la configurazione finale (risolta), del tipo:
    [1, 2, 3, ..., (rows*cols - 1), 0].
    Ad esempio, per 3x3 = [1, 2, 3, 4, 5, 6, 7, 8, 0].
    """
    total = rows * cols
    return list(range(1, total)) + [0]

# --------------------------------------------------------------
# Modalità 1: generazione casuale
# --------------------------------------------------------------
def generate_configuration_random(rows, cols, num_moves):
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

# --------------------------------------------------------------
# Modalità 2: generazione max-Manhattan
# --------------------------------------------------------------
def generate_configuration_max_manhattan(rows, cols, num_moves=10):
    """
    Partendo dalla configurazione finale (soluzione), esegue 'num_moves' mosse,
    ogni volta scegliendo quella che massimizza la distanza di Manhattan.
    """
    tiles = generate_solution_tiles(rows, cols)
    zero_pos = find_zero(tiles)

    for _ in range(num_moves):
        best_move = None
        best_dist = -1

        for move in valid_moves(zero_pos, rows, cols):
            new_tiles = make_move(tiles, zero_pos, move)
            dist = manhattan_distance(new_tiles, rows, cols)
            if dist > best_dist:
                best_dist = dist
                best_move = move

        if best_move is not None:
            tiles = make_move(tiles, zero_pos, best_move)
            zero_pos += best_move
        else:
            # Caso estremamente raro: nessuna mossa valida
            break

    return tiles

# --------------------------------------------------------------
# Modalità 3: "Mixed" (max-Manhattan + casuale)
# --------------------------------------------------------------
def generate_configuration_mixed(rows, cols, num_moves=10, random_prob=0.3):
    """
    Partendo dalla configurazione finale (soluzione), esegue 'num_moves' mosse.
    Ad ogni mossa:
      - Si calcola la mossa "migliore" (quella che massimizza la distanza di Manhattan).
      - Con probabilità random_prob, invece di fare la mossa migliore, se ne sceglie una diversa a caso.
    """
    tiles = generate_solution_tiles(rows, cols)
    zero_pos = find_zero(tiles)

    for _ in range(num_moves):
        moves_and_dist = []
        best_move = None
        best_dist = -1

        # Trova la mossa migliore in termini di distanza di Manhattan
        for move in valid_moves(zero_pos, rows, cols):
            new_tiles = make_move(tiles, zero_pos, move)
            dist = manhattan_distance(new_tiles, rows, cols)
            moves_and_dist.append((move, dist))
            if dist > best_dist:
                best_dist = dist
                best_move = move

        # Con probabilità random_prob, scegli una mossa diversa dal best_move
        if random.random() < random_prob:
            alternative_moves = [m for (m, d) in moves_and_dist if m != best_move]
            if alternative_moves:
                chosen_move = random.choice(alternative_moves)
            else:
                chosen_move = best_move
        else:
            chosen_move = best_move

        # Esegui la mossa scelta
        tiles = make_move(tiles, zero_pos, chosen_move)
        zero_pos += chosen_move

    return tiles

# --------------------------------------------------------------
# Funzione di "dispatch" che sceglie la modalità
# --------------------------------------------------------------
def generate_configuration_from_solution(rows, cols, num_moves=10):
    """
    Sceglie la strategia di generazione in base ai flag:
      - Se RANDOM_MODE=True, usa 'generate_configuration_random'
      - Se MIXED_MODE=True,  usa 'generate_configuration_mixed'
      - Altrimenti,          usa 'generate_configuration_max_manhattan'
    """
    if RANDOM_MODE:
        return generate_configuration_random(rows, cols, num_moves)
    elif MIXED_MODE:
        return generate_configuration_mixed(rows, cols, num_moves, random_prob=0.3)
    else:
        return generate_configuration_max_manhattan(rows, cols, num_moves)

# --------------------------------------------------------------
# Risoluzione del puzzle (A*)
# --------------------------------------------------------------
def solve_puzzle(start_tiles, rows, cols):
    """
    Risolve il puzzle usando l'algoritmo A*. Restituisce il percorso di configurazioni (tiles)
    dalla partenza fino alla soluzione (esclusa la configurazione di partenza).
    """
    zero_pos = find_zero(start_tiles)
    frontier = []
    # Frontiera: heap di tuple (priorità, tiles, zero_pos, costo, path)
    heappush(frontier, (0, start_tiles, zero_pos, 0, []))
    explored = set()

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

# --------------------------------------------------------------
# Funzione principale
# --------------------------------------------------------------
def main(rows, cols, num_moves=10, do_solve=False):
    """
    Funzione principale che:
      1) Genera una configurazione (casuale, mixed, o max-Manhattan).
      2) La stampa a video.
      3) La salva in ./{rows}x{cols}/{rows}x{cols}.json
      4) Eventualmente esegue la risoluzione (opzionale) e ne stampa il percorso.
    """
    # 1) Genera configurazione (partendo da quella finale standard)
    initial_tiles = generate_configuration_from_solution(rows, cols, num_moves)
    print(f"Configurazione iniziale generata ({rows}x{cols}):")
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

# --------------------------------------------------------------
# Esempi d'uso se eseguito come script
# --------------------------------------------------------------
if __name__ == "__main__":
    # # Esempio 1: puzzle 3x3 con 20 mosse
    # main(3, 3, num_moves=30, do_solve=False)

    # # Esempio 2: puzzle 3x4 con 20 mosse
    # main(3, 4, num_moves=30, do_solve=False)

    # # Esempio 3: puzzle 4x4 con 50 mosse
    # main(4, 4, num_moves=25, do_solve=False)
    
    # Esegui lo script "python conf_iniziali.py"
    
    # Crea 33 configurazioni iniziali per ogni dimensione, con un numero di passi randomici tra 10 e 50
    # Strategia random
    # random.seed(42)
    combinazioni = [(3,3), (3,4), (4,4)]
    
    for rows, cols in combinazioni:
        for x in range(33):
            random.seed(x)

            main(rows, cols, num_moves=30, do_solve=False)
            print(f"Configurazione {rows}x{cols}")
    
    