"""
Demo: batch predict images under subfolders of a parent folder.

Expected input format:
demo_test/
  loan_001/
    bank_statement.jpg
    contract.jpg
    ...
  loan_002/
    ...

Run:
    python demo_predict.py
    python demo_predict.py path/to/parent_folder
"""
import argparse
import io
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
ULTRALYTICS_CONFIG_DIR = OUTPUT_DIR / "ultralytics_config"
ULTRALYTICS_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ["YOLO_CONFIG_DIR"] = str(ULTRALYTICS_CONFIG_DIR)

import torch
from ultralytics import YOLO

MODEL_PATH = OUTPUT_DIR / "yolo_cls_runs" / "finance_5cls" / "weights" / "best.pt"
DEFAULT_PARENT_DIR = BASE_DIR / "demo_test"
OUTPUT_JSON_PATH = OUTPUT_DIR / "demo_test_classification_results.json"
IMG_SIZE = 224
BATCH_SIZE = 16
DEVICE = 0 if torch.cuda.is_available() else "cpu"

EN_LABELS = ["face_signing", "id_card_front", "id_card_back", "bank_statement", "contract"]
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def parse_args():
    parser = argparse.ArgumentParser(description="Batch predict subfolders with a YOLO classifier.")
    parser.add_argument(
        "parent_dir",
        nargs="?",
        default=None,
        help="父文件夹路径；其下每个一级子文件夹会作为一个业务文件夹处理。",
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_JSON_PATH),
        help="预测结果JSON输出路径。",
    )
    parser.add_argument(
        "--model",
        default=str(MODEL_PATH),
        help="YOLO五分类权重路径。",
    )
    return parser.parse_args()


def normalize_model_names(names):
    return names if isinstance(names, dict) else dict(enumerate(names))


def get_parent_dir(user_parent_dir):
    if user_parent_dir:
        return Path(user_parent_dir)
    return DEFAULT_PARENT_DIR


def get_case_dirs(parent_dir):
    return sorted(path for path in parent_dir.iterdir() if path.is_dir())


def get_image_paths(image_dir):
    return sorted(
        path
        for path in image_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def predict_batch(model, image_paths, parent_dir, case_dir, model_names, name_to_idx):
    predictions = []
    for i in range(0, len(image_paths), BATCH_SIZE):
        batch_paths = image_paths[i : i + BATCH_SIZE]
        results = model([str(path) for path in batch_paths], verbose=False, imgsz=IMG_SIZE, device=DEVICE)

        for path, result in zip(batch_paths, results):
            probs = result.probs.data.detach().cpu().numpy()
            pred_id = int(probs.argmax())
            pred_label = model_names[pred_id]
            confidence = float(probs[pred_id])

            predictions.append(
                {
                    "file_name": path.name,
                    "folder_name": case_dir.name,
                    "relative_path": path.relative_to(parent_dir).as_posix(),
                    "absolute_path": str(path),
                    "pred_label": pred_label,
                    "confidence": confidence,
                    "probabilities": {
                        label: float(probs[name_to_idx[label]])
                        for label in EN_LABELS
                    },
                }
            )
    return predictions


def summarize_case(predictions):
    counts = {label: 0 for label in EN_LABELS}
    for item in predictions:
        if item["pred_label"] in counts:
            counts[item["pred_label"]] += 1
    return counts


def main():
    args = parse_args()
    model_path = Path(args.model)
    parent_dir = get_parent_dir(args.parent_dir)
    output_path = Path(args.output)

    if not model_path.exists():
        raise FileNotFoundError(f"未找到模型权重: {model_path}")
    if not parent_dir.exists():
        raise FileNotFoundError(f"未找到父文件夹: {parent_dir}")

    print("=" * 80)
    print("YOLO五分类批量预测 Demo")
    print(f"模型: {model_path}")
    print(f"父文件夹: {parent_dir}")
    print(f"输出JSON: {output_path}")
    print(f"设备: {DEVICE}")
    print("=" * 80)

    model = YOLO(str(model_path))
    model_names = normalize_model_names(model.names)
    name_to_idx = {name: idx for idx, name in model_names.items()}
    missing_labels = [label for label in EN_LABELS if label not in name_to_idx]
    if missing_labels:
        raise ValueError(f"当前模型缺少五分类标签，无法输出五类概率: {missing_labels}")

    case_results = []
    total_images = 0
    case_dirs = get_case_dirs(parent_dir)

    for case_dir in case_dirs:
        image_paths = get_image_paths(case_dir)
        if not image_paths:
            case_results.append(
                {
                    "folder_name": case_dir.name,
                    "folder_path": str(case_dir),
                    "image_count": 0,
                    "class_counts": {label: 0 for label in EN_LABELS},
                    "images": [],
                }
            )
            continue

        predictions = predict_batch(model, image_paths, parent_dir, case_dir, model_names, name_to_idx)
        total_images += len(predictions)
        class_counts = summarize_case(predictions)

        case_results.append(
            {
                "folder_name": case_dir.name,
                "folder_path": str(case_dir),
                "image_count": len(predictions),
                "class_counts": class_counts,
                "images": predictions,
            }
        )

        print(f"\n子文件夹: {case_dir.name} ({len(predictions)} 张)")
        for item in predictions:
            print(f"  {item['file_name']} -> {item['pred_label']} ({item['confidence']:.4f})")

    output = {
        "metadata": {
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "model": str(model_path),
            "parent_dir": str(parent_dir),
            "labels": EN_LABELS,
            "folder_count": len(case_results),
            "total_images": total_images,
        },
        "folders": case_results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print(f"完整预测结果已保存: {output_path}")
    print(f"共处理 {len(case_results)} 个子文件夹, {total_images} 张图片")


if __name__ == "__main__":
    main()
