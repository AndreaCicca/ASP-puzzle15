import sys
import threading
import time
import csv
import os
from clingo import Control

DEBUG = False
DEBUGDEEP = False
nun_cpu = os.cpu_count()

# Imposta il debug a True con il flag -d
if "-d" in sys.argv:
    DEBUG = True

if "-dd" in sys.argv:
    DEBUGDEEP = True

class SolverThread(threading.Thread):
    def __init__(self, ctl, results, solved_event):
        super().__init__()
        self.ctl = ctl
        self.results = results  # Lista per memorizzare il numero di occurs
        self.solved_event = solved_event
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()
        self.ctl.interrupt()  # Interrompe Clingo

    def run(self):
        try:
            with self.ctl.solve(yield_=True) as handle:
                for model in handle:
                    if self._stop_event.is_set():
                        break
                    # Conta il numero di 'occurs' invece di raccoglierli
                    occurs_count = sum(1 for atom in model.symbols(atoms=True) if str(atom).startswith("occurs"))
                    self.results.append(occurs_count)
        except Exception as e:
            if DEBUG:
                print(f"Solver interrotto: {e}")
        finally:
            self.solved_event.set()

def solve_game(conf="3x3", path_file="./gioco.asp", initial_config_path="./3x3/initial_state/state_2.pl", goal="./goal/3x3.pl", time_limit=300):
    if DEBUGDEEP:
        print("######### Risoluzione del gioco con ASP ###########")
        print("Configurazione:", conf)
        print("Risoluzione del gioco al path:", path_file)
        print("Obiettivo al path:", goal)
        print("Configurazione iniziale al path:", initial_config_path)
        print(f"Limite di tempo: {time_limit} secondi")
        print(f"Numero di CPU: {nun_cpu}")

    found_solution = False
    total_time = 0
    min_moves = None  # Variabile per memorizzare il numero minimo di mosse

    # Prova diversi valori di maxtime da 1 a 50
    for maxtime in range(1, 51):
        if found_solution:
            break

        if DEBUG:
            print(f"Trying maxtime: {maxtime}")

        ctl = Control(["-t", f"{nun_cpu}", "--configuration", "crafty", "--opt-strategy", "usc"])
        ctl.add("base", [], f"#const maxtime = {maxtime}.")

        if conf == "3x3":
            ctl.add("base", [], "#const nr = 3.")
            ctl.add("base", [], "#const nc = 3.")
        elif conf == "4x4":
            ctl.add("base", [], "#const nr = 4.")
            ctl.add("base", [], "#const nc = 4.")
        elif conf == "3x4":
            ctl.add("base", [], "#const nr = 3.")
            ctl.add("base", [], "#const nc = 4.")

        if initial_config_path:
            ctl.load(initial_config_path)
            ctl.load(goal)

        ctl.load(path_file)
        ctl.ground([("base", [])])

        results = []

        start_time = time.time()
        solved = threading.Event()
        solution_thread = SolverThread(ctl, results, solved)
        solution_thread.start()
        solution_thread.join(timeout=time_limit)

        if solution_thread.is_alive():
            if DEBUG:
                print("Timeout raggiunto. Interruzione della risoluzione.")
            solution_thread.stop()  # Interrompe Clingo
            solution_thread.join()
            total_time += time_limit
            # Passa il maxtime come numero di mosse se il tempo è scaduto
            min_moves = maxtime
            found_solution = True   
        else:
            elapsed_time = time.time() - start_time
            total_time += elapsed_time

            if results:
                # Prende il numero minimo di mosse tra le soluzioni trovate
                current_min = min(results)
                if min_moves is None or current_min < min_moves:
                    min_moves = current_min
                found_solution = True
                if DEBUG:
                    print(f"Solution found with maxtime={maxtime}, time={total_time}, min_moves={min_moves}")
                break  # Esci dal ciclo se hai trovato una soluzione

    if not found_solution:
        if DEBUG:
            print("No solution found")
        return None, total_time  # Nessuna soluzione trovata

    return min_moves, total_time

def benchmark():
    combinazioni = ["3x4"]
    # combinazioni = ["3x3"]
    # combinazioni = ["4x4"]

    # Resetta il CSV
    for c in combinazioni:
        with open(f'results_{c}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["configurazione", "iniziale", "tempo", "mosse"])

    for c in combinazioni:
        goal_path = f"./goal/{c}.pl"
        initial_state_dir = f"./{c}/initial_state"
        if not os.path.exists(initial_state_dir):
            print(f"Directory iniziale {initial_state_dir} non trovata.")
            continue

        lista_iniziali = os.listdir(initial_state_dir)
        lista_iniziali = sorted(lista_iniziali, key=lambda x: int(x.split("_")[1].split(".")[0]))

        print(f"Configurazioni per {c}: ")
        print(lista_iniziali)
        
        for iniziale in lista_iniziali:
            initial_path = os.path.join(initial_state_dir, iniziale)
            all_solutions, elapsed_time = solve_game(
                path_file=f"./gioco_generico.asp",
                initial_config_path=initial_path,
                goal=goal_path,
                conf=c
            )
            
            if all_solutions is not None:
                mosse_minime = all_solutions
            else:
                # Se non c'è soluzione, assegna 0 o un valore che preferisci
                mosse_minime = 0

            with open(f'results_{c}.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([c, iniziale, elapsed_time, mosse_minime])

if __name__ == "__main__":
    benchmark()
