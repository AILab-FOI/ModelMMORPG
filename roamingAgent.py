#!/usr/bin/env python
#-*- coding: utf-8 -*-

import spade
from spade.SWIKB import SWIKB as KB
import time
import llinterface as lli
import random


class Player(spade.Agent.BDIAgent, lli.Connection):
    """Reasoning agent"""

    def say(self, msg):
        print '{[0]}: {}'.format(
            self.name.split('@'), msg)

    class roamBehav(spade.Behaviour.Behaviour):
        """The agent will roam in a 20x20 square"""
        def _process(self):
            time.sleep(3)
            posX = random.randint(40, 60)
            posY = random.randint(90, 108)

            self.myAgent.say('going to {}, {}'.format(posX, posY))

            self.myAgent.setDestination(posX, posY, 2)


    class Login(spade.Behaviour.OneShotBehaviour):
        """Login for the agent"""
        def _process(self):
            self.myAgent.login()

            time.sleep(1)

    def __init__(self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER, *args, **kwargs):
        spade.Agent.Agent.__init__(self, *args, **kwargs)
        lli.Connection.__init__(
            self, SERVER, PORT, USERNAME, PASSWORD, CHARACTER)
        lli.CHARACTER = self.name.split('@')[0]
        # self.co.login()

    def _setup(self):
        login = self.Login()
        self.addBehaviour(login)

        roamingBehav = self.roamBehav()
        self.addBehaviour(roamingBehav)


if __name__ == '__main__':
    from testconf import *
    a = Player(
        SERVER,
        PORT,
        USERNAME,
        PASSWORD,
        CHARACTER,
        'player@127.0.0.1', 'tajna')
    a.start()
    # time.sleep(4)
    # a._kill()
