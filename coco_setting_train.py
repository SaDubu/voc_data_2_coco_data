import os
import shutil
import tempfile

import cv2
import os
import glob

from PIL import Image

BASE_DIR = './Training' 
# 2. XML 파일 입력 폴더
LABEL_ROOT_DIR = os.path.join(BASE_DIR, 'label_coco') 
# 3. YOLO TXT 파일 출력 폴더
OUTPUT_ROOT_DIR = os.path.join('./labels', 'train') 

# 소스 경로: image 폴더 (BASE_DIR과 동일 레벨에 있다고 가정)
SOURCE_DIR = os.path.join(BASE_DIR, 'image') 

# 대상 경로: image_coco 폴더 (BASE_DIR과 동일 레벨에 생성/사용)
TARGET_DIR = os.path.join('./images', 'train')

V_BASE_DIR = './Validation' 
# 2. XML 파일 입력 폴더
V_LABEL_ROOT_DIR = os.path.join(V_BASE_DIR, 'label_coco') 
# 3. YOLO TXT 파일 출력 폴더
V_OUTPUT_ROOT_DIR = os.path.join('./labels', 'valid') 

# 소스 경로: image 폴더 (BASE_DIR과 동일 레벨에 있다고 가정)
V_SOURCE_DIR = os.path.join(V_BASE_DIR, 'image') 

# 대상 경로: image_coco 폴더 (BASE_DIR과 동일 레벨에 생성/사용)
V_TARGET_DIR = os.path.join('./images', 'valid')

def cp_file(origin_path, mv_path):
    # 대상 폴더가 없으면 생성합니다.
    os.makedirs(mv_path, exist_ok=True)
    print(f"대상 폴더: '{mv_path}' 준비 완료.")
    print("-" * 30)

    # 3. 파일 복사 프로세스
    total_copied = 0

    # os.walk를 사용하여 origin pathdhk 그 하위의 모든 폴더를 탐색합니다.
    for root, dirs, files in os.walk(origin_path):
        for filename in files:
            if 'meta' in filename.lower():
                    continue
            # 원본 파일의 전체 경로
            source_file_path = os.path.join(root, filename)
            
            # 대상 파일의 전체 경로 (mv_path 바로 아래에 복사)
            target_file_path = os.path.join(mv_path, filename)
            
            try:
                # shutil.copy2는 파일의 메타데이터(수정 시간 등)도 함께 복사합니다.
                shutil.copy2(source_file_path, target_file_path)
                total_copied += 1
                # 진행 상황을 한 줄에 표시
                print(f'\r✅ 복사 완료: {total_copied}개 파일 ({filename})', end='')
                
            except Exception as e:
                    print(f"\n❌ 오류 발생 - 파일 복사 실패: {source_file_path} -> {e}")

    print(f"\n\n--- 총 {total_copied}개의 .jpg 파일이 '{mv_path}' 폴더로 복사 완료되었습니다. ---")

def get_filename_without_extension(filename):
    """
    확장자가 포함된 파일 이름에서 확장자를 제거한 파일 이름만 반환합니다.
    예: 'image_01.jpg' -> 'image_01'
    """
    # os.path.splitext()를 사용하여 이름과 확장자를 분리하고, 이름 부분만 반환
    result = os.path.splitext(filename)[0]
    return result

def sync_list_a_by_list_b(list_a, list_b):
    """
    list_a를 list_b를 기준으로 동기화합니다. 
    list_a 요소의 확장자 미포함 이름이 list_b의 확장자 미포함 이름 목록에 없으면 list_a에서 해당 요소를 제거합니다.

    Args:
        list_a (list): 동기화할 대상 리스트 (원본이 수정됨).
        list_b (list): 비교 기준이 되는 리스트.

    Returns:
        list: 동기화되어 수정된 list_a (list_a와 동일한 객체).
    """
    # 1. 비교 기준이 되는 list_b의 '확장자 미포함' 파일 이름 집합(Set) 생성
    # Set을 사용하면 요소 존재 여부를 O(1)의 속도로 빠르게 확인할 수 있습니다.
    b_names_set = {get_filename_without_extension(name) for name in list_b}

    # 2. list_a를 순회하며 동기화 (원본 리스트를 수정하므로 역순 순회가 안전합니다)
    i = len(list_a) - 1
    while i >= 0:
        filename_a = list_a[i]
        name_a_without_ext = get_filename_without_extension(filename_a)
        
        # list_a의 파일 이름이 list_b 이름 목록에 없으면 제거
        if name_a_without_ext not in b_names_set:
            list_a.pop(i) # 해당 인덱스의 요소 제거
            print(f"  제거됨: {filename_a} (이유: '{name_a_without_ext}'가 기준 리스트에 없음)")
        
        i -= 1
        
    return list_a

