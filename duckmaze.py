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

import pygame, os, sys, random, gc, md5
from pygame.locals import *
from mopelib import mopelib
import level_editor
import level
#import time


# ----------------------
class DuckMazeConfig( mopelib.Config ):

	def default_config( self ):
		self.colour_duck = ( 255, 255, 0 )
		self.colour_background = ( 170, 179, 235 )
		self.colour_maze = ( 32, 32, 32 )

		self.levels_unlocked = 1
		self.start_level = 0

		self.screen_size = ( 640, 480 )

		self.volume = 50

		self.music_on = 1
		self.sound_effects_on = 1
		self.edit_real_levels = 0

		self.keys_menu = mopelib.MyInputEvent( "Escape" )
		self.keys_menu.add( pygame.KEYDOWN, pygame.K_ESCAPE )
		self.keys_menu.add( pygame.JOYBUTTONDOWN, 8 )	# GP2X Start
		self.keys_menu.add( pygame.JOYBUTTONDOWN, 9 )	# GP2X Select

		self.keys_return = mopelib.MyInputEvent( "Return" )
		self.keys_return.add( pygame.KEYDOWN, pygame.K_RETURN )
		self.keys_return.add( pygame.JOYBUTTONDOWN, 13 )	# GP2X B button

		self.keys_startgame = mopelib.MyInputEvent( "any key" )
		self.keys_startgame.add_all( pygame.KEYDOWN )
		self.keys_startgame.add_all( pygame.JOYBUTTONDOWN )
		self.keys_startgame.add_all( pygame.MOUSEBUTTONDOWN )

		self.keys_up = mopelib.MyInputEvent( "up" )
		self.keys_up.add( pygame.KEYDOWN, ord( 'q' ) )
		self.keys_up.add( pygame.KEYDOWN, pygame.K_UP )
		self.keys_up.add( pygame.JOYBUTTONDOWN, 0 )		# GP2X Joy up
		self.keys_up.add( pygame.JOYBUTTONDOWN, 15 )	# GP2X Y button

		self.keys_right = mopelib.MyInputEvent( "right" )
		self.keys_right.add( pygame.KEYDOWN, ord( 'p' ) )
		self.keys_right.add( pygame.KEYDOWN, pygame.K_RIGHT )
		self.keys_right.add( pygame.JOYBUTTONDOWN, 6 )	# GP2X Joy right
		self.keys_right.add( pygame.JOYBUTTONDOWN, 13 )	# GP2X B button

		self.keys_down = mopelib.MyInputEvent( "down" )
		self.keys_down.add( pygame.KEYDOWN, ord( 'a' ) )
		self.keys_down.add( pygame.KEYDOWN, pygame.K_DOWN )
		self.keys_down.add( pygame.JOYBUTTONDOWN, 4 )	# GP2X Joy down
		self.keys_down.add( pygame.JOYBUTTONDOWN, 14 )	# GP2X X button

		self.keys_left = mopelib.MyInputEvent( "left" )
		self.keys_left.add( pygame.KEYDOWN, ord( 'o' ) )
		self.keys_left.add( pygame.KEYDOWN, pygame.K_LEFT )
		self.keys_left.add( pygame.JOYBUTTONDOWN, 2 )	# GP2X Joy left
		self.keys_left.add( pygame.JOYBUTTONDOWN, 12 )	# GP2X A button

		self.keys_up_release = mopelib.MyInputEvent( "up_release" )
		self.keys_up_release.add( pygame.KEYUP, ord( 'q' ) )
		self.keys_up_release.add( pygame.KEYUP, pygame.K_UP )
		self.keys_up_release.add( pygame.JOYBUTTONUP, 0 )		# GP2X Joy up
		self.keys_up_release.add( pygame.JOYBUTTONUP, 15 )	# GP2X Y button

		self.keys_right_release = mopelib.MyInputEvent( "right_release" )
		self.keys_right_release.add( pygame.KEYUP, ord( 'p' ) )
		self.keys_right_release.add( pygame.KEYUP, pygame.K_RIGHT )
		self.keys_right_release.add( pygame.JOYBUTTONUP, 6 )	# GP2X Joy right
		self.keys_right_release.add( pygame.JOYBUTTONUP, 13 )	# GP2X B button

		self.keys_down_release = mopelib.MyInputEvent( "down_release" )
		self.keys_down_release.add( pygame.KEYUP, ord( 'a' ) )
		self.keys_down_release.add( pygame.KEYUP, pygame.K_DOWN )
		self.keys_down_release.add( pygame.JOYBUTTONUP, 4 )	# GP2X Joy down
		self.keys_down_release.add( pygame.JOYBUTTONUP, 14 )	# GP2X X button

		self.keys_left_release = mopelib.MyInputEvent( "left_release" )
		self.keys_left_release.add( pygame.KEYUP, ord( 'o' ) )
		self.keys_left_release.add( pygame.KEYUP, pygame.K_LEFT )
		self.keys_left_release.add( pygame.JOYBUTTONUP, 2 )	# GP2X Joy left
		self.keys_left_release.add( pygame.JOYBUTTONUP, 12 )	# GP2X A button

		self.keys_volup = mopelib.MyInputEvent( "+" )
		self.keys_volup.add( pygame.KEYDOWN, ord( '+' ) )
		self.keys_volup.add( pygame.KEYDOWN, ord( '=' ) )
		self.keys_volup.add( pygame.JOYBUTTONDOWN, 16 )	# GP2X volume + button

		self.keys_voldown = mopelib.MyInputEvent( "-" )
		self.keys_voldown.add( pygame.KEYDOWN, ord( '-' ) )
		self.keys_voldown.add( pygame.JOYBUTTONDOWN, 17 ) # GP2X volume - button

		self.keys_editor_up = mopelib.MyInputEvent( "up" )
		self.keys_editor_up.add( pygame.KEYDOWN, pygame.K_UP )
		self.keys_editor_up.add( pygame.JOYBUTTONDOWN, 0 )		# GP2X Joy up

		self.keys_editor_right = mopelib.MyInputEvent( "right" )
		self.keys_editor_right.add( pygame.KEYDOWN, pygame.K_RIGHT )
		self.keys_editor_right.add( pygame.JOYBUTTONDOWN, 6 )	# GP2X Joy right

		self.keys_editor_down = mopelib.MyInputEvent( "down" )
		self.keys_editor_down.add( pygame.KEYDOWN, pygame.K_DOWN )
		self.keys_editor_down.add( pygame.JOYBUTTONDOWN, 4 )	# GP2X Joy down

		self.keys_editor_left = mopelib.MyInputEvent( "left" )
		self.keys_editor_left.add( pygame.KEYDOWN, pygame.K_LEFT )
		self.keys_editor_left.add( pygame.JOYBUTTONDOWN, 2 )	# GP2X Joy left

		self.keys_editor_up_release = mopelib.MyInputEvent( "up_release" )
		self.keys_editor_up_release.add( pygame.KEYUP, pygame.K_UP )
		self.keys_editor_up_release.add( pygame.JOYBUTTONUP, 0 )# GP2X Joy up

		self.keys_editor_right_release = mopelib.MyInputEvent( "right_release" )
		self.keys_editor_right_release.add( pygame.KEYUP, pygame.K_RIGHT )
		self.keys_editor_right_release.add( pygame.JOYBUTTONUP, 6 )# GP2X Jy r

		self.keys_editor_down_release = mopelib.MyInputEvent( "down_release" )
		self.keys_editor_down_release.add( pygame.KEYUP, pygame.K_DOWN )
		self.keys_editor_down_release.add( pygame.JOYBUTTONUP, 4 )# GP2X Jy d

		self.keys_editor_left_release = mopelib.MyInputEvent( "left_release" )
		self.keys_editor_left_release.add( pygame.KEYUP, pygame.K_LEFT )
		self.keys_editor_left_release.add( pygame.JOYBUTTONUP, 2 )# GP2X Jy l

		self.keys_editor_placewall = mopelib.MyInputEvent(
			"RETURN or left click" )
		self.keys_editor_placewall.add( pygame.KEYDOWN, pygame.K_RETURN )
		self.keys_editor_placewall.add( pygame.KEYDOWN, ord( 'w' ) )
		self.keys_editor_placewall.add( pygame.MOUSEBUTTONDOWN, 1 ) # l-click
		self.keys_editor_placewall.add( pygame.JOYBUTTONUP, 13 )	# GP2X B

		self.keys_editor_placestart = mopelib.MyInputEvent(
			"SPACE or right click" )
		self.keys_editor_placestart.add( pygame.KEYDOWN, ord( ' ' ) )
		self.keys_editor_placestart.add( pygame.KEYDOWN, ord( 's' ) )
		self.keys_editor_placestart.add( pygame.MOUSEBUTTONDOWN, 3 )# r-click
		self.keys_editor_placestart.add( pygame.JOYBUTTONUP, 12 )	# GP2X A

