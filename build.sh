rm -rf submission/
rm -rf submission.zip
mkdir -p submission/
mkdir -p submission/code/
cp GP/approach1.py submission/code/benchmark.py
cp GP/approach4.py submission/code/new_algo.py

cd report/
pdflatex report.tex -output-directory=report/
bibtex references.bib
pdflatex report.tex -output-directory=report/
pdflatex report.tex -output-directory=report/
cp report.pdf ../submission/
cd ../
pwd
zip -r submission.zip submission