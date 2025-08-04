
import cv2
import tkinter as tk
from tkinter import ttk
from image_processor import return_edges
from gcode_generator import svg_to_gcode

def run_gui():

    def generate_gcode(svg_path='output.svg', output_path='output.gcode'):
        """
        Generate GCode from an SVG file and write to output_path using svg_to_gcode(svg_path, output_path).
        Args:
            svg_path (str): Path to the SVG file.
            output_path (str): Path to write the GCode file.
        """
        try:
            svg_to_gcode(svg_path, output_path)
            print(f'GCode generated and saved to {output_path}')
        except Exception as e:
            print(f'Error generating GCode: {e}')
    img = cv2.imread('Slicer/slicer_test_image.jpg', cv2.IMREAD_GRAYSCALE)
    if img is None:
        print('Image not found!')
        return

    root = tk.Tk()
    root.title('Edge Detection Controls')
    root.minsize(400, 400)

    # Variables
    sobel_ksize = tk.IntVar(value=3)
    threshold = tk.IntVar(value=20)
    use_canny = tk.BooleanVar(value=False)
    canny_thresh1 = tk.IntVar(value=50)
    canny_thresh2 = tk.IntVar(value=150)

    def update_image(*args):
        ksize = sobel_ksize.get()
        # Ensure odd and >=3
        if ksize % 2 == 0:
            ksize += 1
            sobel_ksize.set(ksize)
        if ksize < 3:
            ksize = 3
            sobel_ksize.set(ksize)
        png = return_edges(
            img,
            sobel_ksize=ksize,
            threshold=threshold.get(),
            use_canny=use_canny.get(),
            canny_thresh1=canny_thresh1.get(),
            canny_thresh2=canny_thresh2.get()
        )
        cv2.imshow('Edges', png)


    # Sobel kernel size slider
    ttk.Label(root, text='Sobel Kernel Size (odd)').pack()
    sobel_slider = ttk.Scale(root, from_=3, to=15, orient='horizontal', variable=sobel_ksize)
    sobel_slider.pack(fill='x')
    sobel_slider.bind('<ButtonRelease-1>', lambda e: update_image())

    # Threshold slider
    ttk.Label(root, text='Threshold').pack()
    thresh_slider = ttk.Scale(root, from_=1, to=255, orient='horizontal', variable=threshold)
    thresh_slider.pack(fill='x')
    thresh_slider.bind('<ButtonRelease-1>', lambda e: update_image())

    # Canny checkbox
    canny_check = ttk.Checkbutton(root, text='Use Canny', variable=use_canny, command=update_image)
    canny_check.pack()

    # Canny threshold1 slider
    ttk.Label(root, text='Canny Threshold 1').pack()
    canny1_slider = ttk.Scale(root, from_=1, to=255, orient='horizontal', variable=canny_thresh1)
    canny1_slider.pack(fill='x')
    canny1_slider.bind('<ButtonRelease-1>', lambda e: update_image())

    # Canny threshold2 slider
    ttk.Label(root, text='Canny Threshold 2').pack()
    canny2_slider = ttk.Scale(root, from_=1, to=255, orient='horizontal', variable=canny_thresh2)
    canny2_slider.pack(fill='x')
    canny2_slider.bind('<ButtonRelease-1>', lambda e: update_image())


    # Generate GCode button
    gcode_btn = ttk.Button(root, text='Generate GCode', command=lambda: generate_gcode(svg_path='output.svg', output_path='output.gcode'))
    gcode_btn.pack(pady=10)

    # Initial image
    update_image()

    def on_closing():
        cv2.destroyAllWindows()
        root.destroy()

    root.protocol('WM_DELETE_WINDOW', on_closing)
    root.mainloop()

if __name__ == '__main__':
    run_gui()