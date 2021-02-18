import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from flask import json
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy import interpolate
from scipy.interpolate import make_interp_spline, BSpline
from scipy.ndimage.filters import gaussian_filter1d
from PIL import Image
from shutil import copyfile
import globalsVars

minutes = []
gold_diff = []


# def save_history(response):
#     data = json.loads(response)
#     for m in data["game_time"]:
#         minutes.append(convert_igt_to_minutes(m))
#     gold_diff = data["gold_diff"]


def save_diff_data(data):
    blueGold = data["team"][0]["gold"]
    redGold = data["team"][1]["gold"]
    minute = convert_igt_to_minutes(data["inGameTimer"])

    if not minute in minutes:
        gold_diff.append(blueGold - redGold)
        minutes.append(minute)


def generate_gold_diff_graph():
    """Generates a graph of team gold difference.

    Args:
        minutes ([string]): A list of game time strings in minutes:seconds (ex: 4:56)
        gold_diff ([int]): A list of gold differences between teams.
    """
    # Edge case checks
    if gold_diff == [] or minutes == []:
        return

    if len(minutes) >= 1 and minutes[-1] == minutes[-2]:
        return

    if minutes[0] != 0 or gold_diff[0] != 0:
        minutes.insert(0, 0)
        gold_diff.insert(0, 0)

    plt.style.use("dark_background")
    fig, ax = plt.subplots()

    graph_path = "./data/liveStats/gold_diff.png"
    re_w = 1080
    re_h = 210
    try:
        if len(minutes) > 4:
            threshold_plot(
                ax, np.array(minutes), np.array(gold_diff), 0, "red", "#0099e0"
            )

            # Removes negative sign from y values
            ax.yaxis.set_major_formatter(major_formatter)
            # Sets a horizontal line at 0
            ax.axhline()
            ax.set_xlim(0, max(minutes))

            dpi = 96
            plt.rcParams["figure.figsize"] = (re_w / dpi, re_h / dpi)
            plt.grid(which="major", axis="x", alpha=0.5)
            plt.savefig(graph_path, bbox_inches="tight", pad_inches=0, transparent=True)

            plt.clf()
            plt.close()
    except:
        print("Updating gold diff graph skipped.")

    foreground = Image.open(graph_path)
    background = Image.open("./data/graphics/Gold over time.png").convert("RGBA")
    foreground = foreground.resize((re_w, re_h))
    temp_path = "./data/liveStats/GoldOverTime_temp.png"
    background.paste(foreground, (500, 844), foreground)
    background.save(temp_path)
    if globalsVars.showGoldDiff:
        copyfile(temp_path, "./data/GoldOverTime.png")


def threshold_plot(ax, x, y, threshv, color, overcolor):
    """
    Helper function to plot points above a threshold in a different color
    Parameters
    ----------
    ax : Axes
        Axes to plot to
    x, y : array
        The x and y values
    threshv : float
        Plot using overcolor above this value
    color : color
        The color to use for the lower values
    overcolor: color
        The color to use for values over threshv
    """
    f = interpolate.interp1d(x, y)
    f2 = interpolate.interp1d(x, y, kind="cubic")
    x = np.linspace(min(x), max(x), int((x[-1] - x[0]) * 800))
    y = f2(x)

    # Create a colormap for red, green and blue and a norm to color
    # f' < -0.5 red, f' > 0.5 blue, and the rest green
    cmap = ListedColormap([color, overcolor])
    norm = BoundaryNorm([np.min(y), threshv, np.max(y)], cmap.N)

    # Create a set of line segments so that we can color them individually
    # This creates the points as a N x 1 x 2 array so that we can stack points
    # together easily to get the segments. The segments array for line collection
    # needs to be numlines x points per line x 2 (x and y)
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Create the line collection object, setting the colormapping parameters.
    # Have to set the actual values used for colormapping separately.
    lc = LineCollection(segments, cmap=cmap, norm=norm)
    lc.set_array(y)

    ax.add_collection(lc)
    ax.set_xlim(np.min(x), np.max(x))
    ax.set_ylim(np.min(y) * 1.1, np.max(y) * 1.1)

    plt.fill_between(x, 0, y, where=(y - 1) < -1, color="red")
    plt.fill_between(x, 0, y, where=(y - 1) > -1, color="#0099e0")

    return lc


@ticker.FuncFormatter
def major_formatter(x, pos):
    label = str(int(-x)) if x < 0 else str(int(x))
    return label


def convert_igt_to_minutes(inGameTime):
    time = inGameTime.split(":")
    return float(time[0]) + float(time[1]) / 60
