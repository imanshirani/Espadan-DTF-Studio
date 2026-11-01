# ==========================================
# Espadan DTF Studio - Theme & Style Library
# ==========================================

# --- 1. Global Window Styles ---
MAIN_WINDOW = """
    QWidget { background-color: #10151d; color: #e2e8f0; font-family: 'Segoe UI'; font-size: 12px; }
    QLabel#brand { font-size: 21px; font-weight: 700; color: #f3f7fc; }
    QLabel#muted { color: #92a0b2; font-size: 11px; }
    QLabel#status { background: #192230; border: 1px solid #293547; border-radius: 8px; padding: 12px; color: #b7c7d9; }
    QPushButton { background: #243043; border: 1px solid #344259; padding: 9px 14px; border-radius: 7px; font-weight: 600; }
    QPushButton:hover { background: #303e53; border-color: #58708c; }
    QPushButton:checked { background: #224c49; color: #84f1cf; border-color: #3c917b; }
    QPushButton:disabled { background: #1a2330; color: #66748a; border-color: #253043; }
    QPushButton#primary { background: #59ddbc; color: #0e2621; border: none; padding: 11px 24px; }
    QPushButton#primary:hover { background: #7beacd; }
    QPushButton#primary:disabled { background: #263b39; color: #648981; }
    QPushButton#quiet { border: none; background: transparent; color: #8291a5; }
    QPushButton#aboutSupport { background: #253c52; border: 1px solid #5e829f; color: #eef6ff; padding: 11px 14px; }
    QPushButton#aboutSupport:hover { background: #34546f; border-color: #8db7da; }
    QGroupBox { background: #19212e; border: 1px solid #2c384a; border-radius: 10px; margin-top: 10px; font-weight: 600; }
    QGroupBox::title { subcontrol-origin: margin; left: 14px; padding: 0 4px; color: #9eb2ca; font-size: 10px; }
    QGroupBox QWidget { background: transparent; }
    QComboBox, QSpinBox, QDoubleSpinBox { background: #111a27; border: 1px solid #344259; border-radius: 6px; padding: 7px; min-height: 16px; }
    QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover { border-color: #5b7594; }
    QComboBox QAbstractItemView { background: #192536; selection-background-color: #315068; padding: 4px; }
    QComboBox::drop-down { border: none; width: 20px; }
    QCheckBox { spacing: 9px; min-height: 23px; }
    QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #53657b; border-radius: 4px; background: #131c28; }
    QCheckBox::indicator:checked { background: #59ddbc; border-color: #59ddbc; }
    QCheckBox:disabled { color: #607188; }
    QSlider::groove:horizontal { height: 5px; background: #344156; border-radius: 2px; }
    QSlider::sub-page:horizontal { background: #59ddbc; border-radius: 2px; }
    QSlider::handle:horizontal { background: #b7ffe8; width: 14px; margin: -5px 0; border-radius: 7px; }
    QSlider::sub-page:horizontal:disabled { background: #3d4d62; }
    QSlider::handle:horizontal:disabled { background: #6b7d93; }
    QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled { color: #73849a; border-color: #293548; }
    QToolButton { border: 1px solid #344259; border-radius: 7px; padding: 10px; text-align: left; background: #19212e; }
    QToolButton:checked { color: #7ce8c8; }
    QTabWidget::pane { border: 1px solid #344259; border-radius: 6px; }
    QTabBar::tab { background: #19212e; padding: 9px 8px; color: #9aaac0; }
    QTabBar::tab:selected { background: #293a4d; color: #a5f5dc; }
    QScrollArea { border: none; background: transparent; }
    QScrollBar:vertical { width: 7px; background: #10151d; margin: 0; }
    QScrollBar::handle:vertical { background: #39495f; border-radius: 3px; min-height: 28px; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
    QGraphicsView { border: 1px solid #2c384a; background: #121b27; }
    QToolTip { background: #29394d; color: #eef5ff; border: 1px solid #536b86; padding: 6px; }
"""

ABOUT_DIALOG = """
    QDialog { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    QLabel { font-size: 13px; }
"""

IMAGE_VIEWER = """
    background-color: #121212; 
    border: 2px dashed #444; 
    border-radius: 10px;
"""

# --- 2. Specific Button Styles ---
BTN_GITHUB = """
    QPushButton { background-color: #555555; color: white; padding: 8px; border-radius: 4px; font-weight: bold; }
    QPushButton:hover { background-color: #666666; }
"""

BTN_PAYPAL = """
    QPushButton { background-color: #ffc439; color: black; padding: 8px; border-radius: 4px; font-weight: bold; }
    QPushButton:hover { background-color: #ffaa00; }
"""

BTN_CUSTOM_SHAPE = "background-color: #8e44ad;"
BTN_EXPORT = "background-color: #00ca8b; color: black; font-size: 15px;"
BTN_ABOUT = "background-color: #333; color: #ccc; margin-top: 5px;"

# --- 3. Label & Input Styles ---
LBL_STATUS_DEFAULT = "color: #aaa; font-size: 11px;"
LBL_STATUS_SUCCESS = "color: #00ca8b; font-size: 11px;"
LBL_STATUS_WARNING = "color: #ffaa00; font-size: 11px;"
COMBO_BOX = "background-color: #1e1e1e; padding: 5px;"

# --- 4. HTML Templates ---
ABOUT_HTML_CONTENT = (
    "<h2 style='color: #00ca8b; margin-bottom: 5px; text-align: center;'>Espadan DTF Studio Pro Edition</h2>"
    "<p style='text-align: center; color: #ccc;'>"
    "A professional halftone generator tailored for DTF printing.<br>"
    "Developed by <b>Iman Shirani (Espadan LLC)</b>.<br><br>"
    "Support this project or follow the development:"
    "</p>"
)
