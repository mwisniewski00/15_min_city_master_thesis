% -------------------------------------------------------------------------------------------------------
% Klasa służąca do składu prac licencjackich i magisterskich w języku polskim
% na wydziale Matematyki, Fizyki i Informatyki Uniwersytetu Gdańskiego.
%
% Class for submitting bachelor's and master's theses (in Polish) at the Faculty of Mathematics, 
% Physics and Computer Science of the University of Gdańsk.
%
% Created in compability with LATEX distribution: MiKTeX 2.9.7342
%
% Author: Monika Barzowska (barzowskam@gmail.com)
% Shared under the MIT license.
% -------------------------------------------------------------------------------------------------------



% -------------------------------------------------------------------------------------------------------
% Available custom document options:
% -------------------------------------------------------------------------------------------------------
% On the number of  thesis' authors:
% oneauthor, twoauthors, threeauthors
% On thesis type:
% bachelorthesis, masterthesis
% On the place of submission:
% instituteoffice, deansoffice 



% -------------------------------------------------------------------------------------------------------
% Identification
% -------------------------------------------------------------------------------------------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{mfipl}[2020/02/12 v1.0]



% -------------------------------------------------------------------------------------------------------
% Preliminary declarations (base class)
% -------------------------------------------------------------------------------------------------------
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{report}} 
\ProcessOptions\LoadClass{report} 



% -------------------------------------------------------------------------------------------------------
% Required packages and their configuration
% -------------------------------------------------------------------------------------------------------
% Set of packages providing Polish language support -----------------------------------------------------
\RequirePackage[english,polish]{babel}
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{lipsum}

% Common/basic packages ---------------------------------------------------------------------------------
% enumerate		adds an optional argument to the enumerate environment which determines the style 
%				in which the counter is printed
% CTAN page:	https://www.ctan.org/pkg/enumerate
\RequirePackage{enumerate}

% enumitem		provides user control over the layout of the three basic list environments: enumerate, 
%				itemize and description
% CTAN page:	https://www.ctan.org/pkg/enumitem
\RequirePackage{enumitem}

% geometry		provides flexible user interface to customize page layout
% CTAN page: 	https://www.ctan.org/pkg/geometry
\RequirePackage{geometry}

% xifthen		allows conditional commands in LATEX documents
% CTAN page:	https://www.ctan.org/pkg/xifthen
\RequirePackage{xifthen}

% Math related ------------------------------------------------------------------------------------------
\RequirePackage{amsmath} 			
\RequirePackage{mathtools} 	
\RequirePackage{amsfonts} 		
\RequirePackage{amsthm}			

% eqexpl		its purpose is to enable a perfectly formatted explanation of components of a formula
% CTAN page:	https://www.ctan.org/pkg/eqexpl
\RequirePackage{eqexpl}

% siunitx 		a comprehensive (SI) units package
% CTAN page: 	https://www.ctan.org/pkg/siunitx
\RequirePackage{siunitx}

% Pics related ------------------------------------------------------------------------------------------
% caption		provides many ways to customise the captions in floating environments like figure 
%				and table, and cooperates with many other packages		
% CTAN page:	https://www.ctan.org/pkg/caption
\RequirePackage[labelfont=bf, format=plain, justification=centering,singlelinecheck=false]{caption}

% graphicx		builds upon the standard graphics package
% CTAN page: 	https://www.ctan.org/pkg/graphicx
\RequirePackage{graphicx}

% subcaption	provides a means of using facilities analagous to those of the caption package, 
%				when writing captions for subfigures and the like
% CTAN page:	https://www.ctan.org/pkg/subcaption	
\RequirePackage{subcaption}

% Code snippets related ---------------------------------------------------------------------------------
% listings		enables the user to typeset programs (programming code) within LATEX
% CTAN page:	https://www.ctan.org/pkg/listings	
\RequirePackage{listings}

% xcolor		provides colour control for LATEX documents
% CTAN page: 	https://www.ctan.org/pkg/xcolor
\RequirePackage{xcolor}

