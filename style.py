# ==========================================
# Espadan DTF Studio - Theme & Style Library
# ==========================================

# --- 1. Global Window Styles ---
MAIN_WINDOW = """
    QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    QPushButton { background-color: #007acc; border: none; padding: 10px; border-radius: 6px; font-weight: bold;}
    QPushButton:hover { background-color: #0098ff; }
    QPushButton:disabled { background-color: #555; color: #888; }
    QGroupBox { border: 1px solid #555; border-radius: 6px; margin-top: 15px; padding-top: 15px; font-weight: bold; }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #00ca8b; }
    QSlider::groove:horizontal { border: 1px solid #999; height: 6px; background: #1e1e1e; border-radius: 3px; }
    QSlider::handle:horizontal { background: #00ca8b; width: 16px; margin: -5px 0; border-radius: 8px; }
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
    "<h2 style='color: #00ca8b; margin-bottom: 5px; text-align: center;'>Espadan DTF Studio Pro</h2>"
    "<p style='text-align: center; color: #ccc;'>"
    "A professional halftone generator tailored for DTF printing.<br>"
    "Developed by <b>Iman Shirani (Espadan LLC)</b>.<br><br>"
    "Support this project or follow the development:"
    "</p>"
)