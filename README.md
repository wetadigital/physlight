# PhysLight

This repository contains example materials for Weta Digital's *PhysLight* system.

First, the [imaging notebook](https://github.com/wetadigital/physlight/blob/master/physlight_imaging.ipynb) shows a simple example of calculating the imaging ratio and checking that it gives the correct response for an idealized camera system.

The `data` directory contains the spectral sensitivity curves of a number of cameras as measured with our 'lightsaber' system. It also contains [a notebook](https://github.com/wetadigital/physlight/blob/master/data/plot_curves.ipynb) that loads the data and plots the curves for visual inspection.


![curves image](img/plot_5div.png)


The [physlight camera model notebook](https://github.com/wetadigital/physlight/blob/master/physlight_camera_model.ipynb) shows how to use the curves to convert from spectral radiance to Camera RGB, solve matrices to go from Camera RGB to XYZ, and compares different approaches for handling white balance.

![chart image](img/chart_wb.png)
