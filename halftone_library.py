import numpy as np

class PatternLibrary:
    @staticmethod
    def cell_distances(x, y):
        """Distances from one shared cell center, in units of half a cell."""
        return np.abs((x % (2 * np.pi)) / np.pi - 1), np.abs((y % (2 * np.pi)) / np.pi - 1)

    @staticmethod
    def dot(x, y):
        """Circular contours with thresholds proportional to covered cell area."""
        u, v = PatternLibrary.cell_distances(x, y)
        radius_squared = u * u + v * v
        # Above radius 1 the circle intersects the cell edges. Subtract the
        # four circular segments to keep coverage consistent with other shapes.
        outside = np.maximum(radius_squared, 1)
        segments = outside * np.arccos(1 / np.sqrt(outside)) - np.sqrt(outside - 1)
        area = np.pi * radius_squared / 4 - segments
        return 2 * np.clip(area, 0, 1) - 1

    @staticmethod
    def line(x, y):
        
        return np.sin(x)

    @staticmethod
    def square(x, y):
        u, v = PatternLibrary.cell_distances(x, y)
        return 2 * np.maximum(u, v) ** 2 - 1

    @staticmethod
    def cross(x, y):
       
        return np.maximum(np.sin(x), np.cos(y))

    @staticmethod
    def diamond(x, y):
        u, v = PatternLibrary.cell_distances(x, y)
        distance = u + v
        area = np.where(distance <= 1, distance ** 2 / 2,
                        1 - (2 - distance) ** 2 / 2)
        return 2 * area - 1
