# jeju-park
**Desktop Pet Widget for Windows (.exe)**   
SSB3aXNoIHlvdSB3ZXJlIGhlcmUh
   
노트북이나 PC를 사용하는 동안 화면에 존재하며 돌아다니는 데스크톱 펫

<br>
<br>

## 1. 주요 기능 및 특징

* **화면 위 상주**: 다른 창에 가려지지 않고 항상 최상단(`WindowStaysOnTopHint`)에 위치
* **자유로운 이동**: 마우스 왼쪽 버튼으로 펫을 원하는 위치로 드래그할 수 있음
* **다양한 행동 패턴**: 시간대(낮/밤)와 이전 행동을 기반으로 걷기(`walk`), 제자리 회전(`rightRodao`/`leftRodao`), 정지(`stop`), 눕기(`lay_down`) 등의 상태를 스스로 판단하여 전환함
* **간편한 종료**: 펫을 마우스 우클릭하면 나타나는 종료 버튼(`✕`)을 통해 앱을 끌 수 있음

<br>
<br>

## 2. 기술 스택 및 구조

* **Language**: Python 3
* **Framework**: PySide6 (Qt6)

<br>
<br>

## 3. 개발 환경 세팅 및 도구 설치

**파이썬 가상환경 생성**

```
python -m venv env
```
<br>

**가상환경 활성화**

```
# Windows (cmd)
env\Scripts\activate.bat

# Windows (PowerShell)
env\Scripts\Activate.ps1

# WSL / macOS / Linux
source env/bin/activate
```
<br>

**필수 라이브러리 설치**

```
pip install PySide6 pyinstaller psutil
```

`psutil`은 필수는 아니고, 백그라운드 실행 시 프로세스 우선순위를 낮춰서 다른 작업과 CPU를 덜 경합하게 하는 용도(선택)로 씀.

<br>
<br>

## 4. 실행 방법
```
git clone <레포 주소>
cd jeju-park
python -m venv env
env\Scripts\activate.bat        # Windows 기준
python main.py
```
<br>

**exe 파일로 빌드하기**
프로젝트 폴더에 포함된 배치 파일을 실행하면 자동으로 빌드

```
build_exe.bat
```
빌드 완료 후 다른 PC로 이동하거나 배포할 때는 dist\DesktopPet 폴더 전체를 같이 옮겨야 정상적으로 실행됩니다.

<br>
<br>

## 5. 윈도우 시작 프로그램으로 등록하기

1. `dist\DesktopPet\DesktopPet.exe`의 바로가기를 만든다 (우클릭 → 바로가기 만들기).
2. `Win + R` → `shell:startup` 입력 후 엔터 (시작 프로그램 폴더가 열림).
3. 만들어둔 바로가기를 이 폴더에 복사한다.
4. 다음 로그인부터 자동 실행됨. 해제하려면 같은 폴더에서 바로가기만 삭제하면 됨.
