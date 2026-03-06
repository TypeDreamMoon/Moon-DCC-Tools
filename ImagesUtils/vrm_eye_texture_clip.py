import argparse
import os
import sys
from PIL import Image
from tkinter import filedialog, Tk

def split_eyes_and_center(image_path, output_dir=None):
    """
    切分瞳孔，并确保左右瞳孔各自在其 1:1 画布中绝对像素居中。
    """
    if not os.path.exists(image_path):
        print(f"错误: 找不到文件 {image_path}")
        return

    # 1. 加载图片
    img = Image.open(image_path).convert("RGBA")
    
    # 2. 获取内容的边界（去除四周全透明部分）
    raw_bbox = img.getbbox()
    if not raw_bbox:
        print(f"跳过: {image_path} 似乎是全透明的")
        return
    
    # 裁剪到仅包含内容的区域
    content_only_img = img.crop(raw_bbox)
    w, h = content_only_img.size
    
    # 3. 水平粗切分（将合并的内容从中间切开）
    mid_x = w // 2
    raw_eyes = {
        "_L": content_only_img.crop((0, 0, mid_x, h)),
        "_R": content_only_img.crop((mid_x, 0, w, h))
    }
    
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(image_path)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取原文件名
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    for suffix, eye_raw_img in raw_eyes.items():
        # --- 核心修正部分：重新居中逻辑 ---
        
        # A. 获取当前瞳孔本身的像素包围盒 (getbbox 在这里非常关键)
        eye_bbox = eye_raw_img.getbbox()
        if not eye_bbox:
            continue
        
        # B. 再次裁剪，只留下纯像素区域
        eye_content = eye_raw_img.crop(eye_bbox)
        eye_w, eye_h = eye_content.size
        
        # C. 确定 1:1 正方形的边长（向上取偶数，方便除法）
        side = max(eye_w, eye_h)
        if side % 2 != 0: side += 1
        
        # D. 创建透明正方形画布
        square_img = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        
        # E. 计算纯像素内容的居中偏移量
        offset_x = (side - eye_w) // 2
        offset_y = (side - eye_h) // 2
        
        # F. 将瞳孔贴到中心
        square_img.paste(eye_content, (offset_x, offset_y))
        
        # --- 保存 ---
        out_name = f"{base_name}{suffix}.png"
        out_path = os.path.join(output_dir, out_name)
        square_img.save(out_path)
        print(f"成功导出 (像素居中): {out_path} ({side}x{side})")

def main():
    parser = argparse.ArgumentParser(description="自动分割瞳孔并确保像素级 1:1 居中")
    parser.add_argument("-s", "--select", action="store_true", help="弹出对话框选择图片")
    parser.add_argument("-f", "--file", type=str, help="指定图片文件路径")
    parser.add_argument("-o", "--output", type=str, help="指定输出目录 (默认为输入文件同级目录)")

    args = parser.parse_args()

    target_file = None

    if args.select:
        root = Tk()
        root.withdraw()
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
        split_eyes_and_center(target_file, args.output)
    else:
        print("未选择任何文件")

if __name__ == "__main__":
    main()