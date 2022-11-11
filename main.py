import pandas as pd
import re

import functions.pdf_treatment as pdf
import functions.format as format
import functions.navigation as navigation

url = "https://www.culturaydeporte.gob.es"

print('Start navigating')
#Parce the URL: "https://www.culturaydeporte.gob.es" to start to jump. Starting web from gobernment
webStart = navigation.parseHTML2Soup(url)

# Get films section URL
cineURL = navigation.findLink(webStart, keystring = "/cine/inicio")

# Get films catalog URL
webCine = navigation.parseHTML2Soup(url+cineURL[0])
catalogoURL = navigation.findLink(webCine, keystring = "catalogodecine")

if re.match('^(http|https)://', catalogoURL[0]) is None:
  webCatalogo = navigation.parseHTML2Soup(url+catalogoURL[0])
else:
  webCatalogo = navigation.parseHTML2Soup(catalogoURL[0])
pdfsURL = navigation.findLink(webCatalogo, keystring="descargas-catalogo")

# Get catalog downloads section URL
webPDFs = navigation.parseHTML2Soup(url+pdfsURL[0])

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
wikiMovieList=navigation.WikiList()
wikiMovieList.to_csv('WikiMovieList.csv')

merged_dataframe = format.catalog_and_wikipedia_merge(dataFramePDFs, wikiMovieList)

None
##################################################  Experiment ##########################################
#trend={}
#for index, row in DataFramePDFs.iterrows():
    #print(row["spa_title"])
    #trend[index]=popularity(row["spa_title"])
#
    #if index==100:
#break
