"""贷款记录管理 API — 扫描、CRUD 操作"""
import os
import shutil
from pathlib import Path

from flask import Blueprint, request, jsonify
from config import (
    get_upload_session_dir,
    LOAN_FIELDS,
    LOAN_FIELD_LABELS,
    TASK_UPLOAD_FOLDER,
    validate_task_folder_name,
)
from services.repository import create_operation_log
from routes.auth import current_username

records_bp = Blueprint("records", __name__)

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def _find_matching_file(directory, field_name):
    """Find the file in a directory that matches a given field name."""
    name_map = {
        "bank_statement": ["bank_statement", "bank", "statement"],
        "contract": ["contract"],
        "face_signing": ["face_signing", "face"],
        "id_card_back": ["id_card_back", "back"],
        "id_card_front": ["id_card_front", "front"],
    }
    candidates = name_map.get(field_name, [field_name])

    for entry in sorted(directory.iterdir()):
        if entry.is_file():
            ext = entry.suffix.lower()
            if ext in VALID_EXTENSIONS:
                name_lower = entry.stem.lower()
                for c in candidates:
                    if c in name_lower:
                        return entry
    return None


@records_bp.route("/api/scan/<session_id>", methods=["GET"])
def scan_records(session_id):
    """扫描上传目录，返回 loan_* 子目录记录列表"""
    session_dir = get_upload_session_dir(session_id)
    if not session_dir or not session_dir.exists():
        return jsonify({"code": 404, "message": "上传文件夹不存在，请先上传"}), 404

    records = []
    for entry in sorted(session_dir.iterdir()):
        if not entry.is_dir():
            continue
        loan_id = entry.name
        if not loan_id.lower().startswith("loan"):
            continue

        fields = {}
        for field_name in LOAN_FIELDS:
            matching = _find_matching_file(entry, field_name)
            if matching:
                rel_path = str(matching.relative_to(session_dir)).replace("\\", "/")
                fields[field_name] = {
                    "exists": True,
                    "file_path": rel_path,
                    "filename": matching.name,
                }
            else:
                fields[field_name] = {
                    "exists": False,
                    "file_path": "",
                    "filename": "",
                }

        records.append({
            "loan_id": loan_id,
            "fields": fields,
        })

    return jsonify({
        "code": 200,
        "message": f"扫描完成，共发现 {len(records)} 条贷款记录",
        "data": {
            "session_id": session_id,
            "records": records,
            "total": len(records),
            "field_labels": LOAN_FIELD_LABELS,
        },
    })


@records_bp.route("/api/records/<session_id>", methods=["POST"])
def create_record(session_id):
    """创建新的 loan 子目录记录"""
    session_dir = get_upload_session_dir(session_id)
    if not session_dir or not session_dir.exists():
        return jsonify({"code": 404, "message": "上传文件夹不存在"}), 404

    loan_id = request.form.get("loan_id", "").strip()
    if not loan_id:
        return jsonify({"code": 400, "message": "缺少 loan_id"}), 400

    valid, msg = validate_task_folder_name(loan_id)
    if not valid:
        return jsonify({"code": 400, "message": msg}), 400

    loan_dir = session_dir / loan_id
    if loan_dir.exists():
        return jsonify({"code": 409, "message": "该贷款记录已存在"}), 409

    loan_dir.mkdir(parents=True, exist_ok=False)

    saved = []
    if "files" in request.files:
        for file in request.files.getlist("files"):
            if file.filename:
                safe_name = Path(file.filename).name
                if safe_name.startswith(".") or safe_name.startswith("._"):
                    continue
                target = loan_dir / safe_name
                file.save(str(target))
                saved.append(safe_name)

    create_operation_log(current_username(), "新增记录", f"创建贷款记录 {session_id}/{loan_id}", "success")

    return jsonify({
        "code": 200,
        "message": f"记录 {loan_id} 创建成功",
        "data": {
            "loan_id": loan_id,
            "saved_files": saved,
        },
    })


@records_bp.route("/api/records/<session_id>/<loan_id>", methods=["DELETE"])
def delete_record(session_id, loan_id):
    """删除一个 loan 子目录及其所有文件"""
    session_dir = get_upload_session_dir(session_id)
    if not session_dir or not session_dir.exists():
        return jsonify({"code": 404, "message": "上传文件夹不存在"}), 404

    loan_dir = session_dir / loan_id
    if not loan_dir.exists() or not loan_dir.is_dir():
        return jsonify({"code": 404, "message": "贷款记录不存在"}), 404

    try:
        loan_dir.resolve().relative_to(session_dir.resolve())
    except ValueError:
        return jsonify({"code": 400, "message": "路径非法"}), 400

    shutil.rmtree(str(loan_dir))
    create_operation_log(current_username(), "删除记录", f"删除贷款记录 {session_id}/{loan_id}", "danger")

    return jsonify({
        "code": 200,
        "message": f"记录 {loan_id} 已删除",
    })


@records_bp.route("/api/records/<session_id>/<loan_id>/<field>", methods=["POST"])
def upload_record_field(session_id, loan_id, field):
    """上传/替换某个贷款记录字段的图片文件"""
    if field not in LOAN_FIELDS:
        return jsonify({"code": 400, "message": f"无效字段名: {field}，可选值: {LOAN_FIELDS}"}), 400

    session_dir = get_upload_session_dir(session_id)
    if not session_dir or not session_dir.exists():
        return jsonify({"code": 404, "message": "上传文件夹不存在"}), 404

    loan_dir = session_dir / loan_id
    if not loan_dir.exists():
        loan_dir.mkdir(parents=True, exist_ok=True)

    try:
        loan_dir.resolve().relative_to(session_dir.resolve())
    except ValueError:
        return jsonify({"code": 400, "message": "路径非法"}), 400

    if "file" not in request.files:
        return jsonify({"code": 400, "message": "未选择文件"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"code": 400, "message": "文件名为空"}), 400

    ext = Path(file.filename).suffix.lower()
    if ext not in VALID_EXTENSIONS:
        return jsonify({"code": 400, "message": f"不支持的图片格式: {ext}"}), 400

    # 删除该字段的旧文件
    old_file = _find_matching_file(loan_dir, field)
    if old_file and old_file.exists():
        old_file.unlink()

    # 保存新文件，使用字段名作为文件名
    new_filename = f"{field}{ext}"
    target = loan_dir / new_filename
    file.save(str(target))

    rel_path = str(target.relative_to(session_dir)).replace("\\", "/")
    create_operation_log(
        current_username(), "更新字段",
        f"更新 {session_id}/{loan_id} 的 {LOAN_FIELD_LABELS.get(field, field)}",
        "info",
    )

    return jsonify({
        "code": 200,
        "message": f"字段 {LOAN_FIELD_LABELS.get(field, field)} 更新成功",
        "data": {
            "loan_id": loan_id,
            "field": field,
            "file_path": rel_path,
            "filename": new_filename,
        },
    })
