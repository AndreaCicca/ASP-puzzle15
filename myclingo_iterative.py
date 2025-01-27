import sys
import threading
import time
import csv
import os
from clingo import Control

DEBUG = False
nun_cpu = os.cpu_count()

# Set debug true with -d flag
if "-d" in sys.argv:
    DEBUG = True

def solve_with_timeout(ctl, results, last_holds, solved_event):
    """Funzione per risolvere il problema con il timeout."""
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            actions = [atom for atom in model.symbols(atoms=True) if str(atom).startswith("occurs")]
            results.append(actions)

            holds = [str(atom) for atom in model.symbols(atoms=True) if str(atom).startswith("hold")]
            last_holds[:] = holds  # Aggiorna la lista con l'ultimo modello trovato

    solved_event.set()

class SolverThread(threading.Thread):
    def __init__(self, ctl, results, last_holds, solved_event):
        super().__init__()
        self.ctl = ctl
        self.results = results
        self.last_holds = last_holds
        self.solved_event = solved_event
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        with self.ctl.solve(yield_=True) as handle:
            while not self.stopped():
                for model in handle:
                    actions = [atom for atom in model.symbols(atoms=True) if str(atom).startswith("occurs")]
                    self.results.append(actions)
                    holds = [str(atom) for atom in model.symbols(atoms=True) if str(atom).startswith("hold")]
                    self.last_holds[:] = holds
                break
        self.solved_event.set()

def solve_game(conf="3x3", path_file="./gioco.asp", initial_config_path="./3x3/initial_state/state_2.pl", goal="./goal/3x3.pl", time_limit=300):
    if DEBUG:
        print("######### Risoluzione del gioco con ASP ###########")
        print("Configurazione:", conf)
        print("Risoluzione del gioco al path:", path_file)
        print("Obiettivo al path:", goal)
        print("Configurazione iniziale al path:", initial_config_path)
        print(f"Limite di tempo: {time_limit} secondi")
        print(f"Numero di CPU: {nun_cpu}")

    results = []
    all_results = {}
    times = {}
    found_solution = False
    total_time = 0

    # Try different maxtime values from 1 to 50
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
        last_holds = []

        start_time = time.time()
        solved = threading.Event()
        solution_thread = SolverThread(ctl, results, last_holds, solved)
        solution_thread.start()
        solution_thread.join(timeout=time_limit)

        if solution_thread.is_alive():
            if DEBUG:
                print("Timeout raggiunto. Interruzione della risoluzione.")
            solution_thread.stop()
            solution_thread.join()
            total_time = time_limit
            found_solution = True
        else:
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
        
        # If we found a solution, store it and break out
        if results:
            all_results["default"] = results
            times["default"] = total_time
            found_solution = True
            if DEBUG:
                print(f"Solution found with maxtime={maxtime}, time={total_time}")
            break

    if not found_solution:
        if DEBUG:
            print("No solution found")
        return {}, {"default": total_time}

    return all_results, times

def benchmark():
    # combinazioni = ["3x4"]
    combinazioni = ["4x4"]
    # combinazioni = ["3x4"]
    
    # reset csv
    for c in combinazioni:
        with open(f'results_{c}.csv', mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(["configurazione", "iniziale", "tempo", "mosse"])
    
    for c in combinazioni:
        goal_path = f"./goal/{c}.pl"
        lista_iniziali = os.listdir(f"./{c}/initial_state")
        lista_iniziali = sorted(lista_iniziali, key=lambda x: int(x.split("_")[1].split(".")[0]))

        print(f"Configurazioni per {c}: ")
        print(lista_iniziali)
        
        for iniziale in lista_iniziali:
            initial_path = f"./{c}/initial_state/{iniziale}"
            all_solutions, times = solve_game(path_file=f"./gioco_generico.asp", initial_config_path=initial_path, goal=goal_path, conf=c)
            solutions = all_solutions["default"]
            if solutions:
                shortest_solution = min(solutions, key=lambda x: len(x))
                mosse_minime = len(shortest_solution)
            else:
                mosse_minime = 0
            with open(f'results_{c}.csv', mode='a') as file:
                writer = csv.writer(file)
                writer.writerow([c, iniziale, times["default"], mosse_minime])
        

if __name__ == "__main__":
    benchmark()
