import hashlib
import json
#from server.database import collection 
from server.database import database_mongo ,client,collection
from datetime import datetime,timedelta

#Estanadar para funciones de agregar , editar , buscar , listar 
token_proyecto_collection =  collection("token_proyecto")
log_general_collection =  collection("log_general")
re_derivado_actividad_collection = collection("re_derivado_actividad")
pre_actividad_collection = collection("pre_actividad")
pre_derivado_collection = collection("pre_derivado")
ids_collection = collection("ids_proyectos")
h_re_derivado_actividad_collection = collection("h_re_derivado_actividad")
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
        if set(data.keys()) == {"pre_actividad_id", "valor_pre_actividad","requisito_pre_actividad"}:  # Verificar claves exactas
            if isinstance(data["pre_actividad_id"], int) and isinstance(data["valor_pre_actividad"], int):  # Verificar valores
                return True
    return False

def validar_formato_editar(data):
    print("----")
    print(data)
    print("-----")
    if isinstance(data, dict):  # Verificar que sea un diccionario
        if set(data.keys()) == {"id_re_derivado_actividad","pre_actividad_id", "valor_pre_actividad","requisito_pre_actividad"}:  # Verificar claves exactas
            if isinstance(data["id_re_derivado_actividad"], int) and isinstance(data["pre_actividad_id"], int) and isinstance(data["valor_pre_actividad"], int):  # Verificar valores
                return True
    return False

def analisis_lista(l1,l2):
    if l1 != []:
        if isinstance(l1, list) and l1:  
            # Validar si todos los elementos de `l1` están en `l2`
            if set(l1).issubset(set(l2)):
                return True
                #print("✅ Todos los elementos de 'l1' están en 'l2'.")
            else:
                return False
            # print("❌ Algunos elementos de 'l1' no están en 'l2'.")
        else:
            return True
            #print("⚠️ 'l1' no es una lista o está vacía.")
    else :
        return True


async def guardar_re_derivado_actividad(re_derivado_actividad: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1,"usuario_id":re_derivado_actividad['user_c']},{"_id":0})
    if validar_token and re_derivado_actividad['user_c']:
        if validar_token['fecha_fin']>fecha_actual :
            token_data =re_derivado_actividad['token_proyecto']            
            proyecto_ok ="FAIL"
            #hacer las validaciones del fomato para insertar 
            #verificamos que el pre_derivado_id exista 
            paso_uno = await pre_derivado_collection.find_one({"id_pre_derivado":re_derivado_actividad['pre_derivado_id'],"estado_pre_derivado":1 },{"_id":0,"id_pre_derivado":1,"nombre_pre_derivado":1})
            if paso_uno :
                #analizamos que se un array y cuantos elementos tiene 
                contar_conjunto = len(re_derivado_actividad['conjunto']) 
                if contar_conjunto>0 :
                    # verificamos que los json cumplan con el formato , para eso debemos navegar el array
                    print(re_derivado_actividad['conjunto'])
                    suma_pre_derivado =0

                    for valor in re_derivado_actividad['conjunto'] :
                        suma_pre_derivado +=int(valor['valor_pre_actividad'])
                    if (100-int(re_derivado_actividad['suma_valor_pre_derivado']))>=suma_pre_derivado :
                        #verificar que sea lo adecuado la suma , pedri laas relaciones
                        resultado_suma_validar =  re_derivado_actividad_collection.aggregate([
                            {"$match": {"estado_re_derivado_actividad": 1,"pre_derivado_id":re_derivado_actividad['pre_derivado_id']}},
                            {"$group": {"_id": None, "resultado_suma_validar": {"$sum": "$valor_pre_actividad"}}}
                        ])
                        resultado_sum = await resultado_suma_validar.to_list(length=1)
                        print(resultado_sum)
                        resultado_sum_ok =resultado_sum[0]['resultado_suma_validar'] if resultado_sum else 0
                        print("*****")
                        print(resultado_sum_ok)
                        print("*****")

                        if resultado_sum_ok==re_derivado_actividad['suma_valor_pre_derivado'] :
                            for elemento in re_derivado_actividad['conjunto'] :
                                print("*****elemento*****")
                                print(elemento)
                                valor_principal = validar_formato(elemento)
                                print("*****analisis***")
                                print(valor_principal)
                                if valor_principal :
                                    #for _ in range (int(elemento['cantidad'])):
                                    objeto_novo={}
                                    #consultar el id de re_derivado_actividad
                                    ids_proyectos = await ids_collection.find_one({"id_re_derivado_actividad": {"$exists": True}})
                                    objeto_novo['created_at'] = datetime.now() 
                                    objeto_novo['id_re_derivado_actividad'] = ids_proyectos['id_re_derivado_actividad']+1 if ids_proyectos else 1
                                    objeto_novo['pre_derivado_id'] = re_derivado_actividad['pre_derivado_id']
                                    objeto_novo['pre_actividad_id'] = elemento['pre_actividad_id']
                                    objeto_novo['valor_pre_actividad'] = elemento['valor_pre_actividad']
                                    objeto_novo['estado_re_derivado_actividad'] = 1
                                    objeto_novo['requisito_pre_actividad'] = elemento['requisito_pre_actividad']
                                    objeto_novo['user_c'] = re_derivado_actividad['user_c']
                                    #insertar ese objeto 
                                    guardar_re_derivado_actividad= await re_derivado_actividad_collection.insert_one(objeto_novo)
                                    s_ids ={"id_re_derivado_actividad":objeto_novo['id_re_derivado_actividad'],"fecha":datetime.now()}
                                    procesar_ids = await ids_collection.update_one({"_id":ids_proyectos['_id'] },{"$set":s_ids}) if ids_proyectos else await ids_collection.insert_one(s_ids)
                                    #Guardar en historico
                                    relacion_directa = "derivado : "+str(objeto_novo['pre_derivado_id']) +" - " +" actividad : "+str(objeto_novo['pre_actividad_id'])
                                    re_derivado_actividad_historico = procesar_historico("RELACION derivado-actividad GUARDADO",re_derivado_actividad['user_c'],objeto_novo)
                                    guardar_re_derivado_actividad_historico = await h_re_derivado_actividad_collection.insert_one(re_derivado_actividad_historico)
                                    #Guardar en Log 
                                    log =procesar_log("RELACION derivado-actividad GUARDADO",re_derivado_actividad['user_c'],relacion_directa)
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
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_derivado_actividad['user_c']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":token_data,"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return proyecto_ok
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN/USER"

