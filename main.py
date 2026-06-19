import sys
import random
import signal
from PySide6.QtCore import Qt, QTimer, QRect, QPoint
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtGui import QPixmap, QFont, QTransform

class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.cols = 3  
        self.actions = {
            "walk": (0, 2),         
            "rightRodao": (3, 3),    
            "leftRodao": (4, 4),     
            "stop": (5, 5),          
            "lay_down": (7, 9)       
        }
        
        self.speeds = {
            "walk": 1000,
            "rightRodao": 500,
            "leftRodao": 500,
            "stop": 1000,
            "lay_down": 10000
        }
        
        self.move_speed = 12  
        self.direction_x = random.choice([-1, 1])
        
        self.current_action = random.choice(["walk", "lay_down"])
        self.start_frame, self.end_frame = self.actions[self.current_action]
        self.current_frame = self.start_frame
        self.reset_action_duration()
        
        # 최상단 투명 윈도우 설정
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        self.pet_label = QLabel(self)
        self.pet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 마우스 드래그 부분 수정 필요
        self.pet_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
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
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(self.speeds[self.current_action]) 
        
        self.update_pet_image()
        self._drag_active = False
        self.drag_position = QPoint()


    def update_pet_image(self):
        if self.full_sprite_sheet.isNull():
            self.pet_label.setText("🐴 이미지를 찾을 수 없습니다.")
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
            Qt.TransformationMode.SmoothTransformation
        ))


    def next_frame(self):
        self.current_frame += 1
        if self.current_frame > self.end_frame:
            self.current_frame = self.start_frame
        
        # 드래그 중일 때는 코드가 말의 위치를 강제로 움직이지 못하게 차단
        if not self._drag_active and self.current_action in ["walk", "rightRodao", "leftRodao"]:
            next_x = self.pos().x() + (self.move_speed * self.direction_x)
            if next_x < -50:
                next_x = -50
                self.direction_x = 1
            elif next_x > self.screen_width - self.display_size + 50:
                next_x = self.screen_width - self.display_size + 50
                self.direction_x = -1
            self.move(next_x, self.pos().y())
        
        self.action_duration -= 1
        if self.action_duration <= 0:
            self.switch_action()
            
        self.update_pet_image()


    def switch_action(self):
        old_action = self.current_action
        if old_action == "walk":
            self.current_action = random.choice(["rightRodao", "leftRodao", "lay_down", "stop"])
        elif old_action in ["rightRodao", "leftRodao", "stop"]:
            self.current_action = random.choice(["walk", "lay_down"])
        elif old_action == "lay_down":
            self.current_action = "walk"
            
        self.start_frame, self.end_frame = self.actions[self.current_action]
        self.current_frame = self.start_frame
        
        self.reset_action_duration()
        self.timer.setInterval(self.speeds[self.current_action])
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
            # 현재 창의 절대 좌표와 마우스 좌표 간격 저장
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and (event.buttons() & Qt.MouseButton.LeftButton):
            # 마우스가 움직이는 대로 창 위치 강제 동기화
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
            event.accept()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())