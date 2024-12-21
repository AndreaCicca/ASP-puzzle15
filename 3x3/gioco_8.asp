% Costante: tempo massimo
% #const maxtime = 25.
% clingo initial_state/state_2.pl gioco_8.asp -t8,split --config=crafty -c maxtime=25

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 1) Dominio di X e Y, posizioni e tessere
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
dom(1..3).
posizione(X,Y) :- dom(X), dom(Y).

tessera(0..8).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2) Fluenti
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
fluent(posizione_tessera(Tessera, X, Y)) :-
    tessera(Tessera),
    posizione(X, Y).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 3) Stato iniziale (commentato come esempio)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% initially(posizione_tessera(1, 1, 1)).
% initially(posizione_tessera(7, 1, 2)).
% initially(posizione_tessera(8, 1, 3)).
% initially(posizione_tessera(4, 2, 1)).
% initially(posizione_tessera(5, 2, 2)).
% initially(posizione_tessera(6, 2, 3)).
% initially(posizione_tessera(2, 3, 1)).
% initially(posizione_tessera(0, 3, 2)). % Spazio vuoto
% initially(posizione_tessera(3, 3, 3)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 4) Configurazione obiettivo
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
goal(posizione_tessera(1, 1, 1)).
goal(posizione_tessera(2, 1, 2)).
goal(posizione_tessera(3, 1, 3)).
goal(posizione_tessera(4, 2, 1)).
goal(posizione_tessera(5, 2, 2)).
goal(posizione_tessera(6, 2, 3)).
goal(posizione_tessera(7, 3, 1)).
goal(posizione_tessera(8, 3, 2)).
goal(posizione_tessera(0, 3, 3)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 5) Azione di movimento e definizione di vicinanza
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Singola regola di vicinanza: due posizioni sono adiacenti
% se la distanza di Manhattan è 1
adiacente(X1, Y1, X2, Y2) :-
    posizione(X1, Y1),
    posizione(X2, Y2),
    |X1 - X2| + |Y1 - Y2| == 1.

azione(muovi(Tessera, X1, Y1, X2, Y2)) :-
    tessera(Tessera),
    Tessera != 0,
    adiacente(X1, Y1, X2, Y2).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 6) Possibilità dell’azione
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
possibile(muovi(Tessera, X1, Y1, X2, Y2), T) :-
    holds(posizione_tessera(Tessera, X1, Y1), T),
    holds(posizione_tessera(0, X2, Y2), T),
    adiacente(X1, Y1, X2, Y2),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 7) Scelta dell’azione
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
{ occurs(muovi(Tessera, X1, Y1, X2, Y2), T) } :-
    possibile(muovi(Tessera, X1, Y1, X2, Y2), T),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 8) Effetti delle azioni
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(posizione_tessera(Tessera, X2, Y2), T+1) :-
    occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
    time(T).

holds(posizione_tessera(0, X1, Y1), T+1) :-
    occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 9) Persistenza dei fluenti
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(posizione_tessera(Tessera, X, Y), T+1) :-
    holds(posizione_tessera(Tessera, X, Y), T),
    not occurs(muovi(_, X, Y, _, _), T),
    not occurs(muovi(_, _, _, X, Y), T),
    not goal_reached(T),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 10) Vincoli vari
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Nessuna soluzione se abbiamo stati dopo il tempo TG in cui il goal è raggiunto
:- holds(_, T), goal_reached(TG), T > TG, time(T).

% Vincolo: se un’azione non è possibile non può avvenire
:- occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
   not possibile(muovi(Tessera, X1, Y1, X2, Y2), T),
   time(T).

% Vincolo: non possono avvenire due azioni diverse nello stesso istante
:- occurs(muovi(T1, _, _, _, _), T),
   occurs(muovi(T2, _, _, _, _), T),
   T1 != T2,
   time(T).

% Vincolo: nessuna azione deve avvenire dopo il raggiungimento del goal
:- occurs(_, T),
   T > TG,
   goal_reached(TG),
   time(TG),
   time(T).

% Vincolo: non si va avanti e indietro in due mosse consecutive
:- occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
   occurs(muovi(_, X2, Y2, X1, Y1), T+1).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 11) Euristica: penalizziamo i movimenti che allontanano la tessera dalla posizione goal
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
distanza_manhattan(Tessera, D, T) :-
    tessera(Tessera), Tessera != 0,
    holds(posizione_tessera(Tessera, X1, Y1), T),
    goal(posizione_tessera(Tessera, Xg, Yg)),
    D = |X1 - Xg| + |Y1 - Yg|.

:~ occurs(muovi(Tessera, X1, Y1, X2, Y2), T),
    distanza_manhattan(Tessera, D1, T),
    distanza_manhattan(Tessera, D2, T+1),
    D2 > D1. [D2 - D1@1]

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 12) Tempo e stato iniziale
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
time(0..maxtime).

holds(F, 0) :- initially(F).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 13) Raggiungimento dell’obiettivo
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
goal_reached(T) :-
    time(T),
    #count {
       Tessera, X, Y :
          goal(posizione_tessera(Tessera, X, Y)),
          holds(posizione_tessera(Tessera, X, Y), T)
    } = 9.

% Minimizzare il tempo di raggiungimento del goal
#minimize { T : goal_reached(T) }.

% Assicuriamoci di non ammettere modelli in cui l’obiettivo non è raggiunto
:- not goal_reached(_).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 14) Output
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% #show occurs/2.
% #show possibile/2.
#show holds/2.
#show goal_reached/1.
