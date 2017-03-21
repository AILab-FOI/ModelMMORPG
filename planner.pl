% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %
% %%%%%%%%%%%%%%%% Strategija Agenata za ModelMMORPG %%%%%%%%%%%%%%%% %
% %%%%%%%%%%%%%%%%          SWI Prolog code          %%%%%%%%%%%%%%%% %
% %%%%%%% Written by Marko Malikovic & Markus Schatten (2015) %%%%%%% %
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

% %%%%%%%%%%%%%%%%% %
%  UVODNE NAPOMENE  %
% %%%%%%%%%%%%%%%%% %

% In our system we have formalized:
% - Environment in which there is artificial agent
% - Objectives that should be achieved by artificial agent
% - Actions that artificial agent can perform
% - etc...

%  Based on the above formalizations, artificial agent should generate a plan to perform a given quest.

% More specifically, the inputs to the system are the following parameters:
% - About the map
% - About the agent's position on the map
% - About the agent's personal information (eg. Weapons, clothing, shields)
% - About the position of all the other characters, the items and of other things on the map
% - About other characters
% - About how many diamonds agent collected
% - About the position of the NPC who gave the task to agent
% - About spells which an artificial agent learned
% - About Quest he received
% - etc...

% %%%%%%%%%%%%%%%% %
%  PROGRAMSKI KOD  %
% %%%%%%%%%%%%%%%% %

% OVDJE IMA SUVIŠNIH PREDIKATA KOJE TREBA BRISATI:

:- dynamic location/4.
:- dynamic ownership/3.
:- dynamic diamonds/2.
:- dynamic zeny/2.
:- dynamic ability/2.
:- dynamic done_quest/2.
:- dynamic failed_quest/3.
:- dynamic roasted_maggots/2.
:- dynamic maggot_slimes/2.
:- dynamic cherry_cakes/2.
:- dynamic beers/2.
:- dynamic exp/2.
:- dynamic serf_hat/2.
:- dynamic bug_leg/2.
:- dynamic scorpion_stingers/2.
:- dynamic arrows/2.
:- dynamic bows/2.
:- dynamic cactus_drinks/2.
:- dynamic boots/2.
:- dynamic clothes/2.
:- dynamic plan/1.
:- dynamic plan_list/1.
:- dynamic waiting_quest/3.
:- dynamic killed_giant_maggots/2.
:- dynamic quest_no/4.
:- dynamic quest_sign/3.
:- dynamic npc_message/3.
:- dynamic party/2.
:- dynamic social_network/3.


% %%%%%%%%%%%%%%%% %
%  STANJE SUSTAVA  %
% %%%%%%%%%%%%%%%% %

% On the world are the following:
% ------------------------------

% Agents:

location(a,tonori,78,67).   % Agent a se nalazi na mapi Tonori u Tulimshar Suburbs
location(a1,tonori,74,52).
location(a2,tonori,54,69).
location(a3,tonori,23,39).
location(a4,tonori,11,58).
location(a5,tonori,76,6).
location(a6,tonori,95,37).
location(a7,tonori,38,2).
location(a8,tonori,27,66).

% Various places

location(tulimshar_suburbs,tonori,78,67).
location(mine,tonori,20,30).
location(graveyard,argaes,70,75).

% Entrances and exits:

location(exit_from_sorfinas_room,tonori,83,73).
location(exit_from_tanishas_house,tonori,93,83).
location(entrance_into_mine,tonori,73,63).

% Exits from the maps:

location(exit_from_tonori,tonori,100,100).

% Various things:

location(red_carpet,tonori,80,70).
location(chest_in_sorfinas_room,tonori,81,70).

% NPCs:

location(entertainer,tonori,85,75).
location(trader,tonori,85,76).
location(bernard,tonori,85,77).
location(mikhail,tonori,85,78).
location(sarah,tonori,85,79).
location(vincent,tonori,85,80).
location(sandra,tonori,85,81).
location(lieutenant_dausen_in_sandstorm_desert,tonori,90,86).
location(stewen,tonori,95,95).
location(nickos,tonori,85,95).
location(sorfina,tonori,85,96).
location(tanisha,tonori,85,97).
location(hasan,tonori,85,87).
location(kaan,tonori,85,75).
location(nathan,tonori,71,61).
location(naem,tonori,69,59).
location(dyrin,argaes,50,50).

% Cudovista:

location(monster,tonori,73,59).
location(monster,tonori,23,12).
location(monster,tonori,57,6).
location(monster,tonori,78,31).
location(monster,tonori,33,67).
location(monster,tonori,79,20).
location(monster,tonori,20,9).
location(monster,tonori,3,96).
location(monster,tonori,85,72).
location(monster,tonori,56,86).
location(monster,tonori,34,89).
location(monster,tonori,20,59).
location(monster,tonori,39,8).
location(monster,tonori,86,66).
location(monster,tonori,45,72).
location(monster,tonori,29,12).
location(monster,tonori,2,69).
location(monster,tonori,7,60).
location(monster,tonori,92,57).
location(monster,tonori,30,23).

% Maggots:

location(maggot,tonori,79,44).
location(maggot,tonori,69,10).
location(maggot,tonori,18,49).
location(maggot,tonori,76,96).
location(maggot,tonori,42,55).
location(maggot,tonori,2,69).
location(maggot,tonori,59,12).
location(maggot,tonori,50,12).
location(maggot,tonori,47,82).
location(maggot,tonori,33,10).

% Cave Maggots:

location(cave_maggot,tonori,70,48).
location(cave_maggot,tonori,61,19).
location(cave_maggot,tonori,11,40).
location(cave_maggot,tonori,70,99).
location(cave_maggot,tonori,49,52).
location(cave_maggot,tonori,12,60).
location(cave_maggot,tonori,50,18).
location(cave_maggot,tonori,58,10).
location(cave_maggot,tonori,41,88).
location(cave_maggot,tonori,37,19).

% Giant Maggots:

location(giant_maggot,tonori,89,34).
location(giant_maggot,tonori,59,20).
location(giant_maggot,tonori,8,39).
location(giant_maggot,tonori,66,86).
location(giant_maggot,tonori,52,45).
location(giant_maggot,tonori,12,59).
location(giant_maggot,tonori,69,2).
location(giant_maggot,tonori,60,2).
location(giant_maggot,tonori,57,92).
location(giant_maggot,tonori,23,20).

% Scorpions:

location(scorpion,tonori,19,33).
location(scorpion,tonori,26,67).
location(scorpion,tonori,6,88).
location(scorpion,tonori,31,43).
location(scorpion,tonori,67,89).
location(scorpion,tonori,20,50).
location(scorpion,tonori,15,13).
location(scorpion,tonori,76,13).
location(scorpion,tonori,44,66).
location(scorpion,tonori,86,44).
location(scorpion,tonori,89,30).
location(scorpion,tonori,59,49).
location(scorpion,tonori,8,96).
location(scorpion,tonori,66,55).
location(scorpion,tonori,72,69).
location(scorpion,tonori,12,12).
location(scorpion,tonori,69,12).
location(scorpion,tonori,60,82).
location(scorpion,tonori,57,30).
location(scorpion,tonori,23,37).

% Bats:

location(bat,tonori,59,64).
location(bat,tonori,49,30).
location(bat,tonori,38,29).
location(bat,tonori,96,76).
location(bat,tonori,62,35).
location(bat,tonori,22,49).
location(bat,tonori,79,32).
location(bat,tonori,30,32).
location(bat,tonori,27,62).
location(bat,tonori,53,30).

% Angry Scorpions:

location(angry_scorpion,tonori,89,34).
location(angry_scorpion,tonori,79,0).
location(angry_scorpion,tonori,68,9).
location(angry_scorpion,tonori,66,46).
location(angry_scorpion,tonori,92,5).
location(angry_scorpion,tonori,52,19).
location(angry_scorpion,tonori,49,62).
location(angry_scorpion,tonori,60,62).
location(angry_scorpion,tonori,57,32).
location(angry_scorpion,tonori,23,60).

% Spiky Mushrooms:

location(spiky_mushroom,tonori,80,35).
location(spiky_mushroom,tonori,59,30).
location(spiky_mushroom,tonori,60,19).
location(spiky_mushroom,tonori,66,46).
location(spiky_mushroom,tonori,72,45).
location(spiky_mushroom,tonori,5,59).
location(spiky_mushroom,tonori,69,74).
location(spiky_mushroom,tonori,85,6).
location(spiky_mushroom,tonori,35,39).
location(spiky_mushroom,tonori,93,20).

% Fire Goblins:

location(fire_goblin,tonori,50,65).
location(fire_goblin,tonori,89,0).
location(fire_goblin,tonori,90,49).
location(fire_goblin,tonori,36,76).
location(fire_goblin,tonori,42,75).
location(fire_goblin,tonori,35,89).
location(fire_goblin,tonori,99,44).
location(fire_goblin,tonori,55,36).
location(fire_goblin,tonori,5,69).
location(fire_goblin,tonori,63,50).

% Ice Goblins:

location(ice_goblin,tonori,60,55).
location(ice_goblin,tonori,99,10).
location(ice_goblin,tonori,100,59).
location(ice_goblin,tonori,46,66).
location(ice_goblin,tonori,52,65).
location(ice_goblin,tonori,45,79).
location(ice_goblin,tonori,89,54).
location(ice_goblin,tonori,45,46).
location(ice_goblin,tonori,15,59).
location(ice_goblin,tonori,73,60).

% Sea Slimes:

location(sea_slime,tonori,60,55).
location(sea_slime,tonori,99,10).
location(sea_slime,tonori,100,59).
location(sea_slime,tonori,46,66).
location(sea_slime,tonori,52,65).
location(sea_slime,tonori,45,79).
location(sea_slime,tonori,89,54).
location(sea_slime,tonori,45,46).
location(sea_slime,tonori,15,59).
location(sea_slime,tonori,73,60).

% Red Scorpions:

location(red_scorpion,tonori,70,65).
location(red_scorpion,tonori,89,20).
location(red_scorpion,tonori,90,69).
location(red_scorpion,tonori,56,76).
location(red_scorpion,tonori,62,75).
location(red_scorpion,tonori,55,89).
location(red_scorpion,tonori,99,64).
location(red_scorpion,tonori,55,56).
location(red_scorpion,tonori,25,69).
location(red_scorpion,tonori,83,70).

% Black Scorpions:

location(black_scorpion,tonori,51,86).
location(black_scorpion,tonori,63,44).
location(black_scorpion,tonori,75,82).
location(black_scorpion,tonori,37,90).
location(black_scorpion,tonori,49,98).
location(black_scorpion,tonori,30,69).
location(black_scorpion,tonori,72,87).
location(black_scorpion,tonori,34,75).
location(black_scorpion,tonori,6,83).
location(black_scorpion,tonori,68,91).

% Atributi agenata:
% ----------------

% Level na kojem se nalaze agenti:

ownership(a,level,22).
ownership(a1,level,1).
ownership(a2,level,1).
ownership(a3,level,1).
ownership(a4,level,1).
ownership(a5,level,1).
ownership(a6,level,1).
ownership(a7,level,1).
ownership(a8,level,1).

