"""
Step 1 — 面签图片筛选 Baseline
使用 CLIP-vit-large-patch14 进行5分类筛选
从5种金融影像中识别出面签照片(face_signing)
输出 JSON 格式作为 Step 2 的输入
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel

# ============================================
# 配置
# ============================================
MODEL_NAME = Path(__file__).parent / "models" / "clip-vit-large-patch14"
DATASET_DIR = Path("数据集")
ANNOTATIONS_PATH = DATASET_DIR / "annotations.csv"
BATCH_SIZE = 16
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# 5种影像类型的英文描述 (用于zero-shot分类)
IMAGE_TYPE_LABELS = [
    "A photo of a person signing a loan document at a bank branch, showing the customer and bank employee together",
    "A photo of the front side of a Chinese ID card, showing the national emblem, name, photo and ID number",
    "A photo of the back side of a Chinese ID card, showing the issuing authority and valid period",
    "A photo of a bank statement document, showing transaction records and account information",
    "A photo of a loan contract document, showing contract terms and signatures",
]

EN_TO_CN = {
    "face_signing": "面签合影照片",
    "id_card_front": "身份证正面",
    "id_card_back": "身份证背面",
    "bank_statement": "银行流水",
    "contract": "合同文档",
}
EN_LABELS = list(EN_TO_CN.keys())


def load_model():
    """加载 CLIP 模型和处理器"""
    print(f"加载模型: {MODEL_NAME}")
    print(f"设备: {DEVICE}")
    processor = CLIPProcessor.from_pretrained(MODEL_NAME, local_files_only=True)
    model = CLIPModel.from_pretrained(MODEL_NAME, local_files_only=True).to(DEVICE)
    model.eval()
    return model, processor


def load_data():
    """加载数据集标注"""
    df = pd.read_csv(ANNOTATIONS_PATH, skipinitialspace=True)
    print(f"数据集: {len(df)} 张影像")
    return df


def classify_images(model, processor, df):
    """使用 CLIP 进行5分类"""
    all_preds = []
    all_probs = []

    text_inputs = processor(
        text=IMAGE_TYPE_LABELS,
        return_tensors="pt",
        padding=True,
        truncation=True
    ).to(DEVICE)

    with torch.no_grad():
        text_features = model.get_text_features(**text_inputs)
        if hasattr(text_features, 'pooler_output'):
            text_features = text_features.pooler_output
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)

    image_paths = [str(DATASET_DIR / p) for p in df['file_path']]

    for i in tqdm(range(0, len(image_paths), BATCH_SIZE), desc="5分类"):
        batch_paths = image_paths[i:i + BATCH_SIZE]

        images = []
        valid_indices = []
        for j, p in enumerate(batch_paths):
            try:
                img = Image.open(p).convert("RGB")
                images.append(img)
                valid_indices.append(j)
            except Exception as e:
                print(f"  警告: 无法加载 {p}: {e}")

        if not images:
            continue

        image_inputs = processor(
            images=images,
            return_tensors="pt",
            padding=True
        ).to(DEVICE)

        with torch.no_grad():
            image_features = model.get_image_features(**image_inputs)
            if hasattr(image_features, 'pooler_output'):
                image_features = image_features.pooler_output
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)

            logits_per_image = (image_features @ text_features.T) * model.logit_scale.exp()
            probs = F.softmax(logits_per_image, dim=-1)

        pred_ids = probs.argmax(dim=-1).cpu().numpy()
        prob_vals = probs.cpu().numpy()

        for idx, pred_id in enumerate(pred_ids):
            j = valid_indices[idx]
            all_preds.append(EN_LABELS[pred_id])
            all_probs.append(prob_vals[idx])

    return np.array(all_preds), np.array(all_probs)


def evaluate_classification(y_true, y_pred):
    """评估5分类结果"""
    print("\n" + "=" * 60)
    print("Step 1 — 影像分类结果")
    print("=" * 60)

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_true, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

    print(f"Overall Accuracy : {acc:.4f}")
    print(f"Weighted Precision: {prec:.4f}")
    print(f"Weighted Recall   : {rec:.4f}")
    print(f"Weighted F1-score : {f1:.4f}")

    print("\n各类别详细指标:")
    target_names = [EN_TO_CN[l] for l in EN_LABELS]
    print(classification_report(y_true, y_pred, target_names=target_names, digits=4))

    cm = confusion_matrix(y_true, y_pred, labels=EN_LABELS)
    print("\n混淆矩阵 (行=真实, 列=预测):")
    header = "           " + " ".join(f"{l[:8]:>9}" for l in EN_LABELS)
    print(header)
    for i, row in enumerate(cm):
        print(f"{EN_LABELS[i]:>10}: " + " ".join(f"{v:>9}" for v in row))

    face_true = (y_true == "face_signing").astype(int)
    face_pred = (y_pred == "face_signing").astype(int)
    face_prec = precision_score(face_true, face_pred, zero_division=0)
    face_rec = recall_score(face_true, face_pred, zero_division=0)
    face_f1 = f1_score(face_true, face_pred, zero_division=0)
    print(f"\n⭐ face_signing (面签照片) 二分类指标:")
    print(f"   Precision: {face_prec:.4f}")
    print(f"   Recall   : {face_rec:.4f}")
    print(f"   F1-score : {face_f1:.4f}")

    return {
        "overall": {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1},
        "face_signing": {"precision": face_prec, "recall": face_rec, "f1": face_f1},
    }


def save_results(df, y_pred, y_probs, metrics):
    """保存筛选结果为 JSON 格式"""
    df['pred_label'] = y_pred
    face_signing_idx = EN_LABELS.index("face_signing")
    df['face_signing_prob'] = y_probs[:, face_signing_idx]

    face_signing_df = df[df['pred_label'] == 'face_signing'].copy()

    result_json = {
        "metadata": {
            "total_images": len(df),
            "face_signing_detected": len(face_signing_df),
            "metrics": metrics
        },
        "face_signing_images": []
    }

    for _, row in face_signing_df.iterrows():
        result_json["face_signing_images"].append({
            "image_id": row['image_id'],
            "file_path": row['file_path'],
            "image_type": row['image_type'],
            "business_type": row['business_type'],
            "loan_id": row['loan_id'],
            "similar_group": row['similar_group'] if pd.notna(row['similar_group']) else "",
            "is_similar_pair": int(row['is_similar_pair']),
            "confidence": float(row['face_signing_prob'])
        })

    json_path = OUTPUT_DIR / "face_signing_images.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result_json, f, indent=2, ensure_ascii=False)
    print(f"\n筛选结果已保存: {json_path}")
    print(f"筛选出面签照片: {len(face_signing_df)} 张")

    return json_path


def main():
    print("=" * 60)
    print("Step 1: 影像5分类筛选 (CLIP Zero-Shot)")
    print(f"模型: {MODEL_NAME}")
    print("=" * 60)

    df = load_data()
    model, processor = load_model()

    y_pred, y_probs = classify_images(model, processor, df)

    y_true = df['image_type'].values

    metrics = evaluate_classification(y_true, y_pred)

    save_results(df, y_pred, y_probs, metrics)

    print("\n✅ Step 1 完成!")


if __name__ == "__main__":
    main()