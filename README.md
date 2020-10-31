# covid-19-ita_daily-report

## description:
### This project consists in a simple [script](covid_19.py) usable to generate plots and a [log file](covid_19.log).

## usage:
Simply type:
`python covid_19.py`

## documentation:
The  [documetation](covid_19_doc.pdf) was generated initially in html using [**pdoc**](https://pdoc3.github.io/pdoc/)
and later converted to pdf using [**pdfkit**](https://pypi.org/project/pdfkit/).
For others python documentation tools see [DocumentationTools](https://wiki.python.org/moin/DocumentationTools)

## notes:
The [data source](https://github.com/pcm-dpc/COVID-19/blob/master/dati-json/dpc-covid19-ita-andamento-nazionale.json) 
is updated daily, therefore each row of the [log file](covid_19.log) represents a single day

See the [Pictures](Pictures) folder to see the generated plots

## python version:
This python [version](.python-version) was used

## dependencies:
Required dependencies are listed [here](requirements.txt)
