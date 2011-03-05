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

import os
import math
import time
import random
import cairo
import logging
import rrdtool
from tools import Pallete




class Node:
    ''' Node (device) on a map '''
    def __init__(self, x=0, y=0, color='#ffffff', fontcolor='#000000',
                 fontbgcolor='#FFFFFF', fontsize=11, padding=1, label=None,
                 **kwargs):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.fontcolor = fontcolor
        self.fontbgcolor = fontbgcolor
        self.fontsize = fontsize
        self.padding = padding
        self.label = label
        self.points = None
        self.kwargs = kwargs


class Link:
    ''' A line between two Nodes. The line contains two arrows: one for an input
    value and one for an output value'''
    def __init__(self, nodea, nodeb, bandwidth, width=3, rrdfile=None,
                 colors=None, debug=False, **kwargs):
        self.nodea = nodea
        self.nodeb = nodeb
        self.bandwidth = bandwidth
        self.width = float(width)
        self.pallete = Pallete(colors)
        if debug:
            self.DEBUG = debug
        else:
            self.DEBUG = None
        # creating a rrdfile if it is does not exist
        if rrdfile is None:
            self.rrdfile = self._generate_rrd()
        else:
            self.rrdfile = rrdfile
        
        # fetching data from rrdfile
        self.__rrd_data = self._fetch_rrd_data()

        # fetching input
        self.input = self.__rrd_data[2][0][0]
        if self.input is None:
            self.input = 0

        # fetching output
        self.output = self.__rrd_data[2][0][1]
        if self.output is None:
            self.output = 0

        # defining arrows colors
        self.incolor = None
        self.outcolor = None

        # fetching colors
        self._fill_color()

        self.input_points = self._get_input_arrow_points()
        self.output_points = self._get_output_arrow_points()
        self.kwargs = kwargs

    def _middle(self,x,y):
        ''' Return a middle point coordinate between 2 given points '''
        return x+(y-x)/2

    def _newx(self,a,b,x,y):
        ''' Calculate "x" coordinate '''
        return math.cos(math.atan2(y,x) + math.atan2(b,a))*math.sqrt(x*x+y*y)

    def _newy(self,a,b,x,y):
        ''' Calculate "y" coordinate '''
        return math.sin(math.atan2(y,x) + math.atan2(b,a))*math.sqrt(x*x+y*y)

    def _generate_rrd(self):
        '''
        Create rrd file if rrdfile is None
        '''
        stime = int(time.time()) - 1 * 86400
        dpoints = 288
        etime = stime + (dpoints * 300)
        fname = os.path.join(os.path.abspath(os.path.dirname('./')), 
                             'test.rrd')
        rrdtool.create('test.rrd' ,
                '--start' , str(stime) ,
                "DS:input:COUNTER:600:U:U",
                "DS:output:COUNTER:600:U:U",
                "RRA:AVERAGE:0.5:1:600",
                "RRA:AVERAGE:0.5:6:700",
                "RRA:AVERAGE:0.5:24:775",
                "RRA:AVERAGE:0.5:288:797",
                "RRA:MAX:0.5:1:600",
                "RRA:MAX:0.5:6:700",
                "RRA:MAX:0.5:24:775",
                "RRA:MAX:0.5:444:797",)
        ctime = stime
        input = 0
        output = 0
        for i in xrange(dpoints):
            input += random.randrange(self.bandwidth / 2, self.bandwidth +
                                      self.bandwidth * 2) * 100
            output += random.randrange(self.bandwidth / 2, self.bandwidth +
                                       self.bandwidth * 2) * 100
            ctime += 300
            rrdtool.update(fname , '%d:%d:%d' % (ctime , input, output))
        return os.path.join(os.path.abspath(os.path.dirname('./')), "test.rrd")
    
    def _fetch_rrd_data(self):
        '''
        Fetch input, output data from the rrd file
        '''
        logging.debug('RRD_PATH: %s',self.rrdfile)
        data = rrdtool.fetch(self.rrdfile, 'AVERAGE', '-r', '300', '-s','-300')
        return data

    def _fill_color(self):
        '''
        Set color for the input and output values
        '''
        input = (self.input/self.bandwidth)*100
        output = (self.output/self.bandwidth)*100
        
        if input > 100:
            input = 100

        if output > 100:
            output = 100

        if 1 > input > 0:
            input = 1

        if 1 > output > 0:
            output = 1

        input = int(input)
        output = int(output)

        for level in self.pallete.scale:
            if input in level:
                cindexb = self.pallete.scale.index(level)
                self.incolor = self.pallete.colors[cindexb]

                if self.DEBUG:
                    logging.info('INPUT: Value: %s, index: %s, Color: %s' %
                                 (input, self.pallete.scale.index(level),
                                 self.pallete.colors[cindexb]))

            if output in level:
                cindexa = self.pallete.scale.index(level)
                self.outcolor = self.pallete.colors[cindexa]

                if self.DEBUG:
                    logging.info('OUTPUT: Value: %s, index: %s, Color: %s' %
                                 (output, self.pallete.scale.index(level),
                                  self.pallete.colors[cindexa]))
        
        if self.DEBUG:
            logging.info('COLORS: In: %s|%s, Out: %s|%s' %
                         (self.incolor,input,self.outcolor,output))

    def _get_arrow_points(self,x1,y1,x2,y2,width):
        '''
        Calculate points of an arrow
        @param x1: x of first point 
        @param y1: y of first point
        @param x2: x of second point
        @param y2: y of second point
        @param width: width of arrow
        '''
        points = [(x1+self._newx(x2-x1,y2-y1,0,width),
                  y1+self._newy(x2-x1,y2-y1,0,width)),
                  
                  (x2+self._newx(x2-x1,y2-y1,-4*width,width),
                  y2+self._newy(x2-x1,y2-y1,-4*width,width)),
                  
                  (x2+self._newx(x2-x1,y2-y1,-4*width,2*width),
                  y2+self._newy(x2-x1,y2-y1,-4*width,2*width)),
                  
                  (x2,y2),
                  
                  (x2+self._newx(x2-x1,y2-y1,-4*width,-2*width),
                  y2+self._newy(x2-x1,y2-y1,-4*width,-2*width)),
                  
                  (x2+self._newx(x2-x1,y2-y1,-4*width,-width),
                  y2+self._newy(x2-x1,y2-y1,-4*width,-width)),
                  
                  (x1+self._newx(x2-x1,y2-y1,0,-width),
                  y1+self._newy(x2-x1,y2-y1,0,-width))]
        return points

    def _get_input_arrow_points(self):
        '''
        Calculating points of the input arrow
        '''
        if self.DEBUG:
            logging.info("Calculating Polygon points for Node %s" %
                         self.nodea.label)
        points = self._get_arrow_points(
                self.nodea.x,
                self.nodea.y,
                self._middle(self.nodea.x,self.nodeb.x),
                self._middle(self.nodea.y,self.nodeb.y),
                self.width,
                )
        return points

    def _get_output_arrow_points(self):
        '''
        Calculating points of the output arrow
        '''
        if self.DEBUG:
            logging.info("Calculating Polygon points for Node %s" %
                         self.nodeb.label)
        points = self._get_arrow_points(
                self.nodeb.x,
                self.nodeb.y,
                self._middle(self.nodeb.x,self.nodea.x),
                self._middle(self.nodeb.y,self.nodea.y),
                self.width,
                )
        return points


