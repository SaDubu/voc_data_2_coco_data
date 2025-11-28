import os
import xml.etree.ElementTree as ET

# --- [필수 설정 부분] ---

# 1. XML 파일들의 최상위 루트 폴더 경로를 지정하세요. (예: './Training/label')
LABEL_ROOT_DIR = './Training/label'

# 2. 이미지가 저장된 폴더 이름 (label 폴더와 같은 레벨에 있다고 가정)
IMAGE_ROOT_NAME = 'image' 

# 3. Path 태그에 사용할 상대 경로 접두사 설정 (XML에서 이미지로 접근하기 위함)
# 예: XML이 label/sub에 있고, 이미지가 image/sub에 있다면, '../image/'
RELATIVE_PATH_PREFIX = f'../../{IMAGE_ROOT_NAME}/' 

# 1. XML 파일들의 최상위 루트 폴더 경로를 지정하세요. (예: './Validation/label')
V_LABEL_ROOT_DIR = './Validation/label'

# 2. 이미지가 저장된 폴더 이름 (label 폴더와 같은 레벨에 있다고 가정)
V_IMAGE_ROOT_NAME = 'image' 

# 3. Path 태그에 사용할 상대 경로 접두사 설정 (XML에서 이미지로 접근하기 위함)
# 예: XML이 label/sub에 있고, 이미지가 image/sub에 있다면, '../image/'
V_RELATIVE_PATH_PREFIX = f'../../{V_IMAGE_ROOT_NAME}/' 

# --- [XML 수정 함수] ---

def modify_xml_paths(xml_file_path, current_root_dir, path_prefix):
    """
    단일 XML 파일의 <folder>와 <path> 태그를 수정합니다.
    최상위 태그가 <comp_cd>이더라도 내부의 <annotation>을 찾아 처리합니다.
    """
    try:
        # XML 파일 파싱
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        # 1. <annotation> 태그를 찾습니다.
        # 최상위 태그가 <annotation>이 아니면 자식 중에서 <annotation>을 찾습니다.
        annotation_element = root
        if root.tag != 'annotation':
            annotation_element = root.find('annotation')
        
        if annotation_element is None:
            # <annotation> 태그를 찾지 못하면 건너뜁니다.
            print(f"  [오류 발생] 파일: {xml_file_path}, <annotation> 태그를 찾을 수 없습니다. 건너뜀.")
            return

        # 현재 XML 파일이 위치한 폴더 이름 추출 (예: '10060_해태포키블루베리41G')
        parent_folder_name = os.path.basename(current_root_dir)

        # 2. <filename> 태그를 찾습니다. (path 생성을 위해 필요)
        filename_tag = annotation_element.find('filename')
        if filename_tag is None or filename_tag.text is None:
            print(f"  [오류 발생] 파일: {xml_file_path}, <filename> 태그를 찾을 수 없습니다. 건너뜐.")
            return
        filename = filename_tag.text
            
        # 3. <folder> 태그 수정
        folder_tag = annotation_element.find('folder')
        if folder_tag is not None:
            # 새로운 상대 경로: ../../image/부모폴더/
            folder_tag.text = os.path.join(path_prefix, parent_folder_name).replace('\\', '/')

        # 4. <path> 태그 수정
        path_tag = annotation_element.find('path')
        if path_tag is not None:
            # 새로운 상대 경로 생성: ../../image/부모폴더/파일이름.jpg
            new_path = os.path.join(path_prefix, parent_folder_name, filename).replace('\\', '/')
            path_tag.text = new_path

        # 수정된 내용을 파일에 저장 (덮어쓰기)
        tree.write(xml_file_path, encoding='utf-8', xml_declaration=True)

    except Exception as e:
        print(f"  [오류 발생] 파일: {xml_file_path}, 오류: {e}")

def run(label_dir, path_prefix) :
    # --- [메인 실행 루프] ---
    print(f"--- XML 파일 경로 재귀적 수정 시작: {label_dir} ---")

    # os.walk를 사용하여 label_dir 아래 모든 폴더를 탐색
    xml_count = 0
    for root_dir, dirs, files in os.walk(label_dir):
        for filename in files:
            if filename.endswith('.xml'):
                file_path = os.path.join(root_dir, filename)
                
                # 현재 XML 파일의 위치(root_dir)와 파일 경로를 수정 함수에 전달
                modify_xml_paths(file_path, root_dir, path_prefix)
                xml_count += 1
                print(f'\r {xml_count} ing~~', end='')

    print(f"\n--- 총 {xml_count}개의 XML 파일 경로 수정 완료되었습니다. ---")

if __name__ == '__main__':
    run(LABEL_ROOT_DIR, RELATIVE_PATH_PREFIX)
    run(V_LABEL_ROOT_DIR, V_RELATIVE_PATH_PREFIX)