/* The Mana World Planner
   Currently only for Candor Quests */

:- use_module( library( random ) ).

:- dynamic current_quest/1.
:- dynamic current_action/2.
:- dynamic quest_no/4.
:- dynamic quest_sign/3.
:- dynamic waiting_quest/3.
:- dynamic solved_quest/1.
:- dynamic npc_message/3.
:- dynamic party/3. % party_name, player_name, status (founder/member)
:- dynamic party_member/1. % player_name
:- dynamic party_count/1. 
:- dynamic invitation/4. % party, from player name, to player name, status (sent/accepted/declined)
:- dynamic social_network/3.
:- dynamic slot/4.
:- dynamic agent_location/4. % The current agent
:- dynamic npc_location/4.
:- dynamic player_location/4. % Other players
:- dynamic location/4.
:- dynamic location/5.
:- dynamic mob_location/5.
:- dynamic item_location/5.
:- dynamic ownership/3.
:- dynamic been_at/1.

/*
Actions:
 Go to location M,X,Y (on map, one click)
 Walk to location M,X,Y (possibly on other map, multiple goToLoaction)
 Random walk (possibly on another map, multiple walkToLocation)
 Follow player
 Go to NPC
 Talk to NPC
 Answer NPC
 Stop talking to NPC
 Pick up item
 Equip item
 Find mob
 Attack mob
 Talk to player
 Trade with player
 Create Party
 Accept party invite
 Send party invite
 Decline party invite
*/

do_action( goToLocation( Map, X, Y ), goToLocation, [ Map, X, Y ] ).

done_action( goToLocation( Map, X, Y ), Agent ) :-
	agent_location( Agent, Map, X, Y ).

do_action( tryToGoToLocation( Map, X, Y ), tryToGoToLocation, [ Map, X, Y ] ).

do_action( answerNPC( NPCName, Answer ), answerNPC, [ NPCID, Answer ] ) :-	
	npc_id( NPCID, NPCName ).

do_action( goToNPC( NPCName ), goToNPC, [ NPCName, Map, X, Y ] ) :-
	npc( _, NPCName, Map, X, Y ).

do_action( stopTalkingToNPC( NPCName ), stopTalkingToNPC, [ NPCID ] ) :-
	npc_id( NPCID, NPCName ).

do_action( stopTalkingToNPCSorfina( _ ), stopTalkingToNPCSorfina, [ 110008655 ] ). % Bug in TMW?

do_action( talkToNPC( NPCName ), talkToNPC, [ NPCID ] ) :-
	npc_id( NPCID, NPCName ).

do_action( equipItem( ItemName ), equipItem, [ ItemSlot ] ) :-
	slot( _, ItemSlot, ItemID, _ ),
	item( ItemID, _, ItemName ).

do_action( killMob( MobName ), killMob, [ MobName ] ).

/* Actions without parameters */
do_action( Action, Action, [ dummy ] ) :-
	NonParamActions = [ joinPartyIfNotInParty, joinPartyIfBetter, askForStats,       
			    invitePlayersToParty,  createParty,       giveStats,
                            addNewMember,          removeMember ],
	member( Action, NonParamActions ).

/* Random walk on a given map (avoiding blocked places) 
TODO: Implement walking from map to map */
max_dist( 6 ).

randomWalk( Agent, Map, X, Y ) :-
	agent_location( Agent, Map, X1, Y1 ),
	max_dist( MD ),
	Xp is X1 + MD,
	Yp is Y1 + MD,
	Xn is X1 - MD,
	Yn is Y1 - MD,
	random_between( Xn, Xp, X ),
	random_between( Yn, Yp, Y ),
	\+ blocked( Map, X, Y ).

/*

Quests:
Sorfina - tutorial
Tanisha - maggots
Jessie - stat reset
Ishi - monster points
Ayasha - hide and seek
Zegas - maggot bomb
Valon - kill mobs
Morgan - magic (intelligence 5)
Hasan - scorpion

*/