# ----------------------

class DuckMazeSoundManager( mopelib.SoundManager ):

	def __init__( self, volume ):
		mopelib.SoundManager.__init__( self, config )

		#self.add_sample_group( "waddles", ["waddle1"] )
		#self.add_sample_group( "quacks", ("quack1") )

# ----------------------

def intro_draw_instructions():
	write_text( "Press %s for menu, or %s to start" % (
		config.keys_menu.name, config.keys_startgame.name ),
		(0, 0, 0), 0.05, 0.99 )

# ----------------------
def music_menu(menu, config, gamestate):
	menu_items=[]
	menu.add_item("Super Mario theme song", 0)
	menu.add_item("GOOGLE MY BULBUL",1)
	menu.add_item("Cake town",2)
	return menu
	
def general_menu_create_menu( menu, config, gamestate ):
	menu.items = []
	if gamestate == None:	# We are on a title screen - Start Game option
		menu.add_item( "Start game", MENU_START )
		menu.add_item( "Start at level: %d" % (config.start_level+1),
			MENU_START_LEVEL )
		menu.add_item( "Level editor", MENU_LEVEL_EDITOR )
	elif gamestate.alive == level.INGAME_ALIVE:
		menu.add_item( "Continue", MENU_START )
		menu.add_item( "Restart level", MENU_RESTART )
		menu.add_item( "End game", MENU_END )

	tmp_str = "Music: "
	if config.music_on:
		tmp_str += "on"
	else:
		tmp_str += "off"
	menu.add_item( tmp_str, MENU_MUSIC )

	tmp_str = "Effects: "
	if config.sound_effects_on:
		tmp_str += "on"
	else:
		tmp_str += "off"
	menu.add_item( tmp_str, MENU_SOUND_EFFECTS )

	menu.add_item( "Quit duckmaze", MENU_QUIT )

	return menu

