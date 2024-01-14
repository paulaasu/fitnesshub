const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const router = express.Router();
const mysql = require('mysql2/promise'); // Asegúrate de tener instalado mysql2
const { MongoClient } = require('mongodb');

// Configuración de la conexión a la base de datos
const pool = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: 'deusto',
    database: 'fitnesshubDB',
    waitForConnections: true,
    connectionLimit: 20,
    queueLimit: 0,
    connectTimeout: 30000
});

// Configuración de la conexión a MongoDB
const mongoClient = new MongoClient("mongodb://127.0.0.1:27017", { useUnifiedTopology: true });
//const mongoClient = new MongoClient("mongodb://localhost:27017", { useUnifiedTopology: true });
let db;  // Variable para almacenar la instancia de la base de datos
let collection;  // Variable para almacenar la instancia de la colección

// Conexión a MongoDB
async function connectToMongoDB() {
    try {
        await mongoClient.connect();
        db = mongoClient.db('fitnesshubdb');
        collection = db.collection('user_queries');
        console.log('Connected to MongoDB');
    } catch (error) {
        console.error('Error connecting to MongoDB:', error);
    }
}

// Llamamos a la función para conectar a MongoDB al inicio
connectToMongoDB();

// Register user
/*router.post('/register', async (req, res) => {
    const { username, password, email } = req.body;

    try {
        // Check if the username already exists
        const [existingUsers] = await pool.query('SELECT * FROM users WHERE username = ?', [username]);

        if (existingUsers.length > 0) {
            // Username is already taken
            return res.status(400).send('Username is already taken');
        }
        print("prueba")

        // If the username is unique, proceed with the registration
        const hashedPassword = await bcrypt.hash(password, 10);
        await pool.query('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', [username, hashedPassword, email]);

        res.status(201).send('User registered successfully');
    } catch (error) {
        if (error.code === 'ER_DUP_ENTRY') {
            // Duplicate entry error
            print("USUARIO COGIDO!")
            console.log("USUARIO COGIDO!")
            res.status(400).send('Username or email is already taken');
        } else {
            console.error(error);
            res.status(500).send('Error during registration');
        }
    }
});*/
router.post('/register', async (req, res) => {
    const { username, password, email } = req.body;

    try {
        // Check if the username or email already exists
        const [existingUsers] = await pool.query('SELECT * FROM users WHERE username = ? OR email = ?', [username, email]);

        if (existingUsers.length > 0) {
            // Username or email is already taken
            return res.status(400).json({ error: 'Username or email is already taken' });
        }

        // If the username and email are unique, proceed with the registration
        const hashedPassword = await bcrypt.hash(password, 10);
        await pool.query('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', [username, hashedPassword, email]);

        res.status(201).json({ message: 'User registered successfully' });
    } catch (error) {
        if (error.code === 'ER_DUP_ENTRY') {
            // Duplicate entry error
            console.log("USUARIO COGIDO!")
            res.status(400).json({ error: 'Username or email is already taken' });
        } else {
            console.error(error);
            res.status(500).json({ error: 'Error during registration' });
        }
    }
});


router.post('/login', async (req, res) => {
    const { username, password } = req.body;

    try {
        const [results] = await pool.query('SELECT * FROM users WHERE username = ?', [username]);
        const user = results[0];

        if (user && await bcrypt.compare(password, user.password)) {
            try {
                await collection.insertOne({ username: user.username, activity: 'login', timestamp: new Date(), ip_address: req.ip });
            } catch (error) {
                console.error('Error inserting login document in MongoDB:', error);
            }
            
            const token = jwt.sign({ username: user.username }, 'secret');

            await pool.query('UPDATE users SET jwt_token = ? WHERE username = ?', [token, username]);
            
            res.json({ success: true, message: 'Login successful', token: token, user: user });
        } else {
            res.status(400).json({ success: false, message: 'Invalid credentials' });
        }
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Error during login' });
    }
});

router.post('/logout', async (req, res) => {
    const username = req.body.username; 

    try {
        // Actualizar la columna jwt_token a NULL (o algún valor especial) para invalidar el token
        await pool.query('UPDATE users SET jwt_token = NULL WHERE username = ?', [username]);
        try {
            await collection.insertOne({ username: username, activity: 'logout', timestamp: new Date(), ip_address: req.ip });
        } catch (error) {
            console.error('Error inserting logout document in MongoDB:', error);
        }
        res.json({ success: true, message: 'Logout successful' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Error during logout' });
    }
});

// Marcar un entrenamiento como completado para un usuario específico
router.post('/markCompletedTraining', async (req, res) => {
    const { user_id, training_id } = req.body;

    try {
        // Verificar si el usuario y el entrenamiento existen antes de insertar en la tabla
        const [userResults] = await pool.query('SELECT * FROM users WHERE user_id = ?', [user_id]);
        const [trainingResults] = await pool.query('SELECT * FROM trainings WHERE training_id = ?', [training_id]);

        if (userResults.length === 0 || trainingResults.length === 0) {
            return res.status(404).json({ success: false, message: 'User or training not found' });
        }

        // Insertar el registro en la tabla completed_trainings
        await pool.query('INSERT INTO completed_trainings (user_id, training_id) VALUES (?, ?)', [user_id, training_id]);

        res.status(200).json({ success: true, message: 'Training marked as completed' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Error marking training as completed' });
    }
});

// Verificar si un usuario ha completado un entrenamiento específico
router.post('/checkCompletedTraining', async (req, res) => {
    const { user_id, training_id } = req.body;

    try {
        // Verificar si el usuario y el entrenamiento existen en la tabla completed_trainings
        const [results] = await pool.query('SELECT * FROM completed_trainings WHERE user_id = ? AND training_id = ?', [user_id, training_id]);

        if (results.length > 0) {
            res.status(200).json({ success: true, message: 'User has completed the training' });
        } else {
            res.status(200).json({ success: false, message: 'User has not completed the training' });
        }
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Error checking completed training' });
    }
});

// Eliminar un entrenamiento completado para un usuario específico
router.delete('/deleteCompletedTraining', async (req, res) => {
    const { user_id, training_id } = req.body;

    try {
        // Verificar si el usuario y el entrenamiento existen antes de intentar eliminar el registro
        const [userResults] = await pool.query('SELECT * FROM users WHERE user_id = ?', [user_id]);
        const [trainingResults] = await pool.query('SELECT * FROM trainings WHERE training_id = ?', [training_id]);

        if (userResults.length === 0 || trainingResults.length === 0) {
            return res.status(404).json({ success: false, message: 'User or training not found' });
        }

        // Eliminar el registro en la tabla completed_trainings
        await pool.query('DELETE FROM completed_trainings WHERE user_id = ? AND training_id = ?', [user_id, training_id]);

        res.status(200).json({ success: true, message: 'Completed training deleted successfully' });
    } catch (error) {
        console.error(error);
        res.status(500).json({ success: false, message: 'Error deleting completed training' });
    }
});



module.exports = router;

module.exports = router;

