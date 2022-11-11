import pandas as pd

import functions.pdf_treatment as pdf
import functions.format as format
import functions.navigation as navigation

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

url = "https://www.culturaydeporte.gob.es"

print('Start navigating')
#Parce the URL: "https://www.culturaydeporte.gob.es" to start to jump. Starting web from gobernment
webStart = navigation.parseHTML2Soup(url)

# Get films section URL
cineURL = navigation.findLink(webStart, keystring = "/cine/inicio")

# Get films catalog URL
webCine = navigation.parseHTML2Soup(url+cineURL[0])
catalogoURL = navigation.findLink(webCine, keystring = "catalogodecine")

webCatalogo = navigation.parseHTML2Soup(url+catalogoURL[0])
pdfsURL = navigation.findLink(webCatalogo, keystring="descargas-catalogo")

# Get catalog downloads section URL
webPDFs = navigation.parseHTML2Soup(url+pdfsURL[0])

# Get anual catalog URLs - Filtrar los enlaces - no hay 2014/2015/2016
print("Getting PDF URLs")
pdflinks = navigation.pdfURLs(url, webPDFs)

# Getting PDFs
print("Getting PDFs and cleaning")
DataFramePDFs = pd.DataFrame() # Dataframe que se guarda en el fichero films.csv (sin limpiar)
for year, ulrss in pdflinks:
  print(ulrss)
  DataFramePDFs = pd.concat([DataFramePDFs, pdf.getPDF(url+ulrss, year)], ignore_index=True)

DataFramePDFs.to_csv('films.csv')

##########################################  Scrappear Wikipedia  ################################################
WikiMovieList=navigation.WikiList()
WikiMovieList.to_csv('WikiMovieList.csv')


##################################################  Experiment ##########################################
#trend={}
#for index, row in DataFramePDFs.iterrows():
    #print(row["spa_title"])
    #trend[index]=popularity(row["spa_title"])
#
    #if index==100:
#break
