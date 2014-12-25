# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import arcpy


def CalcSurfaceArea(inputFC, surface, areaField, outputField):
    if not arcpy.Exists(inputFC):
        arcpy.AddIDMessage("ERROR", 110, inputFC)
        raise SystemExit()

    desc = arcpy.Describe(inputFC)
    if desc.shapeType.lower() != "polygon":
        arcpy.AddIDMessage("ERROR", 931)
        raise SystemExit()

    if desc.spatialReference.name == "Unknown":
        arcpy.AddIDMessage("ERROR", 1024)
        raise SystemExit()

    if not arcpy.Exists(surface):
        arcpy.AddIDMessage("ERROR", 110, surface)
        raise SystemExit()

    if not outputField:
        outputField = areaField

    fieldmap = arcpy.FieldMap()
    fieldmap.addInputField(surface, areaField)
    fieldmap.mergeRule = "Sum"

    fieldmap.outputField.name = outputField

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addFieldMap(fieldmap)

    result = arcpy.SpatialJoin_analysis(inputFC, surface, "#",
                                        field_mapping=fieldmappings, match_option="CONTAINS")

    if outputField not in desc.fields:
        arcpy.AddField_management(inputFC, outputField, "DOUBLE")

    cursor1 = arcpy.da.UpdateCursor(inputFC, [outputField])
    cursor2 = arcpy.da.SearchCursor(result, [outputField])
    for row in cursor1:
        row[0] = (cursor2.next()[0] / 1000000.0)
        cursor1.updateRow(row)

    del cursor1, cursor2


if __name__ == "__main__":
    inputFC = arcpy.GetParameterAsText(0)
    surface = arcpy.GetParameterAsText(1)
    areaField = arcpy.GetParameterAsText(2)
    outputField = arcpy.GetParameterAsText(3)

    CalcSurfaceArea(inputFC, surface, areaField, outputField)