% Tables related ----------------------------------------------------------------------------------------
% array 		extends the options for column formats
% CTAN page:	https://www.ctan.org/pkg/array
\RequirePackage{array}

% Bibliography related ----------------------------------------------------------------------------------
% csquotes		provides advanced facilities for inline and display quotations
% CTAN page:	https://www.ctan.org/pkg/csquotes
\RequirePackage{csquotes}

% biblatex		is a complete reimplementation of the bibliographic facilities provided by LATEX
% CTAN page:	https://www.ctan.org/pkg/biblatex
\RequirePackage[
style=numeric,
sorting=none,
language=autobib,
autolang=other,
urldate=short,
backref=false,
isbn=true,
url=true,
maxbibnames=3,
backend=biber
]{biblatex}
\DefineBibliographyStrings{polish}{%
  urlseen = {dostęp:},
}
\addbibresource{bibliography.bib} 


% -------------------------------------------------------------------------------------------------------
% Unused, but recommended packages
% -------------------------------------------------------------------------------------------------------
% 	fancyhdr		provides extensive facilities, both for constructing headers and footers, 
% 					and for controlling their use
% 	CTAN page: 		https://www.ctan.org/pkg/fancyhdr
\RequirePackage{fancyhdr}

% 	rotating 		provides rotation tools, including rotated full-page floats
% 	CTAN page: 		https://www.ctan.org/pkg/rotating
\RequirePackage{rotating}

% 	titlesec		provides an interface to sectioning commands for selection from various 
%					title styles. E.g., marginal titles and to change the font of all headings 
%					with a single command, also providing simple one-step page styles
% 	CTAN page: 		https://www.ctan.org/pkg/titlesec
\RequirePackage[clearempty]{titlesec}

% 	tocloft			provides control over the typography of the Table of Contents, 
%					List of Figures and List of Tables, and the ability to create new lists
% 	CTAN page: 		https://www.ctan.org/pkg/tocloft
\RequirePackage{tocloft}

% 	url 			provides URL-sensitive line breaks
% 	CTAN page: 		https://www.ctan.org/pkg/url
\RequirePackage{url}



% -------------------------------------------------------------------------------------------------------
% Custom document class' options (multiple authors, thesis type, etc.) handling
% -------------------------------------------------------------------------------------------------------
\newboolean{oneauthor}
\newboolean{twoauthors}
\newboolean{threeauthors}
\DeclareOption{oneauthor}{%
	\setboolean{oneauthor}{true}
}
\DeclareOption{twoauthors}{%
	\setboolean{twoauthors}{true}
}
\DeclareOption{threeauthors}{%
	\setboolean{threeauthors}{true}
}

\newboolean{bachelorthesis}
\newboolean{masterthesis}
\DeclareOption{bachelorthesis}{%
	\setboolean{bachelorthesis}{true}
}
\DeclareOption{masterthesis}{%
	\setboolean{masterthesis}{true}
}

\newboolean{instituteoffice}
\newboolean{deansoffice}
\DeclareOption{instituteoffice}{%
	\setboolean{instituteoffice}{true}
}
\DeclareOption{deansoffice}{%
	\setboolean{deansoffice}{true}
}

\ProcessOptions\relax



% -------------------------------------------------------------------------------------------------------
% Document features
% -------------------------------------------------------------------------------------------------------
% Defines document margin sizes 
\geometry{lmargin=35mm, rmargin=25mm, tmargin=25mm, bmargin=25mm, foot=10mm, head=10mm}



% -------------------------------------------------------------------------------------------------------
% Overwriting of existing LaTeX commands
% -------------------------------------------------------------------------------------------------------
% Sets URL display style (changes font type from typewriter to italic)
%\renewcommand\UrlFont{\rmfamily\itshape}

% Renames listings labels
\renewcommand{\lstlistingname}{Snippet}
\renewcommand{\lstlistlistingname}{Lista snippetów}

