/* The Mana World Planner
   Currently only for Candor Quests */


:- dynamic current_quest/1.
:- dynamic current_action/2.
:- dynamic quest_no/4.
:- dynamic quest_sign/3.
:- dynamic waiting_quest/3.
:- dynamic solved_quest/1.
:- dynamic npc_message/3.
:- dynamic party/2.
:- dynamic social_network/3.
:- dynamic slot/4.
:- dynamic location/4.
:- dynamic location/5.
:- dynamic ownership/3.

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
 Fund mob
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
	location( Agent, Map, X, Y ).

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

do_action( killMob( MobName ), killMob, [ MobID ] ) :-
	mob( MobID, _, MobName ).

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
	A02 = goToNPC( 'Sorfina' ),
	A03 = answerNPC( 'Sorfina', 1 ),
	A04 = answerNPC( 'Sorfina', 1 ),
	A05 = answerNPC( 'Sorfina', 1 ),
	A06 = tryToGoToLocation( '029-2', 29, 24 ),
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
	A01 = goToNPC( 'Tanisha' ),
	A02 = answerNPC( 'Tanisha', 1 ),
	A03 = answerNPC( 'Tanisha', 1 ), % next, next, next, next (4 times)
	A04 = stopTalkingToNPC( 'Tanisha' ), 
	A05 = stopTalkingToNPC( 'Tanisha' ), 
	A06 = stopTalkingToNPC( 'Tanisha' ), 
	A07 = stopTalkingToNPC( 'Tanisha' ), 
	A08 = stopTalkingToNPC( 'Tanisha' ), 
	A09 = equipItem( 'Knife' ),
	A10 = killMob( 'Maggot' ),
	A11 = killMob( 'Maggot' ),
	A12 = killMob( 'Maggot' ),
	A13 = killMob( 'Maggot' ),
	A14 = killMob( 'Maggot' ),
	A15 = talkToNPC( 'Tanisha' ), % 5 x next
	A16 = stopTalkingToNPC( 'Tanisha' ),
	A17 = tryToGoToLocation( '029-2', 114, 93 ),
	Plan = [ a( 1, A01 ),   a( 2, A02 ),  a( 3, A03 ),  a( 4, A04 ), 
		 a( 5, A05 ),   a( 6, A06 ),  a( 7, A07 ),  a( 8, A08 ), 
                 a( 9, A09 ),  a( 10, A10 ), a( 11, A11 ), a( 12, A12 ), 
                 a( 13, A13 ), a( 14, A14 ), a( 15, A15 ), a( 16, A16 ),
		 a( 17, A17 ) ].
	
	
	

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

