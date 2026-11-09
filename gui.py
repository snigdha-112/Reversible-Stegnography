
import sys
import subprocess
import wave
import numpy as np
from PIL import Image
import cv2
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget,
    QVBoxLayout, QLabel, QPushButton,
    QLineEdit, QFileDialog, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class SteganographyTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Steganography Tool")
        self.setMinimumSize(800, 600)
        
        tabs = QTabWidget()
        tabs.addTab(self.build_embedding_tab(), "Embedding")
        tabs.addTab(self.build_extraction_tab(),"Extraction")
        tabs.addTab(self.build_detection_tab(), "Detection")
        
        self.setCentralWidget(tabs)
        

    def build_embedding_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.cover_path = QLineEdit()
        self.cover_path.setPlaceholderText("Select cover file...")
        cover_btn = QPushButton("Browse Cover File")
        cover_btn.clicked.connect(self.browse_cover)

        self.secret_path = QLineEdit()
        self.secret_path.setPlaceholderText("Select secret image...")
        secret_btn = QPushButton("Browse Secret Image")
        secret_btn.clicked.connect(self.browse_secret)

        self.media_type = QComboBox()
        self.media_type.addItems(["Image", "Audio", "Video"])

        self.embed_passphrase = QLineEdit()
        self.embed_passphrase.setPlaceholderText("Enter passphrase...")
        self.embed_passphrase.setEchoMode(QLineEdit.Password)

        embed_btn = QPushButton("Hide Secret Image")
        embed_btn.clicked.connect(self.embed)

        self.embed_status = QLabel("Status: Ready")

        layout.addWidget(QLabel("Cover File:"))
        layout.addWidget(self.cover_path)
        layout.addWidget(cover_btn)
        layout.addWidget(QLabel("Secret Image:"))
        layout.addWidget(self.secret_path)
        layout.addWidget(secret_btn)
        layout.addWidget(QLabel("Media Type:"))
        layout.addWidget(self.media_type)
        layout.addWidget(QLabel("Passphrase:"))
        layout.addWidget(self.embed_passphrase)
        layout.addWidget(embed_btn)
        layout.addWidget(self.embed_status)

        tab.setLayout(layout)
        return tab

    def browse_cover(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Cover File", "",
            "All Files (*.jpg *.bmp *.wav *.avi)"
        )
        if file:
            self.cover_path.setText(file)

    def browse_secret(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Secret Image", "",
            "Images (*.jpg *.png *.bmp)"
        )
        if file:
            self.secret_path.setText(file)
    def bit_encrypt(self, image_path, key, output_path):
        img = Image.open(image_path).convert("RGB")
        pixels = np.array(img, dtype=np.uint8)
        encrypted = ((pixels ^ key) << 2) & 0xFF
        encrypted_img = Image.fromarray(encrypted.astype(np.uint8))
        encrypted_img.save(output_path)
        return output_path 
    def bit_decrypt(self, image_path, key, output_path):
        img= Image.open(image_path).convert("RGB")
        pixels = np.array(img, dtype=np.uint8)
        decrypted = (pixels >> 2) ^ key
        decrypted_img = Image.fromarray(decrypted.astype(np.uint8))
        decrypted_img.save(output_path)
        return output_path
                                        

    def embed(self):
        try:
            cover = self.cover_path.text()
            secret = self.secret_path.text()
            passphrase = self.embed_passphrase.text()
            media = self.media_type.currentText()
            if media == "Image":
                self.embed_status.setText("Status: Bit encrypting secret image..")
                cover = cover.replace("/", "\\")
                secret = secret.replace("/", "\\")
                img = Image.open(secret).convert("RGB")
                width, height = img.size
                if width >100 or height > 100:
                    img =img.resize((100,100))
                    temp_resized = secret + "_resized.png"
                    img.save(temp_resized)
                    source = temo_resized
                else:
                    source = secret

                encrypted_secret = secret +"_bitenc.png"
                key = sum(ord(C) for c in passphrase) % 256
                self.bit_encrypt(source, key, encrypted_secret)
                self.embed_status.setText("Hiding encryptes image..")
                openstego_jar = r"C:\Users\SNIGDHA\OneDrive\Desktop\stegnoproject1\openstego-0.8.6\openstego-0.8.6\lib\openstego.jar"
                cover = cover.replace("/","\\")
                encrypted_secret = encrypted_secret.replace("/","\\")
                output = cover.rsplit(".",1)[0] + "_stego.png"
                stego_cmd = [
                    "java","-jar",openstego_jar,
                    "embed","-a","RandomLSB",
                    "-mf", encrypted_secret,
                    "-cf", cover,
                    "-sf", output
                    ]
                stego_result = subprocess.run(stego_cmd, capture_output=True, text=True)
                if stego_result.returncode == 0:
                    print("Saved at:", output)
                    self.embed_status.setText("Done! saved as" + output)
                    print("Stego return code:", stego_result.returncode)
                    print("Stego STDOUT:", stego_result.stdout)
                    print("Stego STDERR:", stego_result.stderr)
                    print("Output path:", output)
                else:
                    self.embed_status.setText("Embedding Error -" + stego_result.stderr)
            elif media == "Audio":
                self.embed_status.setText("Hiding image in audio..")
                cover = cover.replace("/", "\\")
                secret = secret.replace("/","\\")
                
                audio = wave.open(cover, "rb")
                frames = audio.readframes(audio.getnframes())
                channels = audio.getnchannels()
                sampwidth = audio.getsampwidth()
                framerate = audio.getframerate()
                sample = np.frombuffer(frames, dtype=np.int16).copy()
                audio.close()
                print("Channels:", channels)
                print("Sample width:", sampwidth)
                print("Frame rate:", framerate)
                print("Sample length:", len(sample))
                secret_img = Image.open(secret).convert("RGB")
                secret_img = secret_img.resize((50,50))
                secret_pixels = np.array(secret_img).flatten()
                width_bin = format(50, '016b')
                height_bin = format(50, '016b')
                secret_bin = width_bin + height_bin
                for pixel_val in secret_pixels:
                    secret_bin += format(pixel_val, '08b')
                if len(secret_bin) > len(sample):
                    self.embed_status.setText("Error - Audio file is too small!")
                    return
                for i in range(len(secret_bin)):
                    sample_bin = format(int(sample[i]) & 0xFFFF, '016b')
                    new_sample_bin = sample_bin[:-1] + secret_bin[i]
                    sample[i] = np.int16(np.uint16(int(new_sample_bin, 2)))
                output = cover.rsplit(".",1)[0] + "_stego.wav"
                stego_audio = wave.open(output, "wb")
                stego_audio.setnchannels(channels)
                stego_audio.setsampwidth(sampwidth)
                stego_audio.setframerate(framerate)
                stego_audio.writeframes(sample.tobytes())
                stego_audio.close()
                self.embed_status.setText(" Done! Saved as" + output)
                
            elif media == "Video":
                self.embed_status.setText("Hiding image in video...")
                video=cv2.VideoCapture(cover)
                fps=video.get(cv2.CAP_PROP_FPS)
                width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                secret_img = Image.open(secret).convert("RGB")
                secret_img = secret_img.resize((50,50))
                secret_pixels = np.array(secret_img).flatten()
                width_bin = format(50, '016b')
                height_bin = format(50, '016b')
                secret_bin = width_bin + height_bin
                for pixel_val in secret_pixels:
                    secret_bin += format(pixel_val, '08b')
                output = cover.rsplit(".", 1)[0] + "_stego.avi"
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                out = cv2.VideoWriter(output, fourcc, fps, (width, height))
                frame_count =0
                while True:
                    ret, frame = video.read()
                    if not ret:
                        break
                    if frame_count == 0:
                        flat_frame = frame.flatten().copy()
                        bits_array = np.array([int(b) for b in secret_bin], dtype=np.uint8)
                        flat_frame[:len(bits_array)] = (flat_frame[:len(bits_array)] & 0xFE) | bits_array
                        frame = flat_frame.reshape(frame.shape)
                    out.write(frame)
                    frame_count += 1
                video.release()
                out.release()
                self.embed_status.setText("Done! saved as" + output)
                         
                             
        except Exception as e:
            print("Exception:", str(e))
            self.embed_status.setText("Status: Exception — " + str(e))
    def build_extraction_tab(self):
            
        tab = QWidget()
        layout = QVBoxLayout()

        self.stego_path = QLineEdit()
        self.stego_path.setPlaceholderText("Select stego file...")
        stego_btn = QPushButton("Browse stego File")
        stego_btn.clicked.connect(self.browse_stego)
        self.extract_passphrase = QLineEdit()
        self.extract_passphrase.setPlaceholderText("Enter passphrase...")
        self.extract_passphrase.setEchoMode(QLineEdit.Password)
        self.media_type_extract = QComboBox()
        self.media_type_extract.addItems(["Image","Audio","video"])
        extract_btn = QPushButton("Extract and Decrypt")
        extract_btn.clicked.connect(self.extract)
        self.extract_status = QLabel("Status: Ready")
        layout.addWidget(QLabel("Stego File:"))
        layout.addWidget(self.stego_path)
        layout.addWidget(stego_btn)
        layout.addWidget(QLabel("Media Type:"))
        layout.addWidget(self.media_type_extract)
        layout.addWidget(QLabel("passphrase"))
        layout.addWidget(self.extract_passphrase)
        layout.addWidget(extract_btn)
        layout.addWidget(self.extract_status)

        self.recovered_image_label = QLabel("")
        self.recovered_image_label.setMinimumHeight(200)
        self.recovered_image_label.setStyleSheet("border: 1px solid gray;")
        layout.addWidget(QLabel("recovered Image:"))
        layout.addWidget(self.recovered_image_label)
        tab.setLayout(layout)
        return tab
    def browse_stego(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Stego File", "",
            "ALL Files (*.png *.jpg *.bmp *.wav *.avi)"
            )
        if file:
            self.stego_path.setText(file)
    def extract(self):
        try:
            stego = self.stego_path.text()
            passphrase = self.extract_passphrase.text()
            media = self.media_type_extract.currentText()
            if media == "Image":
                self.extract_status.setText(" Extracting hidden data..")
                openstego_jar = r"C:\Users\SNIGDHA\OneDrive\Desktop\stegnoproject1\openstego-0.8.6\openstego-0.8.6\lib\openstego.jar"
                stego = stego.replace("/","\\")
                extract_dir = "\\".join(stego.split("\\")[:-1])
                stego_cmd = [
                    "java", "-jar", openstego_jar,
                    "extract","-a", "RandomLSB",
                    "-sf", stego,
                    "-xd", extract_dir
                    ]
                stego_result = subprocess.run(stego_cmd, capture_output=True, text=True)
                if stego_result.returncode == 0:
                    self.extract_status.setText("Decrypting extracted file...")
                    extracted_file = extract_dir + "\\secret_jpg_bitenc.png"
                    decrypted_file = extract_dir + "\\recovered_secret.png"
                    key = sum(ord(c) for c in passphrase) % 256
                    self.bit_decrypt(extracted_file, key, decrypted_file)
                    self.extract_status.setText("Done ! Recovered image saved as recovered_secret.png")
                    pixmap = Qpixmap.scaled(300,200)
                    self.recovered_image_label.setPixmap(pixmap)
                    
            elif media == "Audio":
                    self.extract_status.setText("Extracting image from audio..")
                    stego = stego.replace("/","\\")
                    audio= wave.open(stego, "rb")
                    frames = audio.readframes(audio.getnframes())
                    sample = np.frombuffer(frames, dtype=np.int16).copy()
                    audio.close()
                    extracted_bits =""
                    for i in range(60032):
                        extracted_bits += format(int(sample[i]) & 0xFFFF, '016b')[-1]

                    width = int(extracted_bits[:16],2)
                    height = int(extracted_bits[16:32],2)
                    pixel_bits = extracted_bits[32:]
                    pixels = []
                    
                    for i in range(0, len(pixel_bits), 8):
                        pixels.append(int(pixel_bits[i:i+8], 2))
                    secret_array = np.array(pixels, dtype=np.uint8).reshape((height, width, 3))
                    recovered = Image.fromarray(secret_array)
                    output = stego.rsplit(".", 1)[0] + "_recovered.png"
                    recovered.save(output)
                    self.extract_status.setText("Done! Recoverd image saved as" + output)
                    
            elif media == "Video":
                    self.extract_status.setText("Extracting image from video..")
                    video = cv2.VideoCapture(stego)
                    ret, frame = video.read()
                    video.release()
                    if not ret:
                        self.extract_status.setText("Error - Cannot read video!")
                        return
                    flat_frame = frame.flatten()
                    total_bits = 50 * 50 * 3 * 8
                    extracted_bits = ""
                    for i in range(total_bits):
                        extracted_bits += str(flat_frame[i] & 1)
                    pixels_bits = extracted_bits[32:]
                    pixels =[]
                    for i in range(0, len(pixels_bits), 8):
                        pixels.append(int(pixels_bits[i:i+8], 2))
                    secret_array = np.array(pixels, dtype=np.uint8).reshape((50, 50, 3))
                    recovered = Image.fromarray(secret_array)
                    output = stego.rsplit(".",1)[0] + "_recovered.png"
                    recovered.save(output)
                    self.extract_status.setText("Done! Recovered iamge saved as" + output)   
                        
                        
                                        
        except Exception as e:
            print("Exception:", str(e))
            self.extract_status.setText("Exception -" + str(e))
    def build_detection_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        self.detect_path = QLineEdit()
        self.detect_path.setPlaceholderText("Select image to analyze..")
        detect_btn = QPushButton("Browse Image")
        detect_btn.clicked.connect(self.browse_detect)
        analyze_btn = QPushButton("Analyze for Hidden Data")
        analyze_btn.clicked.connect(self.detect)
        self.detect_status = QLabel("Status:Ready")
        self.detect_result = QLabel("")

        layout.addWidget(QLabel("Image to Analyze:"))
        layout.addWidget(self.detect_path)
        layout.addWidget(detect_btn)
        layout.addWidget(analyze_btn)
        layout.addWidget(self.detect_status)
        layout.addWidget(self.detect_result)

        tab.setLayout(layout)
        return tab
    def browse_detect(self):
        file, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "",
            "Images(*.png *.jpg *.bmp *.wav *.avi *.mp4)"
            )
        if file:
            self.detect_path.setText(file)
    def detect(self):
        try:
            
            path = self.detect_path.text()
            if not path:
                QMessageBox.warning(self, "Error","Please select an image!")
                return
            self.detect_status.setText("Status: Analyzing..")
            if path.lower().endswith(".wav"):
                audio = wave.open(path, "rb")
                frames = audio.readframes(audio.getnframes())
                sample = np.frombuffer(frames, dtype=np.int16).copy()
                audio.close()
                even = np.sum(sample % 2 == 0)
                odd = np.sum(sample % 2 == 1)
           
            else:
                img = Image.open(path).convert("RGB")
                pixels = np.array(img).flatten()
                even = np.sum(pixels % 2 == 0)
                odd = np.sum(pixels % 2 == 1)
            ratio = round(even / odd, 4)
            if 0.95 <= ratio <= 1.05:
                result = "Hidden data DETECTED"
            else:
                result = "No hidden data found"
            self.detect_status.setText(" Analysis Complete")
            self.detect_result.setText(
                "Even: " + str(even) + "\n" +
                "Odd: " + str(odd) + "\n" +
                "Ratio:" + str(ratio) + "\n\n"+
                
                "RESULT: " + result
                )
            
        except Exception as e:
            print("Exception:", str(e))
            self.detect_status.setText("Status: Exception -" + str(e))
                
    
               
            
app = QApplication(sys.argv)
window = SteganographyTool()
window.show()
sys.exit(app.exec_())


