import sys
import serial
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt


# ==============================
# 🔷 Serial Thread
# ==============================
class SerialThread(QThread):
    data_received = pyqtSignal(str)

    def __init__(self, port, baud):
        super().__init__()
        self.port = port
        self.baud = baud
        self.running = True

    def run(self):
        try:
            ser = serial.Serial(self.port, self.baud, timeout=1)

            while self.running:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    self.data_received.emit(line)

        except Exception as e:
            self.data_received.emit(f"❌ Serial Error: {e}")

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


# ==============================
# 🔷 Main UI
# ==============================
class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Python Data Logger")
        self.showFullScreen()

        # 📁 File for logging
        self.log_file = open("data_log.txt", "a")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # =========================
        # 🔷 TITLE
        # =========================
        title = QLabel("PYTHON DATA LOGGER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px; font-weight: bold; color: #00ffc3;")
        main_layout.addWidget(title)

        # =========================
        # 🔷 STATUS
        # =========================
        self.status = QLabel("🔴 DISCONNECTED")
        self.status.setAlignment(Qt.AlignRight)
        self.status.setStyleSheet("font-size: 14px; color: red;")
        main_layout.addWidget(self.status)

        # =========================
        # 🔷 CONNECTION PANEL
        # =========================
        conn_card = QFrame()
        conn_card.setStyleSheet("""
            QFrame {
                background-color: #1c1c1c;
                border-radius: 15px;
                padding: 15px;
            }
        """)

        conn_layout = QHBoxLayout()

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("COM Port (COM3)")

        self.baud_input = QLineEdit()
        self.baud_input.setPlaceholderText("Baud Rate (115200)")

        self.connect_btn = QPushButton("CONNECT")
        self.disconnect_btn = QPushButton("DISCONNECT")

        conn_layout.addWidget(self.port_input)
        conn_layout.addWidget(self.baud_input)
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.disconnect_btn)

        conn_card.setLayout(conn_layout)
        main_layout.addWidget(conn_card)

        # =========================
        # 🔷 LOG PANEL
        # =========================
        log_card = QFrame()
        log_card.setStyleSheet("""
            QFrame {
                background-color: #1c1c1c;
                border-radius: 15px;
                padding: 10px;
            }
        """)

        log_layout = QVBoxLayout()

        log_label = QLabel("📡 LIVE DATA LOG")
        log_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.clear_btn = QPushButton("Clear Log")

        log_layout.addWidget(log_label)
        log_layout.addWidget(self.output)
        log_layout.addWidget(self.clear_btn)

        log_card.setLayout(log_layout)
        main_layout.addWidget(log_card)

        self.setLayout(main_layout)

        # =========================
        # 🔷 STYLE
        # =========================
        self.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #e0e0e0;
            font-family: Segoe UI;
        }

        QLineEdit {
            background-color: #2a2a2a;
            border: 1px solid #444;
            padding: 10px;
            border-radius: 10px;
        }

        QPushButton {
            background-color: #00c896;
            border-radius: 10px;
            padding: 10px;
            font-weight: bold;
            color: black;
        }

        QPushButton:hover {
            background-color: #00e6ac;
        }

        QTextEdit {
            background-color: #0d0d0d;
            border-radius: 10px;
            padding: 10px;
        }
        """)

        self.connect_btn.setStyleSheet("background-color: #28a745; color: white;")
        self.disconnect_btn.setStyleSheet("background-color: #dc3545; color: white;")

        # =========================
        # 🔷 SIGNALS
        # =========================
        self.connect_btn.clicked.connect(self.start_serial)
        self.disconnect_btn.clicked.connect(self.stop_serial)
        self.clear_btn.clicked.connect(self.output.clear)

        self.thread = None

    # =========================
    # 🔷 ESC to exit fullscreen
    # =========================
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.showNormal()

    # =========================
    def start_serial(self):
        try:
            port = self.port_input.text()
            baud = int(self.baud_input.text())

            self.thread = SerialThread(port, baud)
            self.thread.data_received.connect(self.update_log)
            self.thread.start()

            self.status.setText("🟢 CONNECTED")
            self.status.setStyleSheet("color: #00ff88;")

            self.output.append("Connected Successfully...\n")

        except Exception as e:
            self.output.append(f"❌ Error: {e}")

    # =========================
    def stop_serial(self):
        if self.thread:
            self.thread.stop()

            self.status.setText("🔴 DISCONNECTED")
            self.status.setStyleSheet("color: red;")

            self.output.append("Disconnected\n")

    # =========================
    def update_log(self, data):
        # 🕒 Current Date & Time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        final_data = f"[{timestamp}] {data}"

        # UI display
        self.output.append(final_data)

        # 💾 Save to file
        self.log_file.write(final_data + "\n")
        self.log_file.flush()


# ==============================
# 🔷 RUN
# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    sys.exit(app.exec_())