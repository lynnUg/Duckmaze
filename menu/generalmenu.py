from menu import menucreator
class generalmenu( menucreator):
	def  __init__( self):
		menucreator.__init__(self,"generalmenu")

	def createmenu(self,menu,config):
		menu.items=[]
		menu.add_item( "Start game", 0 )
		menu.add_item( "Start at level: %d" % (config.start_level+1),
			menucreator.MENU_START_LEVEL )
		menu.add_item( "Level editor", menucreator.MENU_LEVEL_EDITOR )
		tmp_str = "Music: "
		if config.music_on:
			tmp_str += "on"
		else:
			tmp_str += "off"
		menu.add_item( tmp_str, menucreator.MENU_MUSIC )
		tmp_str = "Effects: "
		if config.sound_effects_on:
			tmp_str += "on"
		else:
			tmp_str += "off"
			menu.add_item( tmp_str, menucreator.MENU_SOUND_EFFECTS )
			menu.add_item( "Quit duckmaze", menucreator.MENU_QUIT )
		return menu
