import numpy as np
from PIL import Image, ImageOps, ImageFilter
from halftone_library import PatternLibrary


class HalftoneProcessor:
    @staticmethod
    def smoothstep(low, high, values):
        t = np.clip((values - low) / (high - low), 0, 1)
        return t * t * (3 - 2 * t)

    @staticmethod
    def detail_mask(image, radius):
        """Local top/bottom hats detect strokes narrower than the filter window.

        Alpha opening also catches opaque dark strokes on transparent backgrounds.
        This is contrast/geometry detection, not text recognition.
        """
        pixels = np.asarray(image, dtype=np.float32)
        alpha = pixels[:, :, 3] / 255
        light = (pixels[:, :, 0] * .299 + pixels[:, :, 1] * .587 + pixels[:, :, 2] * .114)
        light = np.rint(light * alpha + 127 * (1 - alpha)).astype(np.uint8)
        gray = Image.fromarray(light)
        size = 2 * radius + 1
        opened = gray.filter(ImageFilter.MinFilter(size)).filter(ImageFilter.MaxFilter(size))
        closed = gray.filter(ImageFilter.MaxFilter(size)).filter(ImageFilter.MinFilter(size))
        contrast = np.maximum(light.astype(np.float32) - np.asarray(opened, dtype=np.float32),
                              np.asarray(closed, dtype=np.float32) - light)
        alpha_image = image.getchannel('A')
        alpha_open = alpha_image.filter(ImageFilter.MinFilter(size)).filter(ImageFilter.MaxFilter(size))
        contrast = np.maximum(contrast, pixels[:, :, 3] - np.asarray(alpha_open, dtype=np.float32))
        return HalftoneProcessor.smoothstep(12, 60, contrast) * (alpha > 0)

    @staticmethod
    def load_image(path):
        with Image.open(path) as source:
            info = source.info.copy()
            image = ImageOps.exif_transpose(source).convert('RGBA')
        image.info.update(info)
        return image

    @staticmethod
    def process_image(image_path, pattern_size=30, angle=45, shape_name='dot',
                      alpha_halftone=True, knockout_black=False, black_tolerance=30,
                      custom_mask_path=None, antialias=True, knockout_white=False,
                      white_tolerance=30, ink_reduction=0, reduction_target='all',
                      preserve_glow=False, protect_highlights=False, protect_details=False,
                      glow_strength=75, highlight_strength=70, detail_strength=85,
                      detail_radius=2, tone_reduction=None, output_dpi=None,
                      print_width_cm=None, lpi=None, cancelled=None):
        """Create transparent print gaps; pattern size is in source pixels.

        Knockout fades colors near the garment color. Reduction lowers alpha
        before screening. Strips bound intermediate memory for large designs.
        """
        if not 0 <= ink_reduction <= 100:
            raise ValueError('Ink reduction must be between 0 and 100.')
        for value in (glow_strength, highlight_strength, detail_strength):
            if not np.isfinite(value) or not 0 <= value <= 100:
                raise ValueError('Protection strength must be between 0 and 100.')
        if tone_reduction is not None and (len(tone_reduction) != 3 or
                any(not np.isfinite(v) or not 0 <= v <= 100 for v in tone_reduction)):
            raise ValueError('Shadow, midtone and highlight reduction must be between 0 and 100.')
        if not isinstance(detail_radius, int) or not 1 <= detail_radius <= 15:
            raise ValueError('Detail radius must be between 1 and 15 pixels.')
        if output_dpi is not None and (not np.isfinite(output_dpi) or not 72 <= output_dpi <= 1200):
            raise ValueError('Output DPI must be between 72 and 1200.')
        if reduction_target not in ('all', 'black', 'white', 'both'):
            raise ValueError('Unknown reduction target.')
        if shape_name not in ('dot', 'line', 'square', 'cross', 'diamond', 'custom'):
            raise ValueError('Unknown pattern shape.')
        if shape_name == 'custom' and not custom_mask_path:
            raise ValueError('Load a custom mask before selecting custom shape.')
        image = (image_path.copy() if isinstance(image_path, Image.Image)
                 else HalftoneProcessor.load_image(image_path))
        if cancelled is not None and cancelled():
            raise InterruptedError('Render cancelled.')
        info = image.info.copy()
        if print_width_cm is not None:
            if output_dpi is None or not np.isfinite(print_width_cm) or print_width_cm <= 0:
                raise ValueError('Set a positive print width and output DPI.')
            width = max(1, round(print_width_cm / 2.54 * output_dpi))
            height = max(1, round(image.height * width / image.width))
            if width * height > 60_000_000:
                raise ValueError('Output exceeds 60 million pixels. Reduce print size or DPI.')
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        dpi = output_dpi or info.get('dpi', (300, 300))[0]
        if lpi is not None:
            if not np.isfinite(lpi) or not 1 <= lpi <= dpi / 3:
                raise ValueError('LPI must allow at least 3 pixels per cell (LPI ≤ DPI / 3).')
            pattern_size = dpi / lpi
        if output_dpi is not None:
            info['dpi'] = (output_dpi, output_dpi)
        details = HalftoneProcessor.detail_mask(image, detail_radius) if protect_details else None
        source = np.asarray(image.convert('RGBA'))
        h, w = source.shape[:2]
        output = np.empty_like(source)
        mask = None
        if shape_name == 'custom':
            custom = HalftoneProcessor.load_image(custom_mask_path)
            luminance = np.asarray(custom.convert('L'), dtype=np.float32) / 255
            mask_alpha = np.asarray(custom.getchannel('A'), dtype=np.float32) / 255
            mask = 1 - (1 - luminance) * mask_alpha
        cell_size = max(3, float(pattern_size))
        theta = np.radians(angle)
        cosine, sine = np.cos(theta), np.sin(theta)
        x = np.arange(w, dtype=np.float32)[None, :]
        for start in range(0, h, 256):
            if cancelled is not None and cancelled():
                raise InterruptedError('Render cancelled.')
            stop = min(h, start + 256)
            pixels = source[start:stop]
            rgb = pixels[:, :, :3].astype(np.float32)
            alpha = pixels[:, :, 3].astype(np.float32) / 255
            original_alpha = alpha.copy()
            light = (rgb[:, :, 0] * .299 + rgb[:, :, 1] * .587 + rgb[:, :, 2] * .114) / 255
            highlight = HalftoneProcessor.smoothstep(.65, .95, light)
            chroma = (rgb.max(axis=2) - rgb.min(axis=2)) / 255
            # Colored dark halos and existing soft-alpha edges are likely glow regions.
            colored_halo = np.clip(chroma * 3, 0, 1) * (1 - HalftoneProcessor.smoothstep(.45, .9, light))
            soft_edge = (1 - HalftoneProcessor.smoothstep(.85, 1, original_alpha)) * (original_alpha > 0)
            glow = np.maximum(colored_halo, soft_edge) if preserve_glow else np.zeros_like(alpha)
            glow *= glow_strength / 100
            # Channel distance protects saturated colors from black/white knockout.
            black_distance = rgb.max(axis=2)
            white_distance = 255 - rgb.min(axis=2)
            black_match = 1 - np.clip(black_distance / max(1, black_tolerance * 2.55), 0, 1)
            white_match = 1 - np.clip(white_distance / max(1, white_tolerance * 2.55), 0, 1)
            black_match *= 1 - glow
            white_match *= 1 - glow
            if knockout_black:
                alpha *= 1 - black_match
            if knockout_white:
                alpha *= 1 - white_match
            weights = {'all': 1, 'black': black_match, 'white': white_match,
                       'both': np.maximum(black_match, white_match)}
            protection = np.maximum(glow, highlight * highlight_strength / 100 if protect_highlights else 0)
            if details is not None:
                protection = np.maximum(protection, details[start:stop] * detail_strength / 100)
            reduction = ink_reduction / 100
            if tone_reduction is not None:
                shadow_weight = 1 - HalftoneProcessor.smoothstep(.15, .5, light)
                light_weight = HalftoneProcessor.smoothstep(.5, .85, light)
                mid_weight = 1 - shadow_weight - light_weight
                reduction = (shadow_weight * tone_reduction[0] + mid_weight * tone_reduction[1] +
                             light_weight * tone_reduction[2]) / 100
            alpha *= 1 - reduction * weights[reduction_target] * (1 - protection)
            y = np.arange(start, stop, dtype=np.float32)[:, None]
            xr, yr = x * cosine - y * sine, x * sine + y * cosine
            if mask is not None:
                mh, mw = mask.shape
                ix = np.clip((xr % cell_size / cell_size * mw).astype(int), 0, mw - 1)
                iy = np.clip((yr % cell_size / cell_size * mh).astype(int), 0, mh - 1)
                screen = mask[iy, ix]
            else:
                scale = 2 * np.pi / cell_size
                screen = (getattr(PatternLibrary, shape_name)(xr * scale, yr * scale) + 1) / 2
            screen = screen * 0.9 + 0.05

            def threshold(tone):
                value = (np.clip((tone - screen) * 12 + 0.5, 0, 1)
                         if antialias else (tone > screen).astype(np.float32))
                value = np.where(tone <= 0, 0, np.where(tone >= 1, 1, value))
                return np.rint(value * 255).astype(np.uint8)

            if alpha_halftone:
                output[start:stop, :, :3] = pixels[:, :, :3]
                rendered_alpha = threshold(alpha)
            else:
                gray = (rgb[:, :, 0] * .299 + rgb[:, :, 1] * .587 + rgb[:, :, 2] * .114) / 255
                output[start:stop, :, :3] = threshold(gray)[:, :, None]
                rendered_alpha = (threshold(alpha) if ink_reduction or tone_reduction is not None else
                                  np.rint(alpha * 255).astype(np.uint8))
            if preserve_glow and antialias:
                # Keep existing soft halo transitions rather than breaking them into islands.
                blend = glow * soft_edge
                # Screening must not turn a faint halo pixel into a bright opaque speck.
                rendered_alpha = np.minimum(rendered_alpha, original_alpha * 255)
                rendered_alpha = rendered_alpha * (1 - blend) + alpha * 255 * blend
            if details is not None and antialias:
                blend = details[start:stop] * detail_strength / 100
                rendered_alpha = rendered_alpha * (1 - blend) + alpha * 255 * blend
            output[start:stop, :, 3] = np.rint(rendered_alpha).astype(np.uint8)
        result = Image.fromarray(output)
        for key in ('dpi', 'icc_profile'):
            if key in info:
                result.info[key] = info[key]
        return result

    @staticmethod
    def save_image(image, path):
        options = {key: image.info[key] for key in ('dpi', 'icc_profile') if key in image.info}
        image.save(path, format='PNG', **options)
