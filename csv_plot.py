import sys
import csv
import matplotlib.pyplot as plt
import seaborn as sns

def plot_csv_list(files):
    # Impostiamo un tema carino con Seaborn
    sns.set_style("whitegrid")
    sns.set_context("talk")  # "paper", "notebook", "talk", "poster" (scaling differente di font)

    # Per avere un ciclo di colori, prendiamo una palette di Seaborn
    colors = sns.color_palette("bright")

    # 1. Lettura dati per tutti i file
    all_data = {}
    for filename in files:
        data = {}
        with open(filename, mode="r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                conf = row["configurazione"]
                tempo = float(row["tempo"])
                mosse = float(row["mosse"])

                # Saltiamo i tempi > 300 (come nel tuo codice)
                if tempo > 300:
                    continue

                if conf not in data:
                    data[conf] = {"tempo": [], "mosse": []}
                data[conf]["tempo"].append(tempo)
                data[conf]["mosse"].append(mosse)
        
        all_data[filename] = data

    # 2. Plot con asse x lineare (plot_norm.png)
    fig, axes = plt.subplots(len(files), 1, figsize=(10, 5 * len(files)))
    if len(files) == 1:
        axes = [axes]  # se c’è un solo file, forziamo la lista

    for i, filename in enumerate(files):
        data = all_data[filename]
        color_idx = 0
        for conf, values in data.items():
            # Scatter con markers più grandi e alpha per una migliore visibilità
            axes[i].scatter(values["tempo"], values["mosse"], 
                            label=conf,
                            s=70,       # dimensione del marker
                            alpha=0.7,  # trasparenza
                            color=colors[color_idx % len(colors)],
                            edgecolors='black')
            color_idx += 1

        axes[i].set_xlabel("Tempo")
        axes[i].set_ylabel("Mosse")
        axes[i].set_title(f"File: {filename}", fontsize=16)
        axes[i].legend(loc="best")

    plt.tight_layout()
    plt.savefig("plot_norm.png", dpi=300)  # dpi più alto per maggiore definizione
    plt.close(fig)

    # 3. Plot con asse x log (plot_log.png)
    fig, axes = plt.subplots(len(files), 1, figsize=(10, 5 * len(files)))
    if len(files) == 1:
        axes = [axes]

    for i, filename in enumerate(files):
        data = all_data[filename]
        color_idx = 0
        for conf, values in data.items():
            axes[i].scatter(values["tempo"], values["mosse"], 
                            label=conf,
                            s=70,
                            alpha=0.7,
                            color=colors[color_idx % len(colors)],
                            edgecolors='black')
            color_idx += 1

        axes[i].set_xscale("log")
        axes[i].set_xlabel("Tempo (log scale)")
        axes[i].set_ylabel("Mosse")
        axes[i].set_title(f"File: {filename}", fontsize=16)
        axes[i].legend(loc="best")

    plt.tight_layout()
    plt.savefig("plot_log.png", dpi=300)
    plt.close(fig)

def main():
    if len(sys.argv) < 2:
        print("Uso: python csv_plot.py <file1.csv> [<file2.csv> ...]")
        sys.exit(1)
    
    files = sys.argv[1:]
    plot_csv_list(files)

if __name__ == "__main__":
    main()