def general_menu_screen( config, gamestate ):

	if gamestate == None:
		menu_title = "duckmaze"
	else:
		menu_title = "duckmaze paused"

	menu = mopelib.Menu()
	general_menu_create_menu( menu, config, gamestate )
	menurender.set_menu( menu, menu_title )
	menurender.repaint_full()

	game_start = False

	waiting = True
	while waiting:
		event = pygame.event.wait()
		if event.type == QUIT:
			sys.exit(0)
		elif config.keys_menu.matches( event ):
			waiting = False
		elif config.keys_down.matches( event ):
			menurender.move_down()
		elif config.keys_up.matches( event ):
			menurender.move_up()
		elif config.keys_return.matches( event ):
			code = menu.get_selected_item().code
			if code == MENU_START:
				game_start = True
				waiting = False
			elif code == MENU_RESTART:
				game_start = True
				waiting = False
				gamestate.same_level()
			elif code == MENU_END:
				gamestate.alive = level.INGAME_QUIT
				waiting = False
			elif code == MENU_MUSIC:
				if config.music_on == 1:
					config.music_on = 0
				else:
					config.music_on = 1
				general_menu_create_menu( menu, config, gamestate )
				menurender.repaint_full()
				sound_mgr.setup( gamestate )
				config.save()
			elif code == MENU_SOUND_EFFECTS:
				if config.sound_effects_on:
					config.sound_effects_on = 0
				else:
					config.sound_effects_on = 1
				general_menu_create_menu( menu, config, gamestate )
				menurender.repaint_full()
				sound_mgr.setup( gamestate )
				config.save()
			elif code == MENU_START_LEVEL:
				config.start_level += 1
				if config.start_level >= config.levels_unlocked:
					config.start_level = 0
				general_menu_create_menu( menu, config, gamestate )
				menurender.repaint_full()
				config.save()
			elif code == MENU_LEVEL_EDITOR:
				lve = level_editor.LevelEditor( config, screen, sound_mgr )
				lve.mainloop()
				if config.edit_real_levels:
					levels = load_levels( config )
				menurender.repaint_full()
			elif code == MENU_QUIT:
				sys.exit(0)

	return game_start

