import os
import yaml
from typing import List

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
    
    for i in range (len_a) :
        if list_a[i] == list_b[i] :
            continue
        return False 
    return True

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
    
    # 1. 'names' 딕셔너리 생성
    # 클래스 리스트를 순회하며 인덱스(0부터 시작)를 키로, 클래스 이름을 값으로 하는 딕셔너리를 만듭니다.
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
        print('classes file error, please check file')
        print(f'Train classes file {FILE_PATH}')
        print(f'valid classes file {V_FILE_PATH}')
        exit()

    write_data_yaml(label_list)