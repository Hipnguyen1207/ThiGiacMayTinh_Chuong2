import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy as np
from PIL import Image, ImageTk


current_image_bgr = None
bitwise_image_1 = None
bitwise_image_2 = None
gray_image_current = None
hsv_image_current = None
bitwise_result_current = None
properties_window = None
properties_text = None
properties_texts = {}
properties_image_labels = {}
properties_metric_labels = {}


def display_image(label, image_array):
	image = Image.fromarray(image_array)
	image.thumbnail((440, 600), Image.Resampling.LANCZOS)
	photo = ImageTk.PhotoImage(image)
	label.configure(image=photo, text="")
	label.image = photo


def choose_image():
	global current_image_bgr, gray_image_current, hsv_image_current

	image_path = filedialog.askopenfilename(
		title="Chon anh tu may tinh",
		filetypes=[
			("Tep hinh anh", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp"),
			("Tat ca tep", "*.*"),
		],
	)
	if not image_path:
		return

	try:
		image_data = np.fromfile(image_path, dtype=np.uint8)
		image_bgr = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
	except (OSError, cv2.error) as error:
		messagebox.showerror("Loi doc anh", f"Khong the doc anh:\n{error}")
		return

	if image_bgr is None:
		messagebox.showerror("Loi doc anh", "Tep duoc chon khong phai anh hop le.")
		return

	current_image_bgr = image_bgr
	gray_image_current = None
	hsv_image_current = None
	display_image(original_label, cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
	gray_label.configure(image="", text="Nhan 'Chuyen mau' de xem anh greyscale")
	gray_label.image = None
	hsv_label.configure(image="", text="Nhan 'Chuyen mau' de xem anh HSV")
	hsv_label.image = None
	status_label.configure(text=f"{image_path}  |  {image_bgr.shape[1]} x {image_bgr.shape[0]} px")


	convert_button.configure(state=tk.NORMAL)


def convert_colors():
	global gray_image_current, hsv_image_current
	if current_image_bgr is None:
		return

	gray_image = cv2.cvtColor(current_image_bgr, cv2.COLOR_BGR2GRAY)
	hsv_image = cv2.cvtColor(current_image_bgr, cv2.COLOR_BGR2HSV)
	hsv_display = hsv_image.copy()
	hsv_display[:, :, 0] = np.round(hsv_display[:, :, 0].astype(np.float32) * 255 / 179).astype(np.uint8)

	display_image(gray_label, gray_image)
	display_image(hsv_label, hsv_display)
	gray_image_current = gray_image
	hsv_image_current = hsv_image
	update_properties()


def choose_bitwise_image(image_number):
	global bitwise_image_1, bitwise_image_2

	image_path = filedialog.askopenfilename(
		title=f"Chon anh {image_number} tu may tinh",
		filetypes=[
			("Tep hinh anh", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp"),
			("Tat ca tep", "*.*"),
		],
	)
	if not image_path:
		return

	try:
		image_data = np.fromfile(image_path, dtype=np.uint8)
		image_bgr = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
	except (OSError, cv2.error) as error:
		messagebox.showerror("Loi doc anh", f"Khong the doc anh:\n{error}")
		return

	if image_bgr is None:
		messagebox.showerror("Loi doc anh", "Tep duoc chon khong phai anh hop le.")
		return

	if image_number == 1:
		bitwise_image_1 = image_bgr
		label = bitwise_label_1
	else:
		bitwise_image_2 = image_bgr
		label = bitwise_label_2
	display_image(label, cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
	global bitwise_result_current
	bitwise_result_current = None
	bitwise_result_label.configure(image="", text="Chon ca hai anh de hien thi ket qua")
	bitwise_result_label.image = None


def apply_bitwise_and():
	global bitwise_result_current
	if bitwise_image_1 is None or bitwise_image_2 is None:
		messagebox.showwarning("Thieu anh", "Hay chon ca hai anh truoc.")
		return

	# Phep AND can hai anh cung kich thuoc; resize anh 2 theo kich thuoc anh 1.
	image_2 = cv2.resize(
		bitwise_image_2,
		(bitwise_image_1.shape[1], bitwise_image_1.shape[0]),
		interpolation=cv2.INTER_NEAREST,
	)
	result = cv2.bitwise_and(bitwise_image_1, image_2)
	bitwise_result_current = result
	display_image(bitwise_result_label, cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
	update_properties()


def compare_images(first, second):
	if first.shape != second.shape:
		second = cv2.resize(second, (first.shape[1], first.shape[0]), interpolation=cv2.INTER_NEAREST)
	difference = first.astype(np.float32) - second.astype(np.float32)
	return f"MAE={np.mean(np.abs(difference)):.3f}, MSE={np.mean(difference ** 2):.3f}"


def update_properties():
	if not properties_image_labels:
		return
	def show_comparison(key, changed, original, title):
		image_label = properties_image_labels[key]
		metric_label = properties_metric_labels[key]
		if changed is None or original is None:
			image_label.configure(image="", text="Chua co du lieu")
			image_label.image = None
			metric_label.configure(text=title)
		else:
			display_image(image_label, changed)
			metric_label.configure(text=f"{title}\n{compare_images(changed, original)}")

	if current_image_bgr is not None:
		show_comparison("gray", gray_image_current, cv2.cvtColor(current_image_bgr, cv2.COLOR_BGR2GRAY), "Greyscale so voi anh goc")
		show_comparison("hsv", hsv_image_current, cv2.cvtColor(current_image_bgr, cv2.COLOR_BGR2HSV), "HSV so voi anh goc")
	else:
		show_comparison("gray", None, None, "Chua chon anh goc")
		show_comparison("hsv", None, None, "Chua chon anh goc")
	if bitwise_result_current is not None:
		image_2 = cv2.resize(bitwise_image_2, (bitwise_image_1.shape[1], bitwise_image_1.shape[0]), interpolation=cv2.INTER_NEAREST)
		show_comparison("and1", bitwise_result_current, bitwise_image_1, "Ket qua AND so voi anh 1")
		show_comparison("and2", bitwise_result_current, image_2, "Ket qua AND so voi anh 2")
	else:
		show_comparison("and1", None, None, "Chua co ket qua AND")
		show_comparison("and2", None, None, "Chua co ket qua AND")


def open_properties_window():
	global properties_window
	if properties_window is not None and properties_window.winfo_exists():
		properties_window.lift()
		return
	properties_window = tk.Toplevel(root)
	properties_window.title("Image Properties")
	properties_window.geometry("900x600")
	properties_notebook = ttk.Notebook(properties_window)
	properties_notebook.pack(fill=tk.BOTH, expand=True)

	for tab_name, comparisons in (("Color Conversion", (("gray", "Greyscale"), ("hsv", "HSV"))), ("Bitwise AND", (("and1", "So voi anh 1"), ("and2", "So voi anh 2")))):
		frame = tk.Frame(properties_notebook)
		properties_notebook.add(frame, text=tab_name)
		for column, (key, title) in enumerate(comparisons):
			frame.columnconfigure(column, weight=1)
			frame.rowconfigure(0, weight=1)
			box = tk.LabelFrame(frame, text=title)
			box.grid(row=0, column=column, sticky="nsew", padx=8, pady=8)
			image_label = tk.Label(box, text="Chua co du lieu", bg="#eeeeee")
			image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
			metric_label = tk.Label(box, text="", justify=tk.LEFT)
			metric_label.pack(pady=(0, 8))
			properties_image_labels[key] = image_label
			properties_metric_labels[key] = metric_label
	update_properties()


root = tk.Tk()
root.title("Image Processing")
root.geometry("1450x780")
root.minsize(850, 500)

main_notebook = ttk.Notebook(root)
main_notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

color_tab = tk.Frame(main_notebook)
bitwise_tab = tk.Frame(main_notebook)
main_notebook.add(color_tab, text="Color Conversion")
main_notebook.add(bitwise_tab, text="Bitwise AND")

color_toolbar = tk.Frame(color_tab)
color_toolbar.pack(fill=tk.X, padx=12, pady=12)
select_button = tk.Button(color_toolbar, text="Select Image", command=choose_image, padx=16, pady=8)
select_button.pack(side=tk.LEFT)
convert_button = tk.Button(color_toolbar, text="Convert Color", command=convert_colors, padx=16, pady=8, state=tk.DISABLED)
convert_button.pack(side=tk.LEFT, padx=(8, 0))
tk.Button(color_toolbar, text="Open Properties", command=open_properties_window, padx=16, pady=8).pack(side=tk.LEFT, padx=(8, 0))

images_frame = tk.Frame(color_tab)
images_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
for column in range(3):
	images_frame.columnconfigure(column, weight=1, uniform="images")
images_frame.rowconfigure(0, weight=1)

original_frame = tk.LabelFrame(images_frame, text="Original")
original_frame.grid(row=0, column=0, sticky="nsew", padx=5)
gray_frame = tk.LabelFrame(images_frame, text="Greyscale")
gray_frame.grid(row=0, column=1, sticky="nsew", padx=5)
hsv_frame = tk.LabelFrame(images_frame, text="HSV")
hsv_frame.grid(row=0, column=2, sticky="nsew", padx=5)

original_label = tk.Label(original_frame, text="Select an image to begin", bg="#eeeeee")
original_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
gray_label = tk.Label(gray_frame, text="", bg="#eeeeee")
gray_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
hsv_label = tk.Label(hsv_frame, text="", bg="#eeeeee")
hsv_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

bitwise_toolbar = tk.Frame(bitwise_tab)
bitwise_toolbar.pack(fill=tk.X, padx=12, pady=12)
tk.Button(bitwise_toolbar, text="Open Properties", command=open_properties_window, padx=16, pady=8).pack(side=tk.LEFT)

bitwise_frame = tk.LabelFrame(bitwise_tab, text="Bitwise AND")
bitwise_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
bitwise_inputs_frame = tk.Frame(bitwise_frame)
bitwise_inputs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
bitwise_inputs_frame.columnconfigure(0, weight=1)
bitwise_inputs_frame.rowconfigure(0, weight=1)
bitwise_inputs_frame.rowconfigure(1, weight=1)

bitwise_image_frame_1 = tk.LabelFrame(bitwise_inputs_frame, text="Image 1")
bitwise_image_frame_1.grid(row=0, column=0, sticky="nsew", padx=5, pady=3)
tk.Button(bitwise_image_frame_1, text="Select Image 1", command=lambda: choose_bitwise_image(1)).pack(anchor=tk.NE, padx=5, pady=(5, 0))
bitwise_label_1 = tk.Label(bitwise_image_frame_1, text="Image 1 not selected", bg="#eeeeee")
bitwise_label_1.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

bitwise_image_frame_2 = tk.LabelFrame(bitwise_inputs_frame, text="Image 2")
bitwise_image_frame_2.grid(row=1, column=0, sticky="nsew", padx=5, pady=3)
tk.Button(bitwise_image_frame_2, text="Select Image 2", command=lambda: choose_bitwise_image(2)).pack(anchor=tk.NE, padx=5, pady=(5, 0))
bitwise_label_2 = tk.Label(bitwise_image_frame_2, text="Image 2 not selected", bg="#eeeeee")
bitwise_label_2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

bitwise_result_frame = tk.LabelFrame(bitwise_frame, text="Bitwise AND Result")
bitwise_result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
bitwise_result_label = tk.Label(bitwise_result_frame, text="Select both images to display the result", bg="#eeeeee")
bitwise_result_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
tk.Button(bitwise_result_frame, text="Apply Bitwise AND", command=apply_bitwise_and).pack(pady=(0, 5))

status_label = tk.Label(root, text="", anchor="w")
status_label.pack(fill=tk.X, padx=12, pady=(4, 12))

root.mainloop()
