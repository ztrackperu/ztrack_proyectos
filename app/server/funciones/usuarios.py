import hashlib
import json
#from server.database import collection 
from server.database import database_mongo ,client,collection
from datetime import datetime,timedelta
from cryptography.fernet import Fernet


#Estanadar para funciones de agregar , editar , buscar , listar 
token_proyecto_collection =  collection("token_proyecto")
log_general_collection =  collection("log_general")
usuarios_collection = collection("usuarios")
ids_collection = collection("ids_proyectos")
h_usuarios_collection = collection("h_usuarios")


async def crear_token(usuario_id,token):
    ids_proyectos = await ids_collection.find_one({"id_token": {"$exists": True}})
    id_token = ids_proyectos['id_token']+1 if ids_proyectos['id_token'] else 1
    json_data = {
        "id_token":id_token,
        "usuario_id":usuario_id,
        "token_proyecto":token,
        "estado_token":1,
        "fecha_inicio" :datetime.now(),
        "fecha_fin" :datetime.now() + timedelta(minutes=30)
    }
    #actualizar token 
    ids_proyectos = await ids_collection.update_one({"_id":ids_proyectos['_id']},{"set":{"id_token":id_token} })
    return json_data

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
        "fecha" :datetime.now()
    }
    return agrupado

def filtrar_no_none(data: dict) -> dict:
    """
    Filtra y devuelve solo los elementos del diccionario que no tienen valores None.
    """
    return {k: v for k, v in data.items() if v is not None}
def encriptar_token (usuario,apellido):
    fecha_formateada = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    conjunto = str(usuario)+"_"+fecha_formateada+"_"+str(apellido)
    print(conjunto)
    hash_total = hashlib.sha256(conjunto.encode()).hexdigest()
    return hash_total

