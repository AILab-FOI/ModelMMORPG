#!/usr/bin/env python
#-*- coding: utf-8 -*-

import socket
import struct
import time
import threading
import sys
import re
import select
import os
	

findp_re = re.compile( r'Name: ([^\(]+) .* ?\| Location: ([0-9]+[-][0-9]+) ([0-9]+) ([0-9]+)' )
findpp_re = re.compile( r"Name: ([^\(]+) .* ?\| Party: [\'](.*)[\']" )

DEBUG = True
CHARACTER = None

def debug( *msg ):
	msg = [ str( i ) for i in msg ]
	msg = ' '.join( msg )
	if( DEBUG ):
		if CHARACTER:
			print CHARACTER + ': ' + str( msg )
		else:
			print msg

'''Dictionary holds HEX codes of packets as keys with packet length 
and packet name as values in a tuple.'''
PACKETS = {
0x0061 : (50, 'CMSG_CHAR_PASSWORD_CHANGE' ), 
0x0062 : (3, 'SMSG_CHAR_PASSWORD_RESPONSE' ), 
0x0063 : (-1, 'SMSG_UPDATE_HOST' ), 
0x0064 : (55, '(hard-coded) 1' ), 
0x0065 : (17, 'CMSG_CHAR_SERVER_CONNECT' ), 
0x0066 : (3, 'CMSG_CHAR_SELECT' ), 
0x0067 : (37, 'CMSG_CHAR_CREATE' ), 
0x0068 : (46, 'CMSG_CHAR_DELETE' ), 
0x0069 : (-1, 'SMSG_LOGIN_DATA' ), 
0x006A : (23, 'SMSG_LOGIN_ERROR' ), 
0x006B : (-1, 'SMSG_CHAR_LOGIN' ), 
0x006C : (3, 'SMSG_CHAR_LOGIN_ERROR' ), 
0x006D : (108, 'SMSG_CHAR_CREATE_SUCCEEDED' ), 
0x006E : (3, 'SMSG_CHAR_CREATE_FAILED' ), 
0x006F : (2, 'SMSG_CHAR_DELETE_SUCCEEDED' ), 
0x0070 : (3, 'SMSG_CHAR_DELETE_FAILED' ), 
0x0071 : (28, 'SMSG_CHAR_MAP_INFO' ), 
0x0072 : (19, 'CMSG_MAP_SERVER_CONNECT' ), 
0x0073 : (11, 'SMSG_MAP_LOGIN_SUCCESS' ), 
0x0078 : (54, 'SMSG_BEING_VISIBLE' ), 
0x007B : (60, 'SMSG_BEING_MOVE' ), 
0x007C : (41, 'SMSG_BEING_SPAWN' ), 
0x007D : (2, 'CMSG_MAP_LOADED' ), 
0x007E : (6, 'CMSG_CLIENT_PING' ), 
0x007F : (6, 'SMSG_SERVER_PING' ), 
0x0080 : (7, 'SMSG_BEING_REMOVE' ), 
0x0081 : (4, 'SMSG_CONNECTION_PROBLEM' ), 
0x0085 : (5, 'CMSG_PLAYER_CHANGE_DEST' ), 
0x0086 : (16, 'SMSG_BEING_MOVE2' ), 
0x0087 : (12, 'SMSG_WALK_RESPONSE' ), 
0x0088 : (10, 'SMSG_PLAYER_STOP' ), 
0x0089 : (7, 'CMSG_PLAYER_CHANGE_ACT/CMSG_PLAYER_ATTACK' ), 
0x008A : (29, 'SMSG_BEING_ACTION' ), 
0x008C : (-1, 'CMSG_CHAT_MESSAGE' ), 
0x008D : (-1, 'SMSG_BEING_CHAT' ), 
0x008E : (-1, 'SMSG_PLAYER_CHAT' ), 
0x0090 : (7, 'CMSG_NPC_TALK' ), 
0x0091 : (22, 'SMSG_PLAYER_WARP' ), 
0x0092 : (28, 'SMSG_CHANGE_MAP_SERVER' ), 
0x0094 : (6, '(hard-coded) 2' ), 
0x0095 : (30, 'SMSG_BEING_NAME_RESPONSE' ), 
0x0096 : (-1, 'CMSG_CHAT_WHISPER' ), 
0x0097 : (-1, 'SMSG_WHISPER' ), 
0x0098 : (3, 'SMSG_WHISPER_RESPONSE' ), 
0x0099 : (-1, 'CMSG_ADMIN_ANNOUNCE/CMSG_CHAT_ANNOUNCE' ), 
0x009A : (-1, 'SMSG_GM_CHAT' ), 
0x009B : (5, 'CMSG_PLAYER_CHANGE_DIR' ), 
0x009C : (9, 'SMSG_BEING_CHANGE_DIRECTION' ), 
0x009D : (17, 'SMSG_ITEM_VISIBLE' ), 
0x009E : (17, 'SMSG_ITEM_DROPPED' ), 
0x009F : (6, 'CMSG_ITEM_PICKUP' ), 
0x00A0 : (23, 'SMSG_PLAYER_INVENTORY_ADD' ), 
0x00A1 : (6, 'SMSG_ITEM_REMOVE' ), 
0x00A2 : (6, 'CMSG_PLAYER_INVENTORY_DROP' ), 
0x00A4 : (-1, 'SMSG_PLAYER_EQUIPMENT' ), 
0x00A6 : (-1, 'SMSG_PLAYER_STORAGE_EQUIP' ), 
0x00A7 : (8, 'CMSG_PLAYER_INVENTORY_USE' ), 
0x00A8 : (7, 'SMSG_ITEM_USE_RESPONSE' ), 
0x00A9 : (6, 'CMSG_PLAYER_EQUIP' ), 
0x00AA : (7, 'SMSG_PLAYER_EQUIP' ), 
0x00AB : (4, 'CMSG_PLAYER_UNEQUIP' ), 
0x00AC : (7, 'SMSG_PLAYER_UNEQUIP' ), 
0x00AF : (6, 'SMSG_PLAYER_INVENTORY_REMOVE' ), 
0x00B0 : (8, 'SMSG_PLAYER_STAT_UPDATE_1' ), 
0x00B1 : (8, 'SMSG_PLAYER_STAT_UPDATE_2' ), 
0x00B2 : (3, 'CMSG_PLAYER_RESTART' ), 
0x00B3 : (3, 'SMSG_CHAR_SWITCH_RESPONSE' ), 
0x00B4 : (-1, 'SMSG_NPC_MESSAGE' ), 
0x00B5 : (6, 'SMSG_NPC_NEXT' ), 
0x00B6 : (6, 'SMSG_NPC_CLOSE' ), 
0x00B7 : (-1, 'SMSG_NPC_CHOICE' ), 
0x00B8 : (7, 'CMSG_NPC_LIST_CHOICE' ), 
0x00B9 : (6, 'CMSG_NPC_NEXT_REQUEST' ), 
0x00BB : (5, 'CMSG_STAT_UPDATE_REQUEST' ), 
0x00BC : (6, 'SMSG_PLAYER_STAT_UPDATE_4' ), 
0x00BD : (44, 'SMSG_PLAYER_STAT_UPDATE_5' ), 
0x00BE : (5, 'SMSG_PLAYER_STAT_UPDATE_6' ), 
0x00BF : (3, 'CMSG_PLAYER_EMOTE' ), 
0x00C0 : (7, 'SMSG_BEING_EMOTION' ), 
0x00C1 : (2, 'CMSG_WHO_REQUEST/CMSG_CHAT_WHO' ), 
0x00C2 : (6, 'SMSG_WHO_ANSWER' ), 
0x00C3 : (8, 'SMSG_BEING_CHANGE_LOOKS' ), 
0x00C4 : (6, 'SMSG_NPC_BUY_SELL_CHOICE' ), 
0x00C5 : (7, 'CMSG_NPC_BUY_SELL_REQUEST' ), 
0x00C6 : (-1, 'SMSG_NPC_BUY' ), 
0x00C7 : (-1, 'SMSG_NPC_SELL' ), 
0x00C8 : (-1, 'CMSG_NPC_BUY_REQUEST' ), 
0x00C9 : (-1, 'CMSG_NPC_SELL_REQUEST' ), 
0x00CA : (3, 'SMSG_NPC_BUY_RESPONSE' ), 
0x00CB : (3, 'SMSG_NPC_SELL_RESPONSE' ), 
0x00CC : (6, 'CMSG_ADMIN_KICK' ), 
0x00CD : (6, 'SMSG_ADMIN_KICK_ACK' ), 
0x00E4 : (6, 'CMSG_TRADE_REQUEST' ), 
0x00E5 : (26, 'SMSG_TRADE_REQUEST' ), 
0x00E6 : (3, 'CMSG_TRADE_RESPONSE' ), 
0x00E7 : (3, 'SMSG_TRADE_RESPONSE' ), 
0x00E8 : (8, 'CMSG_TRADE_ITEM_ADD_REQUEST' ), 
0x00E9 : (19, 'SMSG_TRADE_ITEM_ADD' ), 
0x00EB : (2, 'CMSG_TRADE_ADD_COMPLETE' ), 
0x00EC : (3, 'SMSG_TRADE_OK' ), 
0x00ED : (2, 'CMSG_TRADE_CANCEL_REQUEST' ), 
0x00EE : (2, 'SMSG_TRADE_CANCEL' ), 
0x00EF : (2, 'CMSG_TRADE_OK' ), 
0x00F0 : (3, 'SMSG_TRADE_COMPLETE' ), 
0x00F2 : (6, 'SMSG_PLAYER_STORAGE_STATUS' ), 
0x00F3 : (8, 'CMSG_MOVE_TO_STORAGE' ), 
0x00F4 : (21, 'SMSG_PLAYER_STORAGE_ADD' ), 
0x00F5 : (8, 'CSMG_MOVE_FROM_STORAGE' ), 
0x00F6 : (8, 'SMSG_PLAYER_STORAGE_REMOVE' ), 
0x00F7 : (2, 'CMSG_CLOSE_STORAGE' ), 
0x00F8 : (2, 'SMSG_PLAYER_STORAGE_CLOSE' ), 
0x00F9 : (26, 'CMSG_PARTY_CREATE' ), 
0x00FA : (3, 'SMSG_PARTY_CREATE' ), 
0x00FB : (-1, 'SMSG_PARTY_INFO' ), 
0x00FC : (6, 'CMSG_PARTY_INVITE' ), 
0x00FD : (27, 'SMSG_PARTY_INVITE_RESPONSE' ), 
0x00FE : (30, 'SMSG_PARTY_INVITED' ), 
0x00FF : (10, 'CMSG_PARTY_INVITED' ), 
0x0100 : (2, 'CMSG_PARTY_LEAVE' ), 
0x0101 : (6, 'SMSG_PARTY_SETTINGS' ), 
0x0102 : (6, 'CMSG_PARTY_SETTINGS' ), 
0x0103 : (30, 'CMSG_PARTY_KICK' ), 
0x0104 : (79, 'SMSG_PARTY_MOVE' ), 
0x0105 : (31, 'SMSG_PARTY_LEAVE' ), 
0x0106 : (10, 'SMSG_PARTY_UPDATE_HP' ), 
0x0107 : (10, 'SMSG_PARTY_UPDATE_COORDS' ), 
0x0108 : (-1, 'CMSG_PARTY_MESSAGE' ), 
0x0109 : (-1, 'SMSG_PARTY_MESSAGE' ), 
0x010C : (6, 'SMSG_MVP' ), 
0x010E : (11, 'SMSG_PLAYER_SKILL_UP/SMSG_GUILD_SKILL_UP' ), 
0x010F : (-1, 'SMSG_PLAYER_SKILLS' ), 
0x0110 : (10, 'SMSG_SKILL_FAILED' ), 
0x0112 : (4, 'CMSG_SKILL_LEVELUP_REQUEST' ), 
0x0113 : (10, 'CMSG_SKILL_USE_BEING' ), 
0x0116 : (10, 'CMSG_SKILL_USE_POSITION' ), 
0x0119 : (13, 'SMSG_PLAYER_STATUS_CHANGE' ), 
0x011B : (20, 'CMSG_SKILL_USE_MAP' ), 
0x0139 : (16, 'SMSG_PLAYER_MOVE_TO_ATTACK' ), 
0x013A : (4, 'SMSG_PLAYER_ATTACK_RANGE' ), 
0x013B : (4, 'SMSG_PLAYER_ARROW_MESSAGE' ), 
0x013C : (4, 'SMSG_PLAYER_ARROW_EQUIP' ), 
0x0141 : (14, 'SMSG_PLAYER_STAT_UPDATE_3' ), 
0x0142 : (6, 'SMSG_NPC_INT_INPUT' ), 
0x0143 : (10, 'CMSG_NPC_INT_RESPONSE' ), 
0x0146 : (6, 'CMSG_NPC_CLOSE' ), 
0x0148 : (8, 'SMSG_BEING_RESURRECT' ), 
0x0149 : (9, 'CMSG_ADMIN_MUTE' ), 
0x014C : (-1, 'SMSG_GUILD_ALIANCE_INFO' ), 
0x014D : (2, 'CMSG_GUILD_CHECK_MASTER' ), 
0x014E : (6, 'SMSG_GUILD_MASTER_OR_MEMBER' ), 
0x014F : (6, 'CMSG_GUILD_REQUEST_INFO' ), 
0x0151 : (6, 'CMSG_GUILD_REQUEST_EMBLEM' ), 
0x0152 : (-1, 'SMSG_GUILD_EMBLEM' ), 
0x0153 : (-1, 'CMSG_GUILD_CHANGE_EMBLEM' ), 
0x0154 : (-1, 'SMSG_GUILD_MEMBER_LIST' ), 
0x0155 : (-1, 'CMSG_GUILD_CHANGE_MEMBER_POS' ), 
0x0156 : (-1, 'SMSG_GUILD_MEMBER_POS_CHANGE' ), 
0x0159 : (54, 'CMSG_GUILD_LEAVE' ), 
0x015A : (66, 'SMSG_GUILD_LEAVE' ), 
0x015B : (54, 'CMSG_GUILD_EXPULSION' ), 
0x015C : (90, 'SMSG_GUILD_EXPULSION' ), 
0x015D : (42, 'CMSG_GUILD_BREAK' ), 
0x015E : (6, 'SMSG_GUILD_BROKEN' ), 
0x0160 : (-1, 'SMSG_GUILD_POS_INFO_LIST' ), 
0x0161 : (-1, 'CMSG_GUILD_CHANGE_POS_INFO' ), 
0x0162 : (-1, 'SMSG_GUILD_SKILL_INFO' ), 
0x0163 : (-1, 'SMSG_GUILD_EXPULSION_LIST' ), 
0x0165 : (30, 'CMSG_GUILD_CREATE' ), 
0x0166 : (-1, 'SMSG_GUILD_POS_NAME_LIST' ), 
0x0167 : (3, 'SMSG_GUILD_CREATE_RESPONSE' ), 
0x0168 : (14, 'CMSG_GUILD_INVITE' ), 
0x0169 : (3, 'SMSG_GUILD_INVITE_ACK' ), 
0x016A : (30, 'SMSG_GUILD_INVITE' ), 
0x016B : (10, 'CMSG_GUILD_INVITE_REPLY' ), 
0x016C : (43, 'SMSG_GUILD_POSITION_INFO' ), 
0x016D : (14, 'SMSG_GUILD_MEMBER_LOGIN' ), 
0x016E : (186, 'CMSG_GUILD_CHANGE_NOTICE' ), 
0x016F : (182, 'SMSG_GUILD_NOTICE' ), 
0x0170 : (14, 'CMSG_GUILD_ALLIANCE_REQUEST' ), 
0x0171 : (30, 'SMSG_GUILD_REQ_ALLIANCE' ), 
0x0172 : (10, 'CMSG_GUILD_ALLIANCE_REPLY' ), 
0x0173 : (3, 'SMSG_GUILD_REQ_ALLIANCE_ACK' ), 
0x0174 : (-1, 'SMSG_GUILD_POSITION_CHANGED' ), 
0x017E : (-1, 'CMSG_GUILD_MESSAGE' ), 
0x017F : (-1, 'SMSG_GUILD_MESSAGE' ), 
0x0180 : (6, 'CMSG_GUILD_OPPOSITION' ), 
0x0181 : (3, 'SMSG_GUILD_OPPOSITION_ACK' ), 
0x0183 : (10, 'CMSG_GUILD_ALLIANCE_DELETE' ), 
0x0184 : (10, 'SMSG_GUILD_DEL_ALLIANCE' ), 
0x018A : (4, 'CMSG_CLIENT_QUIT' ), 
0x018B : (4, 'SMSG_MAP_QUIT_RESPONSE' ), 
0x0190 : (90, 'CMSG_SKILL_USE_POSITION_MORE' ), 
0x0195 : (102, 'SMSG_PLAYER_GUILD_PARTY_INFO' ), 
0x0196 : (9, 'SMSG_BEING_STATUS_CHANGE' ), 
0x019B : (10, 'SMSG_BEING_SELFEFFECT' ), 
0x019C : (4, 'CMSG_ADMIN_LOCAL_ANNOUNCE' ), 
0x019D : (6, 'CMSG_ADMIN_HIDE' ), 
0x01B1 : (7, 'SMSG_TRADE_ITEM_ADD_RESPONSE' ), 
0x01B6 : (114, 'SMSG_GUILD_BASIC_INFO' ), 
0x01C8 : (13, 'SMSG_PLAYER_INVENTORY_USE' ), 
0x01D4 : (6, 'SMSG_NPC_STR_INPUT' ), 
0x01D5 : (8, 'CMSG_NPC_STR_RESPONSE' ), 
0x01D7 : (11, 'SMSG_BEING_CHANGE_LOOKS2' ), 
0x01D8 : (54, 'SMSG_PLAYER_UPDATE_1' ), 
0x01D9 : (53, 'SMSG_PLAYER_UPDATE_2' ), 
0x01DA : (60, 'SMSG_PLAYER_MOVE' ), 
0x01DE : (33, 'SMSG_SKILL_DAMAGE' ), 
0x01EE : (-1, 'SMSG_PLAYER_INVENTORY' ), 
0x01F0 : (-1, 'SMSG_PLAYER_STORAGE_ITEMS' ), 
0x020C : (10, 'SMSG_ADMIN_IP' ), 
0x7530 : (2, 'CMSG_SERVER_VERSION_REQUEST' ), 
0x7531 : (10, 'SMSG_SERVER_VERSION_RESPONSE' ),
0x8000 : (4, 'UNKNOWN') # I have no idea where this packet comes from, nor what it does
}

