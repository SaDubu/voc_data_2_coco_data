import xml.etree.ElementTree as ET
import os
import shutil

import create_data_yaml as cdy
import coco_setting_train as cst

# --- [Configuration Section] ---
# 1. 'label' 폴더와 'image' 폴더가 들어있는 최상위 폴더 경로
BASE_DIR = './Training' 
# 2. XML 파일 입력 폴더
LABEL_ROOT_DIR = os.path.join(BASE_DIR, 'label') 
# 3. YOLO TXT 파일 출력 폴더
OUTPUT_ROOT_DIR = os.path.join(BASE_DIR, 'label_coco') 

V_BASE_DIR = './Validation' 
# 2. XML 파일 입력 폴더
V_LABEL_ROOT_DIR = os.path.join(V_BASE_DIR, 'label') 
# 3. YOLO TXT 파일 출력 폴더
V_OUTPUT_ROOT_DIR = os.path.join(V_BASE_DIR, 'label_coco') 

# --- [Utility Functions] ---
def find_classes_from_folder_name(root_dir):
    """
    지정된 루트 폴더(LABEL_ROOT_DIR)의 하위 폴더 이름을 스캔하여
    'ID_클래스이름' 형식에서 ID와 첫 번째 '_'를 제외한 전체 문자열을 클래스 이름으로 추출합니다.
    (속도를 최우선으로 하며, 폴더 이름과 XML <name> 태그가 일치한다고 가정합니다.)
    """
    unique_classes = set()
    folder_count = 0
    skipped_folder_count = 0 
    print(f"\n--- 폴더 이름 기반 클래스 이름 추출 시작: {root_dir} ---")
    
    # root_dir의 바로 아래에 있는 서브 폴더들만 확인
    for item in os.listdir(root_dir):
        sub_folder_path = os.path.join(root_dir, item)
        
        # item이 디렉토리인지 확인
        if os.path.isdir(sub_folder_path):
            folder_count += 1
            folder_name = item
            class_name_extracted = False
            
            # 폴더 이름에 '_'가 있는지 확인
            if '_' in folder_name:
                # split('_', 1): 첫 번째 '_'에서만 분할하며, [-1]은 그 뒤의 모든 문자열을 가져옵니다.
                class_name = folder_name.split('_', 1)[-1].strip()
                unique_classes.add(class_name)
                class_name_extracted = True
            else:
                # '_'가 없는 경우, 폴더 이름을 그대로 클래스 이름으로 사용
                unique_classes.add(folder_name.strip())
                class_name_extracted = True
            
            if not class_name_extracted:
                 skipped_folder_count += 1
                
    # 추출된 클래스 리스트를 알파벳/가나다 순으로 정렬하여 반환 (인덱스 고정 위함)
    class_list = sorted(list(unique_classes)) 
    print(f"--- 총 {folder_count}개 폴더 중 클래스 이름 추출 완료.")
    print(f"--- 추출 로직에서 스킵된 폴더 수: {skipped_folder_count}개")
    print(f"--- 추출된 고유 클래스 수: {len(class_list)}개")
    return class_list


def convert_box(size, box):
    """
    Pascal VOC 좌표 (xmin, xmax, ymin, ymax)를 YOLO 정규화 좌표 (x_center, y_center, w, h)로 변환합니다.
    """
    dw, dh = 1. / size[0], 1. / size[1]
    
    # AI Hub 데이터는 보통 1-based이므로, -1을 적용합니다.
    x = (box[0] + box[1]) / 2.0 - 1 
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    
    x_center = x * dw
    y_center = y * dh
    width = w * dw
    height = h * dh
    
    # 결과가 0.0 ~ 1.0 범위를 벗어나지 않도록 클리핑 (정규화된 좌표의 필수 조건)
    x_center = max(0.0, min(x_center, 1.0))
    y_center = max(0.0, min(y_center, 1.0))
    width = max(0.0, min(width, 1.0))
    height = max(0.0, min(height, 1.0))
    
    return x_center, y_center, width, height

