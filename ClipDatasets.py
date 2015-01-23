# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import multiprocessing
import arcpy


def ClipDataset(dataset, clip_fc, out_dir):
    arcpy.env.scratchWorkspace = out_dir
    desc = arcpy.Describe(dataset)
    outName = out_dir + "\\" + desc.baseName

    if desc.DatasetType == "FeatureClass":
        arcpy.Clip_analysis(dataset, clip_fc, outName)
    elif desc.DatasetType == "RasterDataset":
        outRaster = arcpy.sa.ExtractByMask(dataset, clip_fc)
        outRaster.save(outName)


def StartTask(in_datasets, in_fc, field, uid, year, out_dir):
    arcpy.env.overwriteOutput = True

    # prepare clip featureclass
    where_clause = "\"{0}\"='{1}'".format(field, uid)
    arcpy.FeatureClassToFeatureClass_conversion(in_fc, out_dir, uid, where_clause)
    clip_fc = "{0}\\{1}.shp".format(out_dir, uid)

    # prepare out gdb
    gdb_name = "{0}_{1}.gdb".format(uid, year)
    out_gdb = "{0}\\{1}".format(out_dir, gdb_name)
    if not arcpy.Exists(out_gdb):
        arcpy.CreateFileGDB_management(out_dir, gdb_name)

    # clip datasets
    for dataset in in_datasets:
        ClipDataset(dataset, clip_fc, out_gdb)

    # clean clip featureclass
    arcpy.Delete_management(clip_fc)


def ClipDatasets(in_datasets, in_fc, field, year, out_dir):
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool()

    ids = [row[0] for row in arcpy.da.SearchCursor(in_fc, [field])]
    uids = set(ids)
    for uid in uids:
        pool.apply_async(StartTask, (in_datasets, in_fc, field, uid, year, out_dir))
        #StartTask(in_datasets, in_fc, field, uid, year, out_dir)

    pool.close()
    pool.join()


if __name__ == "__main__":
    in_datasets = arcpy.GetParameterAsText(0).split(";")
    in_fc = arcpy.GetParameterAsText(1)
    field = arcpy.GetParameterAsText(2)
    year = arcpy.GetParameterAsText(3)
    out_dir = arcpy.GetParameterAsText(4)

    ClipDatasets(in_datasets, in_fc, field, year, out_dir)