% Renames table and picures labels
\AtBeginDocument{
	\renewcommand{\tablename}{Tabela}
	\renewcommand{\figurename}{Rysunek}
}



% -------------------------------------------------------------------------------------------------------
% Custom macros
% -------------------------------------------------------------------------------------------------------
% Adds \addtocontents{toc}{\protect\thispagestyle{empty}} to each Table of Contents chapter entry.
% Used to remove footer from a page on which given chapter will appear in Table of Contents.
% (Not elegant, but LaTeX way.)
\def\mychapter#1{%
	\chapter{#1}
	\addtocontents{toc}{\protect\thispagestyle{empty}}
}

% Adds \addtocontents{toc}{\protect\thispagestyle{empty}} to each Table of Contents section entry.
% Used to remove footer from a page on which given section will appear in Table of Contents.
% (Not elegant, but LaTeX way.)
\def\mysection#1{%
	\section{#1}
	\addtocontents{toc}{\protect\thispagestyle{empty}}
}

% The use of both of these macros should be sufficient. It's unlikely that a whole Table of Contents page 
% will ever contain only subsections.



% -------------------------------------------------------------------------------------------------------
% Appearance settings/packages options and features
% -------------------------------------------------------------------------------------------------------
% Sets number display style (according to Polish typographic) [package: siunitx]
\sisetup{
	output-decimal-marker = {,},
	%	round-mode=places,
	%	round-precision=4,
	group-separator={~},
}

% Sets caption display style [packages: caption, subcaption]
\captionsetup[subfigure]{labelfont=md}
\captionsetup{%
	subrefformat=parens,
	margin=2cm,
	singlelinecheck=on,
}

% Defines new theorem classess
\theoremstyle{definition}
%\newtheorem{algorithm}{Algorytm}[chapter]
\newtheorem{definition}{Definicja}[section]
\newtheorem{lemma}{Lemat}[section]
\newtheorem{example}{Przykład}[section]
\newtheorem{case}{Przypadek}[section]
\newtheorem{theorem}{Twierdzenie}[section]
\newtheorem{remark}{Uwaga}[section]

% Defines image directory [package: graphicx]
\graphicspath{{./images/}}

% Defines delimeter used within variable explaination [package: eqexpl]
\eqexplSetDelim{-}

% Sets code snippets' style [package: listings]
\definecolor{codegreen}{rgb}{0,0.6,0.1}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.95,0.95,0.92}

\lstdefinestyle{mystyle}{
	backgroundcolor=\color{backcolour},   
	commentstyle=\color{codegreen},
	keywordstyle=\color{magenta},
	numberstyle=\tiny\color{codegray},
	stringstyle=\color{codepurple},
	breakatwhitespace=false,         
	breaklines=true,                 
	captionpos=b,                    
	keepspaces=true,                 
	numbers=left,                    
	numbersep=5pt,                  
	showspaces=false,                
	showstringspaces=false,
	showtabs=false,                  
	tabsize=2
}

% Defines new column type; allows to use tabularx environment together with i.e. centering [package: array]
\newcolumntype{x}{>{\centering\arraybackslash}X}

% Defines quote style alias; csquotes doesn't support polish, but croatian is similar enough [package: csquotes]
\DeclareQuoteAlias{croatian}{polish}



% -------------------------------------------------------------------------------------------------------
% Front page
% -------------------------------------------------------------------------------------------------------
% Custom hangers
% \author's deafult														 									
\def\authorno#1				{\gdef\@authorno{#1}}					% nr albumu autora
\def\secondauthor#1			{\gdef\@secondauthor{#1}}				% (opcjonalnie) drugi autor
\def\secondauthorno#1		{\gdef\@secondauthorno{#1}}				% (opcjonalnie) nr albumu drugiego autora
\def\thirdauthor#1			{\gdef\@thirdauthor{#1}}				% (opcjonalnie) trzeci autor
\def\thirdauthorno#1		{\gdef\@thirdauthorno{#1}}				% (opcjonalnie) nr albumu trzeciego autora
\def\thesistopic#1			{\gdef\@thesistopic{#1}}				% temat pracy
\def\supervisor#1			{\gdef\@supervisor{#1}}					% promotor (WAŻNE: w dopełniaczu)
\def\fieldofstudy#1			{\gdef\@fieldofstudy{#1}}				% kierunek studiów
% \date's default
\def\place#1				{\gdef\@place{#1}}						% miejscowość

