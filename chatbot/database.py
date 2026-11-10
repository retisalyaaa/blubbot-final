import sqlite3


class ChatHistory:
    def __init__(self, path="chat_history.db"):
        self.path = path
        self._run("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT, sender TEXT, text TEXT,
            intent TEXT, score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")

    def _run(self, sql, params=(), fetch=False):
        conn = sqlite3.connect(self.path)
        try:
            with conn:  # commit otomatis, rollback kalau galat
                cur = conn.execute(sql, params)
                return cur.fetchall() if fetch else None
        finally:
            conn.close()

    def add(self, session_id, sender, text, intent=None, score=None):
        self._run(
            "INSERT INTO messages (session_id, sender, text, intent, score) "
            "VALUES (?, ?, ?, ?, ?)",
            (session_id, sender, text, intent, score))

    def history(self, session_id):
        rows = self._run(
            "SELECT sender, text FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,), fetch=True)
        return [{"sender": s, "text": t} for s, t in rows]

    def clear(self, session_id):
        self._run("DELETE FROM messages WHERE session_id = ?", (session_id,))

    def stats(self):
        return self._run(
            "SELECT COALESCE(intent, '(tidak dikenali)'), COUNT(*) FROM messages "
            "WHERE sender = 'user' GROUP BY intent ORDER BY 2 DESC", fetch=True)

    def unknown(self):
        return self._run(
            "SELECT text, score, created_at FROM messages "
            "WHERE sender = 'user' AND intent IS NULL ORDER BY id DESC LIMIT 20",
            fetch=True)