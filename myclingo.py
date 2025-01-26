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

def solve_game(maxtime=50, conf="3x3", path_file="./gioco.asp", initial_config_path="./3x3/initial_state/state_2.pl", goal="./goal/3x3.pl", configurations=["crafty"], time_limit=300):
    
    if DEBUG:
        print("######### Risoluzione del gioco con ASP ###########")
        print("Configurazione:", conf)
        print("Risoluzione del gioco al path:", path_file)
        print("Obiettivo al path:", goal)
        print("Configurazione iniziale al path:", initial_config_path)
        print(f"Limite di tempo: {time_limit} secondi")
        print(f"Numero di CPU: {nun_cpu}")
        print("Maxtime:", maxtime)

    if configurations is None:
        configurations = ["jumpy", "tweety", "trendy", "crafty", "handy"]

    all_results = {}
    times = {}

    for config in configurations:
        print(f"Risoluzione con configurazione: {config}")

        ctl = Control(["-t", f"{nun_cpu}", "--configuration", config, "--opt-strategy", "usc"])
        # ctl = Control(["-t", f"{nun_cpu}"])

        # Aggiungi il limite di tempo come direttiva ASP
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

        # Carica la configurazione iniziale, se presente
        if initial_config_path:
            ctl.load(initial_config_path)
            ctl.load(goal)

        # Carica il programma principale
        ctl.load(path_file)
        
        # aggiungo la configurazione

        # Ground del programma
        ctl.ground([("base", [])])

        # Risolvi e raccogli i risultati
        results = []
        last_holds = []

        start_time = time.time()
        solved = threading.Event()  # Evento per gestire il timeout
        solution_thread = threading.Thread(target=lambda: solve_with_timeout(ctl, results, last_holds, solved))
        solution_thread.start()
        solution_thread.join(timeout=time_limit)

        if solution_thread.is_alive():
            print("Timeout raggiunto. Interruzione della risoluzione.")
            solution_thread.join()  # Assicurati che il thread si chiuda correttamente
            end_time = time_limit
        else:
            end_time = time.time()

        # # Dopo aver iterato tutti i modelli, scrivi gli holds dell'ultimo nel file
        # with open("holds.txt", "w") as file:
        #     for hold in last_holds:
        #         file.write(f"{hold}\n")

        all_results[config] = results
        times[config] = end_time - start_time

    return all_results, times

def multiple_configuration():
    # path_file = "./gioco.asp"  
    # path_goal = "./goal/3x3.pl"
    # initial_config_path = "./3x3/initial_state/state_2.pl"
    # configurazione_gioco = "3x3"
    
    configurazione_gioco = "3x3"
    # configurazione_gioco = "3x4"
    # configurazione_gioco = "4x4"
    path_file = f"./gioco_generico.asp" 
    path_goal = f"./goal/{configurazione_gioco}.pl"
    initial_config_path = f"./{configurazione_gioco}/initial_state/state_10.pl"

    # Controlla i flag e aggiorna i parametri
    if "-p" in sys.argv:
        p_index = sys.argv.index("-p")
        if p_index + 1 < len(sys.argv):
            path_file = sys.argv[p_index + 1]
        else:
            print("Errore: nessun percorso specificato dopo il flag -p")
            sys.exit(1)

    if "-ci" in sys.argv:
        ci_index = sys.argv.index("-ci")
        if ci_index + 1 < len(sys.argv):
            initial_config_path = sys.argv[ci_index + 1]
        else:
            print("Errore: nessun percorso specificato dopo il flag -ci")
            sys.exit(1)

    # if len(sys.argv) > 1 and sys.argv[1] == "-gara":
    #     # Risolvi il puzzle dell'8 con gara
    #     all_solutions, times = solve_game(path_file=path_file, initial_config_path=initial_config_path, goal=path_goal, conf=configurazione_gioco)

    #     # Ordina le configurazioni per tempo
    #     sorted_configs = sorted(times, key=times.get)

    #     # Stampa i risultati della gara
    #     print("Classifica della gara:")
    #     for i, config in enumerate(sorted_configs, 1):
    #         print(f"{i}. Configurazione: {config}, Tempo: {times[config]:.2f} secondi")
    #         solutions = all_solutions[config]
    #         for j, solution in enumerate(solutions, 1):
    #             print(f"  Soluzione {j}:")
    #             for action in solution:
    #                 print(f"    {action}")
    #             print("\n")
    # else:
    
    # Risolvi il puzzle dell'8 senza gara
    all_solutions, times = solve_game(path_file=path_file, initial_config_path=initial_config_path, goal=path_goal, conf=configurazione_gioco, time_limit=300)
    solutions = all_solutions["crafty"]
    for i, solution in enumerate(solutions, 1):
        print(f"\n")
        print(f"Soluzione {i}:")
        # Ordina le azioni in base al momento temporale
        sorted_actions = sorted(solution, key=lambda x: int(str(x).split(",")[-1].strip(")")))
        for action in sorted_actions:
            print(action)
    
    print(f"\n")
    print(f"Tempo impiegato: {times['crafty']:.2f} secondi")


def benchmark():
    
    # devo risolvere tutte le configurazioni con tutte le configurazioni iniziali per 3x3, 3x4, 4x4
    conf = ["crafty"]
    
    # combinazioni = ["3x3", "3x4", "4x4"]
    # combinazioni = ["3x4"]
    combinazioni = ["4x4"]
    # combinazioni = ["3x3"]
    # devo salvare i risultati dentro ad un file csv che tiene traccia del tempo impiegato per ogni configurazione
    # devo prendere i dati relativi agli stati iniziali e al goal
    
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
            solutions = all_solutions["crafty"]
            if solutions:
                shortest_solution = min(solutions, key=lambda x: len(x))
                mosse_minime = len(shortest_solution)
            else:
                mosse_minime = 0
            with open(f'results_{c}.csv', mode='a') as file:
                writer = csv.writer(file)
                writer.writerow([c, iniziale, times["crafty"], mosse_minime])
        

if __name__ == "__main__":
    benchmark()
