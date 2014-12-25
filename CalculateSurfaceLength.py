# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

from math import sin
from math import cos
from math import pi
import arcpy


a, e2 = [0.0] * 2


def initParams(spatialReference):
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


def calcLineLength(B1, L1, H1, B2, L2, H2):
    X1, Y1, Z1 = BLH2XYZ(B1, L1, H1)
    X2, Y2, Z2 = BLH2XYZ(B2, L2, H2)

    return ((X1 - X2)**2 + (Y1 - Y2)**2 + (Z1 - Z2)**2) ** 0.5


def getHeight(point, dem):
    result = arcpy.GetCellValue_management(dem, point, "1")
    height = float(result.getOutput(0))

    return height


def calcPartLength(part, dem):
    length = 0.0
    for i in range(0, part.count - 1):
        point1 = part[i]
        point2 = part[i + 1]
        if point1 and point2:
            H1 = getHeight(point1, dem)
            H2 = getHeight(point2, dem)
            length += calcLineLength(point1.Y, point1.X, H1, point2.Y, point2.X, H2)
    return length


def calcShapeLength(shape, dem):
    length = 0.0
    for part in shape:
        length += calcPartLength(part, dem)

    return length


def calcSurfaceLength(inputFC, dem, fieldName):
    if not arcpy.Exists(inputFC):
        arcpy.AddIDMessage("ERROR", 110, inputFC)
        raise SystemExit()

    if not arcpy.Exists(dem):
        arcpy.AddIDMessage("ERROR", 110, inputFC)
        raise SystemExit()

    desc = arcpy.Describe(inputFC)
    if desc.shapeType.lower() not in ("polygon", "polyline"):
        arcpy.AddIDMessage("ERROR", 931)
        raise SystemExit()

    if desc.spatialReference.name == "Unknown":
        arcpy.AddIDMessage("ERROR", 1024)
        raise SystemExit()

    initParams(desc.spatialReference)

    if fieldName not in desc.fields:
        arcpy.AddField_management(inputFC, fieldName, "DOUBLE")

    cursor = arcpy.da.UpdateCursor(inputFC, ["SHAPE@", fieldName], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        row[1] = calcShapeLength(row[0], dem) / 1000.0   # unit: km
        cursor.updateRow(row)
    del cursor


if __name__ == "__main__":
    inputFC = arcpy.GetParameterAsText(0)
    dem = arcpy.GetParameterAsText(1)
    fieldName = arcpy.GetParameterAsText(2)
    method = arcpy.GetParameterAsText(2).lower()
    calcSurfaceLength(inputFC, dem, fieldName)
