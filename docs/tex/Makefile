# SPDX-License-Identifier: Apache-2.0
# Copyright (c) Contributors to the PhysLight Project.

FILES := main.tex \
    glossary.tex \
    sec_appendix.tex \
    sec_calcsheets.tex \
    sec_imaging.tex \
    sec_implementation.tex \
    sec_intro.tex \
    sec_lighting.tex \
    sec_radiance.tex \
    sec_illuminants.tex \
    sec_sensors.tex \
    sec_notations.tex \
    bibliography.bib \
    bibliography_radiance.bib \
    physlight.cls \
    physlight.dbx \
    physlight.cbx \
    physlight.bbx

MAIN := main
BIB_AUX := $(shell grep newcites $(MAIN).tex | tr '{}' '  ' | awk '{print $$2}')
OUTDIR := built
FIGURE_SRC := figures_src
FIGURE_OUTDIR := figures_built
FIGURE_INTERMEDIATE := ${FIGURE_OUTDIR}/intermediate
SCRIPTSDIR := scripts

OUTPUTNAME := physLight
TEXOPTS := --shell-escape --file-line-error --synctex=1
DIRS := ${OUTDIR} ${FIGURE_OUTDIR} ${FIGURE_INTERMEDIATE}

LATEX := lualatex
BIBTEX := biber

# we would normally use just `inkscape` but when installed from 'snap' inkscape CLI doesn't work correctly :-(
INKSCAPE := ~/Downloads/Inkscape-b0a8486-x86_64.AppImage
EPSTOPDF := epstopdf
PDFCROP := pdfcrop

# all images need a construction rule below
FIGURES := $(FIGURE_OUTDIR)/in_construction.pdf \
	$(FIGURE_OUTDIR)/nicodemus1963-fig1.pdf \
	$(FIGURE_OUTDIR)/nicodemus1963-fig2.pdf \
	$(FIGURE_OUTDIR)/nicodemus1963-fig3.pdf \
	$(FIGURE_OUTDIR)/emitter_surface.pdf \
	$(FIGURE_OUTDIR)/exposure_equation_setup.pdf \
	$(FIGURE_OUTDIR)/a_img_obj.pdf \
	$(FIGURE_OUTDIR)/flux_etc.pdf \
	$(FIGURE_OUTDIR)/roscolux.pgf \
	$(FIGURE_OUTDIR)/Infrared-photo-vs-Ultraviolet-photo.jpg \
	$(FIGURE_OUTDIR)/Orthochromatic-Panchromatic-film-1024x768-1.jpg \
	$(FIGURE_OUTDIR)/raydiff-1.tikz.tex \
	$(FIGURE_OUTDIR)/opposite-angle.tikz.tex \
	$(FIGURE_OUTDIR)/blackbody.pgf \
	$(FIGURE_OUTDIR)/chromas.pgf \
	$(FIGURE_OUTDIR)/chromas_enlarge.pgf \
	$(FIGURE_OUTDIR)/commonilluminants.pgf \
	$(FIGURE_OUTDIR)/illuminantf1-6.pgf \
	$(FIGURE_OUTDIR)/illuminantf7-9.pgf \
	$(FIGURE_OUTDIR)/illuminantf10-12.pgf \
	$(FIGURE_OUTDIR)/illuminantd.pgf \
	$(FIGURE_OUTDIR)/cielms2006.pgf \
	$(FIGURE_OUTDIR)/ciexyz1931.pgf \
	$(FIGURE_OUTDIR)/Red_Mysterium_X.pgf \
	$(FIGURE_OUTDIR)/Canon_1DMarkIII.pgf \
	$(FIGURE_OUTDIR)/Canon_5DMarkII.pgf

all: $(OUTPUTNAME).pdf

$(OUTDIR):
	mkdir $(OUTDIR)

$(FIGURE_OUTDIR):
	mkdir $(FIGURE_OUTDIR)

$(FIGURE_INTERMEDIATE):
	mkdir -p $(FIGURE_INTERMEDIATE)

