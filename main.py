import sys
from pathlib import Path
import numpy as np
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QCheckBox, QComboBox
from PyQt6.QtCore import QThread, QTimer, pyqtSignal
from halftone_ui import HalftoneUI
from halftone_core import HalftoneProcessor
import presets


class RenderWorker(QThread):
    completed = pyqtSignal(int, object, str)

    def __init__(self, revision, image, settings):
        super().__init__()
        self.revision, self.image, self.settings = revision, image, settings

    def run(self):
        try:
            result = HalftoneProcessor.process_image(self.image, cancelled=self.isInterruptionRequested, **self.settings)
            self.completed.emit(self.revision, result, '')
        except Exception as error:
            self.completed.emit(self.revision, None, str(error))


class HalftoneApp:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.ui = HalftoneUI()
        self.current_image_path = None
        self.source_image = None
        self.custom_mask_path = None
        self.processed_image = None
        self.worker = None
        self.revision = 0
        self.pending = False
        self.closing = False
        self.applying_preset = False
        self.timer = QTimer(self.ui)
        self.timer.setSingleShot(True)
        self.timer.setInterval(180)
        self.timer.timeout.connect(self.start_render)
        self.ui.shutdown = self.shutdown
        self.connect_signals()
        self.ui.show()

    def connect_signals(self):
        self.ui.btn_load.clicked.connect(self.load_image)
        self.ui.btn_load_mask.clicked.connect(self.load_mask)
        self.ui.btn_save.clicked.connect(self.save_image)
        for key, widget in self.ui.config_widgets.items():
            if key == 'background':
                continue
            if isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.on_settings_changed)
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self.on_settings_changed)
            else:
                widget.valueChanged.connect(self.on_settings_changed)
        self.ui.combo_garment.currentIndexChanged.connect(self.on_garment_changed)
        self.ui.combo_preset.currentIndexChanged.connect(self.select_preset)
        self.ui.btn_save_preset.clicked.connect(self.save_preset)
        self.ui.btn_load_preset.clicked.connect(self.load_preset)
        self.update_controls()

    def on_garment_changed(self, *_):
        for view in (self.ui.image_view, self.ui.original_view):
            view.set_preview_background(self.ui.combo_garment.currentData())

    def config(self):
        values = {}
        for key, widget in self.ui.config_widgets.items():
            if isinstance(widget, QCheckBox):
                values[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                values[key] = widget.currentText() if key == 'shape_name' else widget.currentData()
            else:
                values[key] = widget.value()
        values['custom_mask_path'] = self.custom_mask_path
        return values

    def apply_config(self, config):
        values = presets.validate(config)
        # Validate external resources before changing any controls.
        mask = values['custom_mask_path']
        if mask:
            HalftoneProcessor.load_image(mask)
        self.applying_preset = True
        try:
            for key, widget in self.ui.config_widgets.items():
                widget.blockSignals(True)
                try:
                    if isinstance(widget, QCheckBox):
                        widget.setChecked(values[key])
                    elif isinstance(widget, QComboBox):
                        index = widget.findText(values[key]) if key == 'shape_name' else widget.findData(values[key])
                        widget.setCurrentIndex(index)
                    else:
                        widget.setValue(values[key])
                finally:
                    widget.blockSignals(False)
            self.custom_mask_path = mask
            self.ui.lbl_mask_status.setText('Custom mask loaded.' if mask else 'No custom mask loaded.')
            self.on_garment_changed()
            self.on_settings_changed()
        finally:
            self.applying_preset = False

    def select_preset(self, *_):
        name = self.ui.combo_preset.currentData()
        if name is not None:
            self.apply_config(dict(presets.DEFAULTS, **presets.BUILTINS[name]))

    def save_preset(self):
        path, _ = QFileDialog.getSaveFileName(self.ui, 'Save settings preset', 'My_DTF_Preset.json', 'Preset (*.json)')
        if not path:
            return
        if not path.lower().endswith('.json'):
            path += '.json'
        try:
            presets.save(path, self.config())
        except Exception as error:
            QMessageBox.warning(self.ui, 'Cannot save preset', str(error))

    def load_preset(self):
        path, _ = QFileDialog.getOpenFileName(self.ui, 'Load settings preset', '', 'Preset (*.json)')
        if not path:
            return
        try:
            config = presets.load(path)
            mask = config.get('custom_mask_path')
            if mask and not Path(mask).is_absolute():
                config['custom_mask_path'] = str(Path(path).parent / mask)
            self.apply_config(config)
            self.ui.combo_preset.blockSignals(True)
            self.ui.combo_preset.setCurrentIndex(0)
            self.ui.combo_preset.blockSignals(False)
        except Exception as error:
            QMessageBox.warning(self.ui, 'Cannot load preset', str(error))

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self.ui, 'Open Design', '',
                                             'Images (*.png *.jpg *.jpeg *.tif *.tiff)')
        if not path:
            return
        try:
            image = HalftoneProcessor.load_image(path)
        except Exception as error:
            QMessageBox.warning(self.ui, 'Cannot open design', str(error))
            return
        self.current_image_path, self.source_image = path, image
        self.ui.image_view.is_first_load = True
        self.ui.original_view.is_first_load = True
        self.ui.lbl_file.setText(Path(path).name)
        self.ui.lbl_file.setToolTip(path)
        if not self.ui.chk_print_size.isChecked() and not self.ui.chk_lpi.isChecked():
            dpi = image.info.get('dpi', (300, 300))[0]
            if not np.isfinite(dpi) or not 72 <= dpi <= 1200:
                dpi = 300
            for widget, value in [(self.ui.spin_dpi, round(dpi)),
                                  (self.ui.spin_width, image.width / dpi * 2.54)]:
                widget.blockSignals(True)
                widget.setValue(value)
                widget.blockSignals(False)
        self.ui.update_image_display(image, image)
        self.processed_image = None
        self.on_settings_changed()

    def load_mask(self):
        path, _ = QFileDialog.getOpenFileName(self.ui, 'Open Custom Shape', '',
                                             'Images (*.png *.jpg *.jpeg)')
        if not path:
            return
        try:
            HalftoneProcessor.load_image(path)
        except Exception as error:
            QMessageBox.warning(self.ui, 'Cannot open mask', str(error))
            return
        self.custom_mask_path = path
        self.ui.lbl_mask_status.setText('Custom mask loaded. Black = print; white = gap.')
        self.ui.lbl_mask_status.setStyleSheet('color: #00ca8b; font-size: 11px;')
        self.ui.combo_shape.blockSignals(True)
        self.ui.combo_shape.setCurrentText('custom')
        self.ui.combo_shape.blockSignals(False)
        self.on_settings_changed()

    def on_settings_changed(self, *_):
        if not self.applying_preset:
            self.ui.combo_preset.blockSignals(True)
            self.ui.combo_preset.setCurrentIndex(0)
            self.ui.combo_preset.blockSignals(False)
        self.update_controls()
        self.revision += 1
        if self.worker is not None:
            self.worker.requestInterruption()
        self.ui.btn_save.setEnabled(False)
        self.timer.stop()
        self.pending = False
        if self.ui.combo_shape.currentText() == 'custom' and not self.custom_mask_path:
            self.ui.lbl_mask_status.setText('Please load a custom mask first.')
            self.ui.lbl_render_status.setText('Custom shape needs a mask. Export is paused.')
            return
        if self.ui.chk_lpi.isChecked() and self.ui.spin_lpi.value() > self.ui.spin_dpi.value() / 3:
            self.ui.lbl_render_status.setText('Lower LPI or increase DPI: each pattern cell needs at least 3 pixels.')
            return
        if self.source_image is None:
            return
        self.pending = True
        self.ui.lbl_render_status.setText('Rendering full-resolution print…')
        self.timer.start()

    def update_controls(self):
        target = self.ui.combo_reduction_target.currentData()
        self.ui.slider_tolerance.setEnabled(self.ui.chk_knockout.isChecked() or target in ('black', 'both'))
        self.ui.slider_white_tolerance.setEnabled(self.ui.chk_knockout_white.isChecked() or target in ('white', 'both'))
        self.ui.slider_size.setEnabled(not self.ui.chk_lpi.isChecked())
        cell = (self.ui.spin_dpi.value() / self.ui.spin_lpi.value()
                if self.ui.chk_lpi.isChecked() else self.ui.slider_size.value())
        self.ui.lbl_size_val.setText(f'Pattern size: {cell:.1f} px')
        self.ui.lbl_angle_val.setText(f'Angle: {self.ui.slider_angle.value()}°')
        tones = self.ui.chk_tones.isChecked()
        self.ui.slider_reduction.setEnabled(not tones)
        self.ui.slider_reduction.setVisible(not tones)
        self.ui.lbl_reduction.setText('Tone coverage is active · Advanced' if tones else
                                     f'Ink reduction: {self.ui.slider_reduction.value()}%')
        for slider in (self.ui.slider_shadows, self.ui.slider_midtones, self.ui.slider_lights):
            slider.setEnabled(tones)
        for key, text in [('shadow_reduction', 'Shadows'), ('midtone_reduction', 'Midtones'),
                          ('light_reduction', 'Highlights'), ('glow_strength', 'Glow protection'),
                          ('highlight_strength', 'Highlight protection'), ('detail_strength', 'Detail protection'),
                          ('black_tolerance', 'Black tolerance'), ('white_tolerance', 'White tolerance')]:
            self.ui.slider_titles[key].setText(f'{text}: {self.ui.config_widgets[key].value()}%')
        self.ui.slider_glow.setEnabled(self.ui.chk_glow.isChecked())
        self.ui.slider_highlights.setEnabled(self.ui.chk_highlights.isChecked())
        self.ui.slider_details.setEnabled(self.ui.chk_details.isChecked())
        self.ui.spin_detail_width.setEnabled(self.ui.chk_details.isChecked())
        self.ui.spin_width.setEnabled(self.ui.chk_print_size.isChecked())
        self.ui.spin_dpi.setEnabled(self.ui.chk_print_size.isChecked() or self.ui.chk_lpi.isChecked())
        self.ui.spin_lpi.setEnabled(self.ui.chk_lpi.isChecked())
        if self.source_image is not None:
            if self.ui.chk_print_size.isChecked():
                width = self.ui.spin_width.value()
                height = width * self.source_image.height / self.source_image.width
                pixels = round(width / 2.54 * self.ui.spin_dpi.value())
                self.ui.lbl_print_size.setText(f'{width:.2f} × {height:.2f} cm · {pixels} px wide\nAspect ratio locked.')
            else:
                self.ui.lbl_print_size.setText(f'Original pixels: {self.source_image.width} × {self.source_image.height}. Aspect ratio locked.')

    def settings(self):
        config = self.config()
        dpi = config['output_dpi'] if config['print_size_enabled'] or config['lpi_enabled'] else (
            self.source_image.info.get('dpi', (300, 300))[0] if self.source_image else 300)
        return dict(pattern_size=self.ui.slider_size.value(), angle=self.ui.slider_angle.value(),
                    shape_name=self.ui.combo_shape.currentText(),
                    alpha_halftone=self.ui.chk_alpha_halftone.isChecked(),
                    knockout_black=self.ui.chk_knockout.isChecked(),
                    black_tolerance=self.ui.slider_tolerance.value(),
                    knockout_white=self.ui.chk_knockout_white.isChecked(),
                    white_tolerance=self.ui.slider_white_tolerance.value(),
                    custom_mask_path=self.custom_mask_path,
                    antialias=self.ui.chk_antialias.isChecked(),
                    ink_reduction=self.ui.slider_reduction.value(),
                    reduction_target=self.ui.combo_reduction_target.currentData(),
                    preserve_glow=config['preserve_glow'], protect_highlights=config['protect_highlights'],
                    protect_details=config['protect_details'], glow_strength=config['glow_strength'],
                    highlight_strength=config['highlight_strength'], detail_strength=config['detail_strength'],
                    detail_radius=max(1, min(15, round(config['detail_width_mm'] / 25.4 * dpi / 2))),
                    tone_reduction=(config['shadow_reduction'], config['midtone_reduction'], config['light_reduction'])
                    if config['tone_enabled'] else None,
                    output_dpi=config['output_dpi'] if config['print_size_enabled'] or config['lpi_enabled'] else None,
                    print_width_cm=config['print_width_cm'] if config['print_size_enabled'] else None,
                    lpi=config['lpi'] if config['lpi_enabled'] else None)

    def start_render(self):
        if self.closing or not self.pending or self.worker is not None:
            return
        self.pending = False
        self.worker = RenderWorker(self.revision, self.source_image, self.settings())
        self.worker.completed.connect(self.render_completed)
        self.worker.finished.connect(self.worker_finished)
        self.worker.start()

    def render_completed(self, revision, result, error):
        if self.closing or revision != self.revision:
            return
        if error:
            self.processed_image = None
            self.ui.lbl_render_status.setText('Render failed. Adjust settings or reload the file.')
            QMessageBox.warning(self.ui, 'Render failed', error)
            return
        self.processed_image = result
        self.ui.update_image_display(result, self.source_image)
        original_alpha = np.asarray(self.source_image.getchannel('A'), dtype=np.float32).mean()
        result_alpha = np.asarray(result.getchannel('A'), dtype=np.float32).mean()
        change = (1 - result_alpha / original_alpha) * 100 if original_alpha else 0
        dpi = result.info.get('dpi')
        dpi_text = f'{dpi[0]:.0f} DPI' if dpi else 'DPI unspecified'
        active = [name for enabled, name in [(self.ui.chk_glow.isChecked(), 'Glow'),
                  (self.ui.chk_highlights.isChecked(), 'Highlights'), (self.ui.chk_details.isChecked(), 'Fine details')]
                  if enabled]
        protections = f" · Protected: {', '.join(active)}" if active else ''
        self.ui.lbl_render_status.setText(
            f'{result.width} × {result.height} px · {dpi_text} · Coverage reduction: {change:.1f}% (estimate){protections}')
        self.ui.btn_save.setEnabled(True)

    def worker_finished(self):
        self.worker.deleteLater()
        self.worker = None
        if self.pending and not self.closing and not self.timer.isActive():
            self.start_render()

    def save_image(self):
        if self.processed_image is None or not self.ui.btn_save.isEnabled():
            return
        path, _ = QFileDialog.getSaveFileName(self.ui, 'Export for RIP', 'DTF_Ready.png', 'PNG Files (*.png)')
        if not path:
            return
        if not path.lower().endswith('.png'):
            path += '.png'
        try:
            HalftoneProcessor.save_image(self.processed_image, path)
        except Exception as error:
            QMessageBox.warning(self.ui, 'Cannot export PNG', str(error))

    def shutdown(self):
        self.closing = True
        self.timer.stop()
        if self.worker is not None:
            self.worker.requestInterruption()
            self.worker.wait()


if __name__ == '__main__':
    app = HalftoneApp()
    sys.exit(app.app.exec())
