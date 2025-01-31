import sys
import csv
import matplotlib.pyplot as plt

def plot_csv_list(files):
    fig, axes = plt.subplots(len(files), 1, figsize=(8, 4 * len(files)))
    if len(files) == 1:
        axes = [axes]  # Assicurarsi che axes sia una lista anche per un solo file

    for i, filename in enumerate(files):
        data = {}
        with open(filename, mode="r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                conf = row["configurazione"]
                tempo = float(row["tempo"])
                mosse = float(row["mosse"])
                
                if tempo > 300:
                    continue
                
                if conf not in data:
                    data[conf] = {"tempo": [], "mosse": []}
                data[conf]["tempo"].append(tempo)
                data[conf]["mosse"].append(mosse)
        
        # Creare i punti 2D per ciascuna configurazione
        for conf, values in data.items():
            axes[i].scatter(values["tempo"], values["mosse"], label=conf)
        
        # Impostare titoli e etichette
        axes[i].set_xlabel("tempo")
        axes[i].set_ylabel("mosse")
        axes[i].set_title(f"File: {filename}")
        axes[i].legend()
        # set log x
        # axes[i].set_xscale("log")

    plt.tight_layout()
    # plt.show()
    plt.savefig("plot.png")

def main():
    if len(sys.argv) < 2:
        print("Uso: python csv_plot.py <file1.csv> [<file2.csv> ...]")
        sys.exit(1)
    
    files = sys.argv[1:]
    plot_csv_list(files)

if __name__ == "__main__":
    main()
