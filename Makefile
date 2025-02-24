date = $(shell date +%Y-%m-%d)

all: nupaqis main clean

nupaqis: make_nupaqis.py
	python3 make_nupaqis.py

clean:
	rm -f INTRODUCTION.tex BYNUPA.tex BYQIS.tex
	rm -f *.aux *.bak *.bbl *.blg *.dvi *.idx *.lof *.log *.lot *.toc \
		*.glg *.gls *.glo *.xdy *.nav *.out *.snm *.vrb *.mp \
		*.synctex.gz *.run.xml *.bcf *.brf *.fls *.fdb_latexmk

realclean: clean
	rm -f *.ps *.pdf

main:
	latexmk -lualatex -logfilewarnings -halt-on-error NUPAQIS
	mkdir -p DRAFTS
	rsync NUPAQIS.pdf DRAFTS/draft_$(date).pdf

final:
	if [ -f *.aux ]; \
		then make clean; \
	fi
	make document