import json
#from server.database import collection 
from server.database import database_mongo ,client,collection
from datetime import datetime,timedelta

#Estanadar para funciones de agregar , editar , buscar , listar 
#proyectos_collection = database_mongo["proyectos"]
#proyectos_collection = collection("proyectos")

fecha_actual =datetime.now()
#ids generales en collecion ids_proyectos
#ids_collection = database_mongo["ids_proyectos"]
#ids_collection = collection("ids_proyectos")


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
    
async def guardar_proyectos(proyecto_data: dict) -> dict:
    #validar id_proyecto sino existe asumir que es 0 por lo que es una funcion de guardado 
    print("--------------")
    print(proyecto_data)
    print("--------------")
    proyectos_collection = collection("proyectos")
    ids_collection = collection("ids_proyectos")

    #proyectos_collection = database_mongo["proyectos"]
    #ids_collection = database_mongo["ids_proyectos"]


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

            #Guardar en Log 

    else : 
        #se actualiza la informacion 
        proyecto_data['updated_at']=fecha_actual
        filter_proyecto = {k: v for k, v in proyecto_data.items() if k not in ['id_proyecto', 'user_c','activar_reportar']}
        actualizar_proyecto = await proyectos_collection.update_one({"id_proyecto": proyecto_data['id_proyecto'],"estado":1},{"$set":proyecto_data}) 
        proyecto_ok = {"id_proyecto":proyecto_data['id_proyecto'],"nombre_proyecto":proyecto_data['id_proyecto']}
    return proyecto_ok

async def aperturar_reportes_en_proyecto(proyecto_data: dict) -> dict:
    return "hola"