class Map:
    def __init__(self,links,image=None):
        self.links = links # Link instance
        self.image = image
        self.surface = self.__surface()
        self.context = self.__context()
        self.nodes = self._nodes()

    def _hex_to_rgb(self,c):
        '''
        Convert hex color to a rgb format
        @param c: color
        '''
        c = int(c.replace('#','0x'),16)
        return [(c >> 16)/255.0,(255 & (c >> 8))/255.0,(255 & c)/255.0]

    def __surface(self):
        ''' Load a surface. If a surface is None, 
        create a new 640x480 image with a white background '''
        if self.image is None:
            img = cairo.ImageSurface(cairo.FORMAT_RGB24,640,480)
        else:
            img = cairo.ImageSurface.create_from_png(self.image)
        return img

    def __context(self):
        '''
        Create Context() instance and fill bg by a white color
        @param image: image
        '''
        context = cairo.Context(self.surface)
        if self.image is None:
            context.set_source_rgb(1,1,1)
            context.paint()
        return context

    def _nodes(self):
        '''
        Return all nodes
        '''
        node_list = []
        for link in self.links:
            if link.nodea not in node_list:
                node_list.append(link.nodea)
            if link.nodeb not in node_list:
                node_list.append(link.nodeb)
        return node_list

    def _draw_polygon(self,points,width,color):
        '''
        Draw the polygon (the arrow) for giving points
        @param points: list of points
        @param width: polygon width
        @param color: inside color of polygon (arrow)
        '''
        self.context.move_to(points[0][0],points[0][1])
        for i in range(0,len(points)):
            self.context.line_to(points[i][0],points[i][1])
        self.context.close_path()
        self.context.set_line_width(width-2)
        border_color = self._hex_to_rgb('#1C1C1C')
        self.context.set_source_rgb(border_color[0],border_color[1],
                                    border_color[2])
        self.context.stroke_preserve()
        color = self._hex_to_rgb(color)
        self.context.set_source_rgb(color[0],color[1],color[2])
        self.context.fill()
        logging.info("color inside: %s, color outside: %s" % (color,
                                                              border_color))

    def _name(self,x,y,label,width=3,padding=1,font=None,size=10,bold=False,
              color='#000000',bgcolor='#FFFFFF'):
        '''
        Draw Node Label
        @param x: x coordinate of a Node
        @param y: y coordinate of a Node
        @param label: Node label
        @param padding: label padding
        @param font: font family, default is sans-serif
        @param size: font size
        @param bold: text style bold - True\False
        @param color: text color
        @param bgcolor: background color
        
        This method returns coordinates (4 points) of the label box
        
        '''
        # Draw rectangle
        if font is None:
            font = 'sans-serif'
        if bold is True:
            self.context.select_font_face(font,cairo.FONT_SLANT_NORMAL,
                                          cairo.FONT_WEIGHT_BOLD)
        else:
            self.context.select_font_face(font,cairo.FONT_SLANT_NORMAL,
                                          cairo.FONT_WEIGHT_NORMAL)
        self.context.set_font_size(size)
        fhw = self.context.text_extents(label)
        strwidth = fhw[2] + padding * 2 + 2
        strheight = fhw[3] + padding * 2 + 2
        x1 = x-strwidth/2-padding-1
        y1 = y-strheight/2-padding+1
        self.context.rectangle(x1,y1,strwidth,strheight)
        stroke_color = self._hex_to_rgb(color)
        self.context.set_source_rgb(stroke_color[0],stroke_color[1],
                                    stroke_color[2])
        self.context.set_line_width(width-2)
        self.context.stroke_preserve()

        border_color = self._hex_to_rgb(bgcolor)
        self.context.set_source_rgb(border_color[0],border_color[1],
                                    border_color[2])
        self.context.fill()

        self.context.move_to(x-strwidth/2-padding*2+1, y+strheight/2-padding*2)
        text_color = self._hex_to_rgb(color)
        self.context.set_source_rgb(text_color[0], text_color[1], text_color[2])
        self.context.show_text(label)
        points = [(x1,y1),(x1+strwidth,y1),(x1+strwidth,y1+strheight),(x1,y1+strheight)]
        return points

    def draw_grid(self):
        w = self.surface.get_width()
        h = self.surface.get_height()
        
        self.context.set_line_width(0.7)
        self.context.set_dash([2,3.0],0)
        
        for i in xrange(0,h+5,5):
            self.context.move_to(-1,i)
            self.context.line_to(w,i)
        self.context.set_source_rgb(0,0,0)
        self.context.stroke()
        self.context.set_dash([])

    def draw_arrows(self):
        for link in self.links:
            # draw input arrow
            self._draw_polygon(link.input_points, link.width, link.incolor)
            # draw output arrow
            self._draw_polygon(link.output_points, link.width, link.outcolor)

    def draw_labels(self,nodes=None,padding=1):
        ''' Draw labels method'''
        if nodes is not None:
            for node in nodes:
                node.points = self._name(node.x,node.y,node.label, padding=padding,
                color=node.fontcolor, bgcolor=node.fontbgcolor)
        else:
            for node in self.nodes:
                node.points = self._name(node.x, node.y, node.label, padding=node.padding,
                           size=node.fontsize, color=node.fontcolor,
                           bgcolor=node.fontbgcolor)

    def save(self,path):
        '''
        Save the image to the file path
        @param path: path to the file
        '''
        self.surface.write_to_png(str(path))
