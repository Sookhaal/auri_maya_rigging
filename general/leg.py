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
        self.raz_ctrls = QtWidgets.QCheckBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.ik_creation_switch.setChecked(self.model.ik_creation_switch)
        self.stretch_creation_switch.setChecked(self.model.stretch_creation_switch)
        self.raz_ctrls.setChecked(self.model.raz_ctrls)
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
        self.raz_ctrls.stateChanged.connect(self.ctrl.on_raz_ctrls_changed)

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
        raz_ctrls_layout = QtWidgets.QHBoxLayout()
        raz_ctrls_text = QtWidgets.QLabel("\"Freez\" ctrls :")
        raz_ctrls_layout.addWidget(raz_ctrls_text)
        raz_ctrls_layout.addWidget(self.raz_ctrls)

        checkbox_layout.addLayout(ik_layout)
        checkbox_layout.addLayout(stretch_layout)
        checkbox_layout.addLayout(raz_ctrls_layout)

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
        self.created_skn_jnts = []
        self.created_fk_jnts = []
        self.created_ik_jnts = []
        self.created_fk_ctrls = []
        self.created_ik_ctrls = []
        self.created_ik_handle = None
        self.option_ctrl = None
        RigController.__init__(self, model, view)

    def on_raz_ctrls_changed(self, state):
        self.model.raz_ctrls = is_checked(state)

    def prebuild(self):
        self.create_temporary_outputs(["ankle_OUTPUT"])

        self.guides_names = ["{0}_hip_GUIDE".format(self.model.module_name),
                             "{0}_knee_GUIDE".format(self.model.module_name),
                             "{0}_ankle_GUIDE".format(self.model.module_name)]

        self.side = {"Left": 1, "Right": -1}
        self.side_coef = self.side.get(self.model.side)

        if self.guide_check(self.guides_names):
            self.guides = pmc.ls("{0}_hip_GUIDE".format(self.model.module_name),
                                 "{0}_knee_GUIDE".format(self.model.module_name),
                                 "{0}_ankle_GUIDE".format(self.model.module_name))
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            return

        hip_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0])
        knee_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[1])
        ankle_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[2])

        hip_guide.setAttr("translate", (2 * self.side_coef, 7, 0))
        knee_guide.setAttr("translate", (2 * self.side_coef, 4, 0.0001))
        ankle_guide.setAttr("translate", (2 * self.side_coef, 1, 0))

        self.guides = [hip_guide, knee_guide, ankle_guide]
        self.guides_grp = self.group_guides(self.guides)
        self.guides_grp.setAttr("visibility", 1)
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
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
            self.connect_fk_stretch(self.created_fk_jnts, self.created_fk_ctrls)
            self.connect_ik_stretch(self.created_ik_jnts, self.created_ik_ctrls, self.side_coef,
                                    self.created_fk_ctrls[0].getParent(), self.created_ik_ctrls[0],
                                    self.created_fk_jnts[-1])
        self.clean_rig()
        self.create_output()
        pmc.select(d=1)

    def create_skn_jnts(self):
        duplicates_guides = []
        for guide in self.guides:
            duplicate = guide.duplicate(n="{0}_duplicate".format(guide))[0]
            duplicates_guides.append(duplicate)

        leg_plane = pmc.polyCreateFacet(p=[pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1),
                                           pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1),
                                           pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)],
                                        n="{0}_temporary_leg_plane".format(self.model.module_name), ch=1)[0]
        leg_plane_face = pmc.ls(leg_plane)[0].f[0]

        hip_const = pmc.normalConstraint(leg_plane_face, duplicates_guides[0], aimVector=(0.0, 0.0, 1.0),
                                         upVector=(1.0 * self.side_coef, 0.0, 0.0), worldUpType="object",
                                         worldUpObject=duplicates_guides[1])
        knee_cons = pmc.normalConstraint(leg_plane_face, duplicates_guides[1], aimVector=(0.0, 0.0, 1.0),
                                         upVector=(1.0 * self.side_coef, 0.0, 0.0), worldUpType="object",
                                         worldUpObject=duplicates_guides[2])
        pmc.delete(hip_const)
        pmc.delete(knee_cons)
        pmc.parent(duplicates_guides[1], duplicates_guides[0])
        pmc.parent(duplicates_guides[2], duplicates_guides[1])

        temp_guide_orient = pmc.group(em=1, n="temp_guide_orient_grp")
        temp_guide_orient.setAttr("translate", pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1))
        temp_guide_orient.setAttr("rotate", -90 * self.side_coef, 0, -90 * self.side_coef)
        pmc.parent(duplicates_guides[0], temp_guide_orient, r=0)
        pmc.select(d=1)

        hip_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1)),
                            n="{0}_hip_SKN".format(self.model.module_name))
        hip_jnt.setAttr("rotate", pmc.xform(duplicates_guides[0], q=1, rotation=1))
        hip_jnt.setAttr("jointOrientX", -90 * self.side_coef)
        hip_jnt.setAttr("jointOrientY", 0)
        hip_jnt.setAttr("jointOrientZ", -90 * self.side_coef)

        knee_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1)),
                             n="{0}_knee_SKN".format(self.model.module_name))
        knee_jnt.setAttr("rotate", pmc.xform(duplicates_guides[1], q=1, rotation=1))
        ankle_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)),
                              n="{0}_ankle_SKN".format(self.model.module_name))

        pmc.parent(hip_jnt, self.jnt_input_grp, r=0)
        self.created_skn_jnts = [hip_jnt, knee_jnt, ankle_jnt]

        pmc.delete(temp_guide_orient)
        pmc.delete(leg_plane)

    def create_options_ctrl(self):
        self.option_ctrl = rig_lib.little_cube("{0}_option_CTRL".format(self.model.module_name))
        option_ofs = pmc.group(self.option_ctrl, n="{0}_option_ctrl_OFS".format(self.model.module_name), r=1)
        pmc.parent(option_ofs, self.ctrl_input_grp)
        rig_lib.matrix_constraint(self.created_skn_jnts[-1], option_ofs, srt="trs")
        ctrl_shape = self.option_ctrl.getShape()
        pmc.move(ctrl_shape, [0, 0, 3 * self.side_coef], relative=1, objectSpace=1, worldSpaceDistance=1)
        self.option_ctrl.addAttr("fkIk", attributeType="float", defaultValue=0, hidden=0, keyable=1, hasMaxValue=1,
                                 hasMinValue=1, maxValue=1, minValue=0)

    def create_and_connect_fk_ik_jnts(self):
        hip_fk_jnt = \
            self.created_skn_jnts[0].duplicate(n="{0}_hip_fk_JNT".format(self.model.module_name))[0]
        knee_fk_jnt = pmc.ls("{0}_hip_fk_JNT|{0}_knee_SKN".format(self.model.module_name))[0]
        ankle_fk_jnt = pmc.ls("{0}_hip_fk_JNT|{0}_knee_SKN|{0}_ankle_SKN".format(self.model.module_name))[0]
        knee_fk_jnt.rename("{0}_knee_fk_JNT".format(self.model.module_name))
        ankle_fk_jnt.rename("{0}_ankle_fk_JNT".format(self.model.module_name))
        self.created_fk_jnts = [hip_fk_jnt, knee_fk_jnt, ankle_fk_jnt]

        hip_ik_jnt = self.created_skn_jnts[0].duplicate(n="{0}_hip_ik_JNT".format(self.model.module_name))[0]
        knee_ik_jnt = pmc.ls("{0}_hip_ik_JNT|{0}_knee_SKN".format(self.model.module_name))[0]
        ankle_ik_jnt = pmc.ls("{0}_hip_ik_JNT|{0}_knee_SKN|{0}_ankle_SKN".format(self.model.module_name))[0]
        knee_ik_jnt.rename("{0}_knee_ik_JNT".format(self.model.module_name))
        ankle_ik_jnt.rename("{0}_ankle_ik_JNT".format(self.model.module_name))
        self.created_ik_jnts = [hip_ik_jnt, knee_ik_jnt, ankle_ik_jnt]

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
        hip_ctrl = pmc.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=2, d=3, s=8,
                              n="{0}_hip_fk_CTRL".format(self.model.module_name), ch=0)[0]
        hip_ofs = pmc.group(hip_ctrl, n="{0}_hip_fk_ctrl_OFS".format(self.model.module_name))
        hip_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[0], q=1, ws=1, translation=1))
        hip_ofs.setAttr("rotateX", -90 * self.side_coef)
        hip_ofs.setAttr("rotateY", 0)
        hip_ofs.setAttr("rotateZ", -90 * self.side_coef)

        hip_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[0], q=1, rotation=1))
        hip_ctrl.setAttr("rotateOrder", 0)
        pmc.parent(hip_ofs, self.ctrl_input_grp, r=0)

        knee_ctrl = pmc.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=2, d=3, s=8,
                               n="{0}_knee_fk_CTRL".format(self.model.module_name), ch=0)[0]
        knee_ofs = pmc.group(knee_ctrl,
                             n="{0}_knee_fk_ctrl_OFS".format(self.model.module_name))
        knee_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1))
        knee_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[1], q=1, rotation=1))
        knee_ctrl.setAttr("rotateOrder", 0)
        pmc.parent(knee_ofs, hip_ctrl, r=0)
        knee_ofs.setAttr("rotate", (0, 0, 0))

        ankle_ctrl = pmc.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=2, d=3, s=8,
                                n="{0}_ankle_fk_CTRL".format(self.model.module_name), ch=0)[0]
        ankle_ofs = pmc.group(ankle_ctrl,
                              n="{0}_ankle_fk_ctrl_OFS".format(self.model.module_name))
        ankle_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[2], q=1, ws=1, translation=1))
        ankle_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[2], q=1, rotation=1))
        ankle_ctrl.setAttr("rotateOrder", 0)
        pmc.parent(ankle_ofs, knee_ctrl, r=0)
        ankle_ofs.setAttr("rotate", (0, 0, 0))

        self.created_fk_ctrls = [hip_ctrl, knee_ctrl, ankle_ctrl]

        for i, ctrl in enumerate(self.created_fk_ctrls):
            ctrl.rotate >> self.created_fk_jnts[i].rotate
            if ctrl == self.created_fk_ctrls[-1]:
                ctrl.scale >> self.created_fk_jnts[i].scale

    def create_ik(self):
        self.created_ik_handle = pmc.ikHandle(n=("{0}_ik_HDL".format(self.model.module_name)),
                                 startJoint=self.created_ik_jnts[0], endEffector=self.created_ik_jnts[-1],
                                 solver="ikRPsolver")[0]
        ik_effector = pmc.listRelatives(self.created_ik_jnts[-2], children=1)[1]
        ik_effector.rename("{0}_ik_EFF".format(self.model.module_name))

        ik_ctrl = rig_lib.medium_cube("{0}_ankle_ik_CTRL".format(self.model.module_name))
        ik_ctrl_ofs = pmc.group(ik_ctrl, n="{0}_ankle_ik_ctrl_OFS".format(self.model.module_name))

        fk_ctrl_01_value = pmc.xform(self.created_fk_ctrls[0], q=1, rotation=1)
        fk_ctrl_02_value = pmc.xform(self.created_fk_ctrls[1], q=1, rotation=1)
        fk_ctrl_03_value = pmc.xform(self.created_fk_ctrls[2], q=1, rotation=1)
        self.created_fk_ctrls[0].setAttr("rotate", (0, 0, 0))
        self.created_fk_ctrls[1].setAttr("rotate", (0, 0, 0))
        self.created_fk_ctrls[2].setAttr("rotate", (0, 0, 0))

        ik_ctrl_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[2], q=1, ws=1, translation=1))
        pmc.parent(self.created_ik_handle, ik_ctrl_ofs, r=0)
        ik_ctrl.setAttr("translate", pmc.xform(self.created_ik_handle, q=1, translation=1))
        pmc.parent(self.created_ik_handle, ik_ctrl, r=0)
        pmc.parent(ik_ctrl_ofs, self.ctrl_input_grp)

        pole_vector = rig_lib.jnt_shape_curve("{0}_poleVector_CTRL".format(self.model.module_name))
        pv_ofs = pmc.group(pole_vector, n="{0}_poleVector_ctrl_OFS".format(self.model.module_name))
        pv_ofs.setAttr("translate", (pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[0],
                                     pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[1],
                                     pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[2] + (
                                         (pmc.xform(self.created_fk_jnts[1], q=1, translation=1)[
                                              0]) * self.side_coef)))
        pmc.poleVectorConstraint(pole_vector, self.created_ik_handle)
        pmc.parent(pv_ofs, self.ctrl_input_grp, r=0)

        self.created_ik_jnts[1].setAttr("preferredAngleZ", 90)

        self.created_ik_ctrls = [ik_ctrl, pole_vector]

        self.created_fk_ctrls[0].setAttr("rotate", fk_ctrl_01_value)
        self.created_fk_ctrls[1].setAttr("rotate", fk_ctrl_02_value)
        self.created_fk_ctrls[2].setAttr("rotate", fk_ctrl_03_value)

        pmc.xform(pole_vector, ws=1, translation=(pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)))

        self.created_ik_handle.setAttr("visibility", 0)

        pmc.xform(ik_ctrl, ws=1, translation=(pmc.xform(self.created_fk_jnts[-1], q=1, ws=1, translation=1)))

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        if self.model.side == "Left":
            color_value = 6
        else:
            color_value = 13

        rig_lib.clean_ctrl(self.option_ctrl, 9, trs="trs")
        self.option_ctrl.setAttr("fkIk", 1)

        if self.model.raz_ctrls:
            for i, ctrl in enumerate(self.created_fk_ctrls):
                rig_lib.raz_fk_ctrl_rotate(ctrl, self.created_fk_jnts[i])

            rig_lib.raz_ik_ctrl_translate_rotate(self.created_ik_ctrls[0])

        invert_value = pmc.createNode("plusMinusAverage", n="{0}_fk_visibility_MDL".format(self.model.module_name))
        invert_value.setAttr("input1D[0]", 1)
        invert_value.setAttr("operation", 2)
        self.option_ctrl.fkIk >> invert_value.input1D[1]

        for ctrl in self.created_fk_ctrls:
            if ctrl == self.created_fk_ctrls[-1]:
                rig_lib.clean_ctrl(ctrl, color_value, trs="t", visibility_dependence=invert_value.output1D)
            else:
                rig_lib.clean_ctrl(ctrl, color_value, trs="ts", visibility_dependence=invert_value.output1D)

        rig_lib.clean_ctrl(self.created_ik_ctrls[0], color_value, trs="", visibility_dependence=self.option_ctrl.fkIk)
        rig_lib.clean_ctrl(self.created_ik_ctrls[1], color_value, trs="rs", visibility_dependence=self.option_ctrl.fkIk)

    def create_output(self):
        rig_lib.create_output(name="{0}_ankle_OUTPUT".format(self.model.module_name), parent=self.created_skn_jnts[-1])


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.side = "Left"
        self.ik_creation_switch = True
        self.stretch_creation_switch = True
        self.raz_ctrls = True
        # self.bend_creation_switch = False
