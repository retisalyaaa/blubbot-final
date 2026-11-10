import os
import uuid

from flask import Flask, jsonify, render_template, request, session

from chatbot.database import ChatHistory
from chatbot.engine import ChatbotEngine, load_theme


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "ganti-ini-saat-deploy"),
        THRESHOLD=float(os.environ.get("THRESHOLD", "0.45")),
        ADMIN_KEY=os.environ.get("ADMIN_KEY", ""),
        DATABASE=os.environ.get(
            "DATABASE", os.path.join(app.root_path, "chat_history.db")),
        THEME_FILE=os.path.join(app.root_path, "themes", "ikan.json"),
    )
    if config:
        app.config.update(config)

    theme = load_theme(app.config["THEME_FILE"])
    bot = ChatbotEngine(theme, app.config["THRESHOLD"])
    history = ChatHistory(app.config["DATABASE"])

    def sid():
        if "sid" not in session:
            session["sid"] = uuid.uuid4().hex
        return session["sid"]

    def galat(pesan):
        return jsonify({"error": pesan}), 400

    @app.get("/")
    def index():
        return render_template("chat.html", theme=theme)

    @app.post("/api/chat")
    def api_chat():
        data = request.get_json(silent=True)
        if data is None:
            return galat("Body harus berformat JSON")
        message = str(data.get("message", "")).strip()
        if not message:
            return galat("Pesan tidak boleh kosong")
        if len(message) > 500:
            return galat("Pesan maksimal 500 karakter")
        hasil = bot.reply(message)
        history.add(sid(), "user", message, hasil["intent"], hasil["score"])
        history.add(sid(), "bot", hasil["reply"])
        return jsonify(hasil)

    @app.get("/api/history")
    def api_history():
        return jsonify(history.history(sid()))

    @app.delete("/api/history")
    def api_clear():
        history.clear(sid())
        return jsonify({"ok": True})

    @app.get("/admin")
    def admin():
        key = app.config["ADMIN_KEY"]
        if key and request.args.get("key") != key:
            return "Kunci admin salah", 403
        return render_template(
            "admin.html", stats=history.stats(),
            unknown=history.unknown(), threshold=bot.threshold)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)