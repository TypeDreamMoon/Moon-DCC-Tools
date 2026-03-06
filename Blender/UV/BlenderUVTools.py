import bpy
import bmesh
from mathutils import Vector

# --- 1. 定义逻辑算子 (Operator) ---
class UV_OT_CenterToCursor(bpy.types.Operator):
    """将选中的 UV 居中到游标位置"""
    bl_idname = "uv.center_to_cursor"
    bl_label = "Center to Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.edit_object
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "未找到有效的网格对象")
            return {'CANCELLED'}

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()
        
        # 获取当前 UV 编辑器的游标位置
        cursor_pos = context.space_data.cursor_location.copy()

        # 收集选中的 UV 顶点
        selected_uvs = [l[uv_layer] for f in bm.faces if f.select for l in f.loops if l[uv_layer].select]

        if not selected_uvs:
            self.report({'INFO'}, "未选中任何 UV 顶点")
            return {'CANCELLED'}

        # 计算几何中心 (Bounding Box)
        min_u = min(uv.uv.x for uv in selected_uvs)
        max_u = max(uv.uv.x for uv in selected_uvs)
        min_v = min(uv.uv.y for uv in selected_uvs)
        max_v = max(uv.uv.y for uv in selected_uvs)
        
        uv_center = Vector(((min_u + max_u) / 2, (min_v + max_v) / 2))
        offset = cursor_pos - uv_center

        # 应用偏移
        for uv in selected_uvs:
            uv.uv += offset

        bmesh.update_edit_mesh(obj.data)
        return {'FINISHED'}

# --- 2. 定义 UI 面板 (Panel) ---
class UV_PT_CustomPanel(bpy.types.Panel):
    """在 UV 编辑器 N 面板中创建一个自定义栏目"""
    bl_label = "UV 快速工具"
    bl_idname = "UV_PT_custom_panel"
    bl_space_type = 'IMAGE_EDITOR'  # 对应 UV 编辑器所在的区域
    bl_region_type = 'UI'           # 对应右侧 N 面板
    bl_category = "Moon Blender UV Tools"        # 面板的标签名称

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        
        # 添加按钮，调用上面定义的 Operator
        col.operator("uv.center_to_cursor", icon='CURSOR')
        
        # 你可以继续添加其他按钮
        col.separator()
        col.label(text="坐标: " + str(context.space_data.cursor_location))

# --- 3. 注册与注销 ---
classes = (UV_OT_CenterToCursor, UV_PT_CustomPanel)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()