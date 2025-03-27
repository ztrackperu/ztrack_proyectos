import hashlib
import json
#from server.database import collection 
from server.database import database_mongo ,client,collection
from datetime import datetime,timedelta


#Estanadar para funciones de agregar , editar , buscar , listar 
#token_proyecto_collection =  collection("token_proyecto")
log_general_collection =  collection("log_general")
control_collection = collection("control")
ids_collection = collection("ids_proyectos")
h_control_collection = collection("h_control")
fecha_actual =datetime.now()


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

def procesar_historico(mensaje,user_c,objeto):
    filter_proyecto = {k: v for k, v in objeto.items() if k not in [ 'user_c','user_m','updated_at','created_at']}
    filter_proyecto['mensaje'] = mensaje
    filter_proyecto['user_evento']=user_c
    filter_proyecto['fecha_evento']=datetime.now()
    return filter_proyecto
def procesar_log(evento,usuario,campo) :
    mensaje2 =str(evento)+" : "+str(campo)+" , hecho por : "+str(usuario)
    agrupado = {"evento":mensaje2,"fecha" :datetime.now()}
    return agrupado
def filtrar_no_none(data: dict) -> dict:
    return {k: v for k, v in data.items() if v is not None}
async def guardar_control(control_data: dict) -> dict:
    coincidencia_dato = await control_collection.find_one({"condicion_control":control_data['condicion_control'] ,"operacion_id":control_data['operacion_id'],"estado_control":1},{"_id":0})
    proyecto_ok ="FAIL"
    id_value = control_data['id_control'] if 'id_control' in control_data else 0
    if id_value==0 :
        #se crea el registro  , se busca coincidencia
        if coincidencia_dato :
            proyecto_ok =  "DUPLICADO"
        else :
            ids_proyectos = await ids_collection.find_one({"id_control": {"$exists": True}})
            control_data['created_at'] = datetime.now() 
            control_data['id_control'] = ids_proyectos['id_control']+1 if ids_proyectos else 1
            guardar_control = await control_collection.insert_one(control_data)
            s_ids ={"id_control":control_data['id_control'],"fecha":datetime.now()}
            procesar_ids = await ids_collection.update_one({"_id":ids_proyectos['_id'] },{"$set":s_ids}) if ids_proyectos else await ids_collection.insert_one(s_ids)
            proyecto_ok = await control_collection.find_one({"_id": guardar_control.inserted_id},{"_id":0,"id_control":1,"condicion_control":1})
            #s_control ={}
            #Guardar en historico
            control_historico = procesar_historico("control GUARDADA",control_data['user_c'],control_data)
            guardar_control_historico = await h_control_collection.insert_one(control_historico)
            #Guardar en Log 
            log =procesar_log("control GUARDADA",control_data['user_c'],control_data['condicion_control'])
            guardar_log = await log_general_collection.insert_one(log)
    else : 
        if coincidencia_dato== None  or coincidencia_dato['id_control']==id_value:
            #se actualiza la informacion 
            control_data['updated_at']=datetime.now()
            control_data['user_m'] =control_data['user_c']
            filter_proyecto = {k: v for k, v in control_data.items() if k not in ['id_control', 'user_c','created_at']}
            filter_proyecto2 =filtrar_no_none(filter_proyecto)
            actualizar_proyecto = await control_collection.update_one({"id_control": control_data['id_control'],"estado_control":1},{"$set":filter_proyecto2}) 
            #Guardar en el historico
            control_historico = procesar_historico("control EDITADA",control_data['user_m'],control_data)
            guardar_control_historico = await h_control_collection.insert_one(control_historico)
            #Guardar en Log 
            log =procesar_log("control EDITADO por ",control_data['user_m'],id_value)
            guardar_log = await log_general_collection.insert_one(log)
            proyecto_ok = {"id_control":control_data['id_control'],"condicion_control":control_data['condicion_control']}
        else :
            proyecto_ok ="DUPLICADO"
    return proyecto_ok



