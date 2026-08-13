"""
金融影像智能相似度检测系统 — Flask 后端
"""
import sys
import os

from pathlib import Path

# 确保 backend 目录在 sys.path 中
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import FINANCE_CLASSIFIER_MODEL_PATH, SECRET_KEY, UPLOAD_FOLDER

from routes.auth import auth_bp
from routes.upload import upload_bp
from routes.classify import classify_bp
from routes.similarity import similarity_bp
from routes.history import history_bp
from routes.records import records_bp
from services.repository import initialize_database


def create_app():
    app = Flask(__name__, static_folder=None)

    # 配置
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB

    # CORS
    CORS(app, supports_credentials=True, origins="*")

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(classify_bp)
    app.register_blueprint(similarity_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(records_bp)
    initialize_database()

    # ============================================
    # 静态文件服务 — Vue 前端
    # ============================================
    FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "dist"

    @app.route("/")
    def serve_frontend():
        if (FRONTEND_DIR / "index.html").exists():
            return send_from_directory(str(FRONTEND_DIR), "index.html")
        return jsonify({
            "code": 200,
            "message": "后端服务运行中，前端请使用 Vite 开发服务器",
            "api_docs": {
                "login": "POST /api/login",
                "register": "POST /api/register",
                "upload": "POST /api/upload/folder",
                "classify": "POST /api/classify",
                "similarity": "POST /api/similarity/detect",
            }
        })

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        return send_from_directory(str(FRONTEND_DIR / "assets"), filename)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "code": 200,
            "message": "服务正常运行",
            "data": {
                "models": {
                    "finance_classifier": FINANCE_CLASSIFIER_MODEL_PATH.is_file(),
                    "clip": os.path.exists(str(Path(__file__).parent.parent / "models" / "clip-vit-large-patch14")),
                    "lora": os.path.exists(str(Path(__file__).parent.parent / "checkpoints" / "face_lora_v2_full" / "best_lora" / "adapter_model.safetensors")),
                    "projection": os.path.exists(str(Path(__file__).parent.parent / "checkpoints" / "face_lora_v2_full" / "best_projection.pt")),
                }
            }
        })

    return app


if __name__ == "__main__":
    app = create_app()
    print("=" * 60)
    print("金融影像智能相似度检测系统 — 后端服务")
    print("=" * 60)
    print(f"上传目录: {UPLOAD_FOLDER}")
    print(f"前端目录: {Path(__file__).parent.parent / 'frontend' / 'dist'}")
    print("启动 Flask 开发服务器...")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
