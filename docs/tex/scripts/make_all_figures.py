#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.

# this scripts creates all the plots for the physLight document

import sys
import subprocess
import argparse
import os.path
from typing import Any, Dict, Iterable, List, Optional, TextIO, Tuple

import math
import csv
import os

hasNumpy = False
hasPyplot = False

try:
    import numpy
    import numpy.linalg
    hasNumpy = True
except:
    pass
try:
    import matplotlib.pyplot as pyplot
    hasPyplot = True
except:
    pass

if not (hasNumpy and hasPyplot):
    print("Missing dependencies:")
    if not hasNumpy:
        print ("   numpy is needed")
    if not hasPyplot:
        print ("   matplotlib is needed")
    print("Please consult your platform's instruction on how to install these packages")
    exit(1)

import system
datadir = os.path.join(os.path.dirname(__file__),'../figures_src/data/')
system.register_searchpaths("data", [datadir])

import CIE
import SPD
import ColorSpace
import SpectralCurve


def load_spectral_data(fname: str) -> list[SpectralCurve.SpectralCurve]:
    scs: list[SpectralCurve.SpectralCurve] = []
    for row in system.readCSV_rows(fname, NaN_as_zero=True):
        if len(row) == 0 or row[0][0] == "#" or len(row) < 4:
            continue
        scs.append(SpectralCurve.makeFromMinSpcData(row[0], float(row[1]), float(row[2]), [float(x) for x in row[3:]]))
    return scs


def spradiance_to_sRGB(spd: SpectralCurve.SpectralCurve, Y: Optional[float] = None):
    """
    Return the color of an illuminant of the given spectral distribution profile,
    If Y is given and non-0, the curve is normalized to that value in CIE CMF 1931/2deg
    """
    # sample the given spd at the wavelengths of interest
    illum = spd.resample(CIE.CMF_1931.ybar)
    if Y:
        # rescale illuminant to have the illuminance we want
        illumY = ColorSpace.scalar(illum, CIE.CMF_1931.ybar)
        illum *= Y / illumY
    # compute XYZ tristimulus values
    XYZ = ColorSpace.XYZ_sc(illum)
    # convert to our primaries
    rec709l = ColorSpace.Rec709l(XYZ)
    # apply OETF (aka 'gamma')
    sRGB = ColorSpace.sRGB_gamma(rec709l)
    # clip, because matplotlib is real bothered by color values outside [0,1]
    # Note: this is just meant to catch a few bits worth of numerics trouble,
    # it shouldn't engage for a large correction, because that would mean our
    # input was beyond the scale
    sRGB = numpy.clip(sRGB, 0, 1)
    return sRGB


def transmittance_to_sRGB(sc: SpectralCurve.SpectralCurve, Y):
    """
    Return the color of a gel of the given transmittance profile,
    as if lit by D65, normalized so that if vals was [1,...,1] you'd get
    a color for which Y is equal to `Y`.
    Note that only D65 is normalized, the transmittance profile is used
    as given.
    """
    # sample D65 at the wavelengths of interest
    illum = SPD.IlluminantD.getCurve(6504)
    # rescale illuminant to have the illuminance we want
    illumY = ColorSpace.scalar(illum, CIE.CMF_1931.ybar)
    illum *= Y / illumY
    # apply transmittance and compute XYZ tristimulus values
    XYZ = ColorSpace.XYZ_sc(sc*illum)
    # convert to our primaries
    rec709l = ColorSpace.Rec709l(XYZ)
    # apply OETF (aka 'gamma')
    sRGB = ColorSpace.sRGB_gamma(rec709l)
    # clip, because matplotlib is real bothered by color values outside [0,1]
    # Note: this is just meant to catch a few bits worth of numerics trouble,
    # it shouldn't engage for a large correction, because that would mean our
    # input was beyond the scale
    sRGB = numpy.clip(sRGB, 0, 1)
    return sRGB


def plot_curve(axes: pyplot.Axes, sc: SpectralCurve.SpectralCurve, **kwargs):
    """ Little helper to plot a SpectralCurve object into a given pyplot plot, kwargs are forwarded to pyplot.plot """
    axes.plot(sc.lnms, sc.data, **kwargs)


