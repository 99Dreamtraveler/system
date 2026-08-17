"""
classify_flask.py — 面签照筛选 Flask 接口
基于 baseline_classify1.py 的 YOLO 人物检测逻辑封装
====================================================
启动方式:
  conda activate pytorch_test
  python classify_flask.py

接口:
  POST /api/classify          — 对指定文件夹执行面签照筛选
  GET  /api/classify/health   — 健康检查
  GET  /api/classify/preview/<path:filepath> — 图片预览
"""
import sys
import os
import json
import traceback
from pathlib import Path
import numpy as np

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import torch
from ultralytics import YOLO

# ============================================
# 配置
# ============================================
# 项目根目录 (system/)
PROJECT_DIR = Path(__file__).parent.parent

# 模型路径
YOLO_MODEL_PATH = PROJECT_DIR / "yolo26n.pt"

# 人物检测参数 (与 baseline_classify1.py 保持一致)
PERSON_CLASS_ID = 0       # YOLO COCO class 0 = person
CONF_THRESHOLD = 0.25     # 置信度阈值
BATCH_SIZE = 16           # 批量处理大小

# 图片扩展名
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}

# 图片类型映射
IMAGE_TYPES = {
    "face_signing": "面签合影照片",
    "id_card_front": "身份证正面",
    "id_card_back": "身份证背面",
    "bank_statement": "银行流水",
    "contract": "合同文档",
}

# ============================================
# Flask 应用
# ============================================
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB
CORS(app, supports_credentials=True, origins="*")

# ============================================
# 模型管理 (单例延迟加载)
# ============================================
_yolo_model = None
_device = None


def get_device():
    """获取计算设备"""
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device


def load_model():
    """加载 YOLO26n 模型 (单例)"""
    global _yolo_model
    if _yolo_model is None:
        print(f"[模型] 加载 YOLO: {YOLO_MODEL_PATH}")
        print(f"[模型] 设备: {get_device()}")
        _yolo_model = YOLO(str(YOLO_MODEL_PATH))
    return _yolo_model


# ============================================
# 核心逻辑 — 与 baseline_classify1.py 对齐
# ============================================

def infer_image_type(filename: str) -> str:
    """根据文件名推断图片类型"""
    name_lower = filename.lower()
    if "face_signing" in name_lower or "face" in name_lower:
        return "face_signing"
    elif "id_card_front" in name_lower or "front" in name_lower:
        return "id_card_front"
    elif "id_card_back" in name_lower or "back" in name_lower:
        return "id_card_back"
    elif "bank_statement" in name_lower or ("bank" in name_lower and "statement" in name_lower):
        return "bank_statement"
    elif "contract" in name_lower:
        return "contract"
    elif "bank" in name_lower:
        return "bank_statement"
    elif "statement" in name_lower:
        return "bank_statement"
    else:
        return "other"


def scan_folder(folder_path: str) -> list:
    """
    递归扫描文件夹中所有图片
    与 baseline_classify1.py 的 load_data + detect_persons 输入对齐
    """
    folder = Path(folder_path)
    images = []

    for root, dirs, files in os.walk(folder):
        # 跳过系统目录和隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith("__") and not d.startswith(".")]
        for f in files:
            # 跳过隐藏文件 (macOS 资源分支等)
            if f.startswith("._") or f.startswith("."):
                continue
            ext = Path(f).suffix.lower()
            if ext not in VALID_EXTENSIONS:
                continue

            full_path = Path(root) / f
            rel_path = full_path.relative_to(folder)
            loan_dir = rel_path.parts[0] if len(rel_path.parts) > 1 else "root"
            filename = rel_path.parts[-1]

            image_type = infer_image_type(filename)

            images.append({
                "image_id": f"IMG_{len(images):05d}",
                "file_path": str(rel_path).replace("\\", "/"),
                "full_path": str(full_path),
                "image_type": image_type,
                "image_type_cn": IMAGE_TYPES.get(image_type, "其他"),
                "loan_id": loan_dir,
                "filename": filename,
            })

    return images