% Oruzje agenata:

ownership(a,arm,gun).
ownership(a1,arm,gun).
ownership(a2,arm,gun).
ownership(a3,arm,mace).
ownership(a4,arm,gun).
ownership(a5,arm,sword).
ownership(a6,arm,gun).
ownership(a7,arm,sword).
ownership(a8,arm,mace).

% Odjeca agenata:

% Nas agent a nema nista na pocetku
ownership(a1,clothes,uniform).
ownership(a2,clothes,uniform).
ownership(a3,clothes,raincoat).
ownership(a4,clothes,uniform).
ownership(a5,clothes,uniform).
ownership(a6,clothes,uniform).
ownership(a7,clothes,raincoat).
ownership(a8,clothes,sweater).

% Stit agenata:

ownership(a,shield,metal).
ownership(a1,shield,wood).
ownership(a2,shield,wood).
ownership(a3,shield,metal).
ownership(a4,shield,wood).
ownership(a5,shield,wood).
ownership(a6,shield,wood).
ownership(a7,shield,wood).
ownership(a8,shield,bark).

% Broj dijamanata koje su skupili agenti:

ownership(a,diamonds,0).
ownership(a1,diamonds,0).
ownership(a2,diamonds,0).
ownership(a3,diamonds,0).
ownership(a4,diamonds,0).
ownership(a5,diamonds,0).
ownership(a6,diamonds,0).
ownership(a7,diamonds,0).
ownership(a8,diamonds,0).

% Novci koje imaju agenti:

ownership(a,zeny,1200).
ownership(a1,zeny,13).
ownership(a2,zeny,1).
ownership(a3,zeny,35).
ownership(a4,zeny,10).
ownership(a5,zeny,108).
ownership(a6,zeny,0).
ownership(a7,zeny,97).
ownership(a8,zeny,100).

% Broj Giant Maggots koje je do sada ubio pojedini agent:

ownership(a,killed_giant_maggots,0).
ownership(a1,killed_giant_maggots,0).
ownership(a2,killed_giant_maggots,0).
ownership(a3,killed_giant_maggots,0).
ownership(a4,killed_giant_maggots,0).
ownership(a5,killed_giant_maggots,0).
ownership(a6,killed_giant_maggots,0).
ownership(a7,killed_giant_maggots,0).
ownership(a8,killed_giant_maggots,0).

% Roasted Maggots koje imaju agenti:

ownership(a,roasted_maggots,2).
ownership(a1,roasted_maggots,0).
ownership(a2,roasted_maggots,2).
ownership(a3,roasted_maggots,5).
ownership(a4,roasted_maggots,0).
ownership(a5,roasted_maggots,1).
ownership(a6,roasted_maggots,1).
ownership(a7,roasted_maggots,8).
ownership(a8,roasted_maggots,0).

% Maggot Slimes koje imaju agenti:

ownership(a,maggot_slimes,8).
ownership(a1,maggot_slimes,4).
ownership(a2,maggot_slimes,0).
ownership(a3,maggot_slimes,0).
ownership(a4,maggot_slimes,5).
ownership(a5,maggot_slimes,0).
ownership(a6,maggot_slimes,0).
ownership(a7,maggot_slimes,0).
ownership(a8,maggot_slimes,3).

% Cherry Cakes koje imaju agenti:

ownership(a,cherry_cakes,0).
ownership(a1,cherry_cakes,0).
ownership(a2,cherry_cakes,0).
ownership(a3,cherry_cakes,0).
ownership(a4,cherry_cakes,0).
ownership(a5,cherry_cakes,0).
ownership(a6,cherry_cakes,0).
ownership(a7,cherry_cakes,0).
ownership(a8,cherry_cakes,0).

% Beers koje imaju agenti:

ownership(a,beers,4).
ownership(a1,beers,3).
ownership(a2,beers,0).
ownership(a3,beers,2).
ownership(a4,beers,0).
ownership(a5,beers,1).
ownership(a6,beers,1).
ownership(a7,beers,2).
ownership(a8,beers,0).

% EXPs koje imaju agenti:

ownership(a,exp,0).
ownership(a1,exp,0).
ownership(a2,exp,0).
ownership(a3,exp,0).
ownership(a4,exp,0).
ownership(a5,exp,0).
ownership(a6,exp,0).
ownership(a7,exp,0).
ownership(a8,exp,0).

% Serf Hat koje imaju agenti:

ownership(a,serf_hat,4).
ownership(a1,serf_hat,3).
ownership(a2,serf_hat,0).
ownership(a3,serf_hat,2).
ownership(a4,serf_hat,0).
ownership(a5,serf_hat,1).
ownership(a6,serf_hat,1).
ownership(a7,serf_hat,2).
ownership(a8,serf_hat,0).

% Scorpion Stingers koje imaju agenti:

ownership(a,scorpion_stingers,2).
ownership(a1,scorpion_stingers,1).
ownership(a2,scorpion_stingers,17).
ownership(a3,scorpion_stingers,23).
ownership(a4,scorpion_stingers,0).
ownership(a5,scorpion_stingers,7).
ownership(a6,scorpion_stingers,13).
ownership(a7,scorpion_stingers,27).
ownership(a8,scorpion_stingers,7).

% Arrows koje imaju agenti:

ownership(a,arrows,0).
ownership(a1,arrows,0).
ownership(a2,arrows,0).
ownership(a3,arrows,0).
ownership(a4,arrows,0).
ownership(a5,arrows,0).
ownership(a6,arrows,0).
ownership(a7,arrows,0).
ownership(a8,arrows,0).

% Bows koje imaju agenti:

ownership(a,bows,0).
ownership(a1,bows,0).
ownership(a2,bows,0).
ownership(a3,bows,0).
ownership(a4,bows,0).
ownership(a5,bows,0).
ownership(a6,bows,0).
ownership(a7,bows,0).
ownership(a8,bows,0).

% Cactus Drinks koje imaju agenti:

ownership(a,cactus_drinks,0).
ownership(a1,cactus_drinks,0).
ownership(a2,cactus_drinks,0).
ownership(a3,cactus_drinks,0).
ownership(a4,cactus_drinks,0).
ownership(a5,cactus_drinks,0).
ownership(a6,cactus_drinks,0).
ownership(a7,cactus_drinks,0).
ownership(a8,cactus_drinks,0).

% Boots koje imaju agenti:

ownership(a,boots,0).
ownership(a1,boots,0).
ownership(a2,boots,0).
ownership(a3,boots,0).
ownership(a4,boots,0).
ownership(a5,boots,0).
ownership(a6,boots,0).
ownership(a7,boots,0).
ownership(a8,boots,0).

% Bug Legs koje imaju agenti:

ownership(a,bug_legs,0).
ownership(a1,bug_legs,0).
ownership(a2,bug_legs,0).
ownership(a3,bug_legs,0).
ownership(a4,bug_legs,0).
ownership(a5,bug_legs,0).
ownership(a6,bug_legs,0).
ownership(a7,bug_legs,0).
ownership(a8,bug_legs,0).

% Atributi cudovista:
% ------------------

% Oruzje cudovista:

ownership(m1,arm,mace).
ownership(m2,arm,mace).
ownership(m3,arm,sword).
ownership(m4,arm,sword).
ownership(m5,arm,sword).
ownership(m6,arm,gun).
ownership(m7,arm,sword).
ownership(m8,arm,mace).
ownership(m9,arm,mace).
ownership(m10,arm,mace).
ownership(m11,arm,sword).
ownership(m12,arm,sword).
ownership(m13,arm,gun).
ownership(m14,arm,sword).
ownership(m15,arm,sword).
ownership(m16,arm,mace).
ownership(m17,arm,sword).
ownership(m18,arm,gun).
ownership(m19,arm,sword).
ownership(m20,arm,mace).

% Stit cudovista:

ownership(m1,shield,bark).
ownership(m2,shield,wood).
ownership(m3,shield,wood).
ownership(m4,shield,wood).
ownership(m5,shield,metal).
ownership(m6,shield,wood).
ownership(m7,shield,wood).
ownership(m8,shield,bark).
ownership(m9,shield,bark).
ownership(m10,shield,wood).
ownership(m11,shield,metal).
ownership(m12,shield,wood).
ownership(m13,shield,wood).
ownership(m14,shield,wood).
ownership(m15,shield,wood).
ownership(m16,shield,bark).
ownership(m17,shield,wood).
ownership(m18,shield,wood).
ownership(m19,shield,wood).
ownership(m20,shield,bark).

% Atributi oruzja:
% ---------------

% Snaga oruzja:

stronger(gun,sword).
stronger(gun,mace).
stronger(mace,sword).

% Atributi stitova:
% ----------------

% Cvrstoca stita:

firmer(metal,wood).
firmer(metal,bark).
firmer(wood,bark).

% Certain items are (in a certain percentage) dropped by:
% ------------------------------------------------------

dropped(bug_legs,maggot,4).
dropped(bug_legs,cave_maggot,4).
dropped(bug_legs,scorpion,7).
dropped(bug_legs,bat,4).
dropped(bug_legs,angry_scorpion,7).
dropped(bug_legs,spiky_mushroom,0.5).
dropped(bug_legs,fire_goblin,8).
dropped(bug_legs,ice_goblin,8).
dropped(bug_legs,sea_slime,5).
dropped(bug_legs,red_scorpion,5).
dropped(bug_legs,giant_maggot,7.5).
dropped(bug_legs,black_scorpion,8).
dropped(maggot_slimes,bat,8).
dropped(maggot_slimes,black_scorpion,8).
dropped(maggot_slimes,cave_maggot,8).
dropped(maggot_slimes,fire_goblin,8).
dropped(maggot_slimes,giant_maggot,7.5).
dropped(maggot_slimes,ice_goblin,8).
dropped(maggot_slimes,maggot,8).
dropped(maggot_slimes,red_scorpion,5).
dropped(maggot_slimes,scorpion,7).
dropped(maggot_slimes,sea_slime,5).
dropped(maggot_slimes,spiky_mushroom,0.5).
dropped(roasted_maggots,bat,1.5).
dropped(roasted_maggots,cave_maggot,1.5).
dropped(roasted_maggots,maggot,1.5).
dropped(cherry_cakes,giant_maggot,1).
dropped(cherry_cakes,santa_slime,5).
dropped(cherry_cakes,yellow_slime,1).
dropped(cactus_drinks,maggots,1.5).
dropped(cactus_drinks,cave_maggot,1.5).
dropped(cactus_drinks,bats,1.5).
dropped(cactus_drinks,spiky_mushroom,1.5).
dropped(cactus_drinks,fire_goblin,1.5).
dropped(cactus_drinks,ice_goblin,1.5).
dropped(cactus_drinks,green_slime,1).
dropped(cactus_drinks,yellow_slime,3.5).
dropped(cactus_drinks,blue_slime,5).
dropped(cactus_drinks,giant_maggot,50).
dropped(angry_scorpion_stingers,angry_scorpion,7).
dropped(iron_potions,spiky_mushroom,8).
dropped(white_fur,fluffy,8).
dropped(white_fur,moggun,6).
dropped(boots,red_slime,2.5).

