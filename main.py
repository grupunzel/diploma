from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.responses import JSONResponse
from backend.config.settings import settings
from backend.config.logger import logger
import asyncio
import os
import sqlite3

# app = FastAPI()

def init_db():
    if os.path.exists('ITest.db'):
        logger.info("Database already exists")
        return
    
    with sqlite3.connect('ITest.db') as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        password TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
                         )
        
        db.execute("""
        CREATE TABLE IF NOT EXISTS TestQuestions (
        question_id INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        module TEXT,
        type TEXT,
        question TEXT,
        answers TEXT DEFAULT NULL,
        right_answer TEXT DEFAULT NULL,
        user_answer TEXT DEFAULT NULL,
        file_answer_path TEXT DEFAULT NULL,
        score INTEGER DEFAULT 10,
        score_earned INTEGER DEFAULT 0,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        end_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE
        )
        """
                         )
        
        db.execute("""
        CREATE TABLE IF NOT EXISTS UserProgress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        test_id INTEGER,
        total_score INTEGER,
        max_score INTEGER,
        percentage INTEGER,
        report TEXT,
        FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
        FOREIGN KEY(test_id) REFERENCES TestQuestions(test_id) ON DELETE CASCADE
        )
        """
                         )
        
        db.commit()


def main():
    init_db()


if __name__ == "__main__":
    main()