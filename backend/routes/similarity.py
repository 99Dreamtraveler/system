"""
相似度检测 API — 面签照相似度检测 (CLIP + LoRA + Projection)
支持两种模式:
  1. folder_path 模式: POST /api/similarity/detect  {"folder_path": "...", "threshold": 0.9}
  2. session_id 模式: POST /api/similarity/detect  {"session_id": "...", "face_images": [...], "threshold": 0.9}
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Blueprint, request, jsonify
from config import SIMILARITY_THRESHOLD, get_upload_session_dir
from services.repository import save_similarity, fail_task
from services.repository import create_operation_log
from routes.auth import current_username

from similarity_flask import detect_similarity, detect_from_folder, threshold_scan, get_device

similarity_bp = Blueprint("similarity", __name__)


@similarity_bp.route("/api/similarity/detect", methods=["POST"])
def run_similarity():
    """
    执行相似度检测

    模式1 — folder_path (推荐):
        {"folder_path": "E:/contest/original_face", "threshold": 0.9}

    模式2 — session_id + face_images (兼容前端):
        {"session_id": "...", "face_images": [...], "threshold": 0.9}
    """
    data = request.get_json() or {}

    folder_path = data.get("folder_path", "")
    session_id = data.get("session_id", "")
    face_images = data.get("face_images", [])
    threshold = data.get("threshold", SIMILARITY_THRESHOLD)

    try:
        # 模式1: folder_path 直接检测
        if folder_path:
            result = detect_from_folder(folder_path, threshold)
            if not result.get("success"):
                if session_id: fail_task(session_id, result.get("message", "检测失败"))
                return jsonify({"code": 500, "message": result.get("message", "检测失败")}), 500

            return jsonify({
                "code": 200,
                "message": f"检测完成，共发现 {result['groups_count']} 个相似组",
                "data": result,
            })

        # 模式2: session_id + face_images (兼容原前端)
        if session_id:
            session_dir = get_upload_session_dir(session_id)
            if not session_dir or not session_dir.exists():
                return jsonify({"code": 404, "message": "上传文件夹不存在"}), 404

            if not face_images:
                return jsonify({"code": 400, "message": "请提供面签照列表 face_images"}), 400

            from services.repository import update_classification
            filtered_images = [
                img_info for img_info in face_images
                if (session_dir / img_info.get("file_path", "")).is_file()
            ]

            # 更新分类统计到数据库
            update_classification(session_id, {
                "total_images": len(face_images),
                "person_detected": len(filtered_images),
            })

            if len(filtered_images) < 2:
                fail_task(session_id, "面签照YOLO筛选后有效图片不足")
                create_operation_log(current_username(), "检测失败",
                                     f"检测任务 {session_id} YOLO筛选后仅{len(filtered_images)}张（需≥2）", "danger")
                return jsonify({
                    "code": 400,
                    "message": f"面签照筛选后有效图片不足（需至少2张，当前{len(filtered_images)}张）",
                }), 400

            create_operation_log(current_username(), "面签照分类完成",
                                 f"五分类筛选出 {len(filtered_images)} 张面签合影照片", "success")

            result = detect_similarity(filtered_images, str(session_dir), threshold)

            if not result.get("success"):
                fail_task(session_id, "相似度检测失败")
                create_operation_log(current_username(), "检测失败", f"检测任务 {session_id} 的相似度检测失败", "danger")
                return jsonify({"code": 500, "message": "相似度检测失败"}), 500

            save_similarity(session_id, result)
            create_operation_log(current_username(), "完成检测", f"检测任务 {session_id} 已完成相似度检测", "success")
            return jsonify({
                "code": 200,
                "message": f"检索完成，共发现 {result['groups_count']} 个相似组",
                "data": result,
            })

        return jsonify({
            "code": 400,
            "message": "请提供 folder_path 或 session_id + face_images",
        }), 400

    except FileNotFoundError as e:
        if session_id: fail_task(session_id, str(e))
        if session_id: create_operation_log(current_username(), "检测失败", f"检测任务 {session_id} 的相似度检测失败", "danger")
        return jsonify({"code": 404, "message": str(e)}), 404
    except Exception as e:
        if session_id: fail_task(session_id, str(e))
        if session_id: create_operation_log(current_username(), "检测失败", f"检测任务 {session_id} 的相似度检测失败", "danger")
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"相似度检测失败: {str(e)}"}), 500


@similarity_bp.route("/api/similarity/threshold-scan", methods=["POST"])
def run_threshold_scan():
    """
    阈值扫描 — 查看不同阈值下的检测统计

    Request:
        {"folder_path": "E:/contest/original_face"}

    或:
        {"session_id": "..."}
    """
    data = request.get_json() or {}
    folder_path = data.get("folder_path", "")
    session_id = data.get("session_id", "")

    try:
        if folder_path:
            result = threshold_scan(folder_path)
        elif session_id:
            session_dir = get_upload_session_dir(session_id)
            if not session_dir or not session_dir.exists():
                return jsonify({"code": 404, "message": "上传文件夹不存在"}), 404
            result = threshold_scan(str(session_dir))
        else:
            return jsonify({"code": 400, "message": "请提供 folder_path 或 session_id"}), 400

        return jsonify({
            "code": 200,
            "message": "阈值扫描完成",
            "data": result,
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"阈值扫描失败: {str(e)}"}), 500


@similarity_bp.route("/api/similarity/related/<session_id>/<path:loan_id>", methods=["GET"])
def get_related_files(session_id, loan_id):
    """获取某贷款目录下的所有相关文件"""
    import os
    from pathlib import Path

    session_dir = get_upload_session_dir(session_id)
    if not session_dir or not session_dir.exists():
        return jsonify({"code": 404, "message": "上传文件夹不存在"}), 404

    # 查找 loan_id 对应的目录
    target_dir = None
    for item in session_dir.iterdir():
        if item.is_dir() and item.name == loan_id:
            target_dir = item
            break

    if not target_dir:
        return jsonify({"code": 404, "message": f"未找到贷款目录: {loan_id}"}), 404

    files = []
    for f in target_dir.iterdir():
        if f.is_file():
            ext = f.suffix.lower()
            if ext in (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"):
                rel_path = f.relative_to(session_dir)
                filename = f.name.lower()

                if "face_signing" in filename:
                    ftype = "face_signing"
                    label = "面签合影照片"
                elif "id_card_front" in filename:
                    ftype = "id_card_front"
                    label = "身份证正面"
                elif "id_card_back" in filename:
                    ftype = "id_card_back"
                    label = "身份证背面"
                elif "bank_statement" in filename:
                    ftype = "bank_statement"
                    label = "银行流水"
                elif "contract" in filename:
                    ftype = "contract"
                    label = "合同文档"
                else:
                    ftype = "other"
                    label = "其他"

                files.append({
                    "filename": f.name,
                    "file_path": str(rel_path).replace("\\", "/"),
                    "image_type": ftype,
                    "label": label,
                    "loan_id": loan_id,
                })

    return jsonify({
        "code": 200,
        "data": {
            "loan_id": loan_id,
            "files": files,
        }
    })
