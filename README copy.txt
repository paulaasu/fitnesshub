0) Software que se Necesita Instalar
Asegúrate de tener instalado lo siguiente:

Python: El lenguaje de programación principal para el backend de la aplicación. Puedes descargar e instalar Python desde python.org.
Node.js: El entorno de ejecución para JavaScript, necesario para ejecutar scripts y aplicaciones frontend. Descárgalo e instálalo desde nodejs.org.
npm (Node Package Manager): Se utiliza para gestionar las dependencias del proyecto, especialmente para las aplicaciones frontend. Se instala automáticamente junto con Node.js.
MySQL: El sistema de gestión de bases de datos relacional. Puedes descargar e instalar MySQL desde mysql.com.
MongoDB: La base de datos NoSQL utilizada para almacenar registros de actividad. Descárgalo e instálalo desde mongodb.com..


1) Start the microservice of users
cd users-microservice
npm install
npm install express bcryptjs jsonwebtoken swagger-ui-express yamljs
mysql -u <usuario> -p<contraseña> < init.sql
node initMongoDB.js
node server.js

2) Start the microservice of trainings
cd trainings-microservice
pip install flask
pip install mysql-connector-python
pip install -r requirements.txt
python main.py

3) Start the gateway
cd api-gateway
pip install fastapi uvicorn httpx
uvicorn main:app --reload --port 8080

HOLA