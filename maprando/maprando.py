"""
A little script to create personalized maps from my Strava activities.
"""

# standard imports
import os
import argparse

# third party imports
import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
from scipy import signal

# local imports
from utils import read_gpx


def maprando(input_file, output_file, title=None):
    """
    Create personalized maps from my Strava activities.
    Input:
        -input_file         str
        -output_file        str
            pdf
        -title              str
    """

    # read gpx file
    activity_date, activity_name, xmin, xmax, ymin, ymax, points = read_gpx(input_file)

    # get coordinates of points in meters (projected in EPSG 3857)
    projected_coords = ccrs.epsg(3857).transform_points(
        ccrs.PlateCarree(),
        np.asarray(points["lon"]),
        np.asarray(points["lat"])
    )

    # add velocity (in km/h) to points dataframe
    gradient = np.gradient( # compute gradient
        projected_coords[:, :2],
        points["time"],
        axis=0
    )
    gradient *= 3.6 # convert form m/s to km/h
    points["vel"] = np.array([norm(v) for v in gradient]) # add to dataframe

    # filter velocity
    b, a = signal.butter(3, 0.01) # get Butterworth filter coefficients
    points["vel"] = signal.filtfilt(b, a, points["vel"]) # apply forward and backward filter

    # create figure
    fig = plt.figure(figsize=(16, 12), dpi=100)

    # create geo axes
    geo_axes = plt.axes(projection=ccrs.PlateCarree())

    # plot points
    plt.scatter(
        points["lon"],
        points["lat"],
        c=points["vel"],
        cmap="RdBu_r",
        linewidth=1,
        marker="o",
        transform=ccrs.PlateCarree(),
    )

    # add colorbar
    cbar = plt.colorbar(shrink=0.4)
    cbar.set_label("Walking speed (km/h)")

    # add open street map background
    osm_background = cimgt.OSM()
    geo_axes.add_image(osm_background, 15)

    # add gridlines
    gridlines = geo_axes.gridlines(
        draw_labels=True,
    )
    gridlines.top_labels = False
    gridlines.right_labels = False
    gridlines.xformatter = FormatStrFormatter("%.3f°E")
    gridlines.yformatter = FormatStrFormatter("%.4f°N")

    # add title
    if title is not None:
        plt.title(title)

    # save map
    plt.savefig(output_file)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    required_arguments = parser.add_argument_group("required arguments")
    required_arguments.add_argument("-i", "--input_file", help="input gpx file", required=True)
    required_arguments.add_argument(
        "-o", "--output_file", help="output pdf file", required=True
    )
    parser.add_argument("-t", "--title")
    args = parser.parse_args()

    maprando(
        args.input_file,
        args.output_file,
        args.title,
    )
