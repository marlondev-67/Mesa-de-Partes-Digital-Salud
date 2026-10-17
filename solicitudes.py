"""
solicitudes.py

Lógica de negocio sobre las solicitudes: creación, registro validado,
actualización, eliminación, estadísticas y reporte de seguimiento.

Estructura de datos: una LISTA de DICCIONARIOS. Cada solicitud es un
diccionario con claves fijas (código, establecimiento, etc.) y todas
se guardan juntas en una sola lista, que se pasa por parámetro entre
funciones y se modifica "en el sitio" (in place).
"""

from datetime import datetime

import datos


# ---------------------------------------------------------------------
# Creación y registro
# ---------------------------------------------------------------------

def codigo_existe(lista_solicitudes, codigo):
    """Indica si un código ya está registrado (sin distinguir mayúsculas)."""
    codigo = codigo.strip().upper()
    return any(s["codigo"].upper() == codigo for s in lista_solicitudes)


def generar_siguiente_codigo(lista_solicitudes):
    """Genera un código sugerido tipo SOL-0001, continuando el consecutivo más alto."""
    maximo = 0
    for solicitud in lista_solicitudes:
        codigo = solicitud.get("codigo", "")
        if codigo.upper().startswith("SOL-") and codigo[4:].isdigit():
            maximo = max(maximo, int(codigo[4:]))
    return f"SOL-{maximo + 1:04d}"


def crear_solicitud(codigo, establecimiento, ubicacion, tipo_emergencia,
                     tipo_solicitud, descripcion, prioridad,
                     numero_afectados=0, condicion_afectados="ninguna_en_particular",
                     cantidad=None):
    """
    Construye el diccionario de una solicitud con sus datos de entrada
    más los campos generados automáticamente: fecha, estado inicial,
    derivación sugerida y constancia de recepción. No valida los
    datos (eso lo hace registrar_solicitud antes de llamar a esta función).
    """
    codigo_final = codigo.strip().upper()
    fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M")
    derivacion = datos.sugerir_derivacion(tipo_solicitud, prioridad.strip().upper())

    return {
        "codigo": codigo_final,
        "establecimiento": establecimiento.strip(),
        "ubicacion": ubicacion.strip(),
        "tipo_emergencia": tipo_emergencia,
        "tipo_solicitud": tipo_solicitud,
        "numero_afectados": numero_afectados if numero_afectados is not None else 0,
        "condicion_afectados": condicion_afectados,
        "descripcion": descripcion.strip(),
        "cantidad": cantidad,
        "fecha_registro": fecha_registro,
        "prioridad": prioridad.strip().upper(),
        "estado": "Pendiente",
        "derivacion": derivacion,
        "constancia_recepcion": (
            f"Constancia de recepción - Código {codigo_final} - Recibido el {fecha_registro}"
        ),
    }


def registrar_solicitud(lista_solicitudes, codigo, establecimiento, ubicacion,
                         tipo_emergencia, tipo_solicitud, descripcion, prioridad,
                         numero_afectados=0, condicion_afectados="ninguna_en_particular",
                         cantidad=None):
    """
    Valida los datos de una nueva solicitud y, si son correctos, la
    agrega a la lista principal. Retorna (exito, mensaje).
    """
    if not datos.campo_no_vacio(codigo):
        return False, "El código no puede estar vacío."
    if not datos.campo_no_vacio(establecimiento):
        return False, "El nombre del establecimiento no puede estar vacío."
    if not datos.campo_no_vacio(ubicacion):
        return False, "La ubicación no puede estar vacía."
    if not datos.campo_no_vacio(descripcion):
        return False, "La descripción no puede estar vacía."
    if tipo_emergencia not in datos.TIPOS_EMERGENCIA_VALIDOS:
        return False, f"Tipo de emergencia no válido: {tipo_emergencia}"
    if tipo_solicitud not in datos.TIPOS_SOLICITUD_VALIDOS:
        return False, f"Tipo de solicitud no válido: {tipo_solicitud}"
    if not datos.validar_prioridad(prioridad):
        return False, f"Prioridad no válida: {prioridad}. Use P1, P2, P3 o P4."
    if condicion_afectados not in datos.CONDICIONES_AFECTADOS_VALIDAS:
        return False, f"Condición de afectados no válida: {condicion_afectados}"
    if numero_afectados is None or numero_afectados < 0:
        return False, "El número de afectados no puede ser negativo."
    if codigo_existe(lista_solicitudes, codigo):
        return False, f"El código '{codigo}' ya existe. Use un código distinto."

    nueva = crear_solicitud(
        codigo, establecimiento, ubicacion, tipo_emergencia, tipo_solicitud,
        descripcion, prioridad, numero_afectados, condicion_afectados, cantidad
    )
    lista_solicitudes.append(nueva)
    return True, f"Solicitud '{nueva['codigo']}' registrada correctamente."


# ---------------------------------------------------------------------
# Actualización y eliminación
# ---------------------------------------------------------------------

def actualizar_estado(lista_solicitudes, codigo, nuevo_estado):
    """Cambia el estado de una solicitud existente. Retorna (exito, mensaje)."""
    if not datos.validar_estado(nuevo_estado):
        return False, f"Estado no válido: {nuevo_estado}"
    codigo = codigo.strip().upper()
    for solicitud in lista_solicitudes:
        if solicitud["codigo"].upper() == codigo:
            solicitud["estado"] = nuevo_estado
            return True, f"Estado de '{codigo}' actualizado a '{nuevo_estado}'."
    return False, f"No se encontró ninguna solicitud con el código '{codigo}'."


