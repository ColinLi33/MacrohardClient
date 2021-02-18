import time
import requests
import sys
import base64
import math
import os
import keyboard
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from flask import json
from threading import Thread
from pynput import keyboard
from PIL import Image
from PIL import ImageFont, ImageDraw
import platform
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy import interpolate
from scipy.interpolate import make_interp_spline, BSpline
from scipy.ndimage.filters import gaussian_filter1d
from shutil import copyfile
from gold_diff import generate_gold_diff_graph, save_diff_data  # , save_history
from keyboardInput import KeyboardInput
from matplotlib import cm
from shutil import copyfile
import globalsVars
import matplotlib.font_manager as font_manager



class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


data = -1


def print_to_cloud():
    toolbar_width = 40

    print("Connecting to Macrohard cloud: ", end="")
    # setup toolbar
    def lololol(tt):
        sys.stdout.write("[%s]" % (" " * toolbar_width))
        sys.stdout.flush()
        sys.stdout.write(
            "\b" * (toolbar_width + 1)
        )  # return to start of line, after '['
        for i in range(toolbar_width):
            time.sleep(tt)  # do real work here
            # update the bar
            sys.stdout.write("-")
            sys.stdout.flush()
        sys.stdout.write("]\n")  # this ends the progress bar

    lololol(0.05)
    print(bcolors.OKGREEN + "Succesfully connected to cloud: ", bcolors.ENDC)

    time.sleep(0.3)
    print("Starting up nodes", end="")
    lololol(0.1)

    print("Connecting nodes", end="")
    lololol(0.01)

    print(bcolors.OKGREEN + "Nodes have been connected: ", bcolors.ENDC)

    print("Checking for GPU", end="")
    lololol(0.02)

    print(bcolors.OKGREEN + "Starting main thread: ", bcolors.ENDC, end="")
    lololol(0.05)


def writeToFile(file, data):
    f = open("./data/" + file + ".txt", "a+")
    f.truncate(0)
    f.write(str(data))
    f.close()


def baronPowerPlayLogic(powerPlay, blue, red):
    if blue:
        f = open("./data/bluePowerPlay.txt", "a+")
        f.truncate(0)
        f.write(str(powerPlay[0]))
        f.close()
        if os.path.exists("./data/redPowerPlay.txt"):
            os.remove("./data/redPowerPlay.txt")
    elif red:
        f = open("./data/redPowerPlay.txt", "a+")
        f.truncate(0)
        f.write(str(powerPlay[1]))
        f.close()
        if os.path.exists("./data/bluePowerPlay.txt"):
            os.remove("./data/bluePowerPlay.txt")
    # no power play so delete the files
    else:
        if os.path.exists("./data/bluePowerPlay.txt"):
            os.remove("./data/bluePowerPlay.txt")
        if os.path.exists("./data/redPowerPlay.txt"):
            os.remove("./data/redPowerPlay.txt")

# READ CODE
def readFromCloud():
    URL = "http://3.135.63.97:3333/"
    num_requests = 0
    initialDamage = []
    # save_history(requests.get(url=URL + "get_history").content)
    while True:
        print("request:", num_requests)
        num_requests += 1
        frame = requests.get(url=URL + "get_data")
        if frame.content == b"-1\n":
            print(bcolors.FAIL + "No active game being sent to cloud", bcolors.ENDC)
        else:
            # print(bcolors.OKGREEN + "Downloaded Frame", bcolors.ENDC)
            global data
            data = base64.b64decode(frame.content)
            data = json.loads(data)
            dataToWrite = {
                "Gametime": data["inGameTimer"],
                "DragonTimer": data["dragonTimer"],
                "BaronTimer": data["baronTimer"],
                "BlueGold": data["team"][0]["gold"],
                "RedGold": data["team"][1]["gold"],
                "BlueTowers": data["team"][0]["towers"],
                "RedTowers": data["team"][1]["towers"],
                "BlueKills": data["team"][0]["kills"],
                "RedKills": data["team"][1]["kills"],
            }
            for x in dataToWrite.keys():
                writeToFile(x, dataToWrite[x])
            baronPowerPlayLogic(
                [data["team"][0]["baronPowerPlay"], data["team"][1]["baronPowerPlay"]],
                data["team"][0]["powerPlay"],
                data["team"][1]["powerPlay"],
            )
            save_diff_data(data)
            check_current_keys()


