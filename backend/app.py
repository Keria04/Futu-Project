import os
import numpy as np
import faiss
from tkinter import Tk, filedialog, Canvas, NW, Button, Label
from PIL import Image, ImageTk

from Model_module.calculate_embeded import calaculate_embeded

# 1. 初始化模型
embedder = calaculate_embeded()
dimension = embedder.get_dimension()

# 2. 嵌入生成函数
def generate_embeddings(img):
    """
    img: 路径(str) 或 PIL.Image
    返回: (1, dim) 的 float32 numpy 数组
    """
    if isinstance(img, str):
        image = Image.open(img)
    else:
        image = img
    vec = embedder.calculate(image)
    return vec.reshape(1, -1)

# 3. 初始化FAISS索引和ID映射
index = faiss.IndexFlatL2(dimension)
id_map = {}

# 4. 入库图片（自动导入datasets目录下所有图片，采用相对路径）
base_dir = os.path.join(os.path.dirname(__file__), '..', 'datasets')
img_exts = ('.jpg', '.jpeg', '.png', '.bmp')
db_img_paths = [
    os.path.relpath(os.path.join(base_dir, fname), start=os.getcwd())
    for fname in os.listdir(base_dir)
    if fname.lower().endswith(img_exts)
]
for idx, path in enumerate(db_img_paths):
    embedding = generate_embeddings(path)
    index.add(embedding)
    id_map[idx] = path

def crop_image_with_gui(image_path):
    """弹出窗口让用户框选图片区域，返回裁剪后的图片对象"""
    root = Tk()
    root.title("选择查询图片区域")
    img = Image.open(image_path)
    tk_img = ImageTk.PhotoImage(img)
    canvas = Canvas(root, width=img.width, height=img.height)
    canvas.pack()
    canvas.create_image(0, 0, anchor=NW, image=tk_img)
    rect = None
    start_x = start_y = end_x = end_y = 0

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        if rect:
            canvas.delete(rect)
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline='red')

    def on_mouse_move(event):
        nonlocal rect
        if rect:
            canvas.coords(rect, start_x, start_y, event.x, event.y)

    def on_mouse_up(event):
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_move)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    cropped_img = [None]

    def confirm_crop():
        x1, y1 = min(start_x, end_x), min(start_y, end_y)
        x2, y2 = max(start_x, end_x), max(start_y, end_y)
        if x2 > x1 and y2 > y1:
            cropped_img[0] = img.crop((x1, y1, x2, y2))
        else:
            cropped_img[0] = img
        root.destroy()

    btn = Button(root, text="确定", command=confirm_crop)
    btn.pack()
    root.mainloop()
    return cropped_img[0]

def select_query_image():
    """弹出文件选择框，返回用户选择的图片路径"""
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="选择查询图片",
        filetypes=[("Image Files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    root.destroy()
    return file_path

def search_image(query_img, topk=3):
    """支持传入PIL图片对象或图片路径"""
    embedding = generate_embeddings(query_img)
    D, I = index.search(embedding, k=topk)
    results = []
    for idx in I[0]:
        results.append(id_map.get(idx, 'Unknown'))
    return results

if __name__ == '__main__':
    # 选择查询图片
    query_path = select_query_image()
    if not query_path:
        print("未选择图片，程序退出。")
        exit(0)
    # 框选区域
    cropped_img = crop_image_with_gui(query_path)
    # 检索
    result = search_image(cropped_img, topk=3)
    print('检索结果:', result)
