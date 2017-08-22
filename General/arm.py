from PySide2 import QtWidgets, QtCore, QtGui

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, is_checked, grpbox
from auri.scripts.Maya_Scripts import rig_lib
from auri.scripts.Maya_Scripts.rig_lib import RigController

reload(rig_lib)

class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        self.modules_cbbox = QtWidgets.QComboBox()
        self.outputs_cbbox = QtWidgets.QComboBox()
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.prebuild_btn = QtWidgets.QPushButton("Prebuild")
        self.side_cbbox = QtWidgets.QComboBox()
        self.ik_creation_switch = QtWidgets.QCheckBox()
        self.stretch_creation_switch = QtWidgets.QCheckBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.ik_creation_switch.setChecked(self.model.ik_creation_switch)
        self.stretch_creation_switch.setChecked(self.model.stretch_creation_switch)
        self.side_cbbox.setCurrentText(self.model.side)
        self.ctrl.look_for_parent()

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        self.ik_creation_switch.stateChanged.connect(self.ctrl.on_ik_creation_switch_changed)
        self.ik_creation_switch.setEnabled(False)
        self.stretch_creation_switch.stateChanged.connect(self.ctrl.on_stretch_creation_switch_changed)

        self.side_cbbox.insertItems(0, ["Left", "Right"])
        self.side_cbbox.currentTextChanged.connect(self.ctrl.on_side_cbbox_changed)

        self.refresh_btn.clicked.connect(self.ctrl.look_for_parent)
        self.prebuild_btn.clicked.connect(self.ctrl.prebuild)

        main_layout = QtWidgets.QVBoxLayout()

        select_parent_layout = QtWidgets.QVBoxLayout()
        select_parent_grp = grpbox("Select parent", select_parent_layout)
        cbbox_layout = QtWidgets.QHBoxLayout()
        cbbox_layout.addWidget(self.modules_cbbox)
        cbbox_layout.addWidget(self.outputs_cbbox)
        select_parent_layout.addLayout(cbbox_layout)
        select_parent_layout.addWidget(self.refresh_btn)

        options_layout = QtWidgets.QVBoxLayout()
        options_grp = grpbox("Options", options_layout)

        side_layout = QtWidgets.QVBoxLayout()
        side_grp = grpbox("Side", side_layout)
        side_layout.addWidget(self.side_cbbox)

        checkbox_layout = QtWidgets.QVBoxLayout()
        ik_layout = QtWidgets.QHBoxLayout()
        ik_text = QtWidgets.QLabel("IK ctrls :")
        ik_layout.addWidget(ik_text)
        ik_layout.addWidget(self.ik_creation_switch)
        stretch_layout = QtWidgets.QHBoxLayout()
        stretch_text = QtWidgets.QLabel("stretch/squash :")
        stretch_layout.addWidget(stretch_text)
        stretch_layout.addWidget(self.stretch_creation_switch)

        checkbox_layout.addLayout(ik_layout)
        checkbox_layout.addLayout(stretch_layout)

        options_layout.addLayout(checkbox_layout)

        main_layout.addWidget(select_parent_grp)
        main_layout.addWidget(side_grp)
        main_layout.addWidget(options_grp)
        main_layout.addWidget(self.prebuild_btn)
        self.setLayout(main_layout)


