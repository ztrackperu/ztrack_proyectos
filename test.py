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

tengo las siguientes colecciones en mongodb: proyecto , derivado ,actividad ,objetivo ,re_proyecto_derivado , re_derivado_actividad y re_actividad_objetivo

re_proyecto_derivado tiene  la relación de proyecto y derivado relacionado de muchos a muchos y asi sucesivamente  
el usuario solicita toda la info con id _proyecto , y el resultado debe ser como el siguiente

{
"id_proyecto" :1 ,
"nombre" :"proyecto 1" ,
    "derivado" :[
        {
            "id_derivado" : 3 ,
            "nombre_derivado" :"derivado 1" ,
            "actividad" :[
                {
                    "id_actividad" : 2 ,
                    "nombre_actividad" :"actividad 1" ,
                    "objetivo" : [
                        {
                            "id_objetivo" : 7 ,
                            "nombre_objetivo" :"objetivo 1" ,
                        },
                                                {
                            "id_objetivo" : 3 ,
                            "nombre_objetivo" :"objetivo 2" ,
                        },
                                                {
                            "id_objetivo" : 4 ,
                            "nombre_objetivo" :"objetivo 3" ,
                        }
                    ]
                },
                {
                    "id_actividad" : 4 ,
                    "nombre_actividad" :"actividad 2" ,
                    "objetivo" : [
                        {
                            "id_objetivo" : 3 ,
                            "nombre_objetivo" :"objetivo 2" ,
                        },
                                                {
                            "id_objetivo" : 11 ,
                            "nombre_objetivo" :"objetivo 10" ,
                        },
                                                {
                            "id_objetivo" : 12 ,
                            "nombre_objetivo" :"objetivo 11" ,
                        }
                    ]
                }

            ]
        },
                {
            "id_derivado" : 7 ,
            "nombre_derivado" :"derivado 2" ,
            "actividad" :[
                {
                    "id_actividad" : 21 ,
                    "nombre_actividad" :"actividad 21" ,
                    "objetivo" : [
                        {
                            "id_objetivo" : 117 ,
                            "nombre_objetivo" :"objetivo 111" ,
                        },
                                                {
                            "id_objetivo" : 113 ,
                            "nombre_objetivo" :"objetivo 112" ,
                        },
                                                {
                            "id_objetivo" : 114 ,
                            "nombre_objetivo" :"objetivo 113" ,
                        }
                    ]
                },
                {
                    "id_actividad" : 44 ,
                    "nombre_actividad" :"actividad 42" ,
                    "objetivo" : [
                        {
                            "id_objetivo" : 443 ,
                            "nombre_objetivo" :"objetivo 442" ,
                        },
                                                {
                            "id_objetivo" : 411 ,
                            "nombre_objetivo" :"objetivo 410" ,
                        },
                                                {
                            "id_objetivo" : 412 ,
                            "nombre_objetivo" :"objetivo 411" ,
                        }
                    ]
                }

            ]
        },
    ]
}

genera el proceso para obtener ese resultando consultando desde python 




                pipeline = [
                    {"$match": {"id_pre_proyecto": id_proyecto,"estado_pre_proyecto":1}},  # Filtrar por ID del proyecto
                    {
                        "$lookup": {
                            "from": "pre_derivado",
                            "localField": "id_pre_proyecto",
                            "foreignField": "proyecto_id",
                            "as": "derivado"
                        }
                    },
                    {"$unwind": "$derivado"},  # Desanidar derivados
                    {
                        "$lookup": {
                            "from": "actividades",
                            "localField": "derivado._id",
                            "foreignField": "derivado_id",
                            "as": "derivado.actividad"
                        }
                    },
                    {"$unwind": "$derivado.actividad"},  # Desanidar actividades
                    {
                        "$lookup": {
                            "from": "objetivos",
                            "localField": "derivado.actividad._id",
                            "foreignField": "actividad_id",
                            "as": "derivado.actividad.objetivo"
                        }
                    },
                    {
                        "$group": {
                            "_id": "$_id",
                            "nombre": {"$first": "$nombre"},
                            "derivado": {
                                "$push": {
                                    "id_derivado": "$derivado._id",
                                    "nombre_derivado": "$derivado.nombre",
                                    "actividad": {
                                        "id_actividad": "$derivado.actividad._id",
                                        "nombre_actividad": "$derivado.actividad.nombre",
                                        "objetivo": {
                                            "$map": {
                                                "input": "$derivado.actividad.objetivo",
                                                "as": "obj",
                                                "in": {
                                                    "id_objetivo": "$$obj._id",
                                                    "nombre_objetivo": "$$obj.nombre"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]


#validar operaciones 

                pipeline = [
                    {"$match": {"id_pre_proyecto": proyecto_data['especifico']}},
                    {"$project": {"_id": 0 }},
                    {
                        "$lookup": {
                            "from": "re_proyecto_derivado",
                            "localField": "id_pre_proyecto",
                            "foreignField": "pre_proyecto_id",
                            "as": "rel_proyecto_derivado"
                        }
                    },
                    {"$unwind": "$rel_proyecto_derivado"},
                    {
                        "$lookup": {
                            "from": "pre_derivado",
                            "localField": "rel_proyecto_derivado.pre_derivado_id",
                            "foreignField": "id_pre_derivado",
                            "as": "derivado"
                        }
                    },
                    {"$unwind": "$derivado"},
                    {
                        "$lookup": {
                            "from": "re_derivado_actividad",
                            "localField": "derivado.id_pre_derivado",
                            "foreignField": "pre_derivado_id",
                            "as": "rel_derivado_actividad"
                        }
                    },
                    {"$unwind": "$rel_derivado_actividad"},
                    {
                        "$lookup": {
                            "from": "pre_actividad",
                            "localField": "rel_derivado_actividad.pre_actividad_id",
                            "foreignField": "id_pre_actividad",
                            "as": "derivado.actividad"
                        }
                    },
                    {"$unwind": "$derivado.actividad"},
                    {
                        "$lookup": {
                            "from": "re_actividad_validacion",
                            "localField": "derivado.actividad.id_pre_actividad",
                            "foreignField": "pre_actividad_id",
                            "as": "rel_actividad_validacion"
                        }
                    },
                    {"$unwind": "$rel_actividad_validacion"},
                    {
                        "$lookup": {
                            "from": "pre_validacion",
                            "localField": "rel_actividad_validacion.pre_validacion_id",
                            "foreignField": "id_pre_validacion",
                            "as": "derivado.actividad.validacion"
                        }
                    },
                    {
                        "$group": {
                            "_id" :"$id_pre_proyecto",
                            "id_pre_proyecto": {"$first": "$id_pre_proyecto"},
                            "nombre_pre_proyecto": {"$first": "$nombre_pre_proyecto"},
                            "derivado": {
                                "$push": {
                                    "id_derivado": "$derivado.id_pre_derivado",
                                    "nombre_derivado": "$derivado.nombre_pre_derivado",
                                    "actividad": {
                                        "$push": {
                                            "id_actividad": "$derivado.actividad.id_pre_actividad",
                                            "nombre_actividad": "$derivado.actividad.nombre_pre_actividad",
                                            "validacion": {
                                                "$push": {
                                                    "id_validacion": "$derivado.actividad.validacion.id_pre_validacion",
                                                    "nombre_validacion": "$derivado.actividad.validacion.nombre_pre_validacion"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ]