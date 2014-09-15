Duckmaze
========
Welcome to Duckmaze :-)
Duckmaze is a game about a duck that is in a maze and needs to get out of the maze. The duck can move walls, but only if there are no walls in the way (it makes sense when you try it).

It's a simple puzzle game which starts with easy levels but progresses to some quite tricky ones.

##- Installing packages

To run duckmaze, you will need to install Python(2.7.*) and the PyGame(1.9.2) library. 

On Linux this should be a simple case of apt-get install python-pygame or yum install pygame or similar.

On Windows, you will need to download the relevant [Python](https://www.python.org/download/releases/2.7/) [PyGame installer](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pygame)

On Mac , pip install hg+http://bitbucket.org/pygame/pygame

##- Potential Challenge

The Duck in duckmaze currently moves left , right , up and down. I would like the geeks at geeknight to add a unique sound to every movement of the duck. When the duck move left , it should meow(cat), move right , it should bark (dog) , move up , it should cluck(chicken) and move down ,it should moo(cow).


I shall walk the geeks through the codeset placing focus on the functions we shall be using. Which is class SoundManager in mopelib/mopelib.py and the function def inlevel_input( event, gamestate ) in duckmaze.py(this function is filled with if statements).