class Controller(RigController):
    def __init__(self, model, view):
        """

        Args:
            model (Model):
            view (View):
        """
        self.guides_grp = None
        self.guides = []
        self.guides_names = []
        self.side = {}
        self.side_coef = 0
        self.jnt_input_grp = None
        self.ctrl_input_grp = None
        self.parts_grp = None
        self.created_skn_jnts = []
        self.created_fk_jnts = []
        self.created_ik_jnts = []
        self.created_fk_ctrls = []
        self.created_ik_ctrls = []
        self.option_ctrl = None
        RigController.__init__(self,  model, view)

    def prebuild(self):
        self.create_temporary_outputs(["wrist_OUTPUT"])

        self.guides_names = ["{0}_shoulder_GUIDE".format(self.model.module_name),
                             "{0}_elbow_GUIDE".format(self.model.module_name),
                             "{0}_wrist_GUIDE".format(self.model.module_name)]

        self.side = {"Left": 1, "Right": -1}
        self.side_coef = self.side.get(self.model.side)

        if self.guide_check(self.guides_names):
            self.guides = pmc.ls("{0}_shoulder_GUIDE".format(self.model.module_name),
                                 "{0}_elbow_GUIDE".format(self.model.module_name),
                                 "{0}_wrist_GUIDE".format(self.model.module_name))
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            return

        shoulder_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0])
        elbow_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[1])
        wrist_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[2])

        shoulder_guide.setAttr("translate", (3 * self.side_coef, 10, 0))
        elbow_guide.setAttr("translate", (5 * self.side_coef, 8, 0))
        wrist_guide.setAttr("translate", (7 * self.side_coef, 6, 0))

        self.guides = [shoulder_guide, elbow_guide, wrist_guide]
        self.guides_grp = self.group_guides(self.guides)
        self.guides_grp.setAttr("visibility", 1)
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.created_ik_ctrls = []
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()

        self.create_skn_jnts()
        self.create_options_ctrl()
        self.create_and_connect_fk_ik_jnts()
        self.create_fk()
        if self.model.ik_creation_switch:
            self.create_ik()
        if self.model.stretch_creation_switch == 1:
            self.connect_fk_stretch()
            self.connect_ik_stretch()
        self.clean_rig()
        self.created_output()
        pmc.select(d=1)

    def connect_to_parent(self):
        check_list = ["CTRL_GRP", "JNT_GRP", "PARTS_GRP"]
        if not rig_lib.exists_check(check_list):
            print("No necessary groups created for module {0}".format(self.model.module_name))
            return

        self.jnt_input_grp = pmc.group(em=1, n="{0}_jnt_INPUT".format(self.model.module_name))
        self.ctrl_input_grp = pmc.group(em=1, n="{0}_ctrl_INPUT".format(self.model.module_name))
        self.parts_grp = pmc.group(em=1, n="{0}_parts_INPUT".format(self.model.module_name))

        if self.model.selected_module != "No_parent" and self.model.selected_module != "{0}".format(
                self.model.module_name):
            parent_name = "{0}_{1}".format(self.model.selected_module, self.model.selected_output)
            parent_node = pmc.ls(parent_name)[0]
            rig_lib.matrix_constraint(parent_node, self.ctrl_input_grp, srt="trs")
            rig_lib.matrix_constraint(parent_node, self.jnt_input_grp, srt="trs")
        else:
            print("No parent for module {0}".format(self.model.module_name))

        pmc.parent(self.jnt_input_grp, "JNT_GRP", r=1)
        pmc.parent(self.parts_grp, "PARTS_GRP", r=1)

        local_ctrl_list = pmc.ls(regex=".*_local_CTRL$")
        if len(local_ctrl_list) > 0:
            local_ctrl = local_ctrl_list[0]
            pmc.parent(self.ctrl_input_grp, local_ctrl, r=1)
        else:
            pmc.parent(self.ctrl_input_grp, "CTRL_GRP", r=1)

    def create_skn_jnts(self):
        duplicates_guides = []
        for guide in self.guides:
            duplicate = guide.duplicate(n="{0}_duplicate".format(guide))[0]
            duplicates_guides.append(duplicate)

        shoulder_const = pmc.aimConstraint(duplicates_guides[1], duplicates_guides[0], maintainOffset=0,
                                           aimVector=(1.0 * self.side_coef, 0.0, 0.0),
                                           upVector=(0.0, 1.0 * self.side_coef, 0.0),
                                           worldUpType="scene")
        elbow_cons = pmc.aimConstraint(duplicates_guides[2], duplicates_guides[1], maintainOffset=0,
                                       aimVector=(1.0 * self.side_coef, 0.0, 0.0),
                                       upVector=(0.0, 1.0 * self.side_coef, 0.0),
                                       worldUpType="scene")
        pmc.delete(shoulder_const)
        pmc.delete(elbow_cons)
        pmc.parent(duplicates_guides[1], duplicates_guides[0])
        pmc.parent(duplicates_guides[2], duplicates_guides[1])
        pmc.select(d=1)

        shoulder_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1)),
                                 n="{0}_shoulder_SKN".format(self.model.module_name))
        shoulder_jnt.setAttr("rotate", pmc.xform(duplicates_guides[0], q=1, rotation=1))
        if self.model.side == "Right":
            shoulder_jnt.setAttr("jointOrientX", -180)
            shoulder_jnt.setAttr("rotate", (pmc.xform(shoulder_jnt, q=1, rotation=1)[0] + 180,
                                            pmc.xform(shoulder_jnt, q=1, rotation=1)[1] * -1,
                                            pmc.xform(shoulder_jnt, q=1, rotation=1)[2] * -1))
        elbow_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1)),
                              n="{0}_elbow_SKN".format(self.model.module_name))
        elbow_jnt.setAttr("rotate", pmc.xform(duplicates_guides[1], q=1, rotation=1))
        wrist_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)),
                              n="{0}_wrist_SKN".format(self.model.module_name))

        pmc.parent(shoulder_jnt, self.jnt_input_grp, r=0)
        self.created_skn_jnts = [shoulder_jnt, elbow_jnt, wrist_jnt]

        pmc.delete(duplicates_guides[:])

    def create_options_ctrl(self):
        self.option_ctrl = rig_lib.little_cube("{0}_option_CTRL".format(self.model.module_name))
        option_ofs = pmc.group(self.option_ctrl, n="{0}_option_ctrl_OFS".format(self.model.module_name), r=1)
        pmc.parent(option_ofs, self.ctrl_input_grp)
        rig_lib.matrix_constraint(self.created_skn_jnts[-1], option_ofs, srt="trs")
        ctrl_shape = self.option_ctrl.getShape()
        pmc.move(ctrl_shape, [0, 0, -3 * self.side_coef], relative=1, objectSpace=1, worldSpaceDistance=1)
        self.option_ctrl.addAttr("fkIk", attributeType="float", defaultValue=0, hidden=0, keyable=1, hasMaxValue=1,
                                 hasMinValue=1, maxValue=1, minValue=0)

    def create_and_connect_fk_ik_jnts(self):
        shoulder_fk_jnt = \
        self.created_skn_jnts[0].duplicate(n="{0}_shoulder_fk_JNT".format(self.model.module_name))[0]
        elbow_fk_jnt = pmc.ls("{0}_shoulder_fk_JNT|{0}_elbow_SKN".format(self.model.module_name))[0]
        wrist_fk_jnt = pmc.ls("{0}_shoulder_fk_JNT|{0}_elbow_SKN|{0}_wrist_SKN".format(self.model.module_name))[0]
        elbow_fk_jnt.rename("{0}_elbow_fk_JNT".format(self.model.module_name))
        wrist_fk_jnt.rename("{0}_wrist_fk_JNT".format(self.model.module_name))
        self.created_fk_jnts = [shoulder_fk_jnt, elbow_fk_jnt, wrist_fk_jnt]

        shoulder_ik_jnt = self.created_skn_jnts[0].duplicate(n="{0}_shoulder_ik_JNT".format(self.model.module_name))[0]
        elbow_ik_jnt = pmc.ls("{0}_shoulder_ik_JNT|{0}_elbow_SKN".format(self.model.module_name))[0]
        wrist_ik_jnt = pmc.ls("{0}_shoulder_ik_JNT|{0}_elbow_SKN|{0}_wrist_SKN".format(self.model.module_name))[0]
        elbow_ik_jnt.rename("{0}_elbow_ik_JNT".format(self.model.module_name))
        wrist_ik_jnt.rename("{0}_wrist_ik_JNT".format(self.model.module_name))
        self.created_ik_jnts = [shoulder_ik_jnt, elbow_ik_jnt, wrist_ik_jnt]

        for i, skn_jnt in enumerate(self.created_skn_jnts):
            pair_blend = pmc.createNode("pairBlend", n="{0}_ik_fk_switch_PAIRBLEND".format(skn_jnt))
            blend_color = pmc.createNode("blendColors", n="{0}_ik_fk_switch_BLENDCOLORS".format(skn_jnt))

            self.created_fk_jnts[i].translate >> pair_blend.inTranslate1
            self.created_fk_jnts[i].rotate >> pair_blend.inRotate1
            self.created_fk_jnts[i].scale >> blend_color.color2
            self.created_ik_jnts[i].translate >> pair_blend.inTranslate2
            self.created_ik_jnts[i].rotate >> pair_blend.inRotate2
            self.created_ik_jnts[i].scale >> blend_color.color1
            pair_blend.outTranslate >> skn_jnt.translate
            pair_blend.outRotate >> skn_jnt.rotate
            blend_color.output >> skn_jnt.scale
            self.option_ctrl.fkIk >> pair_blend.weight
            self.option_ctrl.fkIk >> blend_color.blender

    def create_fk(self):
        shoulder_ctrl = pmc.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=2, d=3, s=8,
                                   n="{0}_shoulder_fk_CTRL".format(self.model.module_name), ch=0)[0]
        shoulder_ofs = pmc.group(shoulder_ctrl, n="{0}_shoulder_fk_ctrl_OFS".format(self.model.module_name))
        shoulder_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[0], q=1, ws=1, translation=1))
        if self.model.side == "Right":
            shoulder_ofs.setAttr("rotateX", -180)
        shoulder_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[0], q=1, rotation=1))
        shoulder_ctrl.setAttr("rotateOrder", 0)
        pmc.parent(shoulder_ofs, self.ctrl_input_grp, r=0)

        elbow_ctrl = pmc.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=2, d=3, s=8,
                                n="{0}_elbow_fk_CTRL".format(self.model.module_name), ch=0)[0]
        elbow_ofs = pmc.group(elbow_ctrl,
                              n="{0}_elbow_fk_ctrl_OFS".format(self.model.module_name))
        elbow_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1))
        elbow_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[1], q=1, rotation=1))
        elbow_ctrl.setAttr("rotateOrder", 0)
        pmc.parent(elbow_ofs, shoulder_ctrl, r=0)
        elbow_ofs.setAttr("rotate", (0, 0, 0))

        wrist_ctrl = pmc.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=2, d=3, s=8,
                                n="{0}_wrist_fk_CTRL".format(self.model.module_name), ch=0)[0]
        wrist_ofs = pmc.group(wrist_ctrl,
                              n="{0}_wrist_fk_ctrl_OFS".format(self.model.module_name))
        wrist_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[2], q=1, ws=1, translation=1))
        wrist_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[2], q=1, rotation=1))
        wrist_ctrl.setAttr("rotateOrder", 0)
        pmc.parent(wrist_ofs, elbow_ctrl, r=0)
        wrist_ofs.setAttr("rotate", (0, 0, 0))

        self.created_fk_ctrls = [shoulder_ctrl, elbow_ctrl, wrist_ctrl]

        for i, ctrl in enumerate(self.created_fk_ctrls):
            ctrl.rotate >> self.created_fk_jnts[i].rotate

    def create_ik(self):
        ik_handle = pmc.ikHandle(n=("{0}_ik_HDL".format(self.model.module_name)),
                                 startJoint=self.created_ik_jnts[0], endEffector=self.created_ik_jnts[-1],
                                 solver="ikRPsolver")[0]
        ik_effector = pmc.listRelatives(self.created_ik_jnts[-2], children=1)[1]
        ik_effector.rename("{0}_ik_EFF".format(self.model.module_name))

        ik_ctrl = rig_lib.medium_cube("{0}_wrist_ik_CTRL".format(self.model.module_name))
        ik_ctrl_ofs = pmc.group(ik_ctrl, n="{0}_wrist_ik_ctrl_OFS".format(self.model.module_name))

        fk_ctrl_01_value = pmc.xform(self.created_fk_ctrls[0], q=1, rotation=1)
        fk_ctrl_02_value = pmc.xform(self.created_fk_ctrls[1], q=1, rotation=1)
        fk_ctrl_03_value = pmc.xform(self.created_fk_ctrls[2], q=1, rotation=1)
        self.created_fk_ctrls[0].setAttr("rotate", (0, 0, 0))
        self.created_fk_ctrls[1].setAttr("rotate", (0, 0, 0))
        self.created_fk_ctrls[2].setAttr("rotate", (0, 0, 0))

        ik_ctrl_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[2], q=1, ws=1, translation=1))
        if self.model.side == "Right":
            ik_ctrl_ofs.setAttr("rotateX", -180)
        pmc.parent(ik_handle, ik_ctrl_ofs, r=0)
        ik_ctrl.setAttr("translate", pmc.xform(ik_handle, q=1, translation=1))
        pmc.parent(ik_handle, ik_ctrl, r=0)
        pmc.parent(ik_ctrl_ofs, self.ctrl_input_grp)

        pole_vector = rig_lib.jnt_shape_curve("{0}_poleVector_CTRL".format(self.model.module_name))
        pv_ofs = pmc.group(pole_vector, n="{0}_poleVector_ctrl_OFS".format(self.model.module_name))
        pv_ofs.setAttr("translate", (pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[0],
                                     pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[1],
                                     pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[2] - (
                                   (pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[0]) * self.side_coef)))
        pmc.poleVectorConstraint(pole_vector, ik_handle)
        pmc.parent(pv_ofs, self.ctrl_input_grp, r=0)

        self.created_ik_jnts[1].setAttr("preferredAngleY", -90)

        self.created_ik_ctrls = [ik_ctrl, pole_vector]

        self.created_fk_ctrls[0].setAttr("rotate", fk_ctrl_01_value)
        self.created_fk_ctrls[1].setAttr("rotate", fk_ctrl_02_value)
        self.created_fk_ctrls[2].setAttr("rotate", fk_ctrl_03_value)

        pmc.xform(pole_vector, ws=1, translation=(pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)))

        ik_handle.setAttr("visibility", 0)

        pmc.evalDeferred("import pymel.core as pmc")
        pmc.evalDeferred("pmc.xform(\"{0}\", ws=1, translation=(pmc.xform(\"{1}\", q=1, ws=1, translation=1)))".format(ik_ctrl, self.created_fk_jnts[-1]))

    def connect_fk_stretch(self):
        self.created_fk_jnts[1].addAttr("baseTranslateX", attributeType="float",
                                        defaultValue=pmc.xform(self.created_fk_jnts[1], q=1, translation=1)[0],
                                        hidden=0, keyable=0)
        self.created_fk_jnts[1].setAttr("baseTranslateX", lock=1, channelBox=0)
        self.created_fk_jnts[2].addAttr("baseTranslateX", attributeType="float",
                                        defaultValue=pmc.xform(self.created_fk_jnts[2], q=1, translation=1)[0],
                                        hidden=0, keyable=0)
        self.created_fk_jnts[2].setAttr("baseTranslateX", lock=1, channelBox=0)
        self.created_fk_ctrls[0].addAttr("stretch", attributeType="float", defaultValue=1, hidden=0, keyable=1,
                                         hasMinValue=1, minValue=0)
        self.created_fk_ctrls[1].addAttr("stretch", attributeType="float", defaultValue=1, hidden=0, keyable=1,
                                         hasMinValue=1, minValue=0)
        arm_mult = pmc.createNode("multDoubleLinear", n="{0}_upperarm_fk_stretch_MDL".format(self.model.module_name))
        forearm_mult = pmc.createNode("multDoubleLinear", n="{0}_forearm_fk_stretch_MDL".format(self.model.module_name))

        self.created_fk_ctrls[0].stretch >> arm_mult.input1
        self.created_fk_jnts[1].baseTranslateX >> arm_mult.input2
        arm_mult.output >> self.created_fk_jnts[1].translateX
        arm_mult.output >> self.created_fk_ctrls[1].getParent().translateX
        self.created_fk_ctrls[1].stretch >> forearm_mult.input1
        self.created_fk_jnts[2].baseTranslateX >> forearm_mult.input2
        forearm_mult.output >> self.created_fk_jnts[2].translateX
        forearm_mult.output >> self.created_fk_ctrls[2].getParent().translateX

    def connect_ik_stretch(self):
        self.created_ik_jnts[1].addAttr("baseTranslateX", attributeType="float",
                                        defaultValue=(pmc.xform(self.created_ik_jnts[1], q=1, translation=1)[0]*self.side_coef),
                                        hidden=0, keyable=0)
        self.created_ik_jnts[1].setAttr("baseTranslateX", lock=1, channelBox=0)
        self.created_ik_jnts[2].addAttr("baseTranslateX", attributeType="float",
                                        defaultValue=(pmc.xform(self.created_ik_jnts[2], q=1, translation=1)[0]*self.side_coef),
                                        hidden=0, keyable=0)
        self.created_ik_jnts[2].setAttr("baseTranslateX", lock=1, channelBox=0)

        self.created_ik_ctrls[0].setAttr("translate", (0, 0, 0))
        start_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_start_LOC".format(self.model.module_name))
        end_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ik_length_end_LOC".format(self.model.module_name))
        pmc.parent(start_loc, self.created_fk_ctrls[0].getParent(), r=1)
        pmc.parent(end_loc, self.created_ik_ctrls[0], r=1)
        start_loc_shape = start_loc.getShape()
        end_loc_shape = end_loc.getShape()
        length_measure = pmc.createNode("distanceDimShape", n="{0}_ik_length_measure_DDMShape".format(self.model.module_name))
        measure_transform = length_measure.getParent()
        measure_transform.rename("{0}_ik_length_measure_DDM".format(self.model.module_name))
        pmc.parent(measure_transform, self.parts_grp, r=0)
        arm_global_scale = pmc.createNode("multiplyDivide", n="{0}_ik_global_scale_MDV".format(self.model.module_name))
        arm_stretch_value = pmc.createNode("multiplyDivide", n="{0}_ik_stretch_value_MDV".format(self.model.module_name))
        stretch_condition = pmc.createNode("condition", n="{0}_ik_stretch_CONDITION".format(self.model.module_name))
        arm_stretch_mult = pmc.createNode("multDoubleLinear", n="{0}_upperarm_ik_stretch_mult_MDL".format(self.model.module_name))
        forearm_stretch_mult = pmc.createNode("multDoubleLinear", n="{0}_forearm_ik_stretch_mult_MDL".format(self.model.module_name))
        global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]

        start_loc_shape.worldPosition[0] >> length_measure.startPoint
        end_loc_shape.worldPosition[0] >> length_measure.endPoint
        arm_global_scale.setAttr("operation", 2)
        length_measure.distance >> arm_global_scale.input1X
        global_scale.output >> arm_global_scale.input2X
        arm_stretch_value.setAttr("operation", 2)
        arm_stretch_value.setAttr("input2X", length_measure.getAttr("distance"))
        arm_global_scale.outputX >> arm_stretch_value.input1X
        stretch_condition.setAttr("operation", 4)
        stretch_condition.setAttr("secondTerm", length_measure.getAttr("distance"))
        stretch_condition.setAttr("colorIfTrueR", 1)
        arm_global_scale.outputX >> stretch_condition.firstTerm
        arm_stretch_value.outputX >> stretch_condition.colorIfFalseR
        stretch_condition.outColorR >> arm_stretch_mult.input1
        self.created_ik_jnts[1].baseTranslateX >> arm_stretch_mult.input2
        arm_stretch_mult.output >> self.created_ik_jnts[1].translateX
        stretch_condition.outColorR >> forearm_stretch_mult.input1
        self.created_ik_jnts[2].baseTranslateX >> forearm_stretch_mult.input2
        forearm_stretch_mult.output >> self.created_ik_jnts[2].translateX

        start_loc_shape.setAttr("visibility", 0)
        end_loc_shape.setAttr("visibility", 0)

        pmc.evalDeferred("import pymel.core as pmc")
        pmc.evalDeferred("pmc.xform(\"{0}\", ws=1, translation=(pmc.xform(\"{1}\", q=1, ws=1, translation=1)))".format(
            self.created_ik_ctrls[0], self.created_fk_jnts[-1]))

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        if self.model.side == "Left":
            color_value = 6
        else:
            color_value = 13

        rig_lib.change_shape_color(self.option_ctrl, 9)

        invert_value = pmc.createNode("plusMinusAverage", n="{0}_fk_visibility_MDL".format(self.model.module_name))
        invert_value.setAttr("input1D[0]", 1)
        invert_value.setAttr("operation", 2)
        self.option_ctrl.fkIk >> invert_value.input1D[1]

        for ctrl in self.created_fk_ctrls:
            rig_lib.change_shape_color(ctrl, color_value)
            ctrl.setAttr("translateX", lock=True, keyable=False, channelBox=False)
            ctrl.setAttr("translateY", lock=True, keyable=False, channelBox=False)
            ctrl.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
            if ctrl != self.created_fk_ctrls[-1]:
                ctrl.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
                ctrl.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
                ctrl.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)
            ctrl_ofs = ctrl.getParent()
            ctrl_ofs.setAttr("translateX", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("translateY", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)

            invert_value.output1D >> ctrl.visibility

        self.created_ik_ctrls[1].setAttr("rotateX", lock=True, keyable=False, channelBox=False)
        self.created_ik_ctrls[1].setAttr("rotateY", lock=True, keyable=False, channelBox=False)
        self.created_ik_ctrls[1].setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
        self.created_ik_ctrls[1].setAttr("scaleX", lock=True, keyable=False, channelBox=False)
        self.created_ik_ctrls[1].setAttr("scaleY", lock=True, keyable=False, channelBox=False)
        self.created_ik_ctrls[1].setAttr("scaleZ", lock=True, keyable=False, channelBox=False)
        for ctrl in self.created_ik_ctrls:
            rig_lib.change_shape_color(ctrl, color_value)
            ctrl_ofs = ctrl.getParent()
            ctrl_ofs.setAttr("translateX", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("translateY", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
            ctrl_ofs.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)

            self.option_ctrl.fkIk >> ctrl.visibility

    def created_output(self):
        end_output = pmc.spaceLocator(p=(0, 0, 0), n="{0}_wrist_OUTPUT".format(self.model.module_name))
        pmc.parent(end_output, self.created_skn_jnts[-1], r=1)
        end_output.visibility.set(0)


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.side = "Left"
        self.ik_creation_switch = True
        self.stretch_creation_switch = True
        # self.bend_creation_switch = False
