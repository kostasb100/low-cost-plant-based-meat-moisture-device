from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QPushButton, QLabel, QFileDialog,
    QRadioButton, QSlider, QComboBox, QLineEdit, QCheckBox, QAction,
    QMessageBox)
from picamera2 import Picamera2, Preview, controls
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import json, sys, os, time
import cv2 as cv
import numpy as np
import RPi.GPIO as GPIO
from hx711 import HX711

DEFAULTS = {
    # Camera Settings
    "shutter_speed": "",
    "lens_position": "",
    "colour_gain_red": "",
    "colour_gain_blue": "",
    "analog_gain": "",
    "preheat": "",
    # Illuminated Capture Settings
    "image_capture": "",
    "illum_raw": False,
    "pause_between_capture": "",
    "illuminated_image_name": "",
    "lamp_drive": "External source",
    # Noise Settings
    "toggle_capture_noise": False,
    "noise_raw": False,
    "noise_image_capture": "",
    "noise_image_name": "",
    "pause_between_noise_capture": "",
    # LED Settings
    "led1_combobox": "None",
    "led2_combobox": "None",
    "led_capture_checkbox": False,
    "led_raw": False,
    "led_image_count": "None",
    "pause_between_led_capture": "None",
    "led_image_name": "",
    "led_image_output_path": "",
    # Advanced Settings
    "metadata": False,
    "toggle_experiment_mode": False,
    "single_shutter": False,
    "multiple_shutter": False,
    "shutter_speed_from": "",
    "shutter_speed_to": "",
    "shutter_speed_by": "",
    "number_experiments": "",
    "time_between_experiments": "",
    # Scale Settings
    "scale_check": False,
    "dat": "None",
    "clk": "None",
    "ref_unit": "",
    "scale_num": "",
}

class SingleCaptureThread(QThread):
    update_progress = pyqtSignal(int)

    def __init__(self, save_dir, main_title, image_count, pause_time,
                 picam2=None, save_metadata=False,save_raw=False, requested_controls=None):

        super().__init__()
        self.save_dir = save_dir
        self.main_title = main_title
        self.image_count = image_count
        self.pause_time = pause_time
        self.picam2 = picam2
        self.save_metadata = save_metadata
        self.save_raw = save_raw
        self.running = True
        self.requested_controls = requested_controls or {}

    def run(self):
        for i in range(self.image_count):
            if not self.running:
                break

            filename = f"{self.main_title}{i}.jpg"
            filepath = os.path.join(self.save_dir, filename)

            if self.picam2:
                request = self.picam2.capture_request()

                # Save JPEG
                request.save("main", filepath)

                # Save RAW as .dng
                if self.save_raw:
                    raw_path = os.path.splitext(filepath)[0] + ".dng"
                    request.save_dng(raw_path)

                # Metadata (optional)
                metadata = request.get_metadata()

                request.release()

                # Image Metadata Storage
                if self.save_metadata:
                    metadata = self.picam2.capture_metadata()

                    # JSON file name matches image name
                    json_path = os.path.join(
                        self.save_dir,
                        f"{self.main_title}{i}.json"
                    )

                    # Ensure everything is JSON-serializable
                    def convert(obj):
                        if isinstance(obj, (tuple, list)):
                            return list(obj)
                        if hasattr(obj, "tolist"):
                            return obj.tolist()
                        return obj

                    clean_metadata = {k: convert(v) for k, v in metadata.items()}
                    clean_requested = {k: convert(v) for k, v in self.requested_controls.items()}

                    json_path = os.path.splitext(filepath)[0] + ".json"

                    with open(json_path, "w") as f:
                        json.dump(
                            {
                                "requested": clean_requested,
                                "metadata": clean_metadata
                            },
                            f,
                            indent=4
                        )

            print(f"{filename}: {filepath}")

            self.update_progress.emit(self.image_count - (i + 1))
            time.sleep(self.pause_time)

