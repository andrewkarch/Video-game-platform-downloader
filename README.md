# Video Game Platform Downloader

A simple application that gets the year and platform of a list of video games. A lot faster and easier than writting them all down by hand.

Will be added to a later application to allow a single game to be added.

The data is downloaded from the [Giant Bomb Database](http://www.giantbomb.com/games/), since it is a well maintained, easily accessed, and up to date.

The app only uses default python libraries, you shouldn't need to install any packages.

It would be nice to get the video game's score from [Metacritic](http://www.metacritc.com/) and the Estimated Play time from [How Long to Beat](http://www.howlongtobeat.com/)

####To use:
0. Get an API key from [here](https://auth.giantbomb.com/signup/), and make it equal to api_key on line 37 of videogames.py
1. Add your games to the videogames.txt, one game per line, they don't have to be exact, just close.
2. Rearrange the platforms in PlatformList.txt. Have the platforms you most prefer added to the top, with the first being your most prefered, second be your second, etc..
3. Run the videogames.py script
4. The results will be stored in a .csv file called "Videogames_Found.csv" in the directory you put videogames.py
