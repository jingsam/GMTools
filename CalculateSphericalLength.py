# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import arcpy


def CalcSphericalLength(in_fc, field):
    if not arcpy.Exists(in_fc):
        arcpy.AddIDMessage("ERROR", 110, in_fc)
        raise SystemExit()

    desc = arcpy.Describe(in_fc)
    if desc.shapeType.lower() not in ("polygon", "polyline"):
        arcpy.AddIDMessage("ERROR", 931)
        raise SystemExit()

    if field not in desc.fields:
        arcpy.AddField_management(in_fc, field, "DOUBLE")

    arcpy.CalculateField_management(in_fc, field, "!shape.length@kilometers!", "PYTHON_9.3")


def BatchCalcSphericalLength(gdb):
    arcpy.env.workspace = gdb
    fcs = arcpy.ListFeatureClasses(feature_type="polygon") + arcpy.ListFeatureClasses(feature_type="polyline")
    for fc in fcs:
        CalcSphericalLength(fc, "L10")

if __name__ == "__main__":
    inpu_fc = arcpy.GetParameterAsText(0)
    field = arcpy.GetParameterAsText(1)

    CalcSphericalLength(inpu_fc, field)