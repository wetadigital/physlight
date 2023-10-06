# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.

import bisect
from typing import Optional
import math
import numpy

import system


class EDF:
    ORIENTATION_Y_UP_X_LENGTH = 0  # IES Type C / CIE Type A
    ORIENTATION_Y_WIDTH_X_UP = 1   # IES Type B / CIE Type B
    ORIENTATION_Y_LENGTH_X_UP = 2  # IES Type A / CIE Type C

    SHAPE_POINT = 0
    SHAPE_RECTANGLE = 1
    SHAPE_CIRCLE = 2
    SHAPE_SPHERE = 3
    SHAPE_HEIGHT_CYL = 4
    SHAPE_LENGTH_CYL = 5
    SHAPE_WIDTH_CYL = 6
    SHAPE_LENGTH_ELLIPSE = 7
    SHAPE_WIDTH_ELLIPSE = 8
    SHAPE_LENGTH_ELLIPSOID = 9
    SHAPE_WIDTH_ELLIPSOID = 10

    SYMMETRY_NONE = 0         # all phi directions have unique values
    SYMMETRY_CYLINDRICAL = 1  # all phi directions are the same
    SYMMETRY_4WAY = 2         # 4-quadrant symmetry
    SYMMETRY_FRONTBACK = 3    # front/back symmetry: value for 1 deg == value for 359 deg
    SYMMETRY_LEFTRIGHT = 4    # left/right symmetry: value for 89 deg == value for 91 deg

    def __init__(self):
        self.metadata = None
        self.orientation = None
        self.shape = None
        self.size = [0,0,0]  # width, length, height (always in meters)
        self.tilt_angles = None
        self.tilt_multipliers = None
        self.ballast_multiplier = 1.
        self.intensity_multiplier = 1.
        self.vert_angles = None  # Y_UP_X_LENGTH: theta
        self.horz_symmetry = None
        self.horz_angles = None  # Y_UP_X_LENGTH: phi
        # intensity for self.horz_angles[i] / self.vert_angles[j] is at
        # self.intensities[i][j]
        self.intensities = None

    def sample(self, phi: float, theta: float, tilt: float = 0.0):
        """
        phi: equator angle, radians [0,2pi]
        theta: zenith angle, radians [0,pi]
        tilt: tilt angle, radians
        """
        intensity = 1.0
        multiplier = 1.0
        if self.orientation == self.ORIENTATION_Y_UP_X_LENGTH:
            multiplier = self.ballast_multiplier * self.intensity_multiplier
            if self.tilt_angles:
                multiplier *= numpy.interp(tilt, self.tilt_angles, self.tilt_multipliers)
            if len(self.horz_angles) == 1:
                intensity = numpy.interp(theta, self.vert_angles, self.intensities[0])
            else:
                # use phi to pick the row
                # ... but first implement symmetry
                phi_symmetric = phi % (2*math.pi)
                if self.horz_symmetry == self.SYMMETRY_NONE:
                    # all phi directions have unique values
                    pass
                elif self.horz_symmetry == self.SYMMETRY_CYLINDRICAL:
                    # all phi directions are the same
                    phi_symmetric = 0.
                elif self.horz_symmetry == self.SYMMETRY_4WAY:
                    # 4-quadrant symmetry
                    if phi_symmetric > math.pi:
                        phi_symmetric -= math.pi

                    if phi_symmetric <= math.pi / 2:
                        phi_symmetric = phi_symmetric
                    else:
                        phi_symmetric = math.pi / 2 - phi_symmetric
                elif self.horz_symmetry == self.SYMMETRY_FRONTBACK:
                    # front/back symmetry: value for 1 deg == value for 359 deg
                    if phi_symmetric > math.pi:
                        phi_symmetric = math.pi - phi_symmetric
                elif self.horz_symmetry == self.SYMMETRY_LEFTRIGHT:
                    # left/right symmetry: value for 89 deg == value for 91 deg
                    phi_symmetric -= math.pi / 2
                    if phi_symmetric > math.pi:
                        phi_symmetric = math.pi - phi_symmetric
                    phi_symmetric += math.pi / 2

                i_low = bisect.bisect_right(self.horz_angles, phi_symmetric)-1
                # interpolate for theta
                lo = numpy.interp(theta, self.vert_angles, self.intensities[i_low])
                # interpolate for phi
                if self.horz_angles[i_low] == phi_symmetric:
                    # if exact, we're done
                    intensity = lo
                else:
                    i_high = (i_low+1) % len(self.horz_angles)
                    # assert(len(self.vert_angles) == len(self.intensities[i_low]))
                    hi = numpy.interp(theta, self.vert_angles, self.intensities[i_high])
                    intensity = numpy.interp(phi_symmetric, [self.horz_angles[i_low],self.horz_angles[i_high]], [lo, hi])

        return intensity * multiplier

    def luminous_power_MC(self, samplecount):
        computed_power = 0
        for n in range(samplecount):
            phi = random.uniform(0, 2 * math.pi)
            theta = random.uniform(0, math.pi)
            computed_power += edf.sample(phi, theta) * math.sin(theta)
        computed_power *= 2 * math.pi * math.pi / samplecount
        return computed_power

    def luminous_power_trapz(self, samplecount = None):
        power = 0
        if samplecount:
            hsamples = 2*int(math.sqrt(samplecount / 2))
            vsamples = samplecount // hsamples
            dh = 2*math.pi/hsamples
            dv = math.pi/vsamples
            for h in range(hsamples):
                phi = dh * h + dh / 2
                for v in range(vsamples):
                    # sample the intensity at the patch center
                    theta = dv*v + dv/2
                    # solid angle of the patch
                    dS = dh * dv * math.sin(theta)
                    intensity = self.sample(phi, theta)
                    power += dS * intensity
        else:
            for h in range(len(self.horz_angles) - 1):
                for v in range(len(self.vert_angles) - 1):
                    # approximate dimensions of the patch
                    dh = self.horz_angles[h+1] - self.horz_angles[h]
                    dv = self.vert_angles[v+1] - self.vert_angles[v]
                    # solid angle of the patch
                    dS = dh * dv * math.sin(self.vert_angles[v] + dv / 2)
                    # sample the intensity at the patch center
                    phi = self.horz_angles[h] + dh/2
                    theta = self.vert_angles[v] + dv/2
                    intensity = self.sample(phi, theta)
                    power += dS * intensity

            if self.horz_symmetry == self.SYMMETRY_NONE:
                # all phi directions have unique values
                pass
            elif self.horz_symmetry == self.SYMMETRY_CYLINDRICAL:
                # all phi directions are the same
                for v in range(len(self.vert_angles) - 1):
                    # approximate dimensions of the patch
                    dh = 2*math.pi
                    dv = self.vert_angles[v+1] - self.vert_angles[v]
                    # bilinearly interpolate intensity at the patch center
                    intensity = (self.intensities[0][v] + self.intensities[0][v+1]) / 2
                    # solid angle of the patch
                    dS = dh * dv * math.sin(self.vert_angles[v] + dv/2)
                    power += dS * intensity
            elif self.horz_symmetry == self.SYMMETRY_4WAY:
                # 4-quadrant symmetry
                power *= 4
            elif self.horz_symmetry == self.SYMMETRY_FRONTBACK or \
                 self.horz_symmetry == self.SYMMETRY_LEFTRIGHT:
                # front/back symmetry: value for 1 deg == value for 359 deg
                # left/right symmetry: value for 89 deg == value for 91 deg
                power *= 2

        return power


def load(fname: str) -> Optional[EDF]:
    """ Load an IES profile in LM-63 format """
    # The iesna.txt file by Ian Ashdown speaks of lines to mean two things:
    #  - a line of text in the usual sense
    #  - a segment of the IES profile file, potentially made of one or more lines as above
    # In this program I am calling this second entity a 'record', because I find it less confusing
    # load file. A record always starts at the start of a line
    lines = None
    with open(fname, 'r') as f:
        # we drop whitespace in front and at the back of the line to simplify our life later
        # also we don't pick up empty lines
        lines = [l.strip() for l in f if l.strip()]

    # record 0: file format
    linecursor = 0
    fileformat = "LM-63-1986"
    if lines[linecursor] == "IESNA91":
        fileformat = "LM-63-1991"
        linecursor += 1
    elif lines[linecursor] == "IESNA:LM-63-1995":
        fileformat = "LM-63-1995"
        linecursor += 1
    elif lines[linecursor] == "IESNA:LM-63-2002":
        fileformat = "LM-63-2002"
        linecursor += 1
    # records 1..4 pull in matadata until the TILT line
    metadata = {}
    while lines[linecursor][0] == '[':
        line = lines[linecursor]
        end = line.index(']')
        key = line[1:end]
        value = line[end+1:].lstrip()
        metadata[key] = value
        linecursor += 1
    # record 5: pull in the TILT value
    _,tiltmode = lines[linecursor].split("=", 1)
    linecursor += 1
    tiltfile = None
    tiltangles = None
    tiltmults = None
    if tiltmode.strip() == "NONE":
        # records 6,7,8,9 not present
        pass
    elif tiltmode.strip() == "INCLUDE":
        # parse records 6,7,8,9:
        # record 6: lamp to luminaire geometry
        lamp_to_lum = int(lines[linecursor])
        linecursor += 1
        # TODO: decode
        # record 7: count of tilt angles and multipliers
        count = int(lines[linecursor])
        linecursor += 1
        # record 8: angles - `count` floats for our tilt angles
        tiltangles = []
        while len(tiltangles) < count:
            tiltangles += [float(f) for f in lines[linecursor].split()]
            linecursor += 1
        # record 9: mults - `count` floats for our multipliers
        tiltmults = []
        while len(tiltmults) < count:
            tiltmults += [float(f) for f in lines[linecursor].split()]
            linecursor += 1
    else:
        tiltfile = tiltmode.strip()
        # TODO: open the file and parse the same way as the 'INCLUDE' case
    # record 10: a whole bunch o' stuff:
    # <# of lamps> <lumens per lamp> <candela multiplier>
    # <# of vertical angles> <# of horizontal angles> <photometric type>
    # <units type> <width> <length> <height>
    fields = lines[linecursor].split()
    linecursor += 1
    fieldcursor = 0
    lampcount = int(fields[fieldcursor])
    fieldcursor += 1
    powers = [float(fields[fieldcursor])] * lampcount
    fieldcursor += 1
    #powers = [float(f) for f in fields[fieldcursor:fieldcursor+lampcount]]
    #fieldcursor += lampcount
    intensitymultiplier = float(fields[fieldcursor])
    fieldcursor += 1
    vert_anglecount = int(fields[fieldcursor])
    fieldcursor += 1
    horz_anglecount = int(fields[fieldcursor])
    fieldcursor += 1
    photometrictype = int(fields[fieldcursor])
    fieldcursor += 1
    if photometrictype == 1:
        photometrictype = "C"  # aka CIE Type A
        # normally used for architectural and roadway
        # luminaires. The polar axis of the photometric web coincides with the
        # vertical axis of the luminaire, and the 0-180 degree photometric plane
        # coincides with the luminaire's major axis (length).
        # (theta = 0 (y-axis) points "up", theta = 90, phi = 0 (x-axis) along the length)
    elif photometrictype == 2:
        photometrictype = "B"  # aka CIE Type B
        # normally used for adjustable outdoor area and sports
        # lighting luminaires. The polar axis of the photometric web coincides with the
        # minor axis (width) of the luminaire, and the 0-180 degree photometric
        # plane coincides with the luminaire's vertical axis.
        # (theta = 0 (y-axis) along the width, theta = 90, phi = 0 (x-axis) points "up")
    elif photometrictype == 3:
        photometrictype = "A"  # aka CIE Type C
        # normally used for automotive headlights and signal
        # lights. The polar axis of the photometric web coincides with the major axis
        # (length) of the luminaire, and the 0-180 degree photometric plane
        # coincides with the luminaire's vertical axis.
        # (theta = 0 (y-axis) along the length, theta = 90, phi = 0 (x-axis) points "up")
    #print("Photometry type ", photometrictype)
    units = int(fields[fieldcursor])
    fieldcursor += 1
    if units == 1:
        units = 'ft'
    elif units == 2:
        units = 'm'
    width,length,height = (float(f) for f in fields[fieldcursor:fieldcursor+3])
    fieldcursor += 3
    # assert(len(fields) == fieldcursor)
    # TODO: decode shape according to section 3.15.4 of iesna.txt
    # record 11 <ballast factor> <future use> <input watts>
    fields = lines[linecursor].split()
    linecursor += 1
    fieldcursor = 0
    ballastfactor = float(fields[fieldcursor])
    fieldcursor += 1
    _ = fields[fieldcursor]
    fieldcursor += 1
    inputwatts = float(fields[fieldcursor])
    fieldcursor += 1
    # record 12: vertical angles
    vert_angles = []
    while len(vert_angles) < vert_anglecount:
        vert_angles += [float(f) for f in lines[linecursor].split()]
        linecursor += 1
    # record 13: horizontal angles
    horz_angles = []
    while len(horz_angles) < horz_anglecount:
        horz_angles += [float(f) for f in lines[linecursor].split()]
        linecursor += 1
    # records 14..17: intensity - one record per each horizontal angle, each with vert_anglecount elms
    intensities = []
    for i in range(horz_anglecount):
        intensityrecord = []
        while len(intensityrecord) < vert_anglecount:
            intensityrecord += [float(f) for f in lines[linecursor].split()]
            linecursor += 1
        intensities.append(intensityrecord)

    if len(lines) != linecursor:
        print("Parsing failed")
        return None

    # now that the file is successfully parsed, we can build an EDF object
    edf = EDF()
    edf.metadata = metadata

    edf.orientation = {"C" : EDF.ORIENTATION_Y_UP_X_LENGTH,
                       "B" : EDF.ORIENTATION_Y_WIDTH_X_UP,
                       "A" : EDF.ORIENTATION_Y_LENGTH_X_UP}[photometrictype]
    if edf.orientation != EDF.ORIENTATION_Y_UP_X_LENGTH:
        print("INTERNAL ERROR: IES Photometry type '%s' is not supported at this time" % photometrictype)

    edf.shape = None # FIXME
    onefoot = 0.0254 * 12  # one foot (aka 12 inch) in meters
    onedegree = math.pi / 180.
    edf.size = [width/onefoot,length/onefoot,height/onefoot] if units == "ft" else [width,length,height]
    if tiltangles:
        edf.tilt_angles = [a * onedegree for a in tiltangles]
        edf.tilt_multipliers = tiltmults
    edf.ballast_multiplier = ballastfactor
    edf.intensity_multiplier = intensitymultiplier
    minangle = min(horz_angles)
    maxangle = max(horz_angles)
    if maxangle == 0:
        edf.horz_symmetry = EDF.SYMMETRY_CYLINDRICAL  # all phi directions are the same
    elif maxangle > 270 and minangle < 90:
        edf.horz_symmetry = EDF.SYMMETRY_NONE # all phi directions have unique values
    elif minangle == 0 and maxangle == 90:
        edf.horz_symmetry = EDF.SYMMETRY_4WAY # 4-quadrant symmetry
    elif minangle == 0 and maxangle == 180:
        edf.horz_symmetry = EDF.SYMMETRY_FRONTBACK # front/back symmetry: value for 1 deg == value for 359 deg
    elif maxangle == 270 and minangle == 90:
        edf.horz_symmetry = EDF.SYMMETRY_LEFTRIGHT # left/right symmetry: value for 89 deg == value for 91 deg
    else:
        print("Warning: can't handle horizontal angle configuration for photometric web of type %s: " % photometrictype, ', '.join(str(s) for s in horz_angles))
        edf.horz_symmetry = EDF.SYMMETRY_NONE

    edf.horz_angles = [a * onedegree for a in horz_angles]
    edf.vert_angles = [a * onedegree for a in vert_angles]
    # intensity for edf.horz_angles[i] / edf.vert_angles[j] is at
    # edf.intensities[i][j]
    edf.intensities = intensities
    return edf

