import pandas as pd
import re

import source.functions.pdf_treatment as pdf
import source.functions.format as format
import source.functions.navigation as navigation

url = "https://www.culturaydeporte.gob.es"

print('Start navigating')
#Parce the URL: "https://www.culturaydeporte.gob.es" to start to jump. Starting web from gobernment
webStart = navigation.parseHTML2Soup(url)

# Get films section URL
cineURL = navigation.findLink(webStart, keystring ="/cine/inicio")

# Get films catalog URL
webCine = navigation.parseHTML2Soup(url + cineURL[0])
catalogoURL = navigation.findLink(webCine, keystring ="catalogodecine")

if re.match('^(http|https)://', catalogoURL[0]) is None:
  webCatalogo = navigation.parseHTML2Soup(url + catalogoURL[0])
else:
  webCatalogo = navigation.parseHTML2Soup(catalogoURL[0])
pdfsURL = navigation.findLink(webCatalogo, keystring="descargas-catalogo")

# Get catalog downloads section URL
webPDFs = navigation.parseHTML2Soup(url + pdfsURL[0])

# Get anual catalog URLs - Filtrar los enlaces - no hay 2014/2015/2016
print("Getting PDF URLs")
pdflinks = navigation.pdfURLs(url, webPDFs)

# Getting PDFs
print("Getting PDFs and cleaning")
dataFramePDFs = pd.DataFrame() # Dataframe que se guarda en el fichero films.csv (sin limpiar)
for year, ulrss in pdflinks:
  print(ulrss)
  dataFramePDFs = pd.concat([dataFramePDFs, pdf.getPDF(url+ulrss, year)], ignore_index=True)

dataFramePDFs.to_csv('films.csv')

##########################################  Scrappear Wikipedia  ################################################
wikiMovieList= navigation.WikiList()
wikiMovieList.to_csv('WikiMovieList.csv')

merged_dataframe = format.catalog_and_wikipedia_merge(dataFramePDFs, wikiMovieList)

print('Getting box info from each film')
a = 0
wikiBaseURL = 'https://en.wikipedia.org/'
wikipediaInfo = pd.DataFrame()
for i, row in merged_dataframe.iterrows():
    if row['wiki_url'] != "":
        a = a + 1
        print(f"Index {a} | Película: {row['spa_title']} | URL: {row['wiki_url']}")
        wikiBox = navigation.getinfoBox(wikiBaseURL + row['wiki_url'])
        Info = {k: format.cleanBox(v) for k, v in wikiBox.items() if v}
        Info = pd.DataFrame(Info.items()).transpose()
        new_header = Info.iloc[0]  # grab the first row for the header
        Info = Info[1:]  # take the data less the header row
        Info.columns = new_header  # set the header row as the df header
        Info['year'] = row['year']
        Info['spa_title'] = row['spa_title']
        Info['eng_title'] = row['eng_title']
        wikipediaInfo = pd.concat([wikipediaInfo, Info], axis=0, ignore_index=True)

finalDataframe = pd.merge(merged_dataframe, wikipediaInfo, on=['spa_title', 'eng_title', 'year'], how='left')

None

##################################################  Experiment ##########################################
#trend={}
#for index, row in DataFramePDFs.iterrows():
    #print(row["spa_title"])
    #trend[index]=popularity(row["spa_title"])
#
    #if index==100:
#break

#Prueba