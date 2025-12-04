import os
import yaml
import shutil
from typing import List
from pathlib import Path

# --- [Configuration Section] ---
# 1. 'label' 폴더와 'image' 폴더가 들어있는 최상위 폴더 경로
BASE_DIR = './Training' 

V_BASE_DIR = './Validation' 

CLASSES_TEXT_FILE = 'classes.txt'

FILE_PATH = os.path.join(BASE_DIR, CLASSES_TEXT_FILE)

V_FILE_PATH = os.path.join(V_BASE_DIR, CLASSES_TEXT_FILE)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_YAML_PATH = os.path.join(CURRENT_DIR, 'data.yaml')

TRAIN_TEXT_PATH = os.path.join(CURRENT_DIR, 'train.txt')

VALID_TEXT_PATH =  os.path.join(CURRENT_DIR, 'valid.txt')

def get_classes_list(path, classes_list) :
    """
    주어진 경로(path)의 텍스트 파일을 읽어와서, 각 줄을 classes_list에 추가합니다.
    
    Args:
        path (str): 읽어올 텍스트 파일의 경로.
        classes_list (list): 파일의 내용(각 줄)을 추가할 리스트.

    Returns:
        int: 파일 읽기가 성공하면 0을 반환하고, 실패하면 1을 반환합니다.
    """
    
    # 1. 파일이 존재하는지 확인
    if not os.path.exists(path):
        print(f"오류: 지정된 파일 경로가 존재하지 않습니다. -> {path}")
        return 1
        
    try:
        # 2. 파일을 '읽기' 모드('r')로 열고 UTF-8 인코딩을 지정
        with open(path, 'r', encoding='utf-8') as f:
            # 3. 파일의 모든 줄을 순회
            for line in f:
                classes_list.append(line)   
        
        # 5. 성공적으로 처리되면 0 반환
        return 0
        
    except Exception as e:
        # 6. 파일 처리 중 예외 발생 시 오류 메시지 출력 후 1 반환
        print(f"오류: 파일 처리 중 예외가 발생했습니다. -> {e}")
        return 1
    
def is_same_list(list_a, list_b) :
    len_a = len(list_a)
    len_b = len(list_b)

    if len_a != len_b :
        return False
    
    len_a = len(list_a)
    len_b = len(list_b)

    for i in range (len_a) :
        if list_a[i] == list_b[i] :
            continue
        return False 
    return True

def long_list(list_a, list_b) :
    list_t = None
    list_s = None
    len_a = len(list_a)
    len_b = len(list_b)

    if len_a > len_b :
        list_t = list_a
        list_s = list_b
    elif len_a < len_b :
        list_t = list_b
        list_s = list_a
    
    return list_t, list_s

def find_folders_to_delete(root_dir, target_list):
    """
    ROOT_DIR 직계 하위 폴더 중 이름이 조건에 맞는 폴더를 찾습니다.
    """
    folders_to_delete = []

    print(f"--- [탐색 시작] {root_dir} 폴더 내부 검사 ---")

    # image와 label 폴더 경로 설정
    image_dir = Path(root_dir) / 'image'
    label_dir = Path(root_dir) / 'label'
    label_coco_dir = Path(root_dir) / 'label_coco'
    
    # 검사할 디렉토리 리스트
    search_dirs = [image_dir, label_dir, label_coco_dir]

    print("--- [탐색 시작] image/ label/ label_coco/ 폴더 검사 ---")
    
    for current_search_dir in search_dirs:
        if not current_search_dir.is_dir():
            print(f"⚠️ 경고: {current_search_dir} 경로를 찾을 수 없습니다. 건너뜁니다.")
            continue
            
        print(f"🔎 {current_search_dir} 폴더 내부를 검사합니다...")

        now_path = Path(current_search_dir)
    
        for item_name in os.listdir(now_path):
            # 1. 전체 경로 생성
            full_path = now_path / item_name
            
            # 2. 파일이 아닌 '디렉토리(폴더)'인지 확인
            if full_path.is_dir():
                
                # 3. 폴더 이름에서 첫 번째 '_'를 기준으로 분리
                parts = item_name.split('_', 1)
                
                # 언더바가 있고, 그 뒤에 문자열이 있을 경우만 검사
                if len(parts) == 2 and parts[1] != '':
                    suffix = parts[1] # 접미사 (예: '4' 또는 '5')
                    
                    # 4. 접미사(suffix)가 target_list에 있는지 확인
                    if suffix in target_list:
                        print(f"✅ 삭제 대상 폴더 발견: {full_path}")
                        folders_to_delete.append(str(full_path))
    
    return folders_to_delete

