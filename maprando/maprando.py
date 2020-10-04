"""
A little script to create personalized maps from my Strava activities.
"""

# standard imports
import os
import sys
import argparse
import datetime
import dateutil.relativedelta

# third party imports
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.image as mpimg
from matplotlib.ticker import FormatStrFormatter
import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt
import cartopy.geodesic
from shapely.geometry import LineString

# local imports
from gpx_utils import read_gpx


def compute_distance(point_1, point_2):
    """
    Compute distance bewteen two points.
    Coordinates should be: (lon, lat), distance is obtained in meters.
    Inputs:
        -point_1    (float, float)
        -point_2    (float, float)
    Output:
        -distance   float
    """

    # create shapely linestring object
    line = LineString((
        (point_1["@lon"], point_1["@lat"]),
        (point_2["@lon"], point_2["@lat"])
    ))

    # create cartopy geodesic
    geodesic = cartopy.geodesic.Geodesic()

    # return distance
    return geodesic.geometry_length(line)


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

    # create figure
    fig = plt.figure(figsize=(8, 6), dpi=100)

    # create geo axes
    geo_axes = plt.axes(projection=ccrs.PlateCarree())

    # plot points
    plt.plot(
        [float(point["@lon"]) for point in points],
        [float(point["@lat"]) for point in points],
        color="blue",
        linewidth=2,
        marker="o",
        transform=ccrs.Geodetic(),
    )

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
