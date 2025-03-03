def filtrar_no_none(data: dict) -> dict:
    """
    Filtra y devuelve solo los elementos del diccionario que no tienen valores None.
    """
    return {k: v for k, v in data.items() if v is not None}

# Objeto JSON de ejemplo
json_schema_extra = {
    "example": {
        "id_proyecto": None,
        "cotizacion_proyecto": "10020250451",
        "cliente_proyecto": "FRANK DONIO - ZGROUP USA ",
        "activar_reportar": None,
        "fecha_solicitud_proyecto": None,
        "fecha_limite_proyecto": None,
        "nombre_proyecto": "40RH BLAST CHILLER 2XL CON CARACTERISTICAS DE MADURADOR",
        "observaciones_proyecto": "Piso plano 5 máquinas Reefer nuevas MAGNUM PLUS MP4000 (4 reefer y 1 madurador ambos con sistema de aire forzado)",
        "encargado_proyecto": "JHON TELLO ARIAS",
        "prioridad_proyecto": "ALTA",
        "estado_proyecto": None,
        "progreso_proyecto": None,
        "url_proyecto": "test/test.jpg",
        "created_at": None,
        "updated_at": None,
        "user_c": None,
        "user_m": None
    }
}

# Filtrar el diccionario
resultado = filtrar_no_none(json_schema_extra["example"])

# Imprimir el resultado
print(resultado)