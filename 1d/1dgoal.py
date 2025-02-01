import os

def create_goal_file(rows, cols, output_filename):
    """
    Crea un file contenente le clausole goal(posizione_tessera(Tess,Pos)).
    Utilizza una disposizione 'classica' per i puzzle NxM:
      - Tessera 1 in posizione 0,
      - Tessera 2 in posizione 1,
      - ...
      - Tessera (rows*cols - 1) in posizione (rows*cols - 2),
      - Spazio (0) in posizione (rows*cols - 1).
    """
    total = rows * cols
    lines = []
    # Tessere 1..(total - 1) in posizioni da 0..(total - 2)
    for tessera in range(1, total):
        # (tessera, tessera-1)
        lines.append(f"goal(posizione_tessera({tessera},{tessera - 1})).")
    # Spazio (0) in posizione total-1
    lines.append(f"goal(posizione_tessera(0,{total - 1})).")

    with open(output_filename, "w") as f:
        f.write("\n".join(lines) + "\n")

def main():
    # Assicuriamoci che esista la cartella "goal"
    os.makedirs("goal", exist_ok=True)

    # Crea il file 3x3.pl nella cartella goal
    create_goal_file(3, 3, os.path.join("goal", "3x3.pl"))
    # Crea il file 3x4.pl nella cartella goal
    create_goal_file(3, 4, os.path.join("goal", "3x4.pl"))
    # Crea il file 4x4.pl nella cartella goal
    create_goal_file(4, 4, os.path.join("goal", "4x4.pl"))

    print("File goal/3x3.pl, goal/3x4.pl e goal/4x4.pl creati con successo!")

if __name__ == "__main__":
    main()
