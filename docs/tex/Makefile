.PHONY=main_1.pdf

FILES := main.tex \
    glossary.tex \
    jenson_font.tex \
    minion_font.tex \
    sec_appendix.tex \
    sec_calcsheets.tex \
    sec_imaging.tex \
    sec_implementation.tex \
    sec_intro.tex \
    sec_lighting.tex \
    sec_radiance.tex \
    sec_theory.tex \
    sec_illuminants.tex \
    sec_sensors.tex \
    sec_notations.tex \
    warnock_font.tex \
    bibliography.bib \
    bibliography_radiance.bib

MAIN := main
BIB_AUX := $(shell grep newcites $(MAIN).tex | tr '{}' '  ' | awk '{print $$2}')
OUTDIR := built
OUTPUTNAME := physLight
OUTPUTNAME_LORES := $(OUTPUTNAME)-lores
TEXOPTS := -shell-escape
DIRS := figures-lores built

all: hires

hires: $(OUTPUTNAME).pdf

lores: $(OUTPUTNAME_LORES).pdf

built:
	mkdir $(OUTDIR)

figures-lores:
	mkdir figures-lores

clean:
	rm -r ./$(OUTDIR)/
	rm -r ./figures-lores/

# this is necessary to build intermediates in the "built/" directory
# note that naked xelatex would cope with -output-directory just fine,
# but some packages don't implement support for subdirectories correctly.
# Pygments (used by minted package) seems to be one current offender
# TEXINPUTS for all TeX input files (source and classes)
# BIBINPUTS for .bib files
# BSTINPUTS for bibliography style files
# Note: the trailing ":" in TEXINPUTS/BIBINPUTS means "add standard searchpath here"
$(OUTPUTNAME).pdf: $(FILES) Makefile $(DIRS)
	(cd $(OUTDIR) && TEXINPUTS=..: xelatex $(TEXOPTS) -jobname=$(OUTPUTNAME) $(MAIN))
	(cd $(OUTDIR) && for f in $(OUTPUTNAME) $(BIB_AUX); do BIBINPUTS=..: bibtex $$f.aux; done)
	(cd $(OUTDIR) && TEXINPUTS=..: xelatex $(TEXOPTS) -jobname=$(OUTPUTNAME) $(MAIN))
	(cd $(OUTDIR) && TEXINPUTS=..: xelatex $(TEXOPTS) -jobname=$(OUTPUTNAME) $(MAIN))
	cp $(OUTDIR)/$(OUTPUTNAME).pdf $(OUTPUTNAME).pdf

$(OUTPUTNAME_LORES).pdf: $(FILES) Makefile $(DIRS)
	sips -Z 800 figures/*.jpg --out figures-lores/
	(cd $(OUTDIR) && TEXINPUTS=..: xelatex $(TEXOPTS) -jobname=$(OUTPUTNAME_LORES) $(MAIN))
	(cd $(OUTDIR) && for f in $(OUTPUTNAME_LORES) $(BIB_AUX); do BIBINPUTS=..: bibtex $$f.aux; done)
	(cd $(OUTDIR) && TEXINPUTS=..: xelatex $(TEXOPTS) -jobname=$(OUTPUTNAME_LORES) $(MAIN))
	(cd $(OUTDIR) && TEXINPUTS=..: xelatex $(TEXOPTS) -jobname=$(OUTPUTNAME_LORES) $(MAIN))
	cp $(OUTDIR)/$(OUTPUTNAME_LORES).pdf $(OUTPUTNAME_LORES).pdf