% Layout
\newcommand{\frontpage}{
	\clearpage 
	\thispagestyle{empty} 
	
%	\begin{center}\includegraphics[scale=0.6]{ug-logo-horizontal}\end{center}
	
	\begin{center}
		UNIWERSYTET GDAŃSKI \\
		WYDZIAŁ MATEMATYKI, FIZYKI I INFORMATYKI
	\end{center}
	
	\vspace{20mm}
	
	\ifthenelse{\boolean{oneauthor}}{%
		\begin{large}
			\begin{center}
				\textbf{\@author} \\
				kierunek: \@fieldofstudy \\
				nr albumu: \@authorno
			\end{center}
		\end{large}	
	}{}

	\ifthenelse{\boolean{twoauthors}}{%
		\begin{large}
			\begin{center}
				\textbf{\@author} \\
				kierunek: \@fieldofstudy \\
				nr albumu: \@authorno
			\end{center}	
			\begin{center}
				\textbf{\@secondauthor} \\
				kierunek: \@fieldofstudy \\
				nr albumu: \@secondauthorno
			\end{center}
		\end{large}
	}{}

	\ifthenelse{\boolean{threeauthors}}{%
		\begin{large}
			\begin{center}
				\textbf{\@author} \\
				kierunek: \@fieldofstudy \\
				nr albumu: \@authorno
			\end{center}
			\begin{center}
				\textbf{\@secondauthor} \\
				kierunek: \@fieldofstudy \\
				nr albumu: \@secondauthorno
			\end{center}
			\begin{center}
				\textbf{\@thirdauthor} \\
				kierunek: \@fieldofstudy \\
				nr albumu: \@thirdauthorno
			\end{center}
		\end{large}
	}{}
	
	\vspace*{\fill}
	
	\begin{huge}
		\begin{center}
			\textbf{\@thesistopic}
		\end{center}
	\end{huge}
	
	\vspace*{\fill}
		
	\ifthenelse{\boolean{bachelorthesis}}{%
		\begin{flushright} 
			\large(Praca licencjacka \\ napisana pod kierunkiem \\ \@supervisor)
		\end{flushright}
	}{}
	\ifthenelse{\boolean{masterthesis}}{%
		\begin{flushright} 
			\large{Praca magisterska \\ napisana pod kierunkiem \\ \@supervisor}
		\end{flushright}
	}{}
	
	\vspace{20mm}
	
	\begin{center}
		\@place, \@date
	\end{center}
	
	\newpage
}



% -------------------------------------------------------------------------------------------------------
% Originality statement
% -------------------------------------------------------------------------------------------------------
% Custom hangers
%% List of prefixes used. Prefixes for "statementcontent" are used in the order of listed categories 
%% category				prefixes		 
%% destination			do, io, u		respectively: dean's office, institute office, universal
%% author(-s) number 	oa, ma			respectively: one author, multiple authors	
\def\uoastatementcontent{\par Oświadczam, że przedłożona praca dyplomowa została przygotowana przeze mnie samodzielnie, nie narusza praw autorskich, interesów prawnych i materialnych innych osób oraz wykorzystanie materiałów wytworzonych przez generatywne narzędzia sztucznej inteligencji odbyło się w zakresie uzgodnionym z promotorem.}