clean:
	-rm -rf $(OUTDIR)/ $(FIGURE_OUTDIR)/ $(FIGURE_INTERMEDIATE)/
	-rm -rf ./_minted-main/
	-rm -f main.synctex.gz main.pdf main.aux main.log main.out main.toc
	-rm -f main.bbl main.blg main.idx main.ind main.ilg main.lof main.lot
	-rm -f rad.aux sec_*.aux

# this is necessary to build intermediates in the "built/" directory
# note that naked lualatex would cope with -output-directory just fine,
# but some packages don't implement support for subdirectories correctly.
# Pygments (used by minted package) seems to be one current offender
# TEXINPUTS for all TeX input files (source and classes)
# BIBINPUTS for .bib files
# BSTINPUTS for bibliography style files
# Note: the trailing ":" in TEXINPUTS/BIBINPUTS means "add standard searchpath here"
# The ln cmds at the bottom set things up so TeXStudio's builtin viewer can jump into the right
# source location
$(OUTPUTNAME).pdf: $(FILES) Makefile | $(DIRS)
	(cd $(OUTDIR) && TEXINPUTS=..: $(LATEX) $(TEXOPTS) --jobname=$(OUTPUTNAME) $(MAIN))
	for f in $(OUTPUTNAME) $(BIB_AUX); do \
	    (cd $(OUTDIR) && BIBINPUTS=..: $(BIBTEX) $$f.bcf) \
	done
	(cd $(OUTDIR) && makeindex -s $(OUTPUTNAME).ist -o $(OUTPUTNAME).gls $(OUTPUTNAME).glo)
	(cd $(OUTDIR) && TEXINPUTS=..: $(LATEX) $(TEXOPTS) --jobname=$(OUTPUTNAME) $(MAIN))
	(cd $(OUTDIR) && TEXINPUTS=..: $(LATEX) $(TEXOPTS) --jobname=$(OUTPUTNAME) $(MAIN))
	cp $(OUTDIR)/$(OUTPUTNAME).pdf $(OUTPUTNAME).pdf
	ln -sf $(OUTPUTNAME).pdf main.pdf
	ln -sf $(OUTDIR)/$(OUTPUTNAME).synctex.gz ./main.synctex.gz

# a "compile once" quick hack for fast iteration, just meant for small changes
.PHONY: quick quickglo
# without glossary rebuild
quick: $(FILES) Makefile
	(cd $(OUTDIR) && TEXINPUTS=..: $(LATEX) $(TEXOPTS) --jobname=$(OUTPUTNAME) $(MAIN))
	cp $(OUTDIR)/$(OUTPUTNAME).pdf $(OUTPUTNAME).pdf
	ln -sf $(OUTPUTNAME).pdf main.pdf
	ln -sf $(OUTDIR)/$(OUTPUTNAME).synctex.gz ./main.synctex.gz

# with glossary rebuild
quickglo: $(FILES) Makefile
	(cd $(OUTDIR) && TEXINPUTS=..: $(LATEX) $(TEXOPTS) --jobname=$(OUTPUTNAME) $(MAIN))
	(cd $(OUTDIR) && makeindex -s $(OUTPUTNAME).ist -o $(OUTPUTNAME).gls $(OUTPUTNAME).glo)
	(cd $(OUTDIR) && TEXINPUTS=..: $(LATEX) $(TEXOPTS) --jobname=$(OUTPUTNAME) $(MAIN))
	cp $(OUTDIR)/$(OUTPUTNAME).pdf $(OUTPUTNAME).pdf
	ln -sf $(OUTPUTNAME).pdf main.pdf
	ln -sf $(OUTDIR)/$(OUTPUTNAME).synctex.gz ./main.synctex.gz

.phony: figures
figures: ${FIGURES}

# the bbox for the crop was determined opening the EPS source in `gv` and using the mouse to determine the bbox coordinates
$(FIGURE_OUTDIR)/in_construction.pdf: $(FIGURE_SRC)/images/43301396_eps_normal_none.eps | $(FIGURE_OUTDIR) $(FIGURE_INTERMEDIATE)
	${EPSTOPDF} $(FIGURE_SRC)/43301396_eps_normal_none.eps $(FIGURE_INTERMEDIATE)/43301396_eps_normal_none.pdf
	${PDFCROP} --bbox "365 46 461 132" $(FIGURE_INTERMEDIATE)/43301396_eps_normal_none.pdf $(realpath $(dir $@))/$(notdir $@)

