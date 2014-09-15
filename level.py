#!/usr/bin/python -u

# duckmaze - a maze game with a duck in it, what can move walls, like.
#
# Copyright (C) 2006-2007 Andy Balaam
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

import os

DIR_UP    = 0
DIR_RIGHT = 1
DIR_DOWN  = 2
DIR_LEFT  = 3

INGAME_ALIVE          = 0
INGAME_FINISHED_LEVEL = 1
INGAME_DEAD           = 2
INGAME_QUIT           = 3
INGAME_WON            = 4

class Level:

	def __init__( self, config, filename_or_level = None ):
		self.config = config

		if filename_or_level == None:
			self.direction = DIR_RIGHT
			self.position = [2, 2]
			self.lines_hor = []
			self.lines_ver = []
			self.total_time = 60
			self.background_colour = self.config.colour_background
			self.text_colour = (255, 255, 255)

			ln = []
			self.lines_hor.append( ln )
			for j in range( 12 ):
				ln.append( 1 )
			for i in range( 1, 8 ):
				ln = []
				self.lines_hor.append( ln )
				for j in range( 12 ):
					ln.append( 0 )
			ln = []
			self.lines_hor.append( ln )
			for j in range( 12 ):
				ln.append( 1 )

			for i in range( 8 ):
				ln = []
				self.lines_ver.append( ln )
				ln.append( 1 )
				for j in range( 1, 12 ):
					ln.append( 0 )
				ln.append( 1 )
		else:
			if isinstance( filename_or_level, str ):
				self.construct_from_file( filename_or_level )
			else:
				self.construct_from_level( filename_or_level )

			self.current_time = self.total_time

	def construct_from_level( self, other ):

		self.direction = other.direction
		self.position = [ other.position[0], other.position[1] ]
		self.lines_hor = []
		self.lines_ver = []
		self.total_time = other.total_time
		self.background_colour = other.background_colour
		self.text_colour = other.text_colour

		for other_ln in other.lines_hor:
			self_ln = []
			self.lines_hor.append( self_ln )
			for other_i in other_ln:
				self_ln.append( other_i )

		for other_ln in other.lines_ver:
			self_ln = []
			self.lines_ver.append( self_ln )
			for other_i in other_ln:
				self_ln.append( other_i )

	def save_to_file( self, filename ):
		fl = file( filename, 'w' )

		fl.write( "time = %d\n" % self.total_time )
		fl.write( "background_colour = (%d, %d, %d)\n"
			% (self.background_colour[0], self.background_colour[1],
			   self.background_colour[2]) )
		fl.write( "text_colour = (%d, %d, %d)\n"
			% (self.text_colour[0], self.text_colour[1], self.text_colour[2] ) )

		for y in range( len( self.lines_ver ) ):
			str_ln = ""
			for n in self.lines_hor[y]:
				if n == 1:
					str_ln += " -"
				else:
					str_ln += "  "
			str_ln += "\n"
			fl.write( str_ln )
			str_ln = ""
			for x in range( len( self.lines_ver[y] ) ):
				n = self.lines_ver[y][x]
				if n == 1:
					str_ln += "|"
				else:
					str_ln += " "
				if y == self.position[1] and x == self.position[0]:
					str_ln += "S"
				else:
					str_ln += " "
			str_ln += "\n"
			fl.write( str_ln )
		str_ln = ""
		for n in self.lines_hor[-1]:
			if n == 1:
				str_ln += " -"
			else:
				str_ln += "  "
		str_ln += "\n"
		fl.write( str_ln )

		fl.flush()
		os.fsync( fl.fileno() )
		fl.close()

	def construct_from_file( self, filename ):

		MODE_CFG = 0
		MODE_HOR = 1
		MODE_VER = 2

		lev_file = file( filename, "r" )

		self.direction = DIR_RIGHT

		self.lines_hor = []
		self.lines_ver = []
		self.position = [ -1, -1 ]
		self.total_time = 60
		self.background_colour = self.config.colour_background
		self.text_colour = (255,255,255)

		line_count = 0

		mode = MODE_CFG
		for ln in lev_file:
			ln = ln[:-1]
			if mode == MODE_CFG:
				split_ln = ln.split( "=" )
				if len( split_ln ) != 2:
					mode = MODE_HOR
				else:
					k = split_ln[0].strip()
					v = self.config.parse_value( split_ln[1] )
					if k == "time":
						self.total_time = v
					elif k == "background_colour":
						self.background_colour = v
					elif k == "text_colour":
						self.text_colour = v
					else:
						print "Unknown level config key: '%s'" % k

			if mode == MODE_HOR:
				hor_line = []
				self.lines_hor.append( hor_line )
				for i in range( 1, self.config.arena_size[0]*2 + 1, 2 ):
					if i < len( ln ) and ln[i] == "-":
						hor_line.append( 1 )
					else:
						hor_line.append( 0 )
				mode = MODE_VER
			elif mode == MODE_VER:
				ver_line = []
				self.lines_ver.append( ver_line )
				chmd = 1
				for i in range( 0, self.config.arena_size[0]*2 + 1, 1 ):
					if i < len( ln ):
						ch = ln[i]
					else:
						ch = " "
					if chmd == 1:
						if ch == "|":
							ver_line.append( 1 )
						else:
							ver_line.append( 0 )
						chmd = 0
					else:
						if ch == "S":
							self.position = [ int( (i-1)/2 ), line_count ]
						chmd = 1
				line_count += 1
				mode = MODE_HOR

		if( len( self.lines_hor ) != self.config.arena_size[1] + 1 ):
			 msg = "Level file '%s' is invalid: it is the wrong size ( %d )"
			 msg %= ( filename, len( self.lines_hor ) )
			 raise Exception( msg )

		if self.position == [ -1, -1 ]:
			raise Exception( "Level file '%s' is invalid: no start pos found "
			 	+ "(is it in the wrong column?)." % filename )

		lev_file.close()

	def is_wall_at_hor( self, x, y ):
		if( y >= 0 and y < len( self.lines_hor ) and
			x >= 0 and x < len( self.lines_hor[0] ) ):
				return self.lines_hor[y][x] == 1
		else:
			return True

	def is_wall_at_ver( self, x, y ):
		if( y >= 0 and y < len( self.lines_ver ) and
			x >= 0 and x < len( self.lines_ver[0] ) ):
				return self.lines_ver[y][x] == 1
		else:
			return True

	def set_wall_at_hor( self, val, x, y ):
		self.lines_hor[y][x] = val

	def set_wall_at_ver( self, val, x, y ):
		self.lines_ver[y][x] = val

	def move_up( self, gamestate ):
		self.direction = DIR_UP
		if not self.is_wall_at_hor( self.position[0], self.position[1] ):
			self.position[1] -= 1
			self.check_finished( gamestate )
		elif not self.is_wall_at_hor( self.position[0], self.position[1] - 1 ):
			self.set_wall_at_hor( 1, self.position[0], self.position[1] - 1 )
			self.set_wall_at_hor( 0, self.position[0], self.position[1] )

	def move_right( self, gamestate ):
		self.direction = DIR_RIGHT
		if not self.is_wall_at_ver( self.position[0] + 1, self.position[1] ):
			self.position[0] += 1
			self.check_finished( gamestate )
		elif not self.is_wall_at_ver( self.position[0] + 2, self.position[1] ):
			self.set_wall_at_ver( 1, self.position[0] + 2, self.position[1] )
			self.set_wall_at_ver( 0, self.position[0] + 1, self.position[1] )

	def move_down( self, gamestate ):
		self.direction = DIR_DOWN
		if not self.is_wall_at_hor( self.position[0], self.position[1] + 1 ):
			self.position[1] += 1
			self.check_finished( gamestate )
		elif not self.is_wall_at_hor( self.position[0], self.position[1] + 2 ):
			self.set_wall_at_hor( 1, self.position[0], self.position[1] + 2 )
			self.set_wall_at_hor( 0, self.position[0], self.position[1] + 1 )

	def move_left( self, gamestate ):
		self.direction = DIR_LEFT
		if not self.is_wall_at_ver( self.position[0], self.position[1] ):
			self.position[0] -= 1
			self.check_finished( gamestate )
		elif not self.is_wall_at_ver( self.position[0] - 1, self.position[1] ):
			self.set_wall_at_ver( 1, self.position[0] - 1, self.position[1] )
			self.set_wall_at_ver( 0, self.position[0], self.position[1] )

	def move_again( self, gamestate ):
		if self.direction == DIR_UP:
			self.move_up( gamestate )
		elif self.direction == DIR_RIGHT:
			self.move_right( gamestate )
		elif self.direction == DIR_DOWN:
			self.move_down( gamestate )
		elif self.direction == DIR_LEFT:
			self.move_left( gamestate )

	def check_finished( self, gamestate ):
		if( self.position[0] < 0 or
			self.position[0] >= len( self.lines_ver[0] ) - 1 or
			self.position[1] < 0 or
			self.position[1] >= len( self.lines_ver )  ):
				gamestate.alive = INGAME_FINISHED_LEVEL


