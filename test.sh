./elimina_esempi.sh
python crea_configurazioni_iniziali.py --mixed
python crea_configurazioni_iniziali.py
python conf_iniziali.py
python myclingo.py
python plot.py -a 4 -l 4

# clingo gioco.asp ./goal/4x4.pl ./4x4/initial_state/state_1.pl -c n=4 -c maxtime=25