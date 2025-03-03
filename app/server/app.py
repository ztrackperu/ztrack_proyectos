from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


#from server.routes.datos import router as DatosRouter

from server.routes.proyectos import router as ProyectosRouter
from server.routes.usuarios import router as UsuariosRouter

#from server.routes.receta import router as RecetasRouter

#from server.routes.proceso import router as ProcesosRouter
#from server.routes.supervisado import router as SupervisadosRouter
#from server.routes.control import router as ControlRouter

app = FastAPI(
    title="Integracion ZTRACK PROYECTOS GENERALES",
    summary="Modulos de datos bidireccional",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    #allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ProyectosRouter, tags=["Proyectos"], prefix="/Proyectos")
app.include_router(UsuariosRouter, tags=["Usuarios"], prefix="/Usuarios")

#app.include_router(ComandosRouter, tags=["Comandos"], prefix="/Comandos")
#app.include_router(RecetasRouter, tags=["Recetas"], prefix="/Recetas")
#app.include_router(ProcesosRouter, tags=["Procesos"], prefix="/Procesos")
#app.include_router(SupervisadosRouter, tags=["Supervisador"], prefix="/Supervisador")
#app.include_router(ControlRouter, tags=["Control"], prefix="/Control")


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app ztrack by test!"}