class Character:
	'''Class to hold all relevant data of a TWM character'''
	def __init__( self, char_id=None, exp=None, zeny=None, job_xp=None, job_level=None, shoes=None, gloves=None, cape=None, misc1=None, option=None, karma=None, manner=None, status_point=None, hp=None, max_hp=None, sp=None, max_sp=None, speed=150, species=None, hair=None, weapon=0, level=None, skill_points=None, head_bottom_legs=None, shield=None, head_top_helmet=None, head_middle_torso=None, hair_color=None, misc2=None, name=None, str=None, agi=None, vit=None, int=None, dex=None, luk=None, char_num=None ):
		self.char_id = char_id, 
		self.exp = exp, 
		self.zeny = zeny, 
		self.job_xp = job_xp, 
		self.job_level = job_level, 
		self.shoes = shoes, 
		self.gloves = gloves, 
		self.cape = cape, 
		self.misc1 = misc1, 
		self.option = option, 
		self.karma = karma, 
		self.manner = manner, 
		self.status_point = status_point, 
		self.hp = hp, 
		self.max_hp = max_hp, 
		self.sp = sp, 
		self.max_sp = max_sp, 
		self.speed = speed, 
		self.species = species, 
		self.hair = hair, 
		self.weapon = weapon, 
		self.level = level, 
		self.skill_points = skill_points, 
		self.head_bottom_legs = head_bottom_legs, 
		self.shield = shield, 
		self.head_top_helmet = head_top_helmet, 
		self.head_middle_torso = head_middle_torso, 
		self.hair_color = hair_color, 
		self.misc2 = misc2, 
		self.name = name, 
		self.str = str, 
		self.agi = agi, 
		self.vit = vit, 
		self.int = int, 
		self.dex = dex, 
		self.luk = luk, 
		self.char_num = char_num

