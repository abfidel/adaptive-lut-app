import numpy as np
import os
from datetime import datetime

class LUTGenerator:
    def __init__(self, lut_size=32):
        self.lut_size = lut_size
    
    def generate_cube_from_json(self, adjustment_json, output_path=None, title=None):
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"static/luts/adaptive_lut_{timestamp}.cube"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write("TITLE \"Adaptive LUT Test\"\n")
            f.write(f"LUT_3D_SIZE {self.lut_size}\n")
            f.write("\n")
            for i in range(self.lut_size ** 3):
                r = (i % self.lut_size) / (self.lut_size - 1)
                g = ((i // self.lut_size) % self.lut_size) / (self.lut_size - 1)
                b = (i // (self.lut_size * self.lut_size)) / (self.lut_size - 1)
                f.write(f"{r:.6f} {g:.6f} {b:.6f}\n")
        return output_path

def create_lut_from_json(adjustment_json, output_path=None, lut_size=32):
    generator = LUTGenerator(lut_size=lut_size)
    return generator.generate_cube_from_json(adjustment_json, output_path)
