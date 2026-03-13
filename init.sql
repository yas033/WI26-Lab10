-- Create database
CREATE DATABASE IF NOT EXISTS guessgame;

-- Use the database
USE guessgame;

-- Create scores table
CREATE TABLE IF NOT EXISTS scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    attempts INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);