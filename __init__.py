#!/usr/bin/env python
# -*- coding: utf-8 -*-
import bpy
import numpy as np
import mathutils
bl_info = {
    "name": "PysicsToBoneAnimation",
    "author": "Hin(@thamurian)",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "",
    "description": "アドオンの有効化と無効化を試すためのサンプル",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object"
}
class PhysicsToBoneAnimation(bpy.types.Operator):
    bl_idname = "object.sample21_create_object"
    bl_label = "PhysicsToBoneAnimation"
    bl_description = "ApplyToAnimation"
    bl_options = {'REGISTER', 'UNDO'}
    def __init__(self):
        self.TEMP_FLAG_NAME = "__tempFragment__"
        self.VERTEX_GROPU_NAME="frag"
        self.ARMATURE_NAME="PhysicsObjectAmt"

    #頂点グループの設定を行う
    def setVertexGroup(self,selected):
        for i in range(len(selected)):
            bpy.ops.object.mode_set(mode="OBJECT")
            bpy.ops.object.select_all(action='DESELECT')
            s = selected[i]
            bpy.context.view_layer.objects.active = s
            name = self.VERTEX_GROPU_NAME + str(i)
            if name not in s.vertex_groups.keys():
                vg = s.vertex_groups.new(name=name)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.object.vertex_group_assign()
        bpy.ops.object.mode_set(mode="OBJECT")

    #アーマチュアとボーンを作成する
    def createArmature(self,selected):
        bpy.ops.object.add(type='ARMATURE', enter_editmode=True, location=(0,0,0))
        amt = bpy.context.object
        amt.name = self.ARMATURE_NAME
        bpy.ops.armature.select_all(action='SELECT')
        bpy.ops.armature.delete()
        bpy.ops.object.mode_set(mode='EDIT')
        for i in range(len(selected)):
            s = selected[i]
            b = amt.data.edit_bones.new(self.VERTEX_GROPU_NAME+str(i))
            b.head = s.location
            b.tail = s.location + mathutils.Vector((0,0.1,0))

        bpy.ops.object.mode_set(mode="OBJECT")
        return amt

    def join(self,selected):
        #bpy.ops.object.select_all(action='DESELECT')
        #オブジェクトの中心に設定するメッシュ
        mesh = bpy.data.meshes.new("mesh")
        obj  = bpy.data.objects.new("MeshObject", mesh)
        scene = bpy.context.scene
        #scene.collection.objects.link(obj)
        bpy.context.collection.objects.link(obj)
        for i in range(len(selected)):
            s = selected[i]
            s.select_set(True)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.join()
        return obj

    def setPose(self,amt, selected):
        bpy.context.view_layer.objects.active = amt
        bpy.ops.object.mode_set(mode="POSE")
        for i in range(len(selected)):
            name = "frag" + str(i)
            s = selected[i]
            bone = amt.pose.bones[name]
            bone.location = s.location - amt.data.bones[name].head
            bone.keyframe_insert(data_path="location",group=name)
            bone.rotation_mode = s.rotation_mode
            if bone.rotation_mode == 'QUATERNION':
                bone.rotation_quaternion = s.rotation_quaternion
                bone.keyframe_insert(data_path="rotation_quaternion",group=name)
            elif bone.rotation_mode == 'AXIS_ANGLE':
                bone.rotation_axis_angle = s.rotation_axis_angle
                bone.keyframe_insert(data_path="rotation_axis_angle",group=name)
            else:
                bone.rotation_euler = s.rotation_euler
                bone.keyframe_insert(data_path="rotation_euler",group=name)

    def execute(self,context):
        _selected = bpy.context.selected_objects
        selected = []
        for s in _selected:
            if s.type == 'MESH':
                selected.append(s)
        if len(selected) == 0:
            return {'CANCELLED'}
        bpy.context.view_layer.objects.active = selected[0]
        nStart = bpy.context.scene.frame_start
        self.renameFragments(selected)
        nEnd = bpy.context.scene.frame_end
        bpy.context.scene.frame_set(nStart)
        #キーフレームにベイクする
        bpy.ops.rigidbody.bake_to_keyframes(frame_start=nStart, frame_end=nEnd)
        self.setVertexGroup(selected)
        amt = self.createArmature(selected)

        for t in range(nStart, nEnd + 1):
            bpy.context.scene.frame_set(t)
            self.setPose(amt,selected)
        #最初の時間に戻る
        bpy.context.scene.frame_set(nStart)
        bpy.ops.object.mode_set(mode="OBJECT")
        self.deleteOtherActions()
        obj = self.join(selected)    
        obj.select_set(True)
        bpy.context.view_layer.objects.active = amt
        bpy.ops.object.parent_set(type='ARMATURE_NAME')
        return {'FINISHED'}
    def renameFragments(self,selected):
        for i in range(len(selected)):
            s = selected[i]
            s.name = self.TEMP_FLAG_NAME+str(i)
    def deleteOtherActions(self):
        #目的のアクション以外のアクションを全部消す
        wlen =  len(self.TEMP_FLAG_NAME)
        for action in bpy.data.actions:
            #if action.name != "PhysicsObjectAmtAction":
            if action.name[0:wlen] == self.TEMP_FLAG_NAME:
                del(action)

def menu_func(self,context):
    #self.layout.separator()
    self.layout.operator(PhysicsToBoneAnimation.bl_idname)


def register():
    #print("サンプル 1-5: アドオン『サンプル 1-5』が有効化されました。")
    bpy.utils.register_class(PhysicsToBoneAnimation)
    bpy.types.VIEW3D_MT_object_apply.append(menu_func)
    pass


def unregister():
    #print("サンプル 1-5: アドオン『サンプル 1-5』が無効化されました。")
    bpy.utils.unregister_class(PhysicsToBoneAnimation)
    bpy.types.VIEW3D_MT_object_apply.remove(menu_func)
    pass


if __name__ == "__main__":
    register()


