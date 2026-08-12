date = $(shell date +%Y-%m-%d)

INSPIRE_REFRESH ?= 0
export INSPIRE_REFRESH

all: yaml nupaqis main clean

refresh:
	$(MAKE) INSPIRE_REFRESH=1 all

nupaqis: make_nupaqis.py
	python3 make_nupaqis.py

clean:
	rm -f INTRODUCTION.tex BYNUPA.tex BYQIS.tex
	rm -f *.aux *.bak *.bbl *.blg *.dvi *.idx *.lof *.log *.lot *.toc \
		*.glg *.gls *.glo *.xdy *.nav *.out *.snm *.vrb *.mp \
		*.synctex.gz *.run.xml *.bcf *.brf *.fls *.fdb_latexmk

realclean: clean
	rm -f *.ps *.pdf

yaml: sort_yaml.py NUPAQIS.yaml
	cp NUPAQIS.yaml NUPAQIS_copy.yaml
	python3 sort_yaml.py
	mv NUPAQIS_copy.yaml NUPAQIS.yaml

main:
	latexmk -bibtex -logfilewarnings -f -interaction=nonstopmode NUPAQIS
	mkdir -p DRAFTS
	rsync NUPAQIS.pdf DRAFTS/draft_$(date).pdf

final:
	if [ -f *.aux ]; \
		then make clean; \
	fi
	make document