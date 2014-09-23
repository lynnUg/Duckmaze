from menu import menucreator
class musicmenu( menucreator):
	def  __init__( self):
		menucreator.__init__(self,"music")

	def createmenu(self,menu,config):
		menu.selected_index=0
		menu.items=[]
		menu.add_item( "Burna boy: Yawa Dey",  0)
		menu.add_item( "Tiwa Savage :Girl O",  1)
		menu.add_item( "Yo yo ma:Bach",  3 )
		return menu
