%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% PARAMETRI E COSTANTI
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% #const nr = 3.         % Numero di righe
% #const nc = 4.         % Numero di colonne
% #const maxtime = 25.   % Tempo massimo di ricerca

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 1) DEFINIZIONE DEL DOMINIO
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
domPos(0..(nr*nc - 1)).
tessera(0..(nr*nc - 1)).   % 0 = spazio vuoto

time(0..maxtime).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2) ADIACENZA TRA POSIZIONI
%
% Usando un indice lineare Pos, 
% Pos corrisponde a (r,c) con:
%   r = Pos // nc
%   c = Pos % nc
%
% Adiacenti = stessi spostamenti (su, giu', dx, sx)
% con i controlli di bordo appropriati.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% dx: P2 è P1+1, riga invariata
adiacente(P1,P2) :-
    domPos(P1), domPos(P2),
    P2 == P1 + 1,
    (P1 / nc) == (P2 / nc).

% sx: P2 è P1-1, riga invariata
adiacente(P1,P2) :-
    domPos(P1), domPos(P2),
    P2 == P1 - 1,
    (P1 / nc) == (P2 / nc).

% giù: P2 è P1+nc, e deve restare < nr*nc
adiacente(P1,P2) :-
    domPos(P1), domPos(P2),
    P2 == P1 + nc,
    P2 < nr*nc.

% su: P2 è P1-nc, e deve essere >= 0
adiacente(P1,P2) :-
    domPos(P1), domPos(P2),
    P2 == P1 - nc,
    P2 >= 0.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 3) STATO INIZIALE: definisci come vuoi
%    (qui un esempio generico)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Esempio per un puzzle 3x4: 0..11
% Righe (r) e colonne (c):
% r=0 => col: 0..3 => Pos: 0..3
% r=1 => col: 0..3 => Pos: 4..7
% r=2 => col: 0..3 => Pos: 8..11


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 5) FLUENTI E FRAME AXIOM
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% holds(F, T) indica che il fluente F e' vero al tempo T.
% (Inizialmente, al tempo 0, sappiamo cio' che e' "initially()".)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(F, 0) :- initially(F).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 5.1) REVOCA DEL FLUENTE
% Se al tempo T avviene un'azione che sposta la tessera
% dal (o verso) una certa posizione, revochiamo quel fluente.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% revoca la posizione di una tessera X se X si e' mossa
revoca(posizione_tessera(Tess, Pos), T) :-
   occurs(muovi(Tess, Pos, Pos2), T).

% revoca la posizione di qualunque tessera fosse in Pos
% se una tessera e' arrivata in Pos
revoca(posizione_tessera(Tess, Pos), T) :-
    occurs(muovi(_, Pos2, Pos), T),
    holds(posizione_tessera(Tess, Pos), T).



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 5.2) PERSISTENZA
% Un fluente resta vero a T+1 se era vero a T e non revocato.
% Se abbiamo gia' raggiunto il goal a T, la persistenza si ferma
% (opzionale: cosi' riduciamo la ricerca dopo il goal).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(F, T+1) :-
    holds(F, T),
    not revoca(F, T),
    not goal_reached(T),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 6) AZIONE E POSSIBILITA' D'AZIONE
% L'azione: muovi(Tessera, Pos1, Pos2)
% e' ammissibile se:
%  - Tessera != 0 (non spostiamo lo spazio)
%  - e' adiacente(Pos1,Pos2)
%  - a Pos1 c'e' la Tessera, a Pos2 c'e' lo spazio (0)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
azione(muovi(Tessera, Pos1, Pos2)) :-
    tessera(Tessera), Tessera != 0,
    adiacente(Pos1, Pos2).

possibile(muovi(Tessera, Pos1, Pos2), T) :-
    holds(posizione_tessera(Tessera, Pos1), T),
    holds(posizione_tessera(0,        Pos2), T),
    adiacente(Pos1, Pos2),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 7) SCELTA AZIONE
% In ogni time-step T, si puo' decidere di far avvenire
% qualunque azione "possibile" (oppure nessuna?).
% Di solito si mette un choice, qui usiamo la notazione { }.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
{ occurs(muovi(Tessera, Pos1, Pos2), T) } :-
    possibile(muovi(Tessera, Pos1, Pos2), T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 8) EFFETTI DELL'AZIONE SUL TEMPO SUCCESSIVO
% Se muovi(Tessera, Pos1, Pos2) avviene a T,
% allora al tempo T+1 la Tessera e' in Pos2
% e lo spazio e' in Pos1.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(posizione_tessera(Tessera, Pos2), T+1) :-
    occurs(muovi(Tessera, Pos1, Pos2), T).

holds(posizione_tessera(0, Pos1), T+1) :-
    occurs(muovi(Tessera, Pos1, Pos2), T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 9) VINCOLI
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% 9.1) Se un'azione non e' possibile, non deve avvenire
:- occurs(muovi(Tessera, Pos1, Pos2), T),
   not possibile(muovi(Tessera, Pos1, Pos2), T).

% 9.2) Non possono avvenire due azioni diverse allo stesso T
:- occurs(muovi(T1, _, _), T),
   occurs(muovi(T2, _, _), T),
   T1 != T2.

% 9.3) Vietiamo "backtracking" immediato della stessa tessera:
%     se Tess si sposta (Pos1->Pos2) a T,
%     non deve tornare (Pos2->Pos1) a T+1
:- occurs(muovi(Tess, Pos1, Pos2), T),
   occurs(muovi(Tess, Pos2, Pos1), T+1).

% 9.4) Se il goal e' raggiunto al tempo TG,
%     nessuna azione puo' avvenire dopo TG
:- goal_reached(TG), occurs(_, T), T > TG.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 10) OBIETTIVO
% Il goal e' raggiunto al tempo T se TUTTE le tessere
% soddisfano la configurazione definita dalle clausole "goal(...)"
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
goal_reached(T) :-
    time(T),
    #count {
       (Tess,Pos) : 
          goal(posizione_tessera(Tess, Pos)),
          holds(posizione_tessera(Tess, Pos), T)
    } = nr*nc.

% Non ammettere modelli in cui l'obiettivo non e' raggiunto
:- not goal_reached(_).

:- holds(_, T),
   goal_reached(TG),
   T > TG,
   time(T).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 11) OTTIMIZZAZIONE: MINIMIZZARE T DI RAGGIUNGIMENTO
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#minimize { T : goal_reached(T) }.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 12) OUTPUT (scegli tu)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#show occurs/2.
#show goal_reached/1.
#show holds/2.