% Atributi questova:
% -----------------

% Quest-ovi koje su od NPC-a dobili pojedini agenti ali ih jos nisu krenuli rjesavati (ovi podaci dolaze izvana iz igre i zapisuju se ovdje):

/*
waiting_quest(npc,a,tutorial).
waiting_quest(npc,a,bernard).
waiting_quest(npc,a,mikhail).
waiting_quest(npc,a,sarah).
waiting_quest(npc,a,vincent).
waiting_quest(npc,a,sandra).
waiting_quest(npc,a,lieutenant_dausen).
waiting_quest(npc,a,emote_skill).
waiting_quest(npc,a,miners_quest).
waiting_quest(npc,a,letter_quest).
*/

% Significance of quest for agent:

quest_sign(a,tutorial,100).
quest_sign(a,maggots,95).
quest_sign(a,sandra,90).
quest_sign(a,lieutenant_dausen,60).
quest_sign(a,emote_skill,40).
quest_sign(a,miners_quest,15).

% Redni brojevi odnosno redosljed po kojem neki agent treba rješavati Questove (izraèunava se na temelju gornjih osobina questova i povremeno se ponovo preraèunava):

quest_no(npc,a,miners_quest,5).
quest_no(npc,a,tutorial,4).
quest_no(npc,a,sandra,3).
quest_no(npc,a,lieutenant_dausen,2).
quest_no(npc,a,emote_skill,1).

% Sorting quests of an agent by priority:
% --------------------------------------

sort_quests(A) :-
     waiting_quest(NPC1,A,Q1),
     waiting_quest(NPC2,A,Q2),
     quest_sign(A,Q1,QS1),
     quest_sign(A,Q2,QS2),
     quest_no(NPC1,A,Q1,QN1),
     quest_no(NPC2,A,Q2,QN2),
     QS1>QS2,
     QN1>QN2
     ->
     retract(quest_no(NPC1,A,Q1,QN1)),
     retract(quest_no(NPC2,A,Q2,QN2)),
     assert(quest_no(NPC1,A,Q1,QN2)),
     assert(quest_no(NPC2,A,Q2,QN1)),
     sort_quests(A);
     true.

% Temeljne akcije:
% ---------------

% Rekurzivna specifikacija akcije "Nas agent A na mapi M hoda na lokaciju (X,Y)":

walk_to_location(A,M,X,Y) :-
     location(A,M,Xa,Ya),                                % Agent A se nalazi na mapi M na lokaciji (Xa,Ya)
    (Xa < X, NewXa is Xa+1 ->                            % Ako se agent gibanjem u desno priblizava lokaciji (X,Y)
          retract(location(A,M,Xa,Ya)),                  % Agent A vise nije na koordinatama (Xa,Ya)
          assert(location(A,M,NewXa,Ya)),                % Agent A se je premjestio na koordinate (Xa+1,Ya) (ostaje na istoj mapi)
          assert(move(A,M,Xa,Ya,M,NewXa,Ya)),            % Dodaj "Pomak agenta A sa (Xa,Ya) na (Xa+1,Ya)"
          assert(plan(move(A,M,Xa,Ya,M,NewXa,Ya))),
          walk_to_location(A,M,X,Y);                     % Ponovno pozovi akciju "walk_to_location(A,X,Y)"
     Xa > X, NewXa is Xa-1 ->                            % Ako se agent gibanjem u lijevo priblizava lokaciji (X,Y)
          retract(location(A,M,Xa,Ya)),                  % Agent A vise nije na koordinatama (Xa,Ya)
          assert(location(A,M,NewXa,Ya)),                % Agent A se je premjestio na koordinate (Xa-1,Ya)
          assert(move(A,M,Xa,Ya,M,NewXa,Ya)),            % Dodaj "Pomak agenta A sa (Xa,Ya) na (Xa-1,Ya)"
          assert(plan(move(A,M,Xa,Ya,M,NewXa,Ya))),
          walk_to_location(A,M,X,Y);                     % Ponovno pozovi akciju "walk_to_location(A,M,X,Y)"
     Ya < Y, NewYa is Ya+1 ->                            % Ako se agent gibanjem prema gore priblizava lokaciji (X,Y)
          retract(location(A,M,Xa,Ya)),                  % Agent A vise nije na koordinatama (Xa,Ya)
          assert(location(A,M,Xa,NewYa)),                % Agent A se je premjestio na koordinate (Xa,Ya+1)
          assert(move(A,M,Xa,Ya,Xa,NewYa)),              % Dodaj "Pomak agenta A sa (Xa,Ya) na (Xa,Ya+1)"
          assert(plan(move(A,M,Xa,Ya,M,Xa,NewYa))),
          walk_to_location(A,M,X,Y);                     % Ponovno pozovi akciju "walk_to_location(A,M,X,Y)"
     Ya > Y, NewYa is Ya-1 ->                            % Ako se agent gibanjem prema dolje priblizava lokaciji (X,Y)
          retract(location(A,M,Xa,Ya)),                  % Agent A vise nije na koordinatama (Xa,Ya)
          assert(location(A,M,Xa,NewYa)),                % Agent A se je premjestio na koordinate (Xa,Ya-1)
          assert(move(A,M,Xa,Ya,M,Xa,NewYa)),            % Dodaj "Pomak agenta A sa (Xa,Ya) na (Xa,Ya-1)"
          assert(plan(move(A,M,Xa,Ya,M,Xa,NewYa))),
          walk_to_location(A,M,X,Y);                     % Ponovno pozovi akciju "walk_to_location(A,M,X,Y)"
      Xa == X, Ya == Y -> true).                         % Ako je agent dosao do pozicije (X,Y) onda je rezultat true

% Akcija kojom agent A hoda na sluèajnu lokaciju na mapi M na kojoj se trenutno nalazi:

random_walk(A) :-
    location(A,M,Xa,Ya),
    random(1,101,RLX),
    random(1,101,RLY),
    walk_to_location(A,M,RLX,RLY),
    assert(plan(talk(A,A,'I came to the random location.'))).

% Akcija kojom agent A ide okolo i ubija mob-ove tako da prikuplja iteme da bi ih na kraju imao N. Agent ubija odredene mob-ove ovisno o time koje iteme skuplja:

collect_items(A,Item,N) :-
     (ownership(A,Item,I),
     I<N,
     dropped(Item,Mob,P),
     location(A,M,XA,YA),                                              % Ako se agent nalazi na lokaciji (XA,YA)
     location(Mob,M,XMob,YMob),                                        % ... i ako se Mob nalazi na lokaciji (XMob,YMob)
     XAXMobDiff is XA-XMob, XAXMobDiff<30, XAXMobDiff>(-30),           % ... i ako je Mob na udaljenosti manjoj od 30 po x-u od agenta
     YAYMobDiff is YA-YMob, YAYMobDiff<30, YAYMobDiff>(-30)            % ... i ako je Mob na udaljenosti manjoj od 30 po y-u od agenta
     ->
     walk_to_location(A,M,XMob,YMob),                                  % ... tada hodaj na lokaciju gdje je Mob i ...
     assert(plan(talk(A,A,'Here is one Mob. I will kill him :D'))),
     retract(location(Mob,M,XMob,YMob)),
     retract(ownership(A,Item,I)),
     NewI is I+1, assert(ownership(A,Item,NewI)),
     collect_items(A,Item,N)).

% Akcije:
% ------

% Neke od akcija koje cemo izmodelirati:

% - Hodaj na tu i tu lokaciju
% - Ubi cudoviste
% - Uzmi dijamant
% - Razgovaraj s nekim likom (zbog razmjene znanja, suradnje, konflikta, ...)
% - Kupi oruzje
% - ...

% Rekurzivne akcije imaju slijedecu formu:

%   Akcija :- Preduvjeti (lista cinjenica koje moraju biti tocne da bi se akcija izvela) ili akcije
%             Brisanja (lista cinjenica koje vise nece biti tocne nakon izvedene akcije)
%             Dodavanja (lista cinjenica koje ce postati istinite nakon izvedene akcije)

% Ako u interaktivnom modu pozivamo akciju npr. "walk_to_location(a,m,x,y)." onda dobivamo odgovor "true" ako se ta akcija trenutno moze izvesti
% Ako u interaktivnom modu pozivamo akciju npr. "walk_to_location(a,m,x,y)." onda dobivamo odgovor "false" ako se ta akcija trenutno ne moze izvesti
% Nakon sto pozovemo neku akciju i akcija se moze izvesti tada sustav mijenja stanje u novo i ostaje u novom stanju dok ceka nasu novu naredbu

% U interaktivnom modu sa "listing(location)." dobijemo sve trenutne instance predikata "location"
% U interaktivnom modu sa "listing(move)." dobijemo sve izvedene instance predikata "move"
% Mozemo nizati vise akcija na slijedeci nacin: "walk_to_location(a,m,x1,y1), walk_to_location(a,m,x2,y2)."

% Nerekurzivne akcije imaju slijedecu formu:

% Akcija :- Preduvjeti (lista cinjenica koje moraju biti tocne da bi se akcija izvela)
%           Brisanja (lista cinjenica koje vise nece biti tocne nakon izvedene akcije)
%           Dodavanja (lista cinjenica koje ce postati istinite nakon izvedene akcije)

% U nerekurzivnim specifikacijama akcija, preduvjeti ne sadrze druge akcije

% Quests
% ------

% Quests are tasks usually given by NPCs

% Quests can include simple missions like:
%  - Collecting items
%  - Talking to several NPCs
%  - ...

% but also more complicated things like:
%  - solving puzzles
%  - winning a boss fight
%  - ...

% Some quests have requirements like:
%  - having completed another quest before
%  - being at a certain level or above

% Some have costs like items or zeny

% Every quest will reward agent with something. The rewards can be:
%  - EXP
%  - zeny
%  - items
%  - equipment
%  - Daily Points
%  - Boss Points
%  - Skills
%  - Magic
%  - Spells
%  - ...

% Note that EXP rewards will grant the total amount, meaning they don't get cut off when reaching a new level so you can also raise more than a single level while completing a Quest.
% In the Quest tables there's a level line telling you either the required level to do this Quest or that this level is just recommended.

% Some Quests are special:
%  - Daily Quests - can be done several times each day
%  - Annual Quests - can only be done in a certain time of the year

% Other Quests are different from the others but still considered as Quests: Skills, Malivox, Candor and others.

% %%%%%%%%%%%%%%%%%%%%%%%%% %
%  Low Level Quests (1-20)  %
% %%%%%%%%%%%%%%%%%%%%%%%%% %

% The recommended levels in the Low Level Quests strongly depend on how you distributed your Status Points - more than for other higher level Quests.
% If you distributed your stats well you might be able to do a Quest earlier, if your stats are rather bad you might end up failing even at a higher level than recommended.

% Quest: Tutorial
% ---------------