# ----------------------

def intro_draw_title():
	screen.blit( intro_surface_title, (0,0) )
	write_text( "Version " + duckmaze_version,
		( 0, 0, 0 ), 0.05, 0.88 )
	write_text( "by Andy Balaam", ( 0, 0, 0 ), 0.06, 0.93 )
	intro_draw_instructions()

def intro_draw_something( intro_mode ):
	if intro_mode == INTRO_MODE_TITLE:
		intro_draw_title()
	elif intro_mode == INTRO_MODE_INSTR:
		screen.blit( intro_surface_instr, (0,0) )
		intro_draw_instructions()
	elif intro_mode == INTRO_MODE_MUSIC:
		screen.blit( intro_surface_music, (0,0) )
		intro_draw_instructions()
	pygame.display.update()

def intro_input( event, config, intro_mode ):
	if event.type == QUIT:
		sys.exit(0)
	elif config.keys_volup.matches( event ):
		config.volume = sound_mgr.increase_volume()
		config.save()
	elif config.keys_voldown.matches( event ):
		config.volume = sound_mgr.decrease_volume()
		config.save()
	else:
		if event.type == EVENTTYPE_TITLE:
			intro_mode += 1
			if intro_mode == INTRO_MODE_ENDED:
				intro_mode = INTRO_MODE_TITLE
			intro_draw_something( intro_mode )
		elif config.keys_menu.matches( event ):
			mopelib.clear_events( EVENTTYPE_TITLE )
			start_game = general_menu_screen( config, None )
			if start_game:
				intro_mode = INTRO_MODE_ENDED
			else:
				intro_draw_something( intro_mode )
			pygame.time.set_timer( EVENTTYPE_TITLE, TITLE_TICK_TIME )
		elif config.keys_startgame.matches( event ):
			intro_mode = INTRO_MODE_ENDED
	return intro_mode

# ----------------------

def intro_mainloop( config ):
	intro_draw_title()

	pygame.display.update()
	pygame.time.set_timer( EVENTTYPE_TITLE, TITLE_TICK_TIME )

	intro_mode = INTRO_MODE_TITLE
	while intro_mode < INTRO_MODE_ENDED:
		intro_mode = intro_input( pygame.event.wait(), config, intro_mode )

	mopelib.clear_events( EVENTTYPE_TITLE )

