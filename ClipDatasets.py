# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import os
import arcpy

def CreateGDB(outputDir, uid, year):
    out_name = "{0}_{1}.gdb".format(uid, year)
    out_GDB = outputDir + "\\" + out_name

    if not arcpy.Exists(out_GDB):
        arcpy.CreateFileGDB_management(outputDir, out_name)

    return out_GDB


def ClipDataset(dataset, clipFC, outGDB):
    arcpy.env.workspace = outGDB
    desc = arcpy.Describe(dataset)
    outName = desc.baseName

    if desc.DatasetType == "FeatureClass":
        arcpy.Clip_analysis(dataset, clipFC, outName)
    elif desc.DatasetType == "RasterDataset":
        outRaster = arcpy.sa.ExtractByMask(dataset, clipFC)
        outRaster.save(outName)


def ClipDatasets(inputDatasets, inputFC, idField, year, outputDir):
    ids = [row[0] for row in arcpy.da.SearchCursor(inputFC, [idField])]
    uids = set(ids)
    arcpy.SetProgressor("step", "Cliping datasets...", 0, len(uids), 1)
    for uid in uids:
        out_path = arcpy.env.scratchWorkspace
        out_name = "TempUnit"
        where_clause = " \"{0}\" = '{1}' ".format(idField, uid)
        clipFC = arcpy.FeatureClassToFeatureClass_conversion(inputFC, out_path, out_name, where_clause)
        outGDB = CreateGDB(outputDir, uid, year)

        for dataset in inputDatasets:
            ClipDataset(dataset, clipFC, outGDB)

        arcpy.DeleteFeatures_management(clipFC)
        arcpy.SetProgressorPosition()


if __name__ == "__main__":
    inputDatasets = arcpy.GetParameterAsText(0).split(";")
    inputFC = arcpy.GetParameterAsText(1)
    idField = arcpy.GetParameterAsText(2)
    year = arcpy.GetParameterAsText(3)
    outputDir = arcpy.GetParameterAsText(4)

    ClipDatasets(inputDatasets, inputFC, idField, year, outputDir)