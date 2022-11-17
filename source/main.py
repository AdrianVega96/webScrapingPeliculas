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

# Get anual catalog URLs - Filtrar los enlaces
print("Getting PDF URLs")
pdflinks = navigation.pdfURLs(url, webPDFs)

# Getting PDFs
print("Getting PDFs and cleaning")
dataFramePDFs = pd.DataFrame() # Dataframe que se guarda en el fichero films.csv (sin limpiar)
for year, ulrss in pdflinks:
  print(ulrss)
  dataFramePDFs = pd.concat([dataFramePDFs, pdf.getPDF(url+ulrss, year)], ignore_index=True)

##########################################  Scrappear Wikipedia  ################################################
wikiMovieList = navigation.WikiList()

print('Getting box info from each film from wikipedia')
wikipediaInfo = navigation.getInfoFromWikiMoviList(wikiMovieList)

merged_dataframe = format.catalog_and_wikipedia_merge(dataFramePDFs, wikipediaInfo)

merged_dataframe['es_catalog'] = 0

merged_dataframe.loc[(merged_dataframe['spa_title'].isna())
                     & (merged_dataframe['eng_title'].isna()), 'es_catalog'] = 1

merged_dataframe.to_csv('dataset/Filmografia_occidental_entre_2009-2015_Titulos_y_ficha_tecnica.csv')

