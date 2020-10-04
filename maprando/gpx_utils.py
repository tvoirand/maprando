"""
Utils module to handle GPX files.
"""

# standard imports
import argparse
import datetime

# third party imports
import xmltodict
import numpy as np
import pandas as pd


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
        -points         [OrderedDict, ...]
            contains for each point:
            ('@lat', float), ('@lon', float), ('ele', float), ('time', '%Y-%m-%dT%H:%M:%SZ')])
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

        if item["@lon"] < xmin:
            xmin = item["@lon"]
        if item["@lon"] > xmax:
            xmax = item["@lon"]
        if item["@lat"] < ymin:
            ymin = item["@lat"]
        if item["@lat"] > ymax:
            ymax = item["@lat"]

    # store longitude, latitude, and elevation in a numpy array
    array = np.asarray([[point["@lon"], point["@lat"], point["ele"]] for point in points])

    # store points in pandas data frame, with datetime index
    data_frame = pd.DataFrame(
        array,
        index=[point["time"] for point in points],
        columns=["lon", "lat", "ele"]
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

    print(points["lon"])