async def editar_re_derivado_actividad(re_derivado_actividad: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1,"usuario_id":re_derivado_actividad['user_c']},{"_id":0})
    if validar_token and re_derivado_actividad['user_c']:
        if validar_token['fecha_fin']>fecha_actual :
            token_data =re_derivado_actividad['token_proyecto']            
            proyecto_ok ="FAIL"
            paso_uno = await pre_derivado_collection.find_one({"id_pre_derivado":re_derivado_actividad['pre_derivado_id'],"estado_pre_derivado":1 },{"_id":0,"id_pre_derivado":1,"nombre_pre_derivado":1})
            if paso_uno :
                #analizamos que se un array y cuantos elementos tiene 
                contar_conjunto = len(re_derivado_actividad['conjunto']) 
                if contar_conjunto>0 :
                    # verificamos que los json cumplan con el formato , para eso debemos navegar el array
                    print(re_derivado_actividad['conjunto'])
                    suma_pre_derivado =0
                    valores_id =[]
                    for valor in re_derivado_actividad['conjunto'] :
                        suma_pre_derivado +=int(valor['valor_pre_actividad'])
                        valores_id.append(valor['id_re_derivado_actividad'])
                    if 100>=suma_pre_derivado :
                        for elemento in re_derivado_actividad['conjunto'] :
                            print(elemento)
                            valor_principal = validar_formato_editar(elemento)
                            print(valor_principal)
                            if valor_principal :
                                #comparar para decidir editar 
                                objetoA = {"id_re_derivado_actividad":elemento['id_re_derivado_actividad'],"estado_re_derivado_actividad":1}
                                paso_analizar = await re_derivado_actividad_collection.find_one(objetoA,{"_id":0})
                                if objetoA :
                                    if paso_analizar['requisito_pre_actividad']==elemento['requisito_pre_actividad'] and paso_analizar['pre_actividad_id']==elemento['pre_actividad_id'] and paso_analizar['valor_pre_actividad']==elemento['valor_pre_actividad'] and paso_analizar['pre_derivado_id']==re_derivado_actividad['pre_derivado_id']:
                                        #no guardar
                                        print("sin modificaciones")
                                    else :
                                        #validar que requisito_pre_actividad sea un array
                                        validar_lista = analisis_lista(elemento['requisito_pre_actividad'],valores_id)
                                        print("jajajajaja")
                                        print(elemento['requisito_pre_actividad'])
                                        print("jajajajaja")
                                        print(valores_id)
                                        print("jajajajaja")

                                        if validar_lista :
                                            #actualizar
                                            objetoB={"requisito_pre_actividad":elemento['requisito_pre_actividad'],"valor_pre_actividad":elemento['valor_pre_actividad'],"user_m":re_derivado_actividad['user_c'],"update_at":datetime.now()}
                                            actualizar_re = await re_derivado_actividad_collection.update_one(objetoA,{"$set":objetoB})
                                            #Guardar en historico
                                            relacion_directa = "proyecto : "+str(re_derivado_actividad['pre_derivado_id']) +" - " +" derivado : "+str(elemento['pre_actividad_id'])
                                            objetoB['id_re_derivado_actividad'] =elemento['id_re_derivado_actividad']
                                            re_derivado_actividad_historico = procesar_historico("RELACION derivado-actividad EDITADO",re_derivado_actividad['user_c'],objetoB)
                                            guardar_re_derivado_actividad_historico = await h_re_derivado_actividad_collection.insert_one(re_derivado_actividad_historico)
                                            #Guardar en Log 
                                            log =procesar_log("RELACION derivado-actividad  EDITADO",re_derivado_actividad['user_c'],relacion_directa)
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
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_derivado_actividad['user_c']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":token_data,"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return proyecto_ok
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN/USER"

async def buscar_re(re_derivado_actividad: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1,"usuario_id":re_derivado_actividad['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            #consultar todas las relaciones disponibles
            if re_derivado_actividad['especifico_derivado'] :
                notificacions = []
                #Consultar proyecto 
                base = await pre_derivado_collection.find_one({"id_pre_derivado":re_derivado_actividad['especifico_derivado'],"estado_pre_derivado":1},{"_id":0})
                consulta_re ={'pre_derivado_id':re_derivado_actividad['especifico_derivado'],"estado_re_derivado_actividad":1}
                suma_pre_derivado =0
                async for notificacion in re_derivado_actividad_collection.find(consulta_re,{"_id":0}).sort({"created_at":-1}):
                    #consultar relacion
                    relacion = await pre_actividad_collection.find_one({"id_pre_actividad":notificacion['pre_actividad_id']},{"_id":0,"nombre_pre_actividad":1})
                    notificacion['nombre_pre_actividad']=relacion['nombre_pre_actividad']
                    notificacions.append(notificacion)
                    suma_pre_derivado +=int(notificacion['valor_pre_actividad'])
                res = {"pre_derivado":base['nombre_pre_derivado'] ,"descripcion":base['observaciones_pre_derivado'] ,"valor_pre_actividad":suma_pre_derivado,"resultado" :notificacions}
                #guardar en log
                log =procesar_log("LISTADO DE RE PROYECTOS POR ",re_derivado_actividad['id_usuario'],re_derivado_actividad['especifico_derivado'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_derivado_actividad['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"


async def eliminar_re(re_derivado_actividad: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1,"usuario_id":re_derivado_actividad['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            #consultar todas las relaciones disponibles
            if re_derivado_actividad['especifico_id']:
            #if re_derivado_actividad['especifico_derivado'] and re_derivado_actividad['derivado_actividad']and re_derivado_actividad['especifico_id']:
                #consulta_uno = {'id_re_derivado_actividad':re_derivado_actividad['especifico_id'],'pre_actividad_id':re_derivado_actividad['derivado_actividad'],'pre_derivado_id':re_derivado_actividad['especifico_derivado'],"estado_re_derivado_actividad":1}
                consulta_uno = {'id_re_derivado_actividad':re_derivado_actividad['especifico_id'],"estado_re_derivado_actividad":1}
                especifico = await re_derivado_actividad_collection.find_one(consulta_uno,{"_id":0})
                if especifico :
                    especifico_ok = await re_derivado_actividad_collection.update_one({"id_re_derivado_actividad":re_derivado_actividad['especifico_id'],"estado_re_derivado_actividad":1},{"$set":{"estado_re_derivado_actividad":0}})
                    res = "OK"
                else :
                    res = "FAIL"
                #guardar en log
                log =procesar_log("relacion proyecto-derivado ELIMINADO ",re_derivado_actividad['id_usuario'],re_derivado_actividad['especifico_id'])
                guardar_log = await log_general_collection.insert_one(log)
                #actualizar vida de token 
                tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_derivado_actividad['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
                extender_token = await token_proyecto_collection.update_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
                return res
            else :
                return "SIN_ESPECIFICO"
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"

async def listar(re_derivado_actividad: dict) -> dict:
    validar_token = await token_proyecto_collection.find_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1,"usuario_id":re_derivado_actividad['id_usuario']},{"_id":0})
    if validar_token :
        if validar_token['fecha_fin']>fecha_actual :
            notificacions = []
            consulta_re ={'estado_pre_actividad':1}
            async for notificacion in pre_actividad_collection.find(consulta_re,{"_id":0}).sort({"created_at":-1}):
                notificacions.append(notificacion)
            res = {"resultado" :notificacions}       
            #actualizar vida de token 
            tiempo_extendido =validar_token['fecha_fin'] + timedelta(minutes=30) if re_derivado_actividad['id_usuario']==1 else datetime.now() + timedelta(minutes=30)
            extender_token = await token_proyecto_collection.update_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1},{"$set":{"fecha_fin":tiempo_extendido}}) 
            return res
        else :
            #cancelar el token 
            invalidar_token = await token_proyecto_collection.update_one({"token_proyecto":re_derivado_actividad['token_proyecto'],"estado_token":1},{"$set":{"estado_token":0,"fecha_invalidar":fecha_actual}}) 
            return "TOKEN_INVALIDO"
    else :
        #no hay token valido 
        return "TOKEN_INVALIDO"
