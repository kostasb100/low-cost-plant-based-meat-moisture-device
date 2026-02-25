from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QPushButton, QLabel, QFileDialog,
    QRadioButton, QSlider, QComboBox, QLineEdit, QCheckBox, QAction,
    QMessageBox
)
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QImage
import json, sys, math, os
import cv2 as cv
import numpy as np
from corner_selector import CornerSelectorWindow

DEFAULTS = {
    # Image
    "image": None,
    # Blur Settings
    "blur_method": "No blur",
    "blur_k1": "",
    "blur_k2": "",
    "blur_sigma": "",
    # Threshold Settings
    "thresh_method": "No_threshold",
    "thresh_val": 0,
    "max_val": 255,
    # Edge Closing
    "edge_closing_enabled": False,
    "morph_k1": "",
    "morph_k2": "",
    # Area and Center Point Detection
    "area_center_enabled": False,
    "area_min": 0,
    "area_max": 0,
    "center_points": "",
    "area_pixels": "",
    # Corner Detection
    "show_reference_line": False,
    "show_reference_ctr_point": False,
    "distance_from_ref_points": "",
    "angle": "",
    "show_corners": False,
    "show_sample_corner_line": False,
}

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        uic.loadUi("image_2.ui",self)
        self.open_file_button = self.findChild(QPushButton, "pushButton")
        self.apply_settings_button = self.findChild(QPushButton, "pushButton_2")
        self.corner_selection_button = self.findChild(QPushButton, "pushButton_3")
        self.edge_closing_radio_button = self.findChild(QRadioButton, "radioButton_3")
        self.displayed_image_label = self.findChild(QLabel, "label")

        self.threshold_value_slider = self.findChild(QSlider, "horizontalSlider")
        self.threshold_maximum_value_slider = self.findChild(QSlider, "horizontalSlider_2")
        self.area_detect_min_slider = self.findChild(QSlider, "horizontalSlider_5")
        self.area_detect_max_slider = self.findChild(QSlider, "horizontalSlider_6")

        self.threshold_value = self.findChild(QLabel, "label_5")
        self.threshold_max_value = self.findChild(QLabel, "label_7")
        self.center_point_label = self.findChild(QLabel, "label_28")
        self.area_sample_label = self.findChild(QLabel, "label_30")
        self.area_detect_min_label = self.findChild(QLabel, "label_33")
        self.area_detect_max_label = self.findChild(QLabel, "label_35")
        self.dist_from_ref_point_label = self.findChild(QLabel, "label_76")
        self.angle_deg_label = self.findChild(QLabel, "label_77")
        self.sample_corner_label = self.findChild(QLabel, "label_37")
        self.ref_corner_label = self.findChild(QLabel, "label_41")

        self.gaussian_blur_kernel1_lineedit = self.findChild(QLineEdit, "lineEdit")
        self.gaussian_blur_kernel2_lineedit = self.findChild(QLineEdit, "lineEdit_2")
        self.gaussian_blur_sigmax_lineedit = self.findChild(QLineEdit, "lineEdit_3")
        self.edge_closing_kernel1_lineedit = self.findChild(QLineEdit, "lineEdit_5")
        self.edge_closing_kernel2_lineedit = self.findChild(QLineEdit, "lineEdit_6")

        self.threshold_value_slider.valueChanged.connect(self.thresh_slide)
        self.threshold_maximum_value_slider.valueChanged.connect(self.max_slide)
        self.area_detect_min_slider.valueChanged.connect(self.area_range_a)
        self.area_detect_max_slider.valueChanged.connect(self.area_range_b)

        self.threshold_value_slider.setMaximum(255)
        self.threshold_maximum_value_slider.setMaximum(255)
        self.threshold_maximum_value_slider.setValue(255)

        self.area_detect_min_slider.setMaximum(9000000)
        self.area_detect_max_slider.setMaximum(9000000)
        self.area_detect_min_slider.setSingleStep(1000)
        self.area_detect_max_slider.setSingleStep(1000)

        self.thresholding_method_combobox = self.findChild(QComboBox, "comboBox")
        self.blur_method_combobox = self.findChild(QComboBox, "comboBox_2")

        self.area_center_point_detect_checkbox = self.findChild(QCheckBox, "checkBox")
        self.show_ref_line_checkbox = self.findChild(QCheckBox, "checkBox_3")
        self.show_ref_center_point_checkbox = self.findChild(QCheckBox, "checkBox_4")
        self.show_corner_checkbox = self.findChild(QCheckBox, "checkBox_6")
        self.show_sample_corner_line_checkbox = self.findChild(QCheckBox, "checkBox_7")

        self.actionNew.triggered.connect(self.new_settings)
        self.actionOpen.triggered.connect(self.load_settings)
        self.actionSave.triggered.connect(self.save_settings)
        self.actionSave_Settings_As.triggered.connect(self.save_settings_as)
        self.actionSave_Image.triggered.connect(self.save_image)
        self.actionSave_Image_As.triggered.connect(self.save_image_as)

        self.open_file_button.clicked.connect(self.load_show_initial_image)
        self.apply_settings_button.clicked.connect(self.img_processing)
        self.corner_selection_button.clicked.connect(self.choose_sample_corners)
        self.show()

    def new_settings(self):
        self.displayed_image_label.clear()

        # Blur Settings
        self.blur_method_combobox.setCurrentText(DEFAULTS.get("blur_method", "No blur"))
        self.gaussian_blur_kernel1_lineedit.setText(str(DEFAULTS.get("blur_kernel_k1", "")))
        self.gaussian_blur_kernel2_lineedit.setText(str(DEFAULTS.get("blur_kernel_k2", "")))
        self.gaussian_blur_sigmax_lineedit.setText(str(DEFAULTS.get("blur_sigma", "")))

        # Threshold Settings
        self.thresholding_method_combobox.setCurrentText(DEFAULTS.get("threshold_method", "No threshold"))
        self.threshold_value_slider.setValue(DEFAULTS.get("threshold_val", 0))
        self.threshold_maximum_value_slider.setValue(DEFAULTS.get("max_val", 255))
        self.threshold_value.setText(str(DEFAULTS.get("threshold_val", 0)))
        self.threshold_max_value.setText(str(DEFAULTS.get("max_val", 255)))

        # Edge Closing
        self.edge_closing_radio_button.setChecked(DEFAULTS.get("edge_closing_radio", False))
        self.edge_closing_kernel1_lineedit.setText(str(DEFAULTS.get("morph_kernel_k1", "")))
        self.edge_closing_kernel2_lineedit.setText(str(DEFAULTS.get("morph_kernel_k2", "")))

        # Area and Center Point Detection
        self.area_center_point_detect_checkbox.setChecked(DEFAULTS.get("area_center_check", False))
        self.area_detect_min_slider.setValue(DEFAULTS.get("area_min", 0))
        self.area_detect_max_slider.setValue(DEFAULTS.get("area_max", 0))
        self.area_detect_min_label.setText(str(DEFAULTS.get("area_min", 0)))
        self.area_detect_max_label.setText(str(DEFAULTS.get("area_max", 0)))
        self.center_point_label.setText(str(DEFAULTS.get("center_points", "")))
        self.area_sample_label.setText(str(DEFAULTS.get("area_pixels", "")))

        # Corner Detection
        self.show_ref_line_checkbox.setChecked(DEFAULTS.get("show_reference_line", False))
        self.show_ref_center_point_checkbox.setChecked(DEFAULTS.get("show_reference_ctr_point", False))
        self.show_corner_checkbox.setChecked(DEFAULTS.get("show_corners", False))
        self.show_sample_corner_line_checkbox.setChecked(DEFAULTS.get("show_sample_corner_line", False))
        self.dist_from_ref_point_label.setText(str(DEFAULTS.get("distance_from_ref_points", "")))
        self.angle_deg_label.setText(str(DEFAULTS.get("angle", "")))

    def load_settings(self):
        json_fname,_ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "",
            "Json Files (*.json);;All Files (*)"
        )

        if not json_fname:
            return

        with open(json_fname, 'r') as json_file:
            loaded_settings = json.load(json_file)

        # Blur Settings
        self.blur_method_combobox.setCurrentText(loaded_settings.get('blur_method', 'No_blur'))
        self.gaussian_blur_kernel1_lineedit.setText(loaded_settings.get('blur_k1', ''))
        self.gaussian_blur_kernel2_lineedit.setText(loaded_settings.get('blur_k2', ''))
        self.gaussian_blur_sigmax_lineedit.setText(loaded_settings.get('blur_sigma', ''))

        # Threshold Settings
        self.thresholding_method_combobox.setCurrentText(loaded_settings.get('thresh_method', 'No_threshold'))
        self.threshold_value_slider.setValue(int(loaded_settings.get('thresh_val', 0)))
        self.threshold_maximum_value_slider.setValue(int(loaded_settings.get('max_val', 255)))

        # Edge Closing
        self.edge_closing_radio_button.setChecked(bool(loaded_settings.get('edge_closing_enabled', False)))
        self.edge_closing_kernel1_lineedit.setText(loaded_settings.get('morph_k1', ''))
        self.edge_closing_kernel2_lineedit.setText(loaded_settings.get('morph_k2', ''))

        # Area and Center Point Detection
        self.area_center_point_detect_checkbox.setChecked(bool(loaded_settings.get('area_center_enabled', False)))
        self.area_detect_min_slider.setValue(int(loaded_settings.get('area_min', 0)))
        self.area_detect_max_slider.setValue(int(loaded_settings.get('area_max', 0)))

    def save_settings(self):
        settings = {
            # Blur Settings
            "blur_method": self.blur_method_combobox.currentText(),
            "blur_k1": self.gaussian_blur_kernel1_lineedit.text(),
            "blur_k2": self.gaussian_blur_kernel2_lineedit.text(),
            "blur_sigma": self.gaussian_blur_sigmax_lineedit.text(),

            # Threshold Settings
            "thresh_method": self.thresholding_method_combobox.currentText(),
            "thresh_val": self.threshold_value_slider.value(),
            "max_val": self.threshold_maximum_value_slider.value(),

            # Edge Closing
            "edge_closing_enabled": self.edge_closing_radio_button.isChecked(),
            "morph_k1": self.edge_closing_kernel1_lineedit.text(),
            "morph_k2": self.edge_closing_kernel2_lineedit.text(),

            # Area and Center Point Detection
            "area_center_enabled": self.area_center_point_detect_checkbox.isChecked(),
            "area_min": self.area_detect_min_slider.value(),
            "area_max": self.area_detect_max_slider.value(),
            "center_points": self.center_point_label.text(),
            "area_pixels": self.area_sample_label.text(),

            # Corner Detection
            "relative_corner_threshold": self.harris_corner_relative_thresh_lineedit.text(),
            "distance_from_ref_points": self.dist_from_ref_point_label.text(),
            "angle": self.angle_deg_label.text()
            }

        with open('settings.json', "w") as settings_file:
            json.dump(settings, settings_file, indent=2)

    def save_settings_as(self):
        settings = {
            # Blur Settings
            "blur_method": self.blur_method_combobox.currentText(),
            "blur_k1": self.gaussian_blur_kernel1_lineedit.text(),
            "blur_k2": self.gaussian_blur_kernel2_lineedit.text(),
            "blur_sigma": self.gaussian_blur_sigmax_lineedit.text(),

            # Threshold Settings
            "thresh_method": self.thresholding_method_combobox.currentText(),
            "thresh_val": self.threshold_value_slider.value(),
            "max_val": self.threshold_maximum_value_slider.value(),

            # Edge Closing
            "edge_closing_enabled": self.edge_closing_radio_button.isChecked(),
            "morph_k1": self.edge_closing_kernel1_lineedit.text(),
            "morph_k2": self.edge_closing_kernel2_lineedit.text(),

            # Area and Center Point Detection
            "area_center_enabled": self.area_center_point_detect_checkbox.isChecked(),
            "area_min": self.area_detect_min_slider.value(),
            "area_max": self.area_detect_max_slider.value(),
            "center_points": self.center_point_label.text(),
            "area_pixels": self.area_sample_label.text(),
        }

        save_fname,_ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Json Files (*.json);;All Files (*)"
        )

        if save_fname:
            if not save_fname.lower().endswith(".json"):
                save_fname += ".json"
            with open(save_fname, 'w') as settings_file:
                json.dump(settings, settings_file, indent = 2)
        else:
            return

    def save_image_as(self):
        if not hasattr(self, "color_img"):
            QMessageBox.warning(self, "No image", "No processed image available to save.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image As",
            "",
            "JPEG Files (*.jpg *.jpeg);;PNG Files (*.png)"
        )

        if file_path:
            success = cv.imwrite(file_path, self.color_img)
            if not success:
                QMessageBox.critical(self, "Error", "Failed to save the image.")
            else:
                QMessageBox.information(self, "Saved", f"Image saved successfully:\n{file_path}")

    def save_image(self):
        if not hasattr(self, "color_img"):
            QMessageBox.warning(self, "No image", "No processed image available to save.")
            return

        file_path = "untitled.jpg"

        success = cv.imwrite(file_path, self.color_img)
        if not success:
            QMessageBox.critical(self, "Error", "Failed to save the image.")
        else:
            QMessageBox.information(self, "Saved", f"Image saved successfully:\n{file_path}")

    def thresh_slide(self, value_thresh):
        self.threshold_value.setText(str(value_thresh))

    def max_slide(self, value_max):
        self.threshold_max_value.setText(str(value_max))

    def area_range_a(self, value):
        self.area_detect_min_label.setText(str(value))

    def area_range_b(self, value):
        self.area_detect_max_label.setText(str(value))

    def resize_with_aspect_ratio(self, image, width=None, height=None, inter=cv.INTER_AREA):
        (h, w) = image.shape[:2]
        if width is None and height is None:
            return image
        if width is not None:
            r = width / float(w)
            dim = (width, int(h * r))
        else:
            r = height / float(h)
            dim = (int(w * r), height)
        return cv.resize(image, dim, interpolation=inter)

    def load_show_initial_image(self):
        fname = QFileDialog.getOpenFileName(self, "Open File","", "JPG Files (*.jpg);;PNG Files (*.png)")
        img = cv.imread(fname[0])
        if img is None:
            return

        img_rgb = cv.cvtColor(img, cv.COLOR_BGR2RGB)

        self.img_original = img_rgb.copy()

        img_resized = self.resize_with_aspect_ratio(img_rgb,self.displayed_image_label.width(),self.displayed_image_label.height())

        h, w, ch = img_resized.shape
        bytes_per_line = ch * w
        qimg = QImage(img_resized.data, w, h,bytes_per_line, QImage.Format_RGB888)

        self.pixmap = QPixmap(qimg)
        self.displayed_image_label.setPixmap(self.pixmap)
        
    def choose_sample_corners(self):
        self.selector_window = CornerSelectorWindow(self.thresh)
        self.selector_window.exec()
        self.points = self.selector_window.view.selected_points

    def show_error(self, message: str):
        msg = QMessageBox(self)
        msg.setWindowTitle('Error')
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        x = msg.exec_()

    def img_processing(self):
        self.img_gray = cv.cvtColor(self.img_original, cv.COLOR_RGB2GRAY)

        value_thresh = self.threshold_value_slider.value()
        value_max = self.threshold_maximum_value_slider.value()
        area_a_value = self.area_detect_min_slider.value()
        area_b_value = self.area_detect_max_slider.value()

        thresholding_method_selection = self.thresholding_method_combobox.currentText()
        blur_method_selection = self.blur_method_combobox.currentText()

        if blur_method_selection == "No blur":
            pass
        elif blur_method_selection == "Gaussian blur":
            try:
                k1 = int(self.gaussian_blur_kernel1_lineedit.text())
                k2 = int(self.gaussian_blur_kernel2_lineedit.text())
                sigma = int(self.gaussian_blur_sigmax_lineedit.text())
            except ValueError:
                self.show_error("Gaussian blur kernel sizes and sigma must be integers.")
                return

            if k1 % 2 == 0 or k2 % 2 == 0 or k1 < 3 or k2 < 3:
                self.show_error("Gaussian blur kernel sizes must be odd integers ≥ 3.")
                return
            elif sigma < 0:
                self.show_error("Sigma must be a positive integer")
                return
            self.img_gray = cv.GaussianBlur(self.img_gray, (k1, k2), sigma)

        elif blur_method_selection == "Median blur":
            try:
                ksize = int(self.gaussian_blur_kernel1_lineedit.text())
            except ValueError:
                self.show_error("Median blur kernel size must be an odd integer.")
                return
            if ksize % 2 == 0 or ksize < 3:
                self.show_error("Median blur kernel must be an odd integer ≥ 3.")
                return
            self.img_gray = cv.medianBlur(self.img_gray, ksize)
        elif blur_method_selection == "Average blur":
            try:
                k1 = int(self.gaussian_blur_kernel1_lineedit.text())
                k2 = int(self.gaussian_blur_kernel2_lineedit.text())
            except ValueError:
                self.show_error("Average blur kernel sizes must be integers.")
                return
            if k1 % 2 == 0 or k2 % 2 == 0 or k1 < 3 or k2 < 3:
                self.show_error("Average blur kernel sizes must be odd integers ≥ 3.")
                return

            self.img_gray = cv.blur(self.img_gray, (k1, k2))

        if thresholding_method_selection == "No threshold":
            pass
        elif thresholding_method_selection == "Thresh Binary":
            _, self.thresh = cv.threshold(self.img_gray, value_thresh, value_max, cv.THRESH_BINARY)
        elif thresholding_method_selection == "Thresh Binary Inverted":
            _, self.thresh = cv.threshold(self.img_gray, value_thresh, value_max, cv.THRESH_BINARY_INV)
        elif thresholding_method_selection == "Thresh Trunc":
            _, self.thresh = cv.threshold(self.img_gray, value_thresh, value_max, cv.THRESH_TRUNC)
        elif thresholding_method_selection == "Thresh To Zero":
            _, self.thresh = cv.threshold(self.img_gray, value_thresh, value_max, cv.THRESH_TOZERO)
        elif thresholding_method_selection == "Thresh Otsu":
            _, self.thresh = cv.threshold(self.img_gray, value_thresh, value_max, cv.THRESH_BINARY + cv.THRESH_OTSU)

        if self.edge_closing_radio_button.isChecked():
            try:
                k1 = int(self.edge_closing_kernel1_lineedit.text())
                k2 = int(self.edge_closing_kernel2_lineedit.text())
            except ValueError:
                self.show_error("Morphology kernel sizes must be integers.")
                return
            if k1 % 2 == 0 or k2 % 2 == 0 or k1 < 3 or k2 < 3:
                self.show_error("Morphology  kernel sizes must be odd integers ≥ 3.")
                return
            kernel = cv.getStructuringElement(cv.MORPH_RECT, (k1, k2))
            self.thresh = cv.morphologyEx(self.thresh, cv.MORPH_GRADIENT, kernel)

            if self.area_center_point_detect_checkbox.isChecked():
                self.contours, self.hierarchy = cv.findContours(self.thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
                color_img = cv.cvtColor(self.thresh, cv.COLOR_GRAY2BGR)
                self.color_img = color_img
                self.center_point = []

                area_min = self.area_detect_min_slider.value()
                area_max = self.area_detect_max_slider.value()

                area_contour_pairs = []
                for i in self.contours:
                    area = cv.contourArea(i)
                    if area_min < area < area_max:
                        area_contour_pairs.append((area, i))

                area_contour_pairs_sorted = sorted(area_contour_pairs, key=lambda x: x[0])

                if len(area_contour_pairs_sorted) >= 2:
                    a0, a1 = area_contour_pairs_sorted[0][0], area_contour_pairs_sorted[1][0]
                    c0, c1 = area_contour_pairs_sorted[0][1], area_contour_pairs_sorted[1][1]

                    if (0.99 * a1 < a0 < 1.01 * a1) or (0.99 * a0 < a1 < 1.01 * a0):
                        sample_area = (a0 + a1) / 2

                        M0 = cv.moments(c0)
                        M1 = cv.moments(c1)

                        if M0['m00'] != 0 and M1['m00'] != 0:
                            cx0, cy0 = M0['m10']/M0['m00'], M0['m01']/M0['m00']
                            cx1, cy1 = M1['m10']/M1['m00'], M1['m01']/M1['m00']

                            avg_cx = int((cx0 + cx1) / 2)
                            avg_cy = int((cy0 + cy1) / 2)

                            self.center_point.append([avg_cx,avg_cy])
                            cv.drawContours(color_img, [c0, c1], -1, (0, 255, 0), 2)
                            cv.circle(color_img, (avg_cx, avg_cy), 14, (0, 255, 0), -1)

                reference_pairs = area_contour_pairs_sorted[2:]

                if len(reference_pairs) >= 2:
                    r0, r1 = reference_pairs[0][1], reference_pairs[1][1]  # contours
                    M0, M1 = cv.moments(r0), cv.moments(r1)

                    if M0['m00'] != 0 and M1['m00'] != 0:
                        cx0, cy0 = M0['m10'] / M0['m00'], M0['m01'] / M0['m00']
                        cx1, cy1 = M1['m10'] / M1['m00'], M1['m01'] / M1['m00']

                        avg_cx = int((cx0 + cx1) / 2)
                        avg_cy = int((cy0 + cy1) / 2)

                        self.center_point.append([avg_cx, avg_cy])

                        cv.drawContours(color_img, [r0, r1], -1, (0, 0, 255), 2)
                        cv.circle(color_img, (avg_cx, avg_cy), 14, (0, 0, 255), -1)

                if self.center_point:
                    self.center_point_label.setText(str(self.center_point))
                if sample_area:
                    self.area_sample_label.setText(str(sample_area))
                if self.show_ref_line_checkbox.isChecked():
                    cv.line(color_img, (0, line_midpoint[0][1]), (width, line_midpoint[0][1]), (0, 0, 255), 8)
                if self.show_ref_center_point_checkbox.isChecked():
                    cv.circle(color_img, (img_center_x, img_center_y), 25, (0, 0, 255), -1)
                if self.show_corner_checkbox.isChecked():
                    if self.points:
                        for i in range(len(self.points[:4])):
                            cv.circle(color_img, (self.points[i][0], self.points[i][1]), 20, (255, 0, 0), -1)
                        for x in range(len(self.points[:4])):
                            cv.circle(color_img, (self.points[4+x][0], self.points[4+x][1]), 20, (255, 122, 122), -1)

                        sample_points = self.points[:4]
                        reference_points = self.points[4:]

                        sample_points_x_sorted= sorted(sample_points, key=lambda x: x[0])
                        reference_points_x_sorted= sorted(reference_points, key=lambda x: x[0])

                        self.sample_corner_label.setText(str(sample_points_x_sorted))
                        self.ref_corner_label.setText(str(reference_points_x_sorted))

                        sample_points_y_sorted= sorted(sample_points, key=lambda x: x[1])
                        reference_points_y_sorted= sorted(reference_points, key=lambda x: x[1])

                        sample_points_xy_sorted_1 = sorted(sample_points_y_sorted[:2], key=lambda x: x[0]) # sample bottom c+d
                        reference_points_xy_sorted_1 = sorted(reference_points_y_sorted[:2], key=lambda x: x[0]) # ref bottom c2+d2
                        sample_points_xy_sorted_2 = sorted(sample_points_y_sorted[2:], key=lambda x: x[0]) # sample top a+b
                        reference_points_xy_sorted_2 = sorted(reference_points_y_sorted[2:], key=lambda x: x[0]) # ref top a2+b2

                        top_sample_line_vector = np.array(
                            [sample_points_xy_sorted_2[1][0] - sample_points_xy_sorted_2[0][0],
                             sample_points_xy_sorted_2[1][1] - sample_points_xy_sorted_2[0][1]])

                        bottom_sample_line_vector = np.array(
                            [sample_points_xy_sorted_1[1][0] - sample_points_xy_sorted_1[0][0],
                             sample_points_xy_sorted_1[1][1] - sample_points_xy_sorted_1[0][1]])

                        top_reference_line_vector = np.array(
                            [reference_points_xy_sorted_2[1][0] - reference_points_xy_sorted_2[0][0],
                             reference_points_xy_sorted_2[1][1] - reference_points_xy_sorted_2[0][1]])

                        bottom_reference_line_vector = np.array(
                            [reference_points_xy_sorted_1[1][0] - reference_points_xy_sorted_1[0][0],
                             reference_points_xy_sorted_1[1][1] - reference_points_xy_sorted_1[0][1]])

                        dot_product1 = np.dot(top_sample_line_vector, top_reference_line_vector)
                        norms1 = np.linalg.norm(top_sample_line_vector) * np.linalg.norm(top_reference_line_vector)
                        angle_rad1 = np.arccos(dot_product1 / norms1)
                        angle_deg1 = np.degrees(angle_rad1)

                        dot_product2 = np.dot(bottom_sample_line_vector, bottom_reference_line_vector)
                        norms2 = np.linalg.norm(bottom_sample_line_vector) * np.linalg.norm(bottom_reference_line_vector)
                        angle_rad2 = np.arccos(dot_product2 / norms2)
                        angle_deg2 = np.degrees(angle_rad2)

                        angle_deg_avg = (angle_deg1 + angle_deg2) / 2

                        distance_between_corner_points = []

                        for i in range(len(sample_points_x_sorted)):
                            distance_between_corner_points.append(round(math.dist(sample_points_x_sorted[i],reference_points_x_sorted[i])))

                        self.dist_from_ref_point_label.setText(str(distance_between_corner_points))
                        self.angle_deg_label.setText(str(round(angle_deg_avg,2)))

                if self.show_sample_corner_line_checkbox.isChecked():
                    cv.line(color_img, (dist_lower[0][0], dist_lower[0][1]),
                                 (dist_lower[1][0], dist_lower[1][1]), (255, 255, 0), 8)
                    pass

        if self.area_center_point_detect_checkbox.isChecked() and color_img is not None:
            final_img = color_img
        else:
            final_img = self.thresh

        if len(final_img.shape) == 2:
            img_resized = self.resize_with_aspect_ratio(final_img, self.displayed_image_label.width(), self.displayed_image_label.height())
            h, w = img_resized.shape
            bytes_per_line = w
            qimg = QImage(img_resized.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
        else:
            img_resized = self.resize_with_aspect_ratio(final_img, self.displayed_image_label.width(), self.displayed_image_label.height())
            h, w, ch = img_resized.shape
            bytes_per_line = ch * w
            img_rgb = cv.cvtColor(img_resized, cv.COLOR_BGR2RGB)
            qimg = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)

        self.pixmap = QPixmap(qimg)
        self.displayed_image_label.setPixmap(self.pixmap)

app = QApplication(sys.argv)
UIWindow = UI()
app.exec()