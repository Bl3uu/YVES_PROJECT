import sys
import os
import asyncio
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap
import edge_tts
import soundfile as sf
import sounddevice as sd

class AudioTTSWorker(QThread):
    speaking_started = pyqtSignal()
    audio_amplitude = pyqtSignal(float)
    speaking_finished = pyqtSignal()

    def __init__(self, voice: str = "en-GB-SoniaNeural", pitch: str = "+10Hz", rate: str = "+6%"):
        super().__init__()
        self.voice = voice
        self.pitch = pitch
        self.rate = rate
        self.text_queue = []
        self._is_running = True

    def queue_speech(self, text: str):
        self.text_queue.append(text)

    async def _synthesize_and_play(self, text: str):
        temp_mp3 = "temp_output.mp3"
        # Apply pitch and rate settings here
        communicate = edge_tts.Communicate(text, self.voice, pitch=self.pitch, rate=self.rate)
        await communicate.save(temp_mp3)

        audio_data, samplerate = sf.read(temp_mp3, dtype="float32")
        
        if len(audio_data.shape) > 1:
            mono_data = audio_data.mean(axis=1)
        else:
            mono_data = audio_data

        self.speaking_started.emit()

        sd.play(audio_data, samplerate=samplerate)

        chunk_size = 1024
        total_samples = len(mono_data)
        current_idx = 0

        while sd.get_stream().active and current_idx < total_samples:
            chunk = mono_data[current_idx : current_idx + chunk_size]
            if len(chunk) > 0:
                rms = np.sqrt(np.mean(chunk**2))
                self.audio_amplitude.emit(rms * 10000)
            
            current_idx += chunk_size
            self.msleep(23)

        sd.wait()
        self.speaking_finished.emit()

        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self._is_running:
            if self.text_queue:
                text = self.text_queue.pop(0)
                loop.run_until_complete(self._synthesize_and_play(text))
            else:
                self.msleep(100)

class YvesDesktopOverlay(QWidget):
    def __init__(self, voice_name: str = "en-GB-SoniaNeural"):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.sprites = {
            "idle": QPixmap("assets/yves_idle.png"),
            "thinking": QPixmap("assets/yves_thinking.png"),
            "speak_open": QPixmap("assets/yves_speaking_open.png"),
            "speak_closed": QPixmap("assets/yves_speaking_closed.png"),
        }

        self.image_label = QLabel(self)
        self.image_label.setPixmap(self.sprites["idle"])

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)
        
        # Move to bottom right corner of primary screen
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 450, screen.height() - 550)

        # Worker initialization
        self.tts_worker = AudioTTSWorker(voice=voice_name)
        self.tts_worker.speaking_started.connect(lambda: self.set_sprite("speak_closed"))
        self.tts_worker.audio_amplitude.connect(self.handle_amplitude)
        self.tts_worker.speaking_finished.connect(lambda: self.set_sprite("idle"))
        self.tts_worker.start()

        self.old_pos = None

    def set_sprite(self, state_key: str):
        if state_key in self.sprites:
            self.image_label.setPixmap(self.sprites[state_key])

    def handle_amplitude(self, rms: float):
        if rms > 150:
            self.set_sprite("speak_open")
        else:
            self.set_sprite("speak_closed")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def contextMenuEvent(self, event):
        # Right-click to exit overlay
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Voices you can try: "en-GB-SoniaNeural", "en-GB-MaisieNeural", "en-US-AshleyNeural"
    overlay = YvesDesktopOverlay(voice_name="en-GB-SoniaNeural")
    overlay.show()

    QTimer.singleShot(2000, lambda: overlay.tts_worker.queue_speech("System initialised. How may I assist you today?"))

    sys.exit(app.exec())