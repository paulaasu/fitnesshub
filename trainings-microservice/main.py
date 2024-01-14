from flask import Flask, request, jsonify
import mysql.connector
import logging

app = Flask(__name__)

# Configuración de la base de datos
db_config = {
    'host': 'localhost',  
    'user': 'root',
    'password': 'deusto',
    'database': 'fitnesshubdb',
}

# Inicializar la conexión a la base de datos
mysql = mysql.connector.connect(**db_config)
logging.basicConfig(level=logging.DEBUG)


@app.route('/getTrainings', methods=['GET'])
def get_trainings():
    logging.debug("Recibida solicitud para obtener entrenamientos.")
    try:
        cur = mysql.cursor(dictionary=True)
        cur.execute("SELECT * FROM trainings")
        trainings = cur.fetchall()
        cur.close()
        logging.debug("Entrenamientos obtenidos exitosamente.")
        print(trainings)
        return jsonify(trainings)
    except Exception as e:
        logging.error(f"Error al obtener entrenamientos: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/trainings/<int:training_id>', methods=['GET'])
def get_training(training_id):
    try:
        cur = mysql.cursor(dictionary=True)
        cur.execute("SELECT * FROM trainings WHERE training_id = %s", (training_id,))
        training = cur.fetchone()
        cur.close()
        if training:
            return jsonify(training)
        else:
            return jsonify({'error': 'Entrenamiento no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host="localhost", port=8001, debug=True)