"""
Utils module for maprando.
"""

# standard imports
import argparse
import datetime

# third party imports
import xmltodict
import numpy as np
import pandas as pd
import cartopy.geodesic
from shapely.geometry import LineString


def compute_distance(point_A, point_B):
    """
    Compute distance bewteen two points using cartopy and shapely.
    Coordinates should be: (lon, lat), distance is obtained in meters.
    Inputs:
        -point_A    (float, float)
        -point_B    (float, float)
    Output:
        -distance   float
    """

    # create shapely linestring object
    line = LineString(((point_A[0], point_A[1]), (point_B[0], point_B[1])))

    # create cartopy geodesic
    geodesic = cartopy.geodesic.Geodesic()

    # return distance
    return geodesic.geometry_length(line)


def read_gpx(input_file):
    """
    Read GPX files.
    Input:
        -input_file     str
    Output:
        -activity_date  datetime.datetime object
        -activity_name  str
        -xmin           float
        -xmax           float
        -ymin           float
        -ymax           float
        -points         pandas dataframe
            index: timestamp as datetime object
            columns:
                "lon" (float) (longitude)
                "lat" (float) (latitude)
                "ele" (float) (elevation)
                "time" (float) (time elapsed since activity start in seconds)
    """

    # parse input file
    with open(input_file, "r") as infile:
        data = xmltodict.parse(infile.read())

    # read activity date
    activity_date = datetime.datetime.strptime(
        data["gpx"]["metadata"]["time"], "%Y-%m-%dT%H:%M:%SZ"
    )

    # read activity name
    activity_name = data["gpx"]["trk"]["name"]

    # read points
    points = data["gpx"]["trk"]["trkseg"]["trkpt"]

    # read coordinates bounds
    xmin = 180
    xmax = -180
    ymin = 90
    ymax = -90
    for item in points:

        # convert longitude, latitude, and elevation to float
        item["@lon"] = float(item["@lon"])
        item["@lat"] = float(item["@lat"])
        item["ele"] = float(item["ele"])

        # convert time to datetime object
        item["time"] = datetime.datetime.strptime(item["time"], "%Y-%m-%dT%H:%M:%SZ")

        if item["@lon"] < xmin:
            xmin = item["@lon"]
        if item["@lon"] > xmax:
            xmax = item["@lon"]
        if item["@lat"] < ymin:
            ymin = item["@lat"]
        if item["@lat"] > ymax:
            ymax = item["@lat"]

    # get time elapsed in seconds for each point
    time_elapsed = [(point["time"] - points[0]["time"]).seconds for point in points]

    # store longitude, latitude, and elevation in a numpy array
    array = np.asarray(
        [
            [point["@lon"], point["@lat"], point["ele"], time_elapsed[i]]
            for i, point in enumerate(points)
        ]
    )

    # store points in pandas data frame, with datetime index
    data_frame = pd.DataFrame(
        array,
        index=[point["time"] for point in points],
        columns=["lon", "lat", "ele", "time"],
    )

    return activity_date, activity_name, xmin, xmax, ymin, ymax, data_frame


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-input", required=True)
    args = parser.parse_args()

    activity_date, activity_name, xmin, xmax, ymin, ymax, points = read_gpx(args.input)

    print(
        activity_date,
        activity_name,
        xmin,
        xmax,
        ymin,
        ymax,
        "{} points".format(len(points)),
    )

    print(points)
