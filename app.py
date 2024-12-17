from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Database setup
DB_FILE = "plex.db"
if not os.path.exists(DB_FILE):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT,
            user BOOLEAN,
            owner BOOLEAN,
            account_id INTEGER,
            account_title TEXT,
            server_title TEXT,
            server_uuid TEXT,
            player_title TEXT,
            player_local BOOLEAN,
            player_public_address TEXT,
            metadata_type TEXT,
            metadata_title TEXT,
            metadata_library_section_type TEXT,
            metadata_rating_key TEXT,
            metadata_parent_title TEXT,
            metadata_grandparent_title TEXT,
            metadata_added_at INTEGER,
            metadata_updated_at INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )''')

@app.route("/", methods=["POST"])
def plex_webhook():
    if request.method == "POST":
        try:
            # Parse the JSON payload
            payload = request.json
            event = payload.get("event", "unknown")
            user = payload.get("user", False)
            owner = payload.get("owner", False)

            # Account details
            account = payload.get("Account", {})
            account_id = account.get("id", 0)
            account_title = account.get("title", "unknown")

            # Server details
            server = payload.get("Server", {})
            server_title = server.get("title", "unknown")
            server_uuid = server.get("uuid", "unknown")

            # Player details
            player = payload.get("Player", {})
            player_title = player.get("title", "unknown")
            player_local = player.get("local", False)
            player_public_address = player.get("publicAddress", "unknown")

            # Metadata details
            metadata = payload.get("Metadata", {})
            metadata_type = metadata.get("type", "unknown")
            metadata_title = metadata.get("title", "unknown")
            metadata_library_section_type = metadata.get("librarySectionType", "unknown")
            metadata_rating_key = metadata.get("ratingKey", "unknown")
            metadata_parent_title = metadata.get("parentTitle", "unknown")
            metadata_grandparent_title = metadata.get("grandparentTitle", "unknown")
            metadata_added_at = metadata.get("addedAt", 0)
            metadata_updated_at = metadata.get("updatedAt", 0)

            # Save to database
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO events (
                                    event, user, owner, account_id, account_title,
                                    server_title, server_uuid, player_title, player_local, player_public_address,
                                    metadata_type, metadata_title, metadata_library_section_type, metadata_rating_key,
                                    metadata_parent_title, metadata_grandparent_title, metadata_added_at, metadata_updated_at
                                  ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (event, user, owner, account_id, account_title,
                                server_title, server_uuid, player_title, player_local, player_public_address,
                                metadata_type, metadata_title, metadata_library_section_type, metadata_rating_key,
                                metadata_parent_title, metadata_grandparent_title, metadata_added_at, metadata_updated_at))
                conn.commit()

            return jsonify({"status": "success", "message": "Webhook received"}), 200
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)