./elimina_esempi.sh
python crea_configurazioni_iniziali.py --mixed
# python crea_configurazioni_iniziali.py

python myclingo.py
# python plot.py -a 3 -l 3

# clingo gioco.asp ./goal/4x4.pl ./4x4/initial_state/state_1.pl -c n=4 -c maxtime=25
# clingo gioco_generico.asp ./goal/3x3.pl ./3x3/initial_state/state_1.pl -t 8 -c nr=3 -c nc=3  -c maxtime=50 --time-limit=300
# clingo  gioco_generico.asp ./goal/4x4.pl ./4x4/initial_state/state_1.pl  -c nr=4 -c nc=4  -c maxtime=50 | wc -l