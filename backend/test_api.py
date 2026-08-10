"""
端到端测试脚本 - 上传数据集、筛选面签照、相似度检测
"""
import requests
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:5000"
DATASET_DIR = Path("E:/contest/dataset")

# ============================================
# Step 1: 上传文件夹
# ============================================
print("=" * 60)
print("Step 1: 上传数据集文件夹")
print("=" * 60)

files_to_upload = []
for root, dirs, files in os.walk(DATASET_DIR):
    # 跳过系统目录和隐藏文件
    dirs[:] = [d for d in dirs if not d.startswith("__") and not d.startswith(".")]
    for f in files:
        if f.startswith("._") or f.startswith("."):
            continue
        full_path = Path(root) / f
        rel_path = full_path.relative_to(DATASET_DIR).as_posix()
        files_to_upload.append((rel_path, str(full_path)))

print(f"找到 {len(files_to_upload)} 个文件")

# 构建 multipart form data
files_payload = []
for rel_path, full_path in files_to_upload:
    files_payload.append(("files", (rel_path, open(full_path, "rb"), "image/jpeg")))

resp = requests.post(f"{BASE_URL}/api/upload/folder", files=files_payload)
result = resp.json()
print(f"上传结果: {result['message']}")
print(f"  session_id: {result['data']['session_id']}")
print(f"  文件总数: {result['data']['total_files']}")
print(f"  子目录数: {len(result['data']['subdirs'])}")
print(f"  图片数: {result['data']['image_count']}")
print(f"  子目录: {result['data']['subdirs'][:5]}...")

session_id = result['data']['session_id']

# 关闭所有文件句柄
for _, (_, f, _) in files_payload:
    f.close()

# ============================================
# Step 2: 面签照筛选
# ============================================
print()
print("=" * 60)
print("Step 2: 面签照筛选 (YOLO)")
print("=" * 60)

resp = requests.post(f"{BASE_URL}/api/classify", json={"session_id": session_id})
result = resp.json()
print(f"筛选结果: {result['message']}")
data = result['data']
print(f"  图片总数: {data['total_images']}")
print(f"  面签照数: {data['person_detected']}")
print(f"  贷款目录数: {len(data['loan_dirs'])}")

face_images = data['face_signing_images']
print(f"  前5张面签照:")
for img in face_images[:5]:
    print(f"    {img['loan_id']} - 置信度: {img['person_confidence']:.3f}")

if data['person_detected'] != 74:
    print(f"  ❌ 期望74张面签照，实际{data['person_detected']}张!")
else:
    print(f"  ✅ 面签照筛选正确! 74/74张")

# ============================================
# Step 3: 相似度检测 (用前5张面签照快速测试)
# ============================================
print()
print("=" * 60)
print("Step 3: 相似度检测 (前5张面签照)")
print("=" * 60)

test_faces = face_images[:5]
resp = requests.post(f"{BASE_URL}/api/similarity/detect", json={
    "session_id": session_id,
    "face_images": test_faces,
    "threshold": 0.75,
})
result = resp.json()
print(f"检测结果: {result['message']}")
data = result['data']
print(f"  总比较对数: {data['total_comparisons']}")
print(f"  可疑相似对: {data['suspicious_pairs']}")
print(f"  相似组数: {data['similar_groups_count']}")

for group in data['similar_groups']:
    print(f"  {group['group_id']}: {group['count']}张, 平均相似度={group['avg_similarity']:.3f}")
    for img in group['images']:
        print(f"    - {img['loan_id']}")

print()
print("=" * 60)
print("✅ 端到端测试完成!")
print(f"   session_id = {session_id}")
print("=" * 60)
