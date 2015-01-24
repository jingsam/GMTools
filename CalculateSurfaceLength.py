# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

from math import sin
from math import cos
from math import pi
import arcpy


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


def CalcLineLength(B1, L1, H1, B2, L2, H2):
    X1, Y1, Z1 = BLH2XYZ(B1, L1, H1)
    X2, Y2, Z2 = BLH2XYZ(B2, L2, H2)

    return ((X1 - X2)**2 + (Y1 - Y2)**2 + (Z1 - Z2)**2) ** 0.5


def GetHeight(point, dem):
    result = arcpy.GetCellValue_management(dem, str(point))
    valuestr = result.getOutput(0)

    return float(valuestr) if valuestr != "NoData" else 0.0


def CalcPartLength(part, dem):
    length = 0.0
    for i in range(0, part.count - 1):
        point1 = part[i]
        point2 = part[i + 1]
        if point1 and point2:
            H1 = GetHeight(point1, dem)
            H2 = GetHeight(point2, dem)
            length += CalcLineLength(point1.Y, point1.X, H1, point2.Y, point2.X, H2)
    return length


def CalcShapeLength(shape, dem):
    length = 0.0
    for part in shape:
        length += CalcPartLength(part, dem)

    return length


def CalcSurfaceLength(in_fc, dem, field):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    if not arcpy.Exists(dem):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    desc = arcpy.Describe(in_fc)
    if desc.shapeType.lower() not in ("polygon", "polyline"):
        arcpy.AddIDMessage("ERROR", 931)
        raise SystemExit()

    if desc.spatialReference.name == "Unknown":
        arcpy.AddIDMessage("ERROR", 1024)
        raise SystemExit()

    InitParams(desc.spatialReference)

    if field not in desc.fields:
        arcpy.AddField_management(in_fc, field, "DOUBLE")

    cursor = arcpy.da.UpdateCursor(in_fc, ["SHAPE@", field], spatial_reference=desc.spatialReference.GCS)
    for row in cursor:
        row[1] = CalcShapeLength(row[0], dem) / 1000.0   # unit: km
        cursor.updateRow(row)
    del cursor


def BatchCalcSurfaceLength(gdb):
    arcpy.env.workspace = gdb
    fcs = arcpy.ListFeatureClasses(feature_type="polygon") + arcpy.ListFeatureClasses(feature_type="polyline")
    for fc in fcs:
        CalcSurfaceLength(fc, "DEM", "L20")


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    dem = arcpy.GetParameterAsText(1)
    field = arcpy.GetParameterAsText(2)
    CalcSurfaceLength(in_fc, dem, field)
