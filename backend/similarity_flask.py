"""
similarity_flask.py — 面签照相似度检测核心逻辑
基于 services/similarity.py 的 detect_from_folder / detect_from_images
供 routes/similarity.py 蓝图调用
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.similarity import (
    detect_from_folder,
    detect_from_images,
    threshold_scan,
    load_similarity_model,
    get_device,
)

# 对外暴露 detect_similarity — 兼容原 routes/similarity.py 调用
# 新接口: detect_from_folder(folder_path, threshold)
# 旧兼容: detect_from_images(face_images, session_dir, threshold)


def detect_similarity(face_images, session_dir, threshold=None):
    """
    兼容原 routes/similarity.py 的调用方式
    实际委托给 detect_from_images
    """
    return detect_from_images(face_images, session_dir, threshold)
