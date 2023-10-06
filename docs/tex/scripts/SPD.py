# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.

# caller sanitized this
import numpy

import system
import CIE
import SpectralCurve
import ColorSpace

illuminantDfile = system.resolve_path('data', 'cie/CIE_illum_Dxx_comp.csv')
illuminantFfile = system.resolve_path('data', 'cie/CIE_illum_FLs.csv')
illuminantLEDfile = system.resolve_path('data', 'cie/CIE_illum_LEDs.csv')

# for some reason, the files downloaded from CIE contain NaN values
# they're not useful to us, so we turn them into 0's
illuminantDdata = system.readCSV_columns(illuminantDfile, NaN_as_zero=True)
illuminantFdata = system.readCSV_columns(illuminantFfile, NaN_as_zero=True)
illuminantLEDdata = system.readCSV_columns(illuminantLEDfile, NaN_as_zero=True)


class BlackBody(object):
    @classmethod
    def chroma(cls, T: float, cmf=CIE.CMF_1931):
        """
        Return xy chromaticity for the given temperature T in Kelvin
        """
        curve = cls.getCurve(cmf.xbar.lnms, T)
        XYZ = ColorSpace.XYZ_sc(curve, cmf)
        return ColorSpace.xy(XYZ)

    @staticmethod
    def chroma_Kang2002(T):
        ''' Kang approximation to (1931) chromaticity of a black body '''
        w = 1000. / T
        x = 0
        y = 0
        if T < 1667 - 0.001:
            raise Exception("T = %g < 1667" % T)
        elif T < 4000:
            x = numpy.polyval([-.2991239, -.234358, .8776956, .17991], w)
            if T < 2222:
                y = numpy.polyval([-1.1063814, -1.34811020, 2.18555832, -.20219683], x)
            else:
                y = numpy.polyval([-.9549476, -1.37418593, 2.09137015, -.16748867], x)
        elif T <= 25000:
            x = numpy.polyval([-3.0258469, 2.1070379, .2226347, .240390], w)
            y = numpy.polyval([3.081758, -5.8733867, 3.75112997, -.37001483], x)
        else:
            raise Exception("T = %g > 25000" % T)

        return numpy.array([x,y])

    @staticmethod
    def sample(lnm, T):
        """
        Return the radiance of a black body in W / m^2 sr nm
        (note that this being *per nm* it's 1e9 times _smaller_ than the normal formula)
        """
        lum = lnm / 1000  # wavelength in micrometers
        l5 = pow(lum, 5)  # l^5
        lT = lum * T / 1000 # lambda_um * T_kK (lambda in micrometers times temp in kiloKelvin)
        return (1.19104e5 / l5) / (numpy.exp(14.3878/lT)-1)

    @classmethod
    def getCurve(cls, lnms, T):
        return SpectralCurve.SpectralCurve("", lnms, cls.sample(lnms, T))


class IlluminantD(object):
    S0 = SpectralCurve.SpectralCurve('S0', illuminantDdata[0], illuminantDdata[1])
    S1 = SpectralCurve.SpectralCurve('S1', illuminantDdata[0], illuminantDdata[2])
    S2 = SpectralCurve.SpectralCurve('S2', illuminantDdata[0], illuminantDdata[3])

    @classmethod
    def chroma(cls, T: float, cmf=CIE.CMF_1931):
        """
        Return xy chromaticity for the given temperature T in Kelvin
        When cmf == CIE.CMF_1931, this uses the definition per
        ISO/CIE 11664-2:2022, otherwise it integrates the resulting curves
        """
        if cmf == CIE.CMF_1931:
            w = 1000. / T
            x = 0
            if T < 4000:
                raise Exception("T = %g < 4000" % T)
            elif T < 7000:
                x = (((-4.6070 * w) + 2.9678)*w + .09911) * w + .244063
            else:
                x = (((-2.0064 * w) + 1.9018)*w + .24748) * w + .237040
            y = ((-3 * x) + 2.87) * x - .275
            return numpy.array([x,y])

        curve = cls.getCurve(T)
        XYZ = ColorSpace.XYZ_sc(curve, cmf)
        return ColorSpace.xy(XYZ)

    @classmethod
    def sample(cls, lnm, T: float):
        x, y = cls.chroma(T)
        M = 0.0241 + 0.2562 * x - 0.7341 * y
        M1 = (-1.3515 - 1.7703 * x + 5.9114 * y) / M
        M2 = (0.03 - 31.4424 * x + 30.0717 * y) / M
        return cls.S0.sample(lnm) + M1 * cls.S1.sample(lnm) + M2 * cls.S2.sample(lnm)

    @classmethod
    def getCurve(cls, T: float):
        x, y = cls.chroma(T)
        M = 0.0241 + 0.2562 * x - 0.7341 * y
        M1 = (-1.3515 - 1.7703 * x + 5.9114 * y) / M
        M2 = (0.03 - 31.4424 * x + 30.0717 * y) / M
        return cls.S0 + M1 * cls.S1 + M2 * cls.S2