def inlevel_redraw_screen( gamestate ):
	maze_colour = mopelib.dim_colour( gamestate.config.colour_maze,
		gamestate.dim )
	duck_colour = mopelib.dim_colour( gamestate.config.colour_duck,
		gamestate.dim )

	if gamestate.dim != gamestate.old_dim:
		bgcol = mopelib.dim_colour( gamestate.cur_lev.background_colour,
			gamestate.dim )
		ingame_surface_background.fill( bgcol )
		gamestate.old_dim = gamestate.dim

	screen.blit( ingame_surface_background, (0,0) )

	lev = gamestate.cur_lev
	for y in range( len( lev.lines_hor ) ):
		for x in range( len( lev.lines_hor[y] ) ):
			pos = lev.lines_hor[y][x]
			if pos == 1:
				pygame.draw.rect( screen, maze_colour,
					( screen_border + scale[0] * (x + 0.1),
					  screen_border + scale[1] * y,
					  scale[0] * 0.92, scale[1] * 0.1 ) )

	for y in range( len( lev.lines_ver ) ):
		for x in range( len( lev.lines_ver[y] ) ):
			pos = lev.lines_ver[y][x]
			if pos == 1:
				pygame.draw.rect( screen, maze_colour,
					( screen_border + scale[0] * x,
					  screen_border + scale[1] * (y + 0.1),
					  scale[0] * 0.1, scale[1] * 0.92 ) )

	if( lev.position[0] >=0 and lev.position[0] < config.arena_size[0] and
			lev.position[1] >=0 and lev.position[1] < config.arena_size[1] ):
		duck_size = int( scale[1] * 0.3 )
		duck_pos = ( int( screen_border + scale[0] * ( lev.position[0] + 0.495 ) ),
					 int( screen_border + scale[1] * ( lev.position[1] + 0.495 ) ) )
		pygame.draw.circle( screen, duck_colour, duck_pos, duck_size )
		pygame.draw.circle( screen, maze_colour, duck_pos, duck_size+1, 1 )

		if lev.direction == level.DIR_UP:
			end_pos_inc = ( 0, -duck_size )
		elif lev.direction == level.DIR_RIGHT:
			end_pos_inc = ( duck_size, 0 )
		elif lev.direction == level.DIR_DOWN:
			end_pos_inc = ( 0, duck_size )
		elif lev.direction == level.DIR_LEFT:
			end_pos_inc = ( -duck_size, 0 )

		pygame.draw.line( screen, maze_colour, duck_pos,
			( duck_pos[0] + end_pos_inc[0], duck_pos[1] + end_pos_inc[1] ) )

	write_text_ingame( gamestate )

	pygame.display.update()


# ----------------------

def inlevel_input( event, gamestate ):
	if event.type == QUIT:
		sys.exit(0)
	elif( ( event.type == pygame.ACTIVEEVENT and event.state == 2 )
	   or config.keys_menu.matches( event ) ):
		general_menu_screen( config, gamestate )
		gamestate.old_dim = -2
		inlevel_redraw_screen( gamestate )
	elif config.keys_volup.matches( event ):
		config.volume = sound_mgr.increase_volume()
		config.save()
	elif config.keys_voldown.matches( event ):
		config.volume = sound_mgr.decrease_volume()
		config.save()
	elif event.type == EVENTTYPE_FADE:
		gamestate.fade_event()
		inlevel_redraw_screen( gamestate )
	elif event.type == EVENTTYPE_TIMER:
		gamestate.timer_tick()
		if gamestate.alive == level.INGAME_DEAD:
			finishedlevel_mainloop( gamestate )
			gamestate.same_level()
		else:
			inlevel_redraw_screen( gamestate )
	elif event.type == EVENTTYPE_MOVE:
		#sound_mgr.play_sample( "waddles" )
		gamestate.cur_lev.move_again( gamestate )
		inlevel_redraw_screen( gamestate )
	else:
		if config.keys_left.matches( event ):
			#sound_mgr.play_sample( "waddles" )
			gamestate.cur_lev.move_left( gamestate )
			inlevel_redraw_screen( gamestate )
			pygame.time.set_timer( EVENTTYPE_MOVE, MOVE_TICK_TIME )
		elif config.keys_right.matches( event ):
			#sound_mgr.play_sample( "waddles" )
			gamestate.cur_lev.move_right( gamestate )
			inlevel_redraw_screen( gamestate )
			pygame.time.set_timer( EVENTTYPE_MOVE, MOVE_TICK_TIME )
		elif config.keys_up.matches( event ):
			#sound_mgr.play_sample( "waddles" )
			gamestate.cur_lev.move_up( gamestate )
			inlevel_redraw_screen( gamestate )
			pygame.time.set_timer( EVENTTYPE_MOVE, MOVE_TICK_TIME )
		elif config.keys_down.matches( event ):
			#sound_mgr.play_sample( "waddles" )
			gamestate.cur_lev.move_down( gamestate )
			inlevel_redraw_screen( gamestate )
			pygame.time.set_timer( EVENTTYPE_MOVE, MOVE_TICK_TIME )
		elif(
			( gamestate.cur_lev.direction == level.DIR_LEFT and
			  config.keys_left_release.matches( event ) ) or
			( gamestate.cur_lev.direction == level.DIR_RIGHT and
			  config.keys_right_release.matches( event ) ) or
			( gamestate.cur_lev.direction == level.DIR_UP and
			  config.keys_up_release.matches( event ) ) or
			( gamestate.cur_lev.direction == level.DIR_DOWN and
			  config.keys_down_release.matches( event ) ) ):
				mopelib.clear_events( EVENTTYPE_MOVE )


