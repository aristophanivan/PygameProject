import sqlite3

class database():
    def __init__(self):
        conn = sqlite3.connect('leaderboard.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                last_wave INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def save_player_progress(self, name, last_wave):
        conn = sqlite3.connect('leaderboard.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO players (name, last_wave) VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET last_wave=excluded.last_wave
        ''', (name, last_wave))
        conn.commit()
        conn.close()
        
    def get_player_progress(self):
        conn = sqlite3.connect('leaderboard.db')
        cursor = conn.cursor()
        rows = cursor.execute('''SELECT name, last_wave FROM players''').fetchall()
        conn.close()
        data = {player: score for player, score in rows}
        return data

