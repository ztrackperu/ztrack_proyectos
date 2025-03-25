import json
#from server.database import collection 
from server.database import database_mongo ,client,collection
from datetime import datetime,timedelta

#Estanadar para funciones de agregar , editar , buscar , listar 
token_proyecto_collection =  collection("token_proyecto")
log_general_collection =  collection("log_general")
pre_proyecto_collection = collection("pre_proyecto")


re_actividad_validacion_collection = collection("re_actividad_validacion")
pre_validacion_collection = collection("pre_validacion")
pre_actividad_collection = collection("pre_actividad")
ids_collection = collection("ids_proyectos")
h_re_actividad_validacion_collection = collection("h_re_actividad_validacion")
fecha_actual =datetime.now()

#Estanadar para funciones de agregar , editar , buscar , listar 
log_general_collection =  collection("log_general")
proyectos_collection = collection("proyectos")
ids_collection = collection("ids_proyectos")
h_proyectos_collection = collection("h_proyectos")
fecha_actual =datetime.now()

def procesar_historico(mensaje,user_c,objeto):
    filter_proyecto = {k: v for k, v in objeto.items() if k not in [ 'user_c','user_m','updated_at','created_at']}
    filter_proyecto['mensaje'] = mensaje
    filter_proyecto['user_evento']=user_c
    filter_proyecto['fecha_evento']=datetime.now()
    return filter_proyecto

def procesar_log(evento,usuario,campo) :
    mensaje2 =str(evento)+" : "+str(campo)+" , hecho por : "+str(usuario)
    agrupado = {
        "evento":mensaje2,
        "fecha" :fecha_actual
    }
    return agrupado

def filtrar_no_none(data: dict) -> dict:
    """
    Filtra y devuelve solo los elementos del diccionario que no tienen valores None.
    """
    return {k: v for k, v in data.items() if v is not None}

def historico_proyectos(grupo,evento):
    return "hola"

async def check_mongo_connection():
    try:
        # Intentar obtener la lista de bases de datos como prueba de conexión
        test=collection("admin")
        #await client.admin.command("ping")
        await test.command("ping")

        return True
    except Exception as e:
        print(f"Error de conexión a MongoDB: {e}")
        return False


async def seleccionar_plantilla(proyecto_data: dict) -> dict:
    #aqui se debe obtener el listado de plantillas disponibles para que se seleccione en la
    #fabricacion del proyecto
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":proyecto_data['token_proyecto'],"estado_token":1,"usuario_id":proyecto_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            consulta_uno = {"estado_pre_proyecto":1}
            proyectos=[]
            async for proyecto in pre_proyecto_collection.find(consulta_uno,{"_id":0,"id_pre_proyecto":1,"nombre_pre_proyecto":1,"cantidad_pre_derivados":1}).sort({"created_at":-1}):
                proyectos.append(proyecto)
            #guardar en log
            log =procesar_log("consulta de plantillas de proyectos ",proyecto_data['id_usuario']," TODOS ")
            guardar_log = await log_general_collection.insert_one(log)
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if proyecto_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":proyecto_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return proyectos
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":proyecto_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def datos_plantila(proyecto_data: dict) -> dict:
    #aqui se anidan todo los datos seleccionadospor la plantilla en cuestion 
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":proyecto_data['token_proyecto'],"estado_token":1,"usuario_id":proyecto_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            #anidar pre-proyecto->pre-derivado-->pre-actividad->pre-validacion
            #primero validar que se ha seleccionado un especifico  especifico
            if proyecto_data['especifico'] :

                pipeline = [
                    {"$match": {"id_pre_proyecto": proyecto_data['especifico']}},
                    {"$project": {"_id": 0}},
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
                        "$group": {
                            "_id":"$id_pre_proyecto",
                            "id_pre_proyecto": { "$first": "$id_pre_proyecto" },
                            "nombre_pre_proyecto": {"$first": "nombre_pre_proyecto"},
                            "derivado": {
                                "$push": {
                                    "id_re_proyecto_derivado": "$derivado.id_re_proyecto_derivado",
                                    "id_derivado": "$derivado.id_pre_derivado",
                                    "nombre_derivado": "$derivado.nombre_pre_derivado"
                                }
                            }
                        }
                    }
                ]
                resultado1 = pre_proyecto_collection.aggregate(pipeline)
                resultado = await resultado1.to_list(length=None)  # Convertir a lista

                print("---******")
                print(resultado)
                print("---******")



                #resultado = list(pre_proyecto_collection.aggregate(pipeline))
                return resultado[0] if resultado else {"mensaje": "No se encontró el proyecto"}
                          
            else :
                return "error fatal"


            consulta_uno = {"estado_pre_proyecto":1}
            proyectos=[]
            async for proyecto in pre_proyecto_collection.find(consulta_uno,{"_id":0,"id_pre_proyecto":1,"nombre_pre_proyecto":1,"cantidad_pre_derivados":1}).sort({"created_at":-1}):
                proyectos.append(proyecto)
            #guardar en log
            log =procesar_log("consulta de plantillas de proyectos ",proyecto_data['id_usuario']," TODOS ")
            guardar_log = await log_general_collection.insert_one(log)
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if proyecto_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":proyecto_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return proyectos


        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":proyecto_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"
    



