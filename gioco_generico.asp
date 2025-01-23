%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 0) PARAMETRI E COSTANTI
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#const nr = 3.        % Numero di righe (esempio)
#const nc = 4.        % Numero di colonne (esempio)
#const maxtime = 25.  % Tempo massimo di ricerca

domR(1..nr).
domC(1..nc).
time(0..maxtime).

% Tessere da 1..(nr*nc-1)
tessera(1..(nr*nc - 1)).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 3) DEFINIZIONE DELL’AZIONE MUOVI_SPAZIO
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Definizione di adiacenza
% (Le 4 regole che consentono X±1 oppure Y±1, vincolate al dominio)
adiacente(X, Y, X+1, Y) :- domR(X),   domC(Y),   X < nr. 
adiacente(X, Y, X-1, Y) :- domR(X),   domC(Y),   X > 1.
adiacente(X, Y, X, Y+1) :- domR(X),   domC(Y),   Y < nc.
adiacente(X, Y, X, Y-1) :- domR(X),   domC(Y),   Y > 1.

% L’azione è definita per posizioni contigue nel tabellone
azione(muovi_spazio(X1, Y1, X2, Y2)) :-
    adiacente(X1, Y1, X2, Y2).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 4) POSSIBILITA' DELL'AZIONE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Correzione fondamentale:
% --> Adesso verifichiamo che X1,Y1 e X2,Y2 siano adiacenti ANCHE QUI,
%     e non solo nella definizione dell'azione stessa.

possibile(muovi_spazio(X1, Y1, X2, Y2), T) :-
    holds(posizione_spazio(X1, Y1), T),
    holds(posizione_tessera(_, X2, Y2), T),
    adiacente(X1, Y1, X2, Y2),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 5) SCELTA DELL'AZIONE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
{ occurs(muovi_spazio(X1, Y1, X2, Y2), T) } :-
    possibile(muovi_spazio(X1, Y1, X2, Y2), T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 6) TRANSIZIONE DI STATO (EFFETTI)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(posizione_spazio(X2, Y2), T+1) :-
    occurs(muovi_spazio(X1, Y1, X2, Y2), T),
    time(T).

holds(posizione_tessera(Tid, X1, Y1), T+1) :-
    occurs(muovi_spazio(X1, Y1, X2, Y2), T),
    holds(posizione_tessera(Tid, X2, Y2), T),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 7) PERSISTENZA
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Se nessuna azione modifica un fluente tra T e T+1, esso persiste
% E si interrompe la persistenza se abbiamo raggiunto il goal al tempo T
% (evitando di generare stati successivi senza senso)

holds(posizione_spazio(X, Y), T+1) :-
    holds(posizione_spazio(X, Y), T),
    not occurs(muovi_spazio(X, Y, _, _), T),
    not occurs(muovi_spazio(_, _, X, Y), T),
    not goal_reached(T),
    time(T).

holds(posizione_tessera(Tid, X, Y), T+1) :-
    holds(posizione_tessera(Tid, X, Y), T),
    not occurs(muovi_spazio(X, Y, _, _), T),
    not occurs(muovi_spazio(_, _, X, Y), T),
    not goal_reached(T),
    time(T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 8) STATO INIZIALE E GOAL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
holds(F, 0) :- initially(F).

% Goal raggiunto T se:
% - Tutte le tessere sono al posto giusto
% - Lo spazio è nella posizione obiettivo (se specificato)
goal_reached(T) :-
    time(T),
    #count {
       Tid, X, Y : goal(posizione_tessera(Tid, X, Y)),
                   holds(posizione_tessera(Tid, X, Y), T)
    } = (nr*nc - 1),
    goal(posizione_spazio(Gx, Gy)),
    holds(posizione_spazio(Gx, Gy), T).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 9) VINCOLI E OTTIMIZZAZIONE
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Minimizzare il tempo di raggiungimento del goal
#minimize { T : goal_reached(T) }.

% Non accettare modelli in cui il goal non è raggiunto
:- not goal_reached(_).

% Non avvengono due azioni diverse nello stesso T
:- #count { X1,Y1,X2,Y2 : occurs(muovi_spazio(X1, Y1, X2, Y2), T) } > 1, time(T).

% Niente azioni dopo che il goal è stato raggiunto
:- occurs(_, T), goal_reached(TG), T > TG.

% Evitare "avanti e indietro" immediato
:- occurs(muovi_spazio(X1, Y1, X2, Y2), T),
   occurs(muovi_spazio(X2, Y2, X1, Y1), T+1).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 10) OUTPUT
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#show occurs/2.
#show holds/2.
#show goal_reached/1.