async def login_proyecto(login_data:dict)->dict :
    #consulta a la base de datos de usuarios 
    print(login_data)
    coincidencia_usuario_pass = await usuarios_collection.find_one({"user_proyecto":login_data['user_proyecto'] ,"clave_proyecto":login_data['clave_proyecto'],
    "estado_usuario":1},{"_id":0,"id_usuario":1,"user_proyecto":1,"tipo_usuario":1,"nombres_usuario":1,"apellidos_usuario":1,"url_foto_usuario":1})
    if(coincidencia_usuario_pass) :
        #validar si ya existe un token y si existe inabilitarlo poninedo estado en 0 
        validar_token = await token_proyecto_collection.find_one({"usuario_id":coincidencia_usuario_pass['id_usuario'],"estado_token":1},{"_id":0})
        if  validar_token :
            # invalidar token 
            if coincidencia_usuario_pass['id_usuario'] !=1 :
                invalidar_token = await token_proyecto_collection.update_one({"usuario_id":coincidencia_usuario_pass['id_usuario'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":datetime.now()}}) 
                coincidencia_usuario_pass["token_proyecto"] = encriptar_token(coincidencia_usuario_pass['user_proyecto'],coincidencia_usuario_pass['apellidos_usuario'])
                secuencia_token = await crear_token(coincidencia_usuario_pass["id_usuario"],coincidencia_usuario_pass["token_proyecto"])
                guardar_token = await token_proyecto_collection.insert_one(secuencia_token)
            else :
                coincidencia_usuario_pass["token_proyecto"] =validar_token['token_proyecto']
                #Guardar en Log 
                log =procesar_log("USUARIO logeado  ",login_data['user_proyecto'],coincidencia_usuario_pass['id_usuario'])
                guardar_log = await log_general_collection.insert_one(log)
            return coincidencia_usuario_pass

        else :
            #asignar token 
            coincidencia_usuario_pass["token_proyecto"] = encriptar_token(coincidencia_usuario_pass['user_proyecto'],coincidencia_usuario_pass['apellidos_usuario'])
            secuencia_token = await crear_token(coincidencia_usuario_pass["id_usuario"],coincidencia_usuario_pass["token_proyecto"])
            guardar_token = await token_proyecto_collection.insert_one(secuencia_token)
            return coincidencia_usuario_pass
    else:
        return 0


async def super_usuario() :
    super_user=  {"id_usuario":1,"user_proyecto":"AdministradorZ","clave_proyecto":"0f2adb0aee3de894ac4e28bfce85a54f5a80b06cb4118b374892a1248b02a395",
        "estado_usuario":1,"tipo_usuario":1,"dni_usuario" :"73144309","token_proyecto":"proyectoztrack2025!","nombres_usuario" :"ZGROUP",
        "apellidos_usuario" :" PERU","correo_usuario" : "ztrack@zgroup.com.pe","url_foto_usuario" :"fotos/usuarios/test_usuario.png",
        "created_at":datetime.now(),"updated_at":datetime.now(),"user_c":1,"user_m":1}
    super_token= {"id_token":1,"usuario_id":1,"token_proyecto":"proyectoztrack2025!","estado_token":1,
        "fecha_inicio" :datetime.now(),"fecha_fin" :datetime.now() + timedelta(days=3000)}
    super_ids = {"id_token":1 ,"id_usuario":1 }
    validar_token = await token_proyecto_collection.find_one({"id_token":1})
    guardar_token = 0 if validar_token else await token_proyecto_collection.insert_one(super_token)
    validar_usuario = await usuarios_collection.find_one({"id_usuario":1})
    guardar_usuario = 0 if validar_usuario else await usuarios_collection.insert_one(super_user)
    validar_ids = await ids_collection.find_one({"id_usuario":1})
    guardar_ids = 0 if validar_ids else await ids_collection.insert_one(super_ids)
    return "ok"


async def guardar_usuario(usuario_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1,"usuario_id":usuario_data['user_c']},{"_id":0})
    if validar_token and usuario_data['user_c']:
        if validar_token['fecha_fin']>datetime.now() :            
            coincidencia_usuario = await usuarios_collection.find_one({"user_proyecto":usuario_data['user_proyecto'] ,"estado_usuario":1},{"_id":0})
            proyecto_ok ="FAIL"
            id_value = usuario_data['id_usuario'] if 'id_usuario' in usuario_data else 0
            token_data = usuario_data['token_proyecto']
            usuario_data = {k: v for k, v in usuario_data.items() if k not in ['token_proyecto']}
            if id_value==0 :
                #se crea el registro  , se busca coincidencia
                if coincidencia_usuario :
                    proyecto_ok =  "DUPLICADO"
                else :
                    if usuario_data['clave_proyecto']!="SINCLAVE":
                        ids_proyectos = await ids_collection.find_one({"id_usuario": {"$exists": True}})
                        usuario_data['created_at'] = datetime.now() 
                        usuario_data['id_usuario'] = ids_proyectos['id_usuario']+1 if ids_proyectos else 1
                        guardar_usuario = await usuarios_collection.insert_one(usuario_data)
                        s_ids ={"id_usuario":usuario_data['id_usuario'],"fecha":datetime.now()}
                        procesar_ids = await ids_collection.update_one({"_id":ids_proyectos['_id'] },{"$set":s_ids}) if ids_proyectos else await ids_collection.insert_one(s_ids)
                        proyecto_ok = await usuarios_collection.find_one({"_id": guardar_usuario.inserted_id},{"_id":0,"id_usuario":1,"user_proyecto":1})
                        #Guardar en historico
                        usuario_historico = procesar_historico("USUARIO GUARDADO",usuario_data['user_c'],usuario_data)
                        guardar_usuario_historico = await h_usuarios_collection.insert_one(usuario_historico)
                        #Guardar en Log 
                        log =procesar_log("USUARIO GUARDADO",usuario_data['user_c'],usuario_data['user_proyecto'])
                        guardar_log = await log_general_collection.insert_one(log)
                    else :
                        return "SINCLAVE"
            else : 
                #se actualiza la informacion 
                usuario_data['updated_at']=datetime.now()
                usuario_data['user_m'] =usuario_data['user_c']
                filter_proyecto = {k: v for k, v in usuario_data.items() if k not in ['id_usuario', 'user_c','created_at','clave_proyecto']}
                filter_proyecto2 =filtrar_no_none(filter_proyecto)
                actualizar_proyecto = await usuarios_collection.update_one({"id_usuario": usuario_data['id_usuario'],"estado_usuario":1},{"$set":filter_proyecto2}) 
                #Guardar en el historico
                usuario_historico = procesar_historico("USUARIO EDITADO",usuario_data['user_c'],usuario_data)
                guardar_usuario_historico = await h_usuarios_collection.insert_one(usuario_historico)
                #Guardar en Log 
                log =procesar_log("USUARIO EDITADO por ",usuario_data['user_c'],usuario_data['id_usuario'])
                guardar_log = await log_general_collection.insert_one(log)
                
                proyecto_ok = {"id_usuario":usuario_data['id_usuario'],"nombre_usuario":usuario_data['user_proyecto']}
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if usuario_data['user_c']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":token_data,"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return proyecto_ok
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":token_data,"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":datetime.now()}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN/USER"

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

async def ver_usuario(usuario_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1,"usuario_id":usuario_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>datetime.now() :
            if usuario_data['especifico']:
                #realizar secuencia para ver informacion especifica 
                especifico = await usuarios_collection.find_one({"id_usuario":usuario_data['especifico'],"estado_usuario":1},{"_id":0 ,"clave_proyecto":0,"token_proyecto":0})             
                #Guardar en Log 
                log =procesar_log("Se solicito info de usuario :  ",usuario_data['id_usuario'],usuario_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if usuario_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return especifico
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":datetime.now()}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def listar_usuarios(usuario_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1,"usuario_id":usuario_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>datetime.now() :
            notificacions = []
            fecha_inicio = convertir_fecha_inicio(usuario_data['fecha_inicio']) if usuario_data['fecha_inicio'] else datetime.now() - timedelta(days=30)
            fecha_fin = convertir_fecha_fin(usuario_data['fecha_fin']) if usuario_data['fecha_fin'] else datetime.now() 
            #logica si funciona
            if usuario_data['tipo_usuario']==1 :
                query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin}}
            elif usuario_data['tipo_usuario']==2 :
                query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin},"estado_usuario":1}
            else :
                query = {"created_at": {"$gte": fecha_inicio, "$lte": fecha_fin},"estado_usuario":1,"user_c":usuario_data['user_c']}
            async for notificacion in usuarios_collection.find(query,{"_id":0,"id_usuario":1,"user_proyecto":1,"nombres_usuario":1,"estado_usuario":1,"tipo_usuario":1,"created_at":1,"apellidos_usuario":1}).sort({"created_at":-1}):
                notificacions.append(notificacion)
            print("__________")
            print(query)
            print("__________")
            print(notificacions)
            res = {"fecha_inicio" :fecha_inicio,"fecha_fin" :fecha_fin ,"resultado" :notificacions}
            #guardar en log
            log =procesar_log("LISTADO DE USUARIOS POR ",usuario_data['id_usuario'],usuario_data['tipo_usuario'])
            guardar_log = await log_general_collection.insert_one(log)
            return res 
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":datetime.now()}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def eliminar_usuarios(usuario_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1,"usuario_id":usuario_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>datetime.now() :
            if usuario_data['especifico']:
                #realizar secuencia para cambiar estado 0 
                objeto = {"estado_usuario":0,"user_m":usuario_data['id_usuario'],"updated_at":datetime.now()}   
                especifico = await usuarios_collection.find_one({"id_usuario":usuario_data['especifico'],"estado_usuario":1},{"_id":0 ,"user_proyecto":1})             
                if especifico :
                    especifico_ok = await usuarios_collection.update_one({"id_usuario":usuario_data['especifico'],"estado_usuario":1},{"$set":objeto})
                    res = "OK"
                else :
                    res = "FAIL"
                #Guardar en Log 
                log =procesar_log("Se elimino usuario :  ",usuario_data['id_usuario'],usuario_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if usuario_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":datetime.now()}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def reestablecer_usuarios(usuario_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1,"usuario_id":usuario_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>datetime.now() :
            if usuario_data['especifico']:
                #realizar secuencia para cambiar estado 0 
                objeto = {"estado_usuario":1,"user_m":usuario_data['id_usuario'],"updated_at":datetime.now()}   
                especifico = await usuarios_collection.find_one({"id_usuario":usuario_data['especifico'],"estado_usuario":0},{"_id":0 ,"user_proyecto":1})             
                if especifico :
                    especifico_ok = await usuarios_collection.update_one({"id_usuario":usuario_data['especifico'],"estado_usuario":0},{"$set":objeto})
                    res = "OK"
                else :
                    res = "FAIL"
                #Guardar en Log 
                log =procesar_log("Se reestablece el usuario :  ",usuario_data['id_usuario'],usuario_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if usuario_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":datetime.now()}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def cambiar_pass(usuario_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1,"usuario_id":usuario_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>datetime.now() :
            #realizar secuencia para cambiar estado 0 
            objeto = {"clave_proyecto":usuario_data['nuevo_pass'],"user_m":usuario_data['id_usuario'],"updated_at":datetime.now()}   
            especifico = await usuarios_collection.find_one({"id_usuario":usuario_data['id_usuario'],"clave_proyecto":usuario_data['pass_actual'], "estado_usuario":1},{"_id":0 ,"user_proyecto":1})             
            if especifico and (usuario_data['nuevo_pass']==usuario_data['nuevo_pass_2']):
                especifico_ok = await usuarios_collection.update_one({"id_usuario":usuario_data['id_usuario'],"estado_usuario":1},{"$set":objeto})
                res = "OK"
            else :
                res = "FAIL"
            #Guardar en Log 
            log =procesar_log("Se cambia pass de  el usuario :  ",usuario_data['id_usuario'],especifico['user_proyecto'])
            guardar_log = await log_general_collection.insert_one(log)
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if usuario_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return res
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":datetime.now()}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def reestablecer_pass(usuario_data: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1,"usuario_id":usuario_data['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>datetime.now() :
            if usuario_data['especifico'] and (usuario_data['tipo_usuario']==1) :
                #realizar secuencia para cambiar estado 0 
                especifico = await usuarios_collection.find_one({"id_usuario":usuario_data['especifico'],"estado_usuario":1},{"_id":0 ,"user_proyecto":1})         
                if especifico :
                    new_pass = "@"+especifico['user_proyecto']
                    hash_pass = hashlib.sha256(new_pass.encode()).hexdigest()
                    objeto = {"clave_proyecto":hash_pass,"user_m":usuario_data['id_usuario'],"updated_at":datetime.now()}  
                    especifico_ok = await usuarios_collection.update_one({"id_usuario":usuario_data['especifico'],"estado_usuario":1},{"$set":objeto})
                    res = "OK"
                else :
                    res = "FAIL"
                #Guardar en Log 
                log =procesar_log("PASS RESETEADA de el usuario :  ",usuario_data['id_usuario'],usuario_data['especifico'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if usuario_data['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":usuario_data['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":datetime.now()}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def aperturar_reportes_en_proyecto(proyecto_data: dict) -> dict:
    return "hola"




