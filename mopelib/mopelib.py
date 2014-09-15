#!/usr/bin/python -u

# mopelib - a python module with some useful classes for creating games.
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

# ----------------------

TEXT_OVER_ITEM_HEIGHT = 0.9
MAX_ITEM_HEIGHT = 0.11

# ----------------------

class MyInputEvent:
	def  __init__( self, name ):
		self.pairs = []
		self.name = name

	def add_all( self, type ):
		self.pairs.append( ( type, -1 ) )

	def add( self, type, number ):
		self.pairs.append( ( type, number ) )

	def matches( self, event ):
		for p in self.pairs:
			type = p[0]
			number = p[1]
			if type == event.type:
				if number == -1:	# Any number is fine
					return True
				elif type == pygame.JOYBUTTONDOWN \
				  or type == pygame.JOYBUTTONUP \
				  or type == pygame.MOUSEBUTTONDOWN \
				  or type == pygame.MOUSEBUTTONUP:
					if number == event.button:
						return True
				elif type == pygame.KEYDOWN \
				  or type == pygame.KEYUP:
					if number == event.key:
						return True
		return False

	def __str__( self ):
		ans = "Input( '%s'" % self.name
		for p in self.pairs:
			ans += ", %d, %d" % ( p[0], p[1] )
		ans += " )"
		return ans

# ----------------------

class HashException( Exception ):
	pass

# ----------------------

def mkdir_if_needed( filename ):
	dr = os.path.split( filename )[0]
	if dr.strip() != "" and not os.path.isdir( dr ):
		os.mkdir( dr )

# ----------------------

def read_version( config ):
	f = file( os.path.join( config.install_dir, "version" ), 'r' )
	ln = f.readline()
	f.close()

	return ln.strip()

# ----------------------

def load_and_scale_image( filename, config ):
	sur = pygame.image.load( os.path.join( config.images_dir, filename ) )

	if sur.get_size() != config.screen_size:
		sur = pygame.transform.scale( sur, config.screen_size )

	sur.convert()
	return sur

# ----------------------

def dim_colour( colour, dim ):
	"""Modify a colour to make it darker or lighter.  Arguments:
	- colour: the colour to modify as a 3-tuple for RGB values
	- dim: 1 for no change, 0<=dim<1 for darker colours and
	       1<dim<=2 for lighter colours
	returns the modified colour.
	"""
	if dim == 1:
		new_colour = colour
	elif dim > 1:
		new_colour = ( colour[0] + ((255-colour[0])*(dim-1)),
					   colour[1] + ((255-colour[1])*(dim-1)),
					   colour[2] + ((255-colour[2])*(dim-1)) )
	else:
		new_colour = ( colour[0] * dim, colour[1] * dim, colour[2] * dim )

	return new_colour

# ----------------------

def clear_events( event_type ):
	pygame.time.set_timer( event_type, 0 )
	pygame.event.clear( event_type )

class Hiscores:
	def __init__( self, hiscores_filename, default_score_table ):
		self.scores = default_score_table
		self.filename = hiscores_filename

		try:
			self.read_scores()
		except HashException:
			print "Fiddling detected: high scores reset to defaults!"
			self.scores = default_score_table

		if len( self.scores[0] ) != self.num_tables:
			print "Creating high score table."
			self.scores = default_score_table

	def read_scores( self ):
		current_array = -1
		next_hash = None

		try:
			f = file( self.filename, 'r' )
			ln = f.readline()
			lines_since_hash = 5
			while( ln ):

				if lines_since_hash == 5:	# Pathetic attempt at security

					lines_since_hash = 0
					if next_hash != None:
						expected_next_hash = self.hash_array(
							self.scores[current_array] )
						if expected_next_hash != next_hash:
							raise HashException()

					next_hash = ln.strip()

					current_array += 1

					del self.scores[current_array][:]

				else:
					lines_since_hash += 1
					split_ln = ln.split( ":", 1 )
					if len( split_ln ) == 2:
						self.scores[current_array].append( ( split_ln[0].strip(), int( split_ln[1] ) ) )

				ln = f.readline()
			f.close()
		except IOError:
			pass	# If the file didn't exist or couldn't be read, we continue


	def hash_array( self, array ):
		ans = ""
		for pair in array:
			ans += pair[0]
			ans += "."
			ans += str( pair[1] )
			ans += "|"

		m = md5.new()
		m.update( ans )
		return m.hexdigest()

	def save_array( self, f, array ):
		f.write( "%s\n" % self.hash_array( array ) );
		for pair in array:
			f.write( "%s : %d\n" % pair );

	def save( self ):
		mkdir_if_needed( self.filename )
		f = file( self.filename, 'w' )
		for arr in self.scores:
			self.save_array( f, arr )
		f.flush()
		os.fsync( f.fileno() )
		f.close()