def check_current_keys():
    print(
        globalsVars.teamFight,
        globalsVars.showGold,
        globalsVars.showXP,
        globalsVars.showGoldDiff,
    )
    if globalsVars.teamFight == 1:  # Team fight gold
            print('teamfight started')
            globalsVars.teamfightdmg = []
            for x in range(2):
                for p in range(5):
                    globalsVars.teamfightdmg.append(data["team"][x]["players"][p]["TOTAL_DAMAGE_DEALT_TO_CHAMPIONS"])
    elif globalsVars.showGold:  # total gold
        get_currentStats("gold")
    elif globalsVars.showXP:  # total XP
        get_currentStats("experience")
    elif globalsVars.showGoldDiff:
        generate_gold_diff_graph()
    elif globalsVars.teamFight == 2:
        print('teamfight ended')
        teamfightDamage()
        globalsVars.teamFight = 2.5
    elif globalsVars.teamFight == 3:
        print('delete teamfight file')
        while(True):
            try:
                os.remove('./data/teamFightDmg.png')
                globalsVars.teamFight = 0
                break
            except FileNotFoundError:
                break
            except:
                print('SLLOW DOWN BUDDY')



def get_currentStats(stat):
    fig, ax = plt.subplots(figsize=(3.05, 6.93))
    statArrayDict = {}
    title_text = ""
    cumulativeXP = [
        0,
        280,
        660,
        1140,
        1720,
        2400,
        3180,
        4060,
        5040,
        6120,
        7300,
        8580,
        9960,
        11440,
        13020,
        14700,
        16480,
        18360,
    ]
    if stat == "gold":
        title_text = "Current Gold"
        for t in range(2):
            for p in range(5):
                statArrayDict[data["team"][t]["players"][p]["summonerName"]] = (
                    data["team"][t]["players"][p]["championName"],
                    data["team"][t]["players"][p]["totalGold"],
                    data["team"][t]["players"][p]["teamID"],
                )
    elif stat == "experience":
        title_text = "Current EXP"
        for t in range(2):
            for p in range(5):
                statArrayDict[data["team"][t]["players"][p]["summonerName"]] = (
                    data["team"][t]["players"][p]["championName"],
                    data["team"][t]["players"][p]["XP"],
                    data["team"][t]["players"][p]["teamID"],
                )
    statArrayDict = {
        k: v for k, v in sorted(statArrayDict.items(), key=lambda item: item[1][1])
    }
    y_pos = range(10)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(statArrayDict.keys())

    teamColors = [x[2] for x in statArrayDict.values()]
    statTotal = [x[1] for x in statArrayDict.values()]
    championNames = [x[0] for x in statArrayDict.values()]
    currentXPInLevel = []
    playerLevels = []
    if stat == "experience":
        for x in statTotal:
            lvlToAppend = 0
            for i, xp in enumerate(cumulativeXP):
                if x >= xp:
                    lvlToAppend = i + 1
            playerLevels.append(lvlToAppend)
        for i, x in enumerate(statTotal):
            currentXPInLevel.append(x - cumulativeXP[playerLevels[i] - 1])
        statTotal = currentXPInLevel

    barList = ax.barh(np.arange(0, 100, 10), statTotal, height=2.6)

    for i, x in enumerate(teamColors):
        if x == 100:
            barList[i].set_color("b")
        else:
            barList[i].set_color("r")

    plt.axis("off")
    plt.savefig("./data/liveStats/statGraph.png", bbox_inches="tight", transparent=True)
    plt.close("all")
    background = Image.open("./data/graphics/liveStatTemplate.png").convert("RGBA")
    foreground = Image.open("./data/liveStats/statGraph.png")
    background.paste(foreground, (57, 182), foreground)

    title_font = ImageFont.truetype("./data/fonts/big_noodle_titling.ttf", 45)
    text_font = ImageFont.truetype("./data/fonts/Forza-Medium.ttf", 15)
    draw = ImageDraw.Draw(background)
    draw.text((75, 129), title_text, (255, 255, 255), font=title_font)
    names = list(statArrayDict.keys())
    names.reverse()
    statTotal.reverse()
    championNames.reverse()
    playerLevels.reverse()
    adder3000 = [0, 0, -1, 3, 2, 5, 6, 7, 8, 7]
    if stat == "experience":
        statTotal = playerLevels

    for i, x in enumerate(names):
        draw.text((67, 200 + (i * 52.4)), x, (255, 255, 255), font=text_font)
        draw.text(
            (250, 200 + (i * 52.4)), str(statTotal[i]), (255, 255, 255), font=text_font
        )
        championImage = Image.open(
            "./data/icon_cirlce/" + championNames[i].lower() + ".png"
        )
        championImage = championImage.resize((46, 45))
        background.paste(championImage, (9, 185 + adder3000[i] + int((51.6 * i))))

    background.save("./data/liveStats/LiveStats_temp.png")
    if globalsVars.showGold == True or globalsVars.showXP == True:
        copyfile("./data/liveStats/LiveStats_temp.png", "./data/LiveStats.png")

