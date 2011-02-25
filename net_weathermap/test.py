#!/usr/bin/env python
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) 2011 Alexey Kostyuk <unitoff+pynetweathermap@gmail.com>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------

import logging
logging.basicConfig(filename='log.txt',
                    level=logging.INFO,
                    format='%(asctime)s %(name)-15s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M',)

from pymaps import Node, Link, Map 
import unittest

class TestNode(unittest.TestCase):
    def setUp(self):
        self.a_node = Node(x=40,y=240,color='#00FF00',label='Point A')
        self.b_node = Node(x=340,y=240,color='#00FF00',label='Point B')
        self.map = Map([Link(self.a_node,self.b_node,1000,width=3,debug=True)])

    def testDrawArrows(self):
        self.map.draw_arrows()

    def testDrawLabels(self):
        self.map.draw_labels()

    def testSaveImage(self):
        self.map.save('/home/unit/Desktop/map.png')

    def testNewSaveImage(self):
        a = Node(x=40,y=240,color='#00FF00',label='Point A')
        b = Node(x=600,y=240,color='#00FF00',label='Point B')
        m = Map([Link(a,b,1000,width=3,debug=True)])
        m.draw_arrows()
        m.draw_labels()
        m.save('map.png')

if __name__ == "__main__":
    unittest.main()
