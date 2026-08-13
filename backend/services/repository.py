"""SQLite persistence for completed image-detection tasks."""
import json
import sqlite3
from datetime import date, datetime, timedelta

from config import DATABASE_PATH, get_upload_session_dir


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    with _connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS detection_tasks (
          task_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, folder_name TEXT,
          status TEXT NOT NULL, created_at TEXT NOT NULL, completed_at TEXT,
          duration INTEGER, total_images INTEGER DEFAULT 0, valid_images INTEGER DEFAULT 0,
          interview_images INTEGER DEFAULT 0, similarity REAL, risk_level TEXT,
          error_message TEXT, progress INTEGER DEFAULT 0, current_step TEXT,
          classification_result TEXT
        );
        CREATE TABLE IF NOT EXISTS similarity_results (
          result_id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL,
          image_id TEXT, image_name TEXT, file_path TEXT, loan_id TEXT,
          similar_image_id TEXT, similar_image_name TEXT, similar_file_path TEXT,
          similar_loan_id TEXT, similarity REAL NOT NULL, risk_level TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS risk_cases (
          case_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, business_a_id TEXT,
          business_b_id TEXT, loan_a_id TEXT, loan_b_id TEXT, image_a_path TEXT,
          image_b_path TEXT, similarity REAL NOT NULL, risk_level TEXT NOT NULL,
          risk_reason TEXT NOT NULL, status TEXT NOT NULL, discovered_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS operation_logs (
          log_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL,
          action TEXT NOT NULL, detail TEXT NOT NULL, type TEXT NOT NULL,
          occurred_at TEXT NOT NULL
        );
        """)
        columns = {row[1] for row in conn.execute("PRAGMA table_info(detection_tasks)").fetchall()}
        if "progress" not in columns:
            conn.execute("ALTER TABLE detection_tasks ADD COLUMN progress INTEGER DEFAULT 0")
        if "current_step" not in columns:
            conn.execute("ALTER TABLE detection_tasks ADD COLUMN current_step TEXT")
        if "classification_result" not in columns:
            conn.execute("ALTER TABLE detection_tasks ADD COLUMN classification_result TEXT")
        conn.execute("UPDATE detection_tasks SET status='检测失败', progress=0, current_step=NULL, error_message='服务重启导致任务中断' WHERE status='检测中'")


def risk_level(similarity):
    if similarity >= 0.90:
        return "高风险"
    if similarity >= 0.80:
        return "中风险"
    return "低风险"


def _relative_file_path(task_id, file_path):
    if not file_path:
        return ""
    session_dir = get_upload_session_dir(task_id)
    if not session_dir:
        return str(file_path).replace("\\", "/")
    try:
        return str(__import__("pathlib").Path(file_path).resolve().relative_to(session_dir.resolve())).replace("\\", "/")
    except ValueError:
        return str(file_path).replace("\\", "/")


def create_task(task_id, folder_name, total_files):
    with _connection() as conn:
        conn.execute("""INSERT INTO detection_tasks
          (task_id, session_id, folder_name, status, created_at, total_images)
          VALUES (?, ?, ?, '待检测', ?, ?)""", (task_id, task_id, folder_name or task_id, _now(), total_files))


def task_exists(task_id):
    """Return whether a persisted detection task already owns this task name."""
    with _connection() as conn:
        return conn.execute("SELECT 1 FROM detection_tasks WHERE task_id=?", (task_id,)).fetchone() is not None


def set_task_progress(task_id, progress, current_step):
    with _connection() as conn:
        conn.execute("UPDATE detection_tasks SET progress=?, current_step=? WHERE task_id=?", (progress, current_step, task_id))


def prepare_task_for_execution(task_id):
    with _connection() as conn:
        conn.execute("""UPDATE detection_tasks SET status='检测中', completed_at=NULL, duration=NULL,
          similarity=NULL, risk_level=NULL, error_message=NULL, progress=1, current_step='等待执行'
          WHERE task_id=?""", (task_id,))


def update_classification(task_id, result):
    with _connection() as conn:
        conn.execute("""UPDATE detection_tasks
          SET total_images = ?, valid_images = ?, interview_images = ?, classification_result = ?
          WHERE task_id = ?""", (
            result.get("total_images", 0),
            result.get("total_images", 0),
            result.get("person_detected", 0),
            json.dumps({
                "all_images": result.get("all_images", []),
                "class_counts": {
                    label: sum(item.get("pred_label") == label for item in result.get("all_images", []))
                    for label in ("face_signing", "id_card_front", "id_card_back", "bank_statement", "contract")
                },
            }, ensure_ascii=False),
            task_id,
        ))


def fail_task(task_id, error_message):
    with _connection() as conn:
        conn.execute("UPDATE detection_tasks SET status='检测失败', progress=0, current_step=NULL, completed_at=?, error_message=? WHERE task_id=?", (_now(), error_message, task_id))


def save_similarity(task_id, result):
    now = _now()
    pairs = result.get("suspicious_pairs", [])
    max_similarity = max((item.get("similarity", 0) for item in pairs), default=0)
    overall_level = risk_level(max_similarity) if pairs else "低风险"
    with _connection() as conn:
        task = conn.execute("SELECT created_at FROM detection_tasks WHERE task_id=?", (task_id,)).fetchone()
        created_at = task["created_at"] if task else now
        started = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        duration = max(0, int((datetime.now() - started).total_seconds()))
        conn.execute("""UPDATE detection_tasks SET status='已完成', completed_at=?, duration=?, valid_images=?,
          similarity=?, risk_level=?, error_message=NULL, progress=100, current_step='检测完成' WHERE task_id=?""", (now, duration, result.get("total_images", 0), max_similarity * 100 if pairs else None, overall_level, task_id))
        conn.execute("DELETE FROM similarity_results WHERE task_id=?", (task_id,))
        conn.execute("DELETE FROM risk_cases WHERE task_id=?", (task_id,))
        for index, pair in enumerate(pairs, 1):
            similarity = float(pair.get("similarity", 0))
            level = risk_level(similarity)
            loan_a = pair.get("image_1", "")
            loan_b = pair.get("image_2", "")
            file_a = _relative_file_path(task_id, pair.get("file_path_1", ""))
            file_b = _relative_file_path(task_id, pair.get("file_path_2", ""))
            conn.execute("""INSERT INTO similarity_results
              (task_id,image_name,file_path,loan_id,similar_image_name,similar_file_path,similar_loan_id,similarity,risk_level,created_at)
              VALUES (?,?,?,?,?,?,?,?,?,?)""", (task_id, loan_a, file_a, loan_a, loan_b, file_b, loan_b, similarity * 100, level, now))
            case_id = f"CASE_{task_id}_{index:03d}"
            reason = "不同业务中出现高度相似面签影像"
            conn.execute("""INSERT INTO risk_cases
              (case_id,task_id,business_a_id,business_b_id,loan_a_id,loan_b_id,image_a_path,image_b_path,similarity,risk_level,risk_reason,status,discovered_at)
              VALUES (?,?,?,?,?,?,?,?,?,?,?,'待核查',?)""", (case_id, task_id, loan_a, loan_b, loan_a, loan_b, file_a, file_b, similarity * 100, level, reason, now))


def _task_payload(row):
    # A NULL database value means similarity detection has not produced a risk decision.
    risk_level = row["risk_level"] if row["status"] == "已完成" and row["risk_level"] else "待检测"
    return {"taskId": row["task_id"], "createdAt": row["created_at"], "detectedAt": row["completed_at"],
            "duration": f"{row['duration'] or 0} 秒" if row["completed_at"] else None, "similarity": row["similarity"],
            "riskLevel": risk_level, "status": row["status"],
            "totalImages": row["total_images"], "validImages": row["valid_images"],
            "interviewImages": row["interview_images"], "progress": row["progress"] or 0,
            "currentStep": row["current_step"], "errorMessage": row["error_message"]}


def list_tasks(filters):
    clauses, values = [], []
    mapping = {"taskId": "task_id LIKE ?", "status": "status = ?"}
    for key, clause in mapping.items():
        if filters.get(key): clauses.append(clause); values.append(f"%{filters[key]}%" if key == "taskId" else filters[key])
    if filters.get("riskLevel") == "待检测":
        clauses.append("risk_level IS NULL")
    elif filters.get("riskLevel"):
        clauses.append("risk_level = ?"); values.append(filters["riskLevel"])
    if filters.get("startTime"): clauses.append("created_at >= ?"); values.append(filters["startTime"])
    if filters.get("endTime"): clauses.append("created_at <= ?"); values.append(f"{filters['endTime']} 23:59:59")
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with _connection() as conn:
        rows = conn.execute(f"SELECT * FROM detection_tasks{where} ORDER BY created_at DESC", values).fetchall()
    return [_task_payload(row) for row in rows]


def get_task(task_id):
    with _connection() as conn:
        task = conn.execute("SELECT * FROM detection_tasks WHERE task_id=?", (task_id,)).fetchone()
        if not task: return None
        results = conn.execute("SELECT * FROM similarity_results WHERE task_id=? ORDER BY similarity DESC", (task_id,)).fetchall()
    payload = _task_payload(task)
    try:
        classification = json.loads(task["classification_result"] or "{}")
    except json.JSONDecodeError:
        classification = {}
    risks = {"high": 0, "medium": 0, "low": 0}
    abnormal = []
    for result in results:
        risks[{"高风险": "high", "中风险": "medium", "低风险": "low"}[result["risk_level"]]] += 1
        abnormal.append({"name": result["file_path"], "reason": f"与 {result['similar_file_path']} 相似度 {result['similarity']:.2f}%", "similarity": result["similarity"]})
    payload.update({"imageStats": {"total": task["total_images"], "valid": task["valid_images"]}, "screeningStats": {"total": task["valid_images"], "interviewPhotos": task["interview_images"]}, "similarityStats": {"similarGroups": len(results), "suspiciousPairs": len(results), "maxSimilarity": task["similarity"]}, "riskStats": risks, "abnormalImages": abnormal, "suspicious_pairs": [dict(row) for row in results], "classification": classification})
    return payload


def list_cases(filters):
    clauses, values = [], []
    for key, column in (("caseId", "case_id"), ("riskLevel", "risk_level"), ("status", "status")):
        if filters.get(key): clauses.append(f"{column} {'LIKE' if key == 'caseId' else '='} ?"); values.append(f"%{filters[key]}%" if key == "caseId" else filters[key])
    if filters.get("businessId"): clauses.append("(business_a_id LIKE ? OR business_b_id LIKE ?)"); values += [f"%{filters['businessId']}%"] * 2
    if filters.get("startTime"): clauses.append("discovered_at >= ?"); values.append(filters["startTime"])
    if filters.get("endTime"): clauses.append("discovered_at <= ?"); values.append(f"{filters['endTime']} 23:59:59")
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with _connection() as conn: rows = conn.execute(f"SELECT * FROM risk_cases{where} ORDER BY discovered_at DESC", values).fetchall()
    return [_case_payload(row) for row in rows]


def _case_payload(row):
    return {"caseId": row["case_id"], "taskId": row["task_id"], "businessA": {"businessId": row["business_a_id"], "loanId": row["loan_a_id"], "imagePath": row["image_a_path"]}, "businessB": {"businessId": row["business_b_id"], "loanId": row["loan_b_id"], "imagePath": row["image_b_path"]}, "similarity": row["similarity"], "riskLevel": row["risk_level"], "riskReasons": [row["risk_reason"]], "similarityAnalysis": ["基于自有模型特征提取与相似度计算", "面部特征相似度较高"], "discoveredAt": row["discovered_at"], "status": row["status"]}


def get_case(case_id):
    with _connection() as conn: row = conn.execute("SELECT * FROM risk_cases WHERE case_id=?", (case_id,)).fetchone()
    return _case_payload(row) if row else None


def update_case_status(case_id, status):
    with _connection() as conn: conn.execute("UPDATE risk_cases SET status=? WHERE case_id=?", (status, case_id))
    return get_case(case_id)


def create_operation_log(username, action, detail, log_type):
    """Store a concise audit event without credentials or filesystem paths."""
    with _connection() as conn:
        conn.execute("""INSERT INTO operation_logs (username, action, detail, type, occurred_at)
          VALUES (?, ?, ?, ?, ?)""", (username or "anonymous", action, detail, log_type, _now()))


def list_operation_logs(page, page_size):
    page = max(1, int(page))
    page_size = min(100, max(1, int(page_size)))
    offset = (page - 1) * page_size
    with _connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM operation_logs").fetchone()[0]
        rows = conn.execute("""SELECT log_id, username, action, detail, type, occurred_at
          FROM operation_logs ORDER BY occurred_at DESC, log_id DESC LIMIT ? OFFSET ?""",
          (page_size, offset)).fetchall()
    return {
        "total": total,
        "page": page,
        "pageSize": page_size,
        "records": [{"id": row["log_id"], "username": row["username"], "action": row["action"],
                     "detail": row["detail"], "type": row["type"], "occurredAt": row["occurred_at"]}
                    for row in rows],
    }


def analytics(start_date, end_date):
    start_day = date.fromisoformat(start_date)
    end_day = date.fromisoformat(end_date)
    with _connection() as conn:
        tasks = conn.execute("SELECT * FROM detection_tasks WHERE created_at >= ? AND created_at <= ? ORDER BY created_at", (f"{start_date} 00:00:00", f"{end_date} 23:59:59")).fetchall()
        cases = conn.execute("""SELECT risk_cases.*, detection_tasks.created_at AS task_created_at
          FROM risk_cases JOIN detection_tasks ON detection_tasks.task_id = risk_cases.task_id
          WHERE detection_tasks.created_at >= ? AND detection_tasks.created_at <= ?""", (f"{start_date} 00:00:00", f"{end_date} 23:59:59")).fetchall()
    dates = [(start_day + timedelta(days=index)).isoformat() for index in range((end_day - start_day).days + 1)]
    detection = [{"date": day, "detectionCount": sum(row["created_at"].startswith(day) for row in tasks), "abnormalCount": sum(row["task_created_at"].startswith(day) for row in cases)} for day in dates]
    risks = [{"date": day, "high": sum(row["risk_level"] == "高风险" and row["task_created_at"].startswith(day) for row in cases), "medium": sum(row["risk_level"] == "中风险" and row["task_created_at"].startswith(day) for row in cases), "low": sum(row["risk_level"] == "低风险" and row["task_created_at"].startswith(day) for row in cases)} for day in dates]
    buckets = [("0~50%", 0, 50), ("50~70%", 50, 70), ("70~80%", 70, 80), ("80~90%", 80, 90), ("90~100%", 90, 101)]
    return {"detectionTrend": detection, "riskTrend": risks, "similarityDistribution": [{"label": label, "count": sum(low <= row["similarity"] < high for row in cases)} for label, low, high in buckets], "imageCategoryDistribution": {"interview": sum(row["interview_images"] for row in tasks), "idCard": 0, "bankStatement": 0, "contract": 0, "other": sum(max(0, row["total_images"] - row["interview_images"]) for row in tasks)}, "riskDistribution": {"high": sum(row["risk_level"] == "高风险" for row in cases), "medium": sum(row["risk_level"] == "中风险" for row in cases), "low": sum(row["risk_level"] == "低风险" for row in cases)}, "tasks": [_task_payload(row) for row in tasks], "cases": [_case_payload(row) for row in cases]}


def all_analytics(end_date=None):
    """Aggregate every persisted task from the first task date through today."""
    end_date = end_date or date.today().isoformat()
    with _connection() as conn:
        first_task = conn.execute("SELECT MIN(created_at) FROM detection_tasks").fetchone()[0]
    start_date = first_task[:10] if first_task else end_date
    return analytics(start_date, end_date)