def teamfightDamage():
    playerNames = []
    dmgDiff = []
    dmgDiffBlue = []
    dmgDiffRed = []
    bluePlayers = []
    redPlayers = []
    champArray = []
    for x in range(2):
        for p in range(5):
            playerNames.append(data["team"][x]["players"][p]["summonerName"])
            dmgDiff.append(data["team"][x]["players"][p]["TOTAL_DAMAGE_DEALT_TO_CHAMPIONS"] - globalsVars.teamfightdmg[5 * x + p])
            champArray.append( data["team"][x]["players"][p]["championName"])
    for x in range(10):
        if x < 5:
            dmgDiffBlue.append(dmgDiff[x])
            bluePlayers.append(playerNames[x])
        else:
            dmgDiffRed.append(dmgDiff[x])
            redPlayers.append(playerNames[x])
    dmgDiff = [dmgDiffBlue,dmgDiffRed]
    playerNames = [bluePlayers, redPlayers]
    print(dmgDiff)
    fig,ax = plt.subplots(nrows=1, ncols=2,figsize=(8.3, 2.7))
    fig.tight_layout()
    for x in range(2):
        y_pos = np.arange(len(playerNames[x]))
        if(x == 0):
            ax[x].barh(y_pos, dmgDiff[x], align='center',color='blue',height = .5)
        else:
            ax[x].barh(y_pos, dmgDiff[x], align='center',color='red',height = .5)
        ax[x].set_yticks(y_pos)
        ax[x].invert_yaxis()
        ax[x].axis("off")

        text_font = font_manager.FontProperties(fname="./data/fonts/Forza-Medium.ttf")
        #print(text_font)
        
        for index, value in enumerate(dmgDiff[x]):
            if(x == 0):
                ax[x].text(value + 10, index, str(int(value)),verticalalignment='center', horizontalalignment='left',color='white', fontsize=10,fontproperties=text_font)
            else:
                ax[x].text(value + 10, index, str(int(value)),verticalalignment='center', horizontalalignment='right',color='white', fontsize=10,fontproperties=text_font)

    ax[1].invert_xaxis()
    plt.savefig('./data/livestats/teamfightdmg.png', bbox_inches="tight", transparent=True)
    plt.close('all')
    background = Image.open("./data/graphics/dmg dealt last.png").convert("RGBA")
    foreground = Image.open("./data/liveStats/teamfightdmg.png")
    background.paste(foreground, (575, 850), foreground)

    title_font = ImageFont.truetype("./data/fonts/big_noodle_titling.ttf", 45)
    text_font = ImageFont.truetype("./data/fonts/Forza-Medium.ttf", 15)

    draw = ImageDraw.Draw(background)
    draw.text((780, 793), 'Damage Dealt Last Fight', (255, 255, 255), font=title_font)
    for i, x in enumerate(champArray):
        championImage = Image.open("./data/icon_cirlce/" + x.lower() + ".png")
        championImage = championImage.resize((37, 37))
        if(i < 5):
            background.paste(championImage, (538, 860 + int((43 * i))))
        else:
            background.paste(championImage, (1358, 860 + int((43 * (i-5)))))
    
    background.save("./data/liveStats/teamfight_temp.png")
    if(globalsVars.teamFight == 2):
        copyfile("./data/liveStats/teamfight_temp.png", "./data/teamFightDmg.png")



if __name__ == "__main__":
    # print_to_cloud()
    plt.switch_backend("agg")
    globalsVars.system = platform.system()

    keyboard = KeyboardInput([("'t'", "<188>"), ("'g'", "<190>"), ("'e'", "<191>")])
    keyboard.start()
    # while True:
    # time.sleep(1)
    # print(globalsVars.teamFight, globalsVars.showGold, globalsVars.showXP)
    # start to listen on a separate thread
    #  listener.join()  # remove if main thread is polling self.keys
    readFromCloud()

