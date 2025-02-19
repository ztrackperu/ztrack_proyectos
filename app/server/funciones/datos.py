import json
from server.database import collection ,collectionTotal
from bson import regex
from datetime import datetime,timedelta
#from fastapi_pagination.ext.motor import paginate
#import mysql.connector


def bd_gene(imei):
    fet =datetime.now()
    #part = fet.strftime('%d_%m_%Y')
    part = fet.strftime('_%m_%Y')
    colect ="D_"+imei+part
    return colect

async def Guardar_Datos(ztrack_data: dict) -> dict:
    #dat = ztrack_data['fecha']
    fet =datetime.now()
    #part = fet.strftime('%d_%m_%Y')
    #colect ="Datos_"+part
    #print(colect)
    ztrack_data['fecha_recepcion'] = fet
    #print(ztrack_data)
    comando ="sin comandos pendientes"
    Hay_dispositivo=""
    #COLECCION ESPECIFICA PARA DISPOSITIVO
    data_collection = collection(bd_gene(ztrack_data['IMEI']))
    #COLECCION PARA TODOS LOS DISPOSITIVOS
    dispositivos_collection = collection(bd_gene('dispositivos'))
    #AQUI SE GUARDA LA TRAMA 
    notificacion = await data_collection.insert_one(ztrack_data)

    new_notificacion = await data_collection.find_one({"_id": notificacion.inserted_id},{"_id":0})
    #Verificar que exista el dispositivo en el registro
    dispositivo_encontrado = await dispositivos_collection.find_one({"imei": ztrack_data['IMEI'],"estado":1},{"_id":0})
    
    if dispositivo_encontrado is not None:
        try:
            Hay_dispositivo= dispositivo_encontrado['imei'] 
            print("Elemento encontrado")
        except ValueError:
            print("NO SE ENCONTRO CONTROL")
    verificar_dispositivo = await dispositivos_collection.update_one({"imei": ztrack_data['IMEI'],"estado":1},{"$set":{"ultimo_dato":fet}}) if Hay_dispositivo else await dispositivos_collection.insert_one({"imei":ztrack_data['IMEI'],"estado":1,"fecha":fet})
    #if control_encontrado['comando'] :

    return comando

async def retrieve_datos(imei: str):
    notificacions = []
    data_collection = collection(bd_gene(imei))
    async for notificacion in data_collection.find({"estado":1},{"_id":0}):
        #print(notificacion)
        notificacions.append(notificacion)
    return notificacions

async def retrieve_datos_e():
    notificacions = []
    data_collection = collection(bd_gene())
    async for notificacion in data_collection.find({"estado":1},{"_id":0}):
        #print(notificacion)
        notificacions.append(notificacion)
    return notificacions


async def retrieve_datos_unico(imei: str):
    notificacions = []
    data_collection = collection(bd_gene(imei))
    async for notificacion in data_collection.find({"estado":1},{"_id":0}).sort({"fecha_recepcion":-1}).limit(1):
        #print(notificacion)
        notificacions.append(notificacion)
    return notificacions


def procesar_texto(texto):
    # Dividir el texto en partes separadas por "_"
    partes = texto.split("_") 
    # Convertir cada parte a mayúsculas para capitalizar las palabras
    partes_capitalizadas = [parte.capitalize() for parte in partes]   
    # Unir las partes con espacios en blanco
    texto_procesado = " ".join(partes_capitalizadas) 
    return texto_procesado

# import all you need from fastapi-pagination

async def config(empresa :int):
    notificacions=[]
    database =collection["config_ztrack"]
    empresa_config= database.get_collection("empresa_config")
    async for mad in empresa_config.find({"user_id":empresa},{"_id":0}):
        notificacions.append(mad)
    #se debe extraer el primir resultado
    return notificacions[0]

async def data_madurador(notificacion_data: dict) -> dict:
    #pedir la ultima conexion 
    #ultima conexion pedir mes y año 
                                                                                                                                                                         
    #construir base de datos 
    #database = client.intranet
    per = notificacion_data['ultima'].split('T')
    #ARRAY 0 represnta la fecha y 1 la hora
    periodo = per[0].split('-')
    #periodo 0 , es el año , 1 es el mes , 2 es el dia 
    #armamos la base de datos 
    bd = notificacion_data['device']+"_"+str(int(periodo[1]))+"_"+periodo[0]
    database = client[bd]
    #print(bd)
    #print("olitas")
    #print(notificacion_data['empresa'])
    #print(notificacion_data['page'])
    #print(notificacion_data['size'])
    madurador = database.get_collection("madurador")
    #notificacion_collection = collection("notificaciones")
    page=notificacion_data['page']
    limit=notificacion_data['size']
    empresa =notificacion_data['empresa']
    #esquema para consultar data 
    dataConfig =await config(empresa)
    #print(dataConfig)
    #print(dataConfig['config_data'])
    #print(dataConfig['config_graph'])
    #result = madurador.find({ "$and": [{"created_at": {"$gte": datetime.fromisoformat("2024-05-07T00:00:00.000Z")}},{"created_at": {"$lte": datetime.fromisoformat("2024-05-09T23:59:59.999Z")}}]},{"_id":0})                                
    #esquema con agregation para mayor versatilidad
    if(notificacion_data['fechaF']=="0" and notificacion_data['fechaI']=="0"):
        fechaF = datetime.fromisoformat(notificacion_data['ultima'])
        one_day = timedelta(hours=12)
        fechaI = fechaF-one_day
        #print(certeza)
        #print(certeza1)
    else : 
        fechaI=datetime.fromisoformat(notificacion_data['fechaI'])
        fechaF=datetime.fromisoformat(notificacion_data['fechaF'])
    print(fechaI)
    print(fechaF)

    pip = [
        {"$match": {
                "$and":[
                    {"created_at": {"$gte": fechaI}},
                    {"created_at": {"$lte": fechaF}}
                ]
            }
        },  
        {"$project":dataConfig['config_data']},
        {"$skip" : (page-1)*limit},
        {"$limit" : limit},  
    ]

    #recorrer array y crear varaibles para insertar
    graph = dataConfig['config_graph']
    #print("baja")
    #print(graph)
    #print("alta")
    listas = {}
    cadena =[]
    for i in range(len(graph)):
        #print(graph[i]['label'])
        nombre_lista = f"{graph[i]['label']}"
        cadena.append(graph[i]['label'])
        lab = procesar_texto(graph[i]['label'])

        listas[nombre_lista] = {
            "data":[],
            "config":[lab,graph[i]['hidden'],graph[i]['color'],graph[i]['tipo']]
        }

    concepto_ots = []
    async for concepto_ot in madurador.aggregate(pip):
        #print(concepto_ot)
        concepto_ots.append(concepto_ot)
        for i in range(len(graph)):
           #dataConfig['config_graph'][i].append(concepto_ot[dataConfig['config_graph'][i]])
           #primerfiltro =depurar_coincidencia(concepto_ot[dato[i]])
           #if(primerfiltro!=None):
               #aqui evaluamos si sera filtro de temperatura , porcentaje , ety-avl, area
                #pu ="oli"
           
           dato =graph
           #print(dato)
           #listas[dato[i]].append(concepto_ot[dato[i]])
           listas[dato[i]['label']]["data"].append(depurar_coincidencia(concepto_ot[dato[i]['label']]))

           #print(concepto_ot[dato[i]])s
           #dato[i].append(concepto_ot[dato[i]])
        #print(concepto_ot['return_air'])
    #print(listas)
    listasT = {"graph":listas,"table":concepto_ots,"cadena":cadena}
    #print(listasT)

    return listasT

             





