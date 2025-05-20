from PIL import Image, ImageDraw, ImageFont
import os
import random
import math

os.makedirs('.', exist_ok=True)

# 询问每类图片生成数量
num_colors = int(input("请输入要生成的纯色图片数量（建议不超过20）: "))
num_gradients = int(input("请输入要生成的渐变图片数量: "))
num_circles = int(input("请输入要生成的圆形图案图片数量: "))
num_shapes = int(input("请输入要生成的矩形/线条图案图片数量: "))
num_texts = int(input("请输入要生成的文字图片数量: "))

# 生成多种纯色图片
colors = [
    'red', 'green', 'blue', 'yellow', 'purple', 'orange', 'cyan', 'magenta', 'lime', 'pink',
    'brown', 'gray', 'black', 'white', 'navy', 'teal', 'maroon', 'olive', 'silver', 'gold'
]
for idx in range(num_colors):
    color = colors[idx % len(colors)]
    img = Image.new('RGB', (224, 224), color)
    img.save(f'color_{idx+1}_{color}.jpg')

# 生成多种渐变图片
for i in range(num_gradients):
    img = Image.new('RGB', (224, 224))
    for x in range(224):
        for y in range(224):
            r = int(255 * x / 223) if i % 2 == 0 else int(255 * y / 223)
            g = int(255 * y / 223) if i % 2 == 1 else int(255 * x / 223)
            b = 128 + (i * 20) % 127
            img.putpixel((x, y), (r, g, b))
    img.save(f'gradient_{i+1}.jpg')

# 生成带几何图案的图片（圆）
for i in range(num_circles):
    img = Image.new('RGB', (224, 224), 'white')
    draw = ImageDraw.Draw(img)
    for _ in range(5):
        x = random.randint(20, 180)
        y = random.randint(20, 180)
        r = random.randint(10, 40)
        color = tuple(random.randint(0, 255) for _ in range(3))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color, outline=None)
    img.save(f'circles_{i+1}.jpg')

# 生成带矩形和线条的图片
for i in range(num_shapes):
    img = Image.new('RGB', (224, 224), 'white')
    draw = ImageDraw.Draw(img)
    for _ in range(3):
        x1 = random.randint(0, 150)
        y1 = random.randint(0, 150)
        x2 = x1 + random.randint(30, 70)
        y2 = y1 + random.randint(30, 70)
        color = tuple(random.randint(0, 255) for _ in range(3))
        draw.rectangle([x1, y1, x2, y2], fill=color)
    for _ in range(3):
        x1 = random.randint(0, 223)
        y1 = random.randint(0, 223)
        x2 = random.randint(0, 223)
        y2 = random.randint(0, 223)
        color = tuple(random.randint(0, 255) for _ in range(3))
        draw.line([x1, y1, x2, y2], fill=color, width=3)
    img.save(f'shapes_{i+1}.jpg')

# 生成带文字的图片
texts = ["Test", "Hello", "Image", "Search", "AI", "Block", "Pattern", "Python", "Faiss", "Vision"]
for i in range(num_texts):
    text = texts[i % len(texts)]
    img = Image.new('RGB', (224, 224), 'white')
    draw = ImageDraw.Draw(img)
    draw.text((40, 100), text, fill='black')
    img.save(f'text_{i+1}_{text}.jpg')
