"""Compatibility entry for the YOLO five-class baseline.

Training and testing have been split into separate files:
- baseline_classify_YOLO_train.py
- baseline_classify_YOLO_test.py
"""
from baseline_classify_YOLO_train import main


if __name__ == "__main__":
    main()
