# -*- coding: utf-8 -*-
__author__ = 'jingsam@163.com'

import arcpy
from RasterToSurface import *

def CreateTriangledNetwork(inputWorkspaces, outputName):
    for workspace in inputWorkspaces:
        arcpy.env.workspace = workspace
        dem = arcpy.ListRasters("DEM")[0]
        RasterToSurface()



if __name__ == "__main__":
    inputWorkspaces = arcpy.GetParameterAsText(0).split(";")
    outputName = arcpy.GetParameterAsText(1)