% Starting Location: Tulimshar Suburbs, north from the big Tulimshar town (at the moment the only town of Tonori Continent)
% Level: 1
% Redoable: No
% Prerequisites: None
% Reward: 1 Cotton Shirt, 1 Knife, 1 Sling Shot, 500 Sling Bulletts, 1 Ragged Shorts, 50 GP
% Costs: ???

% What To Do:

%     Walk up to the red carpet and Sorfina will tell you to open the chest in the room.
%     Take the Cotton Shirt in it and equip it.
%     Talk to Sorfina after you've equipped the Cotton Shirt.
%     Sorfina then gives you more information on where you are and etc.
%     Exit the room.

% Akcija kojom nas agent A obavlja quest Tutorial jer mu ga je zadao NPC:

do_quest(NPC,A,tutorial) :-
%  Preduvjeti:
     ownership(A,level,La), La>=1,                                                     % Agent je najmanje na levelu 1
     location(tanisha,M,TanishaX,TanishaY),
     location(red_carpet,M,XRCT,YRCT),                          % Red Carpet se nalazi na mapi M na lokaciji (XRCT,YRCT)
     location(chest_in_sorfinas_room,M,XCSR,YCSR),
     location(exit_from_sorfinas_room,M,XESR,YESR),
     waiting_quest(NPC,A,tutorial),                                          % Ovaj quest se nalazi na popisu agentovih questova koje treba obaviti
     \+ done_quest(A,tutorial),                                              % Agent nije jos obavio ovaj quest
%  Brisanja:
     % Nema brisanja
%  Dodavanja:
   % Basics:
   % ------
     assert(plan(talk(A,A,'Otvorio sam oci!'))), % Dodaj cinjenicu da je agent rekao sam sebi ono što je u navodnicima
     assert(plan(talk(sorfina,A,'Sorfina objasnjava nasem agentu sta mu se je dogodilo. Na kraju ga pita "Do you have a name?"'))), % Dodaj cinjenicu da je agent rekao Entertaineru ono sto je u navodnicima
     assert(plan(talk(A,sorfina,A))),
     assert(plan(talk(sorfina,A,'Well (ovdje ide ime agenta), what else can you tell me about yourself?'))),
     assert(plan(talk(A,sorfina,'Umm... I... I do not remember anything...'))),
     assert(plan(talk(sorfina,A,'Tu jos tece konverzacija... Sorfina daje upute agentu kako se moze kretati i slicno. Na kraju mu daje uputu da ode na crveni tepih'))),
     walk_to_location(A,M,XRCT,YRCT),                                        % Agent je odsetao na Red Carpet
     assert(plan(talk(sorfina,A,'Very good! I am glad you are recovering. Now you should get dressed again.'))), % Dodaj cinjenicu da je agent rekao Entertaineru ono sto je u navodnicima
     assert(plan(talk(sorfina,A,'In that chest there are some clothes you can take.'))),
     walk_to_location(A,M,XCSR,YCSR),                                        % Agent je odsetao do chest-a
     assert(ownership(A,clothes,cotton_shirt)),
     assert(plan(talk(A,sorfina,'Sorfina, I equipped myself with a cotton shirt.'))),
     assert(plan(talk(sorfina,A,'OK, I give you more information on where you are and etc...'))),
     walk_to_location(A,M,XESR,YESR),                                        % Agent izlazi iz sobe
   % Training:
   % --------
     assert(plan(talk(tanisha,A,'I give you the knife. Kill 5 maggots as training.'))),
     % Ubijanje Giant Maggot-a naokolo (u ovom slucaju treba ubiti 5 Maggota):
     killing_giant_maggots(A,5),
     walk_to_location(A,M,TanishaX,TanishaY),
     assert(plan(talk(A,tanisha,'I killed 5 Giant Maggots!'))),
     assert(plan(talk(tanisha,A,'Great, I give you 5*6 EXPs.'))),
     ownership(A,zeny,zenyA),
     retract(ownership(A,zeny,zenyA)),
     NewzenyA is zenyA+5*6,
     assert(ownership(A,zeny,NewzenyA)),
     assert(plan(talk(tanisha,A,'I inform you about things such as status points, since you just leveled up.'))),
     assert(plan(talk(A,A,'Now, I check out my Status Points and try to increase my stats. For starters, it is advisable to increase my Dexterity (at first), Strength and Vitality. Intelligence will be useful later in the game, when I know a bit of magic. For more information on Status Points, I can read on Status page (https://www.themanaworld.org/index.php/Stats) and Raising your stats on the Walkthrough page (https://www.themanaworld.org/index.php/Walkthrough).'))),
     assert(plan(talk(A,A,'I am now done with the Tutorial and I am free to explore The Mana World!'))),
   % Bully:
   % -----
     assert(plan(talk(A,A,'I leave the Tanisha`s house.'))),
     location(exit_from_tanishas_house,tonori,XETH,YETH),
     walk_to_location(A,M,XETH,YETH),
     assert(plan(talk(A,A,'As I go north of Tanisha`s house, I go past Hasan. I will not try to kill him, as I will probably die by doing this.'))),
     location(hasan,tonori,HasanX,HasanY),
     walk_to_location(A,M,HasanX,HasanY-5),
     location(kaan,tonori,KaanX,KaanY),
     walk_to_location(A,M,KaanX,KaanY),
     assert(plan(talk(A,Kaan,'Hi Kaan! I just killed 5 maggots.'))),
     assert(plan(talk(A,Kaan,'... and Hasan not let me to pass.'))),
     assert(plan(talk(A,A,'I now need to know what is Hasan`s weakness.'))),
     assert(plan(talk(A,A,'Therefore I come back with Tanisha to ask her about Hasan.'))),
     walk_to_location(A,M,TanishaX,TanishaY),
     assert(plan(talk(A,tanisha,'Hi Tanisha again! Hasan not let me to pass.'))),
     assert(plan(talk(tanisha,A,'Hasan is awfully scared of scorpions.'))),
     walk_to_location(A,M,KaanX,KaanY),
     assert(plan(talk(A,Kaan,'Hey Kaan, Tanisha said me that Hasan is awfully scared of scorpions. I will scratch my head as a signal and then I will kill the scorpion which will just appeared!'))),
     assert(plan(talk(Kaan,A,'I give you a sharp knife for that.'))),
     location(A,M,XA,YA),                                                              % Ako se agent nalazi na lokaciji (XA,YA)
     location(s,M,XScorpion,YScorpion),                                                % ... i ako se Scorpion nalazi na lokaciji (XScorpion,YScorpion)
     XAXScorpionDiff is XA-XScorpion, XAXScorpionDiff<30, XAXScorpionDiff>(-30),       % ... i ako je Scorpion na udaljenosti manjoj od 30 po x-u od agenta
     YAYScorpionDiff is YA-YScorpion, YAYScorpionDiff<30, YAYScorpionDiff>(-30) ->     % ... i ako je Scorpion na udaljenosti manjoj od 30 po y-u od agenta
     walk_to_location(A,M,XScorpion,YScorpion),                                        % ... tada hodaj na lokaciju gdje je Scorpion
     assert(plan(talk(A,A,'Here is one Scorpion! I will kill him and show to Hasan. Then Hasan will let me to pass.'))),
     retract(location(s,M,XScorpion,YScorpion)),                 % Na lokaciji (XScorpion,YScorpion) vise nema Scorpiona
     assert(plan(talk(Kaan,A,'I propose you to tell you the way to Tulimshar`s bazaar, you can accept...'))),
     /* Sa ovim ne znam sta treba:
        Valon
        Help Valon exterminate the pests.
          10 Maggots 40 Xp, 25 Zeny
           5 House Maggots 40 Xp, 25 Zeny
           3 Tame Scorpions 40 Xp, 25 Zeny
           1 Scorpion 40 Xp, 25 Zeny 
        Bonus: 50 Xp for completing. */
     /* Sa ovim ne znam sta treba:
        Zegas's Barrels
        The store room is full of House Maggots, but the bug bomb Eomie gave her is in the storeroom in one of the barrels.
        Search the barrels get random reward or possibly find a maggot, ewww!
           50 Xp, 50 Gp for completion + random loot */
     /* Sa ovim ne znam sta treba:
        Morgan is the Dean of Wizardry at MIT the Magic Insitute of Tulimshar. She will only talk to those that posses enough magical talent.
        She teaches them how to use Wands with the spell #confringo.
           wand is quest reward */
     retract(waiting_quest(NPC,A,tutorial))                                      % Brisi zapis da je agent dobio ovaj quest kao zadatak
     ->                                                                      % Ako je sve do ovdje obavljeno onda...
     assert(done_quest(A,tutorial));                                         % ...dodaj cinjenicu da je agent obavio ovaj quest...
     assert(failed_quest(NPC,A,tutorial)).                                       % ...inace dodaj cinjenicu da nije uspio obaviti ovaj quest

% Akcija kojom agent A ide okolo i ubija Giant Maggot-e tako da ce ih sveukupno ubiti N:

killing_giant_maggots(A,N) :-
    ownership(A,killed_giant_maggots,GMa),GMa<N ->                                   % Ako je agent do sada ubio manje Giant Maggots od trazenih N
    (location(A,M,XA,YA),                                                  % Ako se agent nalazi na lokaciji (XA,YA)
    location(gm,M,Xgm,Ygm),                                                % ... i ako se Giant Maggot nalazi na lokaciji (Xgm,Ygm)
    XAXgmDiff is XA-Xgm, XAXgmDiff<30, XAXgmDiff>(-30),                    % ... i ako je Giant Maggot na udaljenosti manjoj od 30 po x-u od agenta
    YAYgmDiff is YA-Ygm, YAYgmDiff<30, YAYgmDiff>(-30) ->                  % ... i ako je Giant Maggot na udaljenosti manjoj od 30 po y-u od agenta tada
    walk_to_location(A,M,Xgm,Ygm),                                         % Hodaj na lokaciju gdje je Giant Maggot
    assert(plan(talk(A,A,'I killed the Giant Maggot :)'))),                % Agent se veseli sto je ubio Giant Maggota
    retract(location(gm,M,Xgm,Ygm)),                                       % Na lokaciji (Xgm,Ygm) vise nema Maggot-a
    retract(ownership(A,killed_giant_maggots,GMa)),                                  % Agent vise nema GMa ubijenih Giant Maggot-a
    NewGMa is GMa+1, assert(ownership(A,killed_giant_maggots,NewGMa));               % Agent ima jednog ubijenog Giant Maggot-a vise
    random_walk(A)),                                                       % Inace (ako agent nema Maggota na vidiku) onda neka se odsece na slucajnu lokaciju
    killing_giant_maggots(A,N);                                            % Ponovno pozivamo akciju killing_giant_maggots
    true.

% Quest: Emote Skill
% ------------------

% Starting Location: U Tulimsharu (at the moment the only town of Tonori Continent) kod Entertainer-a
% Level: 1
% Redoable: No
% Prerequisites: None
% Reward: Emote ability
% Costs: None

% What To Do:

%     In the center of the bazaar of Tulimshar, find the Entertainer at the left of the central road.
%     Talk to her and ask her how she does the emotes above her head.
%     Then ask her to teach you that.
%     You now know how to do emotes.
%     Check in your setup/keyboard window if it doesn't work.

