import hashlib
import json
#from server.database import collection 
from server.database import database_mongo ,client,collection
from datetime import datetime,timedelta

#Estanadar para funciones de agregar , editar , buscar , listar 
log_general_collection =  collection("log_general")
usuarios_collection = collection("usuarios")
ids_collection = collection("ids_proyectos")
h_usuarios_collection = collection("h_usuarios")
fecha_actual =datetime.now()

def procesar_historico(mensaje,user_c,objeto):
    filter_proyecto = {k: v for k, v in objeto.items() if k not in [ 'user_c','user_m','updated_at','created_at']}
    filter_proyecto['mensaje'] = mensaje
    filter_proyecto['user_evento']=user_c
    filter_proyecto['fecha_evento']=fecha_actual
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
def construir_token (usuario,apellido):
    fecha_formateada = fecha_actual.strftime("%d-%m-%Y_%H-%M-%S")
    conjunto = str(usuario)+"_"+fecha_formateada+"_"+str(apellido)
    hash_total = hashlib.sha256(conjunto.encode()).hexdigest()
    return hash_total

async def login_proyecto(login_data:dict)->dict :
    #consulta a la base de datos de usuarios 
    coincidencia_usuario_pass = await usuarios_collection.find_one({"user_proyecto":login_data['user_proyecto'] ,"clave_proyecto":login_data['clave_proyecto'],
    "estado_usuario":1},{"_id":0,"id_usuario":1,"user_proyecto":1,"tipo_usuario":1,"nombres_usuario":1,"apellidos_usuario":1,"url_foto_usuario":1})
    if(coincidencia_usuario_pass) :
        #asignar token 
        coincidencia_usuario_pass["token_proyecto"] = construir_token(coincidencia_usuario_pass['user_proyecto'],coincidencia_usuario_pass['apellidos_usuario'])
        return coincidencia_usuario_pass
    else:
        return 0
    
async def guardar_usuario(usuario_data: dict) -> dict:

    coincidencia_usuario = await usuarios_collection.find_one({"user_proyecto":usuario_data['user_proyecto'] ,"estado_usuario":1},{"_id":0})
    proyecto_ok ="FAIL"
    id_value = usuario_data['id_usuario'] if 'id_usuario' in usuario_data else 0
    if id_value==0 :
        #se crea el registro  , se busca coincidencia
        if coincidencia_usuario :
            proyecto_ok =  "DUPLICADO"
        else :
            ids_proyectos = await ids_collection.find_one({"id_usuario": {"$exists": True}})
            usuario_data['id_usuario'] = ids_proyectos['id_usuario']+1 if ids_proyectos else 1
            guardar_usuario = await usuarios_collection.insert_one(usuario_data)
            s_ids ={"id_usuario":usuario_data['id_usuario'],"fecha":fecha_actual}
            procesar_ids = await ids_collection.update_one({"_id":ids_proyectos['_id'] },{"$set":s_ids}) if ids_proyectos else await ids_collection.insert_one(s_ids)
            proyecto_ok = await usuarios_collection.find_one({"_id": guardar_usuario.inserted_id},{"_id":0,"id_usuario":1,"user_proyecto":1})
            #Guardar en historico
            usuario_historico = procesar_historico("USUARIO GUARDADO",usuario_data['user_c'],usuario_data)
            guardar_usuario_historico = await h_usuarios_collection.insert_one(usuario_historico)
            #Guardar en Log 
            log =procesar_log("USUARIO GUARDADO",usuario_data['user_c'],usuario_data['nombres_usuario'])
            guardar_log = await log_general_collection.insert_one(log)

    else : 
        #se actualiza la informacion 
        usuario_data['updated_at']=fecha_actual
        filter_proyecto = {k: v for k, v in usuario_data.items() if k not in ['id_usuario', 'user_c']}
        filter_proyecto2 =filtrar_no_none(filter_proyecto)
        actualizar_proyecto = await usuarios_collection.update_one({"id_usuario": usuario_data['id_usuario'],"estado_usuario":1},{"$set":filter_proyecto2}) 
        #Guardar en el historico
        usuario_historico = procesar_historico("USUARIO EDITADO",usuario_data['user_c'],usuario_data)
        guardar_usuario_historico = await h_usuarios_collection.insert_one(usuario_historico)
        #Guardar en Log 
        log =procesar_log("USUARIO EDITADO",usuario_data['user_c'],usuario_data['nombres_usuario'])
        guardar_log = await log_general_collection.insert_one(log)
        
        proyecto_ok = {"id_usuario":usuario_data['id_usuario'],"nombre_usuario":usuario_data['id_proyecto']}
    return proyecto_ok

async def aperturar_reportes_en_proyecto(proyecto_data: dict) -> dict:
    return "hola"




