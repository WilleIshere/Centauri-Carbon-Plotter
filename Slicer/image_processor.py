import cv2
import numpy as np

def return_edges(img, sobel_ksize=3, threshold=20, use_canny=False, canny_thresh1=50, canny_thresh2=150, target_width_mm=256, target_height_mm=256):
    """
    Detects edges in a grayscale image, writes the contours as SVG to 'output.svg',
    converts the SVG to a PNG using ImageMagick, and returns the PNG as a cv2 image.

    Parameters:
        img (np.ndarray): Grayscale input image.
        sobel_ksize (int, optional): Kernel size for the Sobel operator (default: 3).
        threshold (int, optional): Threshold value for edge binarization (default: 20).
        use_canny (bool, optional): If True, use Canny edge detection instead of Sobel+threshold (default: False).
        canny_thresh1 (int, optional): First threshold for the hysteresis in Canny (default: 50).
        canny_thresh2 (int, optional): Second threshold for the hysteresis in Canny (default: 150).

    Returns:
        np.ndarray: PNG image (as a cv2 image) generated from the SVG contours.
    """
    # Step 1: Edge detection
    if use_canny:
        binary = cv2.Canny(img, canny_thresh1, canny_thresh2)
    else:
        sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=sobel_ksize)
        sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=sobel_ksize)
        gradient_magnitude = cv2.magnitude(sobelx, sobely)
        gradient_magnitude = cv2.convertScaleAbs(gradient_magnitude)
        # Step 2: Threshold to get binary edges
        _, binary = cv2.threshold(gradient_magnitude, threshold, 255, cv2.THRESH_BINARY)

    # Step 3: Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Step 4: Convert contours to SVG path data, scaling if needed
    height, width = img.shape[:2]
    scale = 1.0
    svg_unit = 'px'
    if target_width_mm is not None and target_height_mm is not None:
        scale_x = target_width_mm / width
        scale_y = target_height_mm / height
        scale = min(scale_x, scale_y)
        svg_unit = 'mm'
        out_w = width * scale
        out_h = height * scale
        offset_x = (target_width_mm - out_w) / 2
        offset_y = (target_height_mm - out_h) / 2
    elif target_width_mm is not None:
        scale = target_width_mm / width
        svg_unit = 'mm'
        out_w = width * scale
        out_h = height * scale
        offset_x = 0
        offset_y = 0
    elif target_height_mm is not None:
        scale = target_height_mm / height
        svg_unit = 'mm'
        out_w = width * scale
        out_h = height * scale
        offset_x = 0
        offset_y = 0
    else:
        out_w = width
        out_h = height
        offset_x = 0
        offset_y = 0

    svg_paths = []
    for contour in contours:
        if len(contour) < 2:
            continue
        x0, y0 = contour[0][0]
        x0s, y0s = x0 * scale + offset_x, y0 * scale + offset_y
        path = f"M {x0s:.3f} {y0s:.3f}"
        for point in contour[1:]:
            x, y = point[0]
            xs, ys = x * scale + offset_x, y * scale + offset_y
            path += f" L {xs:.3f} {ys:.3f}"
        path += " Z"
        svg_paths.append(path)

    # Optionally, wrap in <svg> tags and write to file
    if svg_unit == 'mm':
        svg_header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{target_width_mm:.2f}mm" height="{target_height_mm:.2f}mm" viewBox="0 0 {target_width_mm:.2f} {target_height_mm:.2f}">'
        stroke_width = 0.1
    else:
        svg_header = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">'
        stroke_width = 1
    svg_content = ''.join([f'<path d="{p}" fill="none" stroke="black" stroke-width="{stroke_width}"/>' for p in svg_paths])
    svg_footer = '</svg>'
    svg = svg_header + svg_content + svg_footer

    # Write SVG to file
    with open('output.svg', 'w', encoding='utf-8') as f:
        f.write(svg)
        
    import subprocess
    # Convert SVG file to PNG file using ImageMagick
    subprocess.run(["magick", "output.svg", "output.png"])
    # Read the PNG file back into OpenCV
    png_cv2_img = cv2.imread('output.png')

    return png_cv2_img

