import bpy

from time import sleep


class BatchBake(bpy.types.Operator):
    bl_idname = 'bb.bake'
    bl_label = 'batch bake'
    bl_options = {'UNDO'}

    context = None
    bake_material = None
    bake_image = None
    high = None

    def execute(self, context):
        self.context = context
        self.high = context.scene.highpoly_bake_obj

        for obj in bpy.data.objects:
            obj.hide_render = True
            obj.hide_viewport = False
        bpy.data.objects[self.high].hide_render = False
        bpy.data.objects[self.high].hide_viewport = False

        if (self.context.scene.bake_multiple):
            low_objects = bpy.data.collections[
                context.scene.lowpoly_bake_obj].all_objects
            for obj in low_objects:
                self.bootstrap_bake(obj.name)
        else:
            self.bootstrap_bake(self.context.scene.lowpoly_bake_obj)

        return {'FINISHED'}

    def bootstrap_bake(self, low):
        self.prepare_bake(low)
        self.bake_maps(low)
        #self.clean_up(low)

    def prepare_bake(self, low):
        bpy.data.objects[low].hide_render = False
        bpy.data.objects[low].hide_viewport = False

        bpy.data.scenes[bpy.context.scene.name].render.engine = "CYCLES"

        self.bake_material = bpy.data.materials.new(name=low + '_bake')
        if bpy.data.objects[low].data.materials:
            bpy.data.objects[low].data.materials[0] = self.bake_material
        else:
            bpy.data.objects[low].data.materials.append(self.bake_material)

        self.bake_material.use_nodes = True
        nodes = self.bake_material.node_tree.nodes
        bake_node = nodes.new('ShaderNodeTexImage')
        bake_node.select = True

        self.bake_image = bpy.data.images.new(low + '_bake',
                                              width=512,
                                              height=512)
        bake_node.image = self.bake_image

        bpy.data.objects[self.high].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[low]

    def bake_maps(self, low):
        if (self.context.scene.bake_diffuse):
            self.bake_diffuse(low)
        if (self.context.scene.bake_normal):
            self.bake_normal(low)
        if (self.context.scene.bake_ao):
            self.bake_ao(low)

    def clean_up(self, low):
        bpy.data.objects[low].hide_render = True

    # TODO dry!
    def bake_diffuse(self, low):
        bpy.context.scene.cycles.samples = 1
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.ops.object.bake(type='DIFFUSE',
                            use_clear=True,
                            use_selected_to_active=True)

        self.bake_image.filepath_raw = self.context.scene.bake_out_path + low + '_diffuse.jpg'
        self.bake_image.file_format = 'JPEG'
        self.bake_image.save()

    def bake_normal(self, low):
        bpy.context.scene.cycles.samples = 1
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.ops.object.bake(type='NORMAL',
                            use_clear=True,
                            use_selected_to_active=True)

        self.bake_image.filepath_raw = self.context.scene.bake_out_path + low + '_normal.jpg'
        self.bake_image.file_format = 'JPEG'
        self.bake_image.save()

    def bake_ao(self, low):
        bpy.context.scene.cycles.samples = 32
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False
        bpy.context.scene.render.bake.use_pass_color = True
        bpy.ops.object.bake(type='AO',
                            use_clear=True,
                            use_selected_to_active=True)

        self.bake_image.filepath_raw = self.context.scene.bake_out_path + low + '_ao.jpg'
        self.bake_image.file_format = 'JPEG'
        self.bake_image.save()