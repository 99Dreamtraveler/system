"""Historical task, risk-case and analytics query APIs backed by SQLite."""
from datetime import date, timedelta
from flask import Blueprint, request, jsonify
from services.repository import list_tasks, get_task, list_cases, get_case, update_case_status, analytics, all_analytics, create_operation_log, list_operation_logs
from routes.auth import current_username

history_bp = Blueprint("history", __name__)

@history_bp.route("/api/history/tasks", methods=["GET"])
def tasks():
    records = list_tasks(request.args)
    return jsonify({"code": 200, "data": {"total": len(records), "page": int(request.args.get("page", 1)), "pageSize": int(request.args.get("pageSize", 20)), "records": records}})

@history_bp.route("/api/history/tasks/<task_id>", methods=["GET"])
def task_detail(task_id):
    task = get_task(task_id)
    return jsonify({"code": 200, "data": task}) if task else (jsonify({"code": 404, "message": "检测任务不存在"}), 404)

@history_bp.route("/api/risk/cases", methods=["GET"])
def cases():
    records = list_cases(request.args)
    return jsonify({"code": 200, "data": {"total": len(records), "records": records}})

@history_bp.route("/api/risk/cases/<case_id>", methods=["GET"])
def case_detail(case_id):
    item = get_case(case_id)
    return jsonify({"code": 200, "data": item}) if item else (jsonify({"code": 404, "message": "风险案件不存在"}), 404)

def _change_case(case_id, status):
    item = update_case_status(case_id, status)
    if item:
        action = {"核查中": "开始核查", "已确认": "确认风险", "已排除": "标记为正常"}[status]
        create_operation_log(current_username(), action, f"风险案件 {case_id} 状态更新为 {status}", "warning" if status == "核查中" else "success")
    return jsonify({"code": 200, "data": item}) if item else (jsonify({"code": 404, "message": "风险案件不存在"}), 404)

@history_bp.route("/api/risk/cases/<case_id>/review", methods=["POST"])
def review(case_id): return _change_case(case_id, "核查中")

@history_bp.route("/api/risk/cases/<case_id>/confirm", methods=["POST"])
def confirm(case_id): return _change_case(case_id, "已确认")

@history_bp.route("/api/risk/cases/<case_id>/dismiss", methods=["POST"])
def dismiss(case_id): return _change_case(case_id, "已排除")

@history_bp.route("/api/statistics/analytics", methods=["GET"])
def analytics_statistics():
    end = request.args.get("endDate") or date.today().isoformat()
    if request.args.get("all", "").lower() == "true":
        return jsonify({"code": 200, "data": all_analytics(end)})
    start = request.args.get("startDate") or (date.fromisoformat(end) - timedelta(days=6)).isoformat()
    return jsonify({"code": 200, "data": analytics(start, end)})


@history_bp.route("/api/system/operation-logs", methods=["GET"])
def operation_logs():
    data = list_operation_logs(request.args.get("page", 1), request.args.get("pageSize", 20))
    return jsonify({"code": 200, "data": data})
