# top_woodcutting_bot

Bot for auto woodcutting inside Tales of Pirates game.

Program has 3 main components:

 - Windows
 - Game World
 - Trees

The main process to repeat indefinitely is:

Iterate through declared game client windows (as this bot can handle multiple windows and farm wood on each of them), which are saved on an array, and contains a pair of (X,Y) points which represent the window location on screen, using **pyautogui** click on the ith current window in order to put it on top and focus it.

Next, take game screenshot based on a fixed game client width and height, using the **OpenCV** lib, search in the current screenshot for any of the preloaded images on the assets folder, using the **matchTemplate** function from lib, passing the TM_CCOEFF_NORMED method, which proved to be the best one for in-game tree detection after multiple tests.

Tree image to search in world:

![Tree](https://github.com/steelherrera/top_woodcutting_bot/blob/master/assets/second_match.png?raw=true)

Following is an example of detected trees inside world, with a point on the center of each rectangle drawed after detection:

![World_Detected_Trees](https://drive.google.com/uc?export=download&id=1Kec4RB-fzOJ4nptC0vWhkW4_xgIoycrE)

Once this process is completed, bot must pick the best tree (acoording to how many matches it got from asset image) and click over it in order to cut it down, wait until it has been cut down and loop through this process over and over.

If at any moment, for any reason (e.g miss tree detection) character gets lost, it can walk back to the center tree farm point.

This rellocation function is embedded in the .py **rellocate_character** and basically what it does, is getting coordinates through taking a picture of coordinates located on the mini map (which is in the right above corner), and using the **pytesseract** transform this image coordinates to text.

After getting the current coordinates, detects if character needs to walk up, down, left or right, comparing the current coordinates to the target coordinates which are another property of the game client window.

The next step is to walk in the direction defined by the previous comparison, at a given rate, wait until character has finished moving and then check if target has been reached, if not, repeat process until character reaches target.

There can be a point where the character finds an obstruction from a game object, and can't move because of it, the bot is able to detect this comparing the current coordinates with the last coordinates, if this has not changed, then the player is stuck and in collision with another object, to solve this, the **rate of movement** (this property defines how fast character moves until he reaches his target) is increased in a fixed amount on each iteration, until character evades the obstacle and keep walking, then the **rate of movement** is resetted to its predefined value.