class PacketBuffer( threading.Thread ):
	
		
	
	'''Thread to deal with incomming packets from a given socket server'''
	def __init__( self, server ):
		'''Initialize server handle and packet-list to hold packets (initially empty)'''
		threading.Thread.__init__( self ) 
		self.srv = server
		self.packets = []
		self.stahp = False
		self.buffer = None
		self.kill = False
		
		self.playerInventory = {}
		
		self.playerMap = None
		self.playerPosX = None
		self.playerPosY = None
		
		self.droppedItems = {}
		
		self.monsterMovements = {}
		
		self.talkingToNPC = None
		
		self.detectedNPClist = []
		
		self.loggedInPlayers = {}
		
		self.gameParties = {}
		
		self.npcMessages = []

		self.playerParty = {}
		

	def updatePlayerData (self, slots):
		self.playerSlots = slots
		
	
	
	def run( self ):
		'''Main thread (receive a packet, create a Packet instance and append it to packet list'''
		global Packet
		while True:
			buff = self.recv()
			if buff:
				packet = Packet( buff )
				
				# INVENTORY: 
				self.playerInventory = Packet.playerSlots
				
				# POSITION:
				self.playerMap = Packet.mapID
				self.playerPosX = Packet.chatCoordinates_x
				self.playerPosY = Packet.chatCoordinates_y
				
				# DROPPED ITEMS ON THE MAP
				self.droppedItems = Packet.droppedItemDict
				
				# MONSTER MOVEMENTS (id, x, y)
				self.monsterMovements = Packet.critterMovements
				
				# Player is talking to NPC with name:
				self.talkingToNPC = Packet.talkingWithNPC
				
				# List all logged in players
				self.loggedInPlayers = Packet.loggedInPlayers
				
				# In-game current parties
				self.gameParties = Packet.parties
				
				# Message from NPC
				self.npcMessages = Packet.npcIncomingMessage

				# Party memberships
				self.playerParty = Packet.playerParty
				
				#debug (self.playerMap, self.playerPosX, self.playerPosY)
				#debug ("\n\npacket created\n\n")
				#debug (self.droppedItems)
				#debug (self.monsterMovements)
				#debug (self.talkingToNPC)
				#debug (self.loggedInPlayers)
				#debug (self.gameParties)
				#debug (self.npcMessages)
								
				self.packets.append( packet )
				#debug( "\n\n" )
				#debug( self.packets )
			
			if self.kill:
				return
			
	def recv( self ):
		'''Method to receive an individual packet'''
		buff = ''
		old = ''
		data = None
		self.buffer, data = data, self.buffer
		while not self.stahp:
			try: 
				data = self.srv.recv( 4096, socket.MSG_DONTWAIT )
							
			except:
				time.sleep( 0.1 )
			if old == data:
				break
			if data:
				try:
					'''Get the packets length based on the code and split the data'''
					if data[ 0 ] != '\x81' and data[ 1 ] != '\x00': 
						'''The code is in the first two bytes''' 
						code = struct.unpack( "<H", data[ 0:2 ] )[ 0 ]						
						#debug( "\n\n"	#DEBUG )
						#debug( code		#DEBUG )
						
					else:
						'''But sometimes also in only the first byte'''
						code = ord( data[ 0 ] )
						#debug( "\n\n"	#DEBUG )
						#debug( code		#DEBUG )
					
					length = PACKETS[ code ][ 0 ]
					
					'''If the length is -1 the length is encoded in the 3rd and 4th byte'''
					if length == -1:
						length = struct.unpack( '<H', data[ 2:4 ] )[ 0 ]
					#debug( length, PACKETS[ code ][ 1 ], '\n', Packet( data[ :length ] ) )
					if len( data ) >= length:
						self.buffer = data[ length: ]
						return data[ :length ]
				except:
					pass
				buff += data
				old = data
		return buff

	def hasNew( self, typ=None ):  
		'''If there have been unseen packets (possibly of certain type) return 
		True, else False. Typ can be a string type name or a tuple of such.'''
		if typ:
			if type( typ ) == str:
				typ = ( typ, )
			if [ i for i in self.packets if not i.seen and i.type in typ ]:
				return True
		elif [ i for i in self.packets if not i.seen ]:
			return True
		return False	

	def stop( self ):
		'''Stop reading packets'''
		self.stahp = True
		self.buffer = None

	def go( self ):
		'''Resume reading packets'''
		self.stahp = False

	def getNew( self, typ=None, timeout=10 ):
		''' Get new packet '''
		if typ:
			if type( typ ) == str:
				typ = ( typ, )
			while not self.hasNew( typ ):
				time.sleep( 0.1 )
				timeout -= 0.1
				if timeout <= 0:
					return None
			ret = [ i for i in self.packets if i.type in typ and not i.seen ][ 0 ]
		else:
			ret = [ i for i in self.packets if not i.seen ][ 0 ]
		ret.seen = True
		return ret
		
class Item:
  def __init__( self, itemID, itemAmount ):
    self.itemID = itemID
    self.itemAmount = itemAmount
    
		
		
		
		
		
