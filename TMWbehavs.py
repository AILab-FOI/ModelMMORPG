import spade
from spade.SWIKB import SWIKB as KB
import time
from random import random, randint, choice
from os.path import isfile, join


class ExclusiveBehaviour( spade.Behaviour.OneShotBehaviour ):
	'''Makes sure that two behaviours of this type do not run in parallel'''
	def wait( self ):
		if not hasattr( self.myAgent, 'semaphore' ) or self.myAgent.semaphore == False:
			self.myAgent.semaphore = True
			return
			
		while self.myAgent.semaphore:
			time.sleep( 0.1 )

	def release( self ):
		self.myAgent.semaphore = False

class AnswerNPC( ExclusiveBehaviour ):
	"""Answer to an NPC with given npcID and answer id"""
	def __init__( self, npcID, answer, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.npcID, self.answer = npcID, answer

	def _process( self ):
		self.wait()
		try:
			self.myAgent.say( "Answering to NPC %s with %s ..." % ( self.npcID, self.answer ) )
			self.myAgent.answerToNPC( self.npcID, self.answer )
			time.sleep( 1 )
			self.myAgent.result = True
		except Exception as e:
			print 'ERROR', e
			self.myAgent.result = False
		self.release()


class stopTalkingToNPC( ExclusiveBehaviour ):
	"""Stop talking to an NPC with given npcID"""
	def __init__( self, npcID, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.npcID = npcID

	def _process( self ):
		self.wait()
		try:
			self.myAgent.say( "Stopping communication with NPC %s ..." % ( self.npcID ) )
			self.myAgent.closeCommunication( self.npcID )
			self.myAgent.result = True
		except Exception as e:
			print 'ERROR', e
			self.myAgent.result = False
		self.release()


class talkToNPC( ExclusiveBehaviour ):
	"""Talk to an NPC with given npcID"""
	def __init__( self, npcID, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.npcID = int( npcID )

	def _process( self ):
		self.wait()
		try:
			self.myAgent.say( "Talking to NPC %d ..." % ( self.npcID ) )
			self.myAgent.talkToNPC( self.npcID )
			self.myAgent.result = True
		except Exception as e:
			print 'ERROR', e
			self.myAgent.result = False
		self.release()


class goToNPC( ExclusiveBehaviour ):
	"""Go to an NPC with given npc name, mapID and x,y coordinates"""
	def __init__( self, npc, mapID, x, y, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.npc, self.mapID, self.x, self.y = npc, mapID, x, y

	def _process( self ):
		self.wait()
		try:
			self.myAgent.say( "Going to NPC %s at location %s %d-%d ..." % ( self.npc, self.mapID, self.x, self.y ) )
			self.myAgent.setDestination( self.x, self.y, 2 )
			query = "assert( been_at( '%s' ) )" % self.npc
			self.myAgent.kb.ask( query )
			time.sleep( 2 )
			self.myAgent.result = True
		except Exception as e:
			print 'ERROR', e
			self.myAgent.result = False
		self.release()


class goToLocation( ExclusiveBehaviour ):
	"""Go to location with given mapID and x,y coordinates"""
	def __init__( self, mapID, x, y, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.mapID, self.x, self.y = mapID, x, y

	def _process( self ):
		self.wait()
		try:
			self.myAgent.say( "Going to location %s-%d-%d ..." % ( self.mapID, self.x, self.y ) )
			self.myAgent.setDestination( self.x, self.y, 2 )
			time.sleep( 2 )
			self.myAgent.result = True
		except Exception as e:
			print 'ERROR', e
			self.myAgent.result = False
		self.release()


class equipItem( ExclusiveBehaviour ):
	"""Equip an item in a given slot"""
	def __init__( self, slot, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.slot = slot

	def _process( self ):
		self.wait()
		try:
			self.myAgent.say( "Trying to equip item in slot %d ..." % ( self.slot ) )
			self.myAgent.itemEquip( self.slot )
			time.sleep( 1 )
			self.myAgent.result = True
		except Exception as e:
			print 'ERROR', e
			self.myAgent.result = False
		self.release()


class killMob( ExclusiveBehaviour ):
	"""Kill a mob with given mobname"""
	def __init__( self, mobname, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.mobname = mobname

	def isThereANearMobWithType( self, mobname ):
		mp, x, y = self.myAgent.location

		query = "mob( MID, _, '%s' )" % mobname
		res = self.myAgent.kb.ask( query )
		ret = [ { "BID": bid, "X": l[ -1 ][ 1 ], "Y": l[ -1 ][ 2 ] } for bid, l in self.myAgent.pb.monsterMovements.items() if l[ -1 ][ 0 ] == int( res[ 0 ][ "MID" ] ) ]
		return sorted( ret, key=lambda x: x[ "BID" ] )

	def amIDone( self, location ):
		while self.myAgent.location == None:
			self.myAgent.getMyLocation()
			time.sleep( 0.1 )
		return location == self.myAgent.location

	def _process( self ):
		self.wait()
		try:
			self.myAgent.say( "Trying to attack a %s ..." % ( self.mobname ) )
			mobs = self.isThereANearMobWithType( self.mobname )[ ::-1 ]  # start with the last mob seen
			mob = False
			if mobs:
				for mob in mobs[ :-3 ] or mobs:  # only last 3 mobs
					for i in range( 5 ):  # Retry 5 times
						monster_ID = int( mob[ "BID" ] )
						monster_X = int( mob[ "X" ] )
						monster_Y = int( mob[ "Y" ] )
						self.myAgent.say( "Monster ID: " + str( monster_ID ) )
						self.myAgent.setDestination( monster_X, monster_Y, 2 )
						time.sleep( 1 )
						self.myAgent.attack( monster_ID, 7 )  # 7 to keep attacking, 0 for one attack
						self.myAgent.setDestination( monster_X - randint( 0, 2 ), monster_Y - randint( 0, 2 ), 2 )
						self.myAgent.attack( monster_ID, 7 )
						time.sleep( 1 )
						self.myAgent.setDestination( monster_X + randint( 0, 2 ), monster_Y + randint( 0, 2 ), 2 )
						self.myAgent.attack( monster_ID, 7 )
						time.sleep( 1 )
						self.myAgent.setDestination( monster_X - randint( 0, 2 ), monster_Y + randint( 0, 2 ), 2 )
						self.myAgent.attack( monster_ID, 7 )
						time.sleep( 1 )
						self.myAgent.setDestination( monster_X + randint( 0, 2 ), monster_Y - randint( 0, 2 ), 2 )
						self.myAgent.attack( monster_ID, 7 )
						time.sleep( 1 )
						if self.amIDone( self.myAgent.destinationNPC ):
							self.myAgent.say( "I'm done fighting already!" )
							break
					if self.amIDone( self.myAgent.destinationNPC ):
						self.myAgent.say( "I'm done fighting already!!" )
						break
				if not mob:
					self.myAgent.say( "There are no monsters of type %s near me. " % self.mobname )
			else:
				while self.myAgent.location == None:
					location = self.myAgent.getMyLocation()
					time.sleep( 0.1 )
				mp, x, y = self.myAgent.location
				self.myAgent.say( "I do not seem to see any %s monsters, I'll try to move a bit ..." % self.mobname )
				self.myAgent.setDestination( int( x ) + choice( [ -1, 1 ] ), int( y ) + choice( [ -1, 1 ] ), 2 ) # try to move the agent a bit
				self.myAgent.say( "There are no monsters of this type near me. Giving up." )
			self.myAgent.result = True 
		except Exception as e:
			print 'ERROR', e
			self.myAgent.result = False
		self.release()


class randomWalk( ExclusiveBehaviour ):
	"""Randomly walk around until something interesting comes up"""
	def isThereANearByNPC( self ):
		mp, x, y = self.myAgent.location
		query = "MapName = '%s', npc_location( NPC, MapName, X, Y ), \+ been_at( NPC ), npc( _, NPC, MapName, X, Y ), npc_id( NID, NPC ), DX is abs( X - %s ), DY is abs( Y - %s ), DX < 6, DY < 6." % ( mp, x, y )
		res = self.myAgent.kb.ask( query )
		if res:
			return choice( res )

	def _process( self ):
		self.wait()
		try:
			nearnpc = self.isThereANearByNPC()
			if nearnpc:
				npc = nearnpc[ 'NPC' ]
				npcID = int( nearnpc[ 'NID' ] )
				mapID = nearnpc[ 'MapName' ]
				x = int( nearnpc[ 'X' ] )
				y = int( nearnpc[ 'Y' ] )
				self.myAgent.say( 'Trying to go to NPC: %s' % npc )
				try:
					b = goToNPC( npc, mapID, x, y )
					self.myAgent.addBehaviour( b )
					time.sleep( 2 )

					b = talkToNPC( npcID )
					self.myAgent.addBehaviour( b )
					self.myAgent.result = True
				except Exception as e:
					print 'ERROR', e
					self.myAgent.result = False
			else:
				query = "randomWalk( '%s', Map, X, Y ), !." % self.myAgent.avatar_name
				res = self.myAgent.kb.ask( query )
				if res:
					res = res[ 0 ]
					mp = res[ 'Map' ]
					x = int( res[ 'X' ] )
					y = int( res[ 'Y' ] )
				else:
					mp, x, y = self.myAgent.location
					mn, mx = -5, 6
					x = int( x )
					y = int( y )
					x += randint( mn, mx )
					y += randint( mn, mx )
				b = goToLocation( mp, x, y )
				self.myAgent.addBehaviour( b )
				time.sleep( 1 )
				self.myAgent.result = True
		except Exception as e:
			print 'ERROR', e
			self.myAgent.result = False
		self.release()


class FindPlayer( ExclusiveBehaviour ):
	''' Find a nearby player '''
	pass

class inviteToParty( ExclusiveBehaviour ):
	''' Invite a given player to a party '''
	def __init__( self, player, party_name, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.player = player
		self.party_name = party_name

	def _process( self ):
		self.wait()
		self.myAgent.inviteToParty( self.player )
		self.myAgent.whisper( self.player, 'Oh, you are so cool, please join my party!' )
		query = "assert( invitation( '%s', '%s', '%s', sent ) )" % ( self.party_name, self.myAgent.avatar_name, self.player )
		self.myAgent.kb.ask( query )
		self.myAgent.say( 'I have just invited %s to my party called %s.' % ( self.player, self.party_name ) )
		self.release()
		

class joinParty( ExclusiveBehaviour ):
	''' Join a given party per invitation ''' # responseToPartyInvite 1 accept 0 refuse whisper
	def __init__( self, player, party_name, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.player = player
		self.party_name = party_name

	def _process( self ):
		self.wait()
		self.myAgent.responseToPartyInvite( 1 )
		self.myAgent.whisper( self.player, 'Party time!!!' )
		query = "retract( invitation( '%s', '%s', '%s', _ ) )" % ( self.party_name, self.myAgent.avatar_name, self.player )
		self.myAgent.kb.ask( query )
		time.sleep( 0.5 )
		query = "assert( invitation( '%s', '%s', '%s', accepted ) )" % ( self.party_name, self.myAgent.avatar_name, self.player )
		self.myAgent.kb.ask( query )
		self.myAgent.say( "I have just joined %s's party called %s." % ( self.player, self.party_name ) )
		self.release()

class declinePartyInvitation( ExclusiveBehaviour ):
	''' Decline a party invitation '''
	def __init__( self, player, party_name, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.player = player
		self.party_name = party_name

	def _process( self ):
		self.wait()
		self.myAgent.responseToPartyInvite( 0 )
		self.myAgent.whisper( self.player, 'Meh...' )
		query = "retract( invitation( '%s', '%s', '%s', _ ) )" % ( self.party_name, self.myAgent.avatar_name, self.player )
		self.myAgent.kb.ask( query )
		time.sleep( 0.5 )
		query = "assert( invitation( '%s', '%s', '%s', declined ) )" % ( self.party_name, self.myAgent.avatar_name, self.player )
		self.myAgent.kb.ask( query )
		self.myAgent.say( "I have just refused to join %s's party called %s." % ( self.player, self.party_name ) )
		self.release()

class createParty( ExclusiveBehaviour ):
	''' Create a party '''
	def __init__( self, party_name, *args, **kwargs ):
		ExclusiveBehaviour.__init__( self, *args, **kwargs )
		self.party_name = party_name

	def _process( self ):
		self.wait()
		self.myAgent.createParty( self.party_name )
		query = "assert( party( '%s', '%s', founder ) )" % ( self.party_name, self.myAgent.avatar_name )
		self.myAgent.kb.ask( query )
		self.myAgent.say( "I have just created my party called %s." % self.party_name )
		self.release()

class leaveParty( ExclusiveBehaviour ):
	''' Leave current party '''
	def _process( self ):
		self.wait()
		self.myAgent.createParty( self.party_name )
		query = "retract( party( _, '%s', _ ) )" % self.myAgent.avatar_name
		self.myAgent.kb.ask( query )
		self.myAgent.say( "I have just left my party." )
		self.release()

class Reason( spade.Behaviour.Behaviour ):
	def storeKB( self ):
		''' Store the current state of the KB for later use '''
		self.myAgent.kb.ask( "store( '%s' )" % self.myAgent.kbfile )
		self.myAgent.say( 'Stored my current state of mind!' )

	def getInventory( self ):
		''' Get current inventory
			Returns dictionary { itemSlot:( itemID, itemAmount ) } '''
		''' TODO: make all getters to return None if there were no changes to optimize update '''
		if not hasattr( self.myAgent, 'inventory_cache' ):
			self.myAgent.inventory_cache = None
		try:
			if self.myAgent.inventory_cache == self.myAgent.pb.playerInventory:
				return None  # No changes in inventory
			self.myAgent.inventory_cache = dict( [ ( i, j ) for i, j in self.myAgent.pb.playerInventory.items() ] )
			if self.myAgent.inventory_cache:
				inv = dict( [ ( j, ( i.itemID, i.itemAmount ) ) for j, i in self.myAgent.inventory_cache.items() ] )
				return inv
		except:
			return {}

	def getVisibleItems( self ):
		''' Get visible ( dropped ) items
			Returns dictionary { itemID: ( amount, mapID, X, Y ) } '''
		if not hasattr( self.myAgent, 'droppeditems_cache' ):
			self.myAgent.droppeditems_cache = None
		try:
			if self.myAgent.droppeditems_cache == self.myAgent.pb.droppedItems:
				return None
			self.myAgent.droppeditems_cache = self.myAgent.pb.droppedItems
			items = dict( [ ( i[ 0 ], ( i[ 3 ], self.myAgent.pb.playerMap, i[ 1 ], i[ 2 ] ) ) for i in self.myAgent.droppeditems_cache ] )
			return items
		except:
			return {}

	def getVisibleMobs( self ):
		''' Get visible mobs
			Returns dictionary { mob_being_ID:( mobtype, mapID, X, Y ) } '''
		if not hasattr( self.myAgent, 'mobs_cache' ):
			self.myAgent.mobs_cache = None
		try:
			self.myAgent.say( 'Monster movements ( agent ): ' + str( self.myAgent.pb.monsterMovements ) )
			self.myAgent.say( 'Update cache?: ' + str( self.myAgent.mobs_cache == self.myAgent.pb.monsterMovements ) )
			if self.myAgent.mobs_cache == self.myAgent.pb.monsterMovements:
				self.myAgent.say( 'Nothing to update' )
				return None
			self.myAgent.mobs_cache = dict( [ ( i, j ) for i, j in self.myAgent.pb.monsterMovements.items() ] )
			mobs = dict( [ ( i, ( k[ -1 ][ 0 ], self.myAgent.pb.playerMap, k[ -1 ][ 1 ], k[ -1 ][ 2 ] ) ) for i, k in self.myAgent.mobs_cache.items() ] )
			self.myAgent.say( 'Returning ' + str( mobs ) )
			return mobs
		except Exception, e:
			print 'ERROR', e
			return None

	def getVisibleNPCs( self, recursion_level=0 ):
		''' Get visible NPCs ( e.g. NPCs on the same map )
			returns dict { NPC name:( Map, X, Y, NPC type ) }'''
		MAX_RECURSION = 3
		if not hasattr( self.myAgent, 'location' ) or self.myAgent.location is None:
			return {}
		if not hasattr( self.myAgent, 'map_cache' ):
			self.myAgent.map_cache = None
		if self.myAgent.map_cache == self.myAgent.location[ 0 ] and recursion_level == 0:
			return None  # I'm still on the same map, so the NPCs are the same
		self.myAgent.map_cache = self.myAgent.location[ 0 ]
		query = "npc( Type, Name, '%s', X, Y )" % self.myAgent.location[ 0 ]
		time.sleep( 1 )
		self.myAgent.say( "Querying knowledge base with: " + query )
		res = self.myAgent.kb.ask( query )
		NPCs = {}
		if res:
			for r in res:
				if 'Name' in r:
					if 'Debug' not in r[ 'Name' ]:
						NPCs[ r[ 'Name' ]] = ( self.myAgent.location[ 0 ], r[ 'X' ], r[ 'Y' ], r[ 'Type' ] )
		else:
			if recursion_level <= MAX_RECURSION:
				time.sleep( 1 )
				return self.getVisibleNPCs( recursion_level + 1 )
		return NPCs

	def getVisiblePlayers( self ):
		''' Get visible players
			Returns dict { character_name:( Map, X, Y ) } '''
		if not hasattr( self.myAgent, 'players_cache' ):
			self.myAgent.players_cache = None
		try:
			self.myAgent.listAllPlayers()
			time.sleep( 1 )
			if self.myAgent.players_cache == self.myAgent.pb.loggedInPlayers:
				return None
			self.myAgent.players_cache = self.myAgent.pb.loggedInPlayers
			# visible players are only players on the same map as I am
			visible_players = dict( [ ( i[ 0 ], i[ 1 ] ) for i in self.myAgent.players_cache.items() if i[ 1 ][ 0 ] == self.myAgent.location[ 0 ]] )
			return visible_players
		except:
			return {}

	def getNewNPCMessages( self ):
		''' Get new NPC messages '''
		if not hasattr( self.myAgent, 'npcmsg_cache' ):
			self.myAgent.npcmsg_cache = [ ]
		try:
			if self.myAgent.npcmsg_cache == self.myAgent.pb.npcMessages:
				return None
			npc_msgs = [ i for i in self.myAgent.pb.npcMessages if i not in self.myAgent.npcmsg_cache ]
			self.myAgent.npcmsg_cache.extend( [ i for i in npc_msgs ] )
			msgs = {}
			for npcid, message in npc_msgs:
				if npcid not in msgs:
					msgs[ npcid ] = [ ]
				msgs[ npcid ].append( message )
			return msgs
		except:
			return {}

	def interpretNPCMessage( self, npc, message ):
		''' Interpret NPC messages
			Returns tuple ( waiting_quest( npc, %s, quest_name ), quest_name, npc name )
			The first element in the tuple is a string Prolog predicate
			for the knowledge base where %s is a place to insert the agent's
			character name '''

		if npc != 'Sorfina': # I have no idea why this happens...
			try:
				query = "npc_id( %s, Name )" % npc
				res = self.myAgent.kb.ask( query )
				npc = res[ 0 ][ "Name" ]
			except Exception as e:
				pass
			

		# TODO: Also interpret other messages as possible preconditions for other actions
		if npc == 'ServerInitial':
			if message == '[Server/Client Notice]':
				return "waiting_quest( 'Sorfina', '%s', tutorial )", "tutorial", "Sorfina"
			else:
				return False, None, "Sorfina"
		elif npc == 'Sorfina' or npc == '110008655':
			return False, None, "Sorfina"
		elif npc == 'Dresser#tutorial':
			return False, None, "Sorfina"
		elif npc == 'Tanisha':
			return "waiting_quest( 'Tanisha', '%s', maggots )", "maggots", "Tanisha"
		elif npc == 'Soul Menhir#candor':
			return "waiting_quest( 'Soul Menhir#candor', '%s', soul_menhir_candor )", "soul_menhir_candor", "Soul Menhir#candor"
		elif npc == 'Kaan':
			return "waiting_quest( 'Kaan', '%s', kaan )", "kaan", "Kaan"
		elif npc == 'Aidan':
			return "waiting_quest( 'Aidan', '%s', monster_points )", "monster_points", "Aidan"
		elif npc == 'Ferry Schedule#8':
			return "waiting_quest( 'Ferry Schedule#8', '%s', ferry_schedule_8 )", "ferry_schedule_8", "Ferry Schedule#8"
		return "waiting_quest( '%s', '%s', stop_talking )" % npc, "stop_talking", npc

	def getQuestSignificance( self, quest ):
		''' Hard-coded significances of various quests loosely modelled after
			time of acquirement. First one is Sorfina's tutorial, then Tanisha's
			maggots, then ... '''
		if quest == 'tutorial':
			return 10000
		elif quest == 'maggots':
			return 9999
		elif quest == 'stop_talking':
			return 9998
		elif quest == 'soul_menhir_candor':
			return 9997
		elif quest == 'ferry_schedule_8':
			return 9996
		else:
			# (yet) unknown quest
			return 0

	def getPartyMembership( self ):
		''' Get party membership
			Returns string party name ( -1 if no party, None if no change ) '''
		if not hasattr( self.myAgent, 'party_cache' ):
			self.myAgent.party_cache = None
		try:
			self.myAgent.partyStatus( self.myAgent.avatar_name, self.myAgent.avatar_name )
			time.sleep( 1 )
			if self.myAgent.party_cache == self.myAgent.pb.playerParty[ self.myAgent.avatar_name ]:
				return None
			self.myAgent.party_cache = self.myAgent.pb.playerParty[ self.myAgent.avatar_name ]
			if self.myAgent.party_cache == 'None':
				return -1
			return self.myAgent.party_cache
		except:
			return None
		return -1

	def getSocialNetwork( self ):
		''' Dummy social network until lli is done '''
		dummy = {'Igor': 'friend', 'Bogdan': 'friend', 'Ivek': 'enemy'}
		if not hasattr( self.myAgent, 'soc_net_cache' ):
			self.myAgent.soc_net_cache = None
			return dummy
		return None

	def updateKB( self ):
		''' Update the knowledgebase based on current observation
			of the environment in TMW, e.g.:
			- list own location
			- list the inventory
			- list current visible items laying around ( include location and type )
			- list visible mobs/NPCs/other players ( include location and name )
			- list any changes in quest acomplishment ( e.g. quest solved )
			- list any ongoing or done conversation with NPCs that are possibly
			  giving out a quest
			- any changes in social network ( e.g. friends, enemies etc. )
			- any changes in organization ( e.g. party membership )
			...?
			and update the knowledge base accordingly'''

		if self.myAgent.character_list:
			self.myAgent.say( 'Updating my stats ...' )
			if not hasattr( self.myAgent, 'char_cache' ):
				self.myAgent.char_cache = None

			try:
				test = self.myAgent.char_cache.__dict__ != self.myAgent.character_list[ self.myAgent.character ].__dict__
			except:
				test = True

			if test:
				self.myAgent.char_cache = self.myAgent.character_list[ self.myAgent.character ]
				self.myAgent.avatar_name = self.myAgent.char_cache.name
				for token, value in self.myAgent.char_cache.__dict__.items():
					delete_predicate = "retract( ownership( '%s', '%s', _ ) )" % ( self.myAgent.avatar_name, token )
					if type( value ) == int:
						update_predicate = "assert( ownership( '%s', '%s', %d ) )" % ( self.myAgent.avatar_name, token, value )
					else:
						update_predicate = "assert( ownership( '%s', '%s', '%s' ) )" % ( self.myAgent.avatar_name, token, str( value ) )
					self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
					self.myAgent.kb.ask( delete_predicate )
					self.myAgent.kb.ask( update_predicate )
			else:
				self.myAgent.say( 'No changes in my stats ...' )


			self.myAgent.say( 'Updating my location ...' )
			location = self.myAgent.getMyLocation()
			if location:
				mapname, x, y = location
				delete_predicate = "retract( agent_location( _, _, _, _ ) )"
				update_predicate = "assert( agent_location( '%s', '%s', %s, %s ) )" % ( self.myAgent.avatar_name, mapname, x, y )
				self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
				self.myAgent.kb.ask( delete_predicate )
				self.myAgent.kb.ask( update_predicate )
			elif location is None:
				self.myAgent.say( "I didn't change my location ..." )
			else:
				self.myAgent.say( 'Location unknown ...' )


			self.myAgent.say( 'Updating my inventory ...' )
			# TODO: Possibly a bug
			inv = self.getInventory()
			if inv:
				for slot, j in inv.items():
					itemid, amount = j
					delete_predicate = "retract( ownership( '%s', %s, _ ) )" % ( self.myAgent.avatar_name, itemid )
					update_predicate1 = "assert( ownership( '%s', %s, %d ) )" % ( self.myAgent.avatar_name, itemid, amount )
					update_predicate2 = "assert( slot( '%s', %d, %s, %d ) )" % ( self.myAgent.avatar_name, slot, itemid, amount )
					self.myAgent.say( 'Updating knowledge base with: ' + update_predicate1 )
					self.myAgent.say( 'Updating knowledge base with: ' + update_predicate2 )
					self.myAgent.kb.ask( delete_predicate )
					self.myAgent.kb.ask( update_predicate1 )
					self.myAgent.kb.ask( update_predicate2 )
			elif inv is None:
				self.myAgent.say( 'No changes in inventory ...' )
			else:
				self.myAgent.say( 'Inventory not loaded yet ...' )


			self.myAgent.say( 'Updating visible mobs ...' )
			mobs = self.getVisibleMobs()
			# First delete all known locations
			if mobs:
				delete_predicate = "retract( mob_location( _, _, _, _, _ ) )"
				self.myAgent.kb.ask( delete_predicate )
				for mobid, loc in mobs.items():
					mob, mapname, x, y = loc
					update_predicate = "assert( mob_location( %s, '%s', %d, %d, %d ) )" % ( mob, mapname, x, y, mobid )
					self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
					self.myAgent.kb.ask( update_predicate )
			elif mobs is None:
				self.myAgent.say( 'No changes in visible mobs ...' )
			else:
				self.myAgent.say( 'No critters creeping around ...' )


			self.myAgent.say( 'Updating visible NPCs ...' )
			npcs = self.getVisibleNPCs()
			if npcs:
				for npc, loc in npcs.items():
					mapname, x, y, ID = loc
					update_predicate = "assert( npc_location( '%s', '%s', %s, %s ) )" % ( npc, mapname, x, y )
					self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
					self.myAgent.kb.ask( update_predicate )
			elif npcs is None:
				self.myAgent.say( 'No changes in visible NPCs ...' )
			else:
				self.myAgent.say( "There are seemingly no NPCs on this map, or my location hasn't loaded yet ..." )


			self.myAgent.say( 'Updating visible players ...' )
			players = self.getVisiblePlayers()
			if players:
				delete_predicate = "retract( player_location( _, _, _, _ ) )"
				self.myAgent.kb.ask( delete_predicate )
				for p, loc in players.items():
					mapname, x, y = loc
					update_predicate = "assert( player_location( '%s', '%s', %s, %s ) )" % ( p, mapname, x, y )
					self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
					self.myAgent.kb.ask( update_predicate )
			elif players is None:
				self.myAgent.say( 'No changes in visible players ...' )
			else:
				self.myAgent.say( 'No visible players available ...' )


			self.myAgent.say( 'Updating visible items ...' )
			itms = self.getVisibleItems()
			if itms:
				delete_predicate = "retract( item_location( _, _, _, _, _ ) )"
				for item, loc in itms.items():
					amount, mapname, x, y = loc
					update_predicate = "assert( item_location( '%s', %d, '%s', %d, %d ) )" % ( item, amount, mapname, x, y )
					self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
					self.myAgent.kb.ask( update_predicate )
			elif itms is None:
				self.myAgent.say( 'No changes in visible items ...' )
			else:
				self.myAgent.say( 'No items lying around at this location ...' )

			self.myAgent.say( 'Updating NPC conversations ...' )  # not deleting old messages
			try:
				npc_messages = self.getNewNPCMessages()
			except Exception as e:
				print 'ERROR', e
			counter = 1
			try:
				if npc_messages:
					for npc, messages in npc_messages.items():
						for message in messages:
							res = self.interpretNPCMessage( npc, message )
							update, quest, npc = res
							if npc:
								update_predicate = "assert( npc_message( '%s', '%s', '%s' ) )" % ( self.myAgent.avatar_name, npc, message.replace( "'", "\\'" ).replace( "\n", " " ) )
								self.myAgent.kb.ask( update_predicate )
								self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
							if update:
								try:
									if not self.myAgent.kb.ask( update % self.myAgent.avatar_name ) and not self.myAgent.kb.ask( "solved_quest( '%s' )" % quest ): # if I haven't got this quest already and it isn't solved
										update_predicate = 'assert( %s )' % update % self.myAgent.avatar_name
										self.myAgent.kb.ask( update_predicate )
										self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
										sign = self.getQuestSignificance( quest )
										update_predicate = "assert( quest_sign( '%s', '%s', %d ) )" % ( self.myAgent.avatar_name, quest, sign )
										self.myAgent.kb.ask( update_predicate )
										self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
										delete_predicate = "retract( quest_no( '%s', '%s', '%s', _ ) )" % ( npc, self.myAgent.avatar_name, quest )
										self.myAgent.kb.ask( delete_predicate )
										counter += 1
										update_predicate = "assert( quest_no( '%s', '%s', '%s', %d ) )" % ( npc, self.myAgent.avatar_name, quest, counter )
										self.myAgent.kb.ask( update_predicate )
										self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
								except Exception as e:
									print 'ERROR', e
				elif npc_messages == 'None':
					self.myAgent.say( 'No new NPC messages ...' )
				else:
					self.myAgent.say( 'No NPC messages arrived yet ...' )
			except Exception as e:
				print 'ERROR', e


			'''self.myAgent.say( 'Updating my party membership ...' )
			party = self.getPartyMembership()
			if party == -1:
				self.myAgent.say( 'I am no party member ...' )
			elif party == None:
				self.myAgent.say( 'No change in party membership ...' )
			else:
				delete_predicate = "retract( party( '%s', _ ) )" % self.myAgent.avatar_name
				update_predicate = "assert( party( '%s', '%s' ) )" % ( self.myAgent.avatar_name, party )
				self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
				self.myAgent.kb.ask( delete_predicate )
				self.myAgent.kb.ask( update_predicate )'''

			self.myAgent.say( 'Updating my social network ...' )
			soc_net = self.getSocialNetwork()
			if soc_net:
				delete_predicate = "retract( social_network( '%s', _, _ ) )" % self.myAgent.avatar_name
				self.myAgent.kb.ask( delete_predicate )
				for player, tag in soc_net.items():
					update_predicate = "assert( social_network( '%s', '%s', '%s' ) )" % ( self.myAgent.avatar_name, player, tag )
					self.myAgent.say( 'Updating knowledge base with: ' + update_predicate )
					self.myAgent.kb.ask( update_predicate )
			else:
				self.myAgent.say( 'No changes in my social network ...' )
		# Store my knowledgebase
		self.storeKB()

	def updateObjectives( self ):
		''' List all possible objectives ( e.g. unsolved quests ) '''
		try:
			self.myAgent.say( 'My avatar name is ' + self.myAgent.avatar_name )
		except Exception as e:
			print 'ERROR', e
			self.myAgent.say( "My avatar hasn't loaded yet ..." )
			time.sleep( 1 )
			return None
		self.quests = self.myAgent.askBelieve( "waiting_quest( NPC, '%s', Name )." % self.myAgent.avatar_name )
		time.sleep( 3 )
		if self.quests:
			self.myAgent.say( 'My current quests are:' )
			for quest in self.quests:
				try:
					self.myAgent.say( quest[ 'Name' ] + ' given by ' + quest[ 'NPC' ] )
				except:
					pass
			return self.quests
		else:
			self.myAgent.say( 'I have no current quests!' )
			if random() > 0.5:
				return [ {'Name': 'random_walk', 'NPC': 'anonymous'} ]
			else:
				self.myAgent.say( 'Trying to stop talking to some NPC!' )
				query = "assert( waiting_quest( 'common wisdom', '%s', stop_talking ) )" % self.myAgent.avatar_name
				self.myAgent.askBelieve( query )
				return [ {'Name': 'stop_talking', 'NPC': 'common wisdom'} ]

	def addDestinationNPC( self, quest ):
		self.myAgent.destinationNPC = None
		if quest == 'maggots':
			self.myAgent.destinationNPC = ( '029-2', 110, 88 )

	def selectObjective( self, objectives ):
		''' Select most relevant objective ( quest ) to be solved next '''
		query = "sort_quests( '%s' ), quest_no( NPC, '%s', Name, No ), \+ solved_quest( Name )." % ( self.myAgent.avatar_name, self.myAgent.avatar_name )
		quests = self.myAgent.askBelieve( query )
		if quests:
			next = sorted( quests, key=lambda x: x[ 'No' ] )[ 0 ][ 'Name' ]
			self.myAgent.say( 'My next objective is quest: ' + next )
			self.addDestinationNPC( next )
			return next
		time.sleep( 1 )

	def getNextAction( self, quest ):
		''' Derive the next action of the current quest '''
		if quest == 'random_walk':
			return [ 'randomWalk', [] ]
		time.sleep( 1 )
		query = "next_action( _action ), do_action( _action, Action, _params ), member( Param, _params )"
		res = self.myAgent.kb.ask( query )

		if res:
			action = [ 1, [ ] ]
			for r in res:
				action[ 0 ] = r[ 'Action' ]
				action[ 1 ].append( r[ 'Param' ] )
			return action
		else:
			res = self.myAgent.kb.ask( query )
			if res:
				action = [ 1, [ ] ]
				for r in res:
					action[ 0 ] = r[ 'Action' ]
					action[ 1 ].append( r[ 'Param' ] )
				return action
			self.myAgent.say( 'I have no idea how to solve quest "%s" ...' % quest )
			return None

	def planQuest( self, quest ):
		''' Derive a plan and start the quest '''
		if quest == 'random_walk':
			return True
		time.sleep( 1 )
		query = "start_quest( '%s' )"  % quest
		res = self.myAgent.kb.ask( query )
		if res:
			return True  # quest planned and started
		else: 
			return False  # cannot plan or start quest	

	def act( self, action ):
		''' Act out an action '''
		self.myAgent.result = False
		time.sleep( 1 )
		if action[ 0 ] == 'randomWalk':
			b = randomWalk()
			self.myAgent.addBehaviour( b )
			time.sleep( 1 )
		elif action[ 0 ] == 'answerNPC':
			npcID = int( action[ 1 ][ 0 ] )
			answer = int( action[ 1 ][ 1 ] )
			b = AnswerNPC( npcID, answer )
			self.myAgent.addBehaviour( b )
			time.sleep( 1 )
		elif action[ 0 ] == 'stopTalkingToNPC':
			npcID = int( action[ 1 ][ 0 ] )
			b = stopTalkingToNPC( npcID )
			self.myAgent.addBehaviour( b )
			time.sleep( 1 )
		elif action[ 0 ] == 'stopTalkingToNPCSorfina':
			npcID = int( action[ 1 ][ 0 ] )
			b = stopTalkingToNPC( npcID )
			self.myAgent.addBehaviour( b )
			time.sleep( 1 )
		elif action[ 0 ] == 'talkToNPC':
			npcID = int( action[ 1 ][ 0 ] )
			b = talkToNPC( npcID )
			self.myAgent.addBehaviour( b )
			time.sleep( 1 )
		elif action[ 0 ] == 'goToNPC':
			# TODO: implement navigation to other maps when necessary
			npc = action[ 1 ][ 0 ]
			mapID = action[ 1 ][ 1 ]
			x = int( action[ 1 ][ 2 ] )
			y = int( action[ 1 ][ 3 ] )
			b = goToNPC( npc, mapID, x, y )
			self.myAgent.addBehaviour( b )
			time.sleep( 1 )
		elif action[ 0 ] == 'goToLocation' or action[ 0 ] == 'tryToGoToLocation':
			# TODO: implement navigation to other maps when necessary
			mapID = action[ 1 ][ 0 ]
			x = int( action[ 1 ][ 1 ] )
			y = int( action[ 1 ][ 2 ] )
			b = goToLocation( mapID, x, y )
			self.myAgent.addBehaviour( b )
			time.sleep( 1 )
		elif action[ 0 ] == 'equipItem':
			slot = int( action[ 1 ][ 0 ] )
			b = equipItem( slot )
			self.myAgent.addBehaviour( b )
			time.sleep( 1 )
		elif action[ 0 ] == 'killMob':
			mobname = action[ 1 ][ 0 ]
			b = killMob( mobname )
			self.myAgent.addBehaviour( b )
			time.sleep( 1 )
		


	def actionDone( self, action ):
		''' Test if action was successful '''
		if action[ 0 ] == 'randomWalk':
			return True
		elif action[ 0 ] == 'answerNPC':
			return True # there are no visible outcomes of this action
		elif action[ 0 ] == 'stopTalkingToNPC' or action[ 0 ] == 'stopTalkingToNPCSorfina':
			return True # there are no visible outcomes of this action
		elif action[ 0 ] == 'talkToNPC':
			return True # there are no visible outcomes of this action
		elif action[ 0 ] == 'equipItem':
			return True # TODO: Proove this
		elif action[ 0 ] == 'goToLocation':
			time.sleep( 2 )
			self.myAgent.getMyLocation()
			return self.myAgent.location == tuple( action[ 1 ] ) # returns True if the agent has arrived
		elif action[ 0 ] == 'tryToGoToLocation':
			time.sleep( 1 )
			return True # This is just a try to get the next NPC message
		elif action[ 0 ] == 'goToNPC':
			time.sleep( 2 )
			self.myAgent.getMyLocation()
			self.myAgent.say( 'My location ' + str( self.myAgent.location ) )
			self.myAgent.say( 'My destination ' + str( tuple( action[ 1 ][ 1: ] ) ) )
			return self.myAgent.location == tuple( action[ 1 ][ 1: ] ) # returns True if the agent has arrived
		if action[ 0 ] == 'killMob':
			time.sleep( 5 ) # TODO: Proove this
			return True
		return False # Unknown action

	def actionFailed( self ):
		''' Tell the knowledge base that an action was unsuccessful '''
		query = 'action_failed'
		self.myAgent.kb.ask( query )

	def planDone( self, quest ):
		''' Test if a quest has been finished '''
		if quest == 'random_walk':
			return True
		query = "solved_quest( '%s' ), X = 1" % quest # Little hack to test SWI's state of mind ...
		time.sleep( 1 )
		result = self.myAgent.kb.ask( query )
		try:
			if result[ 'X' ] == 1:
				return True
		except:
			return False

	def reconsider( self ):
		''' Is it time to reconsider my plans? '''
		probability = 0.8  # for now 20%
		reconsider = random() > probability
		return reconsider

	def _process( self ):
		while not self.myAgent.login_complete:
			self.myAgent.login()
			self.myAgent.loggedin = False
			while not self.myAgent.loggedin:
				try:
					self.myAgent.quit()
				except:
					pass
				self.myAgent.loggedin = self.myAgent.login()
			time.sleep( 1 )
			self.myAgent.pb.go()
			counter = 0
			while not self.myAgent.pb.hasNew():
				time.sleep( 0.1 )
				counter += 1
				if counter > 10:
					break

			if counter >= 10:
				continue

			try:
				self.myAgent.locatePlayer()
			except:
				continue

			time.sleep( 1 )

			if not self.myAgent.pb.playerMap:
				continue

			self.myAgent.login_complete = True

		self.myAgent.say( 'Updating my knowledge base ...' )
		self.updateKB()

		self.myAgent.say( 'Updating my objectives ...' )
		obj = self.updateObjectives()
		self.myAgent.say( 'Selecting an objective ...' )
		if obj and obj[ 0 ][ 'Name' ] != 'random_walk':
			next = self.selectObjective( obj )
		else:
			next = 'random_walk'
		if next == 'None' or not next:
			next = 'random_walk'
		self.myAgent.say( 'Planning quest "%s" ...' % next )
		start = self.planQuest( next )
		if not start:
			self.myAgent.say( 'Cannot plan or start quest ...' )
			return
		planDone = False
		while not planDone:
			nextAction = self.getNextAction( next )
			if not nextAction:
				self.myAgent.say( "My plan didn't work out. I'll try something else." )
				break
			self.myAgent.say( 'My next action is "%s( %s )"' % ( nextAction[ 0 ], ','.join( nextAction[ 1 ] ) ) )
			self.act( nextAction )
			counter = 0
			self.myAgent.say( 'I made my move, let us see if this worked ...' )

			# wait until the action is run through
			while self.myAgent.result is False:
				time.sleep( 0.1 )
				counter += 1
				if counter > 1000:
					self.myAgent.say( "An ERROR must have occured when running the behaviour!" )
					break

			if not self.myAgent.result:
				self.myAgent.say( 'Action failed miserably, need to rethink my options ...' )
				break

			retries = 3
			success = self.actionDone( nextAction )
			self.myAgent.say( "Updating my knowledge base ..." )
			self.updateKB()
			# wait until the action is run successfully
			# ( usually a result is obtainable )
			while not success or retries == 0:
				time.sleep( 1 )
				self.myAgent.say( "Updating my knowledge base ..." )
				self.updateKB()
				self.myAgent.say( "Testing if action was successful ..." )
				try:
					success = self.actionDone( nextAction )
				except Exception, e:
					print "ERROR:", e
				retries -= 1

			if not success:
				self.myAgent.say( 'The action was unsuccessful, need to rethink my options ...' )
				self.actionFailed()
				break # action has been unsuccessful

			self.myAgent.say( 'The action was successfull!' )

			try:
				planDone = self.planDone( next )
			except Exception as e:
				print 'ERROR: ', e

			if planDone:
				self.myAgent.say( 'I finished quest "%s"! Going for the next one ...' % next )
				break


			if self.reconsider():
				self.myAgent.say( 'It seems to be time to reconsider my options ...' )
				self.myAgent.say( 'Updating my knowledge base ...' )
				self.updateKB()
				self.myAgent.say( 'Updating my objectives ...' )
				self.myAgent.say( 'woah!' )
				try:
					obj = self.updateObjectives()
				except Exception as e:
					print 'ERROR', e
				self.myAgent.say( 'Selecting an objective ...' )
				if obj and obj[ 0 ][ 'Name' ] != 'random_walk':
					newnext = self.selectObjective( obj )
				else:
					newnext = 'random_walk'
				if newnext != next:
					self.myAgent.say( 'Planning quest "%s" ...' % next )
					start = self.planQuest( next )
					if not start:
						self.myAgent.say( 'Cannot plan or start quest ...' )
						return
