import sys
import random
import signal
from datetime import datetime
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QWidget, QVBoxLayout
from PySide6.QtGui import QPixmap, QTransform

class DesktopPet(QMainWindow):
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
            "lay_down": 1000
        }
        
        self.move_speed = 3
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
        
        self.full_sprite_sheet = QPixmap("assets/sprites.png")
        
        if not self.full_sprite_sheet.isNull():
            self.frame_width = self.full_sprite_sheet.width() // 3
            self.frame_height = self.full_sprite_sheet.height() // 4
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(self.speeds[self.current_action])

        self._move_timer = QTimer(self)
        self._move_timer.setInterval(16)
        self._move_timer.timeout.connect(self._move_step)
        self._move_timer.start()
        
        self._drag_active = False
        self._drag_offset = QPoint()

        # ✅ 커스텀 팝업 (투명 배경)
        self.popup = QWidget()
        self.popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.popup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        layout = QVBoxLayout(self.popup)
        layout.setContentsMargins(0, 0, 0, 0)

        quit_btn = QPushButton("❌")
        quit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #888888;
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
        
        self.update_pet_image()

    def update_pet_image(self):
        if self.full_sprite_sheet.isNull():
            self.pet_label.setText("이미지를 찾을 수 없습니다.")
            return

        row = self.current_frame // self.cols
        col = self.current_frame % self.cols
        
        cropped_pixmap = self.full_sprite_sheet.copy(
            QRect(col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height)
        )
        
        if self.direction_x == -1:
            cropped_pixmap = cropped_pixmap.transformed(QTransform().scale(-1, 1))
        
        self.pet_label.setPixmap(cropped_pixmap.scaled(
            self.display_size, self.display_size, 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        ))

    def next_frame(self):
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

    def switch_action(self):
        old_action = self.current_action
        hour = datetime.now().hour
        is_night = 22 <= hour or hour < 6
        
        if old_action in ["rightRodao", "leftRodao"]:
            self.current_action = random.choice(["walk", "stop"])
        elif old_action == "stop":
            if is_night:
                self.current_action = random.choice(["lay_down", "stop", "walk"])
            else:
                self.current_action = random.choice(["walk", "rightRodao", "leftRodao", "lay_down"])
        elif old_action == "walk":
            if is_night:
                self.current_action = random.choice(["stop", "lay_down"])
            else:
                if self.direction_x == 1:
                    self.current_action = random.choice(["rightRodao", "lay_down", "stop"])
                else:
                    self.current_action = random.choice(["leftRodao", "lay_down", "stop"])
        elif old_action == "lay_down":
            if is_night:
                self.current_action = random.choice(["lay_down", "stop"])
            else:
                self.current_action = random.choice(["walk", "stop"])
            
        self.start_frame, self.end_frame = self.actions[self.current_action]
        self.current_frame = self.start_frame
        self.reset_action_duration()
        self.timer.setInterval(self.speeds[self.current_action])
        if self.current_action == "walk":
            self.direction_x = random.choice([-1, 1])
            self.direction_y = random.choice([-1, 1])

    def reset_action_duration(self):
        if self.current_action in ["rightRodao", "leftRodao", "stop"]:
            self.action_duration = random.randint(1, 1) 
        elif self.current_action == "lay_down":
            self.action_duration = random.randint(5, 10)
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
            self._move_timer.start()
            event.accept()

    def nativeEvent(self, eventType, message):
        return False, 0

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())