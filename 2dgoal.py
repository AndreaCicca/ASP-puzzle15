import os

def create_goal_file_2d(rows, cols, output_filename):
    """
    Crea un file contenente le clausole:
        goal(posizione_tessera(Tess, R, C)).
    Organizza le tessere in ordine row-major:
      - 1 in (1,1), 2 in (1,2), ..., ultima tessera-1 in (R,C-1),
      - 0 (spazio) in (rows, cols).
    """
    lines = []
    total = rows * cols
    # Riempiamo le posizioni r=1..rows, c=1..cols in row-major order
    # e assegniamo tile = (r-1)*cols + c, tranne l'ultima posizione che diventa 0.
    for r in range(1, rows+1):
        for c in range(1, cols+1):
            tile = (r - 1) * cols + c  # Valore lineare
            if tile == total:
                tile = 0  # l'ultima posizione ospita lo spazio
            if tile != 0:
                lines.append(f"goal(posizione_tessera({tile},{r},{c})).")
            else:
                lines.append(f"goal(posizione_spazio({r},{c})).")
    
    with open(output_filename, "w") as f:
        f.write("\n".join(lines) + "\n")

def main():
    # Crea la cartella "goal" se non esiste
    os.makedirs("goal", exist_ok=True)

    # 3x3
    create_goal_file_2d(3, 3, os.path.join("goal", "3x3.pl"))
    # 3x4
    create_goal_file_2d(3, 4, os.path.join("goal", "3x4.pl"))
    # 4x4
    create_goal_file_2d(4, 4, os.path.join("goal", "4x4.pl"))

    print("File goal/3x3.pl, goal/3x4.pl e goal/4x4.pl creati con la rappresentazione 2D.")

if __name__ == "__main__":
    main()
