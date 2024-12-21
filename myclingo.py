import sys
import time
from clingo import Control

def solve_game(maxtime=24, path_file="./3x3/gioco_8.asp", initial_config_path="./3x3/initial_state/state_2.pl", configurations=["jumpy"]):
    print("Risoluzione del gioco al path: ", path_file)
    print("Configurazione iniziale al path: ", initial_config_path)

    if configurations is None:
        configurations = ["jumpy", "tweety", "trendy", "crafty", "handy"]

    all_results = {}
    times = {}

    for config in configurations:
        print(f"Risoluzione con configurazione: {config}")

        # Crea un controllo Clingo con l'opzione multi-threading
        ctl = Control(["-t", "8"])

        # Aggiungi il limite di tempo come direttiva ASP
        ctl.add("base", [], f"#const maxtime = {maxtime}.")

        # Carica la configurazione iniziale, se presente
        if initial_config_path:
            ctl.load(initial_config_path)

        # Carica il programma principale
        ctl.load(path_file)

        # Ground del programma
        ctl.ground([("base", [])])

        # Risolvi e raccogli i risultati
        results = []
        last_holds = []  # Lista per gli holds dell'ultimo modello

        start_time = time.time()
        with ctl.solve(yield_=True) as handle:
            for model in handle:
                # Estrai le azioni dal modello
                actions = [atom for atom in model.symbols(atoms=True) if str(atom).startswith("occurs")]
                results.append(actions)

                # Estrai le soluzioni hold
                holds = [str(atom) for atom in model.symbols(atoms=True) if str(atom).startswith("hold")]
                last_holds = holds  # Aggiorna gli holds all'ultimo modello

        end_time = time.time()

        # Dopo aver iterato tutti i modelli, scrivi gli holds dell'ultimo nel file
        with open("holds.txt", "w") as file:
            for hold in last_holds:
                file.write(f"{hold}\n")

        all_results[config] = results
        times[config] = end_time - start_time

    return all_results, times


def main():
    path_file = "./3x3/gioco_8.asp"  # Percorso predefinito
    initial_config_path = "./3x3/initial_state/state_2.pl"

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

    if len(sys.argv) > 1 and sys.argv[1] == "-gara":
        # Risolvi il puzzle dell'8 con gara
        all_solutions, times = solve_game(path_file=path_file, initial_config_path=initial_config_path)

        # Ordina le configurazioni per tempo
        sorted_configs = sorted(times, key=times.get)

        # Stampa i risultati della gara
        print("Classifica della gara:")
        for i, config in enumerate(sorted_configs, 1):
            print(f"{i}. Configurazione: {config}, Tempo: {times[config]:.2f} secondi")
            solutions = all_solutions[config]
            for j, solution in enumerate(solutions, 1):
                print(f"  Soluzione {j}:")
                for action in solution:
                    print(f"    {action}")
                print("\n")
    else:
        # Risolvi il puzzle dell'8 senza gara
        all_solutions, times = solve_game(path_file=path_file, initial_config_path=initial_config_path)

        # Stampa le soluzioni trovate
        solutions = all_solutions["jumpy"]
        for i, solution in enumerate(solutions, 1):
            print(f"\n")
            print(f"Soluzione {i}:")
            # Ordina le azioni in base al momento temporale
            sorted_actions = sorted(solution, key=lambda x: int(str(x).split(",")[-1].strip(")")))
            for action in sorted_actions:
                print(action)
        
        print(f"\n")
        print(f"Tempo impiegato: {times['jumpy']:.2f} secondi")

if __name__ == "__main__":
    main()
