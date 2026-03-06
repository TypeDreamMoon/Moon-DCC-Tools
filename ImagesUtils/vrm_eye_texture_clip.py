import argparse
import os
import sys
from PIL import Image
from tkinter import filedialog, Tk

def split_eyes(image_path, output_dir=None):
    if not os.path.exists(image_path):
        print(f"错误: 找不到文件 {image_path}")
        return

    # 加载图片
    img = Image.open(image_path).convert("RGBA")
    
    # 获取实际内容边界并裁剪
    bbox = img.getbbox()
    if not bbox:
        print(f"跳过: {image_path} 似乎是全透明的")
        return
    
    cropped_img = img.crop(bbox)
    w, h = cropped_img.size
    
    # 水平切分
    mid_x = w // 2
    eyes = {
        "_L": cropped_img.crop((0, 0, mid_x, h)),
        "_R": cropped_img.crop((mid_x, 0, w, h))
    }
    
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(image_path)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取原文件名（不含后缀）
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    for suffix, eye_img in eyes.items():
        # 1:1 居中处理
        eye_w, eye_h = eye_img.size
        side = max(eye_w, eye_h)
        square_img = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        square_img.paste(eye_img, ((side - eye_w) // 2, (side - eye_h) // 2))
        
        # 保存
        out_name = f"{base_name}{suffix}.png"
        out_path = os.path.join(output_dir, out_name)
        square_img.save(out_path)
        print(f"成功导出: {out_path}")

def main():
    parser = argparse.ArgumentParser(description="自动分割瞳孔并转为1:1正方形")
    parser.add_argument("-s", "--select", action="store_true", help="弹出对话框选择图片")
    parser.add_argument("-f", "--file", type=str, help="指定图片文件路径")
    parser.add_argument("-o", "--output", type=str, help="指定输出目录 (默认为输入文件同级目录)")

    args = parser.parse_args()

    target_file = None

    # 逻辑判断：优先使用 -s 弹出对话框
    if args.select:
        root = Tk()
        root.withdraw()  # 隐藏主窗口
        target_file = filedialog.askopenfilename(
            title="选择瞳孔贴图",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.tga")]
        )
        root.destroy()
    elif args.file:
        target_file = args.file
    else:
        parser.print_help()
        return

    if target_file:
        split_eyes(target_file, args.output)
    else:
        print("未选择任何文件")

if __name__ == "__main__":
    main()