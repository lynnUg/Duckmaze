from generalmenu import generalmenu
from pausemenu import pausemenu
from musicmenu import musicmenu
class menufactory:
	def makemenu(self,gamestate):
		if gamestate:
			return pausemenu(),"duckmaze paused"
		else:
			return generalmenu(),"duckmaze"
	def makemusicmenu(self):
		return musicmenu()
	