% Akcija kojom nas agent A obavlja quest Emote Skill jer mu ga je zadao NPC:

do_quest(NPC,A,emote_skill) :-
%  Preduvjeti:
     location(entertainer,M,XET,YET),                             % Entertainer se nalazi na lokaciji (XE,YE)
     ownership(A,level,La), La>=1,                                                     % Agent je najmanje na levelu 1
     waiting_quest(NPC,A,emote_skill),                                           % Ovaj quest se nalazi na popisu agentovih questova koje treba obaviti
     \+ done_quest(A,emote_skill),                                      % Agent nije jos obavio ovaj quest
%  Brisanja:
     % Nema brisanja
%  Dodavanja:
     walk_to_location(A,M,XET,YET),                                            % Agent je odsetao do Entertainer-a
     assert(plan(talk(A,entertainer,'How you does the emotes above your head?'))), % Dodaj cinjenicu da je agent rekao Entertaineru ono sto je u navodnicima
     assert(plan(talk(A,entertainer,'Please, teach me that.'))),                   % Dodaj cinjenicu da je agent rekao Entertaineru ono sto je u navodnicima
     assert(ability(A,emote_ability)),                                       % Dodaj cinjenicu da agent sada ima Emote ability
     retract(waiting_quest(NPC,A,emote_skill))                                   % Brisi zapis da je agent dobio ovaj quest kao zadatak
     ->                                                                      % Ako je sve do ovdje obavljeno onda...
     assert(done_quest(A,emote_skill));                                      % ...dodaj cinjenicu da je agent obavio ovaj quest...
     assert(failed_quest(NPC,A,emote_skill)).                                    % ...inace dodaj cinjenicu da nije uspio obaviti ovaj quest

% Note: \+ is a prefix operator which, in case of action do_quest, takes \+ ability(A,emote_ability) as its argument. An important point to note about negation in Prolog is that it doesn't mean that the goal you have negated is proved false in the logical sense. It does mean that the goal can not be established from the current set of axioms in the database. The implicit assumption here is that the set of axioms in the current database are a complete description of every aspect of the problem. This is often referred to as the closed world assumption.

% Quest: Trade Skill
% ------------------

% Starting Location: U Tulimshar-u kod Trader-a
% Level: 1
% Redoable: No
% Prerequisites: None
% Reward: Trade Skill
% Costs: 5 GP

% What To Do:

%     In the center of the bazaar of Tulimshar, north of the Soul Menhir, find the Trader at the right of the central road.
%     Talk to him and ask him if he has anything for you.
%     Go as deep as you can in the conversation. (OVO BAS I NE RAZUMIJEM KAKO CEMO)
%     Pay 5 GP and read how the trade system works.
%     Now you have the trade ability!

% Akcija kojom nas agent A obavlja quest Trade Skill jer mu ga je zadao NPC:

do_quest(NPC,A,trade_skill) :-
%  Preduvjeti:
     location(trader,M,XTT,YTT),  % Trader u Tulimsharu gdje treba obaviti quest Trade Skill se nalazi na lokaciji (XT,YT)
     ownership(A,level,La), La>=1,                     % Agent je najmanje na levelu 1
     waiting_quest(NPC,A,trade_skill),           % Ovaj quest se nalazi na popisu agentovih questova koje treba obaviti
     \+ done_quest(A,trade_skill),      % Agent nije jos obavio ovaj quest
     ownership(A,zeny,Ma), Ma>=5,                     % Agent ima najmanje 5 GP
%  Brisanja:
     retract(ownership(A,zeny,Ma)),                   % Agent vise nema Ma novaca
%  Dodavanja:
     walk_to_location(A,M,XTT,YTT),            % Agent je odsetao do Trader-a
     assert(plan(talk(A,trader,'Do you have anything for me?'))),
     NewMa is Ma-5, assert(ownership(A,zeny,NewMa)),  % Agent ima 5 GP manje
     assert(ability(A,trade_ability)),       % Dodaj cinjenicu da agent sada ima Trade ability
     retract(waiting_quest(NPC,A,trade_skill))   % Brisi zapis da je agent dobio ovaj quest kao zadatak
     ->                                      % Ako je sve do ovdje obavljeno onda...
     assert(done_quest(A,trade_skill));      % ...dodaj cinjenicu da je agent obavio ovaj quest...
     assert(failed_quest(NPC,A,trade_skill)).    % ...inace dodaj cinjenicu da nije uspio obaviti ovaj quest

% Quests: Newbie Quests
% ---------------------

% These quests replace one of the old Short Sword quest and they all need to be done in that precise order
% They are the required preamble to Bandit Quest. They can be mixed with the newbie quests
% Both make the Tutorial more complete and the whole set brings you around level 30

% Quest: Bernard
% --------------

% Starting Location: U Tulimshar-u kod Bernarda
% Required level: 1
% Recommended For Level: 20
% Redoable: No
% Prerequisites: None
% Reward: 3 Beers, 5 Cherry Cakes, 100 EXP + 100 EXP (NE RAZUMIJEM ZASTO PISE 100 EXP + 100 EXP. U AKCIJU SAM STAVIO 200 EXP ALI TO MOZDA TREBA PROMIJENITI)
% Costs: 1 Roasted Maggot, 3 Maggot Slimes

% What To Do:

%   Go to the center of Tulimshar near the central road.
%   Go and talk To Bernard.
%   He will ask you for 1 Roasted Maggot.
%   After receiving 5 Cherry Cakes by giving him what he asked you for, he will then need 3 Maggot Slimes for his soup.
%   He will then give you 3 Beers taken from his soup as a reward.

% Akcija kojom nas agent A obavlja quest Bernard jer mu ga je zadao NPC:

do_quest(NPC,A,bernard) :-
%  Preduvjeti:
     location(bernard,M,XBT,YBT),                  % Bernard u Tulimshar-u kod kojeg treba obaviti quest se nalazi na lokaciji (XBT,YBT)
     ownership(A,level,La), La>=1,                                      % Agent je najmanje na levelu 1 (OVO JE Required LEVEL, A NE Recommended - MOZDA CU MORATI ZA SVE QUEST-OVE NAPRAVITI I Required I Recommended PA CEMO ONDA VIDJETI STA S TIM)
     waiting_quest(NPC,A,bernard),                                % Ovaj quest se nalazi na popisu agentovih questova koje treba obaviti
     \+ done_quest(A,bernard),                           % Agent nije jos obavio ovaj quest
     ownership(A,roasted_maggots,RMa), RMa>=1,                          % Agent ima najmanje 1 Roasted Maggot
     ownership(A,maggot_slimes,MSa), MSa>=3,                            % Agent ima najmanje 3 Maggot Slimes
     ownership(A,cherry_cakes,CCa),                                     % Agent ima CCa Cherry Cakes
     ownership(A,beers,Ba),                                             % Agent ima Ba Beers
     ownership(A,exp,EXPa),                                             % Agent ima EXPa EXP-a
%  Brisanja:
     retract(ownership(A,roasted_maggots,RMa)),                         % Agent vise nema RMa Roasted Maggots
     retract(ownership(A,maggot_slimes,MSa)),                           % Agent vise nema MSa Maggot Slimes
     retract(ownership(A,cherry_cakes,CCa)),                            % Agent vise nema CCa Cherry Cakes
     retract(ownership(A,beers,Ba)),                                    % Agent vise nema Ba Beers
     retract(ownership(A,exp,EXPa)),                                    % Agent vise nema EXPa EXP-a
%  Dodavanja:
     walk_to_location(A,M,XBT,YBT),                             % Agent je odsetao do Bernarda
     assert(plan(talk(A,bernard,'Hi Bernard!'))),
     assert(plan(talk(bernard,A,'Give me 1 Roasted Maggot!'))),
     assert(plan(talk(A,bernard,'Here, take 1 Roasted Maggot!'))),
     NewRMa is RMa-1, assert(ownership(A,roasted_maggots,NewRMa)),      % Agent ima jedan Roasted Maggots manje
     assert(plan(talk(bernard,A,'Give me 3 Maggot Slimes for my soup!'))),
     assert(plan(talk(bernard,A,'Here you have 3 Maggot Slimes for your soup!'))),
     NewMSa is MSa-3, assert(ownership(A,maggot_slimes,NewMSa)),        % Agent ima tri Maggot Slimes manje
     NewCCa is CCa+5, assert(ownership(A,cherry_cakes,NewCCa)),         % Agent ima pet Cherry Cakes vise
     NewBa is Ba+3, assert(ownership(A,beers,NewBa)),                   % Agent ima tri Beers vise
     NewEXPa is EXPa+200, assert(ownership(A,exp,NewEXPa)),             % Agent ima 200 EXP-a vise
     retract(waiting_quest(NPC,A,bernard))                        % Brisi zapis da je agent dobio ovaj quest kao zadatak
     ->                                                       % Ako je sve do ovdje obavljeno onda...
     assert(done_quest(A,bernard));                           % ...dodaj cinjenicu da je agent obavio ovaj quest...
     assert(failed_quest(NPC,A,bernard)).                         % ...inace dodaj cinjenicu da nije uspio obaviti ovaj quest

% Quest: Mikhail
% --------------

% Starting Location: U Tulimshar-u kod Mikhaila
% Required level: 1
% Recommended For Level: 20
% Redoable: No
% Prerequisites: All the above Tulimshar Quests (Bernard)
% Reward: 100 EXP
% Costs: 5 Maggot Slimes

% What To Do:

%   Go to the center of Tulimshar near the central road.
%   Talk To Mikhail standing just on the right of the road.
%   He will ask you 5 Maggot Slimes for his grandmother.
%   Give these 5 Maggot Slimes to end the quest.

% Akcija kojom nas agent A obavlja quest Mikhail jer mu ga je zadao NPC:

do_quest(NPC,A,mikhail) :-
%  Preduvjeti:
     location(mikhail,M,XMT,YMT),                % Mikhail u Tulimshar-u kod kojeg treba obaviti quest se nalazi na lokaciji (XMT,YMT)
     ownership(A,level,La), La>=1,                                      % Agent je najmanje na levelu 1 (OVO JE Required LEVEL, A NE Recommended - MOZDA CU MORATI ZA SVE QUEST-OVE NAPRAVITI I Required I Recommended PA CEMO ONDA VIDJETI STA S TIM)
     done_quest(A,bernard),                                   % Agent je obavio sve prethodne Tulimshar questove
     waiting_quest(NPC,A,mikhail),                            % Ovaj quest se nalazi na popisu agentovih questova koje treba obaviti
     \+ done_quest(A,mikhail),                                % Agent nije jos obavio ovaj quest
     ownership(A,maggot_slimes,MSa), MSa>=5,                            % Agent ima najmanje 5 Maggot Slimes
     ownership(A,exp,EXPa),                                             % Agent ima EXPa EXP-a
%  Brisanja:
     retract(ownership(A,maggot_slimes,MSa)),                           % Agent vise nema MSa Maggot Slimes
     retract(ownership(A,exp,EXPa)),                                    % Agent vise nema EXPa EXP-a
