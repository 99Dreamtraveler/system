"""Train the YOLO five-class financial image classifier."""
from yolo_classify_common import (
    EN_LABELS,
    PRETRAINED_CLS_MODEL,
    classify_images,
    load_data,
    prepare_yolo_cls_dataset,
    print_accuracy_summary,
    train_model,
)


def main():
    print("=" * 60)
    print("Step 1: 训练金融影像五分类模型 (YOLO Classification)")
    print(f"类别: {', '.join(EN_LABELS)}")
    print(f"分类预训练模型: {PRETRAINED_CLS_MODEL}")
    print("=" * 60)

    df = load_data()
    data_dir, split_frames = prepare_yolo_cls_dataset(df)
    model = train_model(data_dir)

    val_df = split_frames["val"].copy()
    print(f"\n在 val 集上计算训练后准确率: {len(val_df)} 张")
    y_pred, _ = classify_images(model, val_df)
    y_true = val_df["image_type"].values
    print_accuracy_summary(y_true, y_pred, "Validation")

    print("\n训练完成。请运行 baseline_classify_YOLO_test.py 在 test 集上评估指标。")


if __name__ == "__main__":
    main()
