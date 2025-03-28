from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


#from server.routes.datos import router as DatosRouter

from server.routes.proyectos import router as ProyectosRouter
from server.routes.usuarios import router as UsuariosRouter
from server.routes.pre_proyecto import router as PreProyectoRouter
from server.routes.pre_derivado import router as PreDerivadoRouter
from server.routes.pre_actividad import router as PreActividadRouter
from server.routes.pre_validacion import router as PreValidacionRouter
from server.routes.re_proyecto_derivado import router as ReProyectoDerivadoRouter
from server.routes.re_derivado_actividad import router as ReDerivadoActividadRouter
from server.routes.re_actividad_validacion import router as ReActividadValidacionRouter
from server.routes.pollitos.operaciones import router as PollitosOperacionesRouter



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
app.include_router(PreProyectoRouter, tags=["PreProyecto"], prefix="/PreProyecto")
app.include_router(PreDerivadoRouter, tags=["PreDerivado"], prefix="/PreDerivado")
app.include_router(PreActividadRouter, tags=["PreActividad"], prefix="/PreActividad")
app.include_router(PreValidacionRouter, tags=["PreValidacion"], prefix="/PreValidacion")
app.include_router(ReProyectoDerivadoRouter, tags=["ReProyectoDerivado"], prefix="/ReProyectoDerivado")
app.include_router(ReDerivadoActividadRouter, tags=["ReDerivadoActividad"], prefix="/ReDerivadoActividad")
app.include_router(ReActividadValidacionRouter, tags=["ReActividadValidacion"], prefix="/ReActividadValidacion")
app.include_router(PollitosOperacionesRouter, tags=["PollitosOperaciones"], prefix="/PollitosOperaciones")







@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to this fantastic app ztrack by test!"}
