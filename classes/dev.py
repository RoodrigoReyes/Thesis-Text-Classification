import os
import re
import string
import unicodedata
from collections import Counter

from pypdf import PdfReader
from stopwords import get_stopwords
from tqdm import tqdm


def extract_pdf_text(pdf_file_path):
    """
    Esta función lee un archivo PDF y extrae todo el texto contenido en él.

    Parámetros:
    pdf_file_path (str): Ruta al archivo PDF a procesar.

    Returns:
    str: El texto extraído del PDF.
    """

    # Definiendo el nombre del archivo
    file_name = os.path.basename(pdf_file_path)

    # Crear un lector de PDF
    reader = PdfReader(pdf_file_path, strict=False)

    # Calcular el número de páginas del PDF
    number_of_pages = len(reader.pages)

    # Inicializar una cadena vacía para almacenar todo el texto del PDF
    pdf_text = ""

    # Iterar sobre cada página del PDF
    for number_page in tqdm(range(number_of_pages), ncols=100, desc=file_name):
        # Extraer la página actual
        page = reader.pages[number_page]

        # Extraer el texto de la página actual
        text = page.extract_text()

        # Añadir el texto de la página al texto total del PDF
        pdf_text += text + " "

    return pdf_text


def clean_text(input_str):
    """
    Esta función recibe un texto, elimina los acentos, caracteres especiales y palabras vacías en inglés y español,
    y devuelve el texto limpio. También se eliminan palabras que son números o tienen longitud inferior a 2.

    Parámetros:
    input_str (str): El texto de entrada a procesar.

    Returns:
    str: El texto de entrada procesado.
    """
    # Obtener las palabras vacías (o stopwords) para inglés y español
    english_stopwords = get_stopwords("en")
    spanish_stopwords = get_stopwords("es")

    # Combinar las listas de palabras vacías en una sola lista
    list_stopwords = english_stopwords + spanish_stopwords

    # Crear una cadena de caracteres con todos los signos de puntuación que necesitamos eliminar
    chars = re.escape(string.punctuation)

    # Preprocesar el texto de entrada: eliminar saltos de línea, espacios al principio y al final, y convertir a minúsculas
    strip_text = input_str.strip().replace("\n", "").lower()

    # Normalizar el texto utilizando el formato NFKD, lo que separa los caracteres acentuados en sus componentes base y acentos
    nfkd_form = unicodedata.normalize("NFKD", strip_text)

    # Codificar el texto normalizado a ASCII ignorando los errores, lo que elimina los acentos
    # Luego decodificar el texto a latin-1 para obtener una cadena de caracteres normal
    only_ascii = nfkd_form.encode("ASCII", "ignore").decode("latin-1")

    # Eliminar todos los signos de puntuación del texto
    no_special_characters = re.sub("[" + chars + "]", "", only_ascii)

    # Reemplazar los backslashes con slashes y dividir el texto en palabras individuales
    list_words = no_special_characters.replace("\\", "/").split()

    # Eliminar las palabras vacías del texto, así como palabras que son números o que tienen menos de 2 caracteres
    no_stopwords_text = [
        re.sub(r"[^\x20-\x7e]", "", word).strip()
        for word in list_words
        if word not in list_stopwords and len(word) >= 2 and not word.isnumeric()
    ]

    # Combinar las palabras procesadas en una cadena de caracteres y devolverla
    clean_text = " ".join(no_stopwords_text).strip()

    return clean_text


def count_words(pdf_file_path):
    pdf_text = extract_pdf_text(pdf_file_path)

    pdf_text_clean = clean_text(pdf_text)

    list_pdf_text_words = pdf_text_clean.split()
    two_words = [
        " ".join(ws) for ws in zip(list_pdf_text_words, list_pdf_text_words[1:])
    ]
    three_words = [
        " ".join(ws)
        for ws in zip(
            list_pdf_text_words, list_pdf_text_words[1:], list_pdf_text_words[2:]
        )
    ]
    four_words = [
        " ".join(ws)
        for ws in zip(
            list_pdf_text_words,
            list_pdf_text_words[1:],
            list_pdf_text_words[2:],
            list_pdf_text_words[3:],
        )
    ]

    dict_one_word = dict(Counter(list_pdf_text_words))
    dict_two_words = dict(Counter(two_words))
    dict_three_words = dict(Counter(three_words))
    dict_four_words = dict(Counter(four_words))

    return (
        pdf_text_clean,
        dict_one_word,
        dict_two_words,
        dict_three_words,
        dict_four_words,
    )
