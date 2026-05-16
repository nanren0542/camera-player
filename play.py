import sys
import cv2
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *

class CameraWorker(QThread):
    frame_ready = Signal(QImage)
    record_status = Signal(bool)

    def __init__(self):
        super().__init__()
        self.cap = None
        self.running = False
        self.recording = False
        self.out = None
        self.WIDTH = 1280
        self.HEIGHT = 720
        self.FPS = 25

    def start_camera(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, self.FPS)
        self.running = True
        self.start()

    def start_record(self):
        if self.recording:
            return
        # 真正的 H.264 编码器（avc1）
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        self.out = cv2.VideoWriter(
            "camera_recording_h264.mp4",
            fourcc,
            self.FPS,
            (self.WIDTH, self.HEIGHT)
        )
        if not self.out.isOpened():
            print("❌ H.264 编码器初始化失败，请检查 OpenH264 库")
            self.out = None
            return
        self.recording = True
        self.record_status.emit(True)

    def stop_record(self):
        self.recording = False
        self.record_status.emit(False)
        QTimer.singleShot(100, self._release_writer)

    def _release_writer(self):
        if self.out:
            self.out.release()
            self.out = None
            print("✅ 录像文件已保存")

    def stop_camera(self):
        self.running = False
        self.wait()
        if self.cap:
            self.cap.release()
        self.stop_record()

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            if self.recording and self.out is not None:
                self.out.write(frame)

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.frame_ready.emit(q_img)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 摄像头播放器（自适应版）")
        self.resize(1280, 800)

        # 显示画面：设置为自动拉伸
        self.label = QLabel()
        self.label.setStyleSheet("background-color: black;")
        self.label.setAlignment(Qt.AlignCenter)
        # 关键：让QLabel的图像自动拉伸填充
        self.label.setScaledContents(True)

        self.status_label = QLabel("状态：未启动")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.btn_play = QPushButton("打开摄像头")
        self.btn_stop = QPushButton("停止摄像头")
        self.btn_record = QPushButton("开始录像")
        self.btn_stop_record = QPushButton("停止录像")

        layout = QVBoxLayout()
        layout.addWidget(self.label, stretch=1)  # 关键：给画面区域分配最大空间
        layout.addWidget(self.status_label)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_play)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_record)
        btn_layout.addWidget(self.btn_stop_record)
        layout.addLayout(btn_layout)

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

        self.worker = CameraWorker()
        self.worker.frame_ready.connect(self.update_frame)
        self.worker.record_status.connect(self.update_record_status)

        self.btn_play.clicked.connect(self.worker.start_camera)
        self.btn_stop.clicked.connect(self.worker.stop_camera)
        self.btn_record.clicked.connect(self.worker.start_record)
        self.btn_stop_record.clicked.connect(self.worker.stop_record)

    def update_frame(self, img):
        self.label.setPixmap(QPixmap.fromImage(img))
        self.status_label.setText("状态：摄像头运行中")

    def update_record_status(self, is_recording):
        if is_recording:
            self.status_label.setText("状态：录像中...")
        else:
            self.status_label.setText("状态：摄像头运行中（录像已停止）")

    def closeEvent(self, event):
        self.worker.stop_camera()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())