%  Dodavanja:
     walk_to_location(A,M,XMT,YMT),                           % Agent je odsetao do Mikhaila
     assert(plan(talk(A,mikhail,'Hi Mikhail!'))),
     assert(plan(talk(mikhail,A,'Give me 5 Maggot Slimes for my grandmother!'))),
     assert(plan(talk(mikhail,A,'I give you 5 Maggot Slimes for your grandmother!'))),
     NewMSa is MSa-5, assert(ownership(A,maggot_slimes,NewMSa)),        % Agent ima pet Maggot Slimes manje
     NewEXPa is EXPa+100, assert(ownership(A,exp,NewEXPa)),             % Agent ima 100 EXP-a vise
     retract(waiting_quest(NPC,A,mikhail))                        % Brisi zapis da je agent dobio ovaj quest kao zadatak
     ->                                                       % Ako je sve do ovdje obavljeno onda...
     assert(done_quest(A,mikhail));                           % ...dodaj cinjenicu da je agent obavio ovaj quest...
     assert(failed_quest(NPC,A,mikhail)).                         % ...inace dodaj cinjenicu da nije uspio obaviti ovaj quest

% Quest: Sarah
% ------------

% Starting Location: U Tulimshar-u kod Sarah
% Required level: 1
% Recommended For Level: 20
% Redoable: No
% Prerequisites: All the above Tulimshar Quests (Bernard, Mikhail)
% Reward: Serf Hat (+2 Defense) (OVO 2 Defense NE ZNAM STA JE PA ZA SADA NISAM NI MODELIRAO)
% Costs: 1 Cherry Cake

% What To Do:

%   Take the southeast road of Tulimshar. Sarah will be standing at the corner of the end of that road.
%   Talk to her.
%   She will tell you she wants a Cherry Cake and will give you a hat for that.
%   Talk to her once more and give her the Cherry Cake.
%   You will now have a Serf Hat.

% Akcija kojom nas agent A obavlja quest Sarah jer mu ga je zadao NPC:

do_quest(NPC,A,sarah) :-
%  Preduvjeti:
     location(sarah,M,XST,YST),                    % Sarah u Tulimshar-u kod koje treba obaviti quest se nalazi na lokaciji (XST,YST)
     ownership(A,level,La), La>=1,                                      % Agent je najmanje na levelu 1 (OVO JE Required LEVEL, A NE Recommended - MOZDA CU MORATI ZA SVE QUEST-OVE NAPRAVITI I Required I Recommended PA CEMO ONDA VIDJETI STA S TIM)
     done_quest(A,bernard),                              % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,mikhail),                              % Agent je obavio sve prethodne Tulimshar questove
     waiting_quest(NPC,A,sarah),                                  % Ovaj quest se nalazi na popisu agentovih questova koje treba obaviti
     \+ done_quest(A,sarah),                             % Agent nije jos obavio ovaj quest
     ownership(A,cherry_cakes,CCa), CCa>=1,                             % Agent ima najmanje 1 Cherry Cake
     ownership(A,serf_hat,SHa),                                         % Agent ima SHa Serf Hats
%  Brisanja:
     retract(ownership(A,cherry_cakes,CCa)),                            % Agent vise nema CCa Cherry Cakes
     retract(ownership(A,serf_hat,SHa)),                                % Agent vise nema SHa Serf Hats
%  Dodavanja:
     walk_to_location(A,M,XST,YST),                             % Agent je odsetao do Sarah
     assert(plan(talk(A,sarah,'Hi Sarah!'))),
     assert(plan(talk(sarah,A,'Give me a Cherry Cake and I will give you a hat for that!'))),
     assert(plan(talk(A,sarah,'Okay, agreed! Here you have a Cherry Cake!'))),
     NewCCa is CCa-1, assert(ownership(A,cherry_cakes,NewCCa)),         % Agent ima jedan Cherry Cake manje
     NewSHa is SHa+1, assert(ownership(A,serf_hat,NewSHa)),             % Agent ima 1 Serf Hat vise
     retract(waiting_quest(NPC,A,sarah))                          % Brisi zapis da je agent dobio ovaj quest kao zadatak
     ->                                                       % Ako je sve do ovdje obavljeno onda...
     assert(done_quest(A,sarah));                             % ...dodaj cinjenicu da je agent obavio ovaj quest...
     assert(failed_quest(NPC,A,sarah)).                           % ...inace dodaj cinjenicu da nije uspio obaviti ovaj quest

% Quest: Vincent
% --------------

% Starting Location: U Tulimshar-u kod Vincenta
% Required level: 1
% Recommended For Level: 20
% Redoable: No
% Prerequisites: All the above Tulimshar Quests (Bernard, Mikhail, Sarah)
% Reward: 1000 GP
% Costs: 10 Bug Legs

% What To Do:

%   From the southern exit of Tulimshar, head east along the road to the end. When the road ends going east, head north. You will find Vincent on your left, by the well.
%   Talk to Vincent, and he will ask you to collect 10 Bug Legs for his action figure.
%   Go and collect 10 Bug Legs.
%   Talk to Vincent one last time and give him the 10 Bug Legs you collected to complete the quest.

% OVDJE (U PRVOM ILI DRUGOM PRAVILU) NESTO NE STIMA SA BROJEM bug_legs NAKON SKUPLJANJA - ISPRAVITI TO:

do_quest(NPC,A,vincent) :-
     location(vincent,M,XVT,YVT),
     ownership(A,level,La), La>=1,
     done_quest(A,bernard),
     done_quest(A,mikhail),
     done_quest(A,sarah),
     waiting_quest(NPC,A,vincent),
     \+ done_quest(A,vincent),
     ownership(A,zeny,Ma),
     retract(ownership(A,zeny,Ma)),
     NewMa is Ma+1000,
     assert(ownership(A,zeny,NewMa)),
     walk_to_location(A,M,XVT,YVT),
     assert(plan(talk(A,vincent,'Hi Vincent!'))),
     assert(plan(talk(vincent,A,'Give me 10 Bug Legs for my action figure!'))),
     ownership(A,bug_legs,BL),
     (BL>=10 ->
      NewBL is BL-10,
      assert(ownership(A,bug_legs,NewBL)),
      retract(ownership(A,bug_legs,BL));
      collect_items(A,bug_legs,10),
      assert(ownership(A,bug_legs,0)),
      retract(ownership(A,bug_legs,BL))),
     walk_to_location(A,M,XVT,YVT),
     assert(plan(talk(A,vincent,'I collected 10 Bug Legs. I give it to you!'))),
     retract(waiting_quest(NPC,A,vincent))
     ->
     assert(done_quest(A,vincent));
     assert(failed_quest(NPC,A,vincent)).

% Quest: Sandra
% -------------

% Starting Location: U Tulimshar-u kod Sandre
% Required level: 1
% Recommended For Level: 20
% Redoable: No
% Prerequisites: All the above Tulimshar Quests (Bernard, Mikhail, Sarah, Vincent)
% Rewards: 100 Arrows, 1 Bow (+20 Damage, +5 Range) (NE ZNAM STA JE OVO (+20 Damage, +5 Range) PA TO NISAM JOS MODELIRAO)
% Costs: 5 Scorpion Stingers

% What To Do:

%   Starting from southern exit in town, head east on the first path, past Elanore. Go past the first T junction, and Sandra is on the corner.
%   Talk to Sandra, she wants you to bring her 5 Scorpion Stingers to prove that you killed them.
%   Go and collect the 5 Scorpion Stingers.
%   Talk to Sandra again and give the stingers to receive your reward.

% Akcija kojom nas agent A obavlja quest Sandra jer mu ga je zadao NPC:

do_quest(NPC,A,sandra) :-
%  Preduvjeti:
     location(sandra,M,XST,YST),                   % Sandra u Tulimshar-u kod koje treba obaviti quest se nalazi na lokaciji (XST,YST)
     ownership(A,level,La), La>=1,                                      % Agent je najmanje na levelu 1 (OVO JE Required LEVEL, A NE Recommended - MOZDA CU MORATI ZA SVE QUEST-OVE NAPRAVITI I Required I Recommended PA CEMO ONDA VIDJETI STA S TIM)
     done_quest(A,bernard),                              % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,mikhail),                              % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,sarah),                                % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,vincent),                              % Agent je obavio sve prethodne Tulimshar questove
     waiting_quest(NPC,A,sandra),                                 % Ovaj quest se nalazi na popisu agentovih questova koje treba obaviti
     \+ done_quest(A,sandra),                            % Agent nije jos obavio ovaj quest
     ownership(A,scorpion_stingers,SSa),                                % Agent ima SSa Scorpion Stingers
     ownership(A,arrows,Aa),                                            % Agent ima Aa Arrows
     ownership(A,bows,Ba),                                              % Agent ima Ba Bows
%  Brisanja:
     retract(ownership(A,arrows,Aa)),                                   % Agent vise nema Aa Arrows
     retract(ownership(A,bows,Ba)),                                     % Agent vise nema Ba Bows
%  Dodavanja:
     walk_to_location(A,M,XST,YST),                             % Agent je odsetao do Sandre
     assert(plan(talk(A,sandra,'Hi Sandra!'))),
     assert(plan(talk(sandra,A,'Bring me 5 Scorpion Stingers!'))),
     collect_scorpion_stingers(A,5),                          % Zovi akciju kojom agent prikuplja 5 Scorpion Stingers (ako agent vec ima neki Scorpion Stinger onda ce ih skupiti samo onoliko koliko mu treba do pet)
     walk_to_location(A,M,XST,YST),                             % Agent se vraca kod Sandre
     assert(plan(talk(A,sandra,'I give you 5 Scorpion Stingers.'))),
     ((SSa>5 -> NewSSa is SSa-5, assert(ownership(A,scorpion_stingers,NewSSa)));assert(ownership(A,scorpion_stingers,0))), % Agent ima pet Scorpion Stingers manje
     assert(plan(talk(sandra,A,'I give you 100 Arrows'))),
     NewAa is Aa+100, assert(ownership(A,arrows,NewAa)),                % Agent ima 100 Arrows vise
     assert(plan(talk(sandra,A,'... and 1 Bow.'))),
     NewBa is Ba+1, assert(ownership(A,bows,NewBa)),                    % Agent ima 1 Bow vise
     retract(waiting_quest(NPC,A,sandra))                         % Brisi zapis da je agent dobio ovaj quest kao zadatak
     ->                                                       % Ako je sve do ovdje obavljeno onda...
     assert(done_quest(A,sandra));                            % ...dodaj cinjenicu da je agent obavio ovaj quest...
     assert(failed_quest(NPC,A,sandra)).                          % ...inace dodaj cinjenicu da nije uspio obaviti ovaj quest

% SLIJEDECA AKCIJA NAM VIŠE NECE TREBATI JER OVO TREBAMO UPAKIRATI U GENERICKO PRAVILO ZA SKUPLJANJE ITEMA:
% Akcija kojom agent A ide okolo, ubija Scorpions i prikuplja Scorpion Stingers tako da ce ih na kraju imati N:

