import re
import pandas as pd

def cleanPages(page, numpage, startPage):
    """
        This function clean each page of the selected PDF and extract the information about the films
        inputs:
            page --> list of strings.  Each element is a line of a page
            numpage --> Int.  To know the exact page of the whole pdf document
            startPage --> Int.  To know from where to start the extraction

        outputs:
            newlist --> List of tuplas. Each tuple has the following
                        elements(titulo español, titulo ingles,..,n erros)

    """

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

    ################################## Correcciones futuras ##########################################
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
    #####################################################################################################

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

def catalog_and_wikipedia_merge(gob_catalog_dataframe, wiki_dataframe):
    """
               This function clean each page of the selected PDF and extract the information about the films
               inputs:
                   gob_catalog_dataframe --> DataFrame. Contains the processed info from PDFs of goverment spa_title,eng_title,year
                   wiki_dataframe --> DataFrame. Dataframe with the movies of wikipedia from a 2009 to 2015

               films_with_wiki_url:
                   films_with_wiki_url --> DataFrame. Merged result from both dataset.

        """
    wiki_dataframe['Movie'] = wiki_dataframe['Movie'].str.strip()#Remove empty space
    gob_catalog_dataframe['spa_title'] = gob_catalog_dataframe['spa_title'].str.strip()#Remove empty space
    gob_catalog_dataframe['eng_title'] = gob_catalog_dataframe['eng_title'].str.strip()#Remove empty space
    wiki_dataframe.rename(columns={'Movie': 'spa_title'}, inplace=True)
    films_with_wiki_url = pd.merge(gob_catalog_dataframe, wiki_dataframe, on=['spa_title', 'year'], how='left')
    wiki_dataframe.rename(columns={'spa_title': 'eng_title'}, inplace=True)
    films_with_wiki_url = pd.merge(films_with_wiki_url, wiki_dataframe, on=['eng_title', 'year'], how='left')
    return films_with_wiki_url

def cleanBox(v):

    """
           This function clean each page of the selected PDF and extract the information about the films
           inputs:
               page --> list of strings.  Each element is a line of a page
               numpage --> Int.  To know the exact page of the whole pdf document
               startPage --> Int.  To know from where to start the extraction

           outputs:
               newlist --> List of tuplas. Each tuple has the following
                           elements(titulo español, titulo ingles,..,n erros)

    """
    clean = re.sub("[\(\[].*?[\)\]]", "", v)
    clean = re.sub("million", "M", clean)
    clean = re.sub("^\s+|\s+$", "",clean)
    clean = list(filter(None,clean.splitlines()))
    return clean

def formatBoxInfo(wikiBox, row):
    """
           This function gives the right format to the infobox class of the Wikipedia websites
           https://en.wikipedia.org/wiki/Help:Infobox

           inputs:
               wikiBox --> Dictionary.  Contains raw information of the box
               row --> DataFrame. Contains the processed info of the pfs. Movie name and year of realese

           outputs:
               Info --> Dataframe. Merge in one row the movie, year of realese and the formated box information
    """

    Info = {k: cleanBox(v) for k, v in wikiBox.items() if v}
    Info = pd.DataFrame(Info.items()).transpose()
    new_header = Info.iloc[0]  # grab the first row for the header
    Info = Info[1:]  # take the data less the header row
    Info.columns = new_header  # set the header row as the df header
    Info['Movie'] = row['Movie']
    Info['year'] = row['year']
    return Info