/*
 Sorfina's quest
*/
plan_quest( 'tutorial', Plan ) :-
	A01 = answerNPC( 'ServerInitial', 1 ),
	A02 = tryToGoToLocation( '029-2', 29, 24 ),
	A03 = goToNPC( 'Sorfina' ),
	A04 = answerNPC( 'Sorfina', 1 ),
	A05 = answerNPC( 'Sorfina', 1 ),
	A06 = answerNPC( 'Sorfina', 1 ),
	A07 = goToNPC( '#Carpet' ),
	A08 = stopTalkingToNPCSorfina( 'Sorfina' ), % 8655 ???
	A09 = stopTalkingToNPCSorfina( 'Sorfina' ), % 8655 ???
	A10 = goToLocation( '029-2', 29, 24 ),
	A11 = talkToNPC( 'Dresser#tutorial' ),
	A12 = stopTalkingToNPC( 'Dresser#tutorial' ),
	A13 = equipItem( 'Ragged Shorts' ), % use slot numbers 2 and 3
	A14 = equipItem( 'Cotton Shirt' ), 
	A15 = goToNPC( 'Sorfina' ),
	A16 = talkToNPC( 'Sorfina' ),
	A17 = stopTalkingToNPC( 'Sorfina' ),
	A18 = tryToGoToLocation( '029-2', 44, 31 ),
	Plan = [ a( 1, A01 ),   a( 2, A02 ),  a( 3, A03 ),  a( 4, A04 ), 
		 a( 5, A05 ),   a( 6, A06 ),  a( 7, A07 ),  a( 8, A08 ), 
                 a( 9, A09 ),  a( 10, A10 ), a( 11, A11 ), a( 12, A12 ), 
                 a( 13, A13 ), a( 14, A14 ), a( 15, A15 ), a( 16, A16 ),
		 a( 17, A17 ), a( 18, A18 ) ].

/*
 Tanisha's quest
*/
plan_quest( 'maggots', Plan ) :-
	A01 = answerNPC( 'Tanisha', 1 ),
	A02 = answerNPC( 'Tanisha', 1 ), % next, next, next, next (4 times)
	A03 = stopTalkingToNPC( 'Tanisha' ), 
	A04 = stopTalkingToNPC( 'Tanisha' ), 
	A05 = stopTalkingToNPC( 'Tanisha' ), 
	A06 = stopTalkingToNPC( 'Tanisha' ), 
	A07 = stopTalkingToNPC( 'Tanisha' ), 
	A08 = equipItem( 'Knife' ),
	A09 = tryToGoToLocation( '029-2', 102, 87 ),
	A10 = killMob( 'Maggot' ),
	A11 = killMob( 'Maggot' ),
	A12 = killMob( 'Maggot' ),
	A13 = killMob( 'Maggot' ),
	A14 = killMob( 'Maggot' ),
	A15 = killMob( 'Maggot' ),
	A16 = killMob( 'Maggot' ),
	A17 = killMob( 'Maggot' ),
	A18 = killMob( 'Maggot' ),
	A19 = killMob( 'Maggot' ),
	A20 = goToNPC( 'Tanisha' ),
	A21 = talkToNPC( 'Tanisha' ), % 5 x next
	A22 = stopTalkingToNPC( 'Tanisha' ),
	A23 = stopTalkingToNPC( 'Tanisha' ),
	A24 = stopTalkingToNPC( 'Tanisha' ),
	A25 = stopTalkingToNPC( 'Tanisha' ),
	A26 = stopTalkingToNPC( 'Tanisha' ),
	A27 = tryToGoToLocation( '029-2', 114, 93 ),
	Plan = [ a( 1, A01 ),   a( 2, A02 ),  a( 3, A03 ),  a( 4, A04 ), 
		 a( 5, A05 ),   a( 6, A06 ),  a( 7, A07 ),  a( 8, A08 ), 
                 a( 9, A09 ),  a( 10, A10 ), a( 11, A11 ), a( 12, A12 ), 
                 a( 13, A13 ), a( 14, A14 ), a( 15, A15 ), a( 16, A16 ),
		 a( 17, A17 ), a( 18, A18 ), a( 19, A19 ), a( 20, A20 ), 
		 a( 21, A21 ), a( 22, A22 ), a( 23, A23 ), a( 24, A24 ), 
                 a( 25, A25 ), a( 26, A26 ), a( 27, A27 ) ].