def detect_persons(images: list) -> tuple:
    """
    使用 YOLO26n 检测每张图中是否包含人
    与 baseline_classify1.py 的 detect_persons() 逻辑完全一致

    返回:
        has_person (np.ndarray): bool 数组, 是否检测到人
        confidences (np.ndarray): float 数组, 最高人物置信度 (无人则为 0)
    """
    model = load_model()
    has_person_preds = []
    all_confidences = []

    for i in range(0, len(images), BATCH_SIZE):
        batch = images[i:i + BATCH_SIZE]

        for img_info in batch:
            try:
                results = model(img_info["full_path"], verbose=False)
                result = results[0]

                if result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes
                    cls_ids = boxes.cls.cpu().numpy() if boxes.cls is not None else []
                    confs = boxes.conf.cpu().numpy() if boxes.conf is not None else []

                    # 筛选 person 类别的检测结果
                    person_mask = (cls_ids == PERSON_CLASS_ID)
                    person_confs = confs[person_mask]

                    # 过滤低于置信度阈值的结果
                    person_confs = person_confs[person_confs >= CONF_THRESHOLD]

                    if len(person_confs) > 0:
                        has_person_preds.append(True)
                        all_confidences.append(float(person_confs.max()))
                    else:
                        has_person_preds.append(False)
                        all_confidences.append(0.0)
                else:
                    has_person_preds.append(False)
                    all_confidences.append(0.0)

            except Exception as e:
                print(f"  [警告] 无法处理 {img_info['full_path']}: {e}")
                has_person_preds.append(False)
                all_confidences.append(0.0)

    return np.array(has_person_preds), np.array(all_confidences)


