"""Portable, validated settings; presets never contain the source design."""
import json
import math
from pathlib import Path

DEFAULTS = dict(ink_reduction=0, reduction_target='all', knockout_black=False,
                knockout_white=False, black_tolerance=30, white_tolerance=30,
                preserve_glow=False, protect_highlights=False, protect_details=False,
                glow_strength=75, highlight_strength=70, detail_strength=85,
                detail_width_mm=.35, tone_enabled=False, shadow_reduction=50,
                midtone_reduction=30, light_reduction=15, pattern_size=30, angle=22,
                shape_name='dot', alpha_halftone=True, antialias=True,
                print_size_enabled=False, print_width_cm=30., output_dpi=300,
                lpi_enabled=False, lpi=30., background='transparent', custom_mask_path=None)

BUILTINS = {
    'Clean start': {},
    'Black fabric · breathable': dict(ink_reduction=25, knockout_black=True,
                                     protect_details=True, background='#000000'),
    'White fabric · breathable': dict(ink_reduction=25, knockout_white=True,
                                     protect_details=True, background='#ffffff'),
    'Glow & neon': dict(ink_reduction=25, preserve_glow=True, protect_highlights=True,
                        protect_details=True, tone_enabled=True, background='#000000'),
    'Fine text & linework': dict(ink_reduction=20, protect_details=True, detail_strength=95),
}
RANGES = dict(ink_reduction=(0, 100), black_tolerance=(0, 100), white_tolerance=(0, 100),
              glow_strength=(0, 100), highlight_strength=(0, 100), detail_strength=(0, 100),
              detail_width_mm=(.1, 2), shadow_reduction=(0, 100), midtone_reduction=(0, 100),
              light_reduction=(0, 100), pattern_size=(5, 100), angle=(0, 90),
              print_width_cm=(.1, 200), output_dpi=(72, 1200), lpi=(5, 120))
CHOICES = dict(reduction_target=('all', 'black', 'white', 'both'),
               shape_name=('dot', 'line', 'square', 'cross', 'diamond', 'custom'),
               background=('#000000', '#ffffff', 'transparent'))


def validate(config):
    if not isinstance(config, dict) or set(config) - set(DEFAULTS):
        raise ValueError('Preset contains unknown settings.')
    result = dict(DEFAULTS, **config)
    for key, value in result.items():
        if key in RANGES:
            low, high = RANGES[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
                raise ValueError(f'Invalid preset value: {key}')
            if isinstance(DEFAULTS[key], int) and not isinstance(DEFAULTS[key], bool) and value != int(value):
                raise ValueError(f'{key} must be a whole number.')
            if isinstance(DEFAULTS[key], int) and not isinstance(DEFAULTS[key], bool):
                result[key] = int(value)
        elif key in CHOICES:
            if value not in CHOICES[key]:
                raise ValueError(f'Invalid preset choice: {key}')
        elif isinstance(DEFAULTS[key], bool):
            if not isinstance(value, bool):
                raise ValueError(f'{key} must be true or false.')
        elif key == 'custom_mask_path' and value is not None and not isinstance(value, str):
            raise ValueError('Invalid custom mask path.')
    return result


def load(path):
    if Path(path).stat().st_size > 1_000_000:
        raise ValueError('Preset file is too large.')
    document = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(document, dict) or document.get('format') != 'espadan-dtf-preset' or document.get('version') != 1:
        raise ValueError('This is not a supported Espadan preset.')
    return validate(document.get('settings'))


def save(path, config):
    document = dict(format='espadan-dtf-preset', version=1, settings=validate(config))
    Path(path).write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
