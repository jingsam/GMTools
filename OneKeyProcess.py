# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import sys
import multiprocessing
import arcpy


def ClipDataset(dataset, clipFC, outGDB):
    desc = arcpy.Describe(dataset)
    outName = outGDB + "\\" + desc.baseName

    if desc.DatasetType == "FeatureClass":
        arcpy.Clip_analysis(dataset, clipFC, outName)
    elif desc.DatasetType == "RasterDataset":
        outRaster = arcpy.sa.ExtractByMask(dataset, clipFC)
        outRaster.save(outName)


def ClipDatasets(inputDatasets, inputFC, idField, uid, year, outputDir):
    out_path = arcpy.env.workspace
    out_name = "U" + uid + "_" + year
    where_clause = " \"{0}\" = '{1}' ".format(idField, uid)
    clipFC = arcpy.FeatureClassToFeatureClass_conversion(inputFC, out_path, out_name, where_clause)

    outGDB = CreateGDB(outputDir, uid, year)

    for dataset in inputDatasets:
        ClipDataset(dataset, clipFC, outGDB)


def SetEnvironments(uid, year, outputDir):
    arcpy.env.overwriteOutput = True

    temp_name = "{0}_{1}_Temp.gdb".format(uid, year)
    temp_GDB = arcpy.CreateFileGDB_management(outputDir, temp_name)
    arcpy.env.workspace = temp_GDB
    arcpy.env.scratchWorkspace = temp_GDB


def ClearWorkspace(uid, year, outputDir):
    temp_GDB = "{0}\\{1}_{2}_Temp.gdb".format(outputDir, uid, year)
    arcpy.Delete_management(temp_GDB, "Workspace")


def CreateGDB(uid, year, outputDir):
    out_name = "{0}_{1}.gdb".format(uid, year)
    out_GDB = arcpy.CreateFileGDB_management(outputDir, out_name)

    return out_GDB


def StartTask(inputDatasets, inputFC, idField, uid, year, outputDir):
    SetEnvironments(uid, year, outputDir)

    #ClearWorkspace(uid, year, outputDir)


def OneKeyProcess(inputDatasets, inputFC, idField, year, outputDir):
    #multiprocessing.freeze_support()
    #pool = multiprocessing.Pool()

    ids = [row[0] for row in arcpy.da.SearchCursor(inputFC, [idField])]
    uids = set(ids)
    for uid in uids:
        #pool.apply_async(StartTask, (inputDatasets, inputFC, idField, uid, year, outputDir))
        StartTask(inputDatasets, inputFC, idField, uid, year, outputDir)

    #pool.close()
    #pool.join()


if __name__ == "__main__":
    inputDatasets = arcpy.GetParameterAsText(0).split(";")
    inputFC = arcpy.GetParameterAsText(1)
    idField = arcpy.GetParameterAsText(2)
    year = arcpy.GetParameterAsText(3)
    outputDir = arcpy.GetParameterAsText(4)

    OneKeyProcess(inputDatasets, inputFC, idField, year, outputDir)
