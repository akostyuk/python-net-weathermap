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

class Pallete:
    def __init__(self, colors):
        if colors is None:
            self.__base()
        else:
            self.colors = colors
        self.__scale()
        
    def __base(self):
        self.colors = ["#ffffff", "#c0ffbd", "#19ff4f", "#00a310",
                       "#fbff8f", "#fbff00", "#ff7654","#ff0000",]
        
    def __scale(self):
        scale = len(self.colors) - 1
        lv = []
        lv.append([0])
        step = 100/scale
        for i in xrange(1,scale+1,1):
            new = range(lv[-1][-1],(i*step)+1)
            lv.append(new)
#        lv.remove([1][0])
        lv[1] = lv[1][1:]
        lv[-1].extend([97,98,99,100])
        self.scale = lv
