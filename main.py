"""
main.py

Punto de entrada del programa. Contiene las funciones de interfaz de
consola (pedir datos, mostrar solicitudes, mostrar el menú) y las
funciones que ejecutan cada opción del menú, apoyándose en:
    datos.py       -> catálogos, validaciones, clasificación y JSON
    solicitudes.py -> registro, actualización, eliminación, estadísticas
    algoritmos.py  -> búsqueda lineal y Selection Sort
"""

import algoritmos
import datos
import solicitudes


# ---------------------------------------------------------------------
# Entrada de datos por consola
# ---------------------------------------------------------------------

def pedir_texto_obligatorio(mensaje):
    """Pide un texto y repite la pregunta hasta que no esté vacío."""
    while True:
        valor = input(mensaje).strip()
        if datos.campo_no_vacio(valor):
            return valor
        print("Este campo es obligatorio, no puede quedar vacío.")


def pedir_opcion_de_lista(mensaje, opciones, etiquetas=None):
    """
    Muestra una lista numerada de 'opciones' (usando 'etiquetas' como
    texto visible, si se dan) y retorna la opción elegida, validando
    que el número ingresado esté dentro del rango.
    """
    etiquetas = etiquetas if etiquetas is not None else opciones
    print(f"\n{mensaje}")
    for indice, etiqueta in enumerate(etiquetas, start=1):
        print(f"  {indice}. {etiqueta}")

    while True:
        try:
            opcion = int(input("Elija una opción (número): "))
            if 1 <= opcion <= len(opciones):
                return opciones[opcion - 1]
            print("Opción fuera de rango.")
        except ValueError:
            print("Entrada no válida. Debe ingresar un número.")


def pedir_numero_afectados():
    """Pide el número de personas afectadas (entero >= 0; vacío = 0)."""
    while True:
        texto = input("Número de afectados (0 si no aplica o se desconoce): ").strip()
        if texto == "":
            return 0
        try:
            numero = int(texto)
            if numero >= 0:
                return numero
            print("El número de afectados no puede ser negativo.")
        except ValueError:
            print("Entrada no válida. Debe ingresar un número entero.")


def pedir_prioridad(sugerencia=None):
    """
    Pide el nivel de prioridad (P1-P4). Si hay una sugerencia
    calculada automáticamente, se muestra como referencia y se acepta
    dejando el campo vacío, o puede corregirse escribiendo otro valor.
    """
    print("\nNiveles de prioridad disponibles:")
    for codigo, descripcion in datos.DESCRIPCION_PRIORIDADES.items():
        print(f"  {codigo}: {descripcion}")
    if sugerencia:
        print(f"Sugerencia calculada automáticamente: {sugerencia}")

    while True:
        texto = input(f"Ingrese el nivel de prioridad (P1/P2/P3/P4) [{sugerencia or ''}]: ").strip().upper()
        if texto == "" and sugerencia:
            return sugerencia
        if datos.validar_prioridad(texto):
            return texto
        print("Prioridad no válida. Use P1, P2, P3 o P4.")


def pedir_cantidad_opcional():
    """Pide la cantidad solicitada; puede dejarse vacía si no aplica."""
    while True:
        texto = input("Cantidad solicitada (deje vacío si no aplica): ").strip()
        if texto == "":
            return None
        es_valida, cantidad = datos.validar_cantidad(texto)
        if es_valida:
            return cantidad
        print("La cantidad debe ser un número entero positivo.")


# ---------------------------------------------------------------------
# Salida de datos por consola
# ---------------------------------------------------------------------

def mostrar_solicitud(solicitud):
    """Imprime todos los datos de una solicitud, con formato legible."""
    descripcion_prioridad = datos.DESCRIPCION_PRIORIDADES.get(
        solicitud["prioridad"], solicitud["prioridad"]
    )
    descripcion_condicion = datos.DESCRIPCION_CONDICIONES.get(
        solicitud.get("condicion_afectados", ""), "No especificada"
    )
    print("-" * 50)
    print(f"Código:                {solicitud['codigo']}")
    print(f"Establecimiento:       {solicitud['establecimiento']}")
    print(f"Ubicación:             {solicitud['ubicacion']}")
    print(f"Tipo de emergencia:    {solicitud.get('tipo_emergencia', 'No especificado')}")
    print(f"Tipo de atención:      {solicitud['tipo_solicitud']}")
    print(f"Número de afectados:   {solicitud.get('numero_afectados', 0)}")
    print(f"Condición afectados:   {descripcion_condicion}")
    print(f"Descripción:           {solicitud['descripcion']}")
    print(f"Cantidad:              {solicitud['cantidad'] if solicitud['cantidad'] is not None else 'No aplica'}")
    print(f"Fecha registro:        {solicitud['fecha_registro']}")
    print(f"Prioridad:             {solicitud['prioridad']} ({descripcion_prioridad})")
    print(f"Estado:                {solicitud['estado']}")
    print(f"Derivación asignada:   {solicitud.get('derivacion', 'No asignada')}")
    print(f"Constancia:            {solicitud.get('constancia_recepcion', 'No generada')}")


