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
    import matplotlib as mpl
    import mpl_toolkits.axes_grid1
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
            # we make the pure-hue dots on the spectral locus half brightness
            # because is gives more prominence to the other stuff we plot on the graph
            XYZ *= 0.5 * args.emittancescale / XYZ[1]
            sRGB = ColorSpace.sRGB(XYZ)
            sRGB = numpy.clip(sRGB, 0, 1)
            xy = ColorSpace.xy(XYZ)
            axes.plot([xy[0]], [xy[1]], color=sRGB, marker='o', markersize=6)


def plot_gamut(args, axes: pyplot.Axes, pts: list[tuple[float,float]], **kwargs):
    for xy in pts:
        col = ColorSpace.sRGB(ColorSpace.XYZ(xy, args.emittancescale))
        col = numpy.clip(col, 0, 1)
        pyplot.plot([xy[0]], [xy[1]], color=col, marker='s', markersize=5)

    pts = list(pts) # take a copy
    pts.append(pts[0])
    pyplot.plot(*zip(*pts), **kwargs)


def add_huebars(args, axes: pyplot.Axes, figure: pyplot.Figure):
    """ Draw a hues gradient at the bottom of a graph """

    # first thing, we make a Colormap with the hues we want
    # these are the CIE \bar x, \bar y, \bar z curves sampled regularly
    # to obtain the XYZ coordinates of the pure stimulus at the given wavelength
    # and then converted from XYZ to our display space, sRGB
    #
    # To acquire the values at a coherent brightness that won't overdrive the
    # gamma mapping, we first gather all the data in linear sRGB primaries,
    # then normalize to the maximum value, and then apply the gamma after
    # we got a brightness we're happy with
    xlim = axes.get_xlim()
    drawLocalBar = False
    samplecount = 35
    linRGBs = []

    # sample the 1931 CMF's at several locations to make a pure-hues bar
    for lnm in numpy.linspace(xlim[0], xlim[1], samplecount):
        X = CIE.CMF_1931.xbar.sample(lnm)
        Y = CIE.CMF_1931.ybar.sample(lnm)
        Z = CIE.CMF_1931.zbar.sample(lnm)
        linRGBs.append(ColorSpace.Rec709l((X, Y, Z)))

    # find max and rescale so that it's our chosen max: `colorscale`
    Rmax = max(RGB[0] for RGB in linRGBs)
    Gmax = max(RGB[1] for RGB in linRGBs)
    Bmax = max(RGB[2] for RGB in linRGBs)

    gscale = 1.5 * args.emittancescale / max(Rmax, Gmax, Bmax)

    # pure hues map, globally scaled
    pureHuesCmap_gscale = mpl.colors.LinearSegmentedColormap.from_list(
        "pureHues_gscale",
        [numpy.clip(ColorSpace.sRGB_gamma(RGB * gscale), 0, 1) for RGB in linRGBs])
    # pure hues map, locally scaled so each color has the target Y value
    if drawLocalBar:
        def localscale(rgb):
            return rgb * args.emittancescale / max(rgb)
        pureHuesCmap_lscale = mpl.colors.LinearSegmentedColormap.from_list(
            "pureHues_lscale",
            [numpy.clip(ColorSpace.sRGB_gamma(localscale(RGB)), 0, 1) for RGB in linRGBs])

    # the range our hues correspond to
    norm = mpl.colors.Normalize(vmin=xlim[0], vmax=xlim[1])

    # place it next to the plot: we require a new set of axes to achieve this
    divider = mpl_toolkits.axes_grid1.make_axes_locatable(axes)
    # the added axes take space from the bottom of the current graph, pushing it up
    # this means that they appear in the reverse order from which they are added
    if drawLocalBar:
        caxl = divider.append_axes("bottom", size="7.5%", pad=0.0)
    caxg = divider.append_axes("bottom", size="7.5%", pad=0.0)

    globalBar = figure.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=pureHuesCmap_gscale),
                                cax=caxg,
                                orientation='horizontal')
    if drawLocalBar:
        localBar = figure.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=pureHuesCmap_lscale),
                               cax=caxl,
                               orientation='horizontal')

    # hide the ticks from the top graph and top color bar
    if drawLocalBar:
        localBar.ax.get_xaxis().set_visible(False)
    axes.get_xaxis().set_visible(False)
    # add two dotted lines, to represent limits of "barely visible" region (ybar < 0.1%)
    axes.axvline(380, color=(.7,.7,.7), linewidth=.5, linestyle=":")
    axes.axvline(720, color=(.7,.7,.7), linewidth=.5, linestyle=":")
    axes.axvspan(xlim[0], 380, alpha=0.03, color='black')
    axes.axvspan(720, xlim[1], alpha=0.03, color='black')
    # add two dashed lines, to represent limits of "actually visible" region (ybar < 1%)
    axes.axvline(420, color=(.4,.4,.4), linewidth=.5, linestyle="--")
    axes.axvline(685, color=(.4,.4,.4), linewidth=.5, linestyle="--")