# ----------------------

def finishedgame_input( event, waiting ):
	if event.type == QUIT:
		sys.exit(0)
	elif config.keys_volup.matches( event ):
		config.volume = sound_mgr.increase_volume()
		config.save()
	elif config.keys_voldown.matches( event ):
		config.volume = sound_mgr.decrease_volume()
		config.save()
	elif config.keys_startgame.matches( event ):
		waiting = False
	return waiting

# ----------------------

class GameState:
	def __init__( self, config, levels ):
		self.config = config

		self.levels = levels
		self.level_num = config.start_level
		self.cur_lev = level.Level( config, self.levels[self.level_num] )

		self.alive = level.INGAME_ALIVE
		self.dim = -1
		self.old_dim = -1

	def same_level( self ):
		self.cur_lev = level.Level( config, self.levels[self.level_num] )
		self.alive = level.INGAME_ALIVE
		self.start_fade()

	def start_fade( self ):
		self.dim = 2
		pygame.time.set_timer( EVENTTYPE_FADE, FADE_TICK_TIME )

	def next_level( self ):
		self.level_num += 1
		if self.level_num < len( self.levels ):
			self.cur_lev = level.Level( config, self.levels[self.level_num] )
			self.alive = level.INGAME_ALIVE
		else:
			self.level_num = len( self.levels ) - 1
			self.alive = level.INGAME_WON

		config.start_level = self.level_num
		if config.levels_unlocked < self.level_num + 1:
			config.levels_unlocked = self.level_num + 1
		config.save()

	def fade_event( self ):
		self.dim -= 0.1
		if self.dim <= 1:
			self.dim = 1
			mopelib.clear_events( EVENTTYPE_FADE )

	def timer_tick( self ):
		self.cur_lev.current_time -= 1
		if self.cur_lev.current_time <= 0:
			self.alive = level.INGAME_DEAD

# ----------------------

def ingame_mainloop( config, levels ):
	gamestate = GameState( config, levels )
	while gamestate.alive == level.INGAME_ALIVE:
		inlevel_mainloop( config, gamestate )
		if gamestate.alive == level.INGAME_FINISHED_LEVEL:
			gamestate.next_level()
	return gamestate

# ----------------------

def inlevel_mainloop( config, gamestate ):

	gamestate.start_fade()
	inlevel_redraw_screen( gamestate )

	gc.disable()
	pygame.time.set_timer( EVENTTYPE_TIMER, TIMER_TICK_TIME )
	while gamestate.alive == level.INGAME_ALIVE:
		inlevel_input( pygame.event.wait(), gamestate )
	gc.enable()
	mopelib.clear_events( EVENTTYPE_TIMER )

	mopelib.clear_events( EVENTTYPE_FADE )
	mopelib.clear_events( EVENTTYPE_MOVE )

	ingame_surface_background.fill( config.colour_background )


# ----------------------

def write_text( txt, colour, size, y_pos ):
	ft = pygame.font.Font( None, int( config.screen_size[1] * size ) )
	sf = ft.render( txt, True, colour )
	screen.blit( sf, ( (config.screen_size[0] - sf.get_width() )/2,
		(config.screen_size[1] - sf.get_height() ) * y_pos ) )

# ----------------------