def mostrar_lista_solicitudes(lista_solicitudes):
    """Imprime todas las solicitudes de una lista, o avisa si está vacía."""
    if len(lista_solicitudes) == 0:
        print("\nNo hay solicitudes registradas.")
        return
    print(f"\nTotal de solicitudes a mostrar: {len(lista_solicitudes)}")
    for solicitud in lista_solicitudes:
        mostrar_solicitud(solicitud)
    print("-" * 50)


# ---------------------------------------------------------------------
# Opciones del menú
# ---------------------------------------------------------------------

def opcion_registrar(lista_solicitudes):
    """Pide todos los datos de una nueva solicitud y la registra."""
    print("\n--- Registrar nueva solicitud ---")
    codigo_sugerido = solicitudes.generar_siguiente_codigo(lista_solicitudes)
    codigo = input(f"Código [{codigo_sugerido}]: ").strip() or codigo_sugerido

    establecimiento = pedir_texto_obligatorio("Nombre del establecimiento de salud: ")
    ubicacion = pedir_texto_obligatorio("Ubicación o distrito: ")
    tipo_emergencia = pedir_opcion_de_lista(
        "Tipos de emergencia disponibles:", datos.TIPOS_EMERGENCIA_VALIDOS
    )
    tipo_solicitud = pedir_opcion_de_lista(
        "Tipos de atención requerida disponibles:", datos.TIPOS_SOLICITUD_VALIDOS
    )
    numero_afectados = pedir_numero_afectados()
    etiquetas_condicion = [datos.DESCRIPCION_CONDICIONES[c] for c in datos.CONDICIONES_AFECTADOS_VALIDAS]
    condicion_afectados = pedir_opcion_de_lista(
        "Condición de los afectados:", datos.CONDICIONES_AFECTADOS_VALIDAS, etiquetas_condicion
    )
    descripcion = pedir_texto_obligatorio("Descripción breve de la necesidad: ")

    sugerencia = datos.sugerir_prioridad(tipo_solicitud, tipo_emergencia, numero_afectados, condicion_afectados)
    prioridad = pedir_prioridad(sugerencia)
    cantidad = pedir_cantidad_opcional()

    exito, mensaje = solicitudes.registrar_solicitud(
        lista_solicitudes, codigo, establecimiento, ubicacion,
        tipo_emergencia, tipo_solicitud, descripcion, prioridad,
        numero_afectados, condicion_afectados, cantidad
    )
    print(("\n[OK] " if exito else "\n[ERROR] ") + mensaje)

    if exito:
        resultado = algoritmos.buscar_por_codigo(lista_solicitudes, codigo)
        print(f"\nConstancia de recepción: {resultado['constancia_recepcion']}")
        print(f"Derivación asignada: {resultado['derivacion']}")


def opcion_mostrar_todas(lista_solicitudes):
    print("\n--- Todas las solicitudes registradas ---")
    mostrar_lista_solicitudes(lista_solicitudes)


def opcion_buscar_codigo(lista_solicitudes):
    print("\n--- Buscar solicitud por código ---")
    codigo = pedir_texto_obligatorio("Ingrese el código a buscar: ")
    resultado = algoritmos.buscar_por_codigo(lista_solicitudes, codigo)
    if resultado is not None:
        print("\nSolicitud encontrada:")
        mostrar_solicitud(resultado)
    else:
        print(f"\nNo se encontró ninguna solicitud con el código '{codigo}'.")


def opcion_buscar_establecimiento(lista_solicitudes):
    print("\n--- Buscar solicitudes por establecimiento ---")
    texto = pedir_texto_obligatorio("Ingrese el nombre (o parte del nombre) del establecimiento: ")
    resultados = algoritmos.buscar_por_establecimiento(lista_solicitudes, texto)
    print(f"\nSe encontraron {len(resultados)} solicitud(es).")
    mostrar_lista_solicitudes(resultados)


