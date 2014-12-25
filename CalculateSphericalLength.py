# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy


def calcSphericalLength_ArcGIS(inputFC, fieldName):
    if not arcpy.Exists(inputFC):
        arcpy.AddIDMessage("ERROR", 110, inputFC)
        raise SystemExit()

    desc = arcpy.Describe(inputFC)
    if desc.shapeType.lower() not in ("polygon", "polyline"):
        arcpy.AddIDMessage("ERROR", 931)
        raise SystemExit()

    if fieldName not in desc.fields:
        arcpy.AddField_management(inputFC, fieldName, "DOUBLE")

    arcpy.CalculateField_management(inputFC, fieldName, "!shape.length@kilometers!", "PYTHON_9.3")


if __name__ == "__main__":
    inputFC = arcpy.GetParameterAsText(0)
    fieldName = arcpy.GetParameterAsText(1)
    method = arcpy.GetParameterAsText(2).lower()
    if method == "gdpj":
        calcSphericalLength_ArcGIS(inputFC, fieldName)
    else:
        calcSphericalLength_ArcGIS(inputFC, fieldName)