async def guardar_control_2(control_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1,"usuario_id":control_data['user_c']},{"_id":0})
    if validar_token and control_data['user_c']:
        if validar_token['fecha_fin']>fecha_actual :            
            coincidencia_dato = await control_collection.find_one({"nombre_control":control_data['nombre_control'] ,"estado_control":1},{"_id":0})
            proyecto_ok ="FAIL"
            id_value = control_data['id_control'] if 'id_control' in control_data else 0
            token_data =control_data['token_proyecto']
            control_data = {k: v for k, v in control_data.items() if k not in ['token_proyecto']}

            if id_value==0 :
                #se crea el registro  , se busca coincidencia
                if coincidencia_dato :
                    proyecto_ok =  "DUPLICADO"
                else :
                    ids_proyectos = await ids_collection.find_one({"id_control": {"$exists": True}})
                    control_data['created_at'] = datetime.now() 
                    control_data['id_control'] = ids_proyectos['id_control']+1 if ids_proyectos else 1
                    guardar_control = await control_collection.insert_one(control_data)
                    s_ids ={"id_control":control_data['id_control'],"fecha":datetime.now()}
                    procesar_ids = await ids_collection.update_one({"_id":ids_proyectos['_id'] },{"$set":s_ids}) if ids_proyectos else await ids_collection.insert_one(s_ids)
                    proyecto_ok = await control_collection.find_one({"_id": guardar_control.inserted_id},{"_id":0,"id_control":1,"nombre_control":1})
                    #Guardar en historico
                    control_historico = procesar_historico("PRE PROYECTO GUARDADO",control_data['user_c'],control_data)
                    guardar_control_historico = await h_control_collection.insert_one(control_historico)
                    #Guardar en Log 
                    log =procesar_log("PRE PROYECTO GUARDADO",control_data['user_c'],control_data['nombre_control'])
                    guardar_log = await log_general_collection.insert_one(log)
            else : 
                print(id_value)
                print(coincidencia_dato)
                if coincidencia_dato== None  or coincidencia_dato['id_control']==id_value:
                    #se actualiza la informacion 
                    control_data['updated_at']=datetime.now()
                    control_data['user_m'] =control_data['user_c']
                    filter_proyecto = {k: v for k, v in control_data.items() if k not in ['id_control', 'user_c','created_at']}
                    filter_proyecto2 =filtrar_no_none(filter_proyecto)
                    print(filter_proyecto2)
                    actualizar_proyecto = await control_collection.update_one({"id_control": control_data['id_control'],"estado_control":1},{"$set":filter_proyecto2}) 
                    #Guardar en el historico
                    control_historico = procesar_historico("PRE PROYECTO EDITADO",control_data['user_c'],control_data)
                    guardar_control_historico = await h_control_collection.insert_one(control_historico)
                    #Guardar en Log 
                    log =procesar_log("PRE PROYECTO EDITADO por ",control_data['user_c'],id_value)
                    guardar_log = await log_general_collection.insert_one(log)
                    proyecto_ok = {"id_control":control_data['id_control'],"nombre_control ":control_data['nombre_control']}
                else :
                    proyecto_ok ="DUPLICADO"
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if control_data['user_c']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":token_data,"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return proyecto_ok
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN/USER"


async def ver_control(control_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1,"usuario_id":control_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            if control_data['especifico']:
                #realizar secuencia para ver informacion especifica 
                especifico = await control_collection.find_one({"id_control":control_data['especifico'],"estado_control":1},{"_id":0 })             
                #Guardar en Log 
                log =procesar_log("Se solicito info de PROYECTO :  ",control_data['id_usuario'],control_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if control_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return especifico
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def listar_control(control_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1,"usuario_id":control_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            notificacions = []
            fecha_inicio = convertir_fecha_inicio(control_data['fecha_inicio']) if control_data['fecha_inicio'] else datetime.now() - timedelta(days=30)
            fecha_fin = convertir_fecha_fin(control_data['fecha_fin']) if control_data['fecha_fin'] else datetime.now() 
            #logica si funciona
            if control_data['tipo_usuario']==1 :
                query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin}}
                #query = {"estado_control":1}
            elif control_data['tipo_usuario']==2 :
                query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin},"estado_control":1}
                #query = {"estado_control":1,"user_c":control_data['id_usuario']}
            else :
                query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin},"estado_control":1,"user_c":control_data['id_usuario']}
            async for notificacion in control_collection.find(query,{"_id":0,"id_control":1,"nombre_control":1,"observaciones_control":1,"estado_control":1,"created_at":1}).sort({"created_at":-1}):
                notificacions.append(notificacion)
            res = {"fecha_inicio" :fecha_inicio,"fecha_fin" :fecha_fin ,"resultado" :notificacions}
            #guardar en log
            log =procesar_log("LISTADO DE PROYECTOS POR ",control_data['id_usuario'],"TODOS")
            guardar_log = await log_general_collection.insert_one(log)
            return res 
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def eliminar_control(control_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1,"usuario_id":control_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            if control_data['especifico']:
                #realizar secuencia para cambiar estado 0 
                objeto = {"estado_control":0,"user_m":control_data['id_usuario'],"updated_at":datetime.now()}   
                especifico = await control_collection.find_one({"id_control":control_data['especifico'],"estado_control":1},{"_id":0 ,"nombre_control":1})             
                print(especifico)
                if especifico :
                    especifico_ok = await control_collection.update_one({"id_control":control_data['especifico'],"estado_control":1},{"$set":objeto})
                    res = "OK"
                else :
                    res = "FAIL"
                #Guardar en Log 
                log =procesar_log("Se elimino PROYECTO :  ",control_data['id_usuario'],control_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if control_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def reestablecer_control(control_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1,"usuario_id":control_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            if control_data['especifico']:
                #realizar secuencia para cambiar estado 0 
                objeto = {"estado_control":1,"user_m":control_data['id_usuario'],"updated_at":datetime.now()}   
                especifico = await control_collection.find_one({"id_control":control_data['especifico'],"estado_control":0},{"_id":0 ,"nombre_control":1})             
                if especifico :
                    especifico_ok = await control_collection.update_one({"id_control":control_data['especifico'],"estado_control":0},{"$set":objeto})
                    res = "OK"
                else :
                    res = "FAIL"
                #Guardar en Log 
                log =procesar_log("Se reestablece el PROYECTO :  ",control_data['id_usuario'],control_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if control_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":control_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