def execute_deletion(folders_to_delete):
    """
    폴더 리스트에 있는 모든 폴더와 그 내용을 삭제합니다.
    """
    if not folders_to_delete:
        print("삭제할 대상 폴더가 없습니다.")
        return

    print("\n--- [위험] 실제 폴더 삭제를 시작합니다 ---")
    
    for folder_path in folders_to_delete:
        try:
            # rmtree는 폴더와 그 안의 모든 파일/폴더를 재귀적으로 삭제합니다.
            shutil.rmtree(folder_path)
            print(f"🗑️ 성공적으로 삭제됨: {folder_path}")
        except Exception as e:
            print(f"❌ 삭제 실패 ({folder_path}): {e}")

def difference_data(list_a, list_b) :
    c = set(list_a).difference(set(list_b))
    list_c = list(c)

    list_c = [item.strip() for item in list_c]
    
    return list_c

def write_data_yaml(
    classes_list: List[str], 
    output_filename: str = DATA_YAML_PATH,
    path: str = './', 
    train_file: str = TRAIN_TEXT_PATH, 
    val_file: str = VALID_TEXT_PATH
) -> None:
    """
    Args:
        classes_list (List[str]): 클래스 이름이 순서대로 저장된 리스트.
        output_filename (str): 생성할 YAML 파일의 이름. 기본값은 DATA_YAML_PATH.
        path (str): 데이터셋의 루트 경로. 기본값은 './'.
        train_file (str): 훈련용 이미지/라벨 목록 파일. 기본값은 'train.txt'.
        val_file (str): 검증용 이미지/라벨 목록 파일. 기본값은 'valid.txt'.
    """

    classes_list = [item.strip() for item in classes_list]
    
    # 1. 'names' 딕셔너리 생성
    names_dict = {i: name for i, name in enumerate(classes_list)}
    
    # 2. nc (Number of Classes) 설정
    nc_value = len(classes_list)

    # 3. 최종 YAML 데이터 구조 정의
    yaml_data = {
        'path': path,
        'train': train_file,
        'val': val_file,
        'nc': nc_value,
        'names': names_dict
    }

    # 4. YAML 파일로 저장
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            # default_flow_style=False는 딕셔너리를 {키: 값} 대신 
            # 줄바꿈된 깔끔한 블록 스타일로 출력하도록 합니다.
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True)
            
        print(f"✅ YAML 설정 파일이 성공적으로 생성되었습니다: {output_filename}")
        print(f"   (총 클래스 개수: {nc_value})")
        
    except Exception as e:
        print(f"❌ YAML 파일 작성 중 오류가 발생했습니다: {e}")
    
if __name__ == '__main__':
    label_list = []
    v_label_list = []
    get_classes_list(FILE_PATH, label_list)
    get_classes_list(V_FILE_PATH, v_label_list)

    if not(is_same_list(label_list, v_label_list)) :
        list_a, list_b = long_list(label_list, v_label_list)
        list_c = difference_data(list_a, list_b)
        remove_folder = find_folders_to_delete(BASE_DIR, list_c)
        execute_deletion(remove_folder)
        remove_folder = find_folders_to_delete(V_BASE_DIR, list_c)
        execute_deletion(remove_folder)

    write_data_yaml(label_list)