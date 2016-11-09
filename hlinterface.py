#!/usr/bin/env python
#-*- coding: utf-8 -*-

import spade
from spade.SWIKB import SWIKB as KB
import llinterface as lli
import time

class ManaWorldPlayer( spade.Agent.BDIAgent, lli.Connection ):
	def say( self, msg ):
		print '%s: %s' % ( self.name.split( '@' )[ 0 ], str( msg ) )

	class Login( spade.Behaviour.OneShotBehaviour ):
		def _process( self ):
			self.myAgent.login()

			time.sleep( 1 )
			self.myAgent.pb.go()			
			while not self.myAgent.pb.hasNew():
				time.sleep( 0.1 )

	class Reason( spade.Behaviour.Behaviour ):
		def _process( self ):
			# update KB
			# self.myAgent.kb.addSentence(
			# generate possible objectives
			# choose objective
			# plan
			pass

	def __init__( self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER, *args, **kwargs ):
		spade.Agent.Agent.__init__( self, *args, **kwargs )
		lli.Connection.__init__( self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER )
		
		self.kb = KB()
		try:		
			self.kb.loadModule( 'planner.pl' )
			self.say( 'Planner loaded!' )
		except:
			self.say( 'Error while loading planner, aborting!' )
			import sys
			sys.exit()

		try:		
			self.kb.loadModule( 'tmwmap.P' )
			self.say( 'Map knowledge base loaded!' )
		except:
			self.say( 'Error while loading map knowledge base, aborting!' )
			import sys
			sys.exit()


	def _setup( self ):
		login = self.Login()
		self.addBehaviour( login )

SERVER = 'dragon.foi.hr' 
PORT = 6901
USERNAME = ''
PASSWORD = ''
CHARACTER = 0

if __name__ == '__main__':
	a = ManaWorldPlayer( SERVER, PORT, USERNAME, PASSWORD, CHARACTER, 'player@127.0.0.1', 'tajna' )
	a.start()