def write_text_ingame( gamestate ):
	global ingame_font

	bgcol = mopelib.dim_colour( gamestate.cur_lev.background_colour,
		gamestate.dim )
	fgcol = mopelib.dim_colour( gamestate.cur_lev.text_colour, gamestate.dim )

	write_text_blank_font_coords( "Level: %d" % ( gamestate.level_num + 1 ),
		fgcol, ingame_font, bgcol, 0.3, 0.99 )

	write_text_blank_font_coords( "Time: %s" % gamestate.cur_lev.current_time,
		fgcol, ingame_font, bgcol, 0.7, 0.99 )


def write_text_blank_font_coords( txt, colour, font, bgcolour, x, y ):
	sf = font.render( txt, True, colour )
	sf_bg = pygame.Surface( ( int( sf.get_width() * 1.29 ), sf.get_height() ) )
	sf_bg.fill( bgcolour )

	tlx = ( config.screen_size[0] - sf_bg.get_width() ) * x
	tly = ( config.screen_size[1] - sf_bg.get_height() ) * y

	dirty_rect = Rect( tlx, tly, sf_bg.get_width(), sf_bg.get_height() )
	screen.blit( sf_bg, dirty_rect )
	screen.blit( sf, ( tlx * 1.01, tly ) )

# ----------------------

def finishedlevel_mainloop( gamestate ):
	mopelib.clear_events( EVENTTYPE_MOVE )
	mopelib.clear_events( EVENTTYPE_FADE )

	gamestate.dim = 0.5
	inlevel_redraw_screen( gamestate )
	write_text( "Out of time!", (255,255,255), 0.125, 0.45 )
	waiting = True
	write_text( "Press %s to try again." % config.keys_startgame.name, (255,255,255),
		0.05, 0.8 )
	pygame.display.update()
	while waiting:
		waiting = finishedgame_input( pygame.event.wait(), waiting )


# ----------------------

def finishedgame_mainloop( config, gamestate ):
	mopelib.clear_events( EVENTTYPE_MOVE )
	mopelib.clear_events( EVENTTYPE_FADE )

	if gamestate.alive == level.INGAME_WON:
		config.start_level = 0
		config.save()
		gamestate.dim = 0.5
		inlevel_redraw_screen( gamestate )
		write_text( "Congratulations!", (255,255,255), 0.125, 0.38 )
		write_text( "You won!", (255,255,255), 0.125, 0.52 )
		waiting = True
		write_text( "Press %s" % config.keys_startgame.name, (255,255,255),
			0.05, 0.8 )
		pygame.display.update()
		while waiting:
			waiting = finishedgame_input( pygame.event.wait(), waiting )

		ingame_surface_background.fill( config.colour_background )


# ----------------------

def create_hiscores( filename ):

	default_scores = (
	  [ ( "Master",      10 ),	# Normal, Easy
		( "Of",           9 ),
		( "Pain",         8 ),
		( "(Eating)",     7 ),
		( "mop(e)snake",  6 ) ],
	  [ ( "Master",      50 ),	# Normal, Medium
		( "Of",          40 ),
		( "Pain",        30 ),
		( "(Eating)",    20 ),
		( "mop(e)snake", 10 ) ],
	  [ ( "Master",     100 ),	# Normal, Hard
		( "Of",          80 ),
		( "Pain",        60 ),
		( "(Eating)",    40 ),
		( "mop(e)snake", 20 ) ],
	  [ ( "Master",      10 ),	# Onebutton, Easy
		( "Of",           9 ),
		( "Pain",         8 ),
		( "(Eating)",     7 ),
		( "mop(e)snake",  6 ) ],
	  [ ( "Master",      50 ),	# Onebutton, Medium
		( "Of",          40 ),
		( "Pain",        30 ),
		( "(Eating)",    20 ),
		( "mop(e)snake", 10 ) ],
	  [ ( "Master",     100 ),	# Onebutton, Hard
		( "Of",          80 ),
		( "Pain",        60 ),
		( "(Eating)",    40 ),
		( "mop(e)snake", 20 ) ]
	  )

	return mopelib.Hiscores( filename, default_scores )

