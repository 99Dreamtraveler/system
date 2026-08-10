"""文件上传相关 API"""
import os
import shutil
import uuid
from flask import Blueprint, request, jsonify
from config import (
    TASK_UPLOAD_FOLDER,
    UPLOAD_FOLDER,
    get_upload_session_dir,
    validate_task_folder_name,
)

upload_bp = Blueprint("upload", __name__)

# 存储每个会话的上传文件夹路径
session_folders = {}


def normalize_upload_path(filename):
    """Keep Unicode relative paths while rejecting unsafe path components."""
    relative_path = filename.replace("\\", "/")
    if not relative_path or relative_path.startswith("/"):
        return None

    safe_parts = []
    for part in relative_path.split("/"):
        if not part or part in {".", ".."}:
            return None
        if part.startswith("._") or part.startswith(".") or "__MACOSX" in part:
            return None
        if any(char in part for char in '<>:"|?*\x00'):
            return None
        if part.rstrip(". ").upper() in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}:
            return None
        safe_parts.append(part)

    return "/".join(safe_parts)


@upload_bp.route("/api/upload/folder", methods=["POST"])
def upload_folder():
    """上传文件夹 — 支持多文件上传模拟文件夹"""
    folder_name = request.form.get("folder_name")
    is_named_task = folder_name is not None

    if is_named_task:
        valid, message = validate_task_folder_name(folder_name)
        if not valid:
            return jsonify({"code": 400, "message": message}), 400
        session_id = folder_name
        session_dir = TASK_UPLOAD_FOLDER / session_id
        if session_dir.exists():
            return jsonify({"code": 409, "message": "同名上传任务已存在，请使用不同的文件夹名称"}), 409
    else:
        # Compatibility for existing callers that only supply files/session headers.
        session_id = request.headers.get("X-Session-Id", str(uuid.uuid4()))
        valid, message = validate_task_folder_name(session_id)
        if not valid:
            return jsonify({"code": 400, "message": f"无效 session_id：{message}"}), 400
        session_dir = UPLOAD_FOLDER / session_id
        if session_dir == TASK_UPLOAD_FOLDER:
            return jsonify({"code": 400, "message": "session_id 不可使用保留目录名"}), 400

    if "files" not in request.files:
        return jsonify({"code": 400, "message": "未选择文件"}), 400

    files = request.files.getlist("files")
    if not files:
        return jsonify({"code": 400, "message": "未选择文件"}), 400

    # Legacy uploads preserve the prior overwrite behavior; named tasks never overwrite.
    if not is_named_task and session_dir.exists():
        shutil.rmtree(session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)

    # 第一步: 保留 Unicode 相对目录结构，过滤系统文件与不安全路径。
    path_pairs = []  # [(raw_file, relative_path), ...]
    for file in files:
        if not file.filename:
            continue
        relative_path = normalize_upload_path(file.filename)
        if not relative_path:
            continue
        path_pairs.append((file, relative_path))

    # 第二步: 如果所有文件都在同一个顶层目录下，去掉该前缀
    # 浏览器选择 dataset 文件夹时 → dataset/loan_001/... → loan_001/...
    if path_pairs:
        paths = [p for _, p in path_pairs]
        # 收集所有有层级结构的顶层目录
        top_dirs = set(p.split("/")[0] for p in paths if "/" in p)
        if len(top_dirs) == 1:
            prefix = top_dirs.pop() + "/"
            path_pairs = [(f, p[len(prefix):] if p.startswith(prefix) else p) for f, p in path_pairs]

    # 第三步: 保存文件
    saved_files = []
    for file, safe_path in path_pairs:
        target_path = session_dir / safe_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        file.save(str(target_path))
        saved_files.append(safe_path)

    session_folders[session_id] = str(session_dir)

    # 统计文件夹内容
    subdirs = set()
    image_files = []
    valid_exts = {"jpg", "jpeg", "png", "bmp", "gif", "webp"}
    for f in saved_files:
        parts = f.split("/")
        if len(parts) > 1:
            subdirs.add(parts[0])
        ext = f.lower().rsplit(".", 1)[-1] if "." in f else ""
        if ext in valid_exts:
            image_files.append(f)

    return jsonify({
        "code": 200,
        "message": "上传成功",
        "data": {
            "session_id": session_id,
            "total_files": len(saved_files),
            "subdirs": sorted(subdirs),
            "image_count": len(image_files),
            "images": sorted(image_files)[:50],  # 前50张预览
        }
    })


@upload_bp.route("/api/upload/session/<session_id>", methods=["GET"])
def get_session_info(session_id):
    """获取会话上传信息"""
    session_dir = get_upload_session_dir(session_id)
    if not session_dir or not session_dir.exists():
        return jsonify({"code": 404, "message": "会话不存在"}), 404

    # 扫描目录
    all_files = []
    for root, dirs, files in os.walk(session_dir):
        for f in files:
            rel_path = os.path.relpath(os.path.join(root, f), session_dir)
            all_files.append(rel_path.replace("\\", "/"))

    subdirs = set()
    for f in all_files:
        parts = f.split("/")
        if len(parts) > 1:
            subdirs.add(parts[0])

    return jsonify({
        "code": 200,
        "data": {
            "session_id": session_id,
            "total_files": len(all_files),
            "subdirs": sorted(subdirs),
            "files": sorted(all_files),
        }
    })


@upload_bp.route("/api/file/<session_id>/<path:filepath>", methods=["GET"])
def serve_file(session_id, filepath):
    """提供文件访问"""
    from flask import send_file
    import mimetypes

    session_dir = get_upload_session_dir(session_id)
    if not session_dir or not session_dir.exists():
        return jsonify({"code": 404, "message": "会话不存在"}), 404

    session_root = session_dir.resolve()
    file_path = (session_root / filepath).resolve()
    try:
        file_path.relative_to(session_root)
    except ValueError:
        return jsonify({"code": 400, "message": "文件路径非法"}), 400

    if not file_path.exists():
        return jsonify({"code": 404, "message": "文件不存在"}), 404

    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and mime_type.startswith("image/"):
        return send_file(str(file_path), mimetype=mime_type)

    return send_file(str(file_path))
