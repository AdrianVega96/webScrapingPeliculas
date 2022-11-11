import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import datetime
import time
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
import io
import PyPDF2
import ssl
import re
import itertools
from pytrends.request import TrendReq

def findPDF(SoupInst, keystring=None):
    """
       Find all links from a soup taking into account the tag text.
       If you provide keystring, filter the result
       """
    tmp = None
    # find links. Filter all tag a and find the href inside
    for link in SoupInst.find_all('a', href=True):
        if keystring in link.get_text(strip=True):
            print("Found the URL:", link['href'])
            tmp = link['href']
        else:
            continue

    return tmp


def findLink(SoupInst, keystring=None):
    """
    Find all links from a soup. If you provide keystring, filter the result
    """
    # find links. Filter all tag a and find the href inside
    links = set([link['href'] for link in SoupInst.find_all('a', href=True)])
    tmp = []

    if keystring != None:
        # find if the links any match the keystring
        for link in links:
            if keystring in link:
                tmp.append(link)

        if not tmp:
            print("no encontrado")
            tmp = links

    else:
        tmp = links

    return tmp


# -------------------------------------------------------------------------------------

def parseHTML(url):
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print('The server could not be found!')

    return html


# -------------------------------------------------------------------------------------

def parseHTML2Soup(url):
    ssl._create_default_https_context = ssl._create_unverified_context
    try:
        html = urlopen(url)
        bs = BeautifulSoup(html.read(), 'html.parser')
    except HTTPError as e:
        print(e)
    except URLError as e:
        print('The server could not be found!')

    return bs


# -------------------------------------------------------------------------------------

def cleanPages(page, numpage, startPage):

    #Eliminar primeras lineas
    page = page[2:-2]

    #Limpiar lineas especificas con patrones repetidos
    newlist = list(map(lambda x: re.sub("© Ministerio de Educación, Cultura y Deporte", "", x), page))
    newlist = list(map(lambda x: re.sub("\([^)]*\)", "", x), newlist))

    removeFrom = [True for i in range(len(newlist))]
    for i, item in enumerate(newlist):
        if not i == len(newlist) - 1:
            if (re.search("Dir:", item) or re.search("Dir.:", item)):
                if len(newlist[i+1]) != 0:
                    removeFrom[i+1] = False

    newlist = [l for l,b in zip(newlist,removeFrom) if b]
    newlist = list(map(lambda x: re.sub("Dir:.*$", "", x), newlist))
    newlist = list(map(lambda x: re.sub("Dir.:.*$", "", x), newlist))
    #newlist = list(map(lambda x: re.sub("(España/.*$", "", x), newlist))

    controlpoint = 0


    #Correcciones
    #Si la linea empieza por 'Documentary) Dir: Ramón Tort Musical  ' borrala
    #Si la linea empieza por Dir borrala
    #Borrar (Documental / '
    #Borrar '/ Documentary  '  'Documentary  '
    #'Documentary) '
    #'Último capítulo, adiós Nicaragua / Last Chapter. Goodbye (Documental /  '
    #'• A ritmo de Jess / The Rhythm of Jess  Dir.: Naxo Fiol  Documental / '
    #Fiction / Comedia / Comedy / Romance
    #'Unidos/USA 25%) '
    #'• American Jesus  / American Jesus  (España/Spain 75% -  Estados '


    # Limpiar lineas especificas con patrones repetidos
    newlist = list(map(lambda x: re.sub("^\s+|\s+$", "", x), newlist))
    # Limpiar el contenido en parentesis
    newlist = list(map(lambda x: re.sub("\([^)]*\)", "", x), newlist))
    # Limpiar todos los caracteres especiaales "-" al inicio
    newlist = list(map(lambda x: re.sub("^-", "", x), newlist))
    #Delete bulletPoints
    newlist = list(map(lambda x: re.sub("^•", "", x), newlist))


    # separar por el carcater /, si no esta vacio (recordar que hay lineas vacias)
    newlist = [tuple(re.split('/', e)) for e in newlist if e]

    return newlist  # List de tuplas (titulo español, titulo ingles, eroor [n])


# -------------------------------------------------------------------------------------

### ARREGLAR ESTA FUNCIÓN PARA QUE FUNCIONE BIEN, TAMBIÉN ARREGLAR CLEAN PDF
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
             CleanPDf.append(cleanPages(PageString.splitlines(), page, 1))  # Lista de listas


    # Convierto a dataframe
    ListofPages = list(itertools.chain(*CleanPDf))  # Flat list form list of list --> list of tuplas
    # convertir a dataframe y filtrar las 2 primeras columnas que son los titulos en español e ingles
    df = pd.DataFrame(ListofPages)
    df.drop(df.columns[2:], axis=1, inplace=True)
    df.rename(columns={0: 'spa_title', 1: 'eng_title'}, inplace=True)
    df['year'] = year

    return df


# -------------------------------------------------------------------------------------

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