def opcion_clasificar_prioridad(lista_solicitudes):
    print("\n--- Clasificar solicitudes por prioridad ---")
    for codigo_prioridad, descripcion in datos.DESCRIPCION_PRIORIDADES.items():
        grupo = [s for s in lista_solicitudes if s["prioridad"] == codigo_prioridad]
        print(f"\n== {codigo_prioridad} ({descripcion}) - {len(grupo)} solicitud(es) ==")
        for solicitud in grupo:
            print(f"  - {solicitud['codigo']} | {solicitud['establecimiento']} | {solicitud['estado']}")


def opcion_ordenar_prioridad(lista_solicitudes):
    print("\n--- Ordenar solicitudes por prioridad (Selection Sort) ---")
    if len(lista_solicitudes) == 0:
        print("No hay solicitudes para ordenar.")
        return
    lista_ordenada = algoritmos.ordenar_por_prioridad(lista_solicitudes)
    print("Orden resultante (de más urgente P1 a menos urgente P4):")
    mostrar_lista_solicitudes(lista_ordenada)


def opcion_actualizar_estado(lista_solicitudes):
    print("\n--- Actualizar estado de una solicitud ---")
    codigo = pedir_texto_obligatorio("Ingrese el código de la solicitud: ")
    resultado = algoritmos.buscar_por_codigo(lista_solicitudes, codigo)
    if resultado is None:
        print(f"No se encontró ninguna solicitud con el código '{codigo}'.")
        return
    mostrar_solicitud(resultado)
    nuevo_estado = pedir_opcion_de_lista("Estados disponibles:", datos.ESTADOS_VALIDOS)
    exito, mensaje = solicitudes.actualizar_estado(lista_solicitudes, codigo, nuevo_estado)
    print(("\n[OK] " if exito else "\n[ERROR] ") + mensaje)


def opcion_mostrar_estadisticas(lista_solicitudes):
    print("\n--- Estadísticas de solicitudes ---")
    stats = solicitudes.calcular_estadisticas(lista_solicitudes)

    print(f"Total de solicitudes:           {stats['total']}")
    print(f"Total de personas afectadas:    {stats['total_afectados']}")

    print("\nPor prioridad:")
    for codigo_prioridad, cantidad in stats["por_prioridad"].items():
        print(f"  {codigo_prioridad} ({datos.DESCRIPCION_PRIORIDADES[codigo_prioridad]}): {cantidad}")

    print("\nPor tipo de atención requerida:")
    for tipo, cantidad in stats["por_tipo"].items():
        print(f"  {tipo}: {cantidad}")

    print("\nPor tipo de emergencia:")
    for emergencia, cantidad in stats["por_emergencia"].items():
        print(f"  {emergencia}: {cantidad}")

    print("\nPor estado:")
    for estado, cantidad in stats["por_estado"].items():
        print(f"  {estado}: {cantidad}")

    print(f"\nPorcentaje de solicitudes atendidas: {stats['porcentaje_atendidas']}%")


def opcion_reporte_seguimiento(lista_solicitudes):
    print("\n--- Reporte de seguimiento (atendidas / pendientes) ---")
    reporte = solicitudes.generar_reporte_seguimiento(lista_solicitudes)

    print(f"\n== ATENDIDAS ({len(reporte['atendidas'])}) ==")
    for solicitud in reporte["atendidas"]:
        print(f"  - {solicitud['codigo']} | {solicitud['establecimiento']}")

    print(f"\n== PENDIENTES DE SEGUIMIENTO ({len(reporte['pendientes'])}) ==")
    for solicitud in reporte["pendientes"]:
        print(f"  - {solicitud['codigo']} | {solicitud['establecimiento']} | {solicitud['estado']}")

    print(f"\n== CANCELADAS ({len(reporte['canceladas'])}) ==")
    for solicitud in reporte["canceladas"]:
        print(f"  - {solicitud['codigo']} | {solicitud['establecimiento']}")


