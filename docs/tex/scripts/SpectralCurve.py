# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.

from typing import Union

# caller sanitized this
import numpy


class SpectralCurve(object):
    """
    A sampled spectral curve
    it has three members:
     - name is the curve name
     - lnms is an array containing the wavelengths of the samples
     - data is an array containing the values of the samples
    """
    def __init__(self, name, lnms, values):
        self.name = name
        self.lnms = numpy.array(lnms, float)  # copy intentional
        self.data = numpy.array(values, float) # copy intentional

    def __add__(self, other: "SpectralCurve"):
        """ Element by element addition, with resampling """
        if numpy.any(self.lnms != other.lnms):
            lnms = numpy.concatenate((self.lnms, other.lnms))
            lnms.sort(kind='mergesort')
            selfr = self.resample(lnms)
            otherr = other.resample(lnms)
            return selfr + otherr
        # sum of 2 curves
        return SpectralCurve("", self.lnms, self.data + other.data)

    def __mul__(self, other: Union["SpectralCurve", float]):
        """ Element by element multiplication, with resampling """
        if hasattr(other, "lnms"):
            if numpy.any(self.lnms != other.lnms):
                lnms = numpy.concatenate((self.lnms, other.lnms))
                lnms.sort(kind='mergesort')
                selfr = self.resample(lnms)
                otherr = other.resample(lnms)
                return selfr * otherr
            # product of 2 curves
            return SpectralCurve("", self.lnms, self.data * other.data)
        # product with a scalar
        return SpectralCurve("", self.lnms, self.data * other)

    def __rmul__(self, other):
        return self * other

    def __imul__(self, other: Union["SpectralCurve", float]):
        if hasattr(other, "lnms"):
            if numpy.any(self.lnms != other.lnms):
                lnms = numpy.concatenate((self.lnms, other.lnms))
                lnms.sort(kind='mergesort')
                selfr = self.resample(lnms)
                otherr = other.resample(lnms)
                result = selfr * otherr
                self.lnms = result.lnms
                self.data = result.data
            else:
                self.data *= other.data
        else:
            self.data *= other
        return self

    def sample(self, lnm: Union[numpy.array, list[float], float]):
        """ Samples the curve at the given wavelength """
        return numpy.interp(lnm, self.lnms, self.data, left=0, right=0)

    def resample(self, baseline: Union["SpectralCurve", numpy.array, list[float]]):
        """
        Returns a new curve, with samples at the given wavelengths
        If `baseline` is a SpectralCurve, the result will be sampled
        at the same wavelengths as the curve
        If `baseline` is a numpy array or python list, this will be used as a list
        of wavelenths to use
        """
        lnms = baseline
        if hasattr(baseline, "lnms"):
            lnms = baseline.lnms
        return SpectralCurve(self.name, lnms, self.sample(lnms))


def makeFromMinSpcData(name: str, minl: float, spacing: float, values: list[float]):
    maxl = minl + spacing * (len(values) - 1)
    return SpectralCurve(name, numpy.linspace(minl, maxl, len(values)), values)
