import argparse
import os
from PIL import Image
from tkinter import filedialog, Tk

def split_eyes_advanced(image_path, output_dir=None, res=512, padding=40):
    """
    切分瞳孔，缩放至指定分辨率，并保留内边距。
    """
    if not os.path.exists(image_path):
        print(f"错误: 找不到文件 {image_path}")
        return

    # 1. 加载并获取内容边界
    img = Image.open(image_path).convert("RGBA")
    raw_bbox = img.getbbox()
    if not raw_bbox:
        print(f"跳过: {image_path} 似乎是全透明的")
        return
    
    # 裁剪到仅包含内容的区域并粗分左右
    content_img = img.crop(raw_bbox)
    w, h = content_img.size
    mid_x = w // 2
    
    raw_eyes = {
        "_L": content_img.crop((0, 0, mid_x, h)),
        "_R": content_img.crop((mid_x, 0, w, h))
    }
    
    # 确定输出目录
    if output_dir is None:
        output_dir = os.path.dirname(image_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_name = os.path.splitext(os.path.basename(image_path))[0]

    # 计算可用区域大小
    safe_zone = res - (padding * 2)
    if safe_zone <= 0:
        print("错误: Padding 过大，超过了目标分辨率")
        return

    for suffix, eye_raw_img in raw_eyes.items():
        # A. 提取纯像素部分
        eye_bbox = eye_raw_img.getbbox()
        if not eye_bbox: continue
        eye_content = eye_raw_img.crop(eye_bbox)
        
        # B. 计算缩放比例 (Uniform Scale)
        # 确保瞳孔的长边不超过 safe_zone
        curr_w, curr_h = eye_content.size
        scale = min(safe_zone / curr_w, safe_zone / curr_h)
        
        # 如果瞳孔本身比 safe_zone 小，你可以选择是否放大
        # 这里默认总是缩放以适配 safe_zone (或者你可以加个 if scale < 1)
        new_w = int(curr_w * scale)
        new_h = int(curr_h * scale)
        eye_resized = eye_content.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # C. 创建最终画布并居中粘贴
        final_canvas = Image.new("RGBA", (res, res), (0, 0, 0, 0))
        offset_x = (res - new_w) // 2
        offset_y = (res - new_h) // 2
        final_canvas.paste(eye_resized, (offset_x, offset_y))
        
        # D. 保存
        out_path = os.path.join(output_dir, f"{base_name}{suffix}.png")
        final_canvas.save(out_path)
        print(f"已导出: {out_path} [{res}x{res}, Padding: {padding}]")

def main():
    parser = argparse.ArgumentParser(description="瞳孔切割工具 - 像素级居中与规范化导出")
    parser.add_argument("-s", "--select", action="store_true", help="弹出对话框选择图片")
    parser.add_argument("-f", "--file", type=str, help="指定图片文件路径")
    parser.add_argument("-o", "--output", type=str, help="指定输出目录")
    parser.add_argument("-res", "--resolution", type=int, default=512, help="指定输出图片的宽高 (默认: 512)")
    parser.add_argument("-p", "--padding", type=int, default=40, help="眼睛与边界的最小留白 (默认: 40)")

    args = parser.parse_args()

    target_file = None
    if args.select:
        root = Tk(); root.withdraw()
        target_file = filedialog.askopenfilename(title="选择瞳孔贴图", filetypes=[("Images", "*.png *.jpg *.tga")])
        root.destroy()
    elif args.file:
        target_file = args.file
    else:
        parser.print_help(); return

    if target_file:
        split_eyes_advanced(target_file, args.output, args.resolution, args.padding)

if __name__ == "__main__":
    main()