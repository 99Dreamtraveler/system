"""Background execution for detection tasks, independent of page lifecycle."""
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from config import get_upload_session_dir
from services.repository import get_task, set_task_progress, prepare_task_for_execution, update_classification, save_similarity, fail_task

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="detection-task")
_locks = {}
_locks_guard = Lock()


def _task_lock(task_id):
    with _locks_guard:
        return _locks.setdefault(task_id, Lock())


def run_detection_task(task_id):
    from classify_flask import classify_folder
    from similarity_flask import detect_similarity

    session_dir = get_upload_session_dir(task_id)
    if not session_dir or not session_dir.exists():
        raise FileNotFoundError("上传任务目录不存在")
    set_task_progress(task_id, 10, "面签照片筛选")
    classification = classify_folder(str(session_dir))
    if not classification.get("success"):
        raise RuntimeError("面签照片筛选失败")
    update_classification(task_id, classification)
    face_images = classification.get("face_signing_images", [])
    set_task_progress(task_id, 45, "YOLO 人物检测完成")
    if len(face_images) < 2:
        raise RuntimeError(f"有效面签照片不足（当前 {len(face_images)} 张）")
    set_task_progress(task_id, 55, "特征提取")
    set_task_progress(task_id, 70, "相似度计算")
    result = detect_similarity(face_images, str(session_dir), 0.90)
    if not result.get("success"):
        raise RuntimeError("相似度检测失败")
    save_similarity(task_id, result)


def submit_detection_task(task_id):
    task = get_task(task_id)
    if not task:
        return None, "检测任务不存在"
    if task["status"] == "已完成":
        return task, None
    lock = _task_lock(task_id)
    if not lock.acquire(blocking=False):
        return task, None

    prepare_task_for_execution(task_id)

    def worker():
        try:
            run_detection_task(task_id)
        except Exception as error:
            fail_task(task_id, str(error))
        finally:
            lock.release()

    _executor.submit(worker)
    return get_task(task_id), None