# ----------------------

class Config:

	def __init__( self, config_filename ):

		# Set the default config, and override if we find things in the
		# config file
		self.default_config()

		try:
			f = file( config_filename, 'r' )
			ln = f.readline()
			while( ln ):
				self.process_line( ln )
				ln = f.readline()
			f.close()
		except IOError:
			pass	# If the file didn't exist or couldn't be read, we continue

		# Ensure no-one tries to exploit us with a frigged config file
		self.filename = config_filename

		self.unsaved = []
		self.unsaved.append( "filename" )
		self.unsaved.append( "unsaved" )

	def process_line( self, ln ):
		ln = ln.strip()
		if len( ln ) > 0 and ln[0] != "#" and ln.find( '=' ) != -1:
			split_ln = ln.split( '=' )
			if len( split_ln ) == 2:
				key = split_ln[0].strip()
				value = split_ln[1]

				self.__dict__[key] = self.parse_value( value )

	def parse_value( self, value ):

		value = value.strip()
		if value[:5] == "Input":
			tup = self.parse_value( value[5:] )
			ret = MyInputEvent( tup[0] )
			for i in range( 1, len( tup ), 2 ):
				ret.add( tup[i], tup[i+1] )
			return ret

		elif value[0] == "(" and value[-1] == ")":
			return tuple( map( self.parse_value,
				value[1:-1].split( ',' ) ) )

		elif value[0] == "[" and value[-1] == "]":
			return map( self.parse_value,
				value[1:-1].split( ',' ) )

		elif ( value[0] == '"' and value[-1] == '"' ) \
		  or ( value[0] == "'" and value[-1] == "'" ):
			return value[1:-1]

		else:
			return (int)( value )


	def default_config( self ):
		raise Exception(
			"default_config() should be implemented in the base class." )


	def save( self ):
		mkdir_if_needed( self.filename )
		f = file( self.filename, 'w' )
		keys = self.__dict__.keys()
		keys.sort()
		for k in keys:
			if k not in self.unsaved:
				v = self.__dict__[k]
				if isinstance( v, str ):
					f.write( "%s = '%s'\n" % ( k, str(v) ) )
				else:
					f.write( "%s = %s\n" % ( k, str(v) ) )
		f.flush()
		os.fsync( f.fileno() )
		f.close()

# ----------------------

class MenuItem:
	def __init__( self, text, code ):
		self.code = code
		self.text = text

# ----------------------

class Menu:

	def __init__( self ):
		self.selected_index = 0
		self.items = []

	def set_selected_item( self, item_text ):
		for i in range( len( self.items ) ):
			if self.items[i].text == item_text:
				self.selected_index = i
				break

	def get_selected_item( self ):
		return self.items[self.selected_index]

	def add_item( self, text, code ):
		self.items.append( MenuItem( text, code ) )

	def move_up( self ):
		self.selected_index -= 1
		if self.selected_index == -1:
			self.selected_index = len( self.items ) - 1

	def move_down( self ):
		self.selected_index += 1
		if self.selected_index == len( self.items ):
			self.selected_index = 0

# --------------------------

