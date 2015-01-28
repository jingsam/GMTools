# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import arcpy


def CalcSurfaceArea(in_fc, surface, area_field, out_field):
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

    if not arcpy.Exists(surface):
        arcpy.AddIDMessage("ERROR", 110, surface)
        raise SystemExit()

    if not out_field:
        out_field = area_field

    fieldmap = arcpy.FieldMap()
    fieldmap.addInputField(surface, area_field)
    fieldmap.mergeRule = "Sum"

    fieldmap.outputField.name = out_field

    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addFieldMap(fieldmap)

    result = arcpy.SpatialJoin_analysis(in_fc, surface, "#",
                                        field_mapping=fieldmappings, match_option="CONTAINS")

    if out_field not in desc.fields:
        arcpy.AddField_management(in_fc, out_field, "DOUBLE")

    cursor1 = arcpy.da.UpdateCursor(in_fc, [out_field])
    cursor2 = arcpy.da.SearchCursor(result, [out_field])
    for row1 in cursor1:
        row2 = cursor2.next()
        if row2[0] is None:
            row1[0] = 0.0
        else:
            row1[0] = row2[0]
        cursor1.updateRow(row1)

    del cursor1, cursor2


def BatchCalcSurfaceArea(gdb):
    arcpy.env.workspace = gdb
    fcs = arcpy.ListFeatureClasses(feature_type="polygon")
    for fc in fcs:
        CalcSurfaceArea(fc, "SURFACE", "A20", "A20")


if __name__ == "__main__":
    in_fc = arcpy.GetParameterAsText(0)
    surface = arcpy.GetParameterAsText(1)
    area_field = arcpy.GetParameterAsText(2)
    out_field = arcpy.GetParameterAsText(3)

    CalcSurfaceArea(in_fc, surface, area_field, out_field)