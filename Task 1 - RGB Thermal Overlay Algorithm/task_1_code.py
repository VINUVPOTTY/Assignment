import cv2
import numpy as np
import os
import shutil

def detect_pole_bbox(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80,
                            minLineLength=150, maxLineGap=20)

    if lines is None:
        h, w = img.shape[:2]
        return int(w*0.35), 0, int(w*0.3), h

    verticals = []
    for x1, y1, x2, y2 in lines[:,0]:
        if abs(x1 - x2) < 20: 
            verticals.append((x1, y1, x2, y2))

    if not verticals:
    
        h, w = img.shape[:2]
        return int(w*0.35), 0, int(w*0.3), h

    xs = [v[0] for v in verticals]
    pole_x = int(np.median(xs))

    h, w = img.shape[:2]

    bw = int(w * 0.25)  
    left = max(0, pole_x - bw//2)
    width = bw

    return left, 0, width, h

def align_local_ecc(thermal_crop, rgb_crop):
   
    t_gray = cv2.cvtColor(thermal_crop, cv2.COLOR_BGR2GRAY)
    r_gray = cv2.cvtColor(rgb_crop, cv2.COLOR_BGR2GRAY)

    t_gray = t_gray.astype(np.float32) / 255.0
    r_gray = r_gray.astype(np.float32) / 255.0

    warp_matrix = np.eye(2, 3, dtype=np.float32)

    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
                100, 1e-6)

    try:
        cc, warp_matrix = cv2.findTransformECC(
            r_gray, t_gray, warp_matrix,
            cv2.MOTION_AFFINE, criteria, None, 5
        )
        return warp_matrix

    except:
        return np.eye(2, 3, dtype=np.float32)

def align_full_thermal(thermal, rgb):
    h, w = rgb.shape[:2]

    x, y, w_crop, h_crop = detect_pole_bbox(rgb)

    rgb_crop  = rgb[y:y+h_crop, x:x+w_crop]
    thr_crop  = thermal[y:y+h_crop, x:x+w_crop]

    if thr_crop.size == 0:
        return thermal.copy()

    M = align_local_ecc(thr_crop, rgb_crop)
    M_full = np.eye(3, dtype=np.float32)
    M_full[0:2, :] = M

    aligned = cv2.warpPerspective(
        thermal, M_full, (w, h),
        flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP
    )

    return aligned

def process_task1(input_folder, output_folder="task_1_output"):
    os.makedirs(output_folder, exist_ok=True)

    files = os.listdir(input_folder)
    thermal_files = [f for f in files if f.upper().endswith("_T.JPG")]
    rgb_files     = [f for f in files if f.upper().endswith("_Z.JPG")]

    for tfile in thermal_files:
        base = tfile[:-6]
        expected_rgb = base + "_Z.JPG"

        rfile = next((x for x in rgb_files if x.upper() == expected_rgb.upper()), None)
        if rfile is None:
            print("Missing RGB for:", tfile)
            continue

        print("Processing:", base)

        thermal = cv2.imread(os.path.join(input_folder, tfile))
        rgb     = cv2.imread(os.path.join(input_folder, rfile))

        if thermal is None or rgb is None:
            print("Read error:", base)
            continue
        aligned_thermal = align_full_thermal(thermal, rgb)

        shutil.copy(
            os.path.join(input_folder, rfile),
            os.path.join(output_folder, f"{base}_Z.JPG")
        )

        
        cv2.imwrite(
            os.path.join(output_folder, f"{base}_AT.JPG"),
            aligned_thermal
        )

    print("\nTask 1 Completed Successfully.")

if __name__ == "__main__":
    input_folder = r"D:/dec_ds_2024/Assignment/Task 1 - RGB Thermal Overlay Algorithm/input-images"
    process_task1(input_folder)
