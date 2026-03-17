import sys
from PyQt6.QtWidgets import QApplication, QFileDialog
from halftone_ui import HalftoneUI
from halftone_core import HalftoneProcessor

class HalftoneApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ui = HalftoneUI()
        self.current_image_path = None
        self.custom_mask_path = None 
        self.processed_image = None
        self.connect_signals()
        self.ui.show()

    def connect_signals(self):
        self.ui.btn_load.clicked.connect(self.load_image)
        self.ui.btn_load_mask.clicked.connect(self.load_mask)
        self.ui.btn_save.clicked.connect(self.save_image)
        
        self.ui.slider_size.valueChanged.connect(self.on_settings_changed)
        self.ui.slider_angle.valueChanged.connect(self.on_settings_changed)
        self.ui.slider_tolerance.valueChanged.connect(self.on_settings_changed)
        
        self.ui.chk_alpha_halftone.stateChanged.connect(self.on_settings_changed)
        self.ui.chk_antialias.stateChanged.connect(self.on_settings_changed)
        self.ui.chk_knockout.stateChanged.connect(self.toggle_knockout)
        self.ui.combo_shape.currentTextChanged.connect(self.on_shape_changed)

    def toggle_knockout(self):
        self.ui.slider_tolerance.setEnabled(self.ui.chk_knockout.isChecked())
        self.on_settings_changed()

    def on_shape_changed(self, shape_text):
        
        if shape_text == "custom" and not self.custom_mask_path:
            self.ui.lbl_mask_status.setText("⚠️ Please load a mask first!")
            self.ui.lbl_mask_status.setStyleSheet("color: #ffaa00; font-size: 11px;")
        self.on_settings_changed()

    def load_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open Design", "", "Images (*.png *.jpg *.jpeg)")
        if file_name:
            self.current_image_path = file_name
            self.on_settings_changed()
            self.ui.btn_save.setEnabled(True)

    def load_mask(self):
        file_name, _ = QFileDialog.getOpenFileName(self.ui, "Open Custom Shape", "", "Images (*.png *.jpg)")
        if file_name:
            self.custom_mask_path = file_name
            self.ui.lbl_mask_status.setText("✅ Custom Mask Loaded")
            self.ui.lbl_mask_status.setStyleSheet("color: #00ca8b; font-size: 11px;")
            
            self.ui.combo_shape.setCurrentText("custom")

    def on_settings_changed(self):
        if not self.current_image_path: return
            
        size_val = self.ui.slider_size.value()
        angle = self.ui.slider_angle.value()
        tolerance = self.ui.slider_tolerance.value()
        
        self.ui.lbl_size_val.setText(f"Pattern Size: {size_val}")
        self.ui.lbl_angle_val.setText(f"Angle: {angle}°")

        self.processed_image = HalftoneProcessor.process_image(
            image_path=self.current_image_path,
            pattern_size=size_val,
            angle=angle,
            shape_name=self.ui.combo_shape.currentText(),
            alpha_halftone=self.ui.chk_alpha_halftone.isChecked(),
            knockout_black=self.ui.chk_knockout.isChecked(),
            black_tolerance=tolerance,
            custom_mask_path=self.custom_mask_path,
            antialias=self.ui.chk_antialias.isChecked() 
        )
        self.ui.update_image_display(self.processed_image)

    def save_image(self):
        if self.processed_image:
            save_path, _ = QFileDialog.getSaveFileName(self.ui, "Export for RIP", "DTF_Ready.png", "PNG Files (*.png)")
            if save_path:
                self.processed_image.save(save_path, format="PNG")

if __name__ == "__main__":
    app = HalftoneApp()
    sys.exit(app.app.exec())