\def\domastatementcontent{\par Ja, niżej podpisana/-y, oświadczam, że przedłożona praca dyplomowa (będąca rezultatem pracy zespołu studentów) została przygotowana przeze mnie – w części, za którą odpowiadam – samodzielnie, nie narusza praw autorskich, interesów prawnych i materialnych innych osób.}

\def\iomastatementcontent{\par My, niżej podpisani, oświadczamy, że przedłożona praca dyplomowa (będąca rezultatem pracy zespołu studentów) została przygotowana przez nas – w częściach, za którą każdy z nas odpowiada – samodzielnie, nie narusza praw autorskich, interesów prawnych i materialnych innych osób.}

% Layout
\newcommand{\originalitystatement}{%
	\newpage
	\clearpage 
	\thispagestyle{empty} 
	\begin{flushright}
Załącznik nr 1 do zarządzenia Rektora UG nr 70/R/15 ze zm.\end{flushright}
\vspace{15mm}
	\begin{center}
		\textbf{Oświadczenie}
	\end{center}
	\ifthenelse{\boolean{oneauthor}}{%
		\uoastatementcontent
	}{}
	\ifthenelse{\boolean{twoauthors} \AND \boolean{instituteoffice}}{%
		\iomastatementcontent
	}{}
	\ifthenelse{\boolean{threeauthors} \AND \boolean{instituteoffice}}{%
		\iomastatementcontent
	}{}
	\ifthenelse{\boolean{twoauthors} \AND \boolean{deansoffice}}{%
		\domastatementcontent
	}{}
	\ifthenelse{\boolean{threeauthors} \AND \boolean{deansoffice}}{%
		\domastatementcontent
	}{}
	
	\vspace{15mm}
	
	\begin{minipage}{.45\textwidth}
		\begin{center}
			\dots\dots\dots\dots\dots\dots\dots\dots\\%
			data
		\end{center}
	\end{minipage}%
	\begin{minipage}{.45\textwidth}
		\begin{center}
			\dots\dots\dots\dots\dots\dots\dots\dots\\%
			podpis
		\end{center}
	\end{minipage}
	\newpage
}



% -------------------------------------------------------------------------------------------------------
% Sharing permission
% -------------------------------------------------------------------------------------------------------
% Custom hangers
\def\oapermissioncontent{\par Wyrażam zgodę / nie wyrażam zgody* na udostępnienie osobom zainteresowanym mojej pracy dyplomowej dla celów naukowo-badawczych. \par Zgoda na udostępnienie pracy dyplomowej nie oznacza wyrażenia zgody na kopiowanie pracy dyplomowej w całości lub w części. \vspace{\baselineskip} \newline \noindent \small{\textit{* niepotrzebne skreślić}}}

\def\mapermissioncontent{\par Wyrażamy zgodę/nie wyrażamy zgody* na udostępnienie osobom zainteresowanym naszej pracy dyplomowej dla celów naukowo-badawczych. \vspace{\baselineskip} \par Zgoda na udostępnienie pracy dyplomowej nie oznacza wyrażenia zgody na kopiowanie pracy dyplomowej w całości lub w części. \vspace{\baselineskip} \newline \noindent \small{\textit{* niepotrzebne skreślić}}}

% Layout
\newcommand{\sharingpermission}{%
	\newpage
	\clearpage 
	\thispagestyle{empty} 
	\begin{flushright}
Załącznik nr 3 do zarządzenia Rektora UG nr 70/R/15\end{flushright}
\vspace{15mm}
	\begin{center}
		\textbf{Oświadczenie}
	\end{center}
	\ifthenelse{\boolean{oneauthor}}{%
		\oapermissioncontent
	}{}
	\ifthenelse{\boolean{twoauthors} \OR \boolean{threeauthors}}{%
		\mapermissioncontent
	}{}
	
	\vspace{15mm}
	
	\begin{minipage}{.45\textwidth}
		\begin{center}
			\dots\dots\dots\dots\dots\dots\dots\dots\\%
			data
		\end{center}
	\end{minipage}%
	\begin{minipage}{.45\textwidth}
		\begin{center}
			\dots\dots\dots\dots\dots\dots\dots\dots\\%
			podpis
		\end{center}
	\end{minipage}
	\newpage
}