def process_conversion(xml_file_path, output_dir, classes_list):
    """
    단일 XML 파일을 YOLO TXT 파일로 변환하여 지정된 출력 폴더에 저장합니다.
    """
    try:
        # 1. XML 파일 파싱 및 기본 정보 추출
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        # 출력 파일 경로 설정 (예: 10060_0_m_1.txt)
        img_filename = root.find('filename').text
        out_filename = os.path.splitext(img_filename)[0] + '.txt'
        out_file_path = os.path.join(output_dir, out_filename)
        
        # 2. 이미지 크기 추출
        size = root.find('size')
        w = int(size.find('width').text)
        h = int(size.find('height').text)

        # 3. TXT 파일 작성
        with open(out_file_path, 'w') as out_file:
            for obj in root.iter('object'):
                cls_name = obj.find('name').text.strip()
                
                # 'difficult' 태그가 있으면 1인 경우 건너뛰기
                difficult_tag = obj.find('difficult')
                if difficult_tag is not None and int(difficult_tag.text) == 1:
                    continue

                try:
                    # 동적으로 생성된 CLASSES 리스트에서 인덱스 찾기
                    cls_id = classes_list.index(cls_name) 
                except ValueError:
                    print(f"  [경고] 알 수 없는 클래스 '{cls_name}'가 발견되어 건너뜁니다. 파일: {xml_file_path}")
                    continue

                # 4. 바운딩 박스 추출 및 변환
                xmlbox = obj.find('bndbox')
                box = [float(xmlbox.find(x).text) for x in ('xmin', 'xmax', 'ymin', 'ymax')]
                bb = convert_box((w, h), box)
                
                # TXT 파일에 저장 (인덱 x_center y_center w h)
                out_file.write(f"{cls_id} {bb[0]:.6f} {bb[1]:.6f} {bb[2]:.6f} {bb[3]:.6f}\n")
        
    except Exception as e:
        print(f"[오류] 파일 처리 실패 ({xml_file_path}): {e}")

def create_classes_file(label_dir, base_dir) :
    # 1. XML 스캔 및 CLASSES 리스트 동적 생성
    #CLASSES = find_all_unique_classes(LABEL_ROOT_DIR)
    classes = find_classes_from_folder_name(label_dir)
    # 주의: 이 목록을 그대로 YOLOv5의 data.yaml 파일의 'names' 섹션에 사용해야 합니다!

    # BASE_DIR 경로에 classes.txt 파일로 CLASSES 리스트 저장
    try:
        classes_output_path = os.path.join(base_dir, 'classes.txt')
            
        with open(classes_output_path, 'w', encoding='utf-8') as f:
            for class_name in classes:
                f.write(f"{class_name}\n") # 각 클래스 이름을 한 줄씩 저장
        print(f"✅ CLASSES 리스트를 '{classes_output_path}'에 성공적으로 저장했습니다.")
        
    except Exception as e:
        print(f"❌ classes.txt 파일 저장 중 오류 발생: {e}")

    return classes

def run(label_dir, ouput_dir, base_dir) :  
    classe_label = create_classes_file(label_dir, base_dir)

    print(f"\n--- XML to YOLO TXT 변환 시작 ---")
    print(f"입력 경로: {label_dir}")
    print(f"출력 경로: {ouput_dir}")
    
    # 2. 출력 폴더 생성
    os.makedirs(ouput_dir, exist_ok=True)
    
    total_files = 0
    
    # 3. 변환 프로세스 시작
    for root_dir, dirs, files in os.walk(label_dir):
        relative_path = os.path.relpath(root_dir, label_dir)
        current_output_dir = os.path.join(ouput_dir, relative_path)
        
        # 출력 폴더 구조 유지
        if not os.path.exists(current_output_dir):
            os.makedirs(current_output_dir, exist_ok=True)

        for filename in files:
            if filename.endswith('.xml'):
                if 'meta' in filename.lower():
                    continue

                xml_file_path = os.path.join(root_dir, filename)
                # 동적 생성된 CLASSES 리스트를 process_conversion 함수에 전달
                process_conversion(xml_file_path, current_output_dir, classe_label) 
                total_files += 1

                print(f'\r {total_files} ing ~~~', end='')

    print(f"\n--- 총 {total_files}개의 XML 파일이 YOLO TXT로 변환 완료되었습니다. ---")
# --- [Main Execution Loop] ---
if __name__ == '__main__':
    label_list = create_classes_file(LABEL_ROOT_DIR, BASE_DIR)
    v_label_list = create_classes_file(V_LABEL_ROOT_DIR, V_BASE_DIR)

    if not(cdy.is_same_list(label_list, v_label_list)) :
        list_a, list_b = cdy.long_list(label_list, v_label_list)
        list_c = cdy.difference_data(list_a, list_b)
        remove_folder = cdy.find_folders_to_delete(BASE_DIR, list_c)
        cdy.execute_deletion(remove_folder)
        remove_folder = cdy.find_folders_to_delete(V_BASE_DIR, list_c)
        cdy.execute_deletion(remove_folder)

    run(LABEL_ROOT_DIR, OUTPUT_ROOT_DIR, BASE_DIR)
    run(V_LABEL_ROOT_DIR, V_OUTPUT_ROOT_DIR, V_BASE_DIR)