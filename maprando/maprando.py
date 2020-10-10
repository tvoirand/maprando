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

# local imports
from utils import read_gpx


def maprando(input_file, output_file, background_file=None, logos_file=None):
    """
    Create personalized maps from my Strava activities.
    Input:
        -input_file         str
        -output_file        str
            pdf
        -background_file    str
            to use a georeferenced image file as background
        -logos_file         str
            image file to insert logo in the map
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
    vel = np.asarray(points["vel"])
    vel[vel>6] = 6
    vel[vel<2] = 2
    points["vel"] = vel

    # create figure
    fig = plt.figure(figsize=(8, 6), dpi=100)

    # create geo axes
    geo_axes = plt.axes(projection=ccrs.PlateCarree())

    # plot points
    plt.scatter(
        points["lon"],
        points["lat"],
        c=points["vel"],
        cmap="viridis",
        linewidth=1,
        marker="o",
        alpha=0.8,
        transform=ccrs.PlateCarree(),
    )

    # add colorbar
    cbar = plt.colorbar()

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

    # show map
    plt.show()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    required_arguments = parser.add_argument_group("required arguments")
    required_arguments.add_argument("-input_file", help="input gpx file", required=True)
    required_arguments.add_argument(
        "-output_file", help="output pdf file", required=True
    )
    parser.add_argument("-background_file", help="background image file")
    parser.add_argument("-logos_file", help="logos image file")
    args = parser.parse_args()

    maprando(
        args.input_file,
        args.output_file,
        args.background_file,
        args.logos_file,
    )
