# 🖨️ Espadan DTF Studio - Pro Edition
Developed by: Iman Shirani

[![Donate ❤️](https://img.shields.io/badge/Donate-PayPal-blue.svg)](https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

A professional, standalone Halftone Generator meticulously designed for **Direct-to-Film (DTF)** and Screen Printing pipelines. Built with a modular architecture in Python, this tool bridges the gap between raw designs and RIP software by providing advanced rasterization, soft black knockouts, and custom halftone shapes without the need for expensive commercial plugins.

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
