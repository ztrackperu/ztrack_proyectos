import hashlib
import json
#from server.database import collection 
from server.database import database_mongo ,client,collection
from datetime import datetime,timedelta

#Estanadar para funciones de agregar , editar , buscar , listar 
token_proyecto_collection =  collection("token_proyecto")
log_general_collection =  collection("log_general")
re_actividad_validacion_collection = collection("re_actividad_validacion")
pre_validacion_collection = collection("pre_validacion")
pre_actividad_collection = collection("pre_actividad")
ids_collection = collection("ids_proyectos")
h_re_actividad_validacion_collection = collection("h_re_actividad_validacion")
fecha_actual =datetime.now()

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
    """Filtra y devuelve solo los elementos del diccionario que no tienen valores None."""
    return {k: v for k, v in data.items() if v is not None}

def validar_formato(data):

    if isinstance(data, dict):  # Verificar que sea un diccionario
        if set(data.keys()) == {"pre_validacion_id", "unidad_pre_validacion","valor_pre_validacion","rango_pre_validacion"}:  # Verificar claves exactas
            if isinstance(data["pre_validacion_id"], int) and isinstance(data["valor_pre_validacion"], int):  # Verificar valores
                return True
    return False

def validar_formato_editar(data):
    print("----")
    print(data)
    print("-----")
    if isinstance(data, dict):  # Verificar que sea un diccionario
        if set(data.keys()) == {"id_re_actividad_validacion","unidad_pre_validacion","pre_validacion_id", "valor_pre_validacion","rango_pre_validacion"}:  # Verificar claves exactas
            if isinstance(data["id_re_actividad_validacion"], int) and isinstance(data["pre_validacion_id"], int) and isinstance(data["valor_pre_validacion"], int):  # Verificar valores
                return True
    return False


async def guardar_re_actividad_validacion(re_actividad_validacion: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1,"usuario_id":re_actividad_validacion['user_c']},{"_id":0})
    if validar_token and re_actividad_validacion['user_c']:
        if validar_token['fecha_fin']>fecha_actual :
            token_data =re_actividad_validacion['token_proyecto']            
            proyecto_ok ="FAIL"
            #hacer las validaciones del fomato para insertar 
            #verificamos que el pre_actividad_id exista 
            paso_uno = await pre_actividad_collection.find_one({"id_pre_actividad":re_actividad_validacion['pre_actividad_id'],"estado_pre_actividad":1 },{"_id":0,"id_pre_actividad":1,"nombre_pre_actividad":1})
            if paso_uno :
                #analizamos que se un array y cuantos elementos tiene 
                contar_conjunto = len(re_actividad_validacion['conjunto']) 
                if contar_conjunto>0 :
                    # verificamos que los json cumplan con el formato , para eso debemos navegar el array
                    print(re_actividad_validacion['conjunto'])
                    suma_pre_actividad =0

                    for valor in re_actividad_validacion['conjunto'] :
                        suma_pre_actividad +=int(valor['valor_pre_validacion'])
                    if (100-int(re_actividad_validacion['suma_valor_pre_actividad']))>=suma_pre_actividad :
                        #verificar que sea lo adecuado la suma , pedri laas relaciones
                        resultado_suma_validar =  re_actividad_validacion_collection.aggregate([
                            {"$match": {"estado_re_actividad_validacion": 1,"pre_actividad_id":re_actividad_validacion['pre_actividad_id']}},
                            {"$group": {"_id": None, "resultado_suma_validar": {"$sum": "$valor_pre_validacion"}}}
                        ])
                        resultado_sum = await resultado_suma_validar.to_list(length=1)
                        print(resultado_sum)
                        resultado_sum_ok =resultado_sum[0]['resultado_suma_validar'] if resultado_sum else 0
                        print("*****")
                        print(resultado_sum_ok)
                        print("*****")

                        if resultado_sum_ok==re_actividad_validacion['suma_valor_pre_actividad'] :
                            for elemento in re_actividad_validacion['conjunto'] :
                                print("*****elemento*****")
                                print(elemento)
                                valor_principal = validar_formato(elemento)
                                print("*****analisis***")
                                print(valor_principal)
                                if valor_principal :
                                    #for _ in range (int(elemento['cantidad'])):
                                    objeto_novo={}
                                    #consultar el id de re_actividad_validacion
                                    ids_proyectos = await ids_collection.find_one({"id_re_actividad_validacion": {"$exists": True}})
                                    objeto_novo['created_at'] = datetime.now() 
                                    objeto_novo['id_re_actividad_validacion'] = ids_proyectos['id_re_actividad_validacion']+1 if ids_proyectos else 1
                                    objeto_novo['pre_actividad_id'] = re_actividad_validacion['pre_actividad_id']
                                    objeto_novo['pre_validacion_id'] = elemento['pre_validacion_id']
                                    objeto_novo['valor_pre_validacion'] = elemento['valor_pre_validacion']
                                    objeto_novo['estado_re_actividad_validacion'] = 1
                                    objeto_novo['rango_pre_validacion'] = elemento['rango_pre_validacion']
                                    objeto_novo['unidad_pre_validacion'] = elemento['unidad_pre_validacion']
                                    objeto_novo['user_c'] = re_actividad_validacion['user_c']
                                    #insertar ese objeto 
                                    guardar_re_actividad_validacion= await re_actividad_validacion_collection.insert_one(objeto_novo)
                                    s_ids ={"id_re_actividad_validacion":objeto_novo['id_re_actividad_validacion'],"fecha":datetime.now()}
                                    procesar_ids = await ids_collection.update_one({"_id":ids_proyectos['_id'] },{"$set":s_ids}) if ids_proyectos else await ids_collection.insert_one(s_ids)
                                    #Guardar en historico
                                    relacion_directa = "actividad : "+str(objeto_novo['pre_actividad_id']) +" - " +" validacion : "+str(objeto_novo['pre_validacion_id'])
                                    re_actividad_validacion_historico = procesar_historico("RELACION actividad-validacion GUARDADO",re_actividad_validacion['user_c'],objeto_novo)
                                    guardar_re_actividad_validacion_historico = await h_re_actividad_validacion_collection.insert_one(re_actividad_validacion_historico)
                                    #Guardar en Log 
                                    log =procesar_log("RELACION actividad-validacion GUARDADO",re_actividad_validacion['user_c'],relacion_directa)
                                    guardar_log = await log_general_collection.insert_one(log)
                                    proyecto_ok ="ok"
                                else:
                                    return "MalFormato"
                        else :
                            return "ValSum"    
                    else :
                        return "FailSum"
                else :
                    return "FailRelacion"
            else :
                return "Fail"
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_actividad_validacion['user_c']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":token_data,"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return proyecto_ok
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN/USER"



async def editar_re_actividad_validacion(re_actividad_validacion: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1,"usuario_id":re_actividad_validacion['user_c']},{"_id":0})
    if validar_token and re_actividad_validacion['user_c']:
        if validar_token['fecha_fin']>fecha_actual :
            token_data =re_actividad_validacion['token_proyecto']            
            proyecto_ok ="FAIL"
            paso_uno = await pre_actividad_collection.find_one({"id_pre_actividad":re_actividad_validacion['pre_actividad_id'],"estado_pre_actividad":1 },{"_id":0,"id_pre_actividad":1,"nombre_pre_actividad":1})
            if paso_uno :
                #analizamos que se un array y cuantos elementos tiene 
                contar_conjunto = len(re_actividad_validacion['conjunto']) 
                if contar_conjunto>0 :
                    # verificamos que los json cumplan con el formato , para eso debemos navegar el array
                    print(re_actividad_validacion['conjunto'])
                    suma_pre_actividad =0
                    if 100>=suma_pre_actividad :
                        for elemento in re_actividad_validacion['conjunto'] :
                            print(elemento)
                            valor_principal = validar_formato_editar(elemento)
                            print(valor_principal)
                            if valor_principal :
                                #comparar para decidir editar 
                                objetoA = {"id_re_actividad_validacion":elemento['id_re_actividad_validacion'],"estado_re_actividad_validacion":1}
                                paso_analizar = await re_actividad_validacion_collection.find_one(objetoA,{"_id":0})
                                if objetoA :
                                    if paso_analizar['unidad_pre_validacion']==elemento['unidad_pre_validacion'] and paso_analizar['rango_pre_validacion']==elemento['rango_pre_validacion'] and paso_analizar['pre_validacion_id']==elemento['pre_validacion_id'] and paso_analizar['valor_pre_validacion']==elemento['valor_pre_validacion'] and paso_analizar['pre_actividad_id']==re_actividad_validacion['pre_actividad_id']:
                                        #no guardar
                                        print("sin modificaciones")
                                    else :
                                        #validar que rango_pre_validacion sea un array
                                        validar_lista = len(elemento['rango_pre_validacion'])
                                        print("jajajajaja")
                                        print(elemento['rango_pre_validacion'])

                                        if validar_lista==2 :
                                            #actualizar
                                            objetoB={"unidad_pre_validacion":elemento['unidad_pre_validacion'],"rango_pre_validacion":elemento['rango_pre_validacion'],"valor_pre_validacion":elemento['valor_pre_validacion'],"user_m":re_actividad_validacion['user_c'],"update_at":datetime.now()}
                                            actualizar_re = await re_actividad_validacion_collection.update_one(objetoA,{"$set":objetoB})
                                            #Guardar en historico
                                            relacion_directa = "proyecto : "+str(re_actividad_validacion['pre_actividad_id']) +" - " +" derivado : "+str(elemento['pre_validacion_id'])
                                            objetoB['id_re_actividad_validacion'] =elemento['id_re_actividad_validacion']
                                            re_actividad_validacion_historico = procesar_historico("RELACION actividad-validacion EDITADO",re_actividad_validacion['user_c'],objetoB)
                                            guardar_re_actividad_validacion_historico = await h_re_actividad_validacion_collection.insert_one(re_actividad_validacion_historico)
                                            #Guardar en Log 
                                            log =procesar_log("RELACION actividad-validacion  EDITADO",re_actividad_validacion['user_c'],relacion_directa)
                                            guardar_log = await log_general_collection.insert_one(log)
                                            proyecto_ok ="ok"
                                        else :
                                            return "ListaFail"
                                else :
                                    return "idFail"
                            else:
                                return "MalFormato"
                    else :
                        return "FailSum"
                else :
                    return "FailRelacion"
            else :
                return "Fail"
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_actividad_validacion['user_c']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":token_data,"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return proyecto_ok
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN/USER"

async def buscar_re(re_actividad_validacion: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1,"usuario_id":re_actividad_validacion['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            #consultar todas las relaciones disponibles
            if re_actividad_validacion['especifico_actividad'] :
                notificacions = []
                #Consultar proyecto 
                base = await pre_actividad_collection.find_one({"id_pre_actividad":re_actividad_validacion['especifico_actividad'],"estado_pre_actividad":1},{"_id":0})
                consulta_re ={'pre_actividad_id':re_actividad_validacion['especifico_actividad'],"estado_re_actividad_validacion":1}
                suma_pre_actividad =0
                async for notificacion in re_actividad_validacion_collection.find(consulta_re,{"_id":0}).sort({"created_at":-1}):
                    #consultar relacion
                    relacion = await pre_validacion_collection.find_one({"id_pre_validacion":notificacion['pre_validacion_id']},{"_id":0,"nombre_pre_validacion":1})
                    notificacion['nombre_pre_validacion']=relacion['nombre_pre_validacion']
                    notificacions.append(notificacion)
                    suma_pre_actividad +=int(notificacion['valor_pre_validacion'])
                res = {"pre_actividad":base['nombre_pre_actividad'] ,"descripcion":base['descripcion_pre_actividad'] ,"valor_pre_validacion":suma_pre_actividad,"resultado" :notificacions}
                #guardar en log
                log =procesar_log("LISTADO DE RE PROYECTOS POR ",re_actividad_validacion['id_usuario'],re_actividad_validacion['especifico_actividad'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_actividad_validacion['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"


async def eliminar_re(re_actividad_validacion: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1,"usuario_id":re_actividad_validacion['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            #consultar todas las relaciones disponibles
            if re_actividad_validacion['especifico_id']:
            #if re_actividad_validacion['especifico_actividad'] and re_actividad_validacion['derivado_actividad']and re_actividad_validacion['especifico_id']:
                #consulta_uno = {'id_re_actividad_validacion':re_actividad_validacion['especifico_id'],'pre_validacion_id':re_actividad_validacion['derivado_actividad'],'pre_actividad_id':re_actividad_validacion['especifico_actividad'],"estado_re_actividad_validacion":1}
                consulta_uno = {'id_re_actividad_validacion':re_actividad_validacion['especifico_id'],"estado_re_actividad_validacion":1}
                especifico = await re_actividad_validacion_collection.find_one(consulta_uno,{"_id":0})
                if especifico :
                    especifico_ok = await re_actividad_validacion_collection.update_one({"id_re_actividad_validacion":re_actividad_validacion['especifico_id'],"estado_re_actividad_validacion":1},{"$set":{"estado_re_actividad_validacion":0}})
                    res = "OK"
                else :
                    res = "FAIL"
                #guardar en log
                log =procesar_log("relacion proyecto-derivado ELIMINADO ",re_actividad_validacion['id_usuario'],re_actividad_validacion['especifico_id'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_actividad_validacion['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def listar(re_actividad_validacion: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1,"usuario_id":re_actividad_validacion['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            notificacions = []
            consulta_re ={'estado_pre_validacion':1}
            async for notificacion in pre_validacion_collection.find(consulta_re,{"_id":0}).sort({"created_at":-1}):
                notificacions.append(notificacion)
            res = {"resultado" :notificacions}       
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_actividad_validacion['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return res
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_actividad_validacion['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"