collect_scorpion_stingers(A,N) :-
% Preduvjeti:
    ownership(A,scorpion_stingers,SSa),                                 % Agent ima SSa Scorpion Stingers
    (SSa<N ->                                                 % Ako agent ima manje od N Scorion Stingers...
    location(s,M,Xss,Yss),                                      % ... i Scorpion se nalazi na lokaciji (Xss,Yss)
% Dodavanja:
    walk_to_location(A,M,Xss,Yss),                              % Hodaj na lokaciju gdje je Scorpion
    assert(plan(talk(A,A,'Here is one Scorpion! I will kill him and take his stinger :D'))),
    retract(location(s,M,Xss,Yss)),                             % Na lokaciji (Xss,Yss) vise nema Scorpiona
    retract(ownership(A,scorpion_stingers,SSa)),                        % Agent vise nema SSa Scorpion Stingers
    NewSSa is SSa+1, assert(ownership(A,scorpion_stingers,NewSSa)),     % Agent ima jedan Scorpion Stinger vise
    collect_scorpion_stingers(A,N));
    retract(ownership(A,scorpion_stingers,SSa)), true.                  % Ako agent ima N Scorpion Stingers onda je rezultat true, a usput obrisi i privremeni podatak o broju Scorpion Stingers

% Quest: Lieutenant Dausen
% ------------------------

% Starting Location: U Sandstorm Desert kod Lieutenanta Dausena
% Required level: 1
% Recommended For Level: 20
% Redoable: No
% Prerequisites: All the above Tulimshar Quests (Bernard, Mikhail, Sarah, Vincent, Sandra)
% Rewards: Boots (+2 Defense) (NE ZNAM STA JE OVO (+2 Defense) PA TO NISAM JOS MODELIRAO)
% Costs: 10 Cactus Drinks

% What To Do:

%   Talk to Lieutenant Dausen.
%   He will ask you to get 10 Cactus Drinks.
%   Kill Giant Maggots for 10 green Cactus Drinks.
%   Lieutenant Dausen rewards you with a pair of Boots (+2 Defense).
%   Talk to Lieutenant Dausen again.
%   He will ask you to tell Stewen and Nickos to stay at their posts.
%   First visit Stewen to the southeast, then visit Nickos to the south west near the mine.
%   Talk again to Lieutenant Dausen and get 500 GP.
%   He will mention that Nickos has a quest for you.

% Akcija kojom nas agent A obavlja quest Lieutenant Dausen jer mu ga je zadao NPC:

do_quest(NPC,A,lieutenant_dausen) :-
%  Preduvjeti:
     location(lieutenant_dausen_in_sandstorm_desert,M,XLDSD,YLDSD),      % Lieutenant Dausen u Sandstorm Desert kod kojeg treba obaviti quest se nalazi na lokaciji (XLDSD,YLDSD)
     ownership(A,level,La), La>=1,                                      % Agent je najmanje na levelu 1 (OVO JE Required LEVEL, A NE Recommended - MOZDA CU MORATI ZA SVE QUEST-OVE NAPRAVITI I Required I Recommended PA CEMO ONDA VIDJETI STA S TIM)
     done_quest(A,done_bernard),                              % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,mikhail),                              % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,sarah),                                % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,vincent),                              % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,sandra),                               % Agent je obavio sve prethodne Tulimshar questove
     waiting_quest(NPC,A,lieutenant_dausen),                      % Ovaj quest se nalazi na popisu agentovih questova koje treba obaviti
     \+ done_quest(A,lieutenant_dausen),                      % Agent nije jos obavio ovaj quest
     ownership(A,cactus_drinks,CDa),                                    % Agent ima CDa Cactus Drinks
     ownership(A,boots,Ba),                                             % Agent ima Ba Boots
%  Brisanja:
     retract(ownership(A,boots,Ba)),                                    % Agent vise nema Ba Boots
     retract(ownership(A,zeny,Ma)),                                    % Agent vise nema Ma GPs
%  Dodavanja:
     walk_to_location(A,M,XLDSD,YLDSD),                         % Agent je odsetao do Lieutenant Dausena
     assert(plan(talk(A,lieutenant_dausen_in_sandstorm_desert,'Hi Lieutenant Dausen!'))),
     assert(plan(talk(lieutenant_dausen_in_sandstorm_desert,A,'Give me 10 Cactus Drinks!'))),
     assert(plan(talk(A,lieutenant_dausen_in_sandstorm_desert,'I am going to kill 10 Giant Maggots and then I will bring you 10 Cactus Drinks.'))),
     collect_cactus_drinks(A,10),                             % Zovi akciju kojom agent prikuplja 10 Cactus Drinks tako da ubija Giant Maggots (ako agent vec ima neki Cactus Drink ce ih skupiti samo onoliko koliko mu treba do 10)
     walk_to_location(A,M,XLDSD,YLDSD),                         % Agent se vraca kod Lieutenant Dausen
     assert(plan(talk(A,lieutenant_dausen_in_sandstorm_desert,'Here are 10 Cactus Drinks for you!'))),
     ((CDa>10 -> NewCDa is CDa-10, assert(ownership(A,cactus_drinks,NewCDa)));assert(ownership(A,cactus_drinks,0))),
     assert(plan(talk(lieutenant_dausen_in_sandstorm_desert,A,'Thank you for Cactus Drinks! I give you pair of Boots.'))),
     assert(plan(talk(A,lieutenant_dausen_in_sandstorm_desert,'Thank you for pair of Boots.'))),
     NewBa is Ba+1, assert(ownership(A,boots,NewBa)),                   % Agent ima jedne Boots vise
     assert(plan(talk(A,lieutenant_dausen_in_sandstorm_desert,'Hi Lieutenant Dausen again!'))),
     assert(plan(talk(lieutenant_dausen_in_sandstorm_desert,A,'Hi! Please tell Stewen and Nickos to stay at their posts!'))),
     location(stewen,M,XStewen,YStewen),                        % Ako je Stewen na nekoj lokaciji
     location(nickos,M,XNickos,YNickos),                        % Ako je Nickos na nekoj lokaciji
     walk_to_location(A,M,XStewen,YStewen),                     % Idi kod Stewena...
     assert(plan(talk(A,stewen,'Hi Stewen! Please stay at your post!'))), % ... i reci mu sta trebas
     walk_to_location(A,M,XNickos,YNickos),                     % Idi kod Nickosa...
     assert(plan(talk(A,nickos,'Hi Nickos! Please stay at your post!'))), % ... i reci mu sta trebas
     walk_to_location(A,M,XLDSD,YLDSD),                         % Agent se vraca kod Lieutenant Dausen
     assert(plan(talk(A,lieutenant_dausen_in_sandstorm_desert,'Hi Lieutenant Dausen again! Give mi 500 GP.'))), % Reci Lieutenant Dausen neka ti da 500 GP
     assert(plan(talk(lieutenant_dausen_in_sandstorm_desert,A,'I give you 500 GP!'))),
     NewMa is Ma+500, assert(ownership(A,zeny,NewMa)),                 % Agent ima 500 GP vise
     assert(plan(talk(lieutenant_dausen_in_sandstorm_desert,A,'Nickos has a quest for you!'))),
     retract(waiting_quest(NPC,A,lieutenant_dausen))                   % Brisi zapis da je agent dobio ovaj quest kao zadatak
     ->                                                            % Ako je sve do ovdje obavljeno onda...
     assert(done_quest(A,lieutenant_dausen));                      % ...dodaj cinjenicu da je agent obavio ovaj quest...
     assert(failed_quest(NPC,A,lieutenant_dausen)).                    % ...inace dodaj cinjenicu da nije uspio obaviti ovaj quest

% SLIJEDECA AKCIJA NAM VIŠE NECE TREBATI JER CE BITI UPAKIRANA U GENERICKO SKUPLJANJE ITEMA:
% Akcija kojom agent A ide okolo, ubija Giant Maggots i prikuplja Cactus Drinks tako da ce ih na kraju imati N:

collect_cactus_drinks(A,N) :-
% Preduvjeti:
    ownership(A,cactus_drinks,CDa),                                     % Agent ima CDa Cactus Drinks
    (CDa<N ->                                                 % Ako agent ima manje od N Cactus Drinks...
    location(gm,M,Xgm,Ygm),                                     % ... i Giant Maggot se nalazi na lokaciji (Xgm,Ygm)
% Dodavanja:
    walk_to_location(A,M,Xgm,Ygm),                              % Hodaj na lokaciju gdje je Giant Maggot
    assert(plan(talk(A,A,'Here is one Giant Maggot! I will kill him and take his Cactus Drink :D'))),
    retract(location(gm,M,Xgm,Ygm)),                            % Na lokaciji (Xgm,Ygm) vise nema Giant Maggota
    retract(ownership(A,cactus_drinks,CDa)),                            % Agent vise nema CDa Cactus Drinks
    NewCDa is CDa+1, assert(ownership(A,cactus_drinks,NewCDa)),         % Agent ima jedan Cactus Drink vise
    collect_cactus_drinks(A,N));
    retract(ownership(A,cactus_drinks,CDa)), true.                      % Ako agent ima N Cactus Drinks onda je rezultat true, a usput obrisi i privremeni podatak o broju Cactus Drinks

% Quest: Miners Quest (NE ZNAM DA LI JE OVAJ GOTOV - TREBA PROVJERITI)
% -------------------

% Starting Location: 002-1 Sandstorm Desert
% Required level: 1
% Recommended For Level: 20
% Redoable: No
% Prerequisites: All the above Tulimshar Quests (Bernard, Mikhail, Sarah, Vincent, Sandra, Lieutenant Dausen)
% Rewards: 1 Desert Shirt (+6% defense), 1000 GP, 1 Iten, 1 Leather Shield (+7% defense), 1 Miner Gloves (+2% defense), 1 Miners Hat (+4% defense), 10 Boss Points (with Desert Shirt) 
% Costs: 10 Angry Scorpion Stingers, 3 Treasure Keys

% What To Do Outside:

%   Go talk to Stewen
%   Next go back to Lieutenant Dausen again
%   Then go south-west to the mine and talk to Nickos.
%   Then go back to Lieutenant Dausen and talk to him once more. He will then give you 500 GP!
%   After talking to Lieutenant Dausen, go and see Nickos situated in front of the mine. He will give you permission to enter.
%   Go in and talk to Nathan and Naem. Nathan is right near the entrance. Naem is southeast of the entrance.
%   When Naem and Nathan will be satisfied, go out of the cave and talk to Nickos who will give you 500 GP.
%   Once again, you will need to go and talk to Lieutenant Dausen and then to Nickos again. 

