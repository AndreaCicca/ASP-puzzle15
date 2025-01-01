import sys
import csv
import matplotlib.pyplot as plt

def plot_csv(filename):
    data = {}
    with open(filename, mode="r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conf = row["configurazione"]
            iniziale = row["iniziale"]
            tempo = float(row["tempo"])
            mosse = float(row["mosse"])
            if conf not in data:
                data[conf] = {"iniziale": [], "tempo": [], "mosse": []}
            data[conf]["iniziale"].append(iniziale)
            data[conf]["tempo"].append(tempo)
            data[conf]["mosse"].append(mosse)

    # Crea un plot per ogni configurazione
    for conf, values in data.items():
        plt.figure(figsize=(8,4))
        x_values = range(len(values["iniziale"]))
        plt.bar(x_values, values["tempo"], color="skyblue", label="tempo")
        plt.xticks(x_values, values["iniziale"], rotation=45)
        plt.title(f"Configurazione: {conf}")
        plt.ylabel("tempo")
        plt.legend()
        plt.tight_layout()
        plt.show()

def plot_csv_list(files):
    fig, axes = plt.subplots(1, len(files), figsize=(12, 4), sharey=True)
    if len(files) == 1:
        axes = [axes]
    for i, filename in enumerate(files):
        data = {}
        with open(filename, mode="r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                conf = row["configurazione"]
                tempo = float(row["tempo"])
                mosse = float(row["mosse"])
                if conf not in data:
                    data[conf] = {"tempo": [], "mosse": []}
                data[conf]["tempo"].append(tempo)
                data[conf]["mosse"].append(mosse)
        for conf, values in data.items():
            axes[i].scatter(values["tempo"], values["mosse"], label=conf)
        axes[i].set_xlabel("tempo")
        axes[i].set_ylabel("mosse")
        axes[i].set_title(filename)
        axes[i].legend()
    plt.tight_layout()
    plt.show()

def main():
    if len(sys.argv) < 2:
        print("Uso: python csv_plot.py <file1.csv> [<file2.csv> ...]")
        sys.exit(1)
    
    files = sys.argv[1:]
    plot_csv_list(files)

if __name__ == "__main__":
    main()