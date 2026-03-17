# 🖨️ Espadan DTF Studio - Pro Edition
Developed by: Iman Shirani

[![Donate ❤️](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

A professional, standalone Halftone Generator meticulously designed for **Direct-to-Film (DTF)** and Screen Printing pipelines. Built with a modular architecture in Python, this tool bridges the gap between raw designs and RIP software by providing advanced rasterization, soft black knockouts, and custom halftone shapes without the need for expensive commercial plugins.

![screenshot](/Screenshot/ESPADAN-DTF-STUDIO.png)
![screenshot](/Screenshot/ESPADAN-DTF-STUDIO%20(3).png)

🎥 **[Watch the Full Tutorial on YouTube](https://www.youtube.com/watch?v=J3S0TXRmVB8)**

---

## ✨ Key Features

* **👻 Alpha Channel Halftoning:** Intelligently halftones only the semi-transparent areas (drop shadows, glows, smoke) while preserving solid colors. Prevents harsh edges and white ink borders in DTF printing.
* **🖤 Soft Black Knockout (Blend-If):** Automatically removes true black backgrounds and smoothly fades dark areas into the shirt's fabric, drastically improving breathability and reducing ink costs.
* **📐 Comprehensive Pattern Library:** Choose from classic mathematical shapes including `Dot`, `Line` (Vintage/Retro effect), `Square`, `Cross`, and `Diamond`.
* **💖 Custom Shape Masks:** Load any custom grayscale image (e.g., a faded heart) to use as the halftone dot matrix.
* **🛡️ Ghost-Line Prevention (Dot Gain Control):** Built-in algorithms compress the halftone screen to prevent microscopic dots from rendering in pure black/transparent areas, ensuring a flawless print.
* **🔎 Interactive Workspace:** A professional PyQt6 UI featuring real-time rendering, smooth mouse-wheel zooming, and canvas panning.

---

## 📂 Project Architecture

The application follows a strict and clean separation of concerns:

```text
espadan-dtf-studio/
│
├── main.py                 # Application entry point and signal connector
├── halftone_core.py        # Core image processing and NumPy mathematics
├── halftone_ui.py          # PyQt6 User Interface and Interactive Zoom View
├── halftone_library.py     # Mathematical definitions for pattern shapes
└── style.py                # Centralized CSS stylesheets and color themes

```
## 🚀 Download & Run (Standalone .exe)

The easiest way to use **Espadan DTF Studio** is to download the pre-compiled Windows executable. You do not need to install Python or any coding dependencies!

1. Go to the [Releases](https://github.com/imanshirani/Espadan-DTF-Studio/releases) page.
2. Download `ESPADAN-DTF-STUDIO.exe`.
3. Double-click the file to launch the studio and start halftoning.

---

### 🛡️ A Note on Antivirus & Windows Defender

Because this application is a newly compiled standalone tool (built with PyInstaller) and is not digitally signed with an expensive commercial certificate, **Windows SmartScreen** or your **Antivirus software** might flag it as an "unrecognized app" or show a false positive warning.

**This is completely normal for indie, open-source software.**

* **To run the app:** On the blue Windows SmartScreen popup, click **"More info"** and then **"Run anyway"**.
* **Security First:** Transparency is a priority. If you have any security concerns, you are highly encouraged to:
    1. Scan the `.exe` file on [VirusTotal](https://www.virustotal.com/) before running it.
    2. Or, inspect the completely open-source Python code in this repository and build the executable yourself using the developer instructions below.


🕹️ How to Use
Load Main Image: Import your high-resolution PNG or JPG design.

Tweak DTF Settings: Enable Halftone Alpha Channel for soft edges, or use Knockout Black with the tolerance slider for dark apparel.

Adjust the Grid: Select your desired shape, Pattern Size (LPI equivalent), and Angle. Use the mouse wheel on the preview window to zoom in and check for clean edges.

Export: Click Export PNG to generate a RIP-ready file with preserved transparencies.

👨‍💻 Developed By
Iman Shirani | Espadan LLC Designed for creators, print shops, and the DTF community.
