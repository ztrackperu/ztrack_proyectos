# ztrack_proyectos
pip install --upgrade motor pymongo

# iniciar dokcer 
docker-compose up --build


pip install cryptography

pip install pycryptodome


Iniciar esquema virtual y avanzar 
->ejecutar entorno virtual en windows
myTest\Scripts\activate
->ejecutar entorno virtual en en linux
source myTest/bin/activate

python app/main.py


------------
# sin docker 
->instalar venv en pyhton (myTest) nombre de entorno virtual
python3 -m venv myTest
->ejecutar entorno virtual en windows
myTest\Scripts\activate
->ejecutar entorno virtual en en linux
source myTest/bin/activate
-> cade vez que haya un archivo con requerimientos se ejecuta de esta manera
pip install -r requirements.txt
-> se requiere crear .env
especificando la conexion a la base de datos
MONGO_DETAILS="mongodb://localhost:27017"
#importante para API con mysql 

pip install mysqlclient
pip install sqlalchemy
pip install pymysql


pip install mysqlclient
pip install sqlalchemy
pip install pymysql
pip install python-dotenv
#para paginacion
pip install fastapi-pagination
#para todo s 
pip install "fastapi[all]"
-> se ejecuta 
python app/main.py

