import numpy as np
from PIL import Image
from halftone_library import PatternLibrary

class HalftoneProcessor:
    @staticmethod
    def process_image(image_path, pattern_size=30, angle=45, shape_name="dot", 
                      alpha_halftone=True, knockout_black=False, black_tolerance=30,
                      custom_mask_path=None, antialias=True):
        
        img_pil = Image.open(image_path).convert('RGBA')
        img_arr = np.array(img_pil)

        r, g, b, a = img_arr[:, :, 0], img_arr[:, :, 1], img_arr[:, :, 2], img_arr[:, :, 3]
        h, w = r.shape

        if knockout_black:
            
            luminance = 0.299 * r + 0.587 * g + 0.114 * b
            tol_value = max(1, black_tolerance * 2.55) 
            soft_mask = np.clip(luminance / tol_value, 0, 1)
            a = (a * soft_mask).astype(np.uint8)

        x, y = np.arange(w), np.arange(h)
        X, Y = np.meshgrid(x, y)

        
        theta = np.radians(angle)
        X_rot = X * np.cos(theta) - Y * np.sin(theta)
        Y_rot = X * np.sin(theta) + Y * np.cos(theta)

        cell_size = max(3, pattern_size)

        if shape_name == "custom" and custom_mask_path:
            mask_pil = Image.open(custom_mask_path).convert('L')
            mask_arr = np.array(mask_pil) / 255.0
            mh, mw = mask_arr.shape
            
            idx_x = ((X_rot % cell_size) / cell_size * mw).astype(int)
            idx_y = ((Y_rot % cell_size) / cell_size * mh).astype(int)
            
            idx_x = np.clip(idx_x, 0, mw - 1)
            idx_y = np.clip(idx_y, 0, mh - 1)
            
            screen = mask_arr[idx_y, idx_x]
        else:
            freq_scale = (2 * np.pi) / cell_size
            pattern_func = getattr(PatternLibrary, shape_name, PatternLibrary.dot)
            raw_screen = pattern_func(X_rot * freq_scale, Y_rot * freq_scale)
            screen = (raw_screen + 1) / 2.0 

        
        screen = screen * 0.9 + 0.05 

        
        sharpness = 12.0 
        
        if alpha_halftone:
            a_norm = a / 255.0
            if antialias:
                new_a = np.clip((a_norm - screen) * sharpness + 0.5, 0, 1) * 255.0
                
                
                new_a = np.where(a_norm < 0.02, 0, new_a)
                
                new_a = new_a.astype(np.uint8)
            else:
                new_a = np.where(a_norm > screen, 255, 0).astype(np.uint8)
                
            final_arr = np.dstack((r, g, b, new_a))
        else:
            gray = 0.299 * r + 0.587 * g + 0.114 * b
            gray_norm = gray / 255.0
            if antialias:
                new_gray = np.clip((gray_norm - screen) * sharpness + 0.5, 0, 1) * 255.0
                new_gray = np.where(gray_norm < 0.02, 0, new_gray)
                halftoned_gray = new_gray.astype(np.uint8)
            else:
                halftoned_gray = np.where(gray_norm > screen, 255, 0).astype(np.uint8)
                
            final_arr = np.dstack((halftoned_gray, halftoned_gray, halftoned_gray, np.full((h, w), 255, dtype=np.uint8)))

        return Image.fromarray(final_arr, 'RGBA')