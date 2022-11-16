import pandas as pd
from bs4 import BeautifulSoup
import requests
import datetime
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from pytrends.request import TrendReq
import ssl
import source.functions.format as format

def findPDF(SoupInst, keystring=None):
    """
        This function Find all links from a soup taking into account the tag text

        inputs:
            SoupInst --> bs4.element.  Each element is a line of a page
            keystring --> String.  Key word to search. If you provide keystring, filter the result

        outputs:
            tmp --> List with the links
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
        This function Find all links from a soup taking into account the tag text.
        Similar to the previous function however

        inputs:
            SoupInst --> bs4.element.  Each element is a line of a page
            keystring --> String.  Key word to search. If you provide keystring, filter the result

        outputs:
            tmp --> List with the links
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
    """
        This function store the html  source code of the URL data into a variable

        inputs:
            url --> string.  URL We want to scrap


        outputs:
            html --> HTML data from the the URL provided
    """
    try:
        html = urlopen(url)
    except HTTPError as e:
        print(e)
    except URLError as e:
        print('The server could not be found!')

    return html

# -------------------------------------------------------------------------------------

def pdfURLs(url, webPDFs):
    """
        This function store the html  source code of the URL data into a variable and process the information to
        give back the PDFs url to later process

        inputs:
            url --> string.  original url to scrap
            webPDFs --> bs4.element. Element contains the soup of the pages where all PDF are

        outputs:
            final --> list. List of list that contains the year and the url
    """
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
    """
            This function store the html  source code and convert it into a soup

            inputs:
                url --> string.  original url to scrap


            outputs:
                bs --> bs4.element
    """
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
    """
        This a function test to see if we were able to use the google trend API to complete the final
        dataset. currently out of scope

                inputs:
                    kw --> string.  key word to search


                outputs:
                    data --> Dataframe with the information of google trends
    """

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
    """
          From the url reference of Wikipedia it gets the information realated to the infobox
          https://en.wikipedia.org/wiki/Help:Infobox

                   inputs:
                       url --> string.  Reference URL


                   outputs:
                       ToClean --> Dictionary to with the information to clean
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    tbl = soup.find("table", {"class": "infobox vevent"})
    if tbl is not None:
        list_of_table_rows = tbl.findAll('tr')
        ToClean = {}
        for i, tr in enumerate(list_of_table_rows):

                th = tr.find("th")
                td = tr.find("td")

                if (th is None) or (td is None):
                    ToClean[f"Element{i}"] = ""
                else:
                    ToClean[th.text] = td.text
    else:
        return None
    return ToClean

# -------------------------------------------------------------------------------------

def WikiList():
    """
         From the url reference of Wikipedia it gets the information about the movies between 2009 and 2015
         from spain, EEUU, France, Italy, Mexico, Argentina.

         inputs:
            url --> None


         outputs:
            WikiMovieList --> Return a dataframe with the information about the movie, year and URL
    """
    year=list(range(2009,2016))
    OrigURL="https://en.wikipedia.org/wiki/"

    def wikiMovies(URL,year):
        """
                 From the url reference of Wikipedia, URL that point to a year and country, get all the movies
                 from that time and place

                 inputs:
                    url --> string
                    year--> int


                 outputs:
                    df --> Return a dataframe with the information about the movie, year and URL
        """
        ssl._create_default_https_context = ssl._create_unverified_context
        html = urlopen(URL)
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

def getInfoFromWikiMoviList(wikiMovieList):
    """
        Complete the information of the dataframe wikiMovieList witht the information of the information box
        from the url reference of each movie we scrapped in wikipedia

             inputs:
                wikiMovieList --> Dataframe. Movie,year, URL


             outputs:
                wikipediaInfo --> Dataframe. Infobox + movie + year+ url
   """
    wikiBaseURL = 'https://en.wikipedia.org/'
    wikipediaInfo = pd.DataFrame()
    for i, row in wikiMovieList.iterrows():
        if row['Link'] is not None:
            print(f"Index: {i} | Movie: {row['Movie']} | Year: {row['year']} | URL: {row['Link']}")
            wikiBox = getinfoBox(wikiBaseURL + row['Link'])
            if wikiBox is not None:
                Info = format.formatBoxInfo(wikiBox, row)
                wikipediaInfo = pd.concat([wikipediaInfo, Info], axis=0, ignore_index=True)
    return wikipediaInfo

