# PhysLight White Paper

This document details how to build the *PhysLight* white paper

## Super Quick guide

If you have a (recent, 2023+) working setup of LaTeX, and pygments installed,
you need to add these fonts: 
 - Courier Prime,
 - Charmonman,
 - Noto Sans,
 - Noto Sans Mono.

These can all be found at https://fonts.google.com

Then either
 - open `main.tex` in *TeXStudio* and use the `Compile` or `Build and View` commands; OR
 - (if you have make) open a shell and type `make`

The `make` method is much cleaner in how it manages intermediate files,
while the *TeXStudio* method is more convenient (and also works on Windows).

## More Detailed Guide

The white paper is a moderately complex TeX document relying on a few OpenType fonts,
the *pygments* syntax highlighter and looks best when built with the LuaLaTeX engine.

The build has been tested on Linux with
  - texlive-2019
  - pygments-2.3.1

This document uses these free fonts:
  - Courier Prime (Google - https://fonts.google.com/)
  - Charmon (Google - https://fonts.google.com/)
  - Noto Sans (Google - https://fonts.google.com/)
  - Noto Sans Mono (Google - https://fonts.google.com/)
  - TeX Gyre Pagella (TeXLive)

In parentheses you will find a source for them

### Before we begin

Compiling this document requires the `--shell-escape` option to be passed to the
LaTeX engine, which allows it to invoke external executables.
The implementation of `--shell-escape` is _very_ simple, it's pretty much just a system call with `stdout` capture. Because it's so open, in TeX circles it is looked with circumspection and care.

We surveyed the need for `--shell-escape` and we found these reasons for using it
  - the `ifplatform` and `minted` packages
  - `\makeglossaries` uses the shell for the glossary stuff
  -  `\makeindex` uses `texindy` for the index

Also note that (for no particular reason beyond force of habit) we use `bibtex` for the bibliography.


### Linux preparation
On a Debian-ish Linux, the binaries can be installed with something like

```shell
 $ sudo apt install texlive-full
 $ sudo apt install python3-pygments
```

 These are the basic steps for installing fonts on Linux:
  - download font package
  - unpack in some directory
  - copy into /usr/local/share/fonts/&lt;kind>/&lt;familyname> (needs sudo)
  - or alternatively into ~/.local/share/fonts/&lt;kind>/&lt;familyname> (no sudo, current user only)
  - rebuild font cache (no sudo)

Example:
```shell
 $ sudo mkdir /usr/local/share/fonts/opentype/charmonman/
 $ sudo cp Charmonman-* /usr/local/share/fonts/opentype/charmonman/
 $ fc-cache -f -v
```
 You can use the `fc-list` command to view font names on your system.
 Note that font naming is a fairly complicated affair, so it's often quite non-obvious what FontConfig (the `fc-xxx` commands) thinks the font name actually is.

### Linux Execution
 The document comes with makefiles, so (on unix-like systems) you can build using simply
```shell
$ make
```
the makefile invokes the various components of TeX so that all the intermediate files go in a directory called `built`.

Alternatively, the document will build just fine with the classic simple LaTeX sequence
```shell
 $ lualatex --shell-escape main.tex
 $ bibtex main
 $ lualatex --shell-escape main.tex
 $ lualatex --shell-escape main.tex
```
but note this will leave all the intermediates (and there are quite a few) in the base document directory.

The TeXStudio method has the convenience of working from within the editor UI, but also leaves 
intermediates right next to the source files. TeX people like this, I do not, YMMV

### Windows preparation

 - install texlive or miktex (pick a "full" installation)
 - install python 3
 - install pygments (`pip install pygments` in a cmd prompt should do it)
   - it seems that `pygmentize.exe` will install in `~/AppData/Roaming/Python/Python310/Scripts/pygmentize.exe`
   - in order to make TeXStudio work with that, you need to tune its configuration a bit:
     - in TeXStudio, Options->Configure TeXStudio->Build
     - check the "Show Advanced Options" box at the bottom left of the dialog
     - checking that, the a new text entry at the bottom of the window is revealed, called 
       "Commands ($PATH)": note this is in *addition* to the normal path
     - add the path to `pygmentize.exe` there, it'll be something like `~/AppData/Roaming/Python/Python310/Scripts` (replace `~` with your user home, say `/Users/johndeer`)

 - install the fonts
   - one slow-but-simple method is right-clicking the font files and choosing `Install`
   - you can also copy them in `%WINDIR%\Fonts` (system-wide install)
   - or `%LOCALAPPDATA%\Microsoft\Windows\Fonts` (per-user install)

### Windows execution
 With all the setup above in place, building on Windows should "just work"(TM) from inside TeXStudio because of
 the "magic comments" in `main.tex`



## Illustrations

> These are very old notes on how the basic starting point for some illustrations were
 generated. Be aware that a fair few of the ones we have now were redrawn
 (largely by Johannes Meng, to whom we are quite grateful) in Inkscape and are available as
 Inkscape SVG files in the repo.

To make pictures (not a very perfect process, TBH):

use geogebra (https://www.geogebra.org/) to make a diagram
  - once you're ready to export use `Export to PGF/TikZ` and choose these options:
    - x units: 1.0, y units: 1.0
    - setup x/y min/max to include the picture
       (note this draws on the diagram the part that will be exported so you can tweak)
    - press `Generate PGF/TikZ` code
    - copy-paste the block `\begin{tikzpicture}` into the document

The export is a *great starting point*, but you will easily notice that in several places it'll
be less than ideal. So, you'll have to do manual adjustments of various kinds,
typically on label positioning and formatting. Luckily TikZ source is quite easy to follow,
but this is admittedly quite hacky.
However, the GeoGebra package was very useful to get certain figures made, so this is where we ended up.


