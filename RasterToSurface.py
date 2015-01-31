# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

from math import sin
from math import cos
from math import pi
import numpy as np
import os
import arcpy
from arcpy.sa import *


a, e2 = [0.0] * 2


def InitParams(spatialReference):
    global a, e2
    a = spatialReference.GCS.semiMajorAxis
    b = spatialReference.GCS.semiMinorAxis
    e2 = (a * a - b * b) / (a * a)


def BLH2XYZ(B, L, H):
    B *= (pi / 180.0)
    L *= (pi / 180.0)

    N = a / (1 - e2 * sin(B) * sin(B))
    X = (N + H) * cos(B) * cos(L)
    Y = (N + H) * cos(B) * sin(L)
    Z = (N * (1 - e2) + H) * sin(B)

    return X, Y, Z


def CalcTriangleArea(pointA, pointB, pointC):
    if -9999.0 in (pointA[2], pointB[2], pointC[2]):
        return 0.0

    xA, yA, zA = BLH2XYZ(pointA[1], pointA[0], pointA[2])
    xB, yB, zB = BLH2XYZ(pointB[1], pointB[0], pointB[2])
    xC, yC, zC = BLH2XYZ(pointC[1], pointC[0], pointC[2])

    a = (xB - xA, yB - yA, zB - zA)
    b = (xC - xA, yC - yA, zC - zA)

    return ((a[1] * b[2] - a[2] * b[1]) ** 2 +
            (a[2] * b[0] - a[0] * b[2]) ** 2 +
            (a[0] * b[1] - a[1] * b[0]) ** 2) ** 0.5 * 0.5 * 0.000001  # km2


def RasterToSurface(dem, out_fc, field):
    if not arcpy.Exists(dem):
        arcpy.AddIDMessage("ERROR", 110, dem)
        raise SystemExit()

    desc = arcpy.Describe(dem)
    if desc.spatialReference.name == "Unknown":
        arcpy.AddIDMessage("ERROR", 1024)
        raise SystemExit()

    InitParams(desc.spatialReference)
    rowCount, colCount = desc.height, desc.width

    arcpy.env.outputCoordinateSystem = desc.SpatialReference.GCS
    result = arcpy.RasterToPoint_conversion(dem, "DEM2", "Value")
    demArray = arcpy.da.FeatureClassToNumPyArray(result, ("SHAPE@X", "SHAPE@Y", "grid_code")).reshape(
        (rowCount, colCount))
    arcpy.Delete_management(result)

    dtype = np.dtype([('X', '<f4'), ('Y', '<f4'), ('{0}'.format(field), '<f4')])
    surfaceArray = np.zeros(((rowCount - 1) * 2, (colCount - 1)), dtype)

    for row in xrange(0, rowCount - 1):
        for col in xrange(0, colCount - 1):
            pointA = demArray[row, col]
            pointB = demArray[row, col + 1]
            pointC = demArray[row + 1, col + 1]
            pointD = demArray[row + 1, col]

            xABC = (pointA[0] + pointB[0] + pointC[0]) / 3.0
            yABC = (pointA[1] + pointB[1] + pointC[1]) / 3.0
            sABC = CalcTriangleArea(pointA, pointB, pointC)
            surfaceArray[row * 2, col] = (xABC, yABC, sABC)

            xADC = (pointA[0] + pointD[0] + pointC[0]) / 3.0
            yADC = (pointA[1] + pointD[1] + pointC[1]) / 3.0
            sADC = CalcTriangleArea(pointA, pointD, pointC)  # unit: km2
            surfaceArray[row * 2 + 1, col] = (xADC, yADC, sADC)

    arcpy.da.NumPyArrayToFeatureClass(surfaceArray.reshape((rowCount - 1) * (colCount - 1) * 2, ),
                                      out_fc, ["X", "Y"], desc.spatialReference.GCS)


def BatchRasterToSurface(gdb):
    arcpy.env.overwriteOutput = True
    arcpy.env.workspace = gdb
    dem = gdb + "\\DEM"
    out_fc = gdb + "\\SURFACE"
    RasterToSurface(dem, out_fc, "A20")


if __name__ == "__main__":
    dem = arcpy.GetParameterAsText(0)
    out_fc = arcpy.GetParameterAsText(1)
    field = arcpy.GetParameterAsText(2)

    RasterToSurface(dem, out_fc, field)