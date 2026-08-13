"""Evaluate the trained YOLO five-class classifier on a held-out split."""
from yolo_classify_common import (
    EVAL_SPLIT,
    classify_images,
    evaluate_classification,
    load_split_frames,
    load_trained_model,
    print_accuracy_summary,
    save_results,
)


def main():
    print("=" * 60)
    print("Step 1: 测试金融影像五分类模型 (YOLO Classification)")
    print(f"评估数据集: {EVAL_SPLIT}")
    print("=" * 60)

    split_frames = load_split_frames()
    eval_df = split_frames[EVAL_SPLIT].copy()
    print(f"\n仅在 {EVAL_SPLIT} 集上计算最终指标: {len(eval_df)} 张")

    model = load_trained_model()
    y_pred, y_probs = classify_images(model, eval_df)
    y_true = eval_df["image_type"].values

    print_accuracy_summary(y_true, y_pred, EVAL_SPLIT.capitalize())
    metrics = evaluate_classification(y_true, y_pred)
    save_results(eval_df, y_pred, y_probs, metrics, output_prefix=EVAL_SPLIT)

    print("\n测试完成。")


if __name__ == "__main__":
    main()
