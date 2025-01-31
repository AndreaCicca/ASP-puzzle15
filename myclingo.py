import sys
import threading
import time
import csv
import os
from clingo import Control

DEBUG = False
DEBUGDEEP = False
nun_cpu = os.cpu_count()

if "-d" in sys.argv:
    DEBUG = True

if "-dd" in sys.argv:
    DEBUGDEEP = True


class SolverThread(threading.Thread):
    def __init__(self, ctl, results, solved_event):
        super().__init__()
        self.ctl = ctl
        self.results = results
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
                    occurs_count = sum(1 for atom in model.symbols(atoms=True) if str(atom).startswith("occurs"))
                    self.results.append(occurs_count)
        except Exception as e:
            if DEBUG:
                print(f"Solver interrotto: {e}")
        finally:
            self.solved_event.set()


def solve_game(conf="3x3", 
               path_file="./gioco.asp", 
               initial_config_path="./3x3/initial_state/state_2.pl", 
               goal="./goal/3x3.pl", 
               time_limit=300):
    """
    Versione 'sistemata' che impone un limite TOTALE di 300s per
    l'intera ricerca (non solo per singolo maxtime).
    """
    if DEBUGDEEP:
        print("######### Risoluzione del gioco con ASP ###########")
        print("Configurazione:", conf)
        print("Risoluzione del gioco al path:", path_file)
        print("Obiettivo al path:", goal)
        print("Configurazione iniziale al path:", initial_config_path)
        print(f"Limite di tempo: {time_limit} secondi")
        print(f"Numero di CPU: {nun_cpu}")

    found_solution = False
    min_moves = None

    # Tempo globale di inizio
    start_global_time = time.time()

    # Tenta maxtime da 1 a 50
    for maxtime in range(1, 51):
        # Se abbiamo già trovato soluzione, fermiamoci
        if found_solution:
            break

        # Calcoliamo il tempo rimanente prima di sforare 'time_limit'
        elapsed_global = time.time() - start_global_time
        tempo_rimanente = time_limit - elapsed_global
        if tempo_rimanente <= 0:
            if DEBUG:
                print(f"Tempo globale di {time_limit} secondi esaurito prima di maxtime={maxtime}.")
            break

        if DEBUGDEEP:
            print(f"Tentativo con maxtime={maxtime}, tempo rimanente={tempo_rimanente:.2f}s")

        ctl = Control(["-t", f"{nun_cpu}", 
                       "--configuration", "crafty", 
                       "--opt-strategy", "bb", 
                       "--rand-freq", "0.02"])
        ctl.add("base", [], f"#const maxtime = {maxtime}.")

        # Aggiunta costanti in base alla configurazione
        if conf == "3x3":
            ctl.add("base", [], "#const nr = 3.")
            ctl.add("base", [], "#const nc = 3.")
        elif conf == "4x4":
            ctl.add("base", [], "#const nr = 4.")
            ctl.add("base", [], "#const nc = 4.")
        elif conf == "3x4":
            ctl.add("base", [], "#const nr = 3.")
            ctl.add("base", [], "#const nc = 4.")

        # Carichiamo i file ASP
        if initial_config_path:
            ctl.load(initial_config_path)
            ctl.load(goal)
        ctl.load(path_file)

        # Ground
        ctl.ground([("base", [])])

        results = []
        solved_event = threading.Event()
        solver_thread = SolverThread(ctl, results, solved_event)

        # Lancio del solver in thread separato
        solver_thread.start()
        # Attendi la fine del solver con un timeout = tempo_rimanente
        solver_thread.join(timeout=tempo_rimanente)

        if solver_thread.is_alive():
            # Se è ancora vivo, significa che ha sforato tempo_rimanente
            if DEBUG:
                print(f"Timeout raggiunto in maxtime={maxtime}. Interruzione solver.")
            solver_thread.stop()
            solver_thread.join()

            # Non necessariamente abbiamo una soluzione, 
            # ma abbiamo esaurito il tempo globale.
            found_solution = True
            min_moves = maxtime  # se vuoi associare maxtime al numero di mosse
        else:
            # Solver terminato prima di esaurire il tempo_rimanente
            if results:
                # Se abbiamo soluzioni, cerchiamo il min di occurs
                current_min = min(results)
                if min_moves is None or current_min < min_moves:
                    min_moves = current_min
                found_solution = True
                if DEBUG:
                    print(f"Soluzione trovata con maxtime={maxtime}, min_moves={min_moves}")
            else:
                # Non abbiamo trovato soluzioni per questo maxtime
                # ma il solver è terminato comunque. Proviamo con maxtime successivo.
                if DEBUG:
                    print(f"Test maxtime={maxtime}")

    # Tempo totale effettivo consumato
    total_time = time.time() - start_global_time

    # Se usciamo dal for senza alcuna soluzione
    if not found_solution or min_moves is None:
        if DEBUG:
            print("Nessuna soluzione trovata entro il tempo limite.")
        return None, total_time

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
