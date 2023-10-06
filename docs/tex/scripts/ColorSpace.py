# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.

import math

# caller sanitized this
import numpy
    
import CIE
import SpectralCurve

# XYZ1931 to Rec. 709
MRec709 = numpy.array([
        [ 3.2404542, -1.5371385, -0.4985314],
        [-0.96922660, 1.8760108,  0.041556],
        [ 0.0556434, -0.2040259,  1.0572252]
        ])

MRec709inv = numpy.linalg.inv(MRec709)

# XYZ1931 to CIECAT02
MCIECAT02 = numpy.array([
        [ 0.7328, 0.4296, -.1624],
        [-0.7036, 1.6975,  .0061],
        [ 0.0030, 0.0136,  .9834]
    ])
MCIECAT02inv = numpy.linalg.inv(MCIECAT02)
  

def _polyval(coeffs, x):
    """ Horner's rule """
    result = 0.
    for c in coeffs:
        result *= x
        result += c
    return result


def _integral(sc: SpectralCurve.SpectralCurve):
    """ Integral of a curve over its own domain as a function of lambda """
    return numpy.trapz(sc.data, sc.lnms)


def scalar(sc1: SpectralCurve.SpectralCurve, sc2: SpectralCurve.SpectralCurve):
    """ Compute the scalar product of a spectral curve against another """
    return _integral(sc1 * sc2)


def XYZ_sc(sc: SpectralCurve.SpectralCurve, xyzcmf=CIE.CMF_1931):
    return numpy.array([scalar(sc, xyzcmf.xbar),
                        scalar(sc, xyzcmf.ybar),
                        scalar(sc, xyzcmf.zbar)])


def LMS_sc(sc: SpectralCurve.SpectralCurve, lms = CIE.LMS_2006_2deg):
    return numpy.array([scalar(sc,lms.lbar),
                        scalar(sc,lms.mbar),
                        scalar(sc,lms.sbar)])


def RGB_sc(sc: SpectralCurve.SpectralCurve, rgb):
    return numpy.array([scalar(sc, rgb.rbar),
                        scalar(sc, rgb.gbar),
                        scalar(sc, rgb.bbar)])


def XYZ(xy, Y):
    x, y = xy
    X = Y * x / y
    Z = Y * (1 - x - y) / y
    return numpy.array([X, Y, Z])


def xy(XYZ):
    X, Y, Z = XYZ
    x = X / (X+Y+Z)
    y = Y / (X+Y+Z)
    return numpy.array([x,y])


def Make_3x3(out_data, in_data):
    """solve out = M*in for M in a least squares sense
       out is one column per result (np.array, shape = (3,n))
       in is one column per input (np.array, shape = (3,n))
       M is 3x3 """
    
    # in_inv = in^T*(in*in^T)^-1 
    # M = out*in_inv
    in_inv = numpy.dot(in_data.T, numpy.linalg.inv(numpy.dot(in_data, in_data.T)))
    return numpy.dot(out_data, in_inv)


def CCT_McCamy(xy):
    """ McCamy, Calvin S. (April 1992).
        "Correlated color temperature as an explicit function of chromaticity coordinates".
        Color Research & Application 17 (2) """
    n = (xy[0] - 0.332) / (xy[1] - .1858)
    return numpy.polyval([-449., 3525., -6823.3, 5520.33], n)


def _sRGB_g1(v):
    """ sRGB 'gamma' (OETF) v in [0,1] """
    a = 0.055
    return 12.92 * v if v < 0.0031308 else ((1 + a)*pow(v, 1/2.4) - a)


def _sRGB_ung1(v):
    """ sRGB 'ungamma' (EOTF) v in [0,1] """
    a = 0.055
    return v / 12.92 if v <= 0.04045 else pow((v+a) / (1+a), 2.4)


def sRGB_gamma(sRGBl):
    """ Gamma correction for sRGB (linear to display, OETF) """
    return numpy.array((_sRGB_g1(sRGBl[0]),
                        _sRGB_g1(sRGBl[1]),
                        _sRGB_g1(sRGBl[2])))


def sRGB_ungamma(sRGB):
    """ Gamma uncorrection for sRGB (display to linear, EOTF) """
    return numpy.array((_sRGB_ung1(sRGB[0]),
                        _sRGB_ung1(sRGB[1]),
                        _sRGB_ung1(sRGB[2])))


def sRGB(XYZ):
    return sRGB_gamma(Rec709l(XYZ))


def Rec709l(XYZ):
    return numpy.dot(MRec709, XYZ)


def Rec709linv(r709):
    return numpy.dot(MRec709inv, r709)


def CIELAB(XYZ, whitepoint):
    f = lambda t: math.pow(t, 1/3.) if t > (216 / 24389.) else (841 / 108.) * t + (4 / 29.)
    XYZn = XYZ / whitepoint
    L = 116. * f(XYZn[1]) - 16.
    a = 500. * (f(XYZn[0]) - f(XYZn[1]))
    b = 300. * (f(XYZn[1]) - f(XYZn[2]))
    return numpy.array([L,a,b])


def CIELABinv(Lab, whitepoint):
    finv = lambda t: math.pow(t, 3.) if t > (6 / 29.) else (108 / 841.) * (t - (4 / 29.))
    Xn = finv((Lab[0]+16.)/116. + Lab[1] / 500.)
    Yn = finv((Lab[0]+16.)/116.)
    Zn = finv((Lab[0]+16.)/116. - Lab[2] / 200.)
    return numpy.array([Xn,Yn,Zn]) * whitepoint


def CIECAT02(XYZ):
    return numpy.dot(MCIECAT02, XYZ)


def CIECAT02inv(LMS):
    return numpy.dot(MCIECAT02inv, LMS)