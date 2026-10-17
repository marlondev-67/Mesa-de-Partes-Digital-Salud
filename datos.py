"""
datos.py

Catálogos de valores válidos, validaciones de campos, clasificación
de prioridad/derivación y persistencia en archivo JSON. Todo lo que
tiene que ver con "qué datos son válidos" y "cómo se guardan" vive
aquí, separado de la lógica de negocio (solicitudes.py) y de los
algoritmos de búsqueda/ordenamiento (algoritmos.py).
"""

import json
import os
from datetime import datetime

# ---------------------------------------------------------------------
# Catálogos
# ---------------------------------------------------------------------

TIPOS_EMERGENCIA_VALIDOS = ["sismo", "inundacion", "huaico", "deslizamiento", "otro"]

TIPOS_SOLICITUD_VALIDOS = [
    "atencion medica", "medicamentos", "ambulancia", "equipos medicos", "otros recursos",
]

CONDICIONES_AFECTADOS_VALIDAS = [
    "ninguna_en_particular", "ninos", "gestantes", "adultos_mayores", "heridos_graves",
]

DESCRIPCION_CONDICIONES = {
    "ninguna_en_particular": "Sin condición vulnerable específica",
    "ninos": "Niños",
    "gestantes": "Gestantes",
    "adultos_mayores": "Adultos mayores",
    "heridos_graves": "Heridos graves",
}

PRIORIDADES_VALIDAS = ["P1", "P2", "P3", "P4"]

DESCRIPCION_PRIORIDADES = {"P1": "Crítica", "P2": "Alta", "P3": "Media", "P4": "Baja"}

ESTADOS_VALIDOS = ["Pendiente", "En evaluación", "En atención", "Atendida", "Cancelada"]


# ---------------------------------------------------------------------
# Validaciones
# ---------------------------------------------------------------------

def campo_no_vacio(valor):
    """Verifica que un texto no esté vacío ni sean solo espacios."""
    return isinstance(valor, str) and valor.strip() != ""


def validar_prioridad(prioridad):
    """Verifica que la prioridad sea P1, P2, P3 o P4."""
    return prioridad.strip().upper() in PRIORIDADES_VALIDAS


def validar_estado(estado):
    """Verifica que el estado esté dentro de ESTADOS_VALIDOS."""
    return estado in ESTADOS_VALIDOS


def validar_cantidad(texto_cantidad):
    """
    Valida que el texto sea un entero positivo.
    Retorna (es_valido, cantidad_o_None).
    """
    try:
        cantidad = int(texto_cantidad)
        return (True, cantidad) if cantidad > 0 else (False, None)
    except ValueError:
        return False, None


# ---------------------------------------------------------------------
# Clasificación de prioridad y derivación
# ---------------------------------------------------------------------

MAPA_PRIORIDAD_A_NUMERO = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}

PRIORIDADES_BASE_POR_TIPO = {
    "atencion medica": "P1",
    "ambulancia": "P1",
    "medicamentos": "P2",
    "equipos medicos": "P3",
    "otros recursos": "P4",
}

DERIVACIONES_POR_TIPO = {
    "ambulancia": "Brigada de traslado y emergencias (ambulancia)",
    "atencion medica": "Brigada médica de atención directa",
    "medicamentos": "Almacén de medicamentos / logística de insumos",
    "equipos medicos": "Logística de equipos médicos",
    "otros recursos": "Coordinación general de recursos",
}

TIPOS_EMERGENCIA_QUE_AGRAVAN = ("sismo", "huaico")
CONDICIONES_QUE_AGRAVAN = ("ninos", "gestantes", "adultos_mayores", "heridos_graves")
UMBRAL_AFECTADOS_QUE_AGRAVA = 10


def prioridad_a_numero(codigo_prioridad):
    """Convierte 'P1'..'P4' en 1..4, para poder compararlas."""
    return MAPA_PRIORIDAD_A_NUMERO.get(codigo_prioridad, 99)


def sugerir_prioridad(tipo_solicitud, tipo_emergencia="otro", numero_afectados=0,
                       condicion_afectados="ninguna_en_particular"):
    """
    Calcula una prioridad sugerida: parte de una base según el tipo de
    atención requerida y la agrava (sube un nivel) por cada factor
    presente: emergencia tipo sismo/huaico, 10 o más afectados, o
    condición vulnerable (niños, gestantes, adultos mayores, heridos
    graves). El resultado queda siempre entre P1 y P4.
    """
    nivel = prioridad_a_numero(PRIORIDADES_BASE_POR_TIPO.get(tipo_solicitud, "P4"))

    if tipo_emergencia in TIPOS_EMERGENCIA_QUE_AGRAVAN:
        nivel -= 1
    if numero_afectados is not None and numero_afectados >= UMBRAL_AFECTADOS_QUE_AGRAVA:
        nivel -= 1
    if condicion_afectados in CONDICIONES_QUE_AGRAVAN:
        nivel -= 1

    nivel = max(1, min(4, nivel))
    return f"P{nivel}"


def sugerir_derivacion(tipo_solicitud, prioridad):
    """Sugiere a qué brigada o área derivar la solicitud."""
    base = DERIVACIONES_POR_TIPO.get(tipo_solicitud, "Coordinación general de recursos")
    if prioridad == "P1":
        return f"{base} (atención inmediata / primera salida disponible)"
    return base


# ---------------------------------------------------------------------
# Persistencia en archivo JSON
# ---------------------------------------------------------------------

CARPETA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos")
RUTA_ARCHIVO = os.path.join(CARPETA_DATOS, "solicitudes.json")


def asegurar_carpeta_datos():
    """Crea la carpeta 'datos/' si todavía no existe."""
    if not os.path.exists(CARPETA_DATOS):
        os.makedirs(CARPETA_DATOS)


def guardar_solicitudes(lista_solicitudes, ruta=RUTA_ARCHIVO):
    """Guarda la lista de solicitudes en un archivo JSON. Retorna True/False."""
    asegurar_carpeta_datos()
    try:
        with open(ruta, "w", encoding="utf-8") as archivo:
            json.dump(lista_solicitudes, archivo, ensure_ascii=False, indent=4)
        return True
    except (IOError, OSError, TypeError) as error:
        print(f"Error al guardar los datos: {error}")
        return False


def cargar_solicitudes(ruta=RUTA_ARCHIVO):
    """
    Carga la lista de solicitudes desde el archivo JSON. Si el archivo
    no existe todavía, retorna una lista vacía en vez de fallar.
    """
    if not os.path.exists(ruta):
        return []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return datos if isinstance(datos, list) else []
    except (json.JSONDecodeError, IOError, OSError) as error:
        print(f"Error al leer el archivo de datos: {error}")
        return []