class CaptureThread(QThread):
    update_noise = pyqtSignal(int)  # Remaining Noise Images
    update_image = pyqtSignal(int)  # Remaining Illuminated Images

    def __init__(self, save_dir_image, save_dir_noise, main_title_image,
                 main_title_noise, image_capture, noise_image_capture,
                 pause_between_capture, pause_between_noise_capture,
                 picam2=None):
        super().__init__()
        self.save_dir_image = save_dir_image
        self.save_dir_noise = save_dir_noise
        self.main_title_image = main_title_image
        self.main_title_noise = main_title_noise
        self.image_capture = image_capture
        self.noise_image_capture = noise_image_capture
        self.pause_between_capture = pause_between_capture
        self.pause_between_noise_capture = pause_between_noise_capture
        self.picam2 = picam2
        self.running = True

    def run(self):
        # Capture Noise Images
        for i in range(self.noise_image_capture):
            if not self.running:
                break
            if i == 0:
                self.update_noise.emit(self.noise_image_capture)

            self.update_image.emit(self.image_capture)
            filename = f"{self.main_title_noise}{i}.jpg"
            filepath = os.path.join(self.save_dir_noise, filename)

            if self.picam2:
                request = self.picam2.capture_request()
                # Save JPEG
                request.save("main", filepath)
                # Save RAW as .dng
                if save_noise_raw_checkbox.isChecked():
                    raw_path = os.path.splitext(filepath)[0] + ".dng"
                    request.save_dng(raw_path)
                # Metadata
                metadata = request.get_metadata()
                request.release()
            else:
                print(f"{filename}: {filepath}")

            self.update_noise.emit(self.noise_image_capture - (i + 1))
            time.sleep(self.pause_between_noise_capture)

        # Capture Illuminated Images
        for i in range(self.image_capture):
            if not self.running:
                break

            if i == 0:
                self.update_image.emit(self.image_capture)

            self.update_noise.emit(0)
            filename = f"{self.main_title_image}{i}.jpg"
            filepath = os.path.join(self.save_dir_image, filename)

            if self.picam2:
                request = self.picam2.capture_request()
                # Save JPEG
                request.save("main", filepath)
                # Save RAW as .dng
                if save_illum_raw_checkbox.isChecked():
                    raw_path = os.path.splitext(filepath)[0] + ".dng"
                    request.save_dng(raw_path)
                # Metadata
                metadata = request.get_metadata()
                request.release()
            else:
                print(f"{filename}: {filepath}")

            self.update_image.emit(self.image_capture - (i + 1))
            time.sleep(self.pause_between_capture)

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("capture_2.ui", self)
        self.show()

        self.capture_both_button = self.findChild(QPushButton, "pushButton")
        self.choose_image_output_path_button = self.findChild(QPushButton, "pushButton_3")
        self.choose_noise_output_path_button = self.findChild(QPushButton, "pushButton_2")
        self.button_capture_noise = self.findChild(QPushButton, "pushButton_4")
        self.button_capture_image = self.findChild(QPushButton, "pushButton_5")
        self.choose_experiment_output_path_button = self.findChild(QPushButton, "pushButton_6")

        self.shutter_speed = self.findChild(QLineEdit, "lineEdit")
        self.lens_position = self.findChild(QLineEdit, "lineEdit_2")
        self.colour_gains_red = self.findChild(QLineEdit, "lineEdit_3")
        self.analog_gain = self.findChild(QLineEdit, "lineEdit_5")
        self.colour_gains_blue = self.findChild(QLineEdit, "lineEdit_6")

        self.illuminated_image_output_path = self.findChild(QLineEdit, "lineEdit_7")
        self.illuminated_image_count = self.findChild(QLineEdit, "lineEdit_8")
        self.pause_between_illuminated_capture = self.findChild(QLineEdit, "lineEdit_9")
        self.save_illum_raw_checkbox = self.findChild(QCheckBox, "checkBox_4")
        self.illuminated_image_name = self.findChild(QLineEdit, "lineEdit_14")
        self.lamp_drive_combobox = self.findChild(QComboBox, "comboBox")

        self.noise_image_count = self.findChild(QLineEdit, "lineEdit_10")
        self.pause_between_noise_capture = self.findChild(QLineEdit, "lineEdit_11")
        self.save_noise_raw_checkbox = self.findChild(QCheckBox, "checkBox_6")
        self.noise_image_output_path = self.findChild(QLineEdit, "lineEdit_12")
        self.noise_image_name = self.findChild(QLineEdit, "lineEdit_13")

        self.led1_combobox = self.findChild(QComboBox, "comboBox_3")
        self.led2_combobox = self.findChild(QComboBox, "comboBox_6")
        self.led_capture_checkbox = self.findChild(QCheckBox, "checkBox_5")
        self.led_image_count = self.findChild(QLineEdit, "lineEdit_27")
        self.pause_between_led_capture = self.findChild(QLineEdit, "lineEdit_26")
        self.save_led_raw_checkbox = self.findChild(QCheckBox, "checkBox_7")
        self.led_image_name = self.findChild(QLineEdit, "lineEdit_24")
        self.led_image_output_path = self.findChild(QLineEdit, "lineEdit_25")
        self.choose_led_image_path_button = self.findChild(QPushButton, "pushButton_7")

        self.single_shutter_speed_radiobutton = self.findChild(QRadioButton, "radioButton")
        self.mult_shutter_speeds_radiobutton = self.findChild(QRadioButton, "radioButton_2")
        self.shutter_time_from = self.findChild(QLineEdit, "lineEdit_15")
        self.shutter_time_to = self.findChild(QLineEdit, "lineEdit_16")
        self.shutter_time_by = self.findChild(QLineEdit, "lineEdit_17")
        self.pre_heat_time = self.findChild(QLineEdit, "lineEdit_18")
        self.experiment_output_path = self.findChild(QLineEdit, "lineEdit_19")
        self.time_between_experiments = self.findChild(QLineEdit, "lineEdit_20")

        self.noise_left_label = self.findChild(QLabel, "label_21")
        self.image_left_label = self.findChild(QLabel, "label_22")
        self.current_status = self.findChild(QLabel, "label_32")
        self.number_of_experiments = self.findChild(QLineEdit, "lineEdit_21")

        self.scale_measurement_checkbox = self.findChild(QCheckBox, "checkBox_3")
        self.dat_combobox = self.findChild(QComboBox, "comboBox_2")
        self.clk_combobox = self.findChild(QComboBox, "comboBox_4")
        self.ref_unit_lineedit = self.findChild(QLineEdit, "lineEdit_22")
        self.scale_measurement_number_lineedit = self.findChild(QLineEdit, "lineEdit_23")
        self.experiments_done_label = self.findChild(QLabel, "label_33")

        self.actionNew = self.findChild(QAction, "actionNew")
        self.actionLoad = self.findChild(QAction, "actionLoad")
        self.actionSave = self.findChild(QAction, "actionSave")
        self.actionSave_as = self.findChild(QAction, "actionSave_As")

        self.actionNew.triggered.connect(self.new_settings)
        self.actionLoad.triggered.connect(self.load_settings)
        self.actionSave.triggered.connect(self.save_settings)
        self.actionSave_as.triggered.connect(self.save_settings_as)

        self.choose_image_output_path_button.clicked.connect(self.choose_directory_image)
        self.choose_noise_output_path_button.clicked.connect(self.choose_directory_noise)
        self.choose_experiment_output_path_button.clicked.connect(self.choose_directory_experiment)
        self.choose_led_image_path_button.clicked.connect(self.choose_directory_led_image)

        self.button_capture_noise.clicked.connect(self.start_noise_capture)
        self.button_capture_image.clicked.connect(self.start_image_capture)
        self.capture_both_button.clicked.connect(self.start_both_capture)

        self.get_metada_checkbox = self.findChild(QCheckBox, "checkBox_2")
        self.experiment_mode_checkbox = self.findChild(QCheckBox, "checkBox")

        self.camera_available = True
        self.picam2 = Picamera2()

        self.experiment_status = {
            "scale": "Scaling the sample...",
            "init_camera": "Initializing camera...",
            "led_capture": "Capturing LED image",
            "noise_capture": "Capturing noise...",
            "preheat_lamp": "Preheating Lamp...",
            "image_capture": "Capturing Illuminated Images...",
            "idle": "Idle...",
            "complete": "Experiment completed",
        }

    def set_experiment_status(self, status_key):
        if status_key in self.experiment_status:
            self.current_status.setText(self.experiment_status[status_key])
        QApplication.processEvents()

    def set_led_high(self, pin):
        if pin is not None:
            GPIO.output(pin, GPIO.HIGH)

    def set_led_low(self, pin):
        if pin is not None:
            GPIO.output(pin, GPIO.LOW)

    def start_noise_capture(self):
        # Noise Image Directory Check
        if not self.noise_image_output_path.text().strip():
            QMessageBox.warning(self, "Error", "Please choose noise image directory.")
            return
        save_dir_noise = self.noise_image_output_path.text().strip()

        # Noise Image Prefix Name Check
        if not self.noise_image_name.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a file name prefix for noise images.")
            return
        main_title_noise = self.noise_image_name.text().strip()

        # Noise Image Number Check
        if not self.noise_image_count.text():
            QMessageBox.warning(self, "Error", "Please choose the number of noise images to capture.")
            return
        try:
            noise_image_count = int(self.noise_image_count.text())
            if noise_image_count <= 0:
                QMessageBox.warning(self, "Error", "Number of noise images must be greater than 0.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number format for noise images.")
            return

        # Noise Image Pause Check
        if not self.pause_between_noise_capture.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the noise image capture pause (>0.7 [s]).")
            return
        try:
            pause_noise = float(self.pause_between_noise_capture.text())
            if pause_noise <= 0.7:
                QMessageBox.warning(self, "Error", "Pause time for noise images must be greater than 0.7 seconds.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number format for noise image pause time.")
            return

        # Shutter Speed Check
        if not self.shutter_speed.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the shutter speed.")
            return
        try:
            shutter_speed = int(self.shutter_speed.text())
            if not (30 <= shutter_speed <= 112_000_000):
                QMessageBox.warning(self, "Error",
                                    "Shutter speed must be between 30 µs and 112,000,000 µs (112 seconds).")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Shutter speed must be an integer.")
            return

        # Lens Position Check
        if not self.lens_position.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the lens position.")
            return
        try:
            lens_position = float(self.lens_position.text())
            if not (0 <= lens_position <= 10):
                QMessageBox.warning(self, "Error", "Lens position must be between 0 and 10.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Lens position must be a number.")
            return

        # Red Color Gain Check
        if not self.colour_gains_red.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the red colour gain.")
            return
        try:
            colour_gain_red = float(self.colour_gains_red.text())
            if not (1 <= colour_gain_red <= 8):
                QMessageBox.warning(self, "Error", "Red colour gain must be between 1 and 8.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Red colour gain must be a number.")
            return

        # Blue Color Gain Check
        if not self.colour_gains_blue.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the blue colour gain.")
            return
        try:
            colour_gain_blue = float(self.colour_gains_blue.text())
            if not (1 <= colour_gain_blue <= 8):
                QMessageBox.warning(self, "Error", "Blue colour gain must be between 1 and 8 (inclusive).")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Blue colour gain must be a number.")
            return

        # Analogue Gain Check
        if not self.analog_gain.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the analogue gain.")
            return
        try:
            analog_gain = float(self.analog_gain.text())
            if not (1 <= analog_gain <= 8):
                QMessageBox.warning(self, "Error", "Analogue gain must be between 1 and 8 (inclusive).")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Analogue gain must be a number.")
            return

        if self.camera_available:
            sensor_width, sensor_height = self.picam2.sensor_resolution

            config = self.picam2.create_still_configuration(
                main={"size": (sensor_width, sensor_height)},
                # ~ raw={"size": (sensor_width, sensor_height)},
                buffer_count=2,
                controls={
                    "AeEnable": False,
                    "AwbEnable": False,
                    "Brightness": 0.0,
                    "Contrast": 1.0,
                    "Saturation": 1.0,
                    "Sharpness": 1.0,
                    "NoiseReductionMode": 0,
                    "ExposureTime": shutter_speed,
                    "AnalogueGain": analog_gain,
                    "ColourGains": (colour_gain_red, colour_gain_blue),
                    "LensPosition": lens_position
                }
            )

        time.sleep(2.0)

        self.noise_thread = SingleCaptureThread(
            save_dir_noise, main_title_noise, noise_image_count, pause_noise,
            picam2=self.picam2 if self.camera_available else None,
            save_metadata=self.get_metada_checkbox.isChecked()
        )
        self.noise_thread.update_progress.connect(lambda x: self.noise_left_label.setText(str(x)))
        self.noise_thread.start()

    def start_image_capture(self):
        # Illuminated Image Directory Check
        if not self.illuminated_image_output_path.text().strip():
            QMessageBox.warning(self, "Error", "Please choose illuminated image directory.")
            return
        save_dir_image = self.illuminated_image_output_path.text().strip()

        # Illuminated Image Prefix Name Check
        if not self.illuminated_image_name.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a file name prefix for illuminated images.")
            return
        main_title_image = self.illuminated_image_name.text().strip()

        # Illuminated Image Number Check
        if not self.illuminated_image_count.text():
            QMessageBox.warning(self, "Error", "Please choose the number of illuminated images to capture.")
            return
        try:
            image_count = int(self.illuminated_image_count.text())
            if image_count <= 0:
                QMessageBox.warning(self, "Error", "Number of illuminated images must be greater than 0.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number format for illuminated images.")
            return

        # Illuminated Image Pause Check
        if not self.pause_between_illuminated_capture.text().strip():  # check if empty
            QMessageBox.warning(self, "Error", "Please enter the illuminated image capture pause (>0.7 [s]).")
            return
        try:
            pause_capture = float(self.pause_between_illuminated_capture.text())
            if pause_capture <= 0.7:  # optional constraint
                QMessageBox.warning(self, "Error",
                                    "Pause time for illuminated images must be greater than 0.7 seconds.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number format for illuminated image pause time.")
            return

        # Shutter Speed Check
        if not self.shutter_speed.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the shutter speed.")
            return
        try:
            shutter_speed = int(self.shutter_speed.text())
            if not (30 <= shutter_speed <= 112_000_000):
                QMessageBox.warning(self, "Error",
                                    "Shutter speed must be between 30 µs and 112,000,000 µs (112 seconds).")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Shutter speed must be an integer.")
            return

        # Lens Position Check
        if not self.lens_position.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the lens position.")
            return
        try:
            lens_position = float(self.lens_position.text())
            if not (0 <= lens_position <= 10):
                QMessageBox.warning(self, "Error", "Lens position must be between 0 and 10.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Lens position must be a number.")
            return

        # Red Color Gain Check
        if not self.colour_gains_red.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the red colour gain.")
            return
        try:
            colour_gain_red = float(self.colour_gains_red.text())
            if not (1 <= colour_gain_red <= 8):
                QMessageBox.warning(self, "Error", "Red colour gain must be between 1 and 8.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Red colour gain must be a number.")
            return

        # Blue Color Gain Check
        if not self.colour_gains_blue.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the blue colour gain.")
            return
        try:
            colour_gain_blue = float(self.colour_gains_blue.text())
            if not (1 <= colour_gain_blue <= 8):
                QMessageBox.warning(self, "Error", "Blue colour gain must be between 1 and 8 (inclusive).")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Blue colour gain must be a number.")
            return

        # Analogue Gain Check
        if not self.analog_gain.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the analogue gain.")
            return
        try:
            analog_gain = float(self.analog_gain.text())
            if not (1 <= analog_gain <= 8):
                QMessageBox.warning(self, "Error", "Analogue gain must be between 1 and 8 (inclusive).")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Analogue gain must be a number.")
            return

        if self.camera_available:
            sensor_width, sensor_height = self.picam2.sensor_resolution

            config = self.picam2.create_still_configuration(
                main={"size": (sensor_width, sensor_height)},
                buffer_size=2,
                controls={
                    "AeEnable": False,
                    "AwbEnable": False,
                    "Brightness": 0.0,
                    "Contrast": 1.0,
                    "Saturation": 1.0,
                    "Sharpness": 1.0,
                    "NoiseReductionMode": 0,
                    "ExposureTime": shutter_speed,
                    "AnalogueGain": analog_gain,
                    "ColourGains": (colour_gain_red, colour_gain_blue),
                    "LensPosition": lens_position
                }
            )

        # camera initializing time
        time.sleep(2.0)

        self.image_thread = SingleCaptureThread(
            save_dir_image, main_title_image, image_count, pause_capture,
            picam2=self.picam2 if self.camera_available else None,
            save_metadata=self.get_metada_checkbox.isChecked(),
            requested_controls={
                "ExposureTime": shutter_temp,
                "AnalogueGain": analog_gain,
                "ColourGains": (colour_gain_red, colour_gain_blue),
                "LensPosition": lens_position
            }
        )
        self.image_thread.update_progress.connect(lambda x: self.image_left_label.setText(str(x)))
        self.image_thread.start()

    def start_both_capture(self):
        # Double Capture Directory Check
        if not self.experiment_output_path.text().strip():
            QMessageBox.warning(self, "Error", "Please choose experiment result directory.")
            return
        save_experiment_result = self.experiment_output_path.text().strip()

        # Noise Image Prefix Name Check
        if not self.noise_image_name.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a file name prefix for noise images.")
            return
        main_title_noise = self.noise_image_name.text().strip()

        # Noise Image Number Check
        if not self.noise_image_count.text():
            QMessageBox.warning(self, "Error", "Please choose the number of noise images to capture.")
            return
        try:
            noise_image_count = int(self.noise_image_count.text())
            if noise_image_count <= 0:
                QMessageBox.warning(self, "Error", "Number of noise images must be greater than 0.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number format for noise images.")
            return

        # Noise Image Pause Check
        if not self.pause_between_noise_capture.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the noise image capture pause (>0.7 [s]).")
            return
        try:
            pause_noise = float(self.pause_between_noise_capture.text())
            if pause_noise <= 0.7:
                QMessageBox.warning(self, "Error", "Pause time for noise images must be greater than 0.7 seconds.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number format for noise image pause time.")
            return

        # Illuminated Image Prefix Name Check
        if not self.illuminated_image_name.text().strip():
            QMessageBox.warning(self, "Error",
                                "Please enter a file name prefix for the illuminated images of the experiment.")
            return
        main_title_image = self.illuminated_image_name.text().strip()

        # Illuminated Image Number Check
        if not self.illuminated_image_count.text():
            QMessageBox.warning(self, "Error",
                                "Please choose the number of illuminated images to capture for every experiment.")
            return
        try:
            image_count = int(self.illuminated_image_count.text())
            if image_count <= 0:
                QMessageBox.warning(self, "Error", "Number of illuminated images must be greater than 0.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number format for illuminated images(experiment).")
            return

        # Illuminated Image Pause Check
        if not self.pause_between_illuminated_capture.text().strip():  # check if empty
            QMessageBox.warning(self, "Error",
                                "Please enter the illuminated image capture pause(experiment) (>0.7 [s]).")
            return
        try:
            pause_capture = float(self.pause_between_illuminated_capture.text())
            if pause_capture <= 0.7:  # optional constraint
                QMessageBox.warning(self, "Error",
                                    "Pause time for illuminated images must be greater than 0.7 seconds(experiment.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid number format for illuminated image pause time.")
            return

        # Lens Position Check
        if not self.lens_position.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the lens position=.")
            return
        try:
            lens_position = float(self.lens_position.text())
            if not (0 <= lens_position <= 10):
                QMessageBox.warning(self, "Error", "Lens position must be between 0 and 10.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Lens position must be a number.")
            return

        # Red Color Gain Check
        if not self.colour_gains_red.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the red colour gain.")
            return
        try:
            colour_gain_red = float(self.colour_gains_red.text())
            if not (1 <= colour_gain_red <= 8):
                QMessageBox.warning(self, "Error", "Red colour gain must be between 1 and 8.")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Red colour gain must be a number.")
            return

        # Blue Color Gain Check
        if not self.colour_gains_blue.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the blue colour gain.")
            return
        try:
            colour_gain_blue = float(self.colour_gains_blue.text())
            if not (1 <= colour_gain_blue <= 8):
                QMessageBox.warning(self, "Error", "Blue colour gain must be between 1 and 8 (inclusive).")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Blue colour gain must be a number.")
            return

        # Analogue Gain Check
        if not self.analog_gain.text().strip():
            QMessageBox.warning(self, "Error", "Please enter the analogue gain.")
            return
        try:
            analog_gain = float(self.analog_gain.text())
            if not (1 <= analog_gain <= 8):
                QMessageBox.warning(self, "Error", "Analogue gain must be between 1 and 8 (inclusive).")
                return
        except ValueError:
            QMessageBox.warning(self, "Error", "Analogue gain must be a number.")
            return

        if self.experiment_mode_checkbox.isChecked():
            # Time between experiments check
            if not self.time_between_experiments.text().strip():
                QMessageBox.warning(self, "Error", "Please enter the time between experiments [min].")
                return
            try:
                time_experiments = float(self.time_between_experiments.text())
                if not (0 <= time_experiments <= 120):
                    QMessageBox.warning(self, "Error", "Time between capture must be between 1 and 120 minutes")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Time between capture must be a valid number")
                return

            # Number of experiments check
            if not self.number_of_experiments.text().strip():
                QMessageBox.warning(self, "Error", "Please enter the number of experiments.")
                return
            try:
                num_experiments = int(self.number_of_experiments.text())
                if not (1 <= num_experiments <= 100):
                    QMessageBox.warning(self, "Error", "Number of experiments must be between 1 and 100")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Number of experiments must be must be a valid number")
                return

            # Shutter time FROM check
            if not self.shutter_time_from.text().strip():
                QMessageBox.warning(self, "Error", "Please enter the shutter time FROM [µs].")
                return
            try:
                shutter_from = int(self.shutter_time_from.text())
                if not (1 <= shutter_from <= 200000):
                    QMessageBox.warning(self, "Error", "Shutter time FROM must be between 1 and 200000 [µs].")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Shutter time FROM must be a valid number.")
                return

            # Shutter time TO check
            if not self.shutter_time_to.text().strip():
                QMessageBox.warning(self, "Error", "Please enter the shutter time TO [µs].")
                return
            try:
                shutter_to = int(self.shutter_time_to.text())
                if not (1 <= shutter_to <= 200000):
                    QMessageBox.warning(self, "Error", "Shutter time TO must be between 1 and 200000 [µs].")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Shutter time TO must be a valid number.")
                return

            # Shutter time BY check
            if not self.shutter_time_by.text().strip():
                QMessageBox.warning(self, "Error", "Please enter the shutter time BY [µs].")
                return
            try:
                shutter_by = int(self.shutter_time_by.text())
                if not (1 <= shutter_by <= 200000):
                    QMessageBox.warning(self, "Error", "Shutter time BY must be between 1 and 200000 [µs].")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Shutter time BY must be a valid number.")
                return

            # shutter time division check
            if shutter_from >= shutter_to:
                QMessageBox.warning(self, "Error", "Shutter time FROM must be less than TO.")
                return
            diff = shutter_to - shutter_from
            if diff % shutter_by != 0:
                QMessageBox.warning(
                    self, "Error",
                    f"The difference between FROM and TO ({diff} [µs]) must be divisible by BY ({shutter_by} [µs])."
                )
                return

            if not self.pre_heat_time.text().strip():
                QMessageBox.warning(self, "Error", "Please enter the lamp preheat time [s].")
                return
            try:
                preheat = int(self.pre_heat_time.text())
                if not (1 <= preheat <= 180):
                    QMessageBox.warning(self, "Error", "Preheat time must be between 1 and 180 [s].")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Preheat time must be a valid number.")
                return

            self.experiment_stages = []

            for i in range(num_experiments):
                self.experiment_stages.append(time_experiments * i)

            self.gpio_mapping = {
                "GPIO2 (Pin 3)": 2,
                "GPIO3 (Pin 5)": 3,
                "GPIO4 (Pin 7)": 4,
                "GPIO5 (Pin 29)": 5,
                "GPIO6 (Pin 31)": 6,
                "GPIO7 (Pin 26)": 7,
                "GPIO8 (Pin 24)": 8,
                "GPIO9 (Pin 21)": 9,
                "GPIO10 (Pin 19)": 10,
                "GPIO11 (Pin 23)": 11,
                "GPIO12 (Pin 32)": 12,
                "GPIO13 (Pin 33)": 13,
                "GPIO14 (Pin 8)": 14,
                "GPIO15 (Pin 10)": 15,
                "GPIO16 (Pin 36)": 16,
                "GPIO17 (Pin 11)": 17,
                "GPIO18 (Pin 12)": 18,
                "GPIO19 (Pin 35)": 19,
                "GPIO20 (Pin 38)": 20,
                "GPIO21 (Pin 40)": 21,
                "GPIO22 (Pin 15)": 22,
                "GPIO23 (Pin 16)": 23,
                "GPIO24 (Pin 18)": 24,
                "GPIO25 (Pin 22)": 25,
                "GPIO26 (Pin 37)": 26,
                "GPIO27 (Pin 13)": 27
            }

            try:
                selected_option = self.lamp_drive_combobox.currentText()
                if selected_option == "External source":
                    QMessageBox.warning(
                        self,
                        "Warning",
                        "GPIO pin must be chosen for experiment capture."
                    )
                    return

                self.lamp_pin = self.gpio_mapping[selected_option]

            except KeyError:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Invalid option selected: {selected_option}"
                )
                return

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.lamp_pin, GPIO.OUT, initial=GPIO.LOW)

            try:
                save_dir = self.folder_experiment
            except AttributeError:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please select a directory first."
                )
            # LED Settings Input Check
            if self.led_capture_checkbox.isChecked():
                try:
                    led1_selection = self.led1_combobox.currentText()
                    if led1_selection == "None":
                        QMessageBox.warning(
                            self,
                            "Warning",
                            "LED1 pin must be chosen for LED capture."
                        )
                        return
                    self.led1_pin = self.gpio_mapping[led1_selection]

                except KeyError:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Invalid option selected: {led1_selection}"
                    )
                    return

                GPIO.setup(self.led1_pin, GPIO.OUT, initial=GPIO.LOW)

                try:
                    led2_selection = self.led2_combobox.currentText()
                    if led2_selection == "None":
                        QMessageBox.warning(
                            self,
                            "Warning",
                            "LED2 pin must be chosen for LED capture."
                        )
                        return
                    self.led2_pin = self.gpio_mapping[led2_selection]

                except KeyError:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Invalid option selected: {led2_selection}"
                    )
                    return
                GPIO.setup(self.led2_pin, GPIO.OUT, initial=GPIO.LOW)

                if not self.led_image_count.text().strip():
                    QMessageBox.warning(self, "Error", "Please enter the number of LED images to capture.")
                    return
                try:
                    led_num = int(self.led_image_count.text())
                    if not (1 <= led_num <= 10):
                        QMessageBox.warning(self, "Error", "LED image count must be between 1 and 10.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Error", "LED image count must be a valid number.")
                    return

                if not self.pause_between_led_capture.text().strip():
                    QMessageBox.warning(self, "Error", "Please enter the time for pause between LED image capture.")
                    return
                try:
                    led_pause = int(self.pause_between_led_capture.text())
                    if not (1 <= led_pause <= 10):
                        QMessageBox.warning(self, "Error",
                                            "Pause between LED image capture must be between 1 and 10 seconds.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Error", "Pause between LED capture must be a valid number.")
                    return

                if not self.illuminated_image_name.text().strip():
                    QMessageBox.warning(self, "Error", "Please enter a file name prefix for the LED images.")
                    return

                main_title_led_image = self.led_image_name.text().strip()

            # Scale Settings Input Check
            if self.scale_measurement_checkbox.isChecked():
                try:
                    dat_selection = self.dat_combobox.currentText()
                    if dat_selection == "None":
                        QMessageBox.warning(
                            self,
                            "Warning",
                            "DAT pin must be chosen for scaling measurements."
                        )
                        return

                    self.dat_pin = self.gpio_mapping[dat_selection]

                except KeyError:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Invalid option selected: {dat_selection}"
                    )
                    return

                try:
                    clk_selection = self.clk_combobox.currentText()
                    if clk_selection == "None":
                        QMessageBox.warning(
                            self,
                            "Warning",
                            "CLK pin must be chosen for scaling measurements."
                        )
                        return

                    self.clk_pin = self.gpio_mapping[clk_selection]

                except KeyError:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Invalid option selected: {clk_selection}"
                    )
                    return

                if not self.ref_unit_lineedit.text().strip():
                    QMessageBox.warning(self, "Error", "Please enter the reference unit for the scaling measurements.")
                    return
                try:
                    ref_unit = float(self.ref_unit_lineedit.text())
                except ValueError:
                    QMessageBox.warning(self, "Error", "Reference unit must be a valid number.")
                    return

                if not self.scale_measurement_number_lineedit.text().strip():
                    QMessageBox.warning(self, "Error", "Please enter the number of scaling measurements to be done.")
                    return
                try:
                    scale_num = int(self.scale_measurement_number_lineedit.text())
                    if not (1 <= scale_num <= 50):
                        QMessageBox.warning(self, "Error", "Scale measurement number must be between 1 and 50.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Error", "Scale measurement number must be a valid number.")
                    return

            total_stages = len(self.experiment_stages)
            done_stages = 0
            self.experiments_done_label.setText(f"{done_stages} / {total_stages}")
            QApplication.processEvents()
            
            if self.single_shutter_speed_radiobutton.isChecked():
                shutter_temp = int(self.shutter_speed.text())
                shutter_list = [shutter_temp]
            else:
                shutter_list = list(range(shutter_from, shutter_to + shutter_by, shutter_by))

            if self.camera_available:
                sensor_width, sensor_height = self.picam2.sensor_resolution
                self.picam2.configure(
                    self.picam2.create_still_configuration(
                        main={"size": (sensor_width, sensor_height)},
                        raw={"size": (sensor_width, sensor_height)},
                        buffer_count=2,
                        controls={
                            "AeEnable": False,
                            "AwbEnable": False,
                            "Brightness": 0.0,
                            "Contrast": 1.0,
                            "Saturation": 1.0,
                            "Sharpness": 1.0,
                            "NoiseReductionMode": 0,
                            "ExposureTime": shutter_temp,
                            "AnalogueGain": analog_gain,
                            "ColourGains": (colour_gain_red, colour_gain_blue),
                            "LensPosition": lens_position
                        }
                    )
                )
                
            self.picam2.set_controls({"ScalerCrop": (0, 0, sensor_width, sensor_height)})
            self.picam2.start()

            for stage in self.experiment_stages:
                stage_start_time = time.time()
                stage_folder = os.path.join(save_dir, str(stage))
                os.makedirs(stage_folder, exist_ok=True)

                if self.scale_measurement_checkbox.isChecked():
                    
                    self.set_experiment_status("scale")
                    
                    hx = HX711(self.dat_pin, self.clk_pin)
                    hx.set_reading_format("MSB", "MSB")
                    hx.set_reference_unit(ref_unit)
                
                    time.sleep(1.0)

                    # Wake up HX711
                    hx.power_up()
                    time.sleep(0.5)

                    # Discard unstable first reading
                    hx.get_weight(1)

                    # Robust weight read
                    samples = []

                    for _ in range(scale_num):
                        reading = hx.get_weight(1)
                        samples.append(reading)
                        time.sleep(0.2)
                    
                    sorted_samples= sorted(samples)
                    
                    clean_samples = sorted_samples[3:-3]
                    
                    weight = sum(clean_samples) / len(clean_samples)
                    
                    # Power down to reduce noise
                    hx.power_down()

                    # Save to JSON
                    json_path = os.path.join(stage_folder, f"{stage}.json")
                    with open(json_path, "w") as f:
                        json.dump(
                            {
                                "Weight(g)": round(abs(weight), 2),
                                "Scale": {
                                    "num_samples":scale_num,
                                    "trim":3,
                                    "delay_s": 0.2,
                                    "raw_samples": samples,
                                    "clean_samples": clean_samples
                                }
                        },
                        f,
                        indent=4
                        )

                self.set_experiment_status("init_camera")

                for shutter_temp in shutter_list:
                    shutter_folder = os.path.join(save_dir, str(stage), str(shutter_temp))

                    os.makedirs(shutter_folder, exist_ok=True)

                    self.picam2.set_controls({
                    "ExposureTime": shutter_temp,
                    "AnalogueGain": analog_gain,
                    "ColourGains": (colour_gain_red,colour_gain_blue),
                    "LensPosition": lens_position
                    })

                    # Ensure that LEDs are turned off before noise capture
                    self.set_led_low(self.led1_pin)
                    self.set_led_low(self.led2_pin)
                    
                    time.sleep(1.0)

                    self.set_experiment_status("noise_capture")

                    self.image_thread = SingleCaptureThread(
                        shutter_folder, main_title_noise, noise_image_count, pause_noise,
                        picam2=self.picam2 if self.camera_available else None,
                        save_metadata=self.get_metada_checkbox.isChecked(),
                        save_raw=self.save_noise_raw_checkbox.isChecked(),
                        requested_controls={
                            "ExposureTime": shutter_temp,
                            "AnalogueGain": analog_gain,
                            "ColourGains": (colour_gain_red, colour_gain_blue),
                            "LensPosition": lens_position
                        }
                    )
                    self.image_thread.start()
                    self.image_thread.wait()
                    
                    # ~ self.picam2.stop()

                    if self.led_capture_checkbox.isChecked():
                        self.set_experiment_status("led_capture")

                        time.sleep(1.0)

                        self.image_thread = SingleCaptureThread(
                            shutter_folder, main_title_led_image, led_num, led_pause,
                            picam2=self.picam2 if self.camera_available else None,
                            save_metadata=self.get_metada_checkbox.isChecked(),
                            save_raw=self.save_led_raw_checkbox.isChecked(),
                        )

                        self.image_thread.start()
                        self.image_thread.wait()

                        self.set_led_low(self.led1_pin)
                        self.set_led_low(self.led2_pin)

                self.set_experiment_status("preheat_lamp")
                self.set_led_high(self.lamp_pin)
                time.sleep(preheat)

                self.set_experiment_status("image_capture")
                
                if self.single_shutter_speed_radiobutton.isChecked():
                    shutter_temp = int(self.shutter_speed.text())
                    shutter_list = [shutter_temp]
                else:
                    shutter_list = list(range(shutter_from, shutter_to + shutter_by, shutter_by))
                
                for shutter_temp in shutter_list:
                    shutter_folder = os.path.join(save_dir, str(stage), str(shutter_temp))

                    self.picam2.set_controls({
                    "ExposureTime": shutter_temp,
                    "AnalogueGain": analog_gain,
                    "ColourGains": (colour_gain_red,colour_gain_blue),
                    "LensPosition": lens_position
                    })

                    time.sleep(2.0)

                    self.image_thread = SingleCaptureThread(
                        shutter_folder, main_title_image, image_count, pause_capture,
                        picam2=self.picam2 if self.camera_available else None,
                        save_metadata=self.get_metada_checkbox.isChecked(),
                        save_raw=self.save_illum_raw_checkbox.isChecked(),
                        requested_controls={
                            "ExposureTime": shutter_temp,
                            "AnalogueGain": analog_gain,
                            "ColourGains": (colour_gain_red, colour_gain_blue),
                            "LensPosition": lens_position
                        }
                    )
                    self.image_thread.start()
                    self.image_thread.wait()

                self.set_led_low(self.lamp_pin)

                self.set_experiment_status("idle")

                done_stages += 1
                self.experiments_done_label.setText(f"{done_stages} / {total_stages}")
                QApplication.processEvents()

                if stage != self.experiment_stages[-1]:
                    print(f"Stage {stage} done. Pausing for {time_experiments} minutes...")
                    time.sleep(time_experiments * 60 - preheat)

            self.set_experiment_status("complete")
            self.picam2.stop()
            GPIO.cleanup()

    def choose_directory_image(self):
        folder_image = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "",
        )
        if folder_image:
            self.illuminated_image_output_path.setText(folder_image)

    def choose_directory_noise(self):
        folder_noise = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "",
        )
        if folder_noise:
            self.noise_image_output_path.setText(folder_noise)

    def choose_directory_experiment(self):
        folder_experiment = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "",
        )
        if folder_experiment:
            self.folder_experiment = folder_experiment
            self.experiment_output_path.setText(folder_experiment)

    def choose_directory_led_image(self):
        folder_led_image = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            "",
        )
        if folder_led_image:
            self.folder_led_image = folder_led_image
            self.led_image_output_path.setText(folder_led_image)

    def new_settings(self):
        # General Camera Settings
        self.shutter_speed.setText(str(DEFAULTS.get("shutter_speed", "")))
        self.lens_position.setText(str(DEFAULTS.get("lens_position", "")))
        self.colour_gains_red.setText(str(DEFAULTS.get("colour_gain_red", "")))
        self.colour_gains_blue.setText(str(DEFAULTS.get("colour_gain_blue", "")))
        self.analog_gain.setText(str(DEFAULTS.get("analog_gain", "")))
        self.pre_heat_time.setText(str(DEFAULTS.get("preheat", "")))
        # Illuminated Capture Settings
        self.illuminated_image_count.setText(str(DEFAULTS.get("image_capture", "")))
        self.pause_between_illuminated_capture.setText(str(DEFAULTS.get("pause_between_capture", "")))
        self.save_illum_raw_checkbox.setChecked(DEFAULTS.get("illum_raw", False))
        self.illuminated_image_name.setText(str(DEFAULTS.get("illuminated_image_name", "")))
        self.lamp_drive_combobox.setCurrentText(DEFAULTS.get("lamp_drive", "External source"))
        # Noise Settings
        self.noise_image_count.setText(str(DEFAULTS.get("noise_image_capture", "")))
        self.pause_between_noise_capture.setText(str(DEFAULTS.get("pause_between_noise_capture", "")))
        self.save_noise_raw_checkbox.setChecked(DEFAULTS.get("noise_raw", False))
        self.noise_image_name.setText(str(DEFAULTS.get("noise_image_name", "")))
        # LED Settings
        self.led1_combobox.setCurrentText(DEFAULTS.get("led1_combobox", "None"))
        self.led2_combobox.setCurrentText(DEFAULTS.get("led2_combobox", "None"))
        self.led_capture_checkbox.setChecked(DEFAULTS.get("led_capture_checkbox", False))
        self.led_image_count.setText(str(DEFAULTS.get("led_image_count", "")))
        self.pause_between_led_capture.setText(str(DEFAULTS.get("pause_between_led_capture", "")))
        self.save_led_raw_checkbox.setChecked(DEFAULTS.get("led_raw", False))
        self.led_image_name.setText(str(DEFAULTS.get("led_image_name", "")))
        self.led_image_output_path.setText(str(DEFAULTS.get("led_image_output_path", "")))
        # Advanced Settings
        self.get_metada_checkbox.setChecked(DEFAULTS.get("metadata", False))
        self.experiment_mode_checkbox.setChecked(DEFAULTS.get("toggle_experiment_mode", False))
        self.single_shutter_speed_radiobutton.setChecked(DEFAULTS.get("single_shutter", False))
        self.mult_shutter_speeds_radiobutton.setChecked(DEFAULTS.get("multiple_shutter", False))
        self.shutter_time_from.setText(str(DEFAULTS.get("shutter_speed_from", "")))
        self.shutter_time_to.setText(str(DEFAULTS.get("shutter_speed_to", "")))
        self.shutter_time_by.setText(str(DEFAULTS.get("shutter_speed_by", "")))
        self.number_of_experiments.setText(str(DEFAULTS.get("number_experiments", "")))
        self.time_between_experiments.setText(str(DEFAULTS.get("time_between_experiments", "")))
        # Scale Settings
        self.scale_measurement_checkbox.setChecked(DEFAULTS.get("scale_check", False))
        self.dat_combobox.setCurrentText(DEFAULTS.get("dat", "None"))
        self.clk_combobox.setCurrentText(DEFAULTS.get("clk", "None"))
        self.ref_unit_lineedit.setText(str(DEFAULTS.get("ref_unit", "")))
        self.scale_measurement_number_lineedit.setText(str(DEFAULTS.get("scale_num", "")))

    def load_settings(self):
        json_fname, _ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Json Files (*.json);;All Files (*)"
        )

        if not json_fname:
            return

        with open(json_fname, 'r') as json_file:
            loaded_settings = json.load(json_file)

        # General Camera Settings
        self.shutter_speed.setText(loaded_settings.get("shutter_speed", ""))
        self.lens_position.setText(loaded_settings.get("lens_position", ""))
        self.colour_gains_red.setText(loaded_settings.get("colour_gain_red", ""))
        self.colour_gains_blue.setText(loaded_settings.get("colour_gain_blue", ""))
        self.analog_gain.setText(loaded_settings.get("analog_gain", ""))
        self.pre_heat_time.setText(loaded_settings.get("preheat", ""))
        # Illuminated Capture Settings
        self.illuminated_image_count.setText(loaded_settings.get("image_capture", ""))
        self.pause_between_illuminated_capture.setText(loaded_settings.get("pause_between_capture", ""))
        self.save_illum_raw_checkbox.setChecked(loaded_settings.get("illum_raw", False))
        self.illuminated_image_name.setText(loaded_settings.get("illuminated_image_name", ""))
        self.lamp_drive_combobox.setCurrentText(loaded_settings.get("lamp_drive", "External source"))
        # Noise Settings
        self.noise_image_count.setText(loaded_settings.get("noise_image_capture", ""))
        self.noise_image_name.setText(loaded_settings.get("noise_image_name", ""))
        self.save_noise_raw_checkbox.setChecked(loaded_settings.get("noise_raw", False))
        self.pause_between_noise_capture.setText(loaded_settings.get("pause_between_noise_capture", ""))
        # LED Settings
        self.led1_combobox.setCurrentText(loaded_settings.get("led1_combobox", "None"))
        self.led2_combobox.setCurrentText(loaded_settings.get("led2_combobox", "None"))
        self.led_capture_checkbox.setChecked(loaded_settings.get("led_capture_checkbox", False))
        self.led_image_count.setText(loaded_settings.get("led_image_count", ""))
        self.pause_between_led_capture.setText(loaded_settings.get("pause_between_led_capture", ""))
        self.save_led_raw_checkbox.setChecked(loaded_settings.get("led_raw", False))
        self.led_image_name.setText(loaded_settings.get("led_image_name", ""))
        self.led_image_output_path.setText(loaded_settings.get(("led_image_output_path", "")))
        # Advanced Settings
        self.get_metada_checkbox.setChecked(loaded_settings.get("metadata", False))
        self.experiment_mode_checkbox.setChecked(loaded_settings.get("toggle_experiment_mode", False))
        self.single_shutter_speed_radiobutton.setChecked(loaded_settings.get("single_shutter", False))
        self.mult_shutter_speeds_radiobutton.setChecked(loaded_settings.get("multiple_shutter", False))
        self.shutter_time_from.setText(loaded_settings.get("shutter_speed_from", ""))
        self.shutter_time_to.setText(loaded_settings.get("shutter_speed_to", ""))
        self.shutter_time_by.setText(loaded_settings.get("shutter_speed_by", ""))
        self.number_of_experiments.setText(loaded_settings.get("number_experiments", ""))
        self.time_between_experiments.setText(loaded_settings.get("time_between_experiments", ""))
        # Scale Settings
        self.scale_measurement_checkbox.setChecked(loaded_settings.get("scale_check", False))
        self.dat_combobox.setCurrentText(loaded_settings.get("dat", "None"))
        self.clk_combobox.setCurrentText(loaded_settings.get("clk", "None"))
        self.ref_unit_lineedit.setText(loaded_settings.get("ref_unit", ""))
        self.scale_measurement_number_lineedit.setText(loaded_settings.get("scale_num", ""))

    def save_settings(self):
        capture_settings = {
            # General Camera Settings
            "shutter_speed": self.shutter_speed.text(),
            "lens_position": self.lens_position.text(),
            "colour_gain_red": self.colour_gains_red.text(),
            "colour_gain_blue": self.colour_gains_blue.text(),
            "analog_gain": self.analog_gain.text(),
            "preheat": self.pre_heat_time.text(),
            # Illuminated Capture Settings
            "image_capture": self.illuminated_image_count.text(),
            "illuminated_image_name": self.illuminated_image_name.text(),
            "pause_between_capture": self.pause_between_illuminated_capture.text(),
            "illum_raw": self.save_illum_raw_checkbox.isChecked(),
            "lamp_drive": self.lamp_drive_combobox.currentText(),
            # Noise Settings
            "noise_image_capture": self.noise_image_count.text(),
            "noise_image_name": self.noise_image_name.text(),
            "pause_between_noise_capture": self.pause_between_noise_capture.text(),
            "noise_raw": self.save_noise_raw_checkbox.isChecked(),
            # LED Settings
            "led1_combobox": self.led1_combobox.currentText(),
            "led2_combobox": self.led2_combobox.currentText(),
            "led_capture_checkbox": self.led_capture_checkbox.isChecked(),
            "led_image_count": self.led_image_count.text(),
            "pause_between_led_capture": self.pause_between_led_capture.text(),
            "led_raw": self.save_led_raw_checkbox.isChecked(),
            "led_image_name": self.led_image_name.text(),
            "led_image_output_path": self.led_image_output_path.text(),
            # Advanced Settings
            "metadata": self.get_metada_checkbox.isChecked(),
            "toggle_experiment_mode": self.experiment_mode_checkbox.isChecked(),
            "single_shutter": self.single_shutter_speed_radiobutton.isChecked(),
            "multiple_shutter": self.mult_shutter_speeds_radiobutton.isChecked(),
            "shutter_speed_from": self.shutter_time_from.text(),
            "shutter_speed_to": self.shutter_time_to.text(),
            "shutter_speed_by": self.shutter_time_by.text(),
            "number_experiments": self.number_of_experiments.text(),
            "time_between_experiments": self.time_between_experiments.text(),
            # Scale Settings
            "scale_check": self.scale_measurement_checkbox.isChecked(),
            "dat": self.dat_combobox.currentText(),
            "clk": self.clk_combobox.currentText(),
            "ref_unit": self.ref_unit_lineedit.text(),
            "scale_num": self.scale_measurement_number_lineedit.text(),
        }

        with open('capture_settings.json', "w") as settings_file:
            json.dump(capture_settings, settings_file, indent=2)

    def save_settings_as(self):
        capture_settings = {
            # General Camera Settings
            "shutter_speed": self.shutter_speed.text(),
            "lens_position": self.lens_position.text(),
            "colour_gain_red": self.colour_gains_red.text(),
            "colour_gain_blue": self.colour_gains_blue.text(),
            "analog_gain": self.analog_gain.text(),
            "preheat": self.pre_heat_time.text(),
            # Illuminated Capture Settings
            "image_capture": self.illuminated_image_count.text(),
            "illuminated_image_name": self.illuminated_image_name.text(),
            "pause_between_capture": self.pause_between_illuminated_capture.text(),
            "illum_raw": self.save_illum_raw_checkbox.isChecked(),
            "lamp_drive": self.lamp_drive_combobox.currentText(),
            # Noise Settings
            "noise_image_capture": self.noise_image_count.text(),
            "noise_image_name": self.noise_image_name.text(),
            "noise_raw": self.save_noise_raw_checkbox.isChecked(),
            "pause_between_noise_capture": self.pause_between_noise_capture.text(),
            # LED Settings
            "led1_combobox": self.led1_combobox.currentText(),
            "led2_combobox": self.led2_combobox.currentText(),
            "led_capture_checkbox": self.led_capture_checkbox.isChecked(),
            "led_image_count": self.led_image_count.text(),
            "pause_between_led_capture": self.pause_between_led_capture.text(),
            "led_raw": self.save_led_raw_checkbox.isChecked(),
            "led_image_name": self.led_image_name.text(),
            "led_image_output_path": self.led_image_output_path.text(),
            # Advanced Settings
            "metadata": self.get_metada_checkbox.isChecked(),
            "toggle_experiment_mode": self.experiment_mode_checkbox.isChecked(),
            "single_shutter": self.single_shutter_speed_radiobutton.isChecked(),
            "multiple_shutter": self.mult_shutter_speeds_radiobutton.isChecked(),
            "shutter_speed_from": self.shutter_time_from.text(),
            "shutter_speed_to": self.shutter_time_to.text(),
            "shutter_speed_by": self.shutter_time_by.text(),
            "number_experiments": self.number_of_experiments.text(),
            "time_between_experiments": self.time_between_experiments.text(),
            # Scale Settings
            "scale_check": self.scale_measurement_checkbox.isChecked(),
            "dat": self.dat_combobox.currentText(),
            "clk": self.clk_combobox.currentText(),
            "ref_unit": self.ref_unit_lineedit.text(),
            "scale_num": self.scale_measurement_number_lineedit.text(),
        }

        save_fname, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Json Files (*.json);;All Files (*)"
        )

        if save_fname:
            if not save_fname.lower().endswith(".json"):
                save_fname += ".json"
            with open(save_fname, 'w') as settings_file:
                json.dump(capture_settings, settings_file, indent=2)
        else:
            return

    def closeEvent(self, event):
        try:
            if hasattr(self, "picam2") and self.picam2 is not None:
                self.picam2.stop()
        except Exception as e:
            print(f"Error stopping camera: {e}")

        try:
            GPIO.cleanup()
        except Exception as e:
            print(f"Error cleaning up GPIO: {e}")

        event.accept()

    # ~ def capture(self):
        # ~ save_dir_image = self.illuminated_image_output_path.text().strip()
        # ~ save_dir_noise = self.noise_image_output_path.text().strip()
        # ~ main_title_image = self.illuminated_image_name.text().strip()
        # ~ main_title_noise = self.noise_image_name.text().strip()

        # ~ shutter_speed = int(self.shutter_speed.text())
        # ~ lens_position = float(self.lens_position.text())
        # ~ colour_gain_red = float(self.colour_gains_red.text())
        # ~ colour_gain_blue = float(self.colour_gains_blue.text())
        # ~ analog_gain = float(self.analog_gain.text())

        # ~ image_capture = int(self.illuminated_image_count.text())
        # ~ pause_between_capture = float(self.pause_between_illuminated_capture.text())

        # ~ noise_image_capture = int(self.noise_image_count.text())
        # ~ pause_between_noise_capture = float(self.pause_between_noise_capture.text())

        # ~ if self.lamp_drive_combobox.currentText() == 'External source':
            # ~ QMessageBox.warning(self, "Warning",
                                # ~ "WARNING! Using an external power source for the lamp requires separate captures for regular and noise images.")
            # ~ return

        # ~ if self.camera_available:
            # ~ sensor_width, sensor_height = self.picam2.sensor_resolution

            # ~ config = self.picam2.create_still_configuration(
                # ~ main={"size": (sensor_width, sensor_height)},
                # ~ controls={
                    # ~ "AeEnable": False,
                    # ~ "AwbEnable": False,
                    # ~ "Brightness": 0.0,
                    # ~ "Contrast": 1.0,
                    # ~ "Saturation": 1.0,
                    # ~ "Sharpness": 1.0,
                    # ~ "NoiseReductionMode": 0,
                    # ~ "ExposureTime": shutter_speed,
                    # ~ "AnalogueGain": analog_gain,
                    # ~ "ColourGains": (colour_gain_red, colour_gain_blue),
                    # ~ "LensPosition": lens_position
                # ~ }
            # ~ )

        # ~ # Camera Initializing Time
        # ~ time.sleep(2.0)

        # ~ if self.get_metada_checkbox.isChecked():
            # ~ self.picam2.metadata_enabled = True

        # ~ self.capture_thread = CaptureThread(
            # ~ save_dir_image, save_dir_noise, main_title_image, main_title_noise,
            # ~ image_capture, noise_image_capture, pause_between_capture, pause_between_noise_capture,
            # ~ picam2=self.picam2 if self.camera_available else None
        # ~ )

        # ~ self.capture_thread.update_noise.connect(lambda x: self.noise_left_label.setText(str(x)))
        # ~ self.capture_thread.update_image.connect(lambda x: self.image_left_label.setText(str(x)))
        # ~ self.capture_thread.start()

app = QApplication(sys.argv)
UIWindow = UI()
app.exec()
