import subprocess
import os
import sys

# 실행할 스크립트 파일 목록
SCRIPTS = [
    'xml_path_set.py',
    'trans_coco.py',
    'coco_setting_train.py',
    'create_data_yaml.py'
]

def run_script(script_name):
    """지정된 Python 스크립트를 실행하고 출력을 CMD에 실시간으로 표시합니다."""
    print(f"\n========================================================")
    print(f"▶️ 스크립트 실행 시작: {script_name}")
    print(f"========================================================")
    
    try:
        # subprocess.run을 사용하여 스크립트를 실행합니다.
        # stdout=sys.stdout, stderr=sys.stderr
        # 현재 CMD 창에 실시간으로 스트림합니다.
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            text=True
        )
        
        print(f"\n✅ 스크립트 실행 성공: {script_name}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ 오류 발생: {script_name}이(가) 비정상 종료되었습니다. (Exit Code: {e.returncode})")
        return False
        
    except FileNotFoundError:
        print(f"\n❌ 오류 발생: {script_name} 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return False

def main():
    """모든 스크립트를 순차적으로 실행하는 메인 함수."""
    
    print(f"현재 작업 디렉터리: {os.getcwd()}")
    
    for script in SCRIPTS:
        if not run_script(script):
            print("\n========================================================")
            print(f"🚨 파이프라인 중단: {script} 실행 중 오류가 발생하여 다음 스크립트는 실행되지 않습니다.")
            print("========================================================")
            break
    else:
        print("\n========================================================")
        print("🎉 모든 스크립트가 성공적으로 순차 실행 완료되었습니다.")
        print("========================================================")

if __name__ == "__main__":
    main()