class Packet:
	
	'''Class to hold data about a given packet'''

	droppedItemObjectID = None
	droppedItemID = None
	droppedItem_x = None
	droppedItem_y = None
	droppedItemAmount = None
	droppedItemDict = {}
	
	chatCoordinates = None
	chatCoordinates_x = None
	chatCoordinates_y = None
	mapID = None
	
	playerMovesTo_ID = None
	playerMovesTo_x = None
	playerMovesTo_y = None
	
	critterMovesTo_ID = None
	critterMovesTo_x = None
	critterMovesTo_y = None
	
	critterMovements = {}
	
	playerInventory = {}
	playerEquipment = {}
	
	playerSlots = {}
	
	talkingWithNPC = None
	
	npcDetectedName  = []
	
	loggedInPlayers = {}
	
	parties = {}
	
	npcIncomingMessage = []
	
	whoInvites = None

	playerParty = {}
	
	
	
	def __init__( self, data=None ):
		
		self.droppedItemDict = {}
		
		self.data = data
		if self.data:
			try:
				if self.data[ 0 ] != '\x81' and self.data[ 1 ] != '\x00':
					code = struct.unpack( "<H", self.data[ 0:2 ] )[ 0 ]
				else:
					code = ord( self.data[ 0 ] )
				self.size, self.type = PACKETS[ code ]
			except:
				self.type = ord( self.data[ 0 ] )
				self.size = -1
			self.interpret()
		else:
			self.size, self.type = None, None
		self.seen = False

	def __str__( self ):
		'''debug( a packet in hexadecimal notation (for debug only)'''
		if not self.data:
			raise ValueError, 'Empty packet!'
		ret = ''
		for i, j in enumerate( self.data ):
			ret += '%d %s\n' % ( i, hex( ord( j ) ) )
		return ret



	def interpret( self ):
		'''Parse the packet and assign adequate attributes to the object depending 
		on the packet type'''
		
		
		
		if self.type == 'SMSG_LOGIN_DATA':
			'''
			SMSG_LOGIN_DATA
			Sent in response to Login Request. This packet is sent to the client by the server to define the character sex,
			the account and session IDs, as well as provide a list of worlds the player can connect to.
			Upon receiving this packet, the client shall:
			1) Disconnect from the login server
			2) Connect to the user-specified character server
			3) Immediately send Character Server Connection Request.
			'''
			
			self.id1, self.accid, self.id2 = struct.unpack( "<LLL", self.data[ 4: 16 ] )			
			self.sex = ord( self.data[ 46 ] )
			buff = self.data[ 47: ]
			self.charip = self._parse_ip( buff[ :4 ] )
			self.charport = struct.unpack( "<H", buff[ 4:6 ] )[ 0 ]
		
		elif self.type == 'SMSG_CHAR_LOGIN':
			'''
			SMSG_CHAR_LOGIN
			Sent in response to Character Server Connection Request, either directly or via Net:0x2713.
			Upon receiving this packet, the client is able to select a character to play with, 
			create a character in a new slot, or deleted an existing character.
			'''			
			
			'''size of packet preamble is 28 and 106 of each character information. 
			The name is on 74'''
			
			buff = self.data[ 24: ]
			self.charlist = []
			self.characters = {}
			while buff:
				c = Character()
				c.char_id = struct.unpack( "<L", buff[ :4 ] )[ 0 ]
				#~ debug("\n\n\n")
				#~ debug(c.char_id)
				buff = buff[ 4: ]
				c.exp = struct.unpack( "<L", buff[ :4 ] )[ 0 ]
				buff = buff[ 4: ]
				c.zeny = struct.unpack( "<L", buff[ :4 ] )[ 0 ]
				buff = buff[ 4: ]
				c.job_xp = struct.unpack( "<L", buff[ :4 ] )[ 0 ]
				buff = buff[ 4: ]
				c.job_level = struct.unpack( "<L", buff[ :4 ] )[ 0 ]
				buff = buff[ 4: ]
				c.shoes = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.gloves = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.cape = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.misc1 = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.option = struct.unpack( "<L", buff[ :4 ] )[ 0 ]
				buff = buff[ 4: ]
				c.karma = struct.unpack( "<L", buff[ :4 ] )[ 0 ]
				buff = buff[ 4: ]
				c.manner = struct.unpack( "<L", buff[ :4 ] )[ 0 ]
				buff = buff[ 4: ]
				c.status_point = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.hp = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.max_hp = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.sp = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.max_sp = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.speed = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.species = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.hair = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.weapon = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.level = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.skill_points = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.head_bottom_legs = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.shield = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.head_top_helmet = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.head_middle_torso = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.hair_color = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.misc2 = struct.unpack( "<h", buff[ :2 ] )[ 0 ]
				buff = buff[ 2: ]
				c.name = buff.split( '\0' )[ 0 ]
				buff = buff[ 24: ]
				c.str = struct.unpack( "<B", buff[ :1 ] )[ 0 ]
				buff = buff[ 1: ]
				c.agi = struct.unpack( "<B", buff[ :1 ] )[ 0 ]
				buff = buff[ 1: ]
				c.vit = struct.unpack( "<B", buff[ :1 ] )[ 0 ]
				buff = buff[ 1: ]
				c.int = struct.unpack( "<B", buff[ :1 ] )[ 0 ]
				buff = buff[ 1: ]
				c.dex = struct.unpack( "<B", buff[ :1 ] )[ 0 ]
				buff = buff[ 1: ]
				c.luk = struct.unpack( "<B", buff[ :1 ] )[ 0 ]
				buff = buff[ 1: ]
				c.char_num = struct.unpack( "<B", buff[ :1 ] )[ 0 ]
				buff = buff[ 2: ]
				self.charlist.append( c )
				self.characters[ c.name ] = c
				
				# debug ("CHARACTER ID: %d" %c.char_id ) # NOT THE SAME ID as in-game ID ?
		
		
		elif self.type == 'SMSG_CHAR_MAP_INFO':
			self.charid = struct.unpack( "<L", self.data[ 2:6 ] )[ 0 ]
			self.mapip = self._parse_ip( self.data[ 22:26 ] )
			self.mapport = struct.unpack( "<H", self.data[ 26:28 ] )[ 0 ]
		
		
		elif self.type == 'SMSG_UPDATE_HOST':
			#raise UpdateError, 'Server requests client update!\nComment out update_host: (...) in ./tmwa-server-data/login/conf/local_login.conf'
			pass
		
		#elif self.type == 'SMSG_NPC_MESSAGE':
			#self.message = self.data[ 8:-1 ]
			#self.NPCid =  struct.unpack( "<L", self.data[ 4:8 ] )[ 0 ]
		
		#elif self.type == 'SMSG_NPC_CHOICE':
			#self.message = self.data[ 8:-1 ]
			#self.choices = self.message.split( ':' )[ :-1 ]
			#self.NPCid =  struct.unpack( "<L", self.data[ 4:8 ] )[ 0 ]
		
		
		elif self.type == 'SMSG_PLAYER_WARP':
			self.map = self.data.split( '\0' )[ 1 ]
			self.x = struct.unpack( "<B", self.data[ 18 ] )[ 0 ]
			self.y = struct.unpack( "<B", self.data[ 20 ] )[ 0 ]
		
		
		
		elif self.type == 'SMSG_ITEM_DROPPED':
			
			Packet.droppedItemObjectID = struct.unpack ("<L", self.data[2:6])[0]
			#debug( "\ndroppedItemObjectID: %d" %Packet.droppedItemObjectID )
			
			Packet.droppedItemID = struct.unpack ("<H", self.data[6:8])[0]
			#debug( "\ndroppedItemID: %d"  %Packet.droppedItemID )
			
			Packet.droppedItem_x = struct.unpack ("<H", self.data[9:11])[0]
			#debug( "\nx: %d" %Packet.droppedItem_x )
			
			Packet.droppedItem_y = struct.unpack ("<H", self.data[11:13])[0]
			#debug( "\ny: %d" % Packet.droppedItem_y )
			
			Packet.droppedItemAmount = struct.unpack ("<H", self.data[15:17])[0]
			#debug( "\nAmount: %d" %Packet.droppedItemAmount )
			
			Packet.droppedItemDict[Packet.droppedItemObjectID]=[Packet.droppedItemID, Packet.droppedItem_x, Packet.droppedItem_y, Packet.droppedItemAmount]
			debug( "\n" )
			debug( Packet.droppedItemDict )
	
		
		
		elif self.type == 'SMSG_PLAYER_INVENTORY_ADD': # WORKS
			
			debug( "\n -- added stuff to inventory!" )
			ItemIndex = struct.unpack ("<H", self.data[2:4])[0]
			ItemAmount = struct.unpack ("<H", self.data[4:6])[0]
			ItemID = struct.unpack ("<H", self.data[6:8])[0]
						
			#droppedItemINDEX2 = struct.unpack ("<B", self.data[63])
			#droppedItemINDEX2 = struct.unpack ("<B", self.data[-2])
			#droppedItemINDEX3 = struct.unpack ("<B", self.data[-3])
			#droppedItemINDEX4 = struct.unpack ("<B", self.data[-4])
			#droppedItemINDEX5 = struct.unpack ("<B", self.data[-5])
			
			debug(ItemIndex, ItemAmount, ItemID)
			
			try:
				Packet.playerSlots[ItemIndex].itemAmount = Packet.playerSlots[ItemIndex].itemAmount + ItemAmount
			except KeyError: 
				Packet.playerSlots[ItemIndex] = Item(ItemID, ItemAmount)
			
			debug ("New item received:")
			debug (Packet.playerSlots[ItemIndex].itemID)
			debug (Packet.playerSlots[ItemIndex].itemAmount)
			
			
					
		elif self.type == 'SMSG_PLAYER_INVENTORY_REMOVE':
			
			
			for i in Packet.playerSlots:
				debug (i, Packet.playerSlots[i].itemID, Packet.playerSlots[i].itemAmount)
			
			itemIndex = struct.unpack ("<H", self.data[2:4])[0]
			itemAmount = struct.unpack ("<H", self.data[4:6])[0]
			
			# debug ("\nitem removed:\n")
			# debug(itemIndex, itemAmount)
			
			Packet.playerSlots[itemIndex].itemAmount = Packet.playerSlots[itemIndex].itemAmount - itemAmount
			
			# Now check if the item is completely gone from the inventory; delete from dictionary if so:
			
			if Packet.playerSlots[itemIndex].itemAmount == 0:
				del Packet.playerSlots[itemIndex]
				
				# When the item is completely gone, the item indexes (slot numbers) are shifting:
				Packet.playerSlots = dict(zip( range( 2, len( Packet.playerSlots.values() )+2 ), Packet.playerSlots.values() ) )
				
				debug ("\nItem completely removed from the inventory:")
				for i in Packet.playerSlots:
					debug (i, Packet.playerSlots[i].itemID, Packet.playerSlots[i].itemAmount)
			else:
				debug ("\nItem subtracted from the inventory:")
				for i in Packet.playerSlots:
					debug (i, Packet.playerSlots[i].itemID, Packet.playerSlots[i].itemAmount)

		
		
		elif self.type == 'SMSG_ITEM_REMOVE':
			debug( "\n -- item removed from map!" )
			droppedItemID = struct.unpack ("<L", self.data[-4:])[0]
			debug( "Removed item ID: %d" %droppedItemID )
			del Packet.droppedItemDict[droppedItemID]
			debug( "\nUpdated list of items on the map:" )
			debug( Packet.droppedItemDict )
			

			
		elif self.type == 'SMSG_PLAYER_CHAT':
			
			# debug("CHAT") # testing the packet identification
			# debug( self.data )
			
			if re.match (".*[a-zA-Z0-9]+\:\ [0-9]+\-[0-9]\ \([0-9]+\,[0-9]+", self.data) is not None:
				debug( "\n\nIncoming coordinates found!" )
				Packet.chatCoordinates = self.data
				
				mapID = list(Packet.chatCoordinates) 
				
				Packet.chatCoordinates = list(Packet.chatCoordinates) 
				#debug( Packet.chatCoordinates )
				pos = Packet.chatCoordinates.index("(")
				
				#~ mapID = Packet.chatCoordinates
				pos2 = mapID.index(":")
				del mapID[:pos2+2]
				pos2 = mapID.index("(")
				del mapID[pos2-1:]
				
				mapID = "".join(mapID)
				Packet.mapID = mapID
				
				debug ("MAP ID: %s" %mapID)
				
				del Packet.chatCoordinates[:pos+1] 
				#debug( "\n\n" )
				#debug( Packet.chatCoordinates )
				pos = Packet.chatCoordinates.index(")")
				del Packet.chatCoordinates[pos:]
				#debug( "\n\n" )
				#debug( Packet.chatCoordinates )
				pos = Packet.chatCoordinates.index(",")
				Packet.chatCoordinates_x = "".join(Packet.chatCoordinates[:pos])
				debug( "Coordinates X: %s" %Packet.chatCoordinates_x )
				Packet.chatCoordinates_y = "".join(Packet.chatCoordinates[pos+1:])
				debug( "Coordinates Y: %s" %Packet.chatCoordinates_y )
			
			elif findp_re.match( self.data[4:] ):
				#~ debug ("-- ALL PLAYERS LOCATED --")
				#~ debug (self.data[4:])
				plname, plmap, plx, ply = findp_re.findall( self.data[4:] )[ 0 ]

				Packet.loggedInPlayers[ plname ] = ( plmap, plx, ply )
				
				#~ debug ( 'Hmmm.... ' + str( Packet.loggedInPlayers ) )
			
			
			elif findpp_re.match( self.data[4:] ):
				#debug ("-- PLAYER PARTY DETECTED --")

				plname, party = findpp_re.findall( self.data[4:] )[ 0 ]

				Packet.playerParty[ plname ] = party

				#debug( Packet.playerParty )
				
			#else:
				#debug( "\n\nnon-coordinates chat inbound: %s" %self.data )
				
		
		
		elif self.type == 'SMSG_TRADE_REQUEST':		
			debug( "\n\nTrade request inbound! Use main menu to answer." )
			
		
		
		#elif self.type == 'SMSG_BEING_VISIBLE': Unknown being coordinates
			#debug ("BEING VISIBLE!")
			#self.spawnedID =  struct.unpack( "<L", self.data[ 2:6 ] )[0]
			#debug (self.spawnedID)
			
		
		
		elif self.type == 'SMSG_BEING_MOVE':
			
			self.CritterID =  struct.unpack( "<L", self.data[ 2:6 ] )[0] #WORKS; gets being ID
			self.CritterType = struct.unpack( "<H", self.data[ 14:16 ] )[0] # WORKS: identifies scorpion, maggot, etc.
			
			# debug( self.CritterType )
			# debug( self.CritterID )
			# debug ( type(self.CritterID) )
			
			# coordinates work, but values represent FINAL destination of the monster, not step-by-step.
			x_1 = struct.unpack ("<B", self.data[52])[0]
			x_2 = struct.unpack ("<B", self.data[53])[0]
			x_1 = bin(x_1).replace("0b", "").rjust(8,"0")
			x_2 = bin(x_2).replace("0b", "").rjust(8,"0")
			x = x_1[6:] + x_2[:6]
			x = int(x, 2)
			
			#debug( int(x, 2) )
			
			y_1 = struct.unpack ("<B", self.data[53])[0]
			y_2 = struct.unpack ("<B", self.data[54])[0]
			y_1 = bin(y_1).replace("0b", "").rjust(8,"0")
			y_2 = bin(y_2).replace("0b", "").rjust(8,"0")
			y = y_1[6:] + y_2
			y = int(y, 2)
			
			#debug( int(y, 2) )
			
			Packet.critterMovesTo_ID = self.CritterID
			Packet.critterMovesTo_x = x
			Packet.critterMovesTo_y = y
			
			# debug("Critter %d moves to %d %d" %(Packet.critterMovesTo_ID, Packet.critterMovesTo_x, Packet.critterMovesTo_y)) # WORKS
			
			
			try:				# WORKS, append the new movement to the existing critter ID
				Packet.critterMovements[self.CritterID].append((self.CritterType, x,y))
			except KeyError: 	# WORKS, add the new critter ID and the observed movement
				Packet.critterMovements[self.CritterID] = [(self.CritterType, x,y)]

			# NOTE: if we put self.critterMovements instead of class variable Packet.critterMovements, 
			# the dictionary is reset by every received package
			
			# print Packet.critterMovements
			
			
		
		elif self.type == 'SMSG_PLAYER_MOVE':
			
			# WORKS
			
			self.PlayerID =  struct.unpack( "<L", self.data[ 2:6 ] )[0]
						
			x_1 = struct.unpack ("<B", self.data[52])[0]
			x_2 = struct.unpack ("<B", self.data[53])[0]
			x_1 = bin(x_1).replace("0b", "").rjust(8,"0")
			x_2 = bin(x_2).replace("0b", "").rjust(8,"0")
			x = x_1[6:] + x_2[:6]
			x = int(x, 2)
			
			
			y_1 = struct.unpack ("<B", self.data[53])[0]
			y_2 = struct.unpack ("<B", self.data[54])[0]
			y_1 = bin(y_1).replace("0b", "").rjust(8,"0")
			y_2 = bin(y_2).replace("0b", "").rjust(8,"0")
			y = y_1[6:] + y_2
			y = int(y, 2)
			
			
			Packet.playerMovesTo_ID = self.PlayerID
			#debug( Packet.playerMovesTo_ID )
			Packet.playerMovesTo_x = x
			Packet.playerMovesTo_y = y
			
			# debug( "Player %s moved to:" %self.PlayerID ) # WORKS
			# debug(Packet.playerMovesTo_x, Packet.playerMovesTo_y) # WORKS
		
		
		
		elif self.type == 'SMSG_BEING_NAME_RESPONSE':
			#debug (" \n\nNPC NAME DETECTED \n\n ")
			Packet.npcDetectedName.append(self.data[6:11])
			#debug (Packet.npcDetectedName)
	
			
		
		elif self.type == 'SMSG_PLAYER_INVENTORY':
			debug( "\n\nINVENTORY DETECTED: \n" )
			inventory = self.data[4:]
			
			while inventory:
				invIndex = struct.unpack ("<H", inventory[0:2])[0]
				invID = struct.unpack ("<H", inventory[2:4])[0]
				invAmount = struct.unpack ("<H", inventory[6:8])[0]
				debug( invIndex, invID, invAmount)
				
				Packet.playerSlots[invIndex] = Item(invID,invAmount)
				
				try:
					Packet.playerInventory[invIndex].append((invID,invAmount))
					#~ Packet.playerSlots[invIndex].append((invID,invAmount))
				except KeyError: 	
					Packet.playerInventory[invIndex] = [(invID,invAmount)]
					#~ Packet.playerSlots[invIndex] = [(invID,invAmount)]
				
				inventory = inventory [18:]
			
						
		
		elif self.type == 'SMSG_PLAYER_EQUIPMENT':
			debug( "\n\nEQUIPMENT DETECTED: \n" )
			equipment = self.data[4:]
			
			while equipment:
				eqIndex = struct.unpack ("<H", equipment[0:2])[0]
				eqID = struct.unpack ("<H", equipment[2:4])[0]
				debug( eqIndex, eqID, )
				
				Packet.playerSlots[eqIndex] = Item(eqID,1)
				
				try:
					Packet.playerEquipment[eqIndex].append(eqID)
					#~ Packet.playerSlots[eqIndex].append((eqID,1))
				except KeyError: 	
					Packet.playerEquipment[eqIndex] = eqID
					#~ Packet.playerSlots[eqIndex] = [(eqID,1)]
					
				equipment = equipment [20:]
			
			
		
		elif self.type == 'SMSG_WALK_RESPONSE': # CLIENT JOZEK CAN'T DETECT PACKAGE WHEN IGOR MOVES
			
			x_1 = struct.unpack ("<B", self.data[8])[0]
			x_2 = struct.unpack ("<B", self.data[9])[0]
			x_1 = bin(x_1).replace("0b", "").rjust(8,"0")
			x_2 = bin(x_2).replace("0b", "").rjust(8,"0")
			x = x_1[6:] + x_2[:6]
			x = int(x, 2)
			
			y_1 = struct.unpack ("<B", self.data[9])[0]
			y_2 = struct.unpack ("<B", self.data[10])[0]
			y_1 = bin(y_1).replace("0b", "").rjust(8,"0")
			y_2 = bin(y_2).replace("0b", "").rjust(8,"0")
			y = y_1[6:] + y_2
			y = int(y, 2)

			# debug( "I moved to %d, %d" %(x,y) )
			
			
		
		elif self.type == 'SMSG_NPC_MESSAGE' or self.type == 'SMSG_NPC_CHOICE': 
			
			npcID = struct.unpack( "<L", self.data[ 4:8 ] )[0]
			debug( "Getting message from NPC with ID:" )
			debug( npcID )
			npcMessage = self.data[ 8:-1 ]
			Packet.npcIncomingMessage.append( ( npcID, npcMessage ) )
			debug( "\n\n"  )
			debug( npcMessage )
			
			if re.match (".*[a-zA-Z0-9]*\[[a-zA-Z0-9]*\]", self.data) is not None:
				#~ print "NPC name:"
				chat = list(self.data)
				pos1 = chat.index("[")
				del chat[:pos1+1]
				pos2 = chat.index("]")
				del chat [pos2:]
				chat = "".join(chat)
				#~ debug (chat)
				Packet.talkingWithNPC = chat
				
				
				
			#~ else:
				#~ debug("NPC name not found")
		
		#elif self.type == 'SMSG_NPC_CHOICE':
			#npcMessageQuery = self.data[ 8: ]
			#debug( "\n\nChoose answer\n\n" )
			#debug( npcMessageQuery )
			
		
		elif self.type == 'SMSG_NPC_CLOSE':
			#debug ("CLOSING NPC COMMUNICATION")
			Packet.talkingWithNPC = None
			
			
		elif self.type == 'SMSG_PARTY_INVITED':
			Packet.whoInvites = struct.unpack( "<L", self.data[ 2:6 ] )[0]
			whichParty = self.data[ 6: ]
			debug( "\nYou got an invitation from %s to join party %s " %(Packet.whoInvites, whichParty) )
					
					
					
					
		elif self.type == 'SMSG_PARTY_INFO': # SCRIPT DOES NOT ALWAYS REGISTER THIS PACKET!
			
			debug ("PARTY UPDATE")
			partyName = self.data[4:28]
			partyName = re.sub('\x00', '', partyName)
			members = []
			debug ("party %s updated" %partyName)
			
			partyMembers = self.data[28:]
			
			while (partyMembers):
				memberName = partyMembers[4:28]
				memberName = re.sub('\x00', '', memberName)
				members.append(memberName)
				partyMembers = partyMembers [46:]
				#debug (memberName)
				#debug (Packet.parties)
				
			Packet.parties[partyName] = members
			debug (Packet.parties)
		
		
		elif self.type == 'SMSG_PARTY_LEAVE':
			leaving = self.data[6:]
			leaving = re.sub('\x00', '', leaving)
			debug ("leaving party: %s" %leaving)
			
			for k in Packet.parties.itervalues():
				try:
					k.remove(leaving)
					debug ("party left")
				except ValueError:
					pass
				
			
		
		elif self.type == 'SMSG_PARTY_MESSAGE':
			partyMessageSender = struct.unpack( "<L", self.data[ 4:8 ] )[0]
			partyMesageTxt = self.data[ 8: ]
			debug( "\nParty chat message received from player: %d" % partyMessageSender)
			debug( "\nParty chat message: %s" % partyMesageTxt)
			
		# elif self.type == 'SMSG_PLAYER_STATUS_CHANGE':
			# debug (" \n\n\nSTATUS CHANGE DETECTED \n\n\n ")
		
		# elif self.type == 'SMSG_PLAYER_UPDATE_2':
			# debug (" \n\n\nSTATUS CHANGE DETECTED \n\n\n ")
			
		# elif self.type == 'SMSG_PLAYER_SKILLS':
			# debug (" \n\n\nSTATUS CHANGE DETECTED \n\n\n ")
		
		
		
		elif self.type == 'SMSG_BEING_CHANGE_LOOKS2': # WORKS, extracting the player ID
			self.myID =  struct.unpack( "<L", self.data[ 2:6 ] )[0]
			# debug ("\n\nPlayer ID DETECTED: ")
			# debug (self.myID)
			
					
	def _parse_ip( self, string ):
		'''Parse an IP address'''
		return ".".join( map( str, map( ord, string ) ) )