def plot_spectral_locus(args, axes: pyplot.Axes):
    """ Helper to plot pure, single-wavelength hues on a chromaticity diagram """
    wvlngth = []
    cmf = CIE.CMF_1931
    # create the list of xy coordinates of the pure hues
    for X, Y, Z in zip(cmf.xbar.data, cmf.ybar.data, cmf.zbar.data):
        wvlngth.append(ColorSpace.xy((X, Y, Z)))

    # the zip "repacks" all the x's in one array and all the y's in the other
    axes.plot(*zip(*wvlngth), color = 'black', linestyle='-')

    for lnm in numpy.linspace(300, 830, (830-300)//5 + 1):
        # compute dot color at constant-Y
        XYZ = numpy.array([cmf.xbar.sample(lnm),
                           cmf.ybar.sample(lnm),
                           cmf.zbar.sample(lnm)])
        if XYZ[1] > 0:
            XYZ *= args.colorscale*.15 / XYZ[1]
            sRGB = ColorSpace.sRGB(XYZ)
            sRGB = numpy.clip(sRGB, 0, 1)
            xy = ColorSpace.xy(XYZ)
            axes.plot([xy[0]], [xy[1]], color=sRGB, marker='o', markersize=6)


def plot_gamut(args, axes: pyplot.Axes, pts: list[tuple[float,float]], **kwargs):
    for xy in pts:
        col = ColorSpace.sRGB(ColorSpace.XYZ(xy, args.colorscale))
        col = numpy.clip(col, 0, 1)
        pyplot.plot([xy[0]], [xy[1]], color=col, marker='s', markersize=5)

    pts = list(pts) # take a copy
    pts.append(pts[0])
    pyplot.plot(*zip(*pts), **kwargs)


def do_ciexyz1931(args, figure):
    """ Plot the CIE XYZ 1931 dataset into the figure """
    axes = figure.add_subplot(111)

    xcol = transmittance_to_sRGB(CIE.CMF_1931.xbar, args.colorscale)
    ycol = transmittance_to_sRGB(CIE.CMF_1931.ybar, args.colorscale)
    zcol = transmittance_to_sRGB(CIE.CMF_1931.zbar, args.colorscale)

    plot_curve(axes, CIE.CMF_1931.xbar, color=xcol, linestyle='', marker='x', markersize=5)
    plot_curve(axes, CIE.CMF_1931.ybar, color=ycol, linestyle='', marker='x', markersize=5)
    plot_curve(axes, CIE.CMF_1931.zbar, color=zcol, linestyle='', marker='x', markersize=5)

    xcol = transmittance_to_sRGB(CIE.CMF_1931_wyman.xbar, args.colorscale)
    ycol = transmittance_to_sRGB(CIE.CMF_1931_wyman.ybar, args.colorscale)
    zcol = transmittance_to_sRGB(CIE.CMF_1931_wyman.zbar, args.colorscale)

    plot_curve(axes, CIE.CMF_1931_wyman.xbar, color=xcol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.CMF_1931_wyman.ybar, color=ycol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.CMF_1931_wyman.zbar, color=zcol, linestyle='solid', linewidth=1)

    # set up axes
    axes.axis([360,830,0,2])


def do_ciexyz1964(args, figure):
    """ Plot the CIE XYZ 1964 dataset into the figure """
    axes = figure.add_subplot(111)

    xcol = transmittance_to_sRGB(CIE.CMF_1964.xbar, args.colorscale)
    ycol = transmittance_to_sRGB(CIE.CMF_1964.ybar, args.colorscale)
    zcol = transmittance_to_sRGB(CIE.CMF_1964.zbar, args.colorscale)

    plot_curve(axes, CIE.CMF_1964.xbar, color=xcol, linestyle='', marker='x', markersize=5)
    plot_curve(axes, CIE.CMF_1964.ybar, color=ycol, linestyle='', marker='x', markersize=5)
    plot_curve(axes, CIE.CMF_1964.zbar, color=zcol, linestyle='', marker='x', markersize=5)

    xcol = transmittance_to_sRGB(CIE.CMF_1964_wyman.xbar, args.colorscale)
    ycol = transmittance_to_sRGB(CIE.CMF_1964_wyman.ybar, args.colorscale)
    zcol = transmittance_to_sRGB(CIE.CMF_1964_wyman.zbar, args.colorscale)

    plot_curve(axes, CIE.CMF_1964_wyman.xbar, color=xcol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.CMF_1964_wyman.ybar, color=ycol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.CMF_1964_wyman.zbar, color=zcol, linestyle='solid', linewidth=1)

    # set up axes
    axes.axis([360, 830, 0, 2])


def do_cielms2006(args, figure):
    """ Plot the CIE LMS 2006 dataset into the figure """
    axes = figure.add_subplot(111)

    xcol = transmittance_to_sRGB(CIE.LMS_2006_2deg.lbar, args.colorscale)
    ycol = transmittance_to_sRGB(CIE.LMS_2006_2deg.mbar, args.colorscale)
    zcol = transmittance_to_sRGB(CIE.LMS_2006_2deg.sbar, args.colorscale)

    plot_curve(axes, CIE.LMS_2006_2deg.lbar, color=xcol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.LMS_2006_2deg.mbar, color=ycol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.LMS_2006_2deg.sbar, color=zcol, linestyle='solid', linewidth=1)

    xcol = transmittance_to_sRGB(CIE.LMS_2006_10deg.lbar, args.colorscale)
    ycol = transmittance_to_sRGB(CIE.LMS_2006_10deg.mbar, args.colorscale)
    zcol = transmittance_to_sRGB(CIE.LMS_2006_10deg.sbar, args.colorscale)

    plot_curve(axes, CIE.LMS_2006_10deg.lbar, color=xcol, linestyle='--', linewidth=1)
    plot_curve(axes, CIE.LMS_2006_10deg.mbar, color=ycol, linestyle='--', linewidth=1)
    plot_curve(axes, CIE.LMS_2006_10deg.sbar, color=zcol, linestyle='--', linewidth=1)

    # set up axes
    axes.axis([360, 830, 0, 2])


def do_blackbody(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    lnms = numpy.linspace(300, 830, (830-300)//5 + 1)

    Ts = [
        #1800,  # candle
        2855.54,  # household lamp
        3200,  # tungsten halogen
        #4500,  # house fluorescent
        5000,  # horizon light
        #5500,  # midmorning daylight
        6500,  # noon daylight, sRGB, HDTV
        #7500,  # north sky daylight
    ]

    # Create the plot
    for T in Ts:
        bb_curve = SPD.BlackBody.getCurve(lnms, T)
        bbY = ColorSpace.scalar(bb_curve, CIE.CMF_1931.ybar)
        bb_curve *= 40 / bbY
        col = spradiance_to_sRGB(bb_curve, args.colorscale)
        plot_curve(axes, bb_curve, color=col, linestyle='-', linewidth=3)

    # set up axes
    axes.axis([lnms[0], lnms[-1], 0, 1])


def do_chromas(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    # temperatures of interest:1667 to 25k Kelvin, logspaced gives an approximately even plot
    Ts = numpy.logspace(math.log10(1667), math.log10(25000), 20)
    # for our chosen temperatures, compute the chromaticity coordinates
    # of: a blackbody emitter, Kang's approximation thereof, Illuminant D
    bb_ch   = []
    bb_chK  = []
    bb_illD = []
    for T in Ts:
        bb_ch.append(SPD.BlackBody.chroma(T))
        bb_chK.append(SPD.BlackBody.chroma_Kang2002(T))
        if T >= 4000:
            bb_illD.append(SPD.IlluminantD.chroma(T))
    # Create the plot
    plot_spectral_locus(args, axes)

    #                      white            red            green           blue
    # ITU-R BT.709 	    0.3127 	0.3290 	0.64 	0.33 	0.30 	0.60 	0.15 	0.06
    # ITU-R BT.2020 	0.3127 	0.3290 	0.708 	0.292 	0.170 	0.797 	0.131 	0.046
    # P3-D65 (Monitor) 	0.3127 	0.3290 	0.680 	0.320 	0.265 	0.690 	0.150 	0.060
    sRGBgamut = [(.64, .33),(.3, .6),(.15, .06)]
    bt2020gamut = [(0.708, 0.292), (0.170, 0.797), (0.131, 0.046)]
    p3gamut = [	(0.680, 0.320), (0.265, 0.690), (0.150, 0.060)]
    plot_gamut(args, axes, sRGBgamut, color='black', linestyle='-')
    plot_gamut(args, axes, p3gamut, color='black', linestyle=':')
    plot_gamut(args, axes, bt2020gamut, color='black', linestyle='-.')

    # plot several whitepoints
    axes.plot(*zip(*bb_ch),   color = 'red',   linestyle='',  marker='x', markersize=5)
    axes.plot(*zip(*bb_chK),  color = 'green', linestyle='',  marker='x', markersize=5)
    axes.plot(*zip(*bb_illD), color = 'blue',  linestyle='',  marker='x', markersize=5)

    # set up axes
    axes.axis([0, 1, 0, 1])
    return axes


def do_chromas_enlarge(args, figure):
    axes = do_chromas(args, figure)
    # just zoom in "a bit"
    #axes.axis([.225, .575, .225, .575])
    axes.axis([.2, .6, .2, .6])
    return axes



def do_commonilluminants(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    lnms = numpy.linspace(300, 830, (830-300)//5 + 1)
    bb_curve = SPD.BlackBody.getCurve(lnms, 2855.54)
    illD50 = SPD.IlluminantD.getCurve(5003)
    illD65 = SPD.IlluminantD.getCurve(6504)
    # Create the plot
    col = spradiance_to_sRGB(bb_curve, args.colorscale)
    plot_curve(axes, bb_curve, color=col,   linestyle='-')
    colD50 = spradiance_to_sRGB(illD50, args.colorscale)
    plot_curve(axes, illD50, color=colD50,   linestyle='-')
    colD65 = spradiance_to_sRGB(illD65, args.colorscale)
    plot_curve(axes, illD65, color=colD65,   linestyle='-')

    # set up axes
    axes.axis([lnms[0], lnms[-1], 0, 800])


def do_illuminanta(args, figure):
    axes = figure.add_subplot(111)

    # prepare
    lnms = numpy.linspace(300, 830, (830-300)//5 + 1)
    bb_curve = SPD.BlackBody.getCurve(lnms, 2855.54)

    # Create the plot
    col = spradiance_to_sRGB(bb_curve, args.colorscale)
    plot_curve(axes, bb_curve, color=col,   linestyle='-')

    # set up axes
    axes.axis([lnms[0], lnms[-1], 0, 800])


def do_illuminantd(args, figure):
    axes = figure.add_subplot(111)
    # Create the plot
    # to show some kind of a meaningful color, we rescale the three functions
    # so their peak is at 1.0
    s0scale = 1 / max(SPD.IlluminantD.S0.data)
    s1scale = 1 / max(SPD.IlluminantD.S1.data)
    s2scale = 1 / max(SPD.IlluminantD.S2.data)
    s0col = transmittance_to_sRGB(SPD.IlluminantD.S0 * s0scale, args.colorscale)
    s1col = transmittance_to_sRGB(SPD.IlluminantD.S1 * s1scale, args.colorscale)
    s2col = transmittance_to_sRGB(SPD.IlluminantD.S2 * s2scale, args.colorscale)

    plot_curve(axes, SPD.IlluminantD.S0, color=s0col, linestyle='-')
    plot_curve(axes, SPD.IlluminantD.S1, color=s1col, linestyle='-')
    plot_curve(axes, SPD.IlluminantD.S2, color=s2col, linestyle='-')
    # set up axes
    axes.axis([SPD.IlluminantD.S0.lnms[0], SPD.IlluminantD.S0.lnms[-1], -15, 130])


def do_illuminantf1_6(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    # Create the plot
    for i in range(0,6):
        illFi = SPD.IlluminantF.F[i]
        col = spradiance_to_sRGB(illFi, args.colorscale)
        plot_curve(axes, illFi, color=col, linestyle='-', linewidth = 2)

    # set up axes
    axes.axis([illFi.lnms[0], illFi.lnms[-1], 0, 100])


def do_illuminantf7_9(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    # Create the plot
    for i in range(6, 9):
        illFi = SPD.IlluminantF.F[i]
        col = spradiance_to_sRGB(illFi, args.colorscale)
        plot_curve(axes, illFi, color=col, linestyle='-', linewidth=2)

    # set up axes
    axes.axis([illFi.lnms[0], illFi.lnms[-1], 0, 100])


def do_illuminantf10_12(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    # Create the plot
    for i in range(9, 12):
        illFi = SPD.IlluminantF.F[i]
        col = spradiance_to_sRGB(illFi, args.colorscale)
        plot_curve(axes, illFi, color=col, linestyle='-', linewidth=2)

    # set up axes
    axes.axis([illFi.lnms[0], illFi.lnms[-1], 0, 100])


def do_roscolux(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    gels = load_spectral_data(system.resolve_path('data', "rosco/roscolux.csv"))

    # Create the plot
    for gel in gels:
        color = transmittance_to_sRGB(gel, args.colorscale)
        plot_curve(axes, gel, color=color, linestyle='solid', linewidth=3)

    # set up axes
    axes.axis([360,740,0,1])


def do_Canon_1DMarkIII(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    senscurves = load_spectral_data(system.resolve_path('data', "camera/Canon_1DMarkIII.csv"))

    # Create the plot
    for senscurve in senscurves:
        color = transmittance_to_sRGB(senscurve, args.colorscale)
        plot_curve(axes, senscurve, color=color, linestyle='solid', linewidth=3)

    # set up axes
    axes.axis([360, 740, 0, 1])


def do_Canon_5DMarkII(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    senscurves = load_spectral_data(system.resolve_path('data', "camera/Canon_5DMarkII.csv"))

    # Create the plot
    for senscurve in senscurves:
        color = transmittance_to_sRGB(senscurve, args.colorscale)
        plot_curve(axes, senscurve, color=color, linestyle='solid', linewidth=3)

    # set up axes
    axes.axis([360, 740, 0, 1])


def do_Red_Mysterium_X(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    senscurves = load_spectral_data(system.resolve_path('data', "camera/Red_Mysterium_X.csv"))

    # Create the plot
    for senscurve in senscurves:
        color = transmittance_to_sRGB(senscurve, args.colorscale)
        plot_curve(axes, senscurve, color=color, linestyle='solid', linewidth=3)

    # set up axes
    axes.axis([360, 740, 0, 1])


def plotData(args):
    """ Make the plot `args.plotname`, return it in a figure """

    plotsetup = {
        "chromas":         (do_chromas,         (2.5, 2.5)),
        "chromas_enlarge": (do_chromas_enlarge, (2.5, 2.5)),

        "cielms2006": (do_cielms2006, (6, 2)),
        "ciexyz1931": (do_ciexyz1931, (6, 2)),
        "ciexyz1964": (do_ciexyz1964, (6, 2)),

        "blackbody":         (do_blackbody, (6,2)),
        "commonilluminants": (do_commonilluminants, (6,2)),
        #"illuminanta":       (do_illuminanta, (6,2)),
        "illuminantd":       (do_illuminantd, (6,2)),
        "illuminantf10-12":  (do_illuminantf10_12, (6,2)),
        "illuminantf1-6":    (do_illuminantf1_6, (6,2)),
        "illuminantf7-9":    (do_illuminantf7_9, (6,2)),

        "roscolux":        (do_roscolux, (6, 2)),
        "Red_Mysterium_X": (do_Red_Mysterium_X, (6,2)),
        "Canon_1DMarkIII": (do_Canon_1DMarkIII, (6,2)),
        "Canon_5DMarkII":  (do_Canon_5DMarkII, (6,2)),
    }

    if args.plotname not in plotsetup:
        print("Warning: unknown plotname '%s'" % args.plotname)
        return None

    # execute the plotting
    plotter, figsize = plotsetup[args.plotname]
    fig = pyplot.figure(figsize=figsize)
    plotter(args, fig)

    return fig


def savePlot(args, figure):
    """ Save figure to `args.output` """
    filename = args.output
    print("Saving '%s'" % filename)
    figure.savefig(args.output)


def showPlot(args, figure):
    """ Draw the plot to the screen """
    print("Displaying figure '%s'" % args.plotname)
    pyplot.figure(figure)
    pyplot.show()


def parse_arguments(args = None):
    parser = argparse.ArgumentParser(
        description='Make various figures for the physLight document'
    )
    parser.add_argument("-cs",
                        dest='colorscale',
                        default = 0.85,
                        help='Color scale')
    parser.add_argument("-o",
                        dest='output',
                        help='Output filename')
    parser.add_argument("plotname",
                        help='Plot name')

    parsedargs = parser.parse_args(args)

    # validate args
    # (nothing at the moment)

    return parsedargs


def makePlotParams(args):
    params = {}
    #params = {'font.size': 10,
    #          'font.family': ''}
    return params


if __name__ == '__main__':
    args = parse_arguments()

    params = makePlotParams(args)
    pyplot.rcParams.update(params)

    figure = plotData(args)
    if figure:
        if args.output is not None:
            savePlot(args, figure)
        else:
            showPlot(args, figure)
