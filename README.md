# webScrapingPeliculas

---
- title: webScrapingPeliculas
- author/s: Agustin Rovira Quezada y Adrian Vega Morales
- date: 2022-11-17
---

## Estructura

El proyecto se estrutura en los siguientes directorios:

- Dataset
- Source

Dentro de dataset encontramos el dataset en formato .csv extraido y previo a la limpieza del mismo. En source, por otro lado, encontramos la estructura del código.

Dentro de source tenemos el fichero *main.py* que es la el script que realiza el scraping, es decir, es el fichero que debe ejecutarse, y dentro del directorio functions tenemos los ficheros *navigation.py*, *format.py* y *pdf_treatment.py* que contienen las funciones necesarias para la ejecución del código.

- *navigation.py*. Contiene las funciones necesarias para navegar y extraer el contenido de las distintas webs.
- *format.py*. Contiene las funciones que utilizamos para dar formato a los dataframes y hacer una primera limpieza de los dataframes y las líneas extraidas de los pdfs.
- *pdf_treatment.py*. Incluye las funciones necesarias para extraer y leer los PDFs que encontramos en las webs a las que hacemos el scarping.

Además, en el directorio principal se encuentra el fichero **requirements.txt** que incluye las librerías necesarias para le ejecución del código.

---

DOI de Zenodo del dataset: