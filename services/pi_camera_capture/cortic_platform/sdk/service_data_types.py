""" 
COPYRIGHT_NOTICE:
Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, 2022-2023
COPYRIGHT_NOTICE
"""

from enum import IntEnum


class ServiceDataTypes(IntEnum):
    CvFrame = 0
    NumpyArray = 1
    Int = 2
    Float = 3
    String = 4
    Boolean = 5
    List = 6
    Json = 7
