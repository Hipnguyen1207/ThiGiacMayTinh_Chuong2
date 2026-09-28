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
edit_image_original = None
edit_image_current = None
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


def choose_edit_image():
	global edit_image_original
	image_path = filedialog.askopenfilename(
		title="Chon anh de chinh sua",
		filetypes=[("Tep hinh anh", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.webp"), ("Tat ca tep", "*.*")],
	)
	if not image_path:
		return
	try:
		image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
	except (OSError, cv2.error) as error:
		messagebox.showerror("Loi doc anh", f"Khong the doc anh:\n{error}")
		return
	if image is None:
		messagebox.showerror("Loi doc anh", "Tep duoc chon khong phai anh hop le.")
		return
	edit_image_original = image
	status_label.configure(text=f"Anh chinh sua: {image_path}")
	update_edited_image()


def update_edited_image(value=None):
	global edit_image_current
	if edit_image_original is None:
		return
	brightness = brightness_scale.get()
	contrast = contrast_scale.get() / 100.0
	edit_image_current = cv2.convertScaleAbs(edit_image_original, alpha=contrast, beta=brightness)
	display_image(edit_image_label, cv2.cvtColor(edit_image_current, cv2.COLOR_BGR2RGB))


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


def save_image(image):
	if image is None:
		messagebox.showwarning("Chua co anh", "Hay tao hoac chon anh can luu truoc.")
		return

	file_path = filedialog.asksaveasfilename(
		title="Luu anh",
		defaultextension=".png",
		filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg *.jpeg"), ("BMP", "*.bmp")],
	)
	if not file_path:
		return

	extension = file_path.rsplit(".", 1)[-1].lower()
	if extension == "jpeg":
		extension = "jpg"
	if extension not in ("png", "jpg", "bmp"):
		messagebox.showerror("Dinh dang khong ho tro", "Chi ho tro PNG, JPEG va BMP.")
		return
	try:
		encoded, data = cv2.imencode(f".{extension}", image)
		if not encoded:
			raise OSError("Khong the ma hoa anh theo dinh dang da chon.")
		data.tofile(file_path)
	except (OSError, cv2.error) as error:
		messagebox.showerror("Loi luu anh", f"Khong the luu anh:\n{error}")
		return
	status_label.configure(text=f"Da luu anh: {file_path}")


def save_selected_image(event=None):
	"""Choose an available image from the active tab and save it."""
	if main_notebook.select() == str(color_tab):
		images = [
			("Anh goc", current_image_bgr),
			("Anh Greyscale", gray_image_current),
			("Anh HSV", hsv_image_current),
		]
	elif main_notebook.select() == str(edit_tab):
		images = [("Anh goc", edit_image_original), ("Anh da chinh sua", edit_image_current)]
	else:
		images = [
			("Anh 1", bitwise_image_1),
			("Anh 2", bitwise_image_2),
			("Ket qua Bitwise AND", bitwise_result_current),
		]

	window = tk.Toplevel(root)
	window.title("Chon anh de luu")
	window.resizable(False, False)
	tk.Label(window, text="Chon anh can luu:").pack(padx=18, pady=(12, 6))
	choice = tk.IntVar(value=0)
	for index, (name, image) in enumerate(images):
		tk.Radiobutton(
			window,
			text=name if image is not None else f"{name} (chua co)",
			variable=choice,
			value=index,
			state=tk.NORMAL if image is not None else tk.DISABLED,
		).pack(anchor="w", padx=18)

	def confirm():
		image = images[choice.get()][1]
		if image is None:
			messagebox.showwarning("Chua co anh", "Anh duoc chon chua san sang.", parent=window)
			return
		window.destroy()
		save_image(image)

	tk.Button(window, text="Tiep tuc", command=confirm).pack(pady=12)
	window.bind("<Return>", lambda event: confirm())
	window.transient(root)
	window.grab_set()


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
edit_tab = tk.Frame(main_notebook)
main_notebook.add(color_tab, text="Color Conversion")
main_notebook.add(bitwise_tab, text="Bitwise AND")
main_notebook.add(edit_tab, text="Edit Image")

edit_tab.columnconfigure(1, weight=1)
edit_tab.rowconfigure(1, weight=1)
edit_toolbar = tk.Frame(edit_tab)
edit_toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=12)
edit_file_actions = tk.LabelFrame(edit_toolbar, text="Image actions")
edit_file_actions.pack(side=tk.LEFT, padx=6, pady=6)
tk.Button(edit_file_actions, text="Select Image", command=choose_edit_image, padx=20, pady=12).pack(side=tk.LEFT, padx=4, pady=4)
tk.Button(edit_file_actions, text="Save Edited Image", command=lambda: save_image(edit_image_current), padx=20, pady=12).pack(side=tk.LEFT, padx=4, pady=4)
edit_controls = tk.LabelFrame(edit_toolbar, text="Adjustments")
edit_controls.pack_forget()
edit_controls = tk.LabelFrame(edit_tab, text="Adjustments")
edit_controls.grid(row=1, column=0, sticky="nsw", padx=12, pady=12)
tk.Label(edit_controls, text="Brightness (-255 to 255)").grid(row=0, column=0, sticky="w")
brightness_scale = tk.Scale(edit_controls, from_=-255, to=255, orient=tk.HORIZONTAL, command=update_edited_image)
brightness_scale.set(0)
brightness_scale.grid(row=1, column=0, sticky="ew")
tk.Label(edit_controls, text="Contrast (0 to 255)").grid(row=2, column=0, sticky="w")
contrast_scale = tk.Scale(edit_controls, from_=0, to=255, orient=tk.HORIZONTAL, command=update_edited_image)
contrast_scale.set(100)
contrast_scale.grid(row=3, column=0, sticky="ew")
edit_controls.columnconfigure(0, weight=1)
edit_image_frame = tk.LabelFrame(edit_tab, text="Preview")
edit_image_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 12), pady=12)
edit_image_label = tk.Label(edit_image_frame, text="Select an image to edit", bg="#eeeeee")
edit_image_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