class MenuRenderer:

	TEXT_TYPE_SMALL           = 0
	TEXT_TYPE_MENU_SELECTED   = 1
	TEXT_TYPE_MENU_UNSELECTED = 2

	def __init__( self, screen, config, background_surface,
			colour_menu_unselected, colour_menu_selected, colour_small_print ):
		self.screen = screen
		self.config = config
		self.background_surface = background_surface
		self.colour_menu_unselected = colour_menu_unselected
		self.colour_menu_selected = colour_menu_selected
		self.colour_small_print = colour_small_print

		self.top_pos = 0.15
		self.bottom_pos = 0.85

		self.item_height = 0
		self.text_height = 0

		self.rendered_txt = []
		self.rendered_txt.append( {} )
		self.rendered_txt.append( {} )
		self.rendered_txt.append( {} )

	def set_menu( self, menu, title ):
		self.menu = menu
		self.title_txt = title

		new_item_height = ( ( self.bottom_pos - self.top_pos )
			/ len( self.menu.items ) )
		new_text_height = new_item_height * TEXT_OVER_ITEM_HEIGHT

		if( new_item_height != self.item_height or
		  new_text_height != self.text_height ):
			self.item_height = new_item_height
			self.text_height = new_text_height

			if self.item_height > MAX_ITEM_HEIGHT:
				self.item_height = MAX_ITEM_HEIGHT
				self.text_height = MAX_ITEM_HEIGHT * TEXT_OVER_ITEM_HEIGHT

			self.menu_item_font = pygame.font.Font(
				None, int( self.config.screen_size[1] * self.text_height ) )

			self.small_print_font = pygame.font.Font(
				None, int( self.config.screen_size[1] * 0.06 ) )

	def repaint_full( self ):
		self.screen.blit( self.background_surface, (0,0) )

		cur_pos = self.top_pos
		for item in self.menu.items:
			if self.menu.get_selected_item() == item:
				txt_type = MenuRenderer.TEXT_TYPE_MENU_SELECTED
			else:
				txt_type = MenuRenderer.TEXT_TYPE_MENU_UNSELECTED

			self.write_text( item.text, cur_pos, txt_type )

			cur_pos += self.item_height

		self.write_text( self.title_txt, 0.01,
			MenuRenderer.TEXT_TYPE_SMALL )

		self.write_text( "Press %s and %s to navigate" % (
			self.config.keys_up.name, self.config.keys_down.name ), 0.9,
				MenuRenderer.TEXT_TYPE_SMALL )

		self.write_text( "and %s to select" % self.config.keys_return.name,
			0.95, MenuRenderer.TEXT_TYPE_SMALL )

		pygame.display.update()

	def repaint_items( self, item_indices ):
		dirty_rects = []
		for item_idx in item_indices:
			pos = self.top_pos + ( self.item_height * item_idx )
			if item_idx == self.menu.selected_index:
				txt_type = MenuRenderer.TEXT_TYPE_MENU_SELECTED
			else:
				txt_type = MenuRenderer.TEXT_TYPE_MENU_UNSELECTED

			dirty_rects.append(
				self.write_text( self.menu.items[item_idx].text,
					pos, txt_type ) )

			pygame.display.update( dirty_rects )

	def write_text( self, txt, y_pos, txt_type ):
		if txt in self.rendered_txt[txt_type]:
			sf = self.rendered_txt[txt_type][txt]
		else:
			if txt_type == MenuRenderer.TEXT_TYPE_SMALL:
				ft = self.small_print_font
				colour = self.colour_small_print
			else:
				ft = self.menu_item_font
				if txt_type == MenuRenderer.TEXT_TYPE_MENU_SELECTED:
					colour = self.colour_menu_selected
				else:
					colour = self.colour_menu_unselected

			sf = ft.render( txt, True, colour )
			self.rendered_txt[txt_type][txt] = sf

		pos = ( (self.config.screen_size[0] - sf.get_width() )/2,
			(self.config.screen_size[1] - sf.get_height() ) * y_pos )

		dirty_rect = ( pos[0], pos[1], sf.get_width(), sf.get_height() )

		self.screen.blit( self.background_surface, pos, dirty_rect )
		self.screen.blit( sf, pos )

		return dirty_rect

	def move_somewhere( self, move_method ):
		old_index = self.menu.selected_index
		move_method()
		new_index = self.menu.selected_index

		if old_index != new_index:
			self.repaint_items( [old_index, new_index] )

	def move_down( self ):
		self.move_somewhere( self.menu.move_down )

	def move_up( self ):
		self.move_somewhere( self.menu.move_up )

# ----------------------