def actualizar_prioridad(lista_solicitudes, codigo, nueva_prioridad):
    """Corrige manualmente la prioridad de una solicitud. Retorna (exito, mensaje)."""
    if not datos.validar_prioridad(nueva_prioridad):
        return False, f"Prioridad no válida: {nueva_prioridad}"
    codigo = codigo.strip().upper()
    for solicitud in lista_solicitudes:
        if solicitud["codigo"].upper() == codigo:
            solicitud["prioridad"] = nueva_prioridad.strip().upper()
            return True, f"Prioridad de '{codigo}' actualizada a '{nueva_prioridad}'."
    return False, f"No se encontró ninguna solicitud con el código '{codigo}'."


def eliminar_solicitud(lista_solicitudes, codigo):
    """Elimina una solicitud por código. Retorna (exito, mensaje)."""
    codigo = codigo.strip().upper()
    for indice, solicitud in enumerate(lista_solicitudes):
        if solicitud["codigo"].upper() == codigo:
            lista_solicitudes.pop(indice)
            return True, f"Solicitud '{codigo}' eliminada correctamente."
    return False, f"No se encontró ninguna solicitud con el código '{codigo}'."


# ---------------------------------------------------------------------
# Estadísticas y reporte de seguimiento
# ---------------------------------------------------------------------

def calcular_estadisticas(lista_solicitudes):
    """
    Calcula totales por prioridad, tipo de atención, tipo de
    emergencia y estado, además del total de afectados y el
    porcentaje de solicitudes atendidas.
    """
    total = len(lista_solicitudes)
    por_prioridad = {"P1": 0, "P2": 0, "P3": 0, "P4": 0}
    por_tipo = {tipo: 0 for tipo in datos.TIPOS_SOLICITUD_VALIDOS}
    por_emergencia = {tipo: 0 for tipo in datos.TIPOS_EMERGENCIA_VALIDOS}
    por_estado = {estado: 0 for estado in datos.ESTADOS_VALIDOS}
    total_afectados = 0

    for solicitud in lista_solicitudes:
        if solicitud.get("prioridad") in por_prioridad:
            por_prioridad[solicitud["prioridad"]] += 1
        if solicitud.get("tipo_solicitud") in por_tipo:
            por_tipo[solicitud["tipo_solicitud"]] += 1
        if solicitud.get("tipo_emergencia") in por_emergencia:
            por_emergencia[solicitud["tipo_emergencia"]] += 1
        if solicitud.get("estado") in por_estado:
            por_estado[solicitud["estado"]] += 1
        total_afectados += solicitud.get("numero_afectados", 0) or 0

    atendidas = por_estado.get("Atendida", 0)
    porcentaje_atendidas = round((atendidas / total) * 100, 2) if total > 0 else 0.0

    return {
        "total": total,
        "por_prioridad": por_prioridad,
        "por_tipo": por_tipo,
        "por_emergencia": por_emergencia,
        "por_estado": por_estado,
        "total_afectados": total_afectados,
        "porcentaje_atendidas": porcentaje_atendidas,
    }


def generar_reporte_seguimiento(lista_solicitudes):
    """
    Separa las solicitudes en atendidas, canceladas y pendientes
    (todo lo que no sea "Atendida" ni "Cancelada").
    """
    atendidas, pendientes, canceladas = [], [], []
    for solicitud in lista_solicitudes:
        estado = solicitud.get("estado", "Pendiente")
        if estado == "Atendida":
            atendidas.append(solicitud)
        elif estado == "Cancelada":
            canceladas.append(solicitud)
        else:
            pendientes.append(solicitud)
    return {"atendidas": atendidas, "pendientes": pendientes, "canceladas": canceladas}


# ---------------------------------------------------------------------
# Datos de demostración
# ---------------------------------------------------------------------

def generar_datos_demostracion():
    """Genera solicitudes de ejemplo, claramente ficticias, para probar el sistema."""
    datos_base = [
        ("SOL-DEMO-01", "Posta de Salud Ficticia Norte", "Distrito Ejemplo A",
         "sismo", "ambulancia", "Traslado urgente de paciente (dato de prueba)",
         "P1", 3, "heridos_graves", 1),
        ("SOL-DEMO-02", "Centro de Salud Ficticio Sur", "Distrito Ejemplo B",
         "inundacion", "medicamentos", "Reposición de suero y analgésicos (dato de prueba)",
         "P2", 15, "ninos", 50),
        ("SOL-DEMO-03", "Hospital Ficticio Este", "Distrito Ejemplo C",
         "huaico", "equipos medicos", "Camillas adicionales (dato de prueba)",
         "P3", 8, "adultos_mayores", 5),
        ("SOL-DEMO-04", "Posta de Salud Ficticia Oeste", "Distrito Ejemplo D",
         "deslizamiento", "otros recursos", "Carpas temporales (dato de prueba)",
         "P4", 4, "ninguna_en_particular", 3),
        ("SOL-DEMO-05", "Centro de Salud Ficticio Central", "Distrito Ejemplo E",
         "sismo", "atencion medica", "Brigada médica de apoyo (dato de prueba)",
         "P1", 12, "gestantes", 2),
    ]
    demo = []
    for (codigo, establecimiento, ubicacion, tipo_emergencia, tipo, descripcion,
         prioridad, numero_afectados, condicion, cantidad) in datos_base:
        demo.append(crear_solicitud(
            codigo, establecimiento, ubicacion, tipo_emergencia, tipo,
            descripcion, prioridad, numero_afectados, condicion, cantidad
        ))
    return demo
