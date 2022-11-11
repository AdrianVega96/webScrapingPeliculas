import time
import pandas as pd
import io
import PyPDF2
import ssl
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError

import functions.format as format

import itertools

def getPDF(url, year):
    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        response = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print('The server could not be found')

    df = getAllPages(response, year)

    return df

def getAllPages(response, year):
    # Variables y constantes
    CleanPDf = []  # Almaceno tuplas (titulocastellano, titulo ingles, errores[n])
    # Index show me the type of analisis I need to apply to my dpf. If index is 1 aply clean to indexPDFs and not Advance

    # select pages to extract information based on the bookmark
    with io.BytesIO(response.read()) as f:

        # read the PDF
        pdf = PyPDF2.PdfFileReader(f)
        for page in range(pdf.numPages):
             PageString = pdf.getPage(page).extractText()
             CleanPDf.append(format.cleanPages(PageString.splitlines(), page, 1))  # Lista de listas


    # Convierto a dataframe
    ListofPages = list(itertools.chain(*CleanPDf))  # Flat list form list of list --> list of tuplas
    # convertir a dataframe y filtrar las 2 primeras columnas que son los titulos en español e ingles
    df = pd.DataFrame(ListofPages)
    df.drop(df.columns[2:], axis=1, inplace=True)
    df.rename(columns={0: 'spa_title', 1: 'eng_title'}, inplace=True)
    df['year'] = year

    return df