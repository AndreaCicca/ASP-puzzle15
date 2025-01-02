%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 0) Parametri e costanti
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% #const nr = 3.         % Numero di righe (esempio)
% #const nc = 4.         % Numero di colonne (esempio)
% #const maxtime = 25.   % Tempo massimo di ricerca

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 1) Definizione del dominio
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
domR(1..nr).              % Righe
domC(1..nc).              % Colonne

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2) Tessere
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
tessera(0..(nr*nc - 1)).  % 0 rappresenta lo spazio vuoto

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 3) Fluenti
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% fluent(posizione_tessera(Tessera, X, Y)) :-
%     tessera(Tessera),
%     domR(X), domC(Y).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 4) Stato iniziale (vuoto, da completare)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Esempio di uso (commentato):
%
% initially(posizione_tessera(1, 1, 1)).
% initially(posizione_tessera(2, 1, 2)).
% ...
% initially(posizione_tessera(0, nr, nc)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 5) Configurazione obiettivo (vuota, da completare)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Esempio di uso (commentato):
%
% goal(posizione_tessera(1, 1, 1)).
% goal(posizione_tessera(2, 1, 2)).
% ...
% goal(posizione_tessera(0, nr, nc)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 6) Azione di movimento e vicinanza
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% adiacente(X1, Y1, X2, Y2) :-
%     domR(X1), domC(Y1),
%     domR(X2), domC(Y2),
%     |X1 - X2| + |Y1 - Y2| == 1.


adiacente(X, Y, X+1, Y) :- domR(X), domC(Y), domR(X+1), domC(Y).
adiacente(X, Y, X-1, Y) :- domR(X), domC(Y), domR(X-1), domC(Y).
adiacente(X, Y, X, Y+1) :- domR(X), domC(Y), domR(X), domC(Y+1).
adiacente(X, Y, X, Y-1) :- domR(X), domC(Y), domR(X), domC(Y-1).

azione(muovi(Tessera, X1, Y1, X2, Y2)) :-
    tessera(Tessera),
    Tessera != 0,
    adiacente(X1, Y1, X2, Y2).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 7) Possibilità dell’azione
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
possibile(muovi(Tessera, X1, Y1, X2, Y2), T) :-
    holds(posizione_tessera(Tessera, X1, Y1), T),
    holds(posizione_tessera(0, X2, Y2), T),
    adiacente(X1, Y1, X2, Y2),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 8) Scelta dell’azione
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
{ occurs(muovi(Tessera, X1, Y1, X2, Y2), T) } :-
    possibile(muovi(Tessera, X1, Y1, X2, Y2), T),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 9) Effetti delle azioni
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(posizione_tessera(Tessera, X2, Y2), T+1) :-
    occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
    time(T).

holds(posizione_tessera(0, X1, Y1), T+1) :-
    occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 10) Persistenza dei fluenti
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(posizione_tessera(Tessera, X, Y), T+1) :-
    holds(posizione_tessera(Tessera, X, Y), T),
    not occurs(muovi(_, X, Y, _, _), T),
    not occurs(muovi(_, _, _, X, Y), T),
    not goal_reached(T),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 11) Vincoli vari
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% a) Nessuna soluzione se abbiamo stati dopo il tempo TG in cui il goal è raggiunto
:- holds(_, T), goal_reached(TG), T > TG, time(T).

% b) Se un’azione non è possibile non può avvenire
:- occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
   not possibile(muovi(Tessera, X1, Y1, X2, Y2), T),
   time(T).

% c) Non possono avvenire due azioni diverse nello stesso istante
:- occurs(muovi(T1, _, _, _, _), T),
   occurs(muovi(T2, _, _, _, _), T),
   T1 != T2,
   time(T).

:- #count { Tessera : occurs(muovi(Tessera, _, _, _, _), T) } > 1, time(T).

% d) Nessuna azione deve avvenire dopo il raggiungimento del goal
:- occurs(_, T),
   T > TG,
   goal_reached(TG),
   time(TG),
   time(T).

% e) Nessun “avanti e indietro” in due mosse consecutive
:- occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
   occurs(muovi(_, X2, Y2, X1, Y1), T+1).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 12) Euristica: penalizziamo i movimenti
%     che allontanano la tessera dal goal
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% distanza_manhattan(Tessera, D, X1, Y1, T) :-
%     tessera(Tessera), Tessera != 0,
%     holds(posizione_tessera(Tessera, X1, Y1), T),
%     goal(posizione_tessera(Tessera, Xg, Yg)),
%     D = |X1 - Xg| + |Y1 - Yg|.

% :~ occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
%     distanza_manhattan(Tessera, D1, X1, Y1, T),
%     distanza_manhattan(Tessera, D2, X2, Y2, T+1),
%     D2 > D1. [D2 - D1@1]


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 13) Tempo e stato iniziale
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
time(0..maxtime).

holds(F, 0) :- initially(F).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 14) Raggiungimento dell’obiettivo
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
goal_reached(T) :-
    time(T),
    #count {
       Tessera, X, Y :
          goal(posizione_tessera(Tessera, X, Y)),
          holds(posizione_tessera(Tessera, X, Y), T)
    } = nr*nc.

% Minimizzare il tempo di raggiungimento del goal
#minimize { T : goal_reached(T) }.

% Non ammettere modelli in cui l’obiettivo non è raggiunto
:- not goal_reached(_).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 15) Output (scegli cosa mostrare)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% #show occurs/2.
% #show possibile/2.
#show holds/2.
#show goal_reached/1.