% What To Do In The Cave:
/*
    Now go back in the cave and talk to Nathan, then walk back and forth between him and Naem many times to carry 3 bags of ore that doesn't show up in your inventory so be careful, read what they say at every moment. Don't worry, you will need to do only three back and forth between Nathan and Naem. You will receive a Miners Hat for your transporting.
    Go outside and talk to Nickos again. Then go back in the cave and kill Angry Scorpions until you get 10 Angry Scorpion Stingers.
    After you are done getting 10 Angry Scorpion Stingers, go talk to Nickos and collect a Leather Shield.
    Now go talk to Naem to get the barrier key. But guess what? He doesn't have the key! You need to go talk to Lieutenant Dausen again to have that key.
    The astute reader will notice buttons along the walls inside the mine. The mines must have the key inserted into them and have the key turned in the right direction and in the correct order in order to continue with the quest. Begin with the button in the first room's left corner(south-west of the room): Turn the key right (the button NPC should say you can hear a "click"); Secondly, use the Button near Naem (south-east of the cave): Turn the key left (the button NPC should say you can hear a "click"); and finally use the button on the first room's right (east of cave entrance): Turn the key left (the button NPC should say you can hear a "loud thump").
    Go down to the southeast of the cave so Naem can give you a pair of Miner Gloves.
    Talk to Sema. She tells you there is a chest somewhere that needs 3 Treasure Keys to unlock.
    Kill Archants until you get 3 Treasure Keys then find the chest at the end of the cave and talk to the chest. Open it to receive a Short Bow (+50 Damage).
    Go back and talk to Sema. She will tell you there are a couple of Giant Maggots and asks you to kill one and bring back what it drops, which is an Iten (a very heavy useless grey cube). Kill the giant maggot, take the Iten, return to Sema and talk to her.
    Give the iten to Sema. She will give you a Desert Shirt (+6 Defense).
    You should be now done with these quests in Tulimshar (except, maybe, Anwar's field). You can continue this list of quests by talking to Lena located in Hurnscald and do the Bandit Quest.
*/

% Akcija kojom nas agent A obavlja quest Miners Quest jer mu ga je zadao NPC:

do_quest(NPC,A,miners_quest) :-
     ownership(A,level,La), La>=1,                                                                % Agent je najmanje na levelu 1 (OVO JE Required LEVEL, A NE Recommended - MOZDA CU MORATI ZA SVE QUEST-OVE NAPRAVITI I Required I Recommended PA CEMO ONDA VIDJETI STA S TIM)
     done_quest(A,bernard),                                                        % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,mikhail),                                                        % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,sarah),                                                          % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,vincent),                                                        % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,sandra),                                                         % Agent je obavio sve prethodne Tulimshar questove
     done_quest(A,lieutenant_dausen),                                                   % Agent je obavio sve prethodne Tulimshar questove
     waiting_quest(NPC,A,miners_quest),                                                 % Ovaj quest se nalazi na popisu agentovih questova koje treba obaviti
     \+ done_quest(A,miners_quest),                                                     % Agent nije jos obavio ovaj quest
     location(stewen,M,XStewen,YStewen),                                                % Ako je Stewen na nekoj lokaciji
     walk_to_location(A,M,XStewen,YStewen),                                             % Idi kod Stewena...
     assert(plan(talk(A,stewen,'Hi Stewen! I talk with you.'))),
     location(lieutenant_dausen,M,XLieutenantDausen,YLieutenantDausen),                 % Ako je Lieutenant Dausena na nekoj lokaciji
     walk_to_location(A,M,XLieutenantDausen,YLieutenantDausen),                         % Agent je odsetao do Lieutenant Dausena
     location(mine,tonori,XMine,YMine),                                                 % Rudnik se nalazi na koordinatama (XMine,YMine)
     assert(plan(talk(A,nickos,'Hi Nickos! I talk to you.'))),
     walk_to_location(A,M,XLieutenantDausen,YLieutenantDausen),                         % Agent ide ponovo do Lieutenant Dausena
     assert(plan(talk(A,lieutenant_dausen,'Hi Lieutenant Dausen! I talk to you.'))),
     assert(plan(talk(lieutenant_dausen,A,'Hi Agent! I give you 500 GP.'))),
     ownership(A,zeny,GPs),                                                                      % Agent ima GPs novaca
     retract(ownership(A,zeny,GPs)),                                                             % Agent vise nema GPs novaca
     NewGPs is GPs+500, assert(ownership(A,zeny,NewGPs)),                                        % Agent ima 500 novaca više
     location(nickos,M,XNickos,YNickos),                                                % Nickos se nalazi na lokaciji (XNickos,YNickos)
     walk_to_location(A,M,XNickos,YNickos),                                             % Agent go to Nickos situated in front of the mine
     assert(plan(talk(A,nickos,'Hi Nickos! Can you let me go into the mine?'))),
     assert(plan(talk(nickos,A,'Hi Agent! I give you permission to enter the mine.'))),
     location(nathan,M,XNatnan,YNathan),
     walk_to_location(A,M,XNatnan,YNathan),
     assert(plan(talk(A,nathan,'Hi Nathan! I talk with you.'))),
     assert(plan(talk(nathan,A,'Hi Agent!'))),
     location(naem,tonori,XNaem,YNaem),
     walk_to_location(A,M,XNaem,YNaem),
     assert(plan(talk(A,naem,'Hi Naem! I talk with you.'))),
     assert(plan(talk(naem,A,'Hi Agent!'))),
     location(entrance_into_mine,tonori,XEnterMine,YEnterMine),
     walk_to_location(A,M,XEnterMine,YEnterMine),
     walk_to_location(A,M,XNickos,YNickos),
     assert(plan(talk(A,nickos,'Hi Nickos! I spoke with Nathan and Naem.'))),
     assert(plan(talk(nickos,A,'OK! I give you 500 GPs.'))),
     ownership(A,zeny,GPs),
     retract(ownership(A,zeny,GPs)),
     NewGPs is GPs+500, assert(ownership(A,zeny,NewGPs)),
     walk_to_location(A,M,XLieutenantDausen,YLieutenantDausen),
     assert(plan(talk(A,lieutenant_dausen,'Hi Lieutenant Dausen! I talk to you again.'))),
     walk_to_location(A,M,XNickos,YNickos),
     assert(plan(talk(A,nickos,'Hi Nickos! I talk to you again.'))),

% Ovdje ide dio o tome sto agent radi u pecini

     retract(waiting_quest(NPC,A,miners_quest))                   % Brisi zapis da je agent dobio ovaj quest kao zadatak
     ->                                                            % Ako je sve do ovdje obavljeno onda...
     assert(done_quest(A,miners_quest));                          % ...dodaj cinjenicu da je agent obavio ovaj quest...
     assert(failed_quest(NPC,A,miners_quest)).                    % ...inace dodaj cinjenicu da nije uspio obaviti ovaj quest

% ... ONDA IDE JOŠ DOSTA LOW-LEWEL QUESTOVA ALI MISLIM DA SU SVI JEDNOSTAVNI KAO I OVI GORE

% %%%%%%%%%%%%%%%%%%%%%%%%%%%%% %
%  Medium Level Quests (21-50)  %
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%% %

% Quest: Letter Quest
% -------------------

% Starting location: 027-2 Graveyard
% Required level: 21
% Recommended for level: 30
% Redoable: Yes, forever
% Prerequisites: None
% Reward: EXP and GP
% Costs: None

% What To Do:

%   You have two options to get to the Graveyard. First, you can go south of Hurnscald and talk to Dyrin and pay 750 GP to be transported there. If you're feeling more adventurous, you can try to find your way there by foot. Travel west from the Woodlands to the southwest of Hurnscald, where Gwendolyn is. Eventually, you will reach the Woodland Swamp area. Continue going west until you reach the Swamp. Head a bit northwest, and you can find the path to the graveyard.
%   The caretaker's hut is on your right, heading down the first track. Go inside.
%   Click on the caretaker, and after he talks to you the first time, and the text box is closed, click on him again. He will have a letter for you to deliver to Airlia.
%   To find Airlia, head south of the Soul Menhir in Hurnscald, and head east on the first street. Enter the second building. Airlia is inside on the right.
%   Talk to Airlia and deliver the letter to receive your reward.

% Akcija kojom nas agent A obavlja quest Letter Quest jer mu ga je zadao NPC:

% IMA GREŠKU - PRONAÆI JE:

do_quest(NPC,A,letter_quest) :-
     ownership(A,level,La), La>=21,
     waiting_quest(NPC,A,letter_quest),
     location(graveyard,M,XGraveyard,YGraveyard),
    (ownership(A,zeny,Ma),Ma>=750, /* ... a možda ima i neke dodatne razloge za pješaèenje koje bi trebalo ovdje navesti */
     location(dyrin,M,XDyrin,YDyrin)
     ->
     walk_to_location(A,M,XDyrin,YDyrin),
     assert(plan(talk(A,dyrin,'Hi Dyrin! I pay yout 750 GP for transport to Graveyard.'))),
     assert(plan(talk(dyrin,A,'OK. Let`s go!'))),
     retract(ownership(A,zeny,Ma)),
     NewMa is Ma-750,
     assert(ownership(A,zeny,NewMa));
     walk_to_location(A,M,XGraveyard,YGraveyard)), /* Ovdje je možda potrebno preciznije navesti plan za pješaèenje u Graveyard */
     /* Ovdje idu upute za ostatak questa */
     retract(waiting_quest(NPC,A,letter_quest))
     ->
     assert(done_quest(A,letter_quest));
     assert(failed_quest(NPC,A,letter_quest)).

























































% Formalizacija naseg quest-a:
% ---------------------------

% Quest: There are a number of dragon nests all around the world. Every 24+-1 hours a dragon lays an egg on a random location. A guild needs to provide three people (an archer, a warrior and a mage) to transport the egg to their castle (Guild describes a player group that currently works through a bot). In order to hatch the egg they need to bring it to the arch wizard with a magic hatching potion. The hatching potion is mixed by Pauline the Witch which needs certain ingredients to mix it. If you do not hatch the egg in 24 hours it goes bad. When the dragon is hatched it becomes the pet of the guilds castle. It also allows guild members to summon a dragon during their fights.

% Zmajeva gnijezda (STA JE SA JAJIMA?):

nest(36,62).
nest(45,97).
nest(35,92).
nest(14,81).
nest(6,61).





create_plan_list :-
      plan_list(Plan),                % Varijabla Plan je lista
      plan(Step),                     % Varijabla Korak je neki dogaðaj
      retract(plan_list(Plan)),       % Brišemo prethodnu listu
      retract(plan(Step)),            % Brišemo Korak
      append(Plan,[Step],NoviPlan),   % Spajamo prethodnu listu Plan sa novim korakom i sve spremamo u novu listu NoviPlan
      assert(plan_list(NoviPlan)),    % Ubacujemo predikat plan_list(NoviPlan) u bazu èinjenica
      create_plan_list.               % ponovno pozivamo kreiranje plan-liste





% Pravilo prema kojem agent zna što treba raditi s tim da æe najprije poredati quest-ove po prioritetu:

do(A) :-
     sort_quests(A),
    (quest_no(NPC,A,Q,1)
     ->
     do_quest(NPC,A,Q);
     random_walk(A)).
     create_plan_list.


% Naredbe koje mogu biti zadane:
% -----------------------------

% PLAN (Lista akcija nekog agenta: Akcija1, Akcija2, ..., AkcijaN) JE NIZ INSTANCI PREDIKATA "plan"


















