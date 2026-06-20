import sys
import random
import signal
from datetime import datetime
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
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
            "lay_down": 1000 # 이후에 10000으로 바꾸기 (1분)
        }
        
        self.move_speed = 3   
        self.direction_x = random.choice([-1, 1])
        
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
        
        self.display_size = 750 
        self.resize(self.display_size, self.display_size)
        
        screen = QApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        self.move(random.randint(100, self.screen_width - 300), screen.height() - 750)
        
        self.full_sprite_sheet = QPixmap("assets/sprites.png")
        
        if not self.full_sprite_sheet.isNull():
            self.frame_width = self.full_sprite_sheet.width() // 3
            self.frame_height = self.full_sprite_sheet.height() // 4 
        
        # 애니메이션 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(self.speeds[self.current_action])

        # 이동 전용 타이머 (16ms = 60fps로 부드럽게 이동)
        self._move_timer = QTimer(self)
        self._move_timer.setInterval(16)
        self._move_timer.timeout.connect(self._move_step)
        self._move_timer.start()
        
        self._drag_active = False
        self._drag_offset = QPoint()
        
        self.update_pet_image()
        
    def get_time_based_action(self):
        hour = datetime.now().hour
        if 22 <= hour or hour < 6:
            # 밤: 눕기나 멈춤 위주
            return random.choice(["lay_down", "stop", "lay_down"])
        elif 6 <= hour < 9:
            # 아침: 천천히 시작
            return random.choice(["walk", "stop"])
        else:
            # 낮: 활발하게
            return random.choice(["walk", "lay_down"])

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
            if next_x < -50:
                next_x = -50
                self.direction_x = 1
            elif next_x > self.screen_width - self.display_size + 50:
                next_x = self.screen_width - self.display_size + 50
                self.direction_x = -1
            self.move(next_x, self.pos().y())

    def switch_action(self):
        all_actions = ["walk", "rightRodao", "leftRodao", "stop", "lay_down"]

        old_action = self.current_action
        hour = datetime.now().hour
        is_night = 22 <= hour or hour < 6
        
        if old_action in ["rightRodao", "leftRodao"]:
            self.current_action = random.choice(["walk", "stop"])
        elif old_action == "stop":
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
            self.current_action = random.choice(["walk", "stop"])
            
        self.start_frame, self.end_frame = self.actions[self.current_action]
        self.current_frame = self.start_frame

        self.reset_action_duration()
        self.timer.setInterval(self.speeds[self.current_action])
        if self.current_action == "walk":
            self.direction_x = random.choice([-1, 1])

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