% -------------------------------------------------------------------------------------------------------
% Acknowledgements page
% -------------------------------------------------------------------------------------------------------
% Custom hangers
\def\acknowledgementscontent#1	{\gdef\@acknowledgementscontent{#1}}	% treść podziękowań

% Layout
\newcommand{\acknowledgements}{%
	\newpage
	\clearpage 
	\thispagestyle{empty} 
	
	\vspace*{\fill}
	
	\begin{flushright}
		\textit{\@acknowledgementscontent}
	\end{flushright}
	\newpage
}



% -------------------------------------------------------------------------------------------------------
% Abstract and keywords page
% -------------------------------------------------------------------------------------------------------
% Custom hangers
% \abstract's default	
\def\abstractcontent#1			{\gdef\@abstractcontent{#1}}			% treść abstraktu
\def\keywords#1					{\gdef\@keywords{#1}}					% słowa kluczowe

% Layout
\newcommand{\abstractandkeywords}{%
	\newpage
	\clearpage 
	\thispagestyle{empty} 

	\begin{center}
		\textbf{Streszczenie}
	\end{center}
	\par \@abstractcontent
	
	\vspace{15mm}
	
	\noindent \textbf{\textit{Słowa kluczowe ---}} \@keywords
	\newpage
}


\usepackage[english,polish]{babel}
\selectlanguage{polish}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
%\usepackage{amsmath}
%\usepackage{algorithm}
%\usepackage[noend]{algpseudocode}
%\usepackage[ruled,vlined]{algorithm2e}
%%\renewcommand{\algorithmcfname}{Algorytm}%
%\SetKwInOut{Input}{Wejście}
%\SetKwInOut{Output}{Wyjście}
\usepackage[indent=20pt]{parskip}
\renewcommand{\baselinestretch}{1.1} 
\usepackage{xcolor}
\usepackage{color}
\usepackage{listings}
\usepackage{pgfplots} 
\pgfplotsset{width=12cm,compat=1.9} 
\usepackage{hyperref}



\lstdefinestyle{customc}{
	belowcaptionskip=1\baselineskip,
	breaklines=true,
	frame=L,
	xleftmargin=\parindent,
	language=C++,
	showstringspaces=false,
	basicstyle=\footnotesize\ttfamily,
	keywordstyle=\bfseries\color{black},
	commentstyle=\itshape\color{purple},
	identifierstyle=\color{blue},
	stringstyle=\color{orange},
}

\lstdefinestyle{customasm}{
	belowcaptionskip=1\baselineskip,
	frame=L,
	xleftmargin=\parindent,
	language=[x86masm]Assembler,
	basicstyle=\footnotesize\ttfamily,
	commentstyle=\itshape\color{purple!40!black},
}

\lstset{style=customc}
\lstset{
	literate={ą}{{\k a}}1
	{Ą}{{\k A}}1
	{ż}{{\. z}}1
	{Ż}{{\. Z}}1
	{ź}{{\' z}}1
	{Ź}{{\' Z}}1
	{ć}{{\' c}}1
	{Ć}{{\' C}}1
	{ę}{{\k e}}1
	{Ę}{{\k E}}1
	{ó}{{\' o}}1
	{Ó}{{\' O}}1
	{ń}{{\' n}}1
	{Ń}{{\' N}}1
	{ś}{{\' s}}1
	{Ś}{{\' S}}1
	{ł}{{\l}}1
	{Ł}{{\L}}1
}
% Ustawienie formatu pseudokodu
\lstset
{ %Formatting for code in appendix
    language=C,
    basicstyle=\footnotesize,
    numbers=left,
    stepnumber=1,
    showstringspaces=false,
    tabsize=1,
    breaklines=true,
    breakatwhitespace=false,
}
\newcommand{\mycomment}[1]{}