def do_ciexyz1931(args, figure):
    """ Plot the CIE XYZ 1931 dataset into the figure """
    axes = figure.add_subplot(111)

    xcol = transmittance_to_sRGB(CIE.CMF_1931.xbar, args.transmittancescale)
    ycol = transmittance_to_sRGB(CIE.CMF_1931.ybar, args.transmittancescale)
    zcol = transmittance_to_sRGB(CIE.CMF_1931.zbar, args.transmittancescale)

    # original CIE data was every 5nm, but current distributions use interpolated values
    # down to 1nm spacing. For plotting we plot the original
    plot_curve(axes, CIE.CMF_1931.xbar, color=xcol, linestyle='', marker='x', markersize=5, markevery=5)
    plot_curve(axes, CIE.CMF_1931.ybar, color=ycol, linestyle='', marker='x', markersize=5, markevery=5)
    plot_curve(axes, CIE.CMF_1931.zbar, color=zcol, linestyle='', marker='x', markersize=5, markevery=5)

    xcol = transmittance_to_sRGB(CIE.CMF_1931_wyman.xbar, args.transmittancescale)
    ycol = transmittance_to_sRGB(CIE.CMF_1931_wyman.ybar, args.transmittancescale)
    zcol = transmittance_to_sRGB(CIE.CMF_1931_wyman.zbar, args.transmittancescale)

    plot_curve(axes, CIE.CMF_1931_wyman.xbar, color=xcol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.CMF_1931_wyman.ybar, color=ycol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.CMF_1931_wyman.zbar, color=zcol, linestyle='solid', linewidth=1)

    # set up axes
    axes.axis([360,830,0,2])
    # show pure hue bars
    add_huebars(args, axes, figure)

