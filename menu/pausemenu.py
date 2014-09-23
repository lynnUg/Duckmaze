from menu import menucreator
class pausemenu( menucreator):
	def  __init__( self):
		menucreator.__init__(self,"pausemenu")

	def createmenu(self,menu,config):
		menu.items=[]
		menu.add_item( "Continue",  menucreator.MENU_START )
		menu.add_item( "Restart level",  menucreator.MENU_RESTART )
		menu.add_item( "End game",  menucreator.MENU_END )
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