class UpdateError( ValueError ):
	pass






class Connection:
	
	'''Class to hold a connection to the three TWM servers (login, character, map) and
	provide a low level interface to control a character'''
	
	def __init__( self, server, port, username, password, character=0 ):
		'''Initialization, paramers are self-explanatory except for character which is 
		the selected index of the account character to play with (first is zero, second is 1 etc.)'''
		self.server = server
		self.port = port
		self.username = username
		self.password = password
		self.characters = {}
		self.character_list = []
		self.character = character
		self.sex = None
		self.pb = None # packet buffer
		

	def login( self ):
		'''Login to login server, then select character from character server and 
		finally connect to map server.'''
		self.srv = socket.socket() 
		self.srv.connect( ( self.server, self.port ) ) 
		self.pb = PacketBuffer( self.srv )
		
		self.pb.start()
		
		debug( '\nConnected to server: %s:%d' % ( self.server, self.port ) )
		self.srv.sendall( "\x64\0\1\0\6\0%s%s\x27" % ( self.username.ljust( 24, '\0' ), self.password.ljust( 24, '\0' ) ) )

		buff = self.pb.getNew( 'SMSG_LOGIN_DATA' ) 
		'''
		SMSG_LOGIN_DATA, 0x0069,  Login Data
		Sent in response to Login Request. This packet is sent to the client by the server to define 
		the character sex, the account and session IDs, as well as provide a list of worlds the player can connect to.
		Upon receiving this packet, the client shall:
		Disconnect from the login server
		Connect to the user-specified character server
		Immediately send Character Server Connection Request.
		'''   
		

		# now get the login data out of the packet and connect to the character server
		self.id1, self.accid, self.id2, self.sex = buff.id1, buff.accid, buff.id2, buff.sex
		charip = self.server
		charport = buff.charport 
		debug( 'Login successful! Connecting to character server a %s:%d...' % ( charip, charport ) )
		self.srv.close()
		self.pb.stop()

		assert charport
		self.srv = socket.socket()
		self.pb.srv = self.srv
		self.srv.connect( ( charip, charport ) )
		debug( 'Connected to character server! Selecting character...' )

		self.srv.sendall( "\x65\0%s\0\0%s" % ( struct.pack( "<LLL", self.accid, self.id1, self.id2 ), chr( self.sex ) ) )
		
		self.pb.go()
		
		buff = self.pb.getNew( 'SMSG_CHAR_LOGIN', timeout=20 )
		# ok got character information, extract the names (send \x66 to get mapserver info, and login then)
		self.character_list = buff.charlist
		self.characters = buff.characters
		debug( "Available characters:" )
		
		for j in [ i.__dict__ for i in self.characters.values() ]:
			debug( j[ "name" ] )
			debug( j )
			
		# Extracting character name for later functions:
		self.characterName = j["name"]
		# debug (self.characterName)
		
		self.pb.stop()
		self.srv.sendall( "\x66\0%s" % chr( self.character ) )
		self.pb.go()
		
		debug( "Get map info" )
		buff = self.pb.getNew( 'SMSG_CHAR_MAP_INFO' )
		
		charid = buff.charid
		mapip = self.server
		mapport = buff.mapport
		
		self.srv.close()
		assert mapport
		self.pb.stop()
		
		self.srv = socket.socket()
		self.pb.srv = self.srv
		self.srv.connect( ( mapip, mapport ) )
		debug( "Connected to map server..." )
		
		c = self.character_list[ self.character ] # get selected character
		debug( "Character '%s' selected. Connecting to map server at %s:%d" % ( c.name, mapip, mapport ) )
		self.srv.sendall( "\x72\0%s" % struct.pack( "<LLLLB", self.accid, c.char_id, self.id1, self.id2, self.sex ) )
		self.pb.go()			

		buff = self.pb.getNew( 'SMSG_MAP_LOGIN_SUCCESS' )
		#self.pb.stop()

		# connected, send to server that the map has been loaded
		self.srv.sendall( "\x7d\0" )
		debug( "Map loaded" )

	def quit( self ):
		'''Logout from server'''
		self.srv.sendall( "2u\0\0" ) # CMSG_CLIENT_DISCONNECT
		self.srv.sendall( "\x8a\x01\0" ) # CMSG_CLIENT_QUIT
		self.pb.kill = True
		
	def attack( self, target, keep ):
		'''Attack a given character: the attacker must be placed nearby monster's coordinates'''
		'''if keep:
			k = 0
		else:
			k = 7'''
		#self.srv.sendall( "\x89\0%s" % struct.pack( "<LB", target, k ) )
		self.srv.sendall( "\x89\0%s" % struct.pack( "<LB", target, keep ) )
		
	def stop_attack ( self ):
		self.srv.sendall ("\x18\x01")
		
	def emote( self, emote_id ):
		'''Emote with a given emote ID (not functional yet)'''
		self.srv.sendall( "\xbf\0%s" % struct.pack( "<B", emote_id ) )
		
			
	def setDirection( self, direction ):
		'''Set direction (turn 1 - down, 2 - left, 6 - up, 8 - right)'''
		self.srv.sendall( "\x9b\0\0\0%s" % struct.pack( "<B", direction ) )
		debug( "Character moved!" )

	def setDestination( self, x, y, direction ):
		'''Set destination (walk to given x, y coordinates with orientation direction like in setDirection)'''
		''' use \where in chat to get coordinates # OR PRESS F10) '''
		
		debug( "SET DESTINATION" )
		debug( "X: %d" %x )
		debug( "Y: %d" %y )
		
		data = bin(x)[-10:].replace( 'b', '0' ).rjust(10).replace( ' ', '0' ) + bin(y)[-10:].replace( 'b', '0' ).rjust(10).replace( ' ', '0' ) + bin(direction)[-4:].replace( 'b', '0' ).rjust(4).replace( ' ', '0' )
		
		data = data[ :8 ], data[ 8:16 ], data[ 16: ]
		data = [ int( '0b' + i, 2 ) for i in data ]
		
		b1, b2, b3 = data
		self.srv.sendall( "\x85\0%s" % struct.pack( "<BBB", b1, b2, b3 ) )

	def sit( self ):
		'''Sit and don't move ;-)'''
		self.srv.sendall("\x89\0\0\0\0\0\x02") 
		debug( "Sitting!" )
		

	def stand( self ):
		'''Stand up!'''
		self.srv.sendall("\x89\0\0\0\0\0\x03") 

	def whisper( self, nick, message ):
		'''Whisper a message to a given nick'''
		self.srv.sendall( "\x96\0%s%s%s" % (struct.pack("<H", len(message)+28), nick.ljust(24, '\0'), message) )

	def pickUp( self, itemid ):
		'''Pick up a given item by ID (not functional yet)'''
		self.srv.sendall( "\x9f\0%s" % ( struct.pack( "<L", itemid ) ) )
		
	def itemPickUp (self, itemIndex): # WORKS, but need to know item index
		self.srv.sendall( "\x9f\x00%s" % (struct.pack( "<L", itemIndex )))
		
	def itemEquip (self, itemID): # WORKS, but need to know item index (slot number)
		self.srv.sendall( "\xa9\x00%s" % ( struct.pack( "<L", itemID ) ) )

	def NPCChoose( self, NPC, choice ):
		'''Answer to an NPC choice. NPC is the NPCs ID (from the message received) and
		choice is the index of the chocies from the received list of possible choices 
		(not functional yet)'''
		self.srv.sendall( "\xb8\0%s" % ( struct.pack( "<LB", NPC, choice ) ) )

	def NPCNextDialog( self, NPC ):
		'''Get the next dialog from an NPC. NPC is the NPCs id (from the message received).'''
		self.srv.sendall( "\xb9\0%s" % ( struct.pack( "<L", NPC ) ) )
		# debug("NEXT sent...")
	
	def createParty (self, partyName): # WORKS
		self.srv.sendall( "\xF9\0%s" % partyName.ljust(24, '\0'))
		
	def locatePlayer (self): # GM chat messages
		
		debug ("Character %s location:" %self.characterName)
		charNameHex = self.characterName.encode("hex")
		
		# debug (charNameHex)
		# debug (type(charNameHex))
		
		# 4a 6f 7a 65 6b ("Jozek")
		# 20 3a 20 40 77 68 65 72 65 (" : @where")
		
		locateCommand = charNameHex + "203a20407768657265" + "00"
		locateCommand = locateCommand.decode("hex")
		packetLength = len(locateCommand) + 4
		
		# debug (locateCommand)
		
		self.srv.sendall( "\x8c\0%s%s" %(struct.pack("<H", packetLength),locateCommand))
		
		#self.srv.sendall( "\x8c\0\x13\x00%s" %locateCommand) # x13 je velicina paketa, koja nije fiksna
		#self.srv.sendall( "\x8c\0\x13\x00\x4a\x6f\x7a\x65\x6b\x20\x3a\x20\x40\x77\x68\x65\x72\x65\x00" ) # WORKS for Jozek
		#self.srv.sendall( "\x8c\0%s" % (struct.pack("<H", "igor : @where jozek"))) 
		
	def listAllPlayers (self):
		charNameHex = self.characterName.encode("hex")
		listCommand = charNameHex + "203a204077686f00"
		listCommand = listCommand.decode("hex")
		packetLength = len(listCommand) + 4
		self.srv.sendall( "\x8c\0%s%s" %(struct.pack("<H", packetLength),listCommand))
		#debug("\n-- list all players command sent-- ")
		
	def whereAnyone (self, hunter, victim): # Works for Jozek -> igor
		self.srv.sendall( "\x8c\x00\x18\x00%s : @where %s\x00" %(hunter, victim))
		
	def partyStatus (self, character, other):
		# TODO: For some reason everything breaks after this command is sent... Have to investigate...
		self.srv.sendall( "\x8c\x00\x18\x00%s : @whogroup %s\x00" %(character, other))
		
	def goToDroppedItem (self):
		debug( "\n\n" )
		dIOID = Packet.droppedItemObjectID[0]
		debug( "Dropped item index: %d" %dIOID )
		dIID = Packet.droppedItemID[0]
		x_coord = Packet.droppedItem_x[0]
		y_coord = Packet.droppedItem_y[0]
		c.setDestination (x_coord -1, y_coord, 2)
		time.sleep( 2 )
		c.itemPickUp (dIOID)
		
	def followPlayer(self):
		goTo_x = int(Packet.chatCoordinates_x)-1
		goTo_y = int(Packet.chatCoordinates_y)
		c.setDestination (goTo_x, goTo_y, 2)
		
	def takeAllDroppedItems(self):
		
		for key, value in Packet.droppedItemDict.items():
			
			itemID = key
			debug( "ItemID: %d" %itemID )

			x = value[1]
			debug( "x coord: %d" %x )
			
			y = value[2]
			debug( "y coord: %d" % y )
			
			c.setDestination(x-1, y, 2)
			time.sleep(2)
			c.itemPickUp(itemID)
			time.sleep(0.5)
		
	def talkToNPC (self, npcID): # works, BUT need to know NPC ID, and stand closer to it. NPC IDs become available by clicking "n" in game
		self.srv.sendall( "\x90\x00%s\x00" % (struct.pack("<L", npcID)))
			
	def tradeResponse(self, tradeAnsw): # WORKS
		self.srv.sendall( "\xE6\x00%s" % (struct.pack("<B", tradeAnsw)))
		
	def experimentalSend(self): # experimental packets for sending to server and watching for responses
		self.srv.sendall( "\xC1\0" )
		
	def sendTradeRequest(self): # WORKS, but currently with *fixed* being_id (b8:84:1e:00 -> igor). Need to know how to obtain being_ids.
		self.srv.sendall( "\xe4\x00\xb8\x84\x1e\x00" )
		
	def followAnyPlayer(self, player_ID):
		
		if Packet.playerMovesTo_ID == player_ID:

			# --- Version 1: call function manually to resume following: ---

			#c.setDestination (Packet.playerMovesTo_x -1, Packet.playerMovesTo_y, 2)
			
			# --- Version 2: press CTRL+C to stop following: ---
			
			#try: 
				#while True:
					#c.setDestination (Packet.playerMovesTo_x -1, Packet.playerMovesTo_y, 2)
					#time.sleep(1)
			#except KeyboardInterrupt:
				#exit
			
			# --- Version 3: press ANY KEY to stop following: ---
			
			while True:	
				c.setDestination (Packet.playerMovesTo_x, Packet.playerMovesTo_y, 2)
				if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
					line = raw_input()
					break
				time.sleep(1)
			
		else:
			debug( "Some other player also moving." )
		
		
	def followAnyCritter(self, critterID):
		
		if Packet.critterMovesTo_ID == critterID:
			
			while True:	
				
				c.setDestination (Packet.critterMovesTo_x -1, Packet.critterMovesTo_y, 2)
				
				if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
					line = raw_input()
					break
					
				time.sleep(1)


	def tradeItems(self, itemID, itemNo):
		self.srv.sendall( "\xe8\x00%s" % (struct.pack("<HL", itemID, itemNo)))
		# pr. e8:00:04:00:02:00:00:00

	def addItemsComplete(self):
		self.srv.sendall( "\xeb\x00")
		
	def tradeComplete(self):
		self.srv.sendall( "\xef\x00")

	def answerToNPC(self, npcID, answer):
		print self.srv.sendall( "\xb8\x00%s" % (struct.pack("<LB", npcID, answer)))
		debug( 'Answered to NPC %d with answer %d' % ( npcID, answer ) )
		
	def closeCommunication(self, npcID):
		self.srv.sendall( "\x46\x01%s" % (struct.pack("<L", npcID )))
		
	def inviteToParty(self, npcID):
		self.srv.sendall( "\xfc\x00%s" % (struct.pack("<L", npcID )))	
		
	def leaveParty(self):
		self.srv.sendall( "\x00\x01" )	
		
	def responseToPartyInvite(self, responseToInvite):
		self.srv.sendall("\xff\x00%s\x00\x00\x00" % (struct.pack("<LB", Packet.whoInvites, responseToInvite)))
		
	def sendPartyMessage(self, message):
		messageLength = len(message)+4
		self.srv.sendall( "\x08\x01%s%s" % (struct.pack("<H", messageLength ), message))
		
	def dropItem(self, itemIndex, ItemQ):
		# packet example: a2:00:07:00:01:00
		self.srv.sendall( "\xa2\x00%s" % (struct.pack("<HH", itemIndex, ItemQ)))


