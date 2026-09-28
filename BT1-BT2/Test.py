import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
import numpy as np
from PIL import Image, ImageTk


current_image_bgr = None


def display_image(label, image_array):
	image = Image.fromarray(image_array)
	image.thumbnail((440, 600), Image.Resampling.LANCZOS)
	photo = ImageTk.PhotoImage(image)
	label.configure(image=photo, text="")
	label.image = photo


def choose_image():
	global current_image_bgr

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
	display_image(original_label, cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB))
	gray_label.configure(image="", text="Nhan 'Chuyen mau' de xem anh greyscale")
	gray_label.image = None
	hsv_label.configure(image="", text="Nhan 'Chuyen mau' de xem anh HSV")
	hsv_label.image = None
	status_label.configure(text=f"{image_path}  |  {image_bgr.shape[1]} x {image_bgr.shape[0]} px")


	convert_button.configure(state=tk.NORMAL)


def convert_colors():
	if current_image_bgr is None:
		return

	gray_image = cv2.cvtColor(current_image_bgr, cv2.COLOR_BGR2GRAY)
	hsv_image = cv2.cvtColor(current_image_bgr, cv2.COLOR_BGR2HSV)
	hsv_display = hsv_image.copy()
	hsv_display[:, :, 0] = np.round(hsv_display[:, :, 0].astype(np.float32) * 255 / 179).astype(np.uint8)

	display_image(gray_label, gray_image)
	display_image(hsv_label, hsv_display)


root = tk.Tk()
root.title("Mo va hien thi anh")
root.geometry("1450x780")
root.minsize(850, 500)

toolbar = tk.Frame(root)
toolbar.pack(fill=tk.X, padx=12, pady=12)

select_button = tk.Button(toolbar, text="Chon anh", command=choose_image, padx=16, pady=8)
select_button.pack(side=tk.LEFT)

convert_button = tk.Button(toolbar, text="Chuyen mau", command=convert_colors, padx=16, pady=8, state=tk.DISABLED)
convert_button.pack(side=tk.LEFT, padx=(8, 0))

images_frame = tk.Frame(root)
images_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
for column in range(3):
	images_frame.columnconfigure(column, weight=1, uniform="images")
images_frame.rowconfigure(0, weight=1)

original_frame = tk.LabelFrame(images_frame, text="Anh goc")
original_frame.grid(row=0, column=0, sticky="nsew", padx=5)
gray_frame = tk.LabelFrame(images_frame, text="Greyscale")
gray_frame.grid(row=0, column=1, sticky="nsew", padx=5)
hsv_frame = tk.LabelFrame(images_frame, text="HSV (kenh H/S/V)")
hsv_frame.grid(row=0, column=2, sticky="nsew", padx=5)

original_label = tk.Label(original_frame, text="Chon mot anh de bat dau", bg="#eeeeee")
original_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
gray_label = tk.Label(gray_frame, text="", bg="#eeeeee")
gray_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
hsv_label = tk.Label(hsv_frame, text="", bg="#eeeeee")
hsv_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

status_label = tk.Label(root, text="", anchor="w")
status_label.pack(fill=tk.X, padx=12, pady=(4, 12))

root.mainloop()