def secure_file_sync_and_cleanup(origin_dir, files_to_keep_list):
    """
    files_to_keep_list에 있는 파일만 남기고, origin_dir의 나머지 파일을 정리합니다.
    임시 폴더를 사용한 안전한 이동/복구 방식을 사용합니다.

    Args:
        origin_dir (str): 파일들이 위치한 원본 디렉토리 경로.
        files_to_keep_list (list): 삭제하지 않고 남겨야 할 파일 이름 (확장자 포함) 리스트.
    """
    print(f"\n--- 안전한 파일 정리 시작: {origin_dir} ---")
    
    # 1. 임시 작업 폴더 생성
    # tempfile.mkdtemp()는 OS의 임시 디렉토리에 고유한 이름의 폴더를 생성합니다.
    temp_dir = tempfile.mkdtemp(prefix='yolo_sync_temp_', dir=origin_dir)
    print(f"📦 임시 저장 폴더 생성: {temp_dir}")

    # 2. 남겨야 할 파일들을 임시 폴더로 이동 (KEEP)
    moved_count = 0
    files_to_move = {} # key: 원본 경로, value: 임시 경로 (복구를 위해 저장)

    try:
        # origin_dir을 순회하며 남겨야 할 파일을 찾습니다.
        for root, _, files in os.walk(origin_dir):
            if root == temp_dir: # 임시 폴더가 origin_dir의 하위에 있는 경우 건너뜁니다.
                continue

            for filename in files:

                if filename in files_to_keep_list:
                    original_path = os.path.join(root, filename)
                    temp_path = os.path.join(temp_dir, filename)
                    
                    # shutil.move: 파일 이동
                    shutil.move(original_path, temp_path)
                    files_to_move[temp_path] = original_path # 복구 정보를 저장
                    moved_count += 1
        
        print(f"✅ 1단계 완료: 남길 파일 {moved_count}개를 임시 폴더로 이동했습니다.")
        
        # 3. 원본 폴더의 나머지 파일 삭제 (CLEANUP)
        deleted_count = 0
        
        # 임시 폴더로 이동된 파일은 이제 원본 폴더에 없습니다.
        # os.walk를 다시 실행하여 남아있는 파일(삭제 대상)을 찾습니다.
        for root, _, files in os.walk(origin_dir):
            if root == temp_dir:
                 continue
                 
            for filename in files:
                # 남아있는 모든 파일이 삭제 대상입니다.
                full_file_path = os.path.join(root, filename)
                os.remove(full_file_path)
                # print(f"🗑️ 삭제: {full_file_path}")
                deleted_count += 1
                
        print(f"✅ 2단계 완료: 원본 폴더에서 {deleted_count}개 불필요 파일 삭제 완료.")

        # 4. 파일 복구 및 임시 폴더 삭제 (RESTORE & REMOVE)
        restored_count = 0
        for temp_path, original_path in files_to_move.items():
            shutil.move(temp_path, original_path)
            restored_count += 1

        print(f"✅ 3단계 완료: {restored_count}개 파일 원본 위치로 복구 완료.")
        
    finally:
        # 에러 발생 여부와 관계없이 임시 폴더는 반드시 삭제
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"🔥 4단계 완료: 임시 폴더 삭제 ({temp_dir})")

    print("\n--- 안전한 파일 정리 및 복구 작업 완료 ---")

