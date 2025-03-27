import hashlib
import json
#from server.database import collection 
from server.database import database_mongo ,client,collection
from datetime import datetime,timedelta
from server.funciones.pollitos.control import guardar_control


#Estanadar para funciones de agregar , editar , buscar , listar 
#token_proyecto_collection =  collection("token_proyecto")
log_general_collection =  collection("log_general")
operaciones_collection = collection("operaciones")
#control_collection = collection("control")
ids_collection = collection("ids_proyectos")
#h_control_collection = collection("h_control")
h_operaciones_collection = collection("h_operaciones")
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


async def guardar_operaciones(operaciones_data: dict) -> dict:
    coincidencia_dato = await operaciones_collection.find_one({"titulo_operacion":operaciones_data['titulo_operacion'] ,"estado_operacion":1},{"_id":0})
    proyecto_ok ="FAIL"
    id_value = operaciones_data['id_operacion'] if 'id_operacion' in operaciones_data else 0
    if id_value==0 :
        #se crea el registro  , se busca coincidencia
        if coincidencia_dato :
            proyecto_ok =  "DUPLICADO"
        else :
            ids_proyectos = await ids_collection.find_one({"id_operacion": {"$exists": True}})
            operaciones_data['created_at'] = datetime.now() 
            operaciones_data['id_operacion'] = ids_proyectos['id_operacion']+1 if ids_proyectos else 1
            guardar_operaciones = await operaciones_collection.insert_one(operaciones_data)
            s_ids ={"id_operacion":operaciones_data['id_operacion'],"fecha":datetime.now()}
            procesar_ids = await ids_collection.update_one({"_id":ids_proyectos['_id'] },{"$set":s_ids}) if ids_proyectos else await ids_collection.insert_one(s_ids)
            proyecto_ok = await operaciones_collection.find_one({"_id": guardar_operaciones.inserted_id},{"_id":0,"id_operacion":1,"titulo_operacion":1})
            s_control ={"created_at":operaciones_data['created_at'],"condicion_control":"INICIO" ,"operacion_id":proyecto_ok['id_operacion'],"cantidad_control":operaciones_data['cantidad_control'],"user_c":operaciones_data['user_c']}
            procesar_control = await guardar_control(s_control)
            print("----------------")
            print(procesar_control)
            print("----------------")

            #Guardar en historico
            operaciones_historico = procesar_historico("OPERACION GUARDADA",operaciones_data['user_c'],operaciones_data)
            guardar_operaciones_historico = await h_operaciones_collection.insert_one(operaciones_historico)
            #Guardar en Log 
            log =procesar_log("OPERACION GUARDADA",operaciones_data['user_c'],operaciones_data['titulo_operacion'])
            guardar_log = await log_general_collection.insert_one(log)
    else : 
        if coincidencia_dato== None  or coincidencia_dato['id_operacion']==id_value:
            #se actualiza la informacion 
            operaciones_data['updated_at']=datetime.now()
            operaciones_data['user_m'] =operaciones_data['user_c']
            filter_proyecto = {k: v for k, v in operaciones_data.items() if k not in ['id_operacion', 'user_c','created_at']}
            filter_proyecto2 =filtrar_no_none(filter_proyecto)
            actualizar_proyecto = await operaciones_collection.update_one({"id_operacion": operaciones_data['id_operacion'],"estado_operacion":1},{"$set":filter_proyecto2}) 
            #Guardar en el historico
            operaciones_historico = procesar_historico("OPERACION EDITADA",operaciones_data['user_m'],operaciones_data)
            guardar_operaciones_historico = await h_operaciones_collection.insert_one(operaciones_historico)
            #Guardar en Log 
            log =procesar_log("OPERACION EDITADO por ",operaciones_data['user_m'],id_value)
            guardar_log = await log_general_collection.insert_one(log)
            proyecto_ok = {"id_operacion":operaciones_data['id_operacion'],"titulo_operacion":operaciones_data['titulo_operacion']}
        else :
            proyecto_ok ="DUPLICADO"
    return proyecto_ok


async def ver_operaciones(operaciones_data: dict) -> dict:
    if operaciones_data['especifico']:
        #realizar secuencia para ver informacion especifica 
        especifico = await operaciones_collection.find_one({"id_operacion":operaciones_data['especifico'],"estado_operacion":1},{"_id":0 })             
        #Guardar en Log 
        log =procesar_log("Se solicito info de Operacion :  ",operaciones_data['id_usuario'],operaciones_data['especifico'])
        guardar_log = await log_general_collection.insert_one(log)
        return especifico
    else :
        return "SIN_ESPECIFICO"


async def listar_operaciones(operaciones_data: dict) -> dict:
    notificacions = []
    fecha_inicio = convertir_fecha_inicio(operaciones_data['fecha_inicio']) if operaciones_data['fecha_inicio'] else datetime.now() - timedelta(days=30)
    fecha_fin = convertir_fecha_fin(operaciones_data['fecha_fin']) if operaciones_data['fecha_fin'] else datetime.now() 
    if operaciones_data['id_usuario']==1 :
        query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin}}
    else :
        query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin},"estado_operacion":1}
    async for notificacion in operaciones_collection.find(query,{"_id":0,"id_operacion":1,"codigo_operacion":1,"titulo_operacion":1,"ruta_operacion":1,"estado_operacion":1,"created_at":1}).sort({"created_at":-1}):
        notificacions.append(notificacion)
    res = {"fecha_inicio" :fecha_inicio,"fecha_fin" :fecha_fin ,"resultado" :notificacions}
    #guardar en log
    log =procesar_log("LISTADO DE Operaciones POR ",operaciones_data['id_usuario'],"TODOS")
    guardar_log = await log_general_collection.insert_one(log)
    return res 


async def eliminar_operaciones(operaciones_data: dict) -> dict:
    if operaciones_data['especifico']:
        #realizar secuencia para cambiar estado 0 
        objeto = {"estado_operacion":0,"user_m":operaciones_data['id_usuario'],"updated_at":datetime.now()}   
        especifico = await operaciones_collection.find_one({"id_operacion":operaciones_data['especifico'],"estado_operacion":1},{"_id":0 ,"titulo_operacion":1})             
        print(especifico)
        if especifico :
            especifico_ok = await operaciones_collection.update_one({"id_operacion":operaciones_data['especifico'],"estado_operacion":1},{"$set":objeto})
            res = "OK"
        else :
            res = "FAIL"
        #Guardar en Log 
        log =procesar_log("Se elimino Operacion :  ",operaciones_data['id_usuario'],operaciones_data['especifico'])
        guardar_log = await log_general_collection.insert_one(log)
        return res
    else :
        return "SIN_ESPECIFICO"


async def reestablecer_operaciones(operaciones_data: dict) -> dict:
    if operaciones_data['especifico']:
        #realizar secuencia para cambiar estado 0 
        objeto = {"estado_operacion":1,"user_m":operaciones_data['id_usuario'],"updated_at":datetime.now()}   
        especifico = await operaciones_collection.find_one({"id_operacion":operaciones_data['especifico'],"estado_operacion":0},{"_id":0 ,"titulo_operacion":1})             
        if especifico :
            especifico_ok = await operaciones_collection.update_one({"id_operacion":operaciones_data['especifico'],"estado_operacion":0},{"$set":objeto})
            res = "OK"
        else :
            res = "FAIL"
        #Guardar en Log 
        log =procesar_log("Se reestablece el Operacion :  ",operaciones_data['id_usuario'],operaciones_data['especifico'])
        guardar_log = await log_general_collection.insert_one(log)
        return res
    else :
        return "SIN_ESPECIFICO"