# -------------------------------------------------------------------------------------
def pdfURLs(webPDFs):
    currentDateTime = datetime.datetime.now()
    date = currentDateTime.date()
    final = []

    for i in range(2009, date.year):
        catalogoAnualURL = findLink(webPDFs, keystring=f"descargas-catalogo/{i}")
        if catalogoAnualURL != 'no encontrado':
            webCatalogoAnual = parseHTML2Soup(url + catalogoAnualURL[0])

            # Get PDF URLs
            anualPDFsURL = findPDF(webCatalogoAnual, keystring="Índice alfabético de largometrajes")
            # Completar aqui linea de codigo
            if anualPDFsURL != None:
                final.append([i, anualPDFsURL])
    return final

# -------------------------------------------------------------------------------------

def popularity(kw):
    # Establish Pytrends connection
    Pytrend = TrendReq(retries=2, backoff_factor=0.1, requests_args={'verify':False})

    Keywords = [kw]
    Date_interval = 'today 12-m'

    Pytrend.build_payload(Keywords, cat=34, timeframe=Date_interval, geo='ES', gprop='')
    data = Pytrend.interest_by_region(resolution='REGION', inc_low_vol=True, inc_geo_code=True)
    data = data[data.iloc[:, 2] > 0]
    data.columns = ['Region', 'Code', 'MovieValue']
    data.to_dict('series')

    return data


# -------------------------------------------------------------------------------------

def getinfoBox(URL):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    tbl = soup.find("table", {"class": "infobox vevent"})

    list_of_table_rows = tbl.findAll('tr')
    ToClean = {}
    for i,tr in enumerate(list_of_table_rows):

            th = tr.find("th")
            td = tr.find("td")

            if (th is None) or (td is None):
                ToClean[f"Element{i}"] = ""
            else:
                ToClean[th.text] = td.text


    def cleanBox(v):
        clean=re.sub("[\(\[].*?[\)\]]", "", v)
        clean=re.sub("million", "M", clean)
        clean = re.sub("^\s+|\s+$", "",clean)
        clean=list(filter(None,clean.splitlines()))
        return  clean

    Info={k: cleanBox(v) for k, v in ToClean.items() if  v}
    return Info

# --------------------------------------------------------------------------------------------


def WikiList():
    year=list(range(2009,2016))
    OrigURL="https://en.wikipedia.org/wiki/"

    def wikiMovies(URL,year):
        ssl._create_default_https_context = ssl._create_unverified_context
        html = urlopen(URL)
        #bs = BeautifulSoup(html.read(), 'html.parser')
        #r = requests.get(URL)
        soup = BeautifulSoup(html.read(), "html.parser")
        tbl = soup.find_all("table", {"class":"wikitable sortable"})

        data=[]
        for n1,t in enumerate(tbl):
            movies=t.findAll('i')
            for n2,m in enumerate(movies):
                #print(n1,n2)
                title= m.text if m.text else None
                link= m.a['href'] if m.find("a",href=True) else None
                data.append((title,link,year))

        df = pd.DataFrame(data, columns =['Movie', 'Link', 'year'])
        return df

    c=[]
    for y in year:
        ref = [f"List_of_American_films_of_{y}",f"List_of_Spanish_films_of_{y}",f"List_of_French_films_of_{y}",f"List_of_Italian_films_of_{y}",f"List_of_Argentine_films_of_{y}"]

        for URL in [OrigURL+i for i in ref]:
            c.append(wikiMovies(URL,y))

    WikiMovieList=pd.concat(c, ignore_index=True)
    return WikiMovieList

### Main

url = "https://www.culturaydeporte.gob.es"

print('Start navigating')
#Parce the URL: "https://www.culturaydeporte.gob.es"  to start to jump. Starting web from gobernment
webStart = parseHTML2Soup(url)

# Get films section URL
cineURL = findLink(webStart, keystring = "/cine/inicio")

# Get films catalog URL
webCine = parseHTML2Soup(url+cineURL[0])
catalogoURL = findLink(webCine, keystring = "catalogodecine")

webCatalogo = parseHTML2Soup(url+catalogoURL[0])
pdfsURL = findLink(webCatalogo, keystring="descargas-catalogo")

# Get catalog downloads section URL
webPDFs = parseHTML2Soup(url+pdfsURL[0])

# Get anual catalog URLs - Filtrar los enlaces - no hay 2014/2015/2016
print("Getting PDF URLs")
pdflinks = pdfURLs(webPDFs)

# Getting PDFs
print("Getting PDFs and cleaning")
DataFramePDFs = pd.DataFrame() # Dataframe que se guarda en el fichero films.csv (sin limpiar)
for year, ulrss in pdflinks:
  print(ulrss)
  DataFramePDFs = pd.concat([DataFramePDFs, getPDF(url+ulrss, year)], ignore_index=True)

DataFramePDFs.to_csv('films.csv')

##########################################  Scrappear Wikipedia  ################################################
WikiMovieList=WikiList()
WikiMovieList.to_csv('WikiMovieList.csv')


##################################################  Experiment ##########################################
#trend={}
#for index, row in DataFramePDFs.iterrows():
    #print(row["spa_title"])
    #trend[index]=popularity(row["spa_title"])
#
    #if index==100:
#break
