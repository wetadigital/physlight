# PhysLight

This repository contains example materials for Weta Digital's *PhysLight* system as presented in the Siggraph 2020 Talk *PhysLight: An End-to-End Pipeline for Scene-Referred Lighting*. [Slides can be found here.](https://drive.google.com/file/d/1a2jGciAmfH9yPdJCXNuNNEs_U07znp9C/view?usp=sharing)

![teaser image](img/teaser_gmp.jpg)


The [imaging notebook](https://github.com/wetadigital/physlight/blob/master/physlight_imaging.ipynb) shows a simple example of calculating the imaging ratio and checking that it gives the correct response for an idealized camera system.

The `data` directory contains the spectral sensitivity curves of a number of cameras as measured with our 'lightsaber' system. It also contains [a notebook](https://github.com/wetadigital/physlight/blob/master/data/plot_curves.ipynb) that loads the data and plots the curves for visual inspection.


![curves image](img/plot_5div.png)


The [physlight camera model notebook](https://github.com/wetadigital/physlight/blob/master/physlight_camera_model.ipynb) shows how to use the curves to convert from spectral radiance to Camera RGB, solve matrices to go from Camera RGB to XYZ, and compares different approaches for handling white balance.

![chart image](img/chart_wb.png)

# Installation

Three installation methods are available to run the two notebooks. The first
method requires [Python 3](https://www.python.org/downloads/), the second and
third methods requires [Poetry](https://python-poetry.org/) and
[Docker](https://www.docker.com/) respectively.

## Virtual Environment

With a [Virtual Environment](https://docs.python.org/3/tutorial/venv.html)
created and activated:

```bash
$ pip3 install -r requirements.txt
```

## Docker

Creating the container with the [Dockerfile](https://docs.docker.com/engine/reference/builder/)
is done as follows:

```bash
$ docker build -t wetadigital/physlight:latest "."
```

## Poetry

[Poetry](https://python-poetry.org/) can also be used to install the main
dependencies:

```bash
$ poetry install
$ poetry run python -c "import imageio;imageio.plugins.freeimage.download()"
```

# Usage

The following sections describes the commands to run to launch the Jupyter
Notebook server according to your installation method.

## Virtual Environment

```bash
$ jupyter notebook
```

## Docker

```bash
$ docker run -v $PWD:/home/weta-digital/physlight -p 8888:8888 wetadigital/physlight:latest
```

## Poetry

```bash
$ poetry run jupyter notebook
```