def classify_folder(folder_path: str) -> dict:
    """
    主分类函数 — 对文件夹执行人物检测筛选

    参数:
        folder_path: 待检测的文件夹路径

    返回:
        dict: 包含筛选结果的完整 JSON
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    print(f"[分类] 扫描文件夹: {folder_path}")
    images = scan_folder(folder_path)

    if not images:
        return {
            "success": True,
            "total_images": 0,
            "person_detected": 0,
            "face_signing_images": [],
            "all_images": [],
            "loan_dirs": {},
            "metrics": {
                "model": "yolo26n",
                "conf_threshold": CONF_THRESHOLD,
                "person_ratio": 0.0,
            }
        }

    # 统计目录分布
    loan_dirs = {}
    for img in images:
        lid = img["loan_id"]
        loan_dirs[lid] = loan_dirs.get(lid, 0) + 1

    print(f"[分类] 找到 {len(images)} 张图片, 分布在 {len(loan_dirs)} 个目录")
    print(f"[分类] 开始 YOLO 人物检测...")

    y_pred_bool, y_confidences = detect_persons(images)

    # 组装结果
    all_images = []
    face_signing_images = []

    for i, img_info in enumerate(images):
        result = {
            "image_id": img_info["image_id"],
            "file_path": img_info["file_path"],
            "image_type": img_info["image_type"],
            "image_type_cn": img_info["image_type_cn"],
            "loan_id": img_info["loan_id"],
            "filename": img_info["filename"],
            "has_person": bool(y_pred_bool[i]),
            "person_confidence": float(y_confidences[i]),
        }
        all_images.append(result)

        if bool(y_pred_bool[i]):
            face_signing_images.append(result)

    n_person = len(face_signing_images)
    print(f"[分类] 完成! 检测到人物: {n_person}/{len(images)} ({n_person/len(images)*100:.1f}%)")

    return {
        "success": True,
        "total_images": len(images),
        "person_detected": n_person,
        "face_signing_images": face_signing_images,
        "all_images": all_images,
        "loan_dirs": loan_dirs,
        "metrics": {
            "model": "yolo26n",
            "conf_threshold": CONF_THRESHOLD,
            "person_ratio": round(n_person / len(images), 4) if images else 0.0,
            "device": str(get_device()),
        }
    }


# ============================================
# API 路由
# ============================================

@app.route("/api/classify", methods=["POST"])
def api_classify():
    """
    面签照筛选接口

    请求方式: POST
    Content-Type: application/json

    请求参数:
        {
            "folder_path": "E:/contest/dataset"   // 必填: 待检测的文件夹绝对路径
            // 或者
            "folder": "dataset"                    // 相对于 contest 目录的路径
        }

    返回:
        {
            "success": true,
            "total_images": 370,
            "person_detected": 74,
            "face_signing_images": [...],
            "all_images": [...],
            "loan_dirs": {...},
            "metrics": {...}
        }
    """
    try:
        data = request.get_json() or {}
        folder_path = data.get("folder_path", "") or data.get("folder", "")

        if not folder_path:
            return jsonify({
                "success": False,
                "message": "请提供 folder_path (文件夹绝对路径) 或 folder (相对路径)",
            }), 400

        # 支持相对路径: 相对于 contest 目录
        input_path = Path(folder_path)
        if not input_path.is_absolute():
            input_path = PROJECT_DIR / folder_path

        if not input_path.exists():
            return jsonify({
                "success": False,
                "message": f"文件夹不存在: {input_path}",
            }), 404

        if not input_path.is_dir():
            return jsonify({
                "success": False,
                "message": f"路径不是文件夹: {input_path}",
            }), 400

        result = classify_folder(str(input_path))

        return jsonify({
            "success": result["success"],
            "message": f"筛选完成，共检测到 {result['person_detected']} 张面签照 (总计 {result['total_images']} 张)",
            "data": result,
        })

    except FileNotFoundError as e:
        return jsonify({"success": False, "message": str(e)}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "message": f"分类失败: {str(e)}"}), 500


@app.route("/api/classify/health", methods=["GET"])
def api_health():
    """健康检查"""
    model_path_exists = YOLO_MODEL_PATH.exists()
    return jsonify({
        "success": True,
        "status": "running",
        "model": "yolo26n",
        "model_loaded": _yolo_model is not None,
        "model_path_exists": model_path_exists,
        "model_path": str(YOLO_MODEL_PATH),
        "device": str(get_device()),
        "conf_threshold": CONF_THRESHOLD,
        "person_class_id": PERSON_CLASS_ID,
    })


@app.route("/api/classify/preview/<path:filepath>", methods=["GET"])
def api_preview(filepath):
    """
    图片预览接口 — 通过文件路径直接访问图片

    GET /api/classify/preview/E:/contest/dataset/loan_001/face_signing.jpg
    """
    import mimetypes
    file_path = Path(filepath)
    if not file_path.is_absolute():
        file_path = Path("/") / filepath

    if not file_path.exists():
        return jsonify({"success": False, "message": f"文件不存在: {file_path}"}), 404

    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = "image/jpeg"

    return send_file(str(file_path), mimetype=mime_type)


@app.route("/", methods=["GET"])
def api_index():
    """API 文档首页"""
    return jsonify({
        "service": "面签照智能筛选服务",
        "version": "1.0.0",
        "model": "yolo26n",
        "endpoints": {
            "classify": {
                "method": "POST",
                "path": "/api/classify",
                "description": "对指定文件夹执行面签照筛选",
                "body": {
                    "folder_path": "string (必填) — 文件夹绝对路径",
                    "folder": "string (可选) — 相对于 contest 目录的路径",
                },
                "example": 'curl -X POST http://127.0.0.1:5001/api/classify -H "Content-Type: application/json" -d \'{"folder": "dataset"}\'',
            },
            "health": {
                "method": "GET",
                "path": "/api/classify/health",
                "description": "健康检查 & 模型状态",
            },
            "preview": {
                "method": "GET",
                "path": "/api/classify/preview/<filepath>",
                "description": "通过文件路径预览图片",
            },
        }
    })


# ============================================
# 启动
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("面签照智能筛选服务 (YOLO26n)")
    print("=" * 60)
    print(f"模型路径:   {YOLO_MODEL_PATH}")
    print(f"置信度阈值: {CONF_THRESHOLD}")
    print(f"人物类别ID: {PERSON_CLASS_ID}")
    print(f"设备:       {get_device()}")
    print("=" * 60)
    print("启动 Flask 服务...")
    print("")
    print("  接口示例:")
    print('    curl -X POST http://127.0.0.1:5001/api/classify \\')
    print('      -H "Content-Type: application/json" \\')
    print('      -d \'{"folder": "dataset"}\'')
    print("")
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True,
    )
