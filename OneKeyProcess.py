# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import multiprocessing
import arcpy
from CalculateSphericalArea import BatchCalcSphericalArea
from CalculateSphericalLength import BatchCalcSphericalLength
from RasterToSurface import BatchRasterToSurface
from CalculateSurfaceArea import BatchCalcSurfaceArea
from CalculateSurfaceLength import BatchCalcSurfaceLength


def StartTask(gdb):
    BatchCalcSphericalArea(gdb)
    BatchCalcSphericalLength(gdb)
    BatchRasterToSurface(gdb)
    #BatchCalcSurfaceArea(gdb)
    #BatchCalcSurfaceLength(gdb)


def OneKeyProcess(in_gdbs):
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool()

    for gdb in in_gdbs:
        pool.apply_async(StartTask, (gdb, ))

    pool.close()
    pool.join()


if __name__ == "__main__":
    in_gdbs = arcpy.GetParameterAsText(0).split(";")

    OneKeyProcess(in_gdbs)
