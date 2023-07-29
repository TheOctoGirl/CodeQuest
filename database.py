import mariadb
import settings
import uuid
import random
import time

class Database:
    
    def connect():
        db = mariadb.connect(
            user=settings.db_user,
            password=settings.db_password,
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name
        )
        cur = db.cursor()
        return db, cur
    
    def add_challenge(server_id, start_time, end_time, use_auto_generated_challenge=False, title=None, description=None, challenge_id=None):
        
        if use_auto_generated_challenge == False:
            challenge_id = str(uuid.uuid4())
            db, cur = Database.connect()
            cur.execute("INSERT INTO challenges (challenge_id, server_id, start_time, end_time, challenge_title, challenge_text) VALUES (?, ?, ?, ?, ?, ?)", (challenge_id, server_id, start_time, end_time, title, description))
            db.commit()
            db.close()

        else:
            db, cur = Database.connect()
            cur.execute("SELECT title, text FROM challenge_text WHERE id = ?", (random.randint(1, 24),))
            title, description = cur.fetchone()
            challenge_id = str(uuid.uuid4())
            cur.execute("INSERT INTO challenges (challenge_id, server_id, start_time, end_time, challenge_title, challenge_text) VALUES (?, ?, ?, ?, ?, ?)", (challenge_id, server_id, start_time, end_time,title,description))
            db.commit()
            db.close()

        return title, description
    
    def get_challenge(server_id):
        db, cur = Database.connect()
        current_time = int(time.time())
        cur.execute("SELECT challenge_id FROM challenges WHERE server_id = ? AND start_time < ? < end_time ORDER BY start_time DESC LIMIT 1", (server_id, current_time))
        challenge_id = cur.fetchone()
        db.close()
        return challenge_id[0]

    def add_submission(user_id, repo_url, language, comments, title, challenge_id, server_id, username):
        db, cur = Database.connect()
        submission_id = str(uuid.uuid4())
        cur.execute("INSERT INTO submissions (id, user_id, repo_url, language, comments, title, challenge_id, server_id, username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (submission_id, user_id, repo_url, language, comments, title, challenge_id, server_id, username))
        db.commit()
        db.close()
        return submission_id

    def get_leaderboard(challenge_id):
        db, cur = Database.connect()
        cur.execute("SELECT username, points FROM submissions WHERE challenge_id = ? ORDER BY points DESC LIMIT 5", (challenge_id,))
        leaderboard = cur.fetchall()
        db.close()
        return leaderboard
    
    def get_score(user_id, challenge_id):
        db, cur = Database.connect()
        cur.execute("SELECT points FROM submissions WHERE user_id = ? AND challenge_id = ? ORDER BY points DESC LIMIT 1", (user_id, challenge_id))
        score = cur.fetchone()
        db.close()
        return score
    
    def update_score(submission_id, points_to_add):
        db, cur = Database.connect()
        cur.execute("SELECT points FROM submissions WHERE id = ? ORDER BY points DESC LIMIT 1", (submission_id,))
        points = cur.fetchone()
        if points[0] == None:
            points = 0 + points_to_add
        else:
            points = points[0] + points_to_add
        cur.execute("UPDATE submissions SET points = ? WHERE id = ?", (points, submission_id))
        db.commit()
        db.close()
        return points

    def configure(server_id, leaderboard_channel, challenges_channel, submissions_channel):
        db, cur = Database.connect()
        cur.execute("INSERT INTO settings (server_id, leaderboard_channel, announcements_channel, approval_channel) VALUES (?, ?, ?, ?)", (server_id, leaderboard_channel, challenges_channel, submissions_channel))
        db.commit()
        db.close()

    def get_settings(server_id):
        db, cur = Database.connect()
        cur.execute("SELECT leaderboard_channel, announcements_channel, approval_channel FROM settings WHERE server_id = ?", (server_id,))
        leaderboard_channel, challenges_channel, submissions_channel = cur.fetchone()
        db.close()
        return leaderboard_channel, challenges_channel, submissions_channel