/* Soul Menhir#candor */
plan_quest( 'soul_menhir_candor', Plan ) :-
	A01 = answerNPC( 'Soul Menhir#candor', 1 ),
	A02 = stopTalkingToNPC( 'Soul Menhir#candor' ),
	A03 = tryToGoToLocation( '029-1', 42, 96 ),
	Plan = [ a( 1, A01 ),   a( 2, A02 ),   a( 3, A03 ) ].


/* Ferry Schedule#8 */
plan_quest( 'ferry_schedule_8', Plan ) :- 
	A01 = answerNPC( 'Ferry Schedule#8', 1 ),
	A02 = stopTalkingToNPC( 'Ferry Schedule#8' ),
	A03 = tryToGoToLocation( '029-1', 42, 96 ),
	Plan = [ a( 1, A01 ),   a( 2, A02 ),   a( 3, A03 ) ].

recurring_quest( 'soul_menhir_candor' ).

/* Kaan */
plan_quest( 'kaan', Plan ) :-
	A01 = answerNPC( 'Kaan', 1 ),
	A02 = stopTalkingToNPC( 'Kaan' ),
	Plan = [ a( 1, A01 ),   a( 2, A02 ) ].	

/* Aidan's quest - monster points */
plan_quest( 'monster_points', Plan ) :-
	A01 = answerNPC( 'Aidan', 1 ),
	A02 = answerNPC( 'Aidan', 1 ), % next, next, next, next (4 times)
	A03 = stopTalkingToNPC( 'Aidan' ), 
	A04 = stopTalkingToNPC( 'Aidan' ), 
	A05 = stopTalkingToNPC( 'Aidan' ), 
	A06 = stopTalkingToNPC( 'Aidan' ),
	Plan = [ a( 1, A01 ),   a( 2, A02 ),  a( 3, A03 ),  a( 4, A04 ), 
		 a( 5, A05 ),   a( 6, A06 ) ].

/* Default: stop talking */
plan_quest( 'stop_taking', Plan ) :-
	waiting_quest( NPC, _, stop_talking ),
	A01 = stopTalkingToNPC( NPC ),
	Plan = [ a( 1, A01 ) ].	

recurring_quest( 'stop_talking' ).

/* Random walk */
plan_quest( 'random_walk', Plan ) :-
	waiting_quest( NPC, _, random_walk ),
	A01 = goToRandomLocationOnMap,
	Plan = [ a( 1, A01 ) ].

plan_quest( 'random_walk', Plan ) :-
	waiting_quest( NPC, _, random_walk ),
	A01 = goToNearByNPC,
	Plan = [ a( 1, A01 ) ].

/*** Party related quests ***/

/* Leader - proactive plan (creates a party) */
plan_quest( 'leader', Plan ) :-
	A01 = createParty,
	Plan = [ a( 1, A01 ) ].

/* Leader - periodic plan (already created a party, only invite new people) */
plan_quest( 'invite_player', Plan ) :-
	A01 = invitePlayersToParty, % same as above
	Plan = [ a( 1, A01 ) ].

recurring_quest( 'invite_player' ).

/* Leader - reactive plan (do stuff when asked to) */
plan_quest( 'store_party_stats', Plan ) :-
	A01 = giveStats,
	A02 = addNewMember,
	A03 = removeMember,
	Plan = [ a( 1, A01 ),   a( 2, A02 ),   a( 3, A03 ) ].

