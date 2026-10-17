"""
algoritmos.py

Algoritmos de búsqueda y ordenamiento implementados manualmente (sin
usar sort() ni sorted()):
- buscar_por_codigo / buscar_por_establecimiento: búsqueda lineal, O(n).
- ordenar_por_prioridad: Selection Sort, O(n^2). Se eligió por ser
  fácil de explicar y seguir paso a paso, adecuado para un curso
  introductorio y para listas pequeñas como las de este prototipo.
  Si el volumen de solicitudes creciera mucho, convendría más un
  algoritmo O(n log n) como Merge Sort.
"""

from datos import prioridad_a_numero


def buscar_por_codigo(lista_solicitudes, codigo_buscado):
    """
    Búsqueda lineal: recorre la lista comparando el código de cada
    solicitud hasta encontrar una coincidencia. O(n) en el peor caso.
    Retorna la solicitud encontrada o None si no existe.
    """
    codigo_buscado = codigo_buscado.strip().upper()
    for solicitud in lista_solicitudes:
        if solicitud["codigo"].upper() == codigo_buscado:
            return solicitud
    return None


def buscar_por_establecimiento(lista_solicitudes, texto_busqueda):
    """
    Búsqueda lineal parcial (sin distinguir mayúsculas) de todas las
    solicitudes cuyo establecimiento contenga el texto buscado. O(n).
    Retorna una lista de coincidencias (puede estar vacía).
    """
    texto_busqueda = texto_busqueda.strip().lower()
    return [s for s in lista_solicitudes if texto_busqueda in s["establecimiento"].lower()]


def ordenar_por_prioridad(lista_solicitudes):
    """
    Ordena una COPIA de la lista por prioridad (P1 primero, P4 al
    final) usando Selection Sort: en cada posición i, busca entre los
    elementos restantes el de prioridad más urgente y lo intercambia
    con el de la posición i. Se repite hasta ordenar toda la lista.
    Complejidad O(n^2): por cada uno de los n elementos se recorre,
    en promedio, la mitad de los restantes.
    """
    lista_ordenada = lista_solicitudes.copy()
    n = len(lista_ordenada)

    for i in range(n - 1):
        indice_mas_urgente = i
        for j in range(i + 1, n):
            if prioridad_a_numero(lista_ordenada[j]["prioridad"]) < \
               prioridad_a_numero(lista_ordenada[indice_mas_urgente]["prioridad"]):
                indice_mas_urgente = j

        if indice_mas_urgente != i:
            lista_ordenada[i], lista_ordenada[indice_mas_urgente] = (
                lista_ordenada[indice_mas_urgente],
                lista_ordenada[i],
            )

    return lista_ordenada
