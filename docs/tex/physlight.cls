% A simple class inheriting from "report" that configures it with our stile
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{physlight}[2022/04/29 Class for the physlight document]

% used to set up a few symbols the way I want them to look like
\newif\ifkeepphi
\newif\ifkeepepsilon
\keepphifalse
\keepepsilonfalse
% used in the source to skip over minted sections
\newif\ifwithminted % defined later
\withmintedtrue
% don't abort if we're told to run with a plain engine
\newif\ifusepl@inengine
\usepl@inenginefalse
% our package options
\DeclareOption{keepphi}{\keepphitrue}
\DeclareOption{keepepsilon}{\keepepsilontrue}
\DeclareOption{nominted}{\withmintedfalse}
\DeclareOption{useplainengine}{\usepl@ineneginetrue}
\DeclareOption{colorfulfontdebug}{\PassOptionsToPackage{colorfuldebug}{minionproopticals}}
% everything else goes to 'article'
\DeclareOption*{%
	\PassOptionsToClass{\CurrentOption}{report}%
}
\ProcessOptions\relax
\LoadClass[11pt,a4paper]{report}

% engine detection, platform detection is below
\RequirePackage{ifpdf,ifxetex,ifluatex}
% useful to type directly diacritic characters
% not needed for xelatex or lualatex, they're already in utf8 mode
\ifluatex\else\ifxetex\else
  \RequirePackage[utf8]{inputenc} 
\fi\fi

% it appears these need to come before fontspec ?
\RequirePackage{commath} % maths
\RequirePackage{amssymb} % maths
\RequirePackage{amsmath} % maths
\RequirePackage{dsfont}  % maths

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Engine management

% use this to detect if OpenType fonts are available
\newif\ifhaveopentype

\ifluatex
	% lualatex
	% quiet sends warning to the log only
	% really, we're just trying to quiet script-not-exist-latn
	% which could use something like warnings-off={script-not-exist-latn} 
	% (which works with unicode-math, but apparently not fontspec)
	\RequirePackage{fontspec}
	% enable support for proper OpenType Math fonts (say Tex Gyre Pagella Math)
	\RequirePackage{unicode-math} 
	% it seems lualatex's --shell-escape option has been disabled
	% https://tex.stackexchange.com/questions/268486/xelatex-and-ifplatform-catchfile-loaded-by-minted-errors-on-compilation
	\RequirePackage{shellesc} 
	% needs to come after shellesc for LuaTeX
	\RequirePackage{ifplatform}
	% inspired by ConTeXt, I can't believe there isn't a better way to do this
	\def\texenginename{Lua\TeX}
	% enable advanced font features
	\haveopentypetrue
\else\ifxetex
	% xelatex
	% fontspec + enable use of OpenType non-math in math
	\RequirePackage{mathspec} 
	%\RequirePackage{xunicode} % not needed since TeXLive 2017
	\RequirePackage{xltxtra}  % xelatex extra pieces
	% enable TeX ligatures: `` '' -- --- !` ?` << >>
	% works in xelatex but not needed in lualatex
	\defaultfontfeatures{Ligatures=TeX}
	% needs to come after shellesc for LuaTeX, so we have it here too
	\RequirePackage{ifplatform}
	% inspired by ConTeXt, I can't believe there isn't a better way to do this
	\def\texenginename{\XeTeX}
	% enable advanced font features
	\haveopentypetrue