def do_ciexyz1964(args, figure):
    """ Plot the CIE XYZ 1964 dataset into the figure """
    axes = figure.add_subplot(111)

    xcol = transmittance_to_sRGB(CIE.CMF_1964.xbar, args.transmittancescale)
    ycol = transmittance_to_sRGB(CIE.CMF_1964.ybar, args.transmittancescale)
    zcol = transmittance_to_sRGB(CIE.CMF_1964.zbar, args.transmittancescale)

    # original CIE data was every 5nm, but current distributions use interpolated values
    # down to 1nm spacing. For plotting we plot the original
    plot_curve(axes, CIE.CMF_1964.xbar, color=xcol, linestyle='', marker='x', markersize=5, markevery=5)
    plot_curve(axes, CIE.CMF_1964.ybar, color=ycol, linestyle='', marker='x', markersize=5, markevery=5)
    plot_curve(axes, CIE.CMF_1964.zbar, color=zcol, linestyle='', marker='x', markersize=5, markevery=5)

    xcol = transmittance_to_sRGB(CIE.CMF_1964_wyman.xbar, args.transmittancescale)
    ycol = transmittance_to_sRGB(CIE.CMF_1964_wyman.ybar, args.transmittancescale)
    zcol = transmittance_to_sRGB(CIE.CMF_1964_wyman.zbar, args.transmittancescale)

    plot_curve(axes, CIE.CMF_1964_wyman.xbar, color=xcol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.CMF_1964_wyman.ybar, color=ycol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.CMF_1964_wyman.zbar, color=zcol, linestyle='solid', linewidth=1)

    # set up axes
    axes.axis([360, 830, 0, 2])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_cielms2006(args, figure):
    """ Plot the CIE LMS 2006 dataset into the figure """
    axes = figure.add_subplot(111)

    xcol = transmittance_to_sRGB(CIE.LMS_2006_2deg.lbar, args.transmittancescale)
    ycol = transmittance_to_sRGB(CIE.LMS_2006_2deg.mbar, args.transmittancescale)
    zcol = transmittance_to_sRGB(CIE.LMS_2006_2deg.sbar, args.transmittancescale)

    plot_curve(axes, CIE.LMS_2006_2deg.lbar, color=xcol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.LMS_2006_2deg.mbar, color=ycol, linestyle='solid', linewidth=1)
    plot_curve(axes, CIE.LMS_2006_2deg.sbar, color=zcol, linestyle='solid', linewidth=1)

    xcol = transmittance_to_sRGB(CIE.LMS_2006_10deg.lbar, args.transmittancescale)
    ycol = transmittance_to_sRGB(CIE.LMS_2006_10deg.mbar, args.transmittancescale)
    zcol = transmittance_to_sRGB(CIE.LMS_2006_10deg.sbar, args.transmittancescale)

    plot_curve(axes, CIE.LMS_2006_10deg.lbar, color=xcol, linestyle='--', linewidth=1)
    plot_curve(axes, CIE.LMS_2006_10deg.mbar, color=ycol, linestyle='--', linewidth=1)
    plot_curve(axes, CIE.LMS_2006_10deg.sbar, color=zcol, linestyle='--', linewidth=1)

    # set up axes
    axes.axis([360, 830, 0, 2])
    # show pure hue bars
    add_huebars(args, axes, figure)


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
        col = spradiance_to_sRGB(bb_curve, args.emittancescale)
        print('$%.6g$ \\textcolor[rgb]{%g,%g,%g}{\\rule{1em}{1em}},' % (T, *col))
        plot_curve(axes, bb_curve, color=col, linestyle='-', linewidth=3)

    plot_curve(axes, CIE.CMF_1931.ybar, color='black', linestyle='--', linewidth=.5)

    # set up axes
    # data is normalized, hide vertical axis because it's meaningless
    axes.get_yaxis().set_visible(False)
    axes.axis([lnms[0], lnms[-1], 0, 1.05])
    # show pure hue bars
    add_huebars(args, axes, figure)


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
    luminance = ColorSpace.scalar(bb_curve, CIE.CMF_1931.ybar)
    bb_curve *= 40 / luminance
    illD50 = SPD.IlluminantD.getCurve(5003)
    luminance = ColorSpace.scalar(illD50, CIE.CMF_1931.ybar)
    illD50 *= 40 / luminance
    illD65 = SPD.IlluminantD.getCurve(6504)
    luminance = ColorSpace.scalar(illD65, CIE.CMF_1931.ybar)
    illD65 *= 40 / luminance
    # Create the plot
    col = spradiance_to_sRGB(bb_curve, args.emittancescale)
    plot_curve(axes, bb_curve, color=col,   linestyle='-', linewidth=3)
    colD50 = spradiance_to_sRGB(illD50, args.emittancescale)
    plot_curve(axes, illD50, color=colD50,   linestyle='-', linewidth=3)
    colD65 = spradiance_to_sRGB(illD65, args.emittancescale)
    plot_curve(axes, illD65, color=colD65,   linestyle='-', linewidth=3)

    plot_curve(axes, CIE.CMF_1931.ybar, color='black', linestyle='--', linewidth=.5)

    # set up axes
    axes.get_yaxis().set_visible(False)
    axes.axis([lnms[0], lnms[-1], 0, 1.05])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_illuminanta(args, figure):
    axes = figure.add_subplot(111)

    # prepare
    lnms = numpy.linspace(300, 830, (830-300)//5 + 1)
    bb_curve = SPD.BlackBody.getCurve(lnms, 2855.54)

    # Create the plot
    col = spradiance_to_sRGB(bb_curve, args.emittancescale)
    plot_curve(axes, bb_curve, color=col,   linestyle='-')

    # set up axes
    axes.axis([lnms[0], lnms[-1], 0, 800])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_illuminantd(args, figure):
    axes = figure.add_subplot(111)
    # Create the plot
    # to show some kind of a meaningful color, we rescale the three functions
    # so their peak is at 1.0
    s0scale = 1 / max(SPD.IlluminantD.S0.data)
    s1scale = 1 / max(SPD.IlluminantD.S1.data)
    s2scale = 1 / max(SPD.IlluminantD.S2.data)
    s0col = transmittance_to_sRGB(SPD.IlluminantD.S0 * s0scale, args.transmittancescale)
    s1col = transmittance_to_sRGB(SPD.IlluminantD.S1 * s1scale, args.transmittancescale)
    s2col = transmittance_to_sRGB(SPD.IlluminantD.S2 * s2scale, args.transmittancescale)

    plot_curve(axes, SPD.IlluminantD.S0, color=s0col, linestyle='-')
    plot_curve(axes, SPD.IlluminantD.S1, color=s1col, linestyle='-')
    plot_curve(axes, SPD.IlluminantD.S2, color=s2col, linestyle='-')
    # set up axes
    axes.axis([SPD.IlluminantD.S0.lnms[0], SPD.IlluminantD.S0.lnms[-1], -15, 130])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_illuminantf1_6(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    # Create the plot
    for i in range(0,6):
        illFi = SPD.IlluminantF.F[i]
        col = spradiance_to_sRGB(illFi, args.emittancescale)
        plot_curve(axes, illFi, color=col, linestyle='-', linewidth = 2)

    # set up axes
    axes.axis([illFi.lnms[0], illFi.lnms[-1], 0, 100])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_illuminantf7_9(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    # Create the plot
    for i in range(6, 9):
        illFi = SPD.IlluminantF.F[i]
        col = spradiance_to_sRGB(illFi, args.emittancescale)
        plot_curve(axes, illFi, color=col, linestyle='-', linewidth=2)

    # set up axes
    axes.axis([illFi.lnms[0], illFi.lnms[-1], 0, 100])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_illuminantf10_12(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    # Create the plot
    for i in range(9, 12):
        illFi = SPD.IlluminantF.F[i]
        col = spradiance_to_sRGB(illFi, args.emittancescale)
        plot_curve(axes, illFi, color=col, linestyle='-', linewidth=2)

    # set up axes
    axes.axis([illFi.lnms[0], illFi.lnms[-1], 0, 100])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_roscolux(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    gels = load_spectral_data(system.resolve_path('data', "rosco/roscolux.csv"))

    # Create the plot
    for gel in gels:
        color = transmittance_to_sRGB(gel, args.transmittancescale)
        plot_curve(axes, gel, color=color, linestyle='solid', linewidth=3)

    # set up axes
    axes.axis([360,740,0,1])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_Canon_1DMarkIII(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    senscurves = load_spectral_data(system.resolve_path('data', "camera/Canon_1DMarkIII.csv"))

    # Create the plot
    for senscurve in senscurves:
        color = transmittance_to_sRGB(senscurve, args.transmittancescale)
        plot_curve(axes, senscurve, color=color, linestyle='solid', linewidth=3)

    # set up axes
    axes.axis([360, 740, 0, 1])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_Canon_5DMarkII(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    senscurves = load_spectral_data(system.resolve_path('data', "camera/Canon_5DMarkII.csv"))

    # Create the plot
    for senscurve in senscurves:
        color = transmittance_to_sRGB(senscurve, args.transmittancescale)
        plot_curve(axes, senscurve, color=color, linestyle='solid', linewidth=3)

    # set up axes
    axes.axis([360, 740, 0, 1])
    # show pure hue bars
    add_huebars(args, axes, figure)


def do_Red_Mysterium_X(args, figure):
    axes = figure.add_subplot(111)
    # prepare
    senscurves = load_spectral_data(system.resolve_path('data', "camera/Red_Mysterium_X.csv"))

    # Create the plot
    for senscurve in senscurves:
        color = transmittance_to_sRGB(senscurve, args.transmittancescale)
        plot_curve(axes, senscurve, color=color, linestyle='solid', linewidth=3)

    # set up axes
    axes.axis([360, 740, 0, 1])
    # show pure hue bars
    add_huebars(args, axes, figure)


def plotData(args):
    """ Make the plot `args.plotname`, return it in a figure """

    basesize = 4
    vsize = basesize
    hsize = vsize * 2
    sqsize = hsize * .4

    plotsetup = {
        "chromas":         (do_chromas,         (sqsize, sqsize)),
        "chromas_enlarge": (do_chromas_enlarge, (sqsize, sqsize)),

        "cielms2006": (do_cielms2006, (hsize, vsize)),
        "ciexyz1931": (do_ciexyz1931, (hsize, vsize)),
        "ciexyz1964": (do_ciexyz1964, (hsize, vsize)),

        "blackbody":         (do_blackbody, (hsize,vsize)),
        "commonilluminants": (do_commonilluminants, (hsize,vsize)),
        #"illuminanta":       (do_illuminanta, (hsize,vsize)),
        "illuminantd":       (do_illuminantd, (hsize,vsize)),
        "illuminantf10-12":  (do_illuminantf10_12, (hsize,vsize)),
        "illuminantf1-6":    (do_illuminantf1_6, (hsize,vsize)),
        "illuminantf7-9":    (do_illuminantf7_9, (hsize,vsize)),

        "roscolux":        (do_roscolux, (hsize, vsize)),
        "Red_Mysterium_X": (do_Red_Mysterium_X, (hsize,vsize)),
        "Canon_1DMarkIII": (do_Canon_1DMarkIII, (hsize,vsize)),
        "Canon_5DMarkII":  (do_Canon_5DMarkII, (hsize,vsize)),
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
    parser.add_argument("-es",
                        dest='emittancescale',
                        default=0.75,
                        help='Brightness used for rendering emittance profiles')
    parser.add_argument("-ts",
                        dest='transmittancescale',
                        default = 0.85,
                        help='Illuminant D65 brightness for rendering transmittance profiles')
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

    # fonts used for the pgf backend
    if args.output and args.output.endswith('.pgf'):
        params = {
            # leave the font alone and use the document's setup
            "font.family": "serif",
            'font.size': 10,
            # Use LaTeX default serif font.
            "font.serif": [],
            "text.usetex": True,     # use inline math for ticks
            "pgf.rcfonts": False,    # don't setup fonts from rc parameters
        }
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
