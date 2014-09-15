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

import pygame, sys, re, os, math
from pygame.locals import *
from mopelib import mopelib
import level

MENU_CONTINUE = 1
MENU_NEW      = 2
MENU_LOAD     = 3
MENU_SAVE     = 4
MENU_RETURN   = 5
MENU_QUIT     = 6

EVENTTYPE_MOVE = pygame.USEREVENT

MOVE_TICK_TIME = 150

CURS_HOR = 0
CURS_VER = 1

MENU_TITLE_TEXT = "duckmaze level editor"

# ---------------------

class LevelEditor:

	def __init__( self, config, screen, sound_mgr ):
		self.config = config
		self.screen = screen
		self.sound_mgr = sound_mgr

		if config.edit_real_levels == 1:
			self.level_name_str = "level"
		else:
			self.level_name_str = "custom"

		self.custom_level_re = re.compile(
			"%s_(\\d\\d\\d)" % self.level_name_str )

		self.surface_background = pygame.Surface( screen.get_size() ).convert()
		self.surface_background.fill( ( 255, 255, 255 ) )

		self.menurender = mopelib.MenuRenderer( screen, config,
			self.surface_background, (0, 0, 0), (200, 200, 200), (75, 75, 75) )

		self.direction = level.DIR_RIGHT
		self.cursor = [ 5, 5 ]
		self.cursvh = CURS_VER
		self.curs_edge_x = False
		self.curs_edge_y = False

		self.screen_border = 50

		self.scale = ( ( self.config.screen_size[0] - self.screen_border*2 ) /
						self.config.arena_size[0],
					 ( self.config.screen_size[1] - self.screen_border*2 ) /
					 	(self.config.arena_size[1]+1) )

		self.last_filename = ""

	# ----------------------

	def mainloop( self ):

		pygame.mouse.set_visible( True )

		self.level = None
		self.menu = mopelib.Menu()

		self.menu_screen()

		if self.level != None:
			self.editor_screen()

		pygame.mouse.set_visible( False )


	# ----------------------

	def editor_screen( self ):
		self.editor_redraw_screen()
		while self.level:
			self.editor_input( pygame.event.wait() )

	def editor_input( self, event ):
		if event.type == QUIT:
			sys.exit(0)
		elif self.config.keys_menu.matches( event ):
			self.menu_screen()
			if self.level != None:
				self.editor_redraw_screen()
		elif self.config.keys_volup.matches( event ):
			self.config.volume = self.sound_mgr.increase_volume()
			self.config.save()
		elif self.config.keys_voldown.matches( event ):
			self.config.volume = self.sound_mgr.decrease_volume()
			self.config.save()
		elif self.config.keys_editor_placewall.matches( event ):
			x = self.cursor[0]
			y = self.cursor[1]
			if self.cursvh == CURS_HOR:
				self.level.lines_hor[y][x] = 1 - self.level.lines_hor[y][x]
				self.editor_redraw_lines( ( (CURS_HOR,(x,y)), ) )
			else:
				self.level.lines_ver[y][x] = 1 - self.level.lines_ver[y][x]
				self.editor_redraw_lines( ( (CURS_VER,(x,y)), ) )

		elif self.config.keys_editor_placestart.matches( event ):
			if event.type == MOUSEBUTTONDOWN:
				self.editor_move_mouse( event )
			oldpos = self.level.position
			self.level.position = [ self.cursor[0], self.cursor[1] ]
			if self.level.position[0] >= self.config.arena_size[0]:
				self.level.position[0] = self.config.arena_size[0] - 1
			if self.level.position[1] > self.config.arena_size[1] - 1:
				self.level.position[1] = self.config.arena_size[1] - 1
			self.editor_move_position( oldpos, self.level.position )
		elif event.type == EVENTTYPE_MOVE:
			self.move_again()
		elif event.type == MOUSEMOTION:
			self.editor_move_mouse( event )
		else:
			if self.config.keys_editor_left.matches( event ):
				self.move_left()
				pygame.time.set_timer( EVENTTYPE_MOVE, MOVE_TICK_TIME )
			elif self.config.keys_editor_right.matches( event ):
				self.move_right()
				pygame.time.set_timer( EVENTTYPE_MOVE, MOVE_TICK_TIME )
			elif self.config.keys_editor_up.matches( event ):
				self.move_up()
				pygame.time.set_timer( EVENTTYPE_MOVE, MOVE_TICK_TIME )
			elif self.config.keys_editor_down.matches( event ):
				self.move_down()
				pygame.time.set_timer( EVENTTYPE_MOVE, MOVE_TICK_TIME )
			elif(
				( self.direction == level.DIR_LEFT and
				  self.config.keys_editor_left_release.matches( event ) ) or
				( self.direction == level.DIR_RIGHT and
				  self.config.keys_editor_right_release.matches( event ) ) or
				( self.direction == level.DIR_UP and
				  self.config.keys_editor_up_release.matches( event ) ) or
				( self.direction == level.DIR_DOWN and
				  self.config.keys_editor_down_release.matches( event ) ) ):
					mopelib.clear_events( EVENTTYPE_MOVE )

	def editor_move_mouse( self, event ):

		oldcursvh = self.cursvh
		oldcurs = ( self.cursor[0], self.cursor[1] )

		arena_pos_hor = [ float( event.pos[0] - self.screen_border ) /
							self.scale[0] - 0.5,
						 (float( event.pos[1] - self.screen_border ) /
							self.scale[1]) ]

		arena_pos_ver = [ float( event.pos[0] - self.screen_border ) /
							self.scale[0],
						 (float( event.pos[1] - self.screen_border ) /
							self.scale[1] - 0.5) ]

		dist_from_ver = abs( arena_pos_ver[0]-round(arena_pos_ver[0]) )
		dist_from_hor = abs( arena_pos_hor[1]-round(arena_pos_hor[1]) )

		# Decide whether the cursor is vertical or horizontal:
		# if we are near an edge, put it on the edge.  Otherwise,
		# if we are not too close to the currently-selected orientation,
		# decide based on which gridline we are closest to.
		if( arena_pos_hor[1] > self.config.arena_size[1] + 1 or
		  arena_pos_hor[1] < 0 ):
			self.cursvh = CURS_HOR
		elif( arena_pos_ver[0] > self.config.arena_size[0] or
		  arena_pos_ver[0] < 0 ):
			self.cursvh = CURS_VER
		elif( self.cursvh == CURS_VER and
		  dist_from_ver > 0.2 and
		  dist_from_ver > dist_from_hor ):
			self.cursvh = CURS_HOR
		elif( self.cursvh == CURS_HOR and
		  dist_from_hor > 0.2 and
		  dist_from_hor > dist_from_ver ):
			self.cursvh = CURS_VER

		if self.cursvh == CURS_HOR:
			if arena_pos_hor[0] < 0:
				arena_pos_hor[0] = 0
			elif arena_pos_hor[0] >= self.config.arena_size[0] - 1:
				arena_pos_hor[0] = self.config.arena_size[0] - 1

			if arena_pos_hor[1] < 0:
				arena_pos_hor[1] = 0
			elif arena_pos_hor[1] > self.config.arena_size[1]:
				arena_pos_hor[1] = self.config.arena_size[1]

			self.cursor = [ int(round(arena_pos_hor[0])),
				int(round(arena_pos_hor[1])) ]

		else:
			if arena_pos_ver[0] < 0:
				arena_pos_ver[0] = 0
			elif arena_pos_ver[0] > self.config.arena_size[0]:
				arena_pos_ver[0] = self.config.arena_size[0]

			if arena_pos_ver[1] < 0:
				arena_pos_ver[1] = 0
			elif arena_pos_ver[1] > self.config.arena_size[1] - 1:
				arena_pos_ver[1] = self.config.arena_size[1] - 1

			self.cursor = [ int(round(arena_pos_ver[0])),
				int(round(arena_pos_ver[1])) ]

		self.editor_redraw_lines( ( (oldcursvh, oldcurs),
			(self.cursvh, self.cursor) ) )

	def pos_coords_to_screen( self, pos ):
		return ( int( self.screen_border + self.scale[0]
					* ( pos[0] + 0.55 ) ),
				 int( self.screen_border + self.scale[1]
					* ( pos[1] + 0.55 ) ) )

	def editor_draw_pos( self, pos, maze_colour, duck_size, duck_size_large=0 ):
		duck_colour = self.config.colour_duck

		duck_pos = self.pos_coords_to_screen( pos )

		pygame.draw.circle( self.screen, duck_colour, duck_pos, duck_size )
		pygame.draw.circle( self.screen, maze_colour, duck_pos,
			duck_size+1, 1 )

		lev = self.level

		if lev.direction == level.DIR_UP:
			end_pos_inc = ( 0, -duck_size )
		elif lev.direction == level.DIR_RIGHT:
			end_pos_inc = ( duck_size, 0 )
		elif lev.direction == level.DIR_DOWN:
			end_pos_inc = ( 0, duck_size )
		elif lev.direction == level.DIR_LEFT:
			end_pos_inc = ( -duck_size, 0 )

		pygame.draw.line( self.screen, maze_colour, duck_pos,
			( duck_pos[0] + end_pos_inc[0], duck_pos[1] + end_pos_inc[1] ) )

		rect = ( 0, 0, 0, 0 )
		if duck_size_large != 0:
			rect = ( duck_pos[0] - duck_size_large,
					 duck_pos[1] - duck_size_large,
					 duck_size_large*2, duck_size_large*2 )

		return rect

	def editor_move_position( self, oldpos, newpos ):
		dirty_rects = []
		duck_size = int( self.scale[1] * 0.3 )
		duck_size_large = int( self.scale[1] * 0.35 )
		maze_colour = self.config.colour_maze

		old_middle = self.pos_coords_to_screen( oldpos )
		old_rect = ( old_middle[0] - duck_size_large,
					 old_middle[1] - duck_size_large,
					 duck_size_large*2, duck_size_large*2 )

		self.screen.blit( self.surface_background, old_rect, old_rect )
		dirty_rects.append( old_rect )

		dirty_rects.append( self.editor_draw_pos( newpos, maze_colour,
			duck_size, duck_size_large ) )

		pygame.display.update( dirty_rects )

	def editor_redraw_lines( self, lines_to_draw ):
		dirty_rects = []
		maze_colour = self.config.colour_maze

		for line in lines_to_draw:
			vh = line[0]
			pos = line[1]

			if vh == CURS_HOR:
				rect = self.editor_redraw_line_hor( pos, maze_colour, True )
			else:
				rect = self.editor_redraw_line_ver( pos, maze_colour, True )

			dirty_rects.append( rect )

		pygame.display.update( dirty_rects )

	def editor_redraw_screen( self ):
		maze_colour = self.config.colour_maze

		self.screen.blit( self.surface_background, (0,0) )

		lev = self.level
		for y in range( len( lev.lines_hor ) ):
			for x in range( len( lev.lines_hor[y] ) ):
				self.editor_redraw_line_hor( (x,y), maze_colour )

		for y in range( len( lev.lines_ver ) ):
			for x in range( len( lev.lines_ver[y] ) ):
				self.editor_redraw_line_ver( (x,y), maze_colour )

		if( lev.position[0] >=0 and
		  lev.position[0] < self.config.arena_size[0] and
		  lev.position[1] >=0 and
		  lev.position[1] <= self.config.arena_size[1] ):
			duck_size = int( self.scale[1] * 0.3 )
			self.editor_draw_pos( lev.position, maze_colour, duck_size )

		#write_text_ingame( gamestate )

		pygame.display.update()

	# ------------------

	def editor_redraw_line_hor( self, pos, maze_colour, blank_bg = False ):
		isaline = self.level.lines_hor[pos[1]][pos[0]]
		rect = ( self.screen_border + self.scale[0] * (pos[0] + 0.1),
				 self.screen_border + self.scale[1] * pos[1],
				 math.ceil( self.scale[0] * 0.92 ),
				 math.ceil( self.scale[1] * 0.1 ) )
		curs = ( self.cursvh == CURS_HOR and self.cursor[0] == pos[0]
			and self.cursor[1] == pos[1] )
		if isaline == 1:
			if curs:
				pygame.draw.rect( self.screen, (150,150,150), rect )
				pygame.draw.rect( self.screen, (250,0,0), rect, 1 )
			else:
				pygame.draw.rect( self.screen, maze_colour, rect )
		else:
			if blank_bg:
				self.screen.blit( self.surface_background, rect, rect )
			if curs:
				pygame.draw.rect( self.screen, (100,200,100), rect, 1 )

		return rect

	# ------------------

	def editor_redraw_line_ver( self, pos, maze_colour, blank_bg = False ):
		isaline = self.level.lines_ver[pos[1]][pos[0]]
		rect = ( self.screen_border + self.scale[0] * pos[0],
				 self.screen_border + self.scale[1] * (pos[1] + 0.1),
				 math.ceil( self.scale[0] * 0.1 ),
				 math.ceil( self.scale[1] * 0.92 ) )
		curs = ( self.cursvh == CURS_VER and self.cursor[0] == pos[0]
			and self.cursor[1] == pos[1] )
		if isaline == 1:
			if curs:
				pygame.draw.rect( self.screen, (150,150,150), rect )
				pygame.draw.rect( self.screen, (250,0,0), rect, 1 )
			else:
				pygame.draw.rect( self.screen, maze_colour, rect )
		else:
			if blank_bg:
				self.screen.blit( self.surface_background, rect, rect )
			if curs:
				pygame.draw.rect( self.screen, (100,200,100), rect, 1 )
		return rect

	# ------------------

	def move_again( self ):
		if self.direction == level.DIR_UP:
			self.move_up()
		elif self.direction == level.DIR_RIGHT:
			self.move_right()
		elif self.direction == level.DIR_DOWN:
			self.move_down()
		elif self.direction == level.DIR_LEFT:
			self.move_left()

	def move_up( self ):
		oldcursvh = self.cursvh
		oldcurs = ( self.cursor[0], self.cursor[1] )

		self.direction = level.DIR_UP
		if self.cursvh == CURS_HOR:
			if self.cursor[1] > 0:
				self.cursvh = CURS_VER
				self.cursor[1] = self.cursor[1] - 1
				if self.curs_edge_x:
					self.cursor[0] = self.cursor[0] + 1
				self.curs_edge_x = False
		else:
			if self.cursor[0] >= self.config.arena_size[0]:
				self.cursor[0] = self.config.arena_size[0] - 1
				self.curs_edge_x = True
			self.cursvh = CURS_HOR

		self.editor_redraw_lines( ( (oldcursvh, oldcurs),
			(self.cursvh, self.cursor) ) )

	def move_right( self ):
		oldcursvh = self.cursvh
		oldcurs = ( self.cursor[0], self.cursor[1] )

		self.direction = level.DIR_RIGHT
		if self.cursvh == CURS_HOR:
			if self.cursor[1] > self.config.arena_size[1] - 1:
				self.cursor[1] = self.config.arena_size[1] - 1
				self.curs_edge_y = True
			if self.cursor[0] < self.config.arena_size[0]:
				self.cursvh = CURS_VER
				self.cursor[0] = self.cursor[0] + 1
		else:
			if self.cursor[0] < self.config.arena_size[0]:
				self.cursvh = CURS_HOR
				if self.curs_edge_y:
					self.cursor[1] = self.cursor[1] + 1
				self.curs_edge_y = False

		self.editor_redraw_lines( ( (oldcursvh, oldcurs),
			(self.cursvh, self.cursor) ) )

	def move_down( self ):
		oldcursvh = self.cursvh
		oldcurs = ( self.cursor[0], self.cursor[1] )

		self.direction = level.DIR_DOWN
		if self.cursvh == CURS_VER:
			if self.cursor[0] >= self.config.arena_size[0]:
				self.cursor[0] = self.config.arena_size[0] - 1
				self.curs_edge_x = True
			if self.cursor[1] < self.config.arena_size[1] + 1:
				self.cursvh = CURS_HOR
				self.cursor[1] = self.cursor[1] + 1
		else:
			if self.cursor[1] < self.config.arena_size[1]:
				self.cursvh = CURS_VER
				if self.curs_edge_x:
					self.cursor[0] = self.cursor[0] + 1
				self.curs_edge_x = False

		self.editor_redraw_lines( ( (oldcursvh, oldcurs),
			(self.cursvh, self.cursor) ) )

	def move_left( self ):
		oldcursvh = self.cursvh
		oldcurs = ( self.cursor[0], self.cursor[1] )

		self.direction = level.DIR_LEFT
		if self.cursvh == CURS_VER:
			if self.cursor[0] > 0:
				self.cursvh = CURS_HOR
				self.cursor[0] = self.cursor[0] - 1
				if self.curs_edge_y:
					self.cursor[1] = self.cursor[1] + 1
				self.curs_edge_y = False
		else:
			if self.cursor[1] > self.config.arena_size[1] - 1:
				self.cursor[1] = self.config.arena_size[1] - 1
				self.curs_edge_y = True
			self.cursvh = CURS_VER

		self.editor_redraw_lines( ( (oldcursvh, oldcurs),
			(self.cursvh, self.cursor) ) )

	# ----------------------

	def menu_screen( self ):
		self.menu_create_menu()
		self.menurender.set_menu( self.menu, MENU_TITLE_TEXT )
		self.menurender.repaint_full()

		waiting = True
		while waiting:
			event = pygame.event.wait()
			if event.type == QUIT:
				sys.exit(0)
			elif self.config.keys_menu.matches( event ):
				waiting = False
			elif self.config.keys_editor_down.matches( event ):
				self.menurender.move_down()
			elif self.config.keys_editor_up.matches( event ):
				self.menurender.move_up()
			elif self.config.keys_return.matches( event ):
				code = self.menu.get_selected_item().code
				if code == MENU_CONTINUE:
					waiting = False
				elif code == MENU_NEW:
					self.level = level.Level( self.config )
					waiting = False
				elif code == MENU_LOAD:
					filename = self.choose_level(
						"Choose a level to load", False )
					if filename != "":
						self.last_filename = filename
						self.level = level.Level( self.config, os.path.join(
							self.config.install_dir, "levels", filename ) )
						waiting = False
					else:
						self.menurender.set_menu( self.menu, MENU_TITLE_TEXT )
						self.menurender.repaint_full()
				elif code == MENU_SAVE:
					filename = self.choose_level(
						"Choose a level to save as", True )
					if filename != "":
						self.last_filename = filename
						self.level.save_to_file( os.path.join(
							self.config.install_dir, "levels", filename ) )
						waiting = False
					else:
						self.menurender.set_menu( self.menu, MENU_TITLE_TEXT )
						self.menurender.repaint_full()
				elif code == MENU_RETURN:
					self.level = None
					waiting = False
				elif code == MENU_QUIT:
					sys.exit(0)


	# ----------------------

	def choose_level( self, txt, save ):
		mn = mopelib.Menu()

		levs = []
		levels_dir = os.path.join( self.config.install_dir, "levels" )

		files = os.listdir( levels_dir )
		for f in files:
			m = self.custom_level_re.match( f )
			if m:
				levs.append( int( m.group(1) ) )

		levs.sort()

		old_l = 0
		for l in levs:
			if l != old_l + 1:
				levs = levs[:l]
				break
			old_l = l

		if save:
			levs.append( len( levs ) + 1 )

		#if len( levs ) < 7:
		if save:
			for l in levs[:-1]:
				mn.add_item( "%s_%03d" % ( self.level_name_str, l ), l )
			mn.add_item( "%s_%03d (new)"
				% ( self.level_name_str, len(levs) ), len(levs) )
		else:
			for l in levs:
				mn.add_item( "%s_%03d" % ( self.level_name_str, l ), l )
		if self.last_filename != "":
			mn.set_selected_item( self.last_filename )

		chosen_filename = ""
		if len( levs ) > 0:
			self.menurender.set_menu( mn, txt )
			self.menurender.repaint_full()

			waiting = True
			while waiting:
				event = pygame.event.wait()
				if event.type == QUIT:
					sys.exit(0)
				elif self.config.keys_menu.matches( event ):
					waiting = False
				elif self.config.keys_editor_down.matches( event ):
					self.menurender.move_down()
				elif self.config.keys_editor_up.matches( event ):
					self.menurender.move_up()
				elif self.config.keys_return.matches( event ):
					chosen_filename = ( "%s_%03d"
						% ( self.level_name_str, mn.get_selected_item().code ) )
					waiting = False

		return chosen_filename

	# ----------------------

	def menu_create_menu( self ):
		self.menu.items = []

		if self.level != None:
			self.menu.add_item( "Continue editing", MENU_CONTINUE )
		self.menu.add_item( "Create new level",     MENU_NEW )
		self.menu.add_item( "Load level",           MENU_LOAD )
		if self.level != None:
			self.menu.add_item( "Save level",       MENU_SAVE )
		self.menu.add_item( "Return to duckmaze",   MENU_RETURN )
		self.menu.add_item( "Quit duckmaze",        MENU_QUIT )

		self.menu.selected_index = 0

	# ----------------------