# ----------------------

def load_levels( config ):
	ans = []

	for cur_level in range( 999 ):
		filename = os.path.join( config.install_dir, "levels",
			"level_%03d" % (cur_level + 1) )

		if os.path.isfile( filename ):
			lv = level.Level( config, filename )
			ans.append( lv )
		else:
			break

	return ans

# ----------------------
# Execution starts here
# ----------------------

# Fixed constants

INTRO_MODE_TITLE = 0
INTRO_MODE_INSTR = 1
INTRO_MODE_MUSIC = 2
INTRO_MODE_ENDED = 3

MENU_START         = 0
MENU_RESTART       = 1
MENU_END           = 2
MENU_START_LEVEL   = 3
MENU_LEVEL_EDITOR  = 4
MENU_KEYS          = 5
MENU_MUSIC         = 6
MENU_SOUND_EFFECTS = 7
MENU_KEYS          = 8
MENU_QUIT          = 9

TITLE_TICK_TIME  = 4000
MOVE_TICK_TIME   = 200
TIMER_TICK_TIME  = 1000
FADE_TICK_TIME   = 50

EVENTTYPE_MOVE  = pygame.USEREVENT
EVENTTYPE_TIMER = pygame.USEREVENT + 1
EVENTTYPE_TITLE = pygame.USEREVENT + 2
EVENTTYPE_FADE  = pygame.USEREVENT + 3

num_args = len( sys.argv )
if num_args > 1:
	if sys.argv[1] == "--help":
		print "Usage:"
		print "duckmaze [install_dir] [config_file] [resolution]"
		print
		print "e.g. ./duckmaze.py . duckmazerc.txt '(640,480)'"
		print
		sys.exit( 0 )

	install_dir = sys.argv[1]
else:
	install_dir = "."

if num_args > 2:
	config_filename = sys.argv[2]
else:
	config_filename = os.path.expanduser( "~/.duckmaze/config" )

config = DuckMazeConfig( config_filename )

config.install_dir = install_dir
config.unsaved.append( "install_dir" )

config.images_dir = os.path.join( install_dir, "images" )
config.unsaved.append( "images_dir" )

config.music_dir = os.path.join( install_dir, "music" )
config.unsaved.append( "music_dir" )

pygame.init()
pygame.font.init()

pygame.mouse.set_visible( False )

if num_args > 3:
	config.screen_size = config.parse_value( sys.argv[3] )

window = pygame.display.set_mode( config.screen_size )
pygame.display.set_caption( 'duckmaze' )
screen = pygame.display.get_surface()

config.arena_size = ( 12, 8 )
config.unsaved.append( "arena_size" )

screen_border = 5
scale = ( ( config.screen_size[0] - screen_border*2 ) / config.arena_size[0],
	( config.screen_size[1] - screen_border*2 ) / (config.arena_size[1]+1) )

# General initialisation

num_joysticks = pygame.joystick.get_count()
for j in range( num_joysticks ):
	pygame.joystick.Joystick( j ).init()

intro_surface_title = mopelib.load_and_scale_image( "title.png", config )
intro_surface_instr = mopelib.load_and_scale_image( "instructions.png", config )
intro_surface_music = mopelib.load_and_scale_image( "music.png", config )

ingame_surface_background = pygame.Surface( screen.get_size() ).convert()
ingame_surface_background.fill( config.colour_background )

intro_mode = INTRO_MODE_TITLE

sound_mgr = DuckMazeSoundManager( config.volume )

duckmaze_version = mopelib.read_version( config )

levels = load_levels( config )

ingame_font = pygame.font.Font( None, int( config.screen_size[1] * 0.09 ) )

menurender = mopelib.MenuRenderer( screen, config, ingame_surface_background,
	(32, 32, 32), (255, 255, 255), (75, 75, 75) )

while True:
	sound_mgr.music_loud()
	intro_mainloop( config )
	sound_mgr.music_quiet()
	cur_level = ingame_mainloop( config, levels )
	intro_mode = finishedgame_mainloop( config, cur_level )



