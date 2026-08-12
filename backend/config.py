"""Flask 后端配置"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent              # system/backend
SYSTEM_DIR = BASE_DIR.parent                   # system/

# 上传文件夹
UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
TASK_UPLOAD_FOLDER = UPLOAD_FOLDER / "tasks"
TASK_UPLOAD_FOLDER.mkdir(exist_ok=True)
DATABASE_PATH = BASE_DIR / "detection_results.sqlite3"

WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def validate_task_folder_name(folder_name):
    """Validate a user-provided task directory name without renaming it."""
    if not isinstance(folder_name, str) or not folder_name:
        return False, "缺少 folder_name"
    if folder_name != folder_name.strip():
        return False, "文件夹名称不能以空格开头或结尾"
    if folder_name in {".", ".."} or "/" in folder_name or "\\" in folder_name:
        return False, "文件夹名称只能是单层目录名"
    if any(char in folder_name for char in '<>:"|?*\x00'):
        return False, "文件夹名称包含非法字符"
    if folder_name.rstrip(". ").upper() in WINDOWS_RESERVED_NAMES:
        return False, "文件夹名称为 Windows 保留名称"
    return True, ""


def get_upload_session_dir(session_id):
    """Resolve a new named task directory first, then a legacy session directory."""
    valid, _ = validate_task_folder_name(session_id)
    if not valid:
        return None

    task_dir = TASK_UPLOAD_FOLDER / session_id
    if task_dir.is_dir():
        return task_dir

    legacy_dir = UPLOAD_FOLDER / session_id
    if legacy_dir == TASK_UPLOAD_FOLDER:
        return None
    return legacy_dir

# 模型路径 — 全部在 system/ 内
YOLO_MODEL_PATH = SYSTEM_DIR / "yolo26n.pt"
CLIP_MODEL_PATH = SYSTEM_DIR / "models" / "clip-vit-large-patch14"
LORA_PATH = SYSTEM_DIR / "checkpoints" / "face_lora_v2_full" / "best_lora"
PROJECTION_PATH = SYSTEM_DIR / "checkpoints" / "face_lora_v2_full" / "best_projection.pt"

# 分类配置
CONF_THRESHOLD = 0.25
PERSON_CLASS_ID = 0

# 相似度配置
BATCH_SIZE = 32
SIMILARITY_THRESHOLD = 0.90

# 图片类型映射
IMAGE_TYPES = {
    "face_signing": "面签合影照片",
    "id_card_front": "身份证正面",
    "id_card_back": "身份证背面",
    "bank_statement": "银行流水",
    "contract": "合同文档",
}

# Flask 配置
SECRET_KEY = "contest-secret-key-2024"
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