\else
	\ifusepl@inengine\else
	  % other engine, treating as plain Knuth engine 
	  \typeout{ ******** This class requires LuaLaTeX or XeLaTeX ******** } 
	  \typeout{ *************** [Tested on  TeXLive 2017] *************** } 
	  \typeout{ ** Processing will continue, but it's unlikely to work ** } 
	  \typein{} % pause to attract attention from the user
  	  \bye
	\fi
	% needs to come after shellesc for LuaTeX, so we have it here too
	\RequirePackage{ifplatform}
	% inspired by ConTeXt, I can't believe there isn't a better way to do this
	\def\texenginename{Plain \LaTeX}
	% disable advanced font features
	\haveopentypefalse
\fi % ifxetex
\fi % ifluatex

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Font management

% ADF Foundry ornaments font, used in Appendix C
\RequirePackage{adforn}

% Provides \degree for the raised circle symbol
\RequirePackage{gensymb}

% This is from mathbbm.sty: use \mathbbm to get double-struck numbers.
% We need to do it this specific way is because of how mathspec handles numbers
% we can now write a double-struck 1 as \mathbbm{1}
\newcommand{\mathbbm}[1]{\text{\usefont{U}{bbm}{m}{n}#1}} 

% since recent fontspec, instead of doing
% \NewFontFamily\foo\foofamily{Ubuntu Mono}
% we can simply do
% \newfontfamily\foofamily[NFSSFamily=foo]{Ubuntu Mono}
% replace Unicode{E1C0} with ^^^^e1c0 (note capitalization)
	
% used to set up a few symbols the way I want them to look like
\newif\ifswapphi
\newif\ifswapepsilon
\swapphitrue
\swapepsilontrue

\ifhaveopentype
	% enable finer glossing on the layout
	\RequirePackage{microtype}
	% TeX Gyre Pagella is the main document font
	\setmainfont{TeX Gyre Pagella}
	\setmathfont{TeX Gyre Pagella Math} 
	\ifxetex
		% mathspec already swaps these for us
		\swapphifalse     
		\swapepsilonfalse
	\fi

	% sans serif
	\setsansfont[BoldFont={* Bold}]{Noto Sans}
	\setmathsf[BoldFont={* Bold}]{Noto Sans}
	% monospaced
	\setmonofont[Scale=MatchLowercase]{DejaVu Sans Mono}
	\setmathtt[Scale=MatchLowercase]{DejaVu Sans Mono}

	% for sections titling in sans, should be black 900
	\newfontfamily\sectionsFont[LetterSpace=-5,
	                            UprightFont={* Bold},
	                            BoldFont={* Bold}]{Noto Sans}

	% for the units
	\newfontfamily\unitFont[Scale=MatchLowercase,NFSSFamily=unitFontFamily]{Courier Prime}
	
	% for the listings
	\newfontfamily\mintedFontFamily[Scale=MatchLowercase,NFSSFamily=mintedFontFamily]{DejaVu Sans Mono}

	% this is the font for the physlight "logo". It was designed for Zapf's zapfino font
	% which requires a commercial license
	%\newfontfamily\swashFont[Scale=.9]{Zapfino}
	\newfontfamily\swashFont[Scale=.9]{Charmonman}
	\def\swashytest{\textrm{\swashFont p\kern-.075ex h\kern-.07ex y\kern-.075ex sics}}
	\def\physLight{{\swashFont p\kern-.05ex h\kern-.075ex y\kern-.1ex s\kern-.1ex L\kern-.15ex ig\kern-.25ex ht}}
\else % haveopentypefalse
	\def\swashytest{\textit{<<should be in swash font>>}}
	% use vanilla fonts
	\def\physLight{\emph{physLig\kern-.425ex ht}}
	\allsectionsfont{\sf}
\fi % haveopentype

% prepare for the swapsies to happen at document{begin}
\AtBeginDocument{
  \ifswapphi
  	\ifkeepphi\else
  	  \let\old@phi\phi
	  \let\old@varphi\varphi
	  \let\phi\old@varphi
	  \let\varphi\old@phi
	\fi % keepphi
  \fi % swapphi
  \ifswapepsilon
  	\ifkeepepsilon\else
	  \let\old@epsilon\epsilon
	  \let\old@varepsilon\varepsilon
	  \let\epsilon\old@varepsilon
	  \let\varepsilon\old@epsilon
	\fi % keepepsilon
  \fi % swapepsilon
  %\let\old@emptyset\emptyset
  %\let\old@varnothing\varnothing
  % this is admittedly a bit heavyhanded...
  \def\emptyset{\text{\O}}
  %\let\varnothing\old@emptyset % I doubt anyone would want this, but just in case...
}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Setup package options
% in this thread there is an interesting suggestion that packages should have their
% options passed in using \PassOptionsToPackage so that if another package loads ours
% we get the options setup we need
% https://tex.stackexchange.com/questions/64599/package-options-and-requirepackage-order-of-commands-and-option-conflicts/64614

% used for font color
\PassOptionsToPackage{usenames}{xcolor}
\PassOptionsToPackage{style=authoryear,backend=biber,hyperref=true,backref=true}{biblatex}
%\PassOptionsToPackage{square,comma,sort&compress}{natbib}
\PassOptionsToPackage{makeindex,toc,numberedsection=autolabel}{glossaries}
\PassOptionsToPackage{undefaction=warn}{glossaries-extra}
\PassOptionsToPackage{makeindex}{imakeidx}
\PassOptionsToPackage{colorlinks=true}{hyperref} 
\ifwithminted
  %\PassOptionsToPackage{outputdir=built}{minted}
\fi
\PassOptionsToPackage{capitalise,noabbrev}{cleveref}
\PassOptionsToPackage{top=1in, bottom=1.4in, left=1.25in, right=1.25in}{geometry}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Load the corresponding packages

% subfigures in figures
\RequirePackage{subfigure}

% configure fonts for captions
\RequirePackage{caption}

\ifluatex\else
  % enable the use of more than 16 (?) \write allocations
  % (no need in LuaTeX)
  \RequirePackage{morewrites}
\fi

% used for font color
\RequirePackage{xcolor}

% appendices at end of chapter: use \begin{subappendices}
\RequirePackage{appendix}
\RequirePackage{chngcntr}
\RequirePackage{etoolbox}

% set up bibliography
\RequirePackage{biblatex}
% used for end-of-chapter bibliographies
%\RequirePackage{multibib}
% provide citation page numbers in the bibliography
%\RequirePackage{citeref}

% for \url, has to come after amsmath
\RequirePackage{hyperref} 

% glossary and acronyms, has to come after hyperref so we get gls and index items hyperlinked
\RequirePackage{glossaries}
\RequirePackage{glossaries-extra}
\RequirePackage{imakeidx}
% ... up to here for simplicity, but only glossaries needs that, strictly speaking

% \multirow command in tabular environments
\RequirePackage{multirow} 

% for XMP data in PDF
\RequirePackage{hyperxmp} 

% use pygments to do syntax highlighting of code
% if pygmentize is not available, use the nominted option
\ifwithminted
  \RequirePackage{minted}
\fi
% page breaks with minted
\RequirePackage{mdframed}

% boxes with colors around them
\RequirePackage{tcolorbox}

% quotes at start of chapters
\RequirePackage{epigraph}

% tikz/pgf for images
\RequirePackage{pgf,tikz}


% configure spacing around listing
\RequirePackage{enumitem}

% for header/footer construction
\RequirePackage{lastpage}
\RequirePackage{fancyhdr}

% used to silence warnings
\RequirePackage[immediate]{silence}

% convenient setup for fonts in section headings
% silence the warnings 
%  Command \underbar  has changed.
%  Command \underline  has changed.
\WarningFilter[sectstywarnings]{latex}{Command} 
\RequirePackage{sectsty}
\DeactivateWarningFilters[sectstywarnings]

% handling of SI units
\RequirePackage{siunitx}

% allows crossreferencing and reusing of footnotes using \cref
\RequirePackage{cleveref}

% add support for \marginnote
\RequirePackage{marginnote}

% retouch margins
\RequirePackage{geometry}

% add \sfrac t typeset slash fractions
\RequirePackage{xfrac}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Other various setup

% used to omit blocks of stuff, for example:
% \ifomit 
%    all of this will be skipped
% \fi
\newif\ifomit
\omitfalse

% [appendix] Start of subappendices environment
\AtBeginEnvironment{subappendices}{%
	\section*{Appendices}
	\addcontentsline{toc}{section}{Appendices}
	\counterwithin{figure}{subsection}
	\counterwithin{table}{subsection}
}

% [appendix] End of subappendices environment
\AtEndEnvironment{subappendices}{%
	\counterwithout{figure}{subsection}
	\counterwithout{table}{subsection}
}

% [enumitem] configure spacing around listing
\setlist{noitemsep}
% [cleveref]
\crefformat{footnote}{#2\footnotemark[#1]#3}

% page layout configuration
\ifhaveopentype
  \setlength{\headheight}{31.5pt}
\else
  \setlength{\headheight}{15pt}
\fi
% [epigraph] width for epigraphs
\setlength{\epigraphwidth}{.619\textwidth}

% [sectsty] restyle sections with our preferred font
\allsectionsfont{\sf}
\chapterfont{\sectionsFont}
\sectionfont{\sectionsFont}

% [minted] configure minted environments
\ifwithminted
	% to check what pygmentize styles are available use
	% pygmentize -L styles
	\usemintedstyle{friendly}
	% redefine \theFancyVerbLine to control the formatting of line numbers
	\definecolor{minted-bg}{rgb}{.95, .95, .95}
	% cheat: minted is actually a thin wrapper around fancyvrb
	\fvset{
		fontfamily=mintedFontFamily,
		fontsize=\footnotesize,
		frame=topline,
		framesep=2mm,
		labelposition=topline,
		numbersep=1em,
		samepage=false,
		stepnumber=5,
		tabsize=4
	}
	%\newmint[rsl]{c++}{}
	% these two don't work, need to fix them
	%\def\rsl#1{{\Verb@#1@}}
	%\def\rib#1{{\Verb@#1@}}
	\newminted[ribcode]{text}{% no syntax highlighting
		bgcolor=minted-bg,
		label=\raisebox{-0.5ex}{RIB source},
		mathescape=true,
		texcl=true}
	\newminted[rslcode]{c++}{% pretend it's c++
		bgcolor=minted-bg,
		label=\raisebox{-0.5ex}{Shading Language source},
		mathescape=true,
		texcl=true}
	\newminted[c++code]{c++}{
		bgcolor=minted-bg,
		label=\raisebox{-0.5ex}{C++ source},
		mathescape=true,
		texcl=true}
	\newminted{python}{
		bgcolor=minted-bg,
		label=\raisebox{-0.5ex}{Python source},
		mathescape=true,
		texcl=true}
	\newminted[csvdata]{text}{
		bgcolor=minted-bg,
		label=\raisebox{-0.5ex}{CSV file},
		mathescape=true,
		texcl=true}
\fi

% [glossaries-extra] setup acronyms to be displayed in letterspaced small caps
\newcommand{\wideletterspacedsc}[1]{\textls[75]{\textsc{#1}}}
\renewcommand*{\glsfirstabbrvdefaultfont}[1]{\wideletterspacedsc{#1}}
\renewcommand*{\glsabbrvdefaultfont}[1]{\wideletterspacedsc{#1}}

% [glossaries] there seems to be some odd interaction between fancyfonts and setacronym
\ifdefined\setabbreviationstyle
  \setabbreviationstyle[acronym]{long-short}
\fi

% [caption] setup styling for our captions
\captionsetup{font=small,labelfont=bf,textfont=it}

% [siunitx] add a few units and configure unit formatting
% first, the unit symbols are set in their own font family
\sisetup{
	detect-none = true,
	detect-family = false,
	%mode = text,
	input-digits=0123456789\mitpi, % accept \pi as a digit, \mitpi is from unicode-math
	parse-numbers=false, % solves some problems with fractions, not sure what it breaks though
	exponent-product = \cdot, % 1.3\cdot10^3
	inter-unit-product = \ensuremath{{}\cdot{}}, % m\cdot s
	per-mode = symbol-or-fraction, % / in inline mode, \frac in display mode
	%number-unit-product = \text{~}, % per Chicago Manual of Style, I don't like it
	number-unit-product = \ensuremath{\;}, % a little smaller
}
\DeclareSIUnit{\talbot}{Tb}
\DeclareSIUnit{\nit}{nt}
\DeclareSIUnit{\iso}{ISO}
\DeclareSIUnit{\pixel}{pxl}
\DeclareSIUnit{\fnumber}{f-number}

\DeclareSIUnit{\foot}{ft}
\DeclareSIUnit{\inch}{in}

% alternatively we could use cd/m^2
%\def\nit\candela\per\square\meter

% [pgf] tell PGF about how we want numbers formatted
% this is a command from siunitx v2.x, in v3.x the recommendation is
% to manually keep \sisetup and pgfkeys synced by hand 
% (I will state here, Mr Wright, that I much dislike your approach, sir)
\@ifundefined{SendSettingsToPgf}{\relax}{\SendSettingsToPgf}
% I'm leaving this for another day
% inspecting this page https://github.com/josephwright/siunitx/commit/d35b06cfe6908caae543a660b06d7a9338bfbd9a
% it seems that /pgf/number~format needs to be kept in sync in these settings
% figures 
%{
%  fixed , % fixed-width? lining?
%  fixed~zerofill = true , % leading zeros?
%}
% precision = 
% set~decimal~separator = 
% set~thousands~separator =
% min~exponent~for~1000~sep =
% showpos =   % force showing '+' for positive numbers


% [fancyhdr] configure the headers/footers
\pagestyle{fancy}
\lhead{}
\chead{\leftmark}
\rhead{}
\lfoot{\physLight}
\cfoot{\textsc{\physLightVersion}}
\rfoot{Page \thepage\,/\,\pageref*{LastPage}}

% [fancyhdr] thickness of the rules
\renewcommand{\headrulewidth}{.4pt}
\renewcommand{\footrulewidth}{.4pt}
