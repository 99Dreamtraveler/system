"""
CLIP + LoRA 相似度检测服务 — 基于 similarity_flask1.py 逻辑
支持两种调用模式:
  1. detect_from_folder(folder_path, threshold) → 扫描文件夹直接检测
  2. detect_from_images(face_images, session_dir, threshold) → 指定图片列表检测 (兼容前端)
"""
import sys
import io
import json
import shutil
import numpy as np
from pathlib import Path
from PIL import Image
from collections import defaultdict
from datetime import datetime

import torch
from transformers import CLIPModel, CLIPImageProcessor
from peft import PeftModel

from config import (
    CLIP_MODEL_PATH, LORA_PATH, PROJECTION_PATH,
    BATCH_SIZE, SIMILARITY_THRESHOLD, UPLOAD_FOLDER
)

# 全局模型缓存
_similarity_model = None
_similarity_processor = None
_device = None

# 输出目录
OUTPUT_BASE_DIR = Path(__file__).parent.parent.parent / "output" / "similar_groups"


def get_device():
    global _device
    if _device is None:
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return _device


def format_group_id(index, total_groups):
    """Format a one-based group index using the current result's width."""
    width = max(1, len(str(total_groups)))
    return str(index).zfill(width)


def load_similarity_model():
    """加载 CLIP + LoRA + Projection 模型（单例）"""
    global _similarity_model, _similarity_processor

    if _similarity_model is not None:
        return _similarity_model, _similarity_processor

    print(f"[模型] 加载基础模型: {CLIP_MODEL_PATH}")
    base_model = CLIPModel.from_pretrained(str(CLIP_MODEL_PATH), local_files_only=True)

    # LoRA
    lora_path = LORA_PATH
    if not (lora_path / "adapter_model.safetensors").exists():
        raise FileNotFoundError(f"未找到 LoRA adapter: {lora_path}")

    lora_model = PeftModel.from_pretrained(base_model.vision_model, lora_path)
    base_model.vision_model = lora_model.merge_and_unload()
    print("[模型] ✓ LoRA权重加载成功")

    # Projection 层
    if PROJECTION_PATH.exists():
        base_model.visual_projection.load_state_dict(
            torch.load(str(PROJECTION_PATH), map_location=get_device())
        )
        print("[模型] ✓ 投影层权重加载成功")

    model = base_model.to(get_device())
    model.eval()

    processor = CLIPImageProcessor.from_pretrained(str(CLIP_MODEL_PATH), local_files_only=True)

    _similarity_model = model
    _similarity_processor = processor
    print("[模型] ✓ 相似度模型加载完成")

    return model, processor


# ============================================
# 核心逻辑 — 从 similarity_flask1.py 提取
# ============================================

def _extract_features(model, processor, image_paths):
    """提取 CLIP+LoRA 特征向量 (L2 归一化)"""
    features = {}

    for i in range(0, len(image_paths), BATCH_SIZE):
        batch_paths = image_paths[i:i + BATCH_SIZE]
        images = []
        valid_paths = []

        for p in batch_paths:
            try:
                img = Image.open(p).convert("RGB")
                images.append(img)
                valid_paths.append(p)
            except Exception as e:
                print(f"[警告] 无法加载 {p}: {e}")

        if not images:
            continue

        image_inputs = processor(images=images, return_tensors="pt").to(get_device())

        with torch.no_grad():
            output = model.get_image_features(pixel_values=image_inputs['pixel_values'])
            if hasattr(output, 'pooler_output'):
                img_features = output.pooler_output
            elif hasattr(output, 'image_embeds'):
                img_features = output.image_embeds
            else:
                img_features = output
            img_features = img_features / img_features.norm(dim=-1, keepdim=True)

        for k, path in enumerate(valid_paths):
            features[path] = img_features[k].cpu().numpy()

    return features


def _find_similar_pairs(features, threshold):
    """计算余弦相似度，找出所有超过阈值的图片对"""
    paths = list(features.keys())
    n = len(paths)

    if n < 2:
        return []

    feat_matrix = np.stack([features[p] for p in paths])
    sim_matrix = feat_matrix @ feat_matrix.T

    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            sim = float(sim_matrix[i, j])
            if sim >= threshold:
                pairs.append({
                    "path_i": paths[i],
                    "path_j": paths[j],
                    "similarity": round(sim, 4),
                })

    pairs.sort(key=lambda x: x['similarity'], reverse=True)
    return pairs


def _build_similarity_groups(pairs, image_paths):
    """使用并查集将相似对合并为连通组（优化版 — 路径压缩）"""
    parent = {}
    rank = {}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px == py:
            return
        if rank[px] < rank[py]:
            parent[px] = py
        elif rank[px] > rank[py]:
            parent[py] = px
        else:
            parent[px] = py
            rank[py] += 1

    # 初始化所有路径
    for p in image_paths:
        parent[p] = p
        rank[p] = 0

    for pair in pairs:
        union(pair['path_i'], pair['path_j'])

    # 按根节点分组
    groups = defaultdict(list)
    for p in image_paths:
        root = find(p)
        groups[root].append(p)

    # 只保留至少 2 个成员的组
    result = []
    for root, members in groups.items():
        if len(members) >= 2:
            result.append(sorted(members))

    # 按组大小降序排列
    result.sort(key=len, reverse=True)
    return result


def _compute_group_similarities(group_paths, features):
    """计算组内平均相似度"""
    if len(group_paths) < 2:
        return 0.0, 0.0

    sims = []
    for i in range(len(group_paths)):
        for j in range(i + 1, len(group_paths)):
            feat_i = features[group_paths[i]]
            feat_j = features[group_paths[j]]
            sim = float(np.dot(feat_i, feat_j))
            sims.append(sim)

    return float(np.mean(sims)), float(max(sims))


def _copy_groups_to_folders(groups, output_dir):
    """将相似组的图片复制到子文件夹"""
    output_path = Path(output_dir)
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    group_dirs = []
    for idx, members in enumerate(groups, 1):
        group_dir = output_path / f"group_{idx:03d}"
        group_dir.mkdir(exist_ok=True)

        for src_path in members:
            dst = group_dir / Path(src_path).name
            shutil.copy2(src_path, dst)

        group_dirs.append({
            "group_name": f"group_{idx:03d}",
            "path": str(group_dir),
            "image_count": len(members),
        })

    print(f"[输出] 相似组已保存到: {output_dir}")
    return group_dirs


# ============================================
# 公开接口
# ============================================

def detect_from_folder(folder_path, threshold=None):
    """
    模式1: 从文件夹直接检测（similarity_flask1.py 方式）
    扫描文件夹中所有图片 → 提取特征 → 找相似对 → 分组 → 输出到文件夹

    参数:
        folder_path: 图片文件夹路径
        threshold:  相似度阈值 (默认使用 SIMILARITY_THRESHOLD)

    返回:
        {
            "success": True,
            "input_folder": ...,
            "threshold": ...,
            "total_images": ...,
            "similar_pairs_count": ...,
            "groups_count": ...,
            "output_dir": ...,
            "similar_groups": [...],
            "suspicious_pairs": [...],
        }
    """
    if threshold is None:
        threshold = SIMILARITY_THRESHOLD

    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    # 1. 扫描图片
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    image_files = sorted([f for f in folder.iterdir() if f.suffix.lower() in valid_extensions])

    if len(image_files) < 2:
        return {
            "success": True,
            "input_folder": str(folder_path),
            "threshold": threshold,
            "total_images": len(image_files),
            "similar_pairs_count": 0,
            "groups_count": 0,
            "output_dir": None,
            "similar_groups": [],
            "suspicious_pairs": [],
            "message": "图片数量不足2张" if image_files else "未找到图片",
        }

    image_paths = [str(f) for f in image_files]
    print(f"[检测] 从文件夹加载了 {len(image_paths)} 张图片")

    # 2. 加载模型 & 提取特征
    model, processor = load_similarity_model()
    features = _extract_features(model, processor, image_paths)
    print(f"[检测] 成功提取 {len(features)} 个特征向量")

    # 3. 找相似对
    pairs = _find_similar_pairs(features, threshold)
    print(f"[检测] 发现 {len(pairs)} 对相似图片 (阈值={threshold})")

    # 4. 构建连通组
    groups = _build_similarity_groups(pairs, image_paths)
    print(f"[检测] 合并为 {len(groups)} 个相似组")

    # 5. 输出到文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_BASE_DIR / timestamp
    group_dirs = _copy_groups_to_folders(groups, output_dir)

    # 6. 构建结果
    similar_groups = []
    for idx, members in enumerate(groups, 1):
        avg_sim, max_sim = _compute_group_similarities(members, features)
        similar_groups.append({
            "group_id": format_group_id(idx, len(groups)),
            "images": [{"file_path": p, "filename": Path(p).name} for p in members],
            "count": len(members),
            "avg_similarity": avg_sim,
            "max_similarity": max_sim,
        })

    suspicious_pairs = [
        {
            "image_1": Path(p['path_i']).name,
            "image_2": Path(p['path_j']).name,
            "file_path_1": p['path_i'],
            "file_path_2": p['path_j'],
            "similarity": p['similarity'],
        }
        for p in pairs
    ]

    return {
        "success": True,
        "input_folder": str(folder_path),
        "threshold": threshold,
        "total_images": len(image_paths),
        "similar_pairs_count": len(suspicious_pairs),
        "groups_count": len(similar_groups),
        "output_dir": str(output_dir),
        "group_dirs": group_dirs,
        "similar_groups": similar_groups,
        "suspicious_pairs": suspicious_pairs,
    }


def detect_from_images(face_images, session_dir, threshold=None):
    """
    模式2: 从图片列表检测（兼容前端 — session_id + face_images）
    每张 face_image 需包含 image_id, file_path, loan_id 字段

    参数:
        face_images: [{"image_id": ..., "file_path": ..., "loan_id": ..., ...}, ...]
        session_dir: 上传会话根目录
        threshold:   相似度阈值

    返回: 与 detect_from_folder 结构相同，但 similar_groups[].images 保留原字段
    """
    if threshold is None:
        threshold = SIMILARITY_THRESHOLD

    if len(face_images) < 2:
        return {
            "success": True,
            "input_folder": str(session_dir),
            "threshold": threshold,
            "total_images": len(face_images),
            "similar_pairs_count": 0,
            "groups_count": 0,
            "output_dir": None,
            "similar_groups": [],
            "suspicious_pairs": [],
            "message": "面签照数量不足2张",
        }

    # 1. 构建完整路径映射
    session_path = Path(session_dir)
    image_map = {}   # full_path → face_image metadata
    for img in face_images:
        full_path = str(session_path / img["file_path"])
        image_map[full_path] = img

    image_paths = list(image_map.keys())
    print(f"[检测] 待处理面签照: {len(image_paths)} 张")

    # 2. 加载模型 & 提取特征
    model, processor = load_similarity_model()
    features = _extract_features(model, processor, image_paths)
    print(f"[检测] 成功提取 {len(features)} 个特征向量")

    valid_paths = list(features.keys())

    # 3. 找相似对
    pairs = _find_similar_pairs(features, threshold)
    print(f"[检测] 发现 {len(pairs)} 对相似图片 (阈值={threshold})")

    # 4. 构建连通组
    groups = _build_similarity_groups(pairs, valid_paths)
    print(f"[检测] 合并为 {len(groups)} 个相似组")

    # 5. 输出到文件夹
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = OUTPUT_BASE_DIR / timestamp
    group_dirs = _copy_groups_to_folders(groups, output_dir)

    # 6. 构建结果 — 保留 face_images 的元信息
    similar_groups = []
    for idx, members in enumerate(groups, 1):
        avg_sim, max_sim = _compute_group_similarities(members, features)
        images_meta = []
        for p in members:
            meta = image_map.get(p, {"file_path": p, "filename": Path(p).name})
            images_meta.append({
                "image_id": meta.get("image_id", Path(p).stem),
                "loan_id": meta.get("loan_id", ""),
                "filename": Path(p).name,
                "file_path": meta.get("file_path", p) if isinstance(meta, dict) else p,
                "person_confidence": meta.get("person_confidence", 0.0) if isinstance(meta, dict) else 0.0,
            })

        similar_groups.append({
            "group_id": format_group_id(idx, len(groups)),
            "images": images_meta,
            "count": len(members),
            "avg_similarity": avg_sim,
            "max_similarity": max_sim,
            "output_dir": str(output_dir / f"group_{idx:03d}"),
        })

    suspicious_pairs = [
        {
            "image_1": image_map.get(p['path_i'], {}).get("loan_id", Path(p['path_i']).name),
            "image_2": image_map.get(p['path_j'], {}).get("loan_id", Path(p['path_j']).name),
            "file_path_1": p['path_i'],
            "file_path_2": p['path_j'],
            "similarity": p['similarity'],
        }
        for p in pairs
    ]

    return {
        "success": True,
        "input_folder": str(session_dir),
        "threshold": threshold,
        "total_images": len(valid_paths),
        "similar_pairs_count": len(suspicious_pairs),
        "groups_count": len(similar_groups),
        "output_dir": str(output_dir),
        "group_dirs": group_dirs,
        "similar_groups": similar_groups,
        "suspicious_pairs": suspicious_pairs,
    }


def threshold_scan(folder_path):
    """
    阈值扫描 — 返回各阈值下的检测统计

    参数:
        folder_path: 图片文件夹路径

    返回:
        {
            "success": True,
            "input_folder": ...,
            "total_images": ...,
            "scan": [{"threshold": 0.5, "similar_pairs": N, "groups": M}, ...]
        }
    """
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"文件夹不存在: {folder_path}")

    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
    image_files = sorted([f for f in folder.iterdir() if f.suffix.lower() in valid_extensions])
    image_paths = [str(f) for f in image_files]

    if len(image_paths) < 2:
        return {
            "success": True,
            "input_folder": str(folder_path),
            "total_images": len(image_paths),
            "scan": [],
            "message": "图片数量不足2张",
        }

    model, processor = load_similarity_model()
    features = _extract_features(model, processor, image_paths)

    thresholds = [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.92, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99]
    scan = []
    for thr in thresholds:
        pairs = _find_similar_pairs(features, thr)
        groups = _build_similarity_groups(pairs, image_paths)
        scan.append({
            "threshold": thr,
            "similar_pairs": len(pairs),
            "groups": len(groups),
        })

    return {
        "success": True,
        "input_folder": str(folder_path),
        "total_images": len(image_paths),
        "scan": scan,
    }
