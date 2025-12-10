import cv2
import os
import numpy as np

def detect_changes(before_path, after_path, output_path):
    
    before = cv2.imread(before_path)
    after  = cv2.imread(after_path)

    b_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    a_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    diff = cv2.absdiff(b_gray, a_gray)

    _, thresh = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)

    kernel = np.ones((7, 7), np.uint8)
    clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    annotated = after.copy()
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        if w * h < 300:
            continue

        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 3)

    cv2.imwrite(output_path, annotated)


def main():
    input_folder = r"D:/dec_ds_2024/Assignment/Task_2_input_file/input-images"
    files = os.listdir(input_folder)

    
    before_files = [f for f in files if "~2" not in f and f.endswith(".jpg")]

    for bf in before_files:
        base = bf.replace(".jpg", "")
        before_path = os.path.join(input_folder, bf)

        after_name = base + "~2.jpg"
        after_path = os.path.join(input_folder, after_name)

        
        if not os.path.exists(after_path):
            continue

        output_name = base + "~3.jpg"
        output_path = os.path.join(input_folder, output_name)

        print(f"Processing → {bf} & {after_name}")
        detect_changes(before_path, after_path, output_path)

    print("Task 2 completed successfully!")


if __name__ == "__main__":
    main()