color_toolbar = tk.Frame(color_tab)
color_toolbar.pack(fill=tk.X, padx=12, pady=12)
color_actions = tk.LabelFrame(color_toolbar, text="Image actions")
color_actions.pack(side=tk.LEFT, padx=6, pady=5)
select_button = tk.Button(color_actions, text="Select Image", command=choose_image, padx=20, pady=12)
select_button.pack(side=tk.LEFT, padx=4, pady=4)
convert_button = tk.Button(color_actions, text="Convert Color", command=convert_colors, padx=20, pady=12, state=tk.DISABLED)
convert_button.pack(side=tk.LEFT, padx=4, pady=4)
tk.Button(color_actions, text="Open Properties", command=open_properties_window, padx=20, pady=12).pack(side=tk.LEFT, padx=4, pady=4)
color_save_actions = tk.LabelFrame(color_toolbar, text="Save")
color_save_actions.pack(side=tk.LEFT, padx=6, pady=5)
tk.Button(color_save_actions, text="Save Original", command=lambda: save_image(current_image_bgr), padx=16, pady=12).pack(side=tk.LEFT, padx=4, pady=4)
tk.Button(color_save_actions, text="Save Greyscale", command=lambda: save_image(gray_image_current), padx=16, pady=12).pack(side=tk.LEFT, padx=4, pady=4)
tk.Button(color_save_actions, text="Save HSV", command=lambda: save_image(hsv_image_current), padx=16, pady=12).pack(side=tk.LEFT, padx=4, pady=4)

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
bitwise_select_actions = tk.LabelFrame(bitwise_toolbar, text="Select images")
bitwise_select_actions.pack(side=tk.LEFT, padx=6, pady=5)
tk.Button(bitwise_select_actions, text="Select Image 1", command=lambda: choose_bitwise_image(1), padx=20, pady=12).pack(side=tk.LEFT, padx=4, pady=4)
tk.Button(bitwise_select_actions, text="Select Image 2", command=lambda: choose_bitwise_image(2), padx=20, pady=12).pack(side=tk.LEFT, padx=4, pady=4)
bitwise_actions = tk.LabelFrame(bitwise_toolbar, text="Operations")
bitwise_actions.pack(side=tk.LEFT, padx=6, pady=5)
tk.Button(bitwise_actions, text="Apply Bitwise AND", command=apply_bitwise_and, padx=20, pady=12).pack(side=tk.LEFT, padx=4, pady=4)
tk.Button(bitwise_actions, text="Open Properties", command=open_properties_window, padx=20, pady=12).pack(side=tk.LEFT, padx=4, pady=4)
bitwise_save_actions = tk.LabelFrame(bitwise_toolbar, text="Save")
bitwise_save_actions.pack(side=tk.LEFT, padx=6, pady=5)
tk.Button(bitwise_save_actions, text="Save Result", command=lambda: save_image(bitwise_result_current), padx=20, pady=12).pack(padx=4, pady=4)

bitwise_frame = tk.LabelFrame(bitwise_tab, text="Bitwise AND")
bitwise_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
bitwise_inputs_frame = tk.Frame(bitwise_frame)
bitwise_inputs_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
bitwise_inputs_frame.columnconfigure(0, weight=1)
bitwise_inputs_frame.rowconfigure(0, weight=1)
bitwise_inputs_frame.rowconfigure(1, weight=1)

bitwise_image_frame_1 = tk.LabelFrame(bitwise_inputs_frame, text="Image 1")
bitwise_image_frame_1.grid(row=0, column=0, sticky="nsew", padx=5, pady=3)
bitwise_label_1 = tk.Label(bitwise_image_frame_1, text="Image 1 not selected", bg="#eeeeee")
bitwise_label_1.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

bitwise_image_frame_2 = tk.LabelFrame(bitwise_inputs_frame, text="Image 2")
bitwise_image_frame_2.grid(row=1, column=0, sticky="nsew", padx=5, pady=3)
bitwise_label_2 = tk.Label(bitwise_image_frame_2, text="Image 2 not selected", bg="#eeeeee")
bitwise_label_2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

bitwise_result_frame = tk.LabelFrame(bitwise_frame, text="Bitwise AND Result")
bitwise_result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
bitwise_result_label = tk.Label(bitwise_result_frame, text="Select both images to display the result", bg="#eeeeee")
bitwise_result_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
status_label = tk.Label(root, text="", anchor="w")
status_label.pack(fill=tk.X, padx=12, pady=(4, 12))

root.bind("<Control-s>", save_selected_image)
root.bind("<Control-S>", save_selected_image)

try:
	root.mainloop()
except KeyboardInterrupt:
	# Treat Ctrl+C as a normal request to close the Tkinter application.
	try:
		root.destroy()
	except tk.TclError:
		pass
