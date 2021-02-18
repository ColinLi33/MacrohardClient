import keyboard
from pynput import keyboard
import platform
import globalsVars
import os

class KeyboardInput(object):
    def __init__(self, keys):
        self.keys = keys

    def start(self):
        tListener = keyboard.Listener(on_press=self.listen)
        tListener.start()

    def listen(self, key):
        keys_to_check = []
        if globalsVars.system == "Linux":
            keys_to_check = ["'t'", "'g'", "'e'", "'d"]
        elif globalsVars.system == "Windows":
            # CTRL + ',' '.' '/' ''' respctively
            keys_to_check = ["<188>", "<190>", "<191>", "<222>"]

        key = str(key)
        if key == keys_to_check[0]:  # Team fight gold
            if(globalsVars.teamFight == 2 or globalsVars.teamFight == 2.5):
                globalsVars.teamFight +=.5
            elif(globalsVars.teamFight < 3):
                globalsVars.teamFight +=1
            else:
                globalsVars.teamFight = 1
        elif key == keys_to_check[1]:  # Individual gold
            globalsVars.showGold = not globalsVars.showGold
            if(globalsVars.showGold == False):
                while(True):
                    try:
                        os.remove('./data/LiveStats.png')
                        break
                    except FileNotFoundError:
                        break
                    except:
                        print('SLLOW DOWN BUDDY')
        elif key == keys_to_check[2]:  # Individual XP
            globalsVars.showXP = not globalsVars.showXP
            if(globalsVars.showXP == False):
                while(True):
                    try:
                        os.remove('./data/LiveStats.png')
                        break
                    except FileNotFoundError:
                        break
                    except:
                        print('SLLOW DOWN BUDDY')
        elif key == keys_to_check[3]:  # Team gold diff
            globalsVars.showGoldDiff = not globalsVars.showGoldDiff
            if(globalsVars.showGoldDiff == False):
                while(True):
                    try:
                        os.remove('./data/GoldOverTime.png')
                        break
                    except FileNotFoundError:
                        break
                    except:
                        print('SLLOW DOWN BUDDY')

