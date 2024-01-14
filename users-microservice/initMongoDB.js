// Importa el cliente de MongoDB
const { MongoClient } = require('mongodb');

// URL de conexión a la base de datos MongoDB
const mongoURL = 'mongodb://127.0.0.1:27017';

// Nombre de la base de datos
const dbName = 'fitnesshubdb';

// Nombre de la colección
const collectionName = 'user_queries';

// Función para inicializar la colección en MongoDB
async function initializeMongoDBCollection() {
    // Crea una instancia del cliente de MongoDB
    const client = new MongoClient(mongoURL, { useNewUrlParser: true, useUnifiedTopology: true });

    try {
        // Conecta al servidor de MongoDB
        await client.connect();

        // Obtiene una referencia a la base de datos
        const db = client.db(dbName);

        // Crea la base de datos 'fitnesshubdb' si no existe
        await db.command({ create: dbName });

        // Crea la colección 'user_queries' si no existe
        await db.createCollection(collectionName);

        console.log(`Collection '${collectionName}' initialized successfully`);
    } catch (error) {
        console.error('Error initializing MongoDB collection:', error);
    } finally {
        // Cierra la conexión al cliente de MongoDB
        await client.close();
    }
}

// Ejecuta la función de inicialización
initializeMongoDBCollection();
