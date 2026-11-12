from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QSlider, QGroupBox, QCheckBox, QComboBox,
                             QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                             QDialog, QScrollArea, QToolButton, QTabWidget,
                             QDoubleSpinBox, QSpinBox, QFrame, QStyle, QStyleOptionButton, QSizePolicy)
from PyQt6.QtCore import Qt, QUrl, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QDesktopServices, QColor, QBrush, QPen
from PIL.ImageQt import ImageQt
from PIL import Image
from presets import DEFAULTS, BUILTINS
import style

VERSION = '0.006'


class StudioCheckBox(QCheckBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isChecked():
            option = QStyleOptionButton()
            self.initStyleOption(option)
            rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, option, self)
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor('#12372d'), 2, Qt.PenStyle.SolidLine,
                                Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(rect.left() + 4, rect.top() + 8, rect.left() + 7, rect.top() + 11)
            painter.drawLine(rect.left() + 7, rect.top() + 11, rect.left() + 13, rect.top() + 5)
            painter.end()


class StudioComboBox(QComboBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor('#a7bed7'), 1.5, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        x, y = self.width() - 15, self.height() // 2
        painter.drawLine(x - 4, y - 2, x, y + 2)
        painter.drawLine(x, y + 2, x + 4, y - 2)
        painter.end()


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f'About Espadan DTF Studio - Pro Edition - {VERSION}')
        self.setFixedSize(460, 250)
        self.setStyleSheet(style.MAIN_WINDOW)
        layout = QVBoxLayout(self)
        label = QLabel(style.ABOUT_HTML_CONTENT)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        row = QHBoxLayout()
        self.btn_github = QPushButton('GitHub')
        self.btn_github.setStyleSheet(style.BTN_GITHUB)
        self.btn_github.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://github.com/imanshirani/Espadan-DTF-Studio')))
        self.btn_paypal = QPushButton('Donate (PayPal)')
        self.btn_paypal.setStyleSheet(style.BTN_PAYPAL)
        self.btn_paypal.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl('https://www.paypal.com/donate/?hosted_button_id=LAMNRY6DDWDC4')))
        row.addWidget(self.btn_github)
        row.addWidget(self.btn_paypal)
        layout.addLayout(row)


class ZoomableView(QGraphicsView):
    view_changed = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.pixmap_item = QGraphicsPixmapItem()
        self.scene.addItem(self.pixmap_item)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setMinimumSize(230, 350)
        self.is_first_load = True
        self.preview_background = 'transparent'
        self.horizontalScrollBar().valueChanged.connect(self.notify_view)
        self.verticalScrollBar().valueChanged.connect(self.notify_view)

    def notify_view(self, *_):
        self.view_changed.emit(self)

    def set_preview_background(self, background):
        self.preview_background = background
        if background == 'transparent':
            tile = QPixmap(24, 24)
            tile.fill(QColor('#e2e5e9'))
            painter = QPainter(tile)
            painter.fillRect(0, 0, 12, 12, QColor('#b9bec6'))
            painter.fillRect(12, 12, 12, 12, QColor('#b9bec6'))
            painter.end()
            self.setBackgroundBrush(QBrush(tile))
        else:
            self.setBackgroundBrush(QBrush(QColor(background)))
        self.viewport().update()

    def drawBackground(self, painter, rect):
        if self.preview_background == 'transparent':
            # Checker size stays readable at every image zoom level.
            painter.save()
            painter.resetTransform()
            painter.fillRect(self.viewport().rect(), self.backgroundBrush())
            painter.restore()
        else:
            super().drawBackground(painter, rect)

    def set_image(self, pixmap):
        self.pixmap_item.setPixmap(pixmap)
        self.scene.setSceneRect(self.pixmap_item.boundingRect())
        if self.is_first_load:
            self.fit_image()
            self.is_first_load = False

    def fit_image(self):
        if not self.pixmap_item.pixmap().isNull():
            self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            self.notify_view()

    def actual_size(self):
        center = self.mapToScene(self.viewport().rect().center())
        self.resetTransform()
        self.centerOn(center)
        self.notify_view()

    def wheelEvent(self, event):
        if not event.angleDelta().y():
            return
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        scale = self.transform().m11() * factor
        if .02 <= scale <= 64:
            self.scale(factor, factor)
            self.notify_view()


class HalftoneUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'Espadan DTF Studio - Pro Edition - {VERSION}')
        self.resize(1280, 900)
        self.setMinimumSize(950, 650)
        self.setStyleSheet(style.MAIN_WINDOW)
        self.config_widgets = {}
        self.slider_titles = {}
        self._syncing = False
        self.init_ui()

    def register(self, key, widget):
        self.config_widgets[key] = widget
        return widget

    def note(self, text):
        label = QLabel(text)
        label.setObjectName('muted')
        label.setWordWrap(True)
        return label

    def group(self, title, parent_layout):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 25, 16, 14)
        layout.setSpacing(9)
        parent_layout.addWidget(group)
        return layout

    def slider(self, key, label, layout):
        title = QLabel(label)
        slider = self.register(key, QSlider(Qt.Orientation.Horizontal))
        self.slider_titles[key] = title
        slider.setRange(0, 100)
        slider.setValue(DEFAULTS[key])
        layout.addWidget(title)
        layout.addWidget(slider)
        slider.valueChanged.connect(lambda value: title.setText(f'{label}: {value}%'))
        title.setText(f'{label}: {slider.value()}%')
        return slider, title

    def check(self, key, text, layout, tooltip=''):
        widget = self.register(key, StudioCheckBox(text))
        widget.setChecked(DEFAULTS[key])
        widget.setToolTip(tooltip)
        layout.addWidget(widget)
        return widget

    def spin(self, key, label, low, high, layout, suffix='', decimals=1):
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        if isinstance(DEFAULTS[key], int):
            widget = QSpinBox()
        else:
            widget = QDoubleSpinBox()
            widget.setDecimals(decimals)
        self.register(key, widget)
        widget.setRange(low, high)
        widget.setValue(DEFAULTS[key])
        widget.setSuffix(suffix)
        widget.setMinimumWidth(100)
        row.addWidget(widget)
        layout.addLayout(row)
        return widget

    def init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(16)
        header = QHBoxLayout()
        brand = QVBoxLayout()
        title = QLabel('ESPADAN  /  DTF STUDIO')
        title.setObjectName('brand')
        brand.addWidget(title)
        brand.addWidget(self.note('Less coverage. More detail.'))
        header.addLayout(brand)
        header.addStretch()
        self.btn_load = QPushButton('Open design')
        self.btn_save = QPushButton('Export PNG')
        self.btn_save.setObjectName('primary')
        self.btn_save.setEnabled(False)
        header.addWidget(self.btn_load)
        header.addWidget(self.btn_save)
        root.addLayout(header)
        body = QHBoxLayout()
        body.setSpacing(18)
        root.addLayout(body, 1)
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 5, 0)
        sidebar_layout.setSpacing(12)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(sidebar)
        sidebar_column = QWidget()
        sidebar_column.setFixedWidth(355)
        sidebar_column_layout = QVBoxLayout(sidebar_column)
        sidebar_column_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_column_layout.setSpacing(12)
        sidebar_column_layout.addWidget(scroll, 1)
        body.addWidget(sidebar_column)

        preset_layout = self.group('01  /  START WITH A PRESET', sidebar_layout)
        self.combo_preset = StudioComboBox()
        self.combo_preset.addItem('Custom settings', None)
        for name in BUILTINS:
            self.combo_preset.addItem(name, name)
        preset_layout.addWidget(self.combo_preset)
        preset_row = QHBoxLayout()
        self.btn_save_preset = QPushButton('Save preset')
        self.btn_load_preset = QPushButton('Load preset')
        preset_row.addWidget(self.btn_save_preset)
        preset_row.addWidget(self.btn_load_preset)
        preset_layout.addLayout(preset_row)

        coverage = self.group('02  /  PRINT COVERAGE', sidebar_layout)
        self.slider_reduction, self.lbl_reduction = self.slider('ink_reduction', 'Ink reduction', coverage)
        self.combo_reduction_target = self.register('reduction_target', StudioComboBox())
        for name, value in [('Whole design', 'all'), ('Black areas', 'black'),
                            ('White areas', 'white'), ('Black + white areas', 'both')]:
            self.combo_reduction_target.addItem(name, value)
        coverage.addWidget(self.combo_reduction_target)
        self.chk_knockout = self.check('knockout_black', 'Remove black · black fabric', coverage)
        self.chk_knockout_white = self.check('knockout_white', 'Remove white · white fabric', coverage)

        protection = self.group('03  /  KEEP THE DETAILS', sidebar_layout)
        self.chk_glow = self.check('preserve_glow', 'Preserve glow / soft edges', protection,
                                  'Protect colored dark halos and existing soft alpha transitions. Automatic estimate.')
        self.chk_highlights = self.check('protect_highlights', 'Protect bright highlights', protection,
                                        'Reduce fewer holes in bright reflections; explicit white removal still applies.')
        self.chk_details = self.check('protect_details', 'Protect fine text / lines', protection,
                                     'Use local contrast and stroke width to protect fine details. Not text recognition.')

        self.btn_advanced = QToolButton()
        self.btn_advanced.setText('Advanced settings')
        self.btn_advanced.setCheckable(True)
        self.btn_advanced.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btn_advanced.setArrowType(Qt.ArrowType.RightArrow)
        self.btn_advanced.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sidebar_layout.addWidget(self.btn_advanced)
        self.advanced_panel = QTabWidget()
        sidebar_layout.addWidget(self.advanced_panel)
        self.advanced_panel.hide()
        self.btn_advanced.toggled.connect(self.toggle_advanced)
        self.init_advanced()
        sidebar_layout.addStretch()
        self.btn_about = QPushButton(f'About / Support · {VERSION}')
        self.btn_about.setObjectName('aboutSupport')
        self.btn_about.clicked.connect(self.show_about_dialog)
        sidebar_column_layout.addWidget(self.btn_about)

        preview = QVBoxLayout()
        body.addLayout(preview, 1)
        toolbar = QHBoxLayout()
        self.lbl_file = QLabel('No design loaded')
        self.lbl_file.setObjectName('muted')
        self.lbl_file.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lbl_file.setMaximumWidth(300)
        toolbar.addWidget(self.lbl_file, 1)
        self.combo_garment = self.register('background', StudioComboBox())
        for name, value in [('Black', '#000000'), ('White', '#ffffff'), ('Transparent', 'transparent')]:
            self.combo_garment.addItem(name, value)
        self.combo_garment.setCurrentIndex(2)
        self.combo_garment.setToolTip('Preview background only. Export stays transparent.')
        toolbar.addWidget(self.combo_garment)
        self.btn_compare = QPushButton('Before / After')
        self.btn_compare.setCheckable(True)
        toolbar.addWidget(self.btn_compare)
        self.btn_fit = QPushButton('Fit')
        self.btn_actual = QPushButton('100%')
        toolbar.addWidget(self.btn_fit)
        toolbar.addWidget(self.btn_actual)
        preview.addLayout(toolbar)
        views = QHBoxLayout()
        views.setSpacing(12)
        self.original_panel = QWidget()
        original_layout = QVBoxLayout(self.original_panel)
        original_layout.setContentsMargins(0, 0, 0, 0)
        original_layout.addWidget(self.note('ORIGINAL'))
        self.original_view = ZoomableView()
        original_layout.addWidget(self.original_view, 1)
        self.original_panel.hide()
        views.addWidget(self.original_panel, 1)
        result_panel = QWidget()
        result_layout = QVBoxLayout(result_panel)
        result_layout.setContentsMargins(0, 0, 0, 0)
        result_layout.addWidget(self.note('PRINT PREVIEW'))
        self.image_view = ZoomableView()
        result_layout.addWidget(self.image_view, 1)
        views.addWidget(result_panel, 1)
        preview.addLayout(views, 1)
        self.lbl_render_status = QLabel('Open a design, choose a preset, then export your PNG.')
        self.lbl_render_status.setObjectName('status')
        self.lbl_render_status.setWordWrap(True)
        preview.addWidget(self.lbl_render_status)
        self.btn_compare.toggled.connect(self.toggle_compare)
        self.btn_fit.clicked.connect(self.fit_views)
        self.btn_actual.clicked.connect(self.actual_views)
        for view in (self.image_view, self.original_view):
            view.set_preview_background('transparent')
            view.view_changed.connect(self.sync_views)

    def init_advanced(self):
        pattern = QWidget()
        layout = QVBoxLayout(pattern)
        layout.setSpacing(10)
        self.combo_shape = self.register('shape_name', StudioComboBox())
        self.combo_shape.addItems(['dot', 'line', 'square', 'cross', 'diamond', 'custom'])
        layout.addWidget(QLabel('Pattern shape'))
        layout.addWidget(self.combo_shape)
        self.lbl_size_val = QLabel('Pattern size: 30 px')
        self.slider_size = self.register('pattern_size', QSlider(Qt.Orientation.Horizontal))
        self.slider_size.setRange(5, 100)
        self.slider_size.setValue(30)
        layout.addWidget(self.lbl_size_val)
        layout.addWidget(self.slider_size)
        self.lbl_angle_val = QLabel('Angle: 22°')
        self.slider_angle = self.register('angle', QSlider(Qt.Orientation.Horizontal))
        self.slider_angle.setRange(0, 90)
        self.slider_angle.setValue(22)
        layout.addWidget(self.lbl_angle_val)
        layout.addWidget(self.slider_angle)
        self.chk_alpha_halftone = self.check('alpha_halftone', 'Keep design colors', layout)
        self.chk_antialias = self.check('antialias', 'Smooth edges (anti-aliasing)', layout)
        self.slider_tolerance, _ = self.slider('black_tolerance', 'Black tolerance', layout)
        self.slider_white_tolerance, _ = self.slider('white_tolerance', 'White tolerance', layout)
        self.btn_load_mask = QPushButton('Load custom mask')
        layout.addWidget(self.btn_load_mask)
        self.lbl_mask_status = self.note('No custom mask loaded.')
        layout.addWidget(self.lbl_mask_status)
        self.advanced_panel.addTab(pattern, 'Pattern')

        printing = QWidget()
        layout = QVBoxLayout(printing)
        self.chk_print_size = self.check('print_size_enabled', 'Set physical print size', layout)
        unit_row = QHBoxLayout()
        unit_row.addWidget(QLabel('Unit'))
        self.combo_print_unit = self.register('print_unit', StudioComboBox())
        self.combo_print_unit.addItem('Centimeters (cm)', 'cm')
        self.combo_print_unit.addItem('Inches (in)', 'in')
        unit_row.addWidget(self.combo_print_unit)
        layout.addLayout(unit_row)
        self.spin_width = self.spin('print_width_cm', 'Width', .1, 200, layout, ' cm', 2)
        self.print_width_cm = DEFAULTS['print_width_cm']
        self.spin_width.valueChanged.connect(self.print_width_changed)
        self.combo_print_unit.currentIndexChanged.connect(
            lambda _: self.set_print_dimensions(self.print_width_cm, self.combo_print_unit.currentData()))
        self.spin_dpi = self.spin('output_dpi', 'Output resolution', 72, 1200, layout, ' DPI')
        self.lbl_print_size = self.note('Aspect ratio stays locked to the original design.')
        layout.addWidget(self.lbl_print_size)
        self.chk_lpi = self.check('lpi_enabled', 'Use print density (LPI)', layout)
        self.spin_lpi = self.spin('lpi', 'Pattern density', 5, 120, layout, ' LPI')
        layout.addWidget(self.note('LPI controls cells per inch. Export uses the selected DPI when print size or LPI is enabled.'))
        layout.addStretch()
        self.advanced_panel.addTab(printing, 'Print size')

        tones = QWidget()
        layout = QVBoxLayout(tones)
        self.chk_tones = self.check('tone_enabled', 'Adjust coverage by brightness', layout,
                                    'These three reductions replace the overall reduction when enabled.')
        layout.addWidget(self.note('Overrides overall reduction; blends smoothly between tonal ranges.'))
        self.slider_shadows, _ = self.slider('shadow_reduction', 'Shadows', layout)
        self.slider_midtones, _ = self.slider('midtone_reduction', 'Midtones', layout)
        self.slider_lights, _ = self.slider('light_reduction', 'Highlights', layout)
        self.slider_glow, _ = self.slider('glow_strength', 'Glow protection', layout)
        self.slider_highlights, _ = self.slider('highlight_strength', 'Highlight protection', layout)
        self.slider_details, _ = self.slider('detail_strength', 'Detail protection', layout)
        self.spin_detail_width = self.spin('detail_width_mm', 'Fine stroke width', .1, 2, layout, ' mm', 2)
        self.advanced_panel.addTab(tones, 'Protection')

    def print_width_changed(self, value):
        factor = 2.54 if self.combo_print_unit.currentData() == 'in' else 1
        self.print_width_cm = min(200, max(.1, value * factor))

    def set_print_dimensions(self, width_cm, unit):
        # Retain canonical centimeters so repeated unit switches cannot round
        # the physical size or change export pixels. Presets also store cm.
        self.print_width_cm = width_cm
        self.combo_print_unit.blockSignals(True)
        self.spin_width.blockSignals(True)
        try:
            self.combo_print_unit.setCurrentIndex(self.combo_print_unit.findData(unit))
            factor = 2.54 if unit == 'in' else 1
            self.spin_width.setDecimals(4 if unit == 'in' else 2)
            self.spin_width.setRange(.1 / factor, 200 / factor)
            self.spin_width.setSingleStep(.1)
            self.spin_width.setSuffix(' ' + unit)
            self.spin_width.setValue(width_cm / factor)
        finally:
            self.spin_width.blockSignals(False)
            self.combo_print_unit.blockSignals(False)

    def toggle_advanced(self, checked):
        self.advanced_panel.setVisible(checked)
        self.btn_advanced.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)

    def toggle_compare(self, checked):
        self.original_panel.setVisible(checked)
        self.layout().activate()
        self.fit_views()

    def fit_views(self):
        self._syncing = True
        self.image_view.fit_image()
        if self.original_panel.isVisible():
            self.original_view.fit_image()
        self._syncing = False

    def actual_views(self):
        self.image_view.actual_size()
        self.original_view.actual_size()

    def sync_views(self, view):
        if self._syncing or not self.original_panel.isVisible():
            return
        self._syncing = True
        peer = self.original_view if view is self.image_view else self.image_view
        peer.setTransform(view.transform())
        peer.centerOn(view.mapToScene(view.viewport().rect().center()))
        self._syncing = False

    def update_image_display(self, pil_img, original=None):
        self._syncing = True
        self.image_view.set_image(QPixmap.fromImage(ImageQt(pil_img)))
        if original is not None:
            before = original if original.size == pil_img.size else original.resize(pil_img.size, Image.Resampling.LANCZOS)
            self.original_view.set_image(QPixmap.fromImage(ImageQt(before)))
        self._syncing = False
        self.sync_views(self.image_view)

    def closeEvent(self, event):
        if hasattr(self, 'shutdown'):
            self.shutdown()
        super().closeEvent(event)

    def show_about_dialog(self):
        AboutDialog(self).exec()
