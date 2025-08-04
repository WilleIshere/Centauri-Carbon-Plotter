from xml.etree import ElementTree as ET
import re

def svg_to_gcode(svg_path, output_path, travel_height=5.0, draw_height=0.0):
    """
    Converts an SVG file to G-code by opening the files and converting the SVG paths to G-code commands.
    Each SVG <path> is converted to G0/G1 moves. Adds a travel move (Z up) between paths.
    travel_height: Z height for travel moves between paths
    draw_height: Z height for drawing
    """
    def parse_path_d(d):
        # Robust parser for M/L commands, handles spaces/commas and multiple points
        tokens = re.findall(r'([MLZmlz])|(-?\d*\.?\d+)', d)
        points = []
        idx = 0
        cmd = None
        while idx < len(tokens):
            if tokens[idx][0]:
                cmd = tokens[idx][0].upper()
                idx += 1
            elif cmd in ['M', 'L']:
                x = float(tokens[idx][1])
                y = float(tokens[idx+1][1])
                points.append((cmd, x, y))
                idx += 2
            elif cmd in ['Z']:
                points.append(('Z', None, None))
                idx += 1
            else:
                idx += 1
        return points

    tree = ET.parse(svg_path)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    svg_width = root.attrib.get('width', None)
    svg_height = root.attrib.get('height', None)
    viewBox = root.attrib.get('viewBox', None)
    def parse_svg_dim(val):
        if val is None:
            return None
        return float(val.replace('mm','').strip())
    width_mm = parse_svg_dim(svg_width)
    height_mm = parse_svg_dim(svg_height)
    # Default viewBox
    min_x = min_y = 0.0
    vb_width = width_mm if width_mm is not None else 256.0
    vb_height = height_mm if height_mm is not None else 256.0
    if viewBox:
        vb = viewBox.split()
        if len(vb) == 4:
            min_x = float(vb[0])
            min_y = float(vb[1])
            vb_width = float(vb[2])
            vb_height = float(vb[3])
    if width_mm is None or height_mm is None:
        width_mm = vb_width
        height_mm = vb_height

    with open(output_path, 'w') as gcode:
        gcode.write('; --- G-code setup start ---\n')
        gcode.write('G21 ; Set units to mm\n')
        gcode.write('G90 ; Absolute positioning\n')
        gcode.write('G92 X0 Y0 Z0 ; Set current position as zero\n')
        gcode.write('G0 Z{:.3f} ; Move to safe travel height\n'.format(travel_height))
        gcode.write('; --- G-code setup end ---\n')
        for path in root.findall('.//svg:path', ns):
            d = path.attrib.get('d')
            if not d:
                continue
            points = parse_path_d(d)
            if not points:
                continue
            # Travel move up before each path
            gcode.write(f'G0 Z{travel_height:.3f}\n')
            for i, (cmd, x, y) in enumerate(points):
                # Map SVG viewBox coordinates to mm
                if x is not None and y is not None:
                    x_mm = ((x - min_x) / vb_width) * width_mm
                    y_mm = ((y - min_y) / vb_height) * height_mm
                else:
                    x_mm = y_mm = None
                if cmd == 'M':
                    gcode.write(f'G0 X{x_mm:.3f} Y{y_mm:.3f}\n')  # Rapid move to start
                    gcode.write(f'G0 Z{draw_height:.3f}\n')  # Plunge to draw height
                elif cmd == 'L':
                    gcode.write(f'G1 X{x_mm:.3f} Y{y_mm:.3f}\n')  # Linear move
                elif cmd == 'Z':
                    gcode.write(f'G0 Z{travel_height:.3f} ; Path close, lift\n')
        gcode.write('M2 ; End of program\n')