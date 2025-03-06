import hashlib
import json
#from server.database import collection 
from server.database import database_mongo ,client,collection
from datetime import datetime,timedelta

#Estanadar para funciones de agregar , editar , buscar , listar 
token_proyecto_collection =  collection("token_proyecto")
log_general_collection =  collection("log_general")
pre_validacion_collection = collection("pre_validacion")
ids_collection = collection("ids_proyectos")
h_pre_validacion_collection = collection("h_pre_validacion")
fecha_actual =datetime.now()

def procesar_historico(mensaje,user_c,objeto):
    filter_proyecto = {k: v for k, v in objeto.items() if k not in [ 'user_c','user_m','updated_at','created_at']}
    filter_proyecto['mensaje'] = mensaje
    filter_proyecto['user_evento']=user_c
    filter_proyecto['fecha_evento']=fecha_actual
    return filter_proyecto
def procesar_log(evento,usuario,campo) :
    mensaje2 =str(evento)+" : "+str(campo)+" , hecho por : "+str(usuario)
    agrupado = {"evento":mensaje2,"fecha" :datetime.now()}
    return agrupado
def filtrar_no_none(data: dict) -> dict:
    """Filtra y devuelve solo los elementos del diccionario que no tienen valores None."""
    return {k: v for k, v in data.items() if v is not None}
def convertir_fecha_inicio(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d-%m-%Y_%H-%M-%S")
    except ValueError:
        return datetime.now()- timedelta(days=30)
def convertir_fecha_fin(fecha_str):
    try:
        return datetime.strptime(fecha_str, "%d-%m-%Y_%H-%M-%S")
    except ValueError:
        return datetime.now() 

async def guardar_pre_validacion(pre_validacion_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1,"usuario_id":pre_validacion_data['user_c']},{"_id":0})
    if validar_token and pre_validacion_data['user_c']:
        if validar_token['fecha_fin']>fecha_actual :            
            coincidencia_dato = await pre_validacion_collection.find_one({"nombre_pre_validacion":pre_validacion_data['nombre_pre_validacion'] ,"estado_pre_validacion":1},{"_id":0})
            proyecto_ok ="FAIL"
            id_value = pre_validacion_data['id_pre_validacion'] if 'id_pre_validacion' in pre_validacion_data else 0
            token_data =pre_validacion_data['token_proyecto']
            pre_validacion_data = {k: v for k, v in pre_validacion_data.items() if k not in ['token_proyecto']}

            if id_value==0 :
                #se crea el registro  , se busca coincidencia
                if coincidencia_dato :
                    proyecto_ok =  "DUPLICADO"
                else :
                    ids_proyectos = await ids_collection.find_one({"id_pre_validacion": {"$exists": True}})
                    pre_validacion_data['created_at'] = datetime.now() 
                    pre_validacion_data['id_pre_validacion'] = ids_proyectos['id_pre_validacion']+1 if ids_proyectos else 1
                    guardar_pre_validacion = await pre_validacion_collection.insert_one(pre_validacion_data)
                    s_ids ={"id_pre_validacion":pre_validacion_data['id_pre_validacion'],"fecha":datetime.now()}
                    procesar_ids = await ids_collection.update_one({"_id":ids_proyectos['_id'] },{"$set":s_ids}) if ids_proyectos else await ids_collection.insert_one(s_ids)
                    proyecto_ok = await pre_validacion_collection.find_one({"_id": guardar_pre_validacion.inserted_id},{"_id":0,"id_pre_validacion":1,"nombre_pre_validacion":1})
                    #Guardar en historico
                    pre_validacion_historico = procesar_historico("PRE VALIDACION GUARDADO",pre_validacion_data['user_c'],pre_validacion_data)
                    guardar_pre_validacion_historico = await h_pre_validacion_collection.insert_one(pre_validacion_historico)
                    #Guardar en Log 
                    log =procesar_log("PRE VALIDACION GUARDADO",pre_validacion_data['user_c'],pre_validacion_data['nombre_pre_validacion'])
                    guardar_log = await log_general_collection.insert_one(log)
            else : 
                print(id_value)
                print(coincidencia_dato)
                if coincidencia_dato== None  or coincidencia_dato['id_pre_validacion']==id_value:
                    #se actualiza la informacion 
                    pre_validacion_data['updated_at']=datetime.now()
                    pre_validacion_data['user_m'] =pre_validacion_data['user_c']
                    filter_proyecto = {k: v for k, v in pre_validacion_data.items() if k not in ['id_pre_validacion', 'user_c','created_at']}
                    filter_proyecto2 =filtrar_no_none(filter_proyecto)
                    print(filter_proyecto2)
                    actualizar_proyecto = await pre_validacion_collection.update_one({"id_pre_validacion": pre_validacion_data['id_pre_validacion'],"estado_pre_validacion":1},{"$set":filter_proyecto2}) 
                    #Guardar en el historico
                    pre_validacion_historico = procesar_historico("PRE VALIDACION EDITADO",pre_validacion_data['user_c'],pre_validacion_data)
                    guardar_pre_validacion_historico = await h_pre_validacion_collection.insert_one(pre_validacion_historico)
                    #Guardar en Log 
                    log =procesar_log("PRE VALIDACION EDITADO por ",pre_validacion_data['user_c'],id_value)
                    guardar_log = await log_general_collection.insert_one(log)
                    proyecto_ok = {"id_pre_validacion":pre_validacion_data['id_pre_validacion'],"nombre_pre_validacion ":pre_validacion_data['nombre_pre_validacion']}
                else :
                    proyecto_ok ="DUPLICADO"
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if pre_validacion_data['user_c']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":token_data,"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return proyecto_ok
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN/USER"


