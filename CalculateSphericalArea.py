# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

from math import sin
from math import cos
from math import pi
import arcpy


b2, A, B, C, D, E = [0.0] * 6


def InitParams(spatialReference):
    a = spatialReference.GCS.semiMajorAxis
    b = spatialReference.GCS.semiMinorAxis
    e2 = (a * a - b * b) / (a * a)
    e4 = e2 * e2
    e6 = e4 * e2
    e8 = e6 * e2

    global b2, A, B, C, D, E
    b2 = b * b
    A = 1 + (3.0 / 6) * e2 + (30.0 / 80) * e4 + (35.0 / 112) * e6 + (630.0 / 2304) * e8
    B = (1.0 / 6) * e2 + (15.0 / 80) * e4 + (21.0 / 112) * e6 + (420.0 / 2304) * e8
    C = (3.0 / 80) * e4 + (7.0 / 112) * e6 + (180.0 / 2304) * e8
    D = (1.0 / 112) * e6 + (45.0 / 2304) * e8
    E = (5.0 / 2304) * e8


def CalcTrapezoidArea(B1, L1, B2, L2):
    if B2 == B1:
        return 0.0

    B1 *= (pi / 180.0)
    L1 *= (pi / 180.0)
    B2 *= (pi / 180.0)
    L2 *= (pi / 180.0)

    dB = B2 - B1
    dL = (L1 + L2) / 2
    Bm = (B1 + B2) / 2

    sA = A * sin(0.5 * dB) * cos(Bm)
    sB = B * sin(1.5 * dB) * cos(3 * Bm)
    sC = C * sin(2.5 * dB) * cos(5 * Bm)
    sD = D * sin(3.5 * dB) * cos(7 * Bm)
    sE = E * sin(4.5 * dB) * cos(9 * Bm)
    S = 2 * b2 * dL * (sA - sB + sC - sD + sE)

    return -S


def CalcPartArea(part):
    area = 0.0
    for i in range(0, part.count - 1):
        point1 = part[i]
        point2 = part[i + 1]
        if point1 and point2:
            area += CalcTrapezoidArea(point1.Y, point1.X, point2.Y, point2.X)
    return area


def CalcPolygonArea(polygon):
    area = 0.0
    for part in polygon:
        area += CalcPartArea(part)

    return area


def CalcSphericalArea_GDPJ(in_fc, field):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    desc = arcpy.Describe(in_fc)
    if desc.shapeType.lower() != "polygon":
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
        row[1] = CalcPolygonArea(row[0]) / 1000000.0    # unit: km2
        cursor.updateRow(row)
    del cursor


def CalcSphericalArea_ArcGIS(in_fc, field):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    desc = arcpy.Describe(in_fc)
    if desc.shapeType.lower() not in ("polygon", "polyline"):
        arcpy.AddIDMessage("ERROR", 931)
        raise SystemExit()

    if field not in desc.fields:
        arcpy.AddField_management(in_fc, field, "DOUBLE")

    arcpy.CalculateField_management(in_fc, field, "!shape.area@squarekilometers!", "PYTHON_9.3")


def CalcSphericalArea(in_fc, field, method):
    if method.lower() == "gdpj":
        CalcSphericalArea_GDPJ(in_fc, field)
    else:
        CalcSphericalArea_ArcGIS(in_fc, field)


def BatchCalcSphericalArea(gdb):
    arcpy.env.workspace = gdb
    fcs = arcpy.ListFeatureClasses(feature_type="polygon")
    for fc in fcs:
        CalcSphericalArea(fc, "A10", "arcgis")


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    field = arcpy.GetParameterAsText(1)
    method = arcpy.GetParameterAsText(2)

    CalcSphericalArea(in_fc, field, method)
