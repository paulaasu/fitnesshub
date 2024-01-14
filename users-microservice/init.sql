-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS fitnesshubDB;

-- Seleccionar la base de datos
USE fitnesshubDB;

-- Crear la tabla users si no existe
CREATE TABLE IF NOT EXISTS users (
  user_id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  jwt_token VARCHAR(255) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS trainings (
    training_id INT PRIMARY KEY AUTO_INCREMENT,
    exercises VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    duration int
);

INSERT INTO trainings (exercises, name, duration) VALUES
('Push-ups, Squats, Plank', 'Full Body Workout', 30),
('Running, Lunges, Jumping Jacks', 'Cardio Blast', 20),
('Dumbbell Curls, Bench Press, Leg Press', 'Strength Training', 45),
('Yoga Poses', 'Yoga Session', 60);
('Burpees, Mountain Climbers, High Knees', 'HIIT Circuit', 25),
('Cycling, Elliptical, Rowing', 'Cardio Mix', 30),
('Deadlifts, Shoulder Press, Pull-ups', 'Powerlifting Focus', 40),
('Pilates Mat Exercises', 'Pilates Core Workout', 50);

CREATE TABLE IF NOT EXISTS completed_trainings(
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id int,
    training_id int,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (training_id) REFERENCES trainings(training_id)
);