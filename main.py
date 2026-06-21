import sys
import random
import signal
import os
from datetime import datetime
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QTransform

_FLIP_TRANSFORM = QTransform().scale(-1, 1)  # 재사용할 좌우 반전 변환


def resource_path(relative_path):
    """ PyInstaller 빌드 환경과 일반 개발 환경(VS Code)의 경로를 모두 지원하는 함수 """
    try:
        # PyInstaller가 실행 시 임시로 압축을 푸는 내부 디렉터리 경로
        base_path = sys._MEIPASS
    except Exception:
        # VS Code 등 일반 파이썬 실행 환경일 때의 현재 경로
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class DesktopPet(QMainWindow):
    LAY_DOWN_WEIGHT = 3  # lay_down이 다른 행동보다 이 배수만큼 더 잘 뽑힘

    def __init__(self):
        super().__init__()
        
        self.cols = 3  
        self.rows = 4

        self.actions = {
            "walk": (0, 2),         
            "rightRodao": (4, 4),    
            "leftRodao": (6, 6),     
            "stop": (5, 5),          
            "lay_down": (7, 9)   
        }

        self.speeds = {
            "walk": 200,        
            "rightRodao": 500,
            "leftRodao": 500,
            "stop": 1500,
            "lay_down": 5000
        }

        self.move_speed = 1
        self.move_interval_ms = 50  # walk일 때만 도는 이동 타이머 주기

        self.direction_x = random.choice([-1, 1])
        self.direction_y = random.choice([-1, 1])
        
        self.current_action = random.choice(["walk", "lay_down"])
        self.start_frame, self.end_frame = self.actions[self.current_action]
        self.current_frame = self.start_frame
        self.reset_action_duration()
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        self.pet_label = QLabel(self)
        self.pet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(self.pet_label)
        
        self.display_size = 350
        self.resize(self.display_size, self.display_size)
        
        screen = QApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        
        start_x = random.randint(0, self.screen_width - self.display_size)
        start_y = random.randint(0, self.screen_height - self.display_size)
        self.move(start_x, start_y)
        
        self.full_sprite_sheet = QPixmap(resource_path("assets/sprites.png"))

        if self.full_sprite_sheet.isNull():
            print("오류: 이미지를 불러올 수 없습니다. 프로그램을 종료합니다.", file=sys.stderr)
            sys.exit(1)

        self.frame_width = self.full_sprite_sheet.width() // 3
        self.frame_height = self.full_sprite_sheet.height() // 4

        self._frame_cache = {}  # (프레임, 방향) -> 가공된 QPixmap 캐시
        self._last_drawn_key = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(self.speeds[self.current_action])

        self._move_timer = QTimer(self)
        self._move_timer.setInterval(self.move_interval_ms)
        self._move_timer.timeout.connect(self._move_step)
        if self.current_action == "walk":
            self._move_timer.start()

        self._drag_active = False
        self._drag_offset = QPoint()

        self.popup = None  # 우클릭 시 _ensure_popup에서 지연 생성

        self.update_pet_image()

    def _ensure_popup(self):
        if self.popup is not None:
            return

        self.popup = QWidget()
        self.popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        layout = QVBoxLayout(self.popup)
        layout.setContentsMargins(0, 0, 0, 0)

        quit_btn = QPushButton("X")
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                width: 14px;
                height: 14px;
                color: white;
                border-radius: 7px;
                font-size: 13px;
            }
            QPushButton:hover {
                border: 1px solid #aaaaaa;
                background-color: rgba(255, 255, 255, 30);
            }
        """)

        quit_btn.clicked.connect(QApplication.quit)
        layout.addWidget(quit_btn)
        self.popup.setLayout(layout)

    def _get_processed_frame(self, frame_index, direction_x):
        key = (frame_index, direction_x)
        cached = self._frame_cache.get(key)
        if cached is not None:
            return cached

        row = frame_index // self.cols
        col = frame_index % self.cols

        cropped_pixmap = self.full_sprite_sheet.copy(
            QRect(col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)
        )

        if direction_x == -1:
            cropped_pixmap = cropped_pixmap.transformed(_FLIP_TRANSFORM)

        scaled_pixmap = cropped_pixmap.scaled(
            self.display_size, self.display_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )

        self._frame_cache[key] = scaled_pixmap
        return scaled_pixmap

    def update_pet_image(self):
        key = (self.current_frame, self.direction_x)
        if key == self._last_drawn_key:
            return  

        pixmap = self._get_processed_frame(self.current_frame, self.direction_x)
        self.pet_label.setPixmap(pixmap)
        self._last_drawn_key = key

    def next_frame(self):
        if self.start_frame == self.end_frame:
            self.current_frame = self.start_frame  
        else:
            self.current_frame = random.randint(self.start_frame, self.end_frame)

        self.action_duration -= 1
        if self.action_duration <= 0:
            self.switch_action()

        self.update_pet_image()

    def _move_step(self):
        if not self._drag_active and self.current_action == "walk":
            next_x = self.pos().x() + (self.move_speed * self.direction_x)
            next_y = self.pos().y() + (self.move_speed * self.direction_y)

            if next_x < 0:
                next_x = 0
                self.direction_x = 1
            elif next_x > self.screen_width - self.display_size:
                next_x = self.screen_width - self.display_size
                self.direction_x = -1

            if next_y < 0:
                next_y = 0
                self.direction_y = 1
            elif next_y > self.screen_height - self.display_size:
                next_y = self.screen_height - self.display_size
                self.direction_y = -1

            self.move(next_x, next_y)

    def _pick_action(self, options):
        weights = [self.LAY_DOWN_WEIGHT if opt == "lay_down" else 1 for opt in options]
        return random.choices(options, weights=weights)[0]

    def switch_action(self):
        old_action = self.current_action
        hour = datetime.now().hour
        is_night = 22 <= hour or hour < 6

        if old_action in ["rightRodao", "leftRodao"]:
            self.current_action = random.choice(["walk", "stop"])
        elif old_action == "stop":
            if is_night:
                self.current_action = self._pick_action(["lay_down", "stop", "walk"])
            else:
                self.current_action = self._pick_action(["walk", "rightRodao", "leftRodao", "lay_down"])
        elif old_action == "walk":
            if is_night:
                self.current_action = self._pick_action(["stop", "lay_down"])
            else:
                if self.direction_x == 1:
                    self.current_action = self._pick_action(["rightRodao", "lay_down", "stop"])
                else:
                    self.current_action = self._pick_action(["leftRodao", "lay_down", "stop"])
        elif old_action == "lay_down":
            if is_night:
                self.current_action = self._pick_action(["lay_down", "stop"])
            else:
                self.current_action = random.choice(["walk", "stop"])

        self.start_frame, self.end_frame = self.actions[self.current_action]
        self.current_frame = self.start_frame
        self.reset_action_duration()
        self.timer.setInterval(self.speeds[self.current_action])

        if self.current_action == "walk":
            self.direction_x = random.choice([-1, 1])
            self.direction_y = random.choice([-1, 1])
            if not self._drag_active:
                self._move_timer.start()
        else:
            self._move_timer.stop()  

    def reset_action_duration(self):
        if self.current_action in ["rightRodao", "leftRodao", "stop"]:
            self.action_duration = random.randint(1, 1)
        elif self.current_action == "lay_down":
            self.action_duration = random.randint(15, 30)
        else:
            self.action_duration = random.randint(15, 25)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = True
            self.timer.stop()
            self._move_timer.stop()
            self._drag_offset = event.globalPosition().toPoint() - self.pos()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._ensure_popup()
            self.popup.move(event.globalPosition().toPoint())
            self.popup.show()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
            self.timer.start(self.speeds[self.current_action])
            if self.current_action == "walk":
                self._move_timer.start()
            event.accept()

    def nativeEvent(self, eventType, message):
        return False, 0


def _lower_process_priority():
    try:
        import psutil
        p = psutil.Process()
        if sys.platform == "win32":
            p.nice(psutil.IDLE_PRIORITY_CLASS)
        else:
            p.nice(10)
    except ImportError:
        print(
            "psutil이 설치되어 있지 않아 프로세스 우선순위를 낮추지 못했습니다 "
            "(선택 사항이며, 실행에는 문제 없음. 'pip install psutil'로 설치 가능).",
            file=sys.stderr,
        )
    except Exception as e:
        print(f"프로세스 우선순위 설정 실패 (무시하고 계속 진행): {e}", file=sys.stderr)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    _lower_process_priority()
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())