class SoundManager:

	def __init__( self, config, music_filename = None ):
		self.sound_inited = False
		self.music_loaded = False
		self.music_is_quiet = False
		self.music_playing = False
		self.volume = 0
		self.music_sample = None
		self.samples_loaded = False
		self.sample_filenames = {}
		self.sample_groups = {}
		self.config = config

                if "music_on" not in config.__dict__:
                    config.music_on = 1
                if "sound_effects_on" not in config.__dict__:
                    config.sound_effects_on = 1

		if music_filename != None:
			self.music_filename = os.path.join( config.music_dir,
				music_filename )
		else:
			self.music_filename = ""

		self.sounds_dir = os.path.join( config.install_dir, "sounds" )

		self.setup( None )

	def add_sample_group( self, groupname, filenames ):
		if self.sound_inited:
			self.sample_filenames[groupname] = []
			for fn in filenames:
				self.sample_filenames[groupname].append(
					os.path.join( self.sounds_dir, fn + ".wav" ) )
			if self.config.sound_effects_on:
				self.samples_load()

	def play_sample( self, groupname ):
		if self.sound_inited:
			if self.sound_effects_on and self.volume > 0:
				group = self.sample_groups[groupname]
				group[ random.randint( 0, len( group ) - 1 ) ].play()
				#print "play sample '%s'" % groupname

	def set_volume( self ):
		if self.sound_inited:
			#print "set sample volumes %f" % self.volume
			for sg in self.sample_groups.values():
				for s in sg:
					s.set_volume( self.volume )

			self.set_music_volume()

	def set_music_volume( self ):
		if self.music_is_quiet:
			if self.volume <= 0.3:
				self.music_stop()
			else:
				if self.config.music_on:
					if not self.music_loaded:
						self.music_load()
					if not self.music_playing:
						self.music_start()
					if self.music_sample != None:
						self.music_sample.set_volume( self.volume / 3 )
						#print "set music volume %f" % (self.volume / 3)


		else:
			if self.music_sample != None:
				self.music_sample.set_volume( self.volume )
				#print "set music volume %f" % (self.volume)


	def increase_volume( self ):
		if self.sound_inited and self.volume < 1:
			self.volume += 0.1
			if self.volume > 1:
				self.volume = 1
			self.set_volume()
		return int( round( self.volume * 100 ) )


	def decrease_volume( self ):
		if self.sound_inited and self.volume > 0:
			self.volume -= 0.1
			if self.volume < 0:
				self.volume = 0
			self.set_volume()
		return int( round( self.volume * 100 ) )

	def music_start( self ):
		if self.sound_inited and not self.music_playing:
			if self.music_sample != None:
				self.music_sample.play( -1 )
				#print "play music (music_start)"
			self.music_playing = True

	def music_stop( self ):
		if self.sound_inited and self.music_playing:
			if self.music_sample != None:
				self.music_sample.stop()
				#print "stop music"
				self.music_playing = False

	def music_quiet( self ):
		if self.sound_inited:
			self.music_is_quiet = True
			self.set_music_volume()

	def music_loud( self ):
		if self.sound_inited:
			self.music_is_quiet = False
			self.set_music_volume()

	def samples_load( self ):
		if self.sound_inited:
			self.samples_loaded = True
			for groupname in self.sample_filenames.keys():
				self.sample_groups[groupname] = []
				for fn in self.sample_filenames[groupname]:
					if os.path.isfile( fn ):
						snd = pygame.mixer.Sound( fn )
						#print "load sample '%s'" % fn
						self.sample_groups[groupname].append( snd )
					else:
						print "Could not find sound file '%s'" % fn

	def music_load( self ):
		if self.sound_inited:
			self.music_loaded = True
			if self.music_filename != "":
				if os.path.isfile( self.music_filename ):
					self.music_sample = pygame.mixer.Sound( self.music_filename )
					#print "load music '%s'" % self.music_filename
				else:
					print "Could not find music file '%s'." % self.music_filename

	def setup( self, gamestate ):
		if "volume" in self.config.__dict__:
			self.volume = self.config.volume / 100.0

		if not self.sound_inited:
			pygame.mixer.init()
			#print "init mixer"

		if pygame.mixer.get_init():
			self.sound_inited = True
		else:
			self.sound_inited = False
			if "init_error" not in self.__dict__:
				print "Unable to initialise the sound mixer."
				self.init_error = True

		if self.sound_inited:
			if self.config.music_on:
				if not self.music_loaded:
					self.music_load()
				self.music_start()
			else:
				self.music_stop()

			if self.config.sound_effects_on:
				if not self.samples_loaded:
					self.samples_load()
				self.sound_effects_on = True
			else:
				self.sound_effects_on = False
			self.set_volume()