$(FIGURE_OUTDIR)/nicodemus1963-fig1.pdf: $(FIGURE_SRC)/images/nicodemus1963/nicodemus1963-fig1.pdf | $(FIGURE_OUTDIR)
	cp $(realpath $<) $(realpath $(dir $@))/$(notdir $@)

$(FIGURE_OUTDIR)/nicodemus1963-fig2.pdf: $(FIGURE_SRC)/images/nicodemus1963/nicodemus1963-fig2.pdf | $(FIGURE_OUTDIR)
	cp $(realpath $<) $(realpath $(dir $@))/$(notdir $@)

$(FIGURE_OUTDIR)/nicodemus1963-fig3.pdf: $(FIGURE_SRC)/images/nicodemus1963/nicodemus1963-fig3.pdf | $(FIGURE_OUTDIR)
	cp $(realpath $<) $(realpath $(dir $@))/$(notdir $@)

$(FIGURE_OUTDIR)/Infrared-photo-vs-Ultraviolet-photo.jpg: $(FIGURE_SRC)/images/Infrared-photo-vs-Ultraviolet-photo.jpg | $(FIGURE_OUTDIR)
	cp $(realpath $<) $(realpath $(dir $@))/$(notdir $@)

$(FIGURE_OUTDIR)/Orthochromatic-Panchromatic-film-1024x768-1.jpg: $(FIGURE_SRC)/images/Orthochromatic-Panchromatic-film-1024x768-1.jpg | $(FIGURE_OUTDIR)
	cp $(realpath $<) $(realpath $(dir $@))/$(notdir $@)

$(FIGURE_OUTDIR)/emitter_surface.pdf: $(FIGURE_SRC)/diagrams/emitter_surface.svg | $(FIGURE_OUTDIR)
	${INKSCAPE} --export-type=PDF --export-latex -o $(realpath $(dir $@))/$(notdir $@) $(realpath $<)

$(FIGURE_OUTDIR)/exposure_equation_setup.pdf: $(FIGURE_SRC)/diagrams/exposure_equation_setup.svg | $(FIGURE_OUTDIR)
	${INKSCAPE} --export-type=PDF --export-latex -o $(realpath $(dir $@))/$(notdir $@) $(realpath $<)

$(FIGURE_OUTDIR)/a_img_obj.pdf: $(FIGURE_SRC)/diagrams/a_img_obj.svg | $(FIGURE_OUTDIR)
	${INKSCAPE} --export-type=PDF --export-latex -o $(realpath $(dir $@))/$(notdir $@) $(realpath $<)

$(FIGURE_OUTDIR)/flux_etc.pdf: $(FIGURE_SRC)/diagrams/flux_etc.svg | $(FIGURE_OUTDIR)
	${INKSCAPE} --export-type=PDF --export-latex -o $(realpath $(dir $@))/$(notdir $@) $(realpath $<)

$(FIGURE_OUTDIR)/raydiff-1.tikz.tex: $(FIGURE_SRC)/diagrams/raydiff-1.tikz.tex | $(FIGURE_OUTDIR)
	cp $(realpath $<) $(realpath $(dir $@))/$(notdir $@)

$(FIGURE_OUTDIR)/opposite-angle.tikz.tex: $(FIGURE_SRC)/diagrams/opposite-angle.tikz.tex  | $(FIGURE_OUTDIR)
	cp $(realpath $<) $(realpath $(dir $@))/$(notdir $@)

$(FIGURE_OUTDIR)/blackbody.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/chromas.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/chromas_enlarge.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/commonilluminants.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/illuminantf1-6.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/illuminantf7-9.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/illuminantf10-12.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/illuminantd.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/cielms2006.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/ciexyz1931.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/roscolux.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/Red_Mysterium_X.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/Canon_1DMarkIII.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))

$(FIGURE_OUTDIR)/Canon_5DMarkII.pgf: $(SCRIPTSDIR)/make_all_figures.py | $(FIGURE_OUTDIR)
	${SCRIPTSDIR}/make_all_figures.py -o $(realpath $(dir $@))/$(notdir $@) $(basename $(notdir $@))
