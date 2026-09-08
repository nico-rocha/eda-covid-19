<!-- README.md do projeto de dados python covid!

Para rodar o projeto:

Estou usando o Ubuntu 24.04.4 LTS e utilizei o mise para baixar diretamente no projeto o Python e sua versão, utilizei o Python 3.12.14

- Instalar o Mise:
curl https://mise.run | sh

- Ativar o Mise:
echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
source ~/.bashrc

- Instalar o Python via Mise:
cd ~/projects/python_projects/eda
mise use python@3.12

- Apontar o VScode para o python do mise:
  mise which python

- Instalar as bibliotecas do projeto:
pip install pandas matplotlib numpy

- Baixar o dataset (fonte que estou usando como referência -> OWID COVID-19 - https://github.com/owid/covid-19-data):
curl -sL -o owid-covid-data.csv https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv

- Rodar o script:
python eda_covid_brasil.py

- Saída esperada: impressão no terminal das correlações e respostas das perguntas orientadas por dados e a geração de 4 arquivos de gráficos das análises na mesma pasta.

--- Problemas e soluções ---
No module named pip -> VSCode usando /usr/bin/python3 (Python do sistema) em vez do Python do mise	

Failed to fetch available Python versions ao escolher "Global"	-> o VSCode não escaneia o diretório de instalações do mise, usar "Enter Interpreter Path..." em vez de "Global"

FileNotFoundError: owid-covid-data.csv -> Dataset não baixado na pasta do projeto, baixe o dataset -->