async def guardar_proyectos(proyecto_data: dict) -> dict:
    #validar id_proyecto sino existe asumir que es 0 por lo que es una funcion de guardado 
    print("--------------")
    print(proyecto_data)
    print("--------------")

    coincidencia_proyecto = await proyectos_collection.find_one({"nombre_proyecto":proyecto_data['nombre_proyecto'] ,"estado_proyecto":1},{"_id":0})
    proyecto_ok ="FAIL"
    id_value = proyecto_data['id_proyecto'] if 'id_proyecto' in proyecto_data else 0
    if id_value==0 :
        #se crea el registro  , se busca coincidencia
        if coincidencia_proyecto :
            proyecto_ok =  "DUPLICADO"
        else :
            ids_proyectos = await ids_collection.find_one({"id_proyecto": {"$exists": True}})
            proyecto_data['id_proyecto'] = ids_proyectos['id_proyecto']+1 if ids_proyectos else 1
            guardar_proyecto = await proyectos_collection.insert_one(proyecto_data)
            s_ids ={"id_proyecto":proyecto_data['id_proyecto'],"fecha":fecha_actual}
            procesar_ids = await ids_collection.update_one({"_id":ids_proyectos['_id'] },{"$set":s_ids}) if ids_proyectos else await ids_collection.insert_one(s_ids)
            proyecto_ok = await proyectos_collection.find_one({"_id": guardar_proyecto.inserted_id},{"_id":0,"id_proyecto":1,"nombre_proyecto":1})
            #Guardar en historico
            proyecto_historico = procesar_historico("PROYECTO GUARDADO",proyecto_data['user_c'],proyecto_data)
            guardar_proyecto_historico = await h_proyectos_collection.insert_one(proyecto_historico)
            #Guardar en Log 
            log =procesar_log("PROYECTO GUARDADO",proyecto_data['user_c'],proyecto_data['nombre_proyecto'])
            guardar_log = await log_general_collection.insert_one(log)

    else : 
        #se actualiza la informacion 
        proyecto_data['updated_at']=fecha_actual
        filter_proyecto = {k: v for k, v in proyecto_data.items() if k not in ['id_proyecto', 'user_c']}
        filter_proyecto2 =filtrar_no_none(filter_proyecto)
        actualizar_proyecto = await proyectos_collection.update_one({"id_proyecto": proyecto_data['id_proyecto'],"estado_proyecto":1},{"$set":filter_proyecto2}) 
        #Guardar en el historico
        proyecto_historico = procesar_historico("PROYECTO EDITADO",proyecto_data['user_c'],proyecto_data)
        guardar_proyecto_historico = await h_proyectos_collection.insert_one(proyecto_historico)
        #Guardar en Log 
        log =procesar_log("PROYECTO EDITADO",proyecto_data['user_c'],proyecto_data['nombre_proyecto'])
        guardar_log = await log_general_collection.insert_one(log)
        
        proyecto_ok = {"id_proyecto":proyecto_data['id_proyecto'],"nombre_proyecto":proyecto_data['id_proyecto']}
    return proyecto_ok

async def aperturar_reportes_en_proyecto(proyecto_data: dict) -> dict:
    return "hola"