async def ver_pre_validacion(pre_validacion_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1,"usuario_id":pre_validacion_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            if pre_validacion_data['especifico']:
                #realizar secuencia para ver informacion especifica 
                especifico = await pre_validacion_collection.find_one({"id_pre_validacion":pre_validacion_data['especifico'],"estado_pre_validacion":1},{"_id":0 })             
                #Guardar en Log 
                log =procesar_log("Se solicito info de VALIDACION :  ",pre_validacion_data['id_usuario'],pre_validacion_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if pre_validacion_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return especifico
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def listar_pre_validacion(pre_validacion_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1,"usuario_id":pre_validacion_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            notificacions = []
            fecha_inicio = convertir_fecha_inicio(pre_validacion_data['fecha_inicio']) if pre_validacion_data['fecha_inicio'] else datetime.now() - timedelta(days=30)
            fecha_fin = convertir_fecha_fin(pre_validacion_data['fecha_fin']) if pre_validacion_data['fecha_fin'] else datetime.now() 
            #logica si funciona
            if pre_validacion_data['tipo_usuario']==1 :
                query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin}}
                #query = {"estado_pre_validacion":1}
            elif pre_validacion_data['tipo_usuario']==2 :
                query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin,"estado_pre_validacion":1}}
                #query = {"estado_pre_validacion":1,"user_c":pre_validacion_data['id_usuario']}
            else :
                query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin,"estado_pre_validacion":1,"user_c":pre_validacion_data['id_usuario']}}
            async for notificacion in pre_validacion_collection.find(query,{"_id":0,"id_pre_validacion":1,"nombre_pre_validacion":1,"observaciones_pre_validacion":1,"estado_pre_validacion":1,"created_at":1}).sort({"created_at":-1}):
                notificacions.append(notificacion)
            res = {"fecha_inicio" :fecha_inicio,"fecha_fin" :fecha_fin ,"resultado" :notificacions}
            #guardar en log
            log =procesar_log("LISTADO DE VALIDACIONES POR ",pre_validacion_data['id_usuario'],"TODOS")
            guardar_log = await log_general_collection.insert_one(log)
            return res 
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def eliminar_pre_validacion(pre_validacion_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1,"usuario_id":pre_validacion_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            if pre_validacion_data['especifico']:
                #realizar secuencia para cambiar estado 0 
                objeto = {"estado_pre_validacion":0,"user_m":pre_validacion_data['id_usuario'],"updated_at":datetime.now()}   
                especifico = await pre_validacion_collection.find_one({"id_pre_validacion":pre_validacion_data['especifico'],"estado_pre_validacion":1},{"_id":0 ,"nombre_pre_validacion":1})             
                print(especifico)
                if especifico :
                    especifico_ok = await pre_validacion_collection.update_one({"id_pre_validacion":pre_validacion_data['especifico'],"estado_pre_validacion":1},{"$set":objeto})
                    res = "OK"
                else :
                    res = "FAIL"
                #Guardar en Log 
                log =procesar_log("Se elimino VALIDACION :  ",pre_validacion_data['id_usuario'],pre_validacion_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if pre_validacion_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def reestablecer_pre_validacion(pre_validacion_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1,"usuario_id":pre_validacion_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            if pre_validacion_data['especifico']:
                #realizar secuencia para cambiar estado 0 
                objeto = {"estado_pre_validacion":1,"user_m":pre_validacion_data['id_usuario'],"updated_at":datetime.now()}   
                especifico = await pre_validacion_collection.find_one({"id_pre_validacion":pre_validacion_data['especifico'],"estado_pre_validacion":0},{"_id":0 ,"nombre_pre_validacion":1})             
                if especifico :
                    especifico_ok = await pre_validacion_collection.update_one({"id_pre_validacion":pre_validacion_data['especifico'],"estado_pre_validacion":0},{"$set":objeto})
                    res = "OK"
                else :
                    res = "FAIL"
                #Guardar en Log 
                log =procesar_log("Se reestablece el VALIDACION :  ",pre_validacion_data['id_usuario'],pre_validacion_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if pre_validacion_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":pre_validacion_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