def create_image_paths_txt(images_list, output_filename="paths.txt"):
    """
    주어진 파일명 리스트를 기반으로 각 파일 앞에 경로를 붙여 TXT 파일을 생성합니다.

    Args:
        images_list (list): 확장자 포함 파일명 리스트 (예: ['cat_01.jpg', 'dog_02.png']).
        output_filename (str): 생성할 TXT 파일의 이름.
    """
    # 1. .을 기준으로 문자열을 나눔: ['train', 'txt']
    parts = output_filename.split('.')

    # 2. 첫 번째 원소(인덱스 0)를 선택
    result = parts[0]

    # 현재 스크립트가 실행되는 디렉토리
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_dir, output_filename)
    
    # TXT 파일에 들어갈 기본 경로 접두사
    path_prefix = "./images/" + result + "/" 
    
    total_entries = 0
    
    print(f"\n--- 경로 파일 생성 시작: {output_filename} ---")
    
    try:
        # 파일을 쓰기 모드 ('w')로 엽니다. (파일이 존재하면 내용을 덮어씁니다.)
        with open(output_path, 'w', encoding='utf-8') as f:
            for filename in images_list:
                # 2. 경로와 파일명을 결합합니다.
                full_path_entry = f"{path_prefix}{filename}\n"
                
                # 3. 파일에 기록합니다.
                f.write(full_path_entry)
                total_entries += 1
        
        print(f"✅ 파일 생성 완료: {output_path}")
        print(f"총 {total_entries}개의 이미지 경로가 기록되었습니다.")
        
    except Exception as e:
        print(f"❌ 파일 작성 중 오류 발생: {e}")
 
# 목표 해상도 (가로, 세로)
TARGET_SIZE = (640, 640) 

def img_resize(target_dir) :
        # TARGET_DIR 내의 모든 jpg 및 jpeg 파일 목록을 가져옵니다.
        image_extensions = ('.jpg', '.jpeg') # 검색하려는 확장자들을 소문자로 정의

        image_files = []
        for filename in os.listdir(target_dir):
            # 파일 확장자를 소문자로 변환하여 일치하는지 확인
            if filename.lower().endswith(image_extensions):
                file_path = os.path.join(target_dir, filename)
                image_files.append(file_path)

        total_images = len(image_files)

        if total_images == 0:
            print(f"❌ '{target_dir}' 경로에서 JPG/JPEG 파일을 찾을 수 없습니다.")
        else:
            print(f"총 {total_images}개의 이미지를 {TARGET_SIZE[0]}x{TARGET_SIZE[1]}로 리사이징 시작...")
            
            for i, file_path in enumerate(image_files):
                # 덮어쓰기이므로 input_path와 output_path가 동일합니다.
                output_path = file_path 
                filename = os.path.basename(file_path)

                try:
                    img = cv2.imread(file_path)
                    
                    if img is None:
                        print(f"  > 경고: '{filename}' 파일을 읽을 수 없습니다.")
                        continue

                    # 이미지 리사이징
                    resized_img = cv2.resize(img, TARGET_SIZE, interpolation=cv2.INTER_LINEAR)
                    
                    # 원본 파일 경로에 덮어쓰기 저장
                    cv2.imwrite(output_path, resized_img)

                    if (i + 1) % 100 == 0 or (i + 1) == total_images:
                        print(f"\r  > 진행률: {i + 1}/{total_images}개 이미지 덮어쓰기 완료.", end='')

                except Exception as e:
                    print(f"  > 오류 발생: '{filename}' 덮어쓰기 중 문제 발생: {e}")

            print("-" * 40)
            print("✅ 모든 이미지 파일 덮어쓰기 완료.") 

def make_list(target_dir, filename_list) :
    # os.walk를 사용하여 origin pathdhk 그 하위의 모든 폴더를 탐색합니다.
    for root, dirs, files in os.walk(target_dir):
        for filename in files:  
            filename_list.append(filename)     

def run(source_dir, target_dir, label_dir, output_dir, txt_filename):
    images_list = []
    cp_file(source_dir, target_dir)
    print('image cp complate')
    img_resize(target_dir)
    print('image 640X640 complate')
    make_list(target_dir, images_list)

    labels_list = []
    cp_file(label_dir, output_dir)
    print('label cp complate')
    make_list(label_dir, labels_list)

    labels_list = sync_list_a_by_list_b(labels_list, images_list)
    images_list = sync_list_a_by_list_b(images_list, labels_list)

    secure_file_sync_and_cleanup(output_dir, labels_list)
    secure_file_sync_and_cleanup(target_dir, images_list)

    create_image_paths_txt(images_list, txt_filename)
    
if __name__ == '__main__':
    run(SOURCE_DIR, TARGET_DIR, LABEL_ROOT_DIR, OUTPUT_ROOT_DIR, 'train.txt')
    run(V_SOURCE_DIR, V_TARGET_DIR, V_LABEL_ROOT_DIR, V_OUTPUT_ROOT_DIR, 'valid.txt')