class IlluminantE(object):

    @classmethod
    def chroma(cls, cmf=CIE.CMF_1931):
        """
        Return xy chromaticity for the given temperature T in Kelvin
        computed against the given cmf
        """
        curve = cls.getCurve(cmf.xbar.lnms)
        XYZ = ColorSpace.XYZ_sc(curve, cmf)
        return ColorSpace.xy(XYZ)

    @classmethod
    def sample(cls, lnm):
        v = 1.
        # if the input is an array return an array of that size
        if hasattr(lnm, "__len__"):
            return numpy.array([v]*len(lnm))
        else:
            return v

    @classmethod
    def getCurve(cls, lnms):
        return SpectralCurve.SpectralCurve("", lnms, cls.sample(lnms))


class IlluminantF(object):
    # the i-th element of S0, S1, S2
    # is at wavelength lnms nm
    F1 = SpectralCurve.SpectralCurve('F1', illuminantFdata[0], illuminantFdata[1])
    F2 = SpectralCurve.SpectralCurve('F2', illuminantFdata[0], illuminantFdata[2])
    F3 = SpectralCurve.SpectralCurve('F3', illuminantFdata[0], illuminantFdata[3])
    F4 = SpectralCurve.SpectralCurve('F4', illuminantFdata[0], illuminantFdata[4])
    F5 = SpectralCurve.SpectralCurve('F5', illuminantFdata[0], illuminantFdata[5])
    F6 = SpectralCurve.SpectralCurve('F6', illuminantFdata[0], illuminantFdata[6])
    F7 = SpectralCurve.SpectralCurve('F7', illuminantFdata[0], illuminantFdata[7])
    F8 = SpectralCurve.SpectralCurve('F8', illuminantFdata[0], illuminantFdata[8])
    F9 = SpectralCurve.SpectralCurve('F9', illuminantFdata[0], illuminantFdata[9])
    F10 = SpectralCurve.SpectralCurve('F10', illuminantFdata[0], illuminantFdata[10])
    F11 = SpectralCurve.SpectralCurve('F11', illuminantFdata[0], illuminantFdata[11])
    F12 = SpectralCurve.SpectralCurve('F12', illuminantFdata[0], illuminantFdata[12])

    # data for Fi is also at IlluminantF[i-1]
    F = [F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12]


class IlluminantLED(object):
    LED1 = SpectralCurve.SpectralCurve('LED1', illuminantLEDdata[0], illuminantLEDdata[1])
    LED2 = SpectralCurve.SpectralCurve('LED2', illuminantLEDdata[0], illuminantLEDdata[2])
    LED3 = SpectralCurve.SpectralCurve('LED3', illuminantLEDdata[0], illuminantLEDdata[3])
    LED4 = SpectralCurve.SpectralCurve('LED4', illuminantLEDdata[0], illuminantLEDdata[4])
    LED5 = SpectralCurve.SpectralCurve('LED5', illuminantLEDdata[0], illuminantLEDdata[5])
    LED6 = SpectralCurve.SpectralCurve('LED6', illuminantLEDdata[0], illuminantLEDdata[6])
    LED7 = SpectralCurve.SpectralCurve('LED7', illuminantLEDdata[0], illuminantLEDdata[7])
    LED8 = SpectralCurve.SpectralCurve('LED8', illuminantLEDdata[0], illuminantLEDdata[8])

    # data for LEDi is also at LED[i-1]
    LED = [LED1, LED2, LED3, LED4, LED5, LED6, LED7, LED8]
