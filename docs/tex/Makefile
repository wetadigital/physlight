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
    physlight.cls

MAIN := main
BIB_AUX := $(shell grep newcites $(MAIN).tex | tr '{}' '  ' | awk '{print $$2}')
OUTDIR := built
OUTPUTNAME := physLight
TEXOPTS := --shell-escape --file-line-error --synctex=1
DIRS := built

LATEX := lualatex
BIBTEX := bibtex

all: $(OUTPUTNAME).pdf

built:
	mkdir $(OUTDIR)

clean:
	-rm -rf ./$(OUTDIR)/
	-rm -rf ./_minted-main/
	-rm main.synctex.gz main.pdf main.aux main.log main.out main.toc 
	-rm main.bbl main.blg main.idx main.ind main.ilg main.lof main.lot 
	-rm rad.aux sec_*.aux

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
	    (cd $(OUTDIR) && BIBINPUTS=..: $(BIBTEX) $$f.aux) \
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


