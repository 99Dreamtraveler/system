"""YOLO 人物检测服务 — 基于 baseline_classify1.py 逻辑"""
import sys
import io
import os
import json
from pathlib import Path
import numpy as np
from PIL import Image

import torch
from ultralytics import YOLO
from config import YOLO_MODEL_PATH, CONF_THRESHOLD, PERSON_CLASS_ID

# 全局模型缓存
_yolo_model = None
_device = None


def get_device():
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device


def load_model():
    """加载 YOLO 模型（单例）"""
    global _yolo_model
    if _yolo_model is None:
        print(f"加载 YOLO 模型: {YOLO_MODEL_PATH}")
        _yolo_model = YOLO(str(YOLO_MODEL_PATH))
        print(f"设备: {get_device()}")
    return _yolo_model


def scan_folder(folder_path):
    """扫描文件夹，找到所有图片和子目录结构"""
    folder = Path(folder_path)
    images = []
    loan_dirs = {}

    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

    for root, dirs, files in os.walk(folder):
        # 跳过 __MACOSX 等系统目录
        dirs[:] = [d for d in dirs if not d.startswith("__") and not d.startswith(".")]
        for f in files:
            # 跳过隐藏文件 (如 ._ 开头的 macOS 资源分支)
            if f.startswith("._") or f.startswith("."):
                continue
            ext = Path(f).suffix.lower()
            if ext in valid_exts:
                full_path = Path(root) / f
                rel_path = full_path.relative_to(folder)
                loan_dir = rel_path.parts[0] if len(rel_path.parts) > 1 else "root"
                filename = rel_path.parts[-1]

                # 根据文件名推断图片类型
                name_lower = filename.lower()
                if "face_signing" in name_lower or "face" in name_lower:
                    image_type = "face_signing"
                elif "id_card_front" in name_lower or "front" in name_lower:
                    image_type = "id_card_front"
                elif "id_card_back" in name_lower or "back" in name_lower:
                    image_type = "id_card_back"
                elif "bank_statement" in name_lower or "bank" in name_lower or "statement" in name_lower:
                    image_type = "bank_statement"
                elif "contract" in name_lower:
                    image_type = "contract"
                else:
                    image_type = "other"

                img_info = {
                    "image_id": f"IMG_{len(images):05d}",
                    "file_path": str(rel_path).replace("\\", "/"),
                    "full_path": str(full_path),
                    "image_type": image_type,
                    "loan_id": loan_dir,
                    "filename": filename,
                }
                images.append(img_info)

                if loan_dir not in loan_dirs:
                    loan_dirs[loan_dir] = []
                loan_dirs[loan_dir].append(img_info)

    return images, loan_dirs


def detect_persons(images, batch_size=16):
    """使用 YOLO 检测图片中是否包含人"""
    model = load_model()
    has_person = []
    confidences = []

    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]

        for img_info in batch:
            try:
                results = model(img_info["full_path"], verbose=False)
                result = results[0]

                if result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes
                    cls_ids = boxes.cls.cpu().numpy() if boxes.cls is not None else []
                    confs = boxes.conf.cpu().numpy() if boxes.conf is not None else []

                    person_mask = (cls_ids == PERSON_CLASS_ID)
                    person_confs = confs[person_mask]
                    person_confs = person_confs[person_confs >= CONF_THRESHOLD]

                    if len(person_confs) > 0:
                        has_person.append(True)
                        confidences.append(float(person_confs.max()))
                    else:
                        has_person.append(False)
                        confidences.append(0.0)
                else:
                    has_person.append(False)
                    confidences.append(0.0)

            except Exception as e:
                print(f"  警告: 无法处理 {img_info['full_path']}: {e}")
                has_person.append(False)
                confidences.append(0.0)

    return np.array(has_person), np.array(confidences)


def classify_images(folder_path):
    """主分类函数 — 扫描文件夹，检测人物"""
    print(f"分类文件夹: {folder_path}")
    images, loan_dirs = scan_folder(folder_path)

    if not images:
        return {
            "total_images": 0,
            "person_detected": 0,
            "face_signing_images": [],
            "all_images": [],
            "loan_dirs": {},
        }

    print(f"找到 {len(images)} 张图片，分布在 {len(loan_dirs)} 个目录")

    y_pred_bool, y_confidences = detect_persons(images)

    # 组装结果
    all_images = []
    face_signing_images = []

    for i, img_info in enumerate(images):
        result = {
            **img_info,
            "has_person": bool(y_pred_bool[i]),
            "person_confidence": float(y_confidences[i]),
        }
        # 移除内部路径
        result.pop("full_path", None)

        all_images.append(result)

        if bool(y_pred_bool[i]):
            face_signing_images.append(result)

    return {
        "total_images": len(images),
        "person_detected": len(face_signing_images),
        "face_signing_images": face_signing_images,
        "all_images": all_images,
        "loan_dirs": {k: len(v) for k, v in loan_dirs.items()},
        "metrics": {
            "model": "yolo26n",
            "conf_threshold": CONF_THRESHOLD,
            "person_ratio": len(face_signing_images) / len(images) if images else 0,
        }
    }