if __name__ == '__main__':
	from testconf import * 
	c = Connection( SERVER, PORT, USERNAME, PASSWORD, CHARACTER )
	c.login()

	time.sleep( 1 )
	c.pb.go()		
	
	# Get the initial location of the player:
	c.locatePlayer()
		
	while not c.pb.hasNew():
		time.sleep( 0.1 )
	
	

	while True:
	
		debug( "\n\n" )
		debug( "      ", 46 * "#" )
		debug( "       # ModelMMORPG Low Level TMW Python Interface #" )
		debug( "      ", 46 * "#" )
		debug( "\n" )
		
		debug( 30 * "-" , "MENU" , 30 * "-" )

		debug( "1. Navigation" )
		debug( "2. Attack" )
		debug( "3. Sit" )
		debug( "4. Stand" )
		debug( "5. Whisper" )
		debug( "6. Stop Attack" )
		debug( "7. Pick Item" )
		debug( "8. Equip Item" )
		debug( "9. EXIT" )
		debug( "10. PARTY: Create party" )
		debug( "11. Where am I?" )
		debug( "12. Go near the last dropped item!" )
		debug( "13. Go near the player!" )
		debug( "14. Where is anyone?"  )
		debug( "15. Go to Igor!" )
		debug( "16. Take all dropped items!" )
		debug( "17. Talk to NPC" )
		debug( "18. TRADE ANSW: Answer Trade Request" )
		debug( "19. exp: CMSG_WHO_REQUEST" )
		debug( "20. TRADE REQ: Send Trade Request (to Igor)" )
		debug( "21. Follow player" )
		debug( "22. Follow critter" )
		#debug( "23. Follow critter and attack" )
		debug( "24. TRADE: add items" )
		debug( "25. TRADE: done adding items" )
		debug( "26. TRADE: CONFIRM&DONE" )
		debug( "27. NPC: Answer to the man/lady" )
		debug( "28. NPC: Stop communication" )
		debug( "29. PARTY: Invite to Party" )
		debug( "30. PARTY: Leave Party" )
		debug( "31. PARTY: Response to a Party Invitation" )
		debug( "32. PARTY: Send a party message" )
		debug( "33. Show (*initial*) Player Inventory" )
		debug( "34. Show (*initial*) Player Equipment" )
		debug( "35. Show (*initial*) Player Slots" )
		debug( "36. Drop item" )
		debug( "37. List all logged in players with their position")
		debug( "38. Send NEXT in dialog with NPC")
		debug( "39. Get PARTY status" )
		debug( "40. NPC: Next dialog" )
		
		debug( 67 * "-" )
		
		command = raw_input("Choose Menu option: ")
		
		if command == "1":
			x_coord = int(raw_input("input x: "))
			y_coord = int(raw_input("input y: "))
			c.setDestination( x_coord, y_coord, 2 )
			
		elif command == "2": 
			monster_ID = int(raw_input("monster ID: "))
			keep_attacking = raw_input("keep attacking? (y/n): ")
			
			if keep_attacking == "y":
				keep_attacking = 7
			else:
				keep_attacking = 0
			
			c.attack(monster_ID, keep_attacking)
			
		elif command == "3": 
			c.sit()
			
		elif command == "4": 
			c.stand()
			
		elif command == "5": 
			wh_to = raw_input("User nickname: ")
			wh_message = raw_input("Enter message: ")
			c.whisper(wh_to, wh_message) 
			
		elif command == "6": 
			c.stop_attack()
			
		elif command == "7":
			itemIndex = int(raw_input("Enter item index: "))
			c.itemPickUp(itemIndex)
		
		elif command == "8": 
			
			itemID = int(raw_input("Enter item ID (slot): "))
			c.itemEquip(itemID)	
		
		elif command == "9": 
			break
		
		elif command == "10": 
			partyName = raw_input("Party name: ")
			c.createParty(partyName) 
			
		elif command == "11": 
			c.locatePlayer()
			
		elif command == "12":
			c.goToDroppedItem()
			
		elif command == "13":
			c.followPlayer()
			
		elif command == "14":
			hunter = raw_input("Enter your nickname: ")
			victim = raw_input("Whom do you seek?: ")
			c.whereAnyone (hunter, victim)
			
		elif command == "15":
			c.whereAnyone("Jozek", "igor")
			time.sleep(1)
			c.followPlayer()
			
		elif command == "16":
			c.takeAllDroppedItems()
			
		elif command == "17":
			npcID = int(raw_input("Enter NPC id: "))
			c.talkToNPC(npcID)

		elif command == "18":
			tradeAns = raw_input("Y/N: ")
			if tradeAns == "Y":
				c.tradeResponse(3)
			else:
				c.tradeResponse(4)
		
		elif command == "19":	
			c.experimentalSend()
			
	
		elif command == "20":	
			c.sendTradeRequest()
			
			
		elif command == "21":	
			followWho = int(raw_input("Please enter player ID: "))
			c.followAnyPlayer(followWho)
			
			
		elif command == "22":
			followWhat = int(raw_input("Please enter critter ID: "))
			c.followAnyCritter(followWhat)
			
			
		elif command == "24":
			itemIndex = int(raw_input("Please enter item Index: "))	
			itemQ = int(raw_input("Please enter quantity: "))
			c.tradeItems(itemIndex, itemQ)
			
		
		elif command == "25":
			c.addItemsComplete()
			
		elif command == "26":
			c.tradeComplete()
		
		elif command == "27": # Sending identical packet as a real client, but no response?
			npcID = int(raw_input("Please enter npc ID: "))
			answer = int(raw_input("Please enter your choice: "))
			c.answerToNPC(npcID, answer)
			
		elif command == "28":
			npcID = int(raw_input("Please enter npc ID: "))
			c.closeCommunication(npcID)
			
		elif command == "29":
			npcID = int(raw_input("Please enter ID of the player you wish to invite: "))
			c.inviteToParty(npcID)	
		
		elif command == "30":
			c.leaveParty()
			
		elif command == "31":
			responseToInvite = int(raw_input("Type 1 for accept, 0 for refuse: "))
			c.responseToPartyInvite(responseToInvite)
	
		elif command == "32":
			partyMessage = raw_input("Type your message: ")
			c.sendPartyMessage(partyMessage)
			
		elif command == "33":
			debug (Packet.playerInventory)
			
		elif command == "34":
			debug (Packet.playerEquipment)
			
		elif command == "35":
			debug ("\n\nSlot NO, Item ID, Item Amount:")
			for i in Packet.playerSlots:
				debug (i, Packet.playerSlots[i].itemID, Packet.playerSlots[i].itemAmount)
	
		elif command == "36":
			itemIndex = int(raw_input("Please enter item Index: "))
			itemQ = int(raw_input("Please enter item quantity: "))
			c.dropItem(itemIndex, itemQ)
			
		elif command == "37":
			c.listAllPlayers()
			
		elif command == "38":
			npcID = int(raw_input("Enter NPC id: "))
			c.NPCNextDialog(npcID)

		elif command == "39":
			character = raw_input("Enter your nickname: ")
			other = raw_input("Whose membership do you want to test?: ")
			c.partyStatus( character, other )

		elif command == "40":
			npcID = int( raw_input( "Enter NPC id:" ) )
			c.NPCNextDialog( npcID )
					
			
			
	'''
	for i, j in zip( range( 50, 90 ), range( 50, 90 ) ): 
		c.setDestination( i, j, 1 )
		time.sleep( 0.2 )
	'''
	


	time.sleep( 2 )
	debug( [ (i.type, i.data) for i in c.pb.packets ] )

	'''
	m1 = c.pb.getNew( ( 'SMSG_NPC_MESSAGE', 'SMSG_PLAYER_CHAT' ) )
	m2 = c.pb.getNew( ( 'SMSG_NPC_MESSAGE', 'SMSG_PLAYER_WARP' ) )
	if m2.type != 'SMSG_PLAYER_WARP':
		m3 = c.pb.getNew( 'SMSG_NPC_CHOICE' )

		debug( m1.NPCid )
		debug( m1.message )
		debug( m2.message )
		debug( m3.choices )

		c.NPCChoose( m1.NPCid, 1 )

		time.sleep( 1 )
		
		c.NPCNextDialog( m1.NPCid )
		
		time.sleep( 1 )
		
		c.NPCNextDialog( m1.NPCid )
		
		time.sleep( 1 )
		
		c.NPCNextDialog( m1.NPCid )
		
		time.sleep( 1 )
		
		c.NPCNextDialog( m1.NPCid )
		
		time.sleep( 1 )
		
		c.NPCNextDialog( m1.NPCid )
		
		time.sleep( 1 )
	else:
		debug( m2.map, m2.x, m2.y )


	debug( [ (i.type, i.data) for i in c.pb.packets ] )
	'''
	c.quit() # works
	sys.exit()