/* Opportunist - reactive plan (if someone invites me, I evaluate and eventually join) */
plan_quest( 'opportunist', Plan ) :- 
	A01 = askForStats,
	A02 = joinPartyIfBetter,
	Plan = [ a( 1, A01 ),   a( 2, A02 ) ].

/* Extremist follower - reactive plan (if someone invites me, I join if I am not in another party) */
plan_quest( 'extremist_follower', Plan ) :-
	A01 = joinPartyIfNotInParty,
	Plan = [ a( 1, A01 ) ].

recurring_quest( 'leader' ).

/* Auxiliary predicates */

sort_quests( A ) :-
     waiting_quest( NPC1, A, Q1 ),
     waiting_quest( NPC2, A, Q2 ),
     quest_sign( A, Q1, QS1 ),
     quest_sign( A, Q2, QS2 ),
     quest_no( NPC1, A, Q1, QN1 ),
     quest_no( NPC2, A, Q2, QN2 ),
     QS1 > QS2,
     QN1 > QN2
     ->
     retract( quest_no( NPC1, A, Q1, QN1 ) ),
     retract( quest_no( NPC2, A, Q2, QN2 ) ),
     assert( quest_no( NPC1, A, Q1, QN2 ) ),
     assert( quest_no( NPC2, A, Q2, QN1 ) ),
     sort_quests( A );
     true.

next_action( Action ) :-
	current_quest( Quest ),
	\+ current_action( _, _ ),
	plan_quest( Quest, [ a( Num, Action ) | _ ] ),
	assert( current_action( Num, Action ) ), !.

next_action( Action ) :-
	current_quest( Quest ),
	current_action( CNum, CAction ),
	plan_quest( Quest, Actions ),
	nextto( a( CNum, CAction ), a( Num, Action ), Actions ),
	retract( current_action( CNum, CAction ) ),
	assert( current_action( Num, Action ) ).

next_action( done ) :-
	current_quest( Quest ),
	current_action( CNum, CAction ),
	plan_quest( Quest, Actions ),
	\+ nextto( a( CNum, CAction ), a( _, _ ), Actions ),
	retract( current_action( CNum, CAction ) ),
	retract( current_quest( Quest ) ),
	retract( waiting_quest( _, _, Quest ) ),
	assert( solved_quest( Quest ) ).

action_failed :-
	retract( current_action( _, _ ) ).

start_quest( Quest ) :-
	retract( current_quest( _ ) ),
	retract( current_action( _, _ ) ),
	assert( current_quest( Quest ) ), !.

start_quest( Quest ) :-
	assert( current_quest( Quest ) ).

store( File ) :-
	open( File, write, Out ),
	with_output_to( Out, listing ),
	close( Out ).

visited_npc( NPC ) :-
	quest_no( NPC, _, Quest, _ ),
	solved_quest( Quest ),
	\+ recurring_quest( Quest ).

nearby_player( Agent, Name, ID ) :-
	agent_location( Agent, Map, X1, Y1 ),
	player_location( Name, Map, X2, Y2 ),
	max_dist( D ),
	X is abs( X1 - X2 ),
	Y is abs( Y1 - Y2 ),
	D >= X,
	D >= Y,
	userid( Name, ID ),
	Agent \= Name.

nearby_non_member( Agent, Name, ID ) :-
	nearby_player( Agent, Name, ID ),
	\+ party_member( Name ).

add_party_member( Member ) :-
	assert( party_member( Member ) ),
	retract( party_count( C ) ),
	C1 is C + 1,
	assert( party_count( C1 ) ).

remove_party_member( Member ) :-
	retract( party_member( Member ) ),
	retract( party_count( C ) ),
	C1 is C - 1,
	assert( party_count( C1 ) ).

% Every leader has a party with one member (themselves)
party_count( 1 ).
