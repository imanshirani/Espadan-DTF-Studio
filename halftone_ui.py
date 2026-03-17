from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QSlider, QFileDialog, QGroupBox, QCheckBox, 
                             QComboBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                             QDialog)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QPixmap, QImage, QPainter, QDesktopServices
from PIL.ImageQt import ImageQt
import style 


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Espadan DTF Studio Version 0.001")
        self.setFixedSize(380, 200)
        self.setStyleSheet(style.ABOUT_DIALOG)

        layout = QVBoxLayout()
        
        info_label = QLabel(style.ABOUT_HTML_CONTENT)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        btn_layout = QHBoxLayout()
        
        self.btn_github = QPushButton("🐙 GitHub")
        self.btn_github.setStyleSheet(style.BTN_GITHUB)
        self.btn_github.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/imanshirani/Espadan-DTF-Studio"))) 
        
        self.btn_paypal = QPushButton("☕ Donate (PayPal)")
        self.btn_paypal.setStyleSheet(style.BTN_PAYPAL)
        self.btn_paypal.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4"))) 

        btn_layout.addWidget(self.btn_github)
        btn_layout.addWidget(self.btn_paypal)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)



class ZoomableView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        self.setStyleSheet(style.IMAGE_VIEWER)
        self.setMinimumSize(650, 500)
        self.is_first_load = True

    def set_image(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        
        if self.is_first_load:
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.is_first_load = False

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor
        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor
        self.scale(zoom_factor, zoom_factor)



class HalftoneUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Espadan DTF Studio - Pro Edition")
        self.resize(1000, 750)
        self.setStyleSheet(style.MAIN_WINDOW)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        settings_layout = QVBoxLayout()
        settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.btn_load = QPushButton("📂 1. Load Main Image")
        settings_layout.addWidget(self.btn_load)

        self.btn_load_mask = QPushButton("💖 2. Load Custom Shape (Optional)")
        self.btn_load_mask.setStyleSheet(style.BTN_CUSTOM_SHAPE)
        settings_layout.addWidget(self.btn_load_mask)
        
        self.lbl_mask_status = QLabel("No custom shape loaded.")
        self.lbl_mask_status.setStyleSheet(style.LBL_STATUS_DEFAULT)
        settings_layout.addWidget(self.lbl_mask_status)

        group_dtf = QGroupBox("DTF & Render Settings")
        vbox_dtf = QVBoxLayout()
        self.chk_alpha_halftone = QCheckBox("Halftone Alpha Channel")
        self.chk_alpha_halftone.setChecked(True)
        vbox_dtf.addWidget(self.chk_alpha_halftone)

        self.chk_antialias = QCheckBox("High Quality Render (Anti-Aliasing)")
        self.chk_antialias.setChecked(True)
        vbox_dtf.addWidget(self.chk_antialias)

        self.chk_knockout = QCheckBox("Knockout Black")
        vbox_dtf.addWidget(self.chk_knockout)

        self.slider_tolerance = QSlider(Qt.Orientation.Horizontal)
        self.slider_tolerance.setRange(0, 100)
        self.slider_tolerance.setValue(30)
        self.slider_tolerance.setEnabled(False) 
        vbox_dtf.addWidget(QLabel("Black Tolerance:"))
        vbox_dtf.addWidget(self.slider_tolerance)
        group_dtf.setLayout(vbox_dtf)
        settings_layout.addWidget(group_dtf)

        group_halftone = QGroupBox("Halftone Grid")
        vbox_halftone = QVBoxLayout()
        self.combo_shape = QComboBox()
        self.combo_shape.addItems(["dot", "line", "square", "cross", "diamond", "custom"])
        self.combo_shape.setStyleSheet(style.COMBO_BOX)
        vbox_halftone.addWidget(QLabel("Halftone Shape:"))
        vbox_halftone.addWidget(self.combo_shape)

        self.lbl_size_val = QLabel("Pattern Size: 30")
        self.slider_size = QSlider(Qt.Orientation.Horizontal)
        self.slider_size.setRange(5, 100)
        self.slider_size.setValue(30)
        
        self.lbl_angle_val = QLabel("Angle: 22°")
        self.slider_angle = QSlider(Qt.Orientation.Horizontal)
        self.slider_angle.setRange(0, 90)
        self.slider_angle.setValue(22)

        vbox_halftone.addWidget(self.lbl_size_val)
        vbox_halftone.addWidget(self.slider_size)
        vbox_halftone.addWidget(self.lbl_angle_val)
        vbox_halftone.addWidget(self.slider_angle)
        group_halftone.setLayout(vbox_halftone)
        settings_layout.addWidget(group_halftone)

        settings_layout.addStretch()
        
        self.btn_save = QPushButton("💾 Export PNG")
        self.btn_save.setStyleSheet(style.BTN_EXPORT)
        self.btn_save.setEnabled(False)
        settings_layout.addWidget(self.btn_save)

        self.btn_about = QPushButton("ℹ️ About / Support")
        self.btn_about.setStyleSheet(style.BTN_ABOUT)
        self.btn_about.clicked.connect(self.show_about_dialog)
        settings_layout.addWidget(self.btn_about)

        self.image_view = ZoomableView()

        main_layout.addLayout(settings_layout, 2)
        main_layout.addWidget(self.image_view, 5) 
        self.setLayout(main_layout)

    def update_image_display(self, pil_img):
        qim = ImageQt(pil_img)
        pixmap = QPixmap.fromImage(qim)
        self.image_view.set_image(pixmap)

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()