"""分类 API — 面签照筛选 (直接调用 classify_flask 核心逻辑)"""
import sys
from pathlib import Path

# 确保能导入同级的 classify_flask 模块
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Blueprint, request, jsonify
from config import get_upload_session_dir
from services.repository import update_classification, fail_task
from services.repository import create_operation_log
from routes.auth import current_username

# 直接导入 classify_flask.py 的分类核心函数
from classify_flask import classify_folder, get_device

classify_bp = Blueprint("classify", __name__)


@classify_bp.route("/api/classify", methods=["POST"])
def run_classify():
    """执行面签照筛选"""
    data = request.get_json() or {}
    session_id = data.get("session_id", "")

    if not session_id:
        return jsonify({"code": 400, "message": "缺少 session_id"}), 400

    session_dir = get_upload_session_dir(session_id)
    if not session_dir or not session_dir.exists():
        return jsonify({"code": 404, "message": "上传文件夹不存在，请先上传"}), 404

    try:
        create_operation_log(current_username(), "开始检测", f"检测任务 {session_id} 开始面签照片筛选", "warning")
        result = classify_folder(str(session_dir))

        if not result.get("success"):
            fail_task(session_id, "分类处理失败")
            create_operation_log(current_username(), "检测失败", f"检测任务 {session_id} 的面签照片筛选失败", "danger")
            return jsonify({
                "code": 500,
                "message": "分类处理失败",
            }), 500

        update_classification(session_id, result)
        return jsonify({
            "code": 200,
            "message": f"筛选完成，共检测到 {result['person_detected']} 张面签照 (总计 {result['total_images']} 张)",
            "data": result,
        })

    except Exception as e:
        fail_task(session_id, str(e))
        create_operation_log(current_username(), "检测失败", f"检测任务 {session_id} 的面签照片筛选失败", "danger")
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "message": f"分类失败: {str(e)}"}), 500


@classify_bp.route("/api/classify/status", methods=["GET"])
def classify_status():
    """获取分类服务状态"""
    from classify_flask import YOLO_MODEL_PATH, CLASS_LABELS
    return jsonify({
        "code": 200,
        "message": "服务正常运行",
        "data": {
            "status": "ready",
            "model": "finance_5cls_best.pt",
            "model_path_exists": YOLO_MODEL_PATH.is_file(),
            "device": str(get_device()),
            "labels": list(CLASS_LABELS),
        }
    })
