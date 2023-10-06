# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.

import math

# caller sanitized this
import numpy

import system
import SpectralCurve

cmf1931file = system.resolve_path('data', 'cie/CIE_xyz_1931_2deg.csv')
cmf1964file = system.resolve_path('data', 'cie/CIE_xyz_1964_10deg.csv')
# 2006 data
lms20062degfile = system.resolve_path('data', 'cie/CIE_lms_cf_2deg.csv')
lms200610degfile = system.resolve_path('data', 'cie/CIE_lms_cf_10deg.csv')

# for some reason, the files downloaded from CIE contain NaN values
# they're not useful to us, so we turn them into 0's
cmf1931data = system.readCSV_columns(cmf1931file, NaN_as_zero=True)
cmf1964data = system.readCSV_columns(cmf1964file, NaN_as_zero=True)
lms20062degdata = system.readCSV_columns(lms20062degfile, NaN_as_zero=True)
lms200610degdata = system.readCSV_columns(lms200610degfile, NaN_as_zero=True)


class CMF_1931(object):
    """ Color Matching Functions for the 1931 CIE Standard Observer (2 Degree) """
    xbar = SpectralCurve.SpectralCurve('xbar', cmf1931data[0], cmf1931data[1])
    ybar = SpectralCurve.SpectralCurve('ybar', cmf1931data[0], cmf1931data[2])
    zbar = SpectralCurve.SpectralCurve('zbar', cmf1931data[0], cmf1931data[3])


class CMF_1931_wyman(object):
    xbar = None  # initialized below
    ybar = None
    zbar = None
    @staticmethod
    def _gauss(x):
        return numpy.exp(-x*x / 2)
    
    @staticmethod
    def _dia(lnm, off, b, c):
        a = lnm - off
        return a * (b if a < 0 else c)
    
    @classmethod
    def xbarF(cls, l):
        x1 = cls._dia(l, 442, 0.0624, 0.0374)
        x2 = cls._dia(l, 599.8, 0.0264, 0.0323)
        x3 = cls._dia(l, 501.1, 0.049, 0.0382)
        return 0.362 * cls._gauss(x1) + 1.056 * cls._gauss(x2) - 0.065 * cls._gauss(x3)
    
    @classmethod
    def ybarF(cls, l):
        y1 = cls._dia(l, 568.8, 0.0213, 0.0247)
        y2 = cls._dia(l, 530.9, 0.0613, 0.0322)
        return 0.821 * cls._gauss(y1) + 0.286 * cls._gauss(y2)
    
    @classmethod
    def zbarF(cls, l):
        z1 = cls._dia(l, 437, 0.0845, 0.0278)
        z2 = cls._dia(l, 459, 0.0385, 0.0725)
        return 1.217 * cls._gauss(z1) + 0.681 * cls._gauss(z2)


# initialize outside of class: class methods can only be called on the class, but the class
# doesn't exist until we leave its definition scope, and so we're left with this hackish thing
CMF_1931_wyman.xbar = SpectralCurve.SpectralCurve('xbar',
                                                  CMF_1931.xbar.lnms,
                                                  numpy.array([CMF_1931_wyman.xbarF(x) for x in CMF_1931.xbar.lnms]))
CMF_1931_wyman.ybar = SpectralCurve.SpectralCurve('ybar',
                                                  CMF_1931.ybar.lnms,
                                                  numpy.array([CMF_1931_wyman.ybarF(x) for x in CMF_1931.ybar.lnms]))
CMF_1931_wyman.zbar = SpectralCurve.SpectralCurve('zbar',
                                                  CMF_1931.zbar.lnms,
                                                  numpy.array([CMF_1931_wyman.zbarF(x) for x in CMF_1931.zbar.lnms]))


class CMF_1964(object):
    """ Color Matching Functions for the 1964 CIE Supplementary Standard Observer (10 Degree) """
    xbar = SpectralCurve.SpectralCurve('xbar', cmf1964data[0], cmf1964data[1])
    ybar = SpectralCurve.SpectralCurve('ybar', cmf1964data[0], cmf1964data[2])
    zbar = SpectralCurve.SpectralCurve('zbar', cmf1964data[0], cmf1964data[3])


class CMF_1964_wyman(object):
    xbar = None  # initialized below
    ybar = None
    zbar = None
    
    @staticmethod
    def _gauss(x):
        return numpy.exp(-x*x / 2)
    
    @classmethod
    def xbarF(cls, l):
        x1 = 50 * math.log((l+570.1) / 1014.)
        x2 = math.sqrt(468) * math.log((1338. - l) / 743.5)
        return 0.398 * cls._gauss(x1) + 1.132 * cls._gauss(x2)
    
    @classmethod
    def ybarF(cls, l):
        return 1.011 * cls._gauss((l-556.1) / 46.14)
    
    @classmethod
    def zbarF(cls, l):
        z1 = 8 * math.log((l-265.8) / 180.4)
        return 2.060 * cls._gauss(z1)


# initialize outside of class: class methods can only be called on the class, but the class
# doesn't exist until we leave its definition scope, and so we're left with this hackish thing
CMF_1964_wyman.xbar = SpectralCurve.SpectralCurve('xbar',
                                                  CMF_1964.xbar.lnms,
                                                  numpy.array([CMF_1964_wyman.xbarF(x) for x in CMF_1964.xbar.lnms]))
CMF_1964_wyman.ybar = SpectralCurve.SpectralCurve('ybar',
                                                  CMF_1964.ybar.lnms,
                                                  numpy.array([CMF_1964_wyman.ybarF(x) for x in CMF_1964.ybar.lnms]))
CMF_1964_wyman.zbar = SpectralCurve.SpectralCurve('zbar',
                                                  CMF_1964.zbar.lnms,
                                                  numpy.array([CMF_1964_wyman.zbarF(x) for x in CMF_1964.zbar.lnms]))


class LMS_2006_2deg(object):
    lbar = SpectralCurve.SpectralCurve('lbar', lms20062degdata[0], lms20062degdata[1])
    mbar = SpectralCurve.SpectralCurve('mbar', lms20062degdata[0], lms20062degdata[2])
    sbar = SpectralCurve.SpectralCurve('sbar', lms20062degdata[0], lms20062degdata[3])

class LMS_2006_10deg(object):
    lbar = SpectralCurve.SpectralCurve('lbar', lms200610degdata[0], lms200610degdata[1])
    mbar = SpectralCurve.SpectralCurve('mbar', lms200610degdata[0], lms200610degdata[2])
    sbar = SpectralCurve.SpectralCurve('sbar', lms200610degdata[0], lms200610degdata[3])