# self-test
if __name__ == '__main__':
    import os.path
    import random
    datadir = os.path.join(os.path.dirname(__file__),'../figures_src/data/')
    system.register_searchpaths("data", [datadir])
    files = [
        'ieslm63/0000185eb674b406fccad004f9275f6e.ies',
        'ieslm63/00303c4e79984346f73c7d8042dee1ad.ies',
        #'ieslm63/006eee706aab7fcacabe69958b454bc9.ies', # doesn't have reported lm power
        'ieslm63/00715027edfa347b29d76898771819c2.ies',
        'ieslm63/0073eb5a64f0c18baea319e10f93efb5.ies',
        'ieslm63/00751debb20da686f6cf0baa331bded3.ies',
        #'ieslm63/009092d67a9e943ba297c29b272a5e15.ies', # doesn't have reported lm power
        'ieslm63/0098d3784ddbb80a3b707d248746ed15.ies',
        'ieslm63/00a395219421cfa56034b797cec995eb.ies',
        'ieslm63/00cfaf17dc5faec6fdfd88927aaed008.ies',
        'ieslm63/01306a8d4bed8455ced1f41ae4176050.ies',
        'ieslm63/015ae384bf4d8d8fb196b64e06a4ea30.ies',
        'ieslm63/015e201d1686f0ac9611271952d8c9c3.ies',
        'ieslm63/016f0843c2627f0f573a2bf25347ea8a.ies',
        #'ieslm63/01f01731b381b906475deb2438106290.ies', # doesn't have reported lm power
        'ieslm63/01f18cd2eee9e4824d9ecf4d8126c28e.ies',
        'ieslm63/01fdaa394caf0c0ce827eb07b08849b6.ies',
        'ieslm63/02195a36fc71f8cf0d88be1f66d05578.ies',
         'ieslm63/bega_84659K4.ies',
        'ieslm63/bega_84693k4.ies',
        'ieslm63/bega_84693K4.ies',
        'ieslm63/bega_omni001_1238lm.ies',
        'ieslm63/bega_50988.6k3.ies'
    ]
    for fn in files:
        print("IES LM-63 file: ", fn)
        fullpath = system.resolve_path('data', fn)
        edf = load(fullpath)

        reported_power = 0
        if '_ABSOLUTELUMENS' in edf.metadata:
            reported_power = float(edf.metadata['_ABSOLUTELUMENS'])
        elif ' lm' in edf.metadata['LAMP']:
            fields = edf.metadata['LAMP'].split(",")
            for field in edf.metadata['LAMP'].split(","):
                if 'lm' in field:
                    toks = field.split()
                    i = toks.index('lm')
                    reported_power = float(toks[i-1])
        if reported_power == 0:
            for k in sorted(edf.metadata.keys()):
                print ("%s: %s" % (k, edf.metadata[k]))
            print("Unable to determine nominal power")
            exit(1)


        samplecount = 100000

        computed_powerMC = edf.luminous_power_MC(samplecount)
        #computed_powerMC = edf.luminous_power_trapz(10000)
        computed_power_trapz = edf.luminous_power_trapz()
        errorMC = (computed_powerMC - reported_power) / reported_power
        error_trapz = (computed_power_trapz - reported_power) / reported_power
        if abs(errorMC) > 0.03:
            for k in sorted(edf.metadata.keys()):
                print ("%s: %s" % (k, edf.metadata[k]))
        print("Power: computed MC %.8g lm, computed trapz %.8g, reported %.8g lm, error %.3g%%" % (computed_powerMC, computed_power_trapz, reported_power, 100 * errorMC))
        print("=================================")
