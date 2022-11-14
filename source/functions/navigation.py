import pandas as pd
from bs4 import BeautifulSoup
import requests
import datetime
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from pytrends.request import TrendReq
import ssl
import re

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

# -------------------------------------------------------------------------------------

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

def pdfURLs(url, webPDFs):
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

def getinfoBox(url):
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
    return ToClean

# -------------------------------------------------------------------------------------

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