def opcion_eliminar(lista_solicitudes):
    print("\n--- Eliminar una solicitud ---")
    codigo = pedir_texto_obligatorio("Ingrese el código de la solicitud a eliminar: ")
    resultado = algoritmos.buscar_por_codigo(lista_solicitudes, codigo)
    if resultado is None:
        print(f"No se encontró ninguna solicitud con el código '{codigo}'.")
        return
    mostrar_solicitud(resultado)
    confirmacion = input("¿Confirma que desea eliminarla? (si/no): ").strip().lower()
    if confirmacion == "si":
        exito, mensaje = solicitudes.eliminar_solicitud(lista_solicitudes, codigo)
        print(("\n[OK] " if exito else "\n[ERROR] ") + mensaje)
    else:
        print("\nOperación cancelada. La solicitud no fue eliminada.")


def opcion_cargar_demo(lista_solicitudes):
    print("\n--- Cargar datos de demostración ---")
    confirmacion = input(
        "Esto agregará solicitudes ficticias de ejemplo a la lista actual. ¿Desea continuar? (si/no): "
    ).strip().lower()
    if confirmacion != "si":
        print("Operación cancelada.")
        return
    agregadas = 0
    for solicitud_demo in solicitudes.generar_datos_demostracion():
        if not solicitudes.codigo_existe(lista_solicitudes, solicitud_demo["codigo"]):
            lista_solicitudes.append(solicitud_demo)
            agregadas += 1
    print(f"\n[OK] Se agregaron {agregadas} solicitudes de demostración.")


def opcion_guardar(lista_solicitudes):
    print("\n--- Guardar datos ---")
    if datos.guardar_solicitudes(lista_solicitudes):
        print(f"[OK] Datos guardados correctamente en: {datos.RUTA_ARCHIVO}")
    else:
        print("[ERROR] No se pudieron guardar los datos.")


# ---------------------------------------------------------------------
# Menú principal
# ---------------------------------------------------------------------

def mostrar_menu():
    print("\n----------------- MENÚ PRINCIPAL -----------------")
    print("1. Registrar solicitud sanitaria")
    print("2. Mostrar todas las solicitudes")
    print("3. Buscar solicitud por código")
    print("4. Buscar solicitudes por establecimiento de salud")
    print("5. Clasificar solicitudes por prioridad")
    print("6. Ordenar solicitudes por prioridad")
    print("7. Actualizar el estado de una solicitud")
    print("8. Mostrar estadísticas de solicitudes")
    print("9. Eliminar una solicitud")
    print("10. Cargar datos de demostración")
    print("11. Guardar los datos")
    print("12. Ver reporte de seguimiento (atendidas / pendientes)")
    print("13. Salir del sistema")
    print("----------------------------------------------------")


def leer_opcion_menu():
    """Pide una opción entre 1 y 13, validando que sea un número entero en rango."""
    while True:
        try:
            opcion = int(input("\nElija una opción (1-13): "))
            if 1 <= opcion <= 13:
                return opcion
            print("Opción fuera de rango. Ingrese un número entre 1 y 13.")
        except ValueError:
            print("Entrada no válida. Debe ingresar un número entero.")


def main():
    """Carga los datos guardados, ejecuta el bucle del menú y termina al elegir Salir."""
    print("=" * 60)
    print("   MESA DE PARTES DIGITAL-SALUD")
    print("   Gestión de solicitudes de asistencia sanitaria")
    print("   en emergencias por desastres naturales")
    print("=" * 60)

    lista_solicitudes = datos.cargar_solicitudes()
    print(f"\nSe cargaron {len(lista_solicitudes)} solicitud(es) desde el archivo de datos.")

    acciones_del_menu = {
        1: opcion_registrar,
        2: opcion_mostrar_todas,
        3: opcion_buscar_codigo,
        4: opcion_buscar_establecimiento,
        5: opcion_clasificar_prioridad,
        6: opcion_ordenar_prioridad,
        7: opcion_actualizar_estado,
        8: opcion_mostrar_estadisticas,
        9: opcion_eliminar,
        10: opcion_cargar_demo,
        11: opcion_guardar,
        12: opcion_reporte_seguimiento,
    }

    continuar = True
    while continuar:
        mostrar_menu()
        opcion = leer_opcion_menu()

        if opcion == 13:
            respuesta = input("\n¿Desea guardar los cambios antes de salir? (si/no): ").strip().lower()
            if respuesta == "si":
                opcion_guardar(lista_solicitudes)
            print("\nHasta pronto.")
            continuar = False
        else:
            acciones_del_menu[opcion](lista_solicitudes)


if __name__ == "__main__":
    main()
