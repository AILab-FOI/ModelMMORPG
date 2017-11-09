#!/usr/bin/env python
#-*- coding: utf-8 -*-

import spade
from spade.SWIKB import SWIKB as KB
import llinterface as lli
import time
import TMWbehavs
from random import random, randint, choice
from os.path import isfile, join


class ManaWorldPlayer(spade.Agent.BDIAgent, lli.Connection):


	class ChangeRole(spade.Behaviour.OneShotBehaviour):
		"""Behaviour to change the Role of the Agent. The Agent will acquire behaviours of the needed Role."""
		def _process(self):
			pass

	def getMyLocation( self ):
		''' Get player location
			Returns tuple ( mapID, X, Y ) '''
		if not hasattr( self, 'location' ):
			self.location = None
		try:
			self.locatePlayer()
			time.sleep( 0.5 )
			if self.location == ( self.pb.playerMap, self.pb.playerPosX, self.pb.playerPosY ):
				return None
			self.location = ( self.pb.playerMap, self.pb.playerPosX, self.pb.playerPosY )
			if self.location[ 0 ]:
				return self.location
			else:
				return ()
		except:
			return ()

	def say(self, msg):
		''' Say something (e.g. print to console for debug purposes) '''
		print '%s: %s' % (self.name.split('@')[0], str(msg))

	def __init__(self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER, *args, **kwargs):
		spade.Agent.Agent.__init__(self, *args, **kwargs)
		lli.Connection.__init__(self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER)
		lli.CHARACTER = self.name.split('@')[0]

		self.kb = KB()
		self.destinationNPC = None

		# Check if there is an existing knowledge base
		self.kbfile = join(KBFOLDER, lli.CHARACTER + '.pl')
		if isfile(self.kbfile):
			try:
				self.say('I found my old brain!')
				self.kb.ask("['" + self.kbfile + "']")
				self.say('Loaded my previous state of mind!')
			except:
				self.say('Error while loading previous knowledge base file, aborting!')
				import sys
				sys.exit()

		try:
			self.kb.ask("['planner.pl']")
			self.say('Planner loaded!')
		except:
			self.say('Error while loading planner, aborting!')
			import sys
			sys.exit()

		try:
			self.kb.ask("['item-db.pl']")
			self.say('Item knowledge base loaded!')
		except:
			self.say('Error while loading item knowledge base, aborting!')
			import sys
			sys.exit()

		try:
			self.kb.ask("['npc-db.pl']")
			self.say('NPC knowledge base loaded!')
		except:
			self.say('Error while loading NPC knowledge base, aborting!')
			import sys
			sys.exit()

		''' TODO: Uncomment this later when random_walk is fully implemented -- working on it'''
		try:
			self.say('Map knowledge base loading (this might take some time)!')
			self.kb.ask("['tmwmap_candor.P']")
			time.sleep( 9 )
			self.say('Map knowledge base loaded!')
		except:
			self.say('Error while loading map knowledge base, aborting!')
			import sys
			sys.exit()

	def _setup(self):
		self.login_complete = False

		reason = TMWbehavs.Reason()
		self.addBehaviour(reason)


if __name__ == '__main__':
	from testconf import *
	import argparse
	import os
	import glob

	parser = argparse.ArgumentParser(description='Create a TMW agent player (mali_agent[num])')
	parser.add_argument('--name', help='Create a TMW agent "mali_agent[num]" agents', type=int)
	parser.add_argument('--num', help='Create [num] TMW agents from [name] to [name+num] "mali_agent[i]" agents', type=int)
	parser.add_argument('--interval', help='Interval between agent instances in seconds', type=int, default=10)
	parser.add_argument('--clear', help='Clear existing knowledge bases (DANGEROUS: Deletes all .pl files from KBFOLDER)', action='store_true')
	
	
	args = parser.parse_args()

	# Delete all knowledge bases
	if args.clear:
		files = glob.glob(join(KBFOLDER, '*.pl'))
		for f in files:
			os.remove(f)
	
	if args.num and args.name:
		agent_list = []	
		for i in range(args.name, args.name + args.num):
			a = ManaWorldPlayer(SERVER, PORT, 'mali_agent%d' % i, PASSWORD, CHARACTER, 'agent_%d@127.0.0.1' % i, 'tajna')
			a.start()
			time.sleep(args.interval)
			agent_list.append(a)
	elif args.name:
		a = ManaWorldPlayer(SERVER, PORT, 'mali_agent%d' % args.name, PASSWORD, CHARACTER, 'mali_agent%d@127.0.0.1' % args.name, 'tajna')
		a.start()

	else:
		print 'Invalid number of arguments. Type "hlinterface.py --help" for details.'
	
