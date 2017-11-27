from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial

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
        self.fk_ik_type_cbbox = QtWidgets.QComboBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.side_cbbox.setCurrentText(self.model.side)
        self.fk_ik_type_cbbox.setCurrentText(self.model.fk_ik_type)
        self.ctrl.look_for_parent()

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        self.side_cbbox.insertItems(0, ["Left", "Right"])
        self.side_cbbox.currentTextChanged.connect(self.ctrl.on_side_cbbox_changed)

        self.fk_ik_type_cbbox.insertItems(0, ["one_chain", "three_chains"])
        self.fk_ik_type_cbbox.currentTextChanged.connect(self.ctrl.on_fk_ik_type_changed)

        self.refresh_btn.clicked.connect(self.ctrl.look_for_parent)
        self.prebuild_btn.clicked.connect(self.ctrl.prebuild)

        main_layout = QtWidgets.QVBoxLayout()

        select_parent_and_object_layout = QtWidgets.QVBoxLayout()

        select_parent_layout = QtWidgets.QVBoxLayout()
        select_parent_grp = grpbox("Select parent", select_parent_layout)
        parent_cbbox_layout = QtWidgets.QHBoxLayout()
        parent_cbbox_layout.addWidget(self.modules_cbbox)
        parent_cbbox_layout.addWidget(self.outputs_cbbox)

        select_parent_layout.addLayout(parent_cbbox_layout)
        select_parent_and_object_layout.addWidget(select_parent_grp)
        select_parent_and_object_layout.addWidget(self.refresh_btn)

        side_layout = QtWidgets.QVBoxLayout()
        side_grp = grpbox("Side", side_layout)
        side_layout.addWidget(self.side_cbbox)

        chain_type_layout = QtWidgets.QVBoxLayout()
        chain_type_grp = grpbox("Fk/Ik chain type", chain_type_layout)
        chain_type_layout.addWidget(self.fk_ik_type_cbbox)

        main_layout.addLayout(select_parent_and_object_layout)
        main_layout.addWidget(side_grp)
        main_layout.addWidget(chain_type_grp)
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
        self.leg_ik_ctrl = None
        self.leg_ik_handle = None
        self.leg_ankle_rotation_handle = None
        self.leg_ik_length_end_loc = None
        self.leg_option_ctrl = None
        self.created_skn_jnts = []
        self.created_locs = []
        self.created_fk_jnts = []
        self.created_ik_jnts = []
        self.created_ctrtl_jnts = []
        self.toes_ctrl = None
        self.jnts_to_skin = []
        RigController.__init__(self, model, view)

    def prebuild(self):
        self.guides_names = ["{0}_ankle_GUIDE".format(self.model.module_name), "{0}_ball_GUIDE".format(self.model.module_name),
                             "{0}_toe_GUIDE".format(self.model.module_name), "{0}_heel_GUIDE".format(self.model.module_name),
                             "{0}_infoot_GUIDE".format(self.model.module_name), "{0}_outfoot_GUIDE".format(self.model.module_name)]

        self.side = {"Left": 1, "Right": -1}
        self.side_coef = self.side.get(self.model.side)

        if self.guide_check(self.guides_names):
            self.guides = pmc.ls(self.guides_names)
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            self.guides_grp.setAttr("visibility", 1)
            self.view.refresh_view()
            pmc.select(d=1)
            return

        ankle_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0])
        ball_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[1])
        toe_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[2])
        heel_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[3])
        infoot_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[4])
        outfoot_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[5])

        ankle_guide.setAttr("translate", (2 * self.side_coef, 1, 0))
        ball_guide.setAttr("translate", (2 * self.side_coef, 0.5, 1.5))
        toe_guide.setAttr("translate", (2 * self.side_coef, 0, 3))
        heel_guide.setAttr("translate", (2 * self.side_coef, 0, -1))
        infoot_guide.setAttr("translate", (1 * self.side_coef, 0, 1))
        outfoot_guide.setAttr("translate", (3 * self.side_coef, 0, 1))

        self.guides = [ankle_guide, ball_guide, toe_guide, heel_guide, infoot_guide, outfoot_guide]
        self.guides_grp = self.group_guides(self.guides)
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()

        self.get_parent_ik_objects()

        self.create_skn_jnts_and_locs()

        if self.model.fk_ik_type == "three_chains":
            self.create_and_connect_fk_ik_jnts()
            self.create_fk()
            self.create_ik_and_roll()

        if self.model.fk_ik_type == "one_chain":
            self.create_and_connect_ctrl_jnts()
            self.create_one_chain_fk()
            self.create_one_chain_ik_and_roll()

        self.clean_rig()
        pmc.select(d=1)

    def get_parent_ik_objects(self):
        self.leg_ik_ctrl = pmc.ls("{0}_ankle_ik_CTRL".format(self.model.selected_module))[0]
        self.leg_ik_handle = pmc.ls("{0}_ik_HDL".format(self.model.selected_module))[0]
        if pmc.objExists("{0}_ankle_rotation_ik_HDL".format(self.model.selected_module)):
            self.leg_ankle_rotation_handle = pmc.ls("{0}_ankle_rotation_ik_HDL".format(self.model.selected_module))[0]
        self.leg_option_ctrl = pmc.ls("{0}_option_CTRL".format(self.model.selected_module))[0]
        self.leg_ik_length_end_loc = pmc.ls("{0}_ik_length_end_LOC".format(self.model.selected_module))[0]

    def create_skn_jnts_and_locs(self):
        duplicates_guides = []
        for guide in self.guides:
            duplicate = guide.duplicate(n="{0}_duplicate".format(guide))[0]
            duplicates_guides.append(duplicate)

        duplicates_guides[0].setAttr("rotateOrder", 4)
        duplicates_guides[1].setAttr("rotateOrder", 4)
        duplicates_guides[2].setAttr("rotateOrder", 4)

        ankle_const = pmc.aimConstraint(duplicates_guides[1], duplicates_guides[0], maintainOffset=0,
                                        aimVector=(0.0, 1.0 * self.side_coef, 0.0),
                                        upVector=(0.0, 0.0, 1.0 * self.side_coef), worldUpType="scene")
        ball_cons = pmc.aimConstraint(duplicates_guides[2], duplicates_guides[1], maintainOffset=0,
                                      aimVector=(0.0, 1.0 * self.side_coef, 0.0),
                                      upVector=(0.0, 0.0, 1.0 * self.side_coef), worldUpType="scene")

        pmc.delete(ankle_const)
        pmc.delete(ball_cons)
        pmc.parent(duplicates_guides[1], duplicates_guides[0])
        pmc.parent(duplicates_guides[2], duplicates_guides[1])

        temp_guide_orient = pmc.group(em=1, n="temp_guide_orient_grp")
        temp_guide_orient.setAttr("translate", pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1))
        temp_guide_orient.setAttr("rotateOrder", 4)
        temp_guide_orient.setAttr("rotate", 0, 90 * (1 - self.side_coef), 90 * (1 + self.side_coef))
        pmc.parent(duplicates_guides[0], temp_guide_orient, r=0)
        pmc.select(d=1)

        ankle_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1)),
                              n="{0}_foot_SKN".format(self.model.module_name))
        ankle_jnt.setAttr("rotateOrder", 4)
        ankle_jnt.setAttr("jointOrient", 0, 90 * (1 - self.side_coef), 90 * (1 + self.side_coef))
        ankle_jnt.setAttr("rotate", pmc.xform(duplicates_guides[0], q=1, rotation=1))

        ball_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1)),
                             n="{0}_toes_SKN".format(self.model.module_name))
        ball_jnt.setAttr("rotateOrder", 4)
        ball_jnt.setAttr("rotate", pmc.xform(duplicates_guides[1], q=1, rotation=1))
        toe_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)),
                            n="{0}_toes_end_JNT".format(self.model.module_name))
        toe_jnt.setAttr("rotateOrder", 4)

        pmc.parent(ankle_jnt, self.jnt_input_grp, r=0)
        self.created_skn_jnts = [ankle_jnt, ball_jnt, toe_jnt]

        ball_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ball_LOC".format(self.model.module_name))
        toe_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_toe_LOC".format(self.model.module_name))
        heel_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_heel_LOC".format(self.model.module_name))
        infoot_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_infoot_LOC".format(self.model.module_name))
        infoot_loc.setAttr("rotateOrder", 2)
        outfoot_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_outfoot_LOC".format(self.model.module_name))
        outfoot_loc.setAttr("rotateOrder", 2)

        ball_loc.setAttr("translate", pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1))
        toe_loc.setAttr("translate", pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1))
        heel_loc.setAttr("translate", pmc.xform(duplicates_guides[3], q=1, ws=1, translation=1))
        heel_loc.setAttr("rotateY", pmc.xform(duplicates_guides[3], q=1, ws=1, rotation=1)[1])
        infoot_loc.setAttr("translate", pmc.xform(duplicates_guides[4], q=1, ws=1, translation=1))
        infoot_loc.setAttr("rotateY", pmc.xform(duplicates_guides[4], q=1, ws=1, rotation=1)[1])
        outfoot_loc.setAttr("translate", pmc.xform(duplicates_guides[5], q=1, ws=1, translation=1))
        outfoot_loc.setAttr("rotateY", pmc.xform(duplicates_guides[5], q=1, ws=1, rotation=1)[1])

        pmc.parent(heel_loc, self.ctrl_input_grp)
        pmc.parent(outfoot_loc, heel_loc)
        pmc.parent(infoot_loc, outfoot_loc)
        pmc.parent(toe_loc, infoot_loc)
        pmc.parent(ball_loc, toe_loc)

        self.created_locs = [ball_loc, toe_loc, heel_loc, infoot_loc, outfoot_loc]

        pmc.delete(duplicates_guides[:])
        pmc.delete(temp_guide_orient)

        self.jnts_to_skin = self.created_skn_jnts[:-1]

    def create_and_connect_fk_ik_jnts(self):
        ankle_fk_jnt = self.created_skn_jnts[0].duplicate(n="{0}_ankle_fk_JNT".format(self.model.module_name))[0]
        ball_fk_jnt = pmc.ls("{0}_ankle_fk_JNT|{0}_toes_SKN".format(self.model.module_name))[0]
        toe_fk_jnt = pmc.ls("{0}_ankle_fk_JNT|{0}_toes_SKN|{0}_toes_end_JNT".format(self.model.module_name))[0]
        ball_fk_jnt.rename("{0}_toes_fk_JNT".format(self.model.module_name))
        toe_fk_jnt.rename("{0}_toes_end_fk_JNT".format(self.model.module_name))
        self.created_fk_jnts = [ankle_fk_jnt, ball_fk_jnt, toe_fk_jnt]

        ankle_ik_jnt = self.created_skn_jnts[0].duplicate(n="{0}_ankle_ik_JNT".format(self.model.module_name))[0]
        ball_ik_jnt = pmc.ls("{0}_ankle_ik_JNT|{0}_toes_SKN".format(self.model.module_name))[0]
        toe_ik_jnt = pmc.ls("{0}_ankle_ik_JNT|{0}_toes_SKN|{0}_toes_end_JNT".format(self.model.module_name))[0]
        ball_ik_jnt.rename("{0}_toes_ik_JNT".format(self.model.module_name))
        toe_ik_jnt.rename("{0}_toes_end_ik_JNT".format(self.model.module_name))
        self.created_ik_jnts = [ankle_ik_jnt, ball_ik_jnt, toe_ik_jnt]

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
            self.leg_option_ctrl.fkIk >> pair_blend.weight
            self.leg_option_ctrl.fkIk >> blend_color.blender

    def create_fk(self):
        toes_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=1, d=3, s=8,
                                n="{0}_toes_fk_CTRL_shape".format(self.model.module_name), ch=0)[0]
        self.toes_ctrl = rig_lib.create_jnttype_ctrl("{0}_toes_fk_CTRL".format(self.model.module_name), toes_shape,
                                                     drawstyle=2, rotateorder=4)
        self.toes_ctrl.setAttr("translate", pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1))
        self.toes_ctrl.setAttr("jointOrient", (90, 90 * (1 - self.side_coef), 90 * (1 + self.side_coef)))
        pmc.parent(self.toes_ctrl, self.ctrl_input_grp, r=0)

        self.toes_ctrl.addAttr("jntRotateOffsetX", attributeType="float",
                               defaultValue=self.created_fk_jnts[1].getAttr("rotateX"), hidden=0, keyable=0)
        self.toes_ctrl.addAttr("jntRotateOffsetY", attributeType="float",
                               defaultValue=self.created_fk_jnts[1].getAttr("rotateY"), hidden=0, keyable=0)
        self.toes_ctrl.addAttr("jntRotateOffsetZ", attributeType="float",
                               defaultValue=self.created_fk_jnts[1].getAttr("rotateZ"), hidden=0, keyable=0)
        jnt_offset = pmc.createNode("plusMinusAverage", n="{0}_ball_jnt_offset_PMA".format(self.created_fk_jnts[1]))
        jnt_offset.setAttr("operation", 1)
        self.toes_ctrl.rotate >> jnt_offset.input3D[0]
        self.toes_ctrl.jntRotateOffsetX >> jnt_offset.input3D[1].input3Dx
        self.toes_ctrl.jntRotateOffsetY >> jnt_offset.input3D[1].input3Dy
        self.toes_ctrl.jntRotateOffsetZ >> jnt_offset.input3D[1].input3Dz
        jnt_offset.output3D >> self.created_fk_jnts[1].rotate

    def create_ik_and_roll(self):
        toe_ik_handle = pmc.ikHandle(n=("{0}_toe_ik_HDL".format(self.model.module_name)),
                                     startJoint=self.created_ik_jnts[1], endEffector=self.created_ik_jnts[2],
                                     solver="ikSCsolver")[0]
        ik_effector = pmc.listRelatives(self.created_ik_jnts[1], children=1)[1]
        ik_effector.rename("{0}_toe_ik_EFF".format(self.model.module_name))
        ball_ik_handle = pmc.ikHandle(n=("{0}_ball_ik_HDL".format(self.model.module_name)),
                                      startJoint=self.created_ik_jnts[0], endEffector=self.created_ik_jnts[1],
                                      solver="ikSCsolver")[0]
        ik_effector = pmc.listRelatives(self.created_ik_jnts[0], children=1)[1]
        ik_effector.rename("{0}_ball_ik_EFF".format(self.model.module_name))

        pmc.parent(self.leg_ik_handle, world=1)
        if self.leg_ankle_rotation_handle is not None:
            pmc.parent(self.leg_ankle_rotation_handle, world=1)
        pmc.parent(self.leg_ik_length_end_loc, world=1)
        if pmc.objExists("{0}_roll_OFS".format(self.model.module_name)):
            pmc.delete("{0}_roll_OFS".format(self.model.module_name))
        locs_offset = pmc.group(em=1, n="{0}_roll_OFS".format(self.model.module_name))
        locs_offset.setAttr("translate", pmc.xform(self.created_skn_jnts[0], q=1, ws=1, translation=1))
        locs_offset.setAttr("rotateOrder", 4)
        pmc.parent(locs_offset, self.leg_ik_ctrl, r=0)
        toe_bend_group = pmc.group(em=1, n="{0}_toe_bend_OFS".format(self.model.module_name))
        toe_bend_group.setAttr("translate", pmc.xform(self.created_locs[0], q=1, ws=1, translation=1))
        pmc.parent(ball_ik_handle, self.created_locs[0], r=0)
        pmc.parent(toe_bend_group, self.created_locs[1], r=0)
        pmc.parent(toe_ik_handle, toe_bend_group, r=0)
        pmc.parent(self.created_locs[2], locs_offset, r=0)
        pmc.parent(self.leg_ik_handle, self.created_locs[0], r=0)
        if self.leg_ankle_rotation_handle is not None:
            pmc.parent(self.leg_ankle_rotation_handle, self.created_locs[0], r=0)
        pmc.parent(self.leg_ik_length_end_loc, self.created_locs[0], r=0)

        if "roll" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("roll")
        self.leg_ik_ctrl.addAttr("roll", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "bendLimitAngle" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("bendLimitAngle")
        self.leg_ik_ctrl.addAttr("bendLimitAngle", attributeType="float", defaultValue=45, hidden=0, keyable=1)
        if "toeStraightAngle" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("toeStraightAngle")
        self.leg_ik_ctrl.addAttr("toeStraightAngle", attributeType="float", defaultValue=70, hidden=0, keyable=1)
        if "bank" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("bank")
        self.leg_ik_ctrl.addAttr("bank", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "lean" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("lean")
        self.leg_ik_ctrl.addAttr("lean", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "heelTwist" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("heelTwist")
        self.leg_ik_ctrl.addAttr("heelTwist", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "toeTwist" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("toeTwist")
        self.leg_ik_ctrl.addAttr("toeTwist", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "toeBend" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("toeBend")
        self.leg_ik_ctrl.addAttr("toeBend", attributeType="float", defaultValue=0, hidden=0, keyable=1)

        roll_heel_limit = pmc.createNode("clamp", n="{0}_heel_CLAMP".format(self.model.module_name))
        roll_zerotobend_limit = pmc.createNode("clamp", n="{0}_zero_to_bend_CLAMP".format(self.model.module_name))
        roll_zerotobend_percent = pmc.createNode("setRange", n="{0}_zero_to_bend_percent_RANGE".format(self.model.module_name))
        roll_bendtostraight_limit = pmc.createNode("clamp", n="{0}_bend_to_straight_CLAMP".format(self.model.module_name))
        roll_bendtostraight_percent = pmc.createNode("setRange", n="{0}_bend_to_straight_percent_RANGE".format(self.model.module_name))
        roll_toe_mult = pmc.createNode("multiplyDivide", n="{0}_toe_roll_mult_MDV".format(self.model.module_name))
        roll_bendtostraight_invertpercent = pmc.createNode("plusMinusAverage", n="{0}_invert_percent_RANGE".format(self.model.module_name))
        roll_ball_percent_mult = pmc.createNode("multiplyDivide", n="{0}_ball_percent_mult_MDV".format(self.model.module_name))
        roll_ball_mult = pmc.createNode("multiplyDivide", n="{0}_ball_roll_mult_MDV".format(self.model.module_name))

        roll_heel_limit.setAttr("minR", -90)
        roll_heel_limit.setAttr("maxR", 0)
        self.leg_ik_ctrl.roll >> roll_heel_limit.inputR
        roll_heel_limit.outputR >> self.created_locs[2].rotateX

        self.leg_ik_ctrl.bendLimitAngle >> roll_bendtostraight_limit.minR
        self.leg_ik_ctrl.toeStraightAngle >> roll_bendtostraight_limit.maxR
        self.leg_ik_ctrl.roll >> roll_bendtostraight_limit.inputR

        roll_bendtostraight_percent.setAttr("minX", 0)
        roll_bendtostraight_percent.setAttr("maxX", 1)
        roll_bendtostraight_limit.inputR >> roll_bendtostraight_percent.valueX
        roll_bendtostraight_limit.minR >> roll_bendtostraight_percent.oldMinX
        roll_bendtostraight_limit.maxR >> roll_bendtostraight_percent.oldMaxX

        roll_toe_mult.setAttr("operation", 1)
        roll_bendtostraight_percent.outValueX >> roll_toe_mult.input1X
        roll_bendtostraight_limit.inputR >> roll_toe_mult.input2X
        roll_toe_mult.outputX >> self.created_locs[1].rotateX

        roll_bendtostraight_invertpercent.setAttr("operation", 2)
        roll_bendtostraight_invertpercent.setAttr("input1D[0]", 1)
        roll_bendtostraight_percent.outValueX >> roll_bendtostraight_invertpercent.input1D[1]

        roll_zerotobend_limit.setAttr("minR", 0)
        self.leg_ik_ctrl.bendLimitAngle >> roll_zerotobend_limit.maxR
        self.leg_ik_ctrl.roll >> roll_zerotobend_limit.inputR

        roll_zerotobend_percent.setAttr("minX", 0)
        roll_zerotobend_percent.setAttr("maxX", 1)
        roll_zerotobend_limit.inputR >> roll_zerotobend_percent.valueX
        roll_zerotobend_limit.minR >> roll_zerotobend_percent.oldMinX
        roll_zerotobend_limit.maxR >> roll_zerotobend_percent.oldMaxX

        roll_ball_percent_mult.setAttr("operation", 1)
        roll_zerotobend_percent.outValueX >> roll_ball_percent_mult.input1X
        roll_bendtostraight_invertpercent.output1D >> roll_ball_percent_mult.input2X

        roll_ball_mult.setAttr("operation", 1)
        roll_ball_percent_mult.outputX >> roll_ball_mult.input1X
        self.leg_ik_ctrl.roll >> roll_ball_mult.input2X
        roll_ball_mult.outputX >> self.created_locs[0].rotateX

        self.leg_ik_ctrl.toeBend >> toe_bend_group.rotateX

        heel_offset = pmc.createNode("plusMinusAverage", n="{0}_heeltwist_offset_PMA".format(self.created_locs[2]))
        heel_offset.setAttr("operation", 1)
        heel_offset.setAttr("input1D[0]", self.created_locs[2].getAttr("rotateY"))
        self.leg_ik_ctrl.heelTwist >> heel_offset.input1D[1]
        heel_offset.output1D >> self.created_locs[2].rotateY

        toe_offset = pmc.createNode("plusMinusAverage", n="{0}_toetwist_offset_PMA".format(self.created_locs[1]))
        toe_offset.setAttr("operation", 1)
        toe_offset.setAttr("input1D[0]", self.created_locs[1].getAttr("rotateY"))
        self.leg_ik_ctrl.toeTwist >> toe_offset.input1D[1]
        toe_offset.output1D >> self.created_locs[1].rotateY

        self.leg_ik_ctrl.lean >> self.created_locs[0].rotateZ

        bank_in_limit = pmc.createNode("clamp", n="{0}_bank_in_CLAMP".format(self.model.module_name))
        bank_out_limit = pmc.createNode("clamp", n="{0}_bank_out_CLAMP".format(self.model.module_name))

        if self.model.side == "Right":
            bank_in_limit.setAttr("minR", -90)
            bank_in_limit.setAttr("maxR", 0)
            self.leg_ik_ctrl.bank >> bank_in_limit.inputR
            bank_in_limit.outputR >> self.created_locs[3].rotateZ
            bank_out_limit.setAttr("minR", 0)
            bank_out_limit.setAttr("maxR", 90)
            self.leg_ik_ctrl.bank >> bank_out_limit.inputR
            bank_out_limit.outputR >> self.created_locs[4].rotateZ
        else:
            bank_invert = pmc.createNode("multiplyDivide", n="{0}_bank_invert_value_MDV".format(self.model.module_name))
            bank_invert.setAttr("input2X", -1)
            self.leg_ik_ctrl.bank >> bank_invert.input1X
            bank_in_limit.setAttr("minR", 0)
            bank_in_limit.setAttr("maxR", 90)
            bank_invert.outputX >> bank_in_limit.inputR
            bank_in_limit.outputR >> self.created_locs[3].rotateZ
            bank_out_limit.setAttr("minR", -90)
            bank_out_limit.setAttr("maxR", 0)
            bank_invert.outputX >> bank_out_limit.inputR
            bank_out_limit.outputR >> self.created_locs[4].rotateZ

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        if self.model.side == "Left":
            color_value = 6
        else:
            color_value = 13

        if self.model.fk_ik_type == "three_chains":
            fk_visibility_ctrl = pmc.ls("{0}_fk_visibility_MDL".format(self.model.selected_module))[0]
            rig_lib.clean_ctrl(self.toes_ctrl, color_value, trs="t", visibility_dependence=fk_visibility_ctrl.output1D)

        if self.model.fk_ik_type == "one_chain":
            fk_visibility_ctrl = pmc.ls("{0}_fk_visibility_MDL".format(self.model.selected_module))[0]
            rig_lib.clean_ctrl(self.created_ctrtl_jnts[1], color_value, trs="t",
                               visibility_dependence=fk_visibility_ctrl.output1D)

            self.created_ctrtl_jnts[0].setAttr("drawStyle", 2)
            self.created_ctrtl_jnts[2].setAttr("drawStyle", 2)

        self.created_locs[2].setAttr("visibility", 0)

        info_crv = rig_lib.signature_shape_curve("{0}_INFO".format(self.model.module_name))
        info_crv.getShape().setAttr("visibility", 0)
        info_crv.setAttr("hiddenInOutliner", 1)
        info_crv.setAttr("translateX", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("translateY", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("visibility", lock=True, keyable=False, channelBox=False)
        info_crv.setAttr("overrideEnabled", 1)
        info_crv.setAttr("overrideDisplayType", 2)
        pmc.parent(info_crv, self.parts_grp)

        rig_lib.add_parameter_as_extra_attr(info_crv, "parent_Module", self.model.selected_module)
        rig_lib.add_parameter_as_extra_attr(info_crv, "parent_output", self.model.selected_output)
        rig_lib.add_parameter_as_extra_attr(info_crv, "side", self.model.side)
        rig_lib.add_parameter_as_extra_attr(info_crv, "fk_ik_type", self.model.fk_ik_type)

        if not pmc.objExists("jnts_to_SKN_SET"):
            skn_set = pmc.createNode("objectSet", n="jnts_to_SKN_SET")
        else:
            skn_set = pmc.ls("jnts_to_SKN_SET", type="objectSet")[0]
        for jnt in self.jnts_to_skin:
            if type(jnt) == list:
                for obj in jnt:
                    skn_set.add(obj)
            else:
                skn_set.add(jnt)

    def create_and_connect_ctrl_jnts(self):
        ankle_ctrl_jnt = self.created_skn_jnts[0].duplicate(n="{0}_ankle_ctrl_JNT".format(self.model.module_name))[0]
        ball_ctrl_jnt = pmc.ls("{0}_ankle_ctrl_JNT|{0}_toes_SKN".format(self.model.module_name))[0]
        toe_ctrl_jnt = pmc.ls("{0}_ankle_ctrl_JNT|{0}_toes_SKN|{0}_toes_end_JNT".format(self.model.module_name))[0]
        ball_ctrl_jnt.rename("{0}_toes_ctrl_JNT".format(self.model.module_name))
        toe_ctrl_jnt.rename("{0}_toes_end_ctrl_JNT".format(self.model.module_name))

        self.created_ctrtl_jnts = [ankle_ctrl_jnt, ball_ctrl_jnt, toe_ctrl_jnt]

        pmc.parent(ankle_ctrl_jnt, self.ctrl_input_grp, r=0)

        for i, skn_jnt in enumerate(self.created_skn_jnts):
            self.created_ctrtl_jnts[i].translate >> skn_jnt.translate
            self.created_ctrtl_jnts[i].jointOrient >> skn_jnt.jointOrient
            self.created_ctrtl_jnts[i].rotate >> skn_jnt.rotate
            self.created_ctrtl_jnts[i].scale >> skn_jnt.scale

    def create_one_chain_fk(self):
        toes_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=1, d=3, s=8,
                                n="{0}_toes_fk_CTRL_shape".format(self.model.module_name), ch=0)[0]
        pmc.parent(toes_shape.getShape(), self.created_ctrtl_jnts[1], r=1, s=1)
        self.created_ctrtl_jnts[1].rename("{0}_toes_fk_CTRL".format(self.model.module_name))
        self.created_ctrtl_jnts[1].getShape().rename("{0}Shape".format(self.created_ctrtl_jnts[1]))
        self.created_ctrtl_jnts[1].setAttr("radius", 0)
        pmc.delete(toes_shape)

        loc = pmc.spaceLocator(p=(0, 0, 0), n="toe_jnt_rotation_temp_loc")
        pmc.parent(loc, self.created_ctrtl_jnts[1], r=1)
        pmc.parent(loc, self.created_ctrtl_jnts[0], r=0)
        self.created_ctrtl_jnts[1].setAttr("jointOrient", loc.getAttr("rotate"))
        self.created_ctrtl_jnts[1].setAttr("rotate", (0, 0, 0))
        pmc.delete(loc)

        ctrl_cvs = self.created_ctrtl_jnts[1].getShape().cv[:]
        for i, cv in enumerate(ctrl_cvs):
            pmc.xform(self.created_ctrtl_jnts[1].getShape().controlPoints[i], ws=1,
                      translation=(pmc.xform(cv, q=1, ws=1, translation=1)[0],
                      pmc.xform(cv, q=1, ws=1, translation=1)[1],
                      pmc.xform(self.created_ctrtl_jnts[1], q=1, ws=1, translation=1)[2]))

    def create_one_chain_ik_and_roll(self):
        toe_ik_handle = pmc.ikHandle(n=("{0}_toe_ik_HDL".format(self.model.module_name)),
                                     startJoint=self.created_ctrtl_jnts[1], endEffector=self.created_ctrtl_jnts[2],
                                     solver="ikSCsolver")[0]

        ik_effector = pmc.listRelatives(self.created_ctrtl_jnts[1], children=1)[1]
        ik_effector.rename("{0}_toe_ik_EFF".format(self.model.module_name))
        ball_ik_handle = pmc.ikHandle(n=("{0}_ball_ik_HDL".format(self.model.module_name)),
                                      startJoint=self.created_ctrtl_jnts[0], endEffector=self.created_ctrtl_jnts[1],
                                      solver="ikSCsolver")[0]
        ik_effector = pmc.listRelatives(self.created_ctrtl_jnts[0], children=1)[1]
        ik_effector.rename("{0}_ball_ik_EFF".format(self.model.module_name))

        self.leg_option_ctrl.fkIk >> ball_ik_handle.ikBlend
        self.leg_option_ctrl.fkIk >> toe_ik_handle.ikBlend

        pmc.parent(self.leg_ik_handle, world=1)
        pmc.parent(self.leg_ik_length_end_loc, world=1)
        if pmc.objExists("{0}_roll_OFS".format(self.model.module_name)):
            pmc.delete("{0}_roll_OFS".format(self.model.module_name))
        locs_offset = pmc.group(em=1, n="{0}_roll_OFS".format(self.model.module_name))
        locs_offset.setAttr("translate", pmc.xform(self.created_skn_jnts[0], q=1, ws=1, translation=1))
        locs_offset.setAttr("rotateOrder", 4)
        pmc.parent(locs_offset, self.leg_ik_ctrl, r=0)
        toe_bend_group = pmc.group(em=1, n="{0}_toe_bend_OFS".format(self.model.module_name))
        toe_bend_group.setAttr("translate", pmc.xform(self.created_locs[0], q=1, ws=1, translation=1))
        pmc.parent(ball_ik_handle, self.created_locs[0], r=0)
        pmc.parent(toe_bend_group, self.created_locs[1], r=0)
        pmc.parent(toe_ik_handle, toe_bend_group, r=0)
        pmc.parent(self.created_locs[2], locs_offset, r=0)
        pmc.parent(self.leg_ik_handle, self.created_locs[0], r=0)
        pmc.parent(self.leg_ik_length_end_loc, self.created_locs[0], r=0)

        if self.leg_ankle_rotation_handle is not None:
            pmc.pointConstraint(self.leg_ik_handle, self.leg_ankle_rotation_handle, maintainOffset=1)

        if "roll" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("roll")
        self.leg_ik_ctrl.addAttr("roll", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "bendLimitAngle" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("bendLimitAngle")
        self.leg_ik_ctrl.addAttr("bendLimitAngle", attributeType="float", defaultValue=45, hidden=0, keyable=1)
        if "toeStraightAngle" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("toeStraightAngle")
        self.leg_ik_ctrl.addAttr("toeStraightAngle", attributeType="float", defaultValue=70, hidden=0, keyable=1)
        if "bank" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("bank")
        self.leg_ik_ctrl.addAttr("bank", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "lean" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("lean")
        self.leg_ik_ctrl.addAttr("lean", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "heelTwist" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("heelTwist")
        self.leg_ik_ctrl.addAttr("heelTwist", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "toeTwist" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("toeTwist")
        self.leg_ik_ctrl.addAttr("toeTwist", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "toeBend" in pmc.listAttr(self.leg_ik_ctrl, keyable=1):
            self.leg_ik_ctrl.deleteAttr("toeBend")
        self.leg_ik_ctrl.addAttr("toeBend", attributeType="float", defaultValue=0, hidden=0, keyable=1)

        roll_heel_limit = pmc.createNode("clamp", n="{0}_heel_CLAMP".format(self.model.module_name))
        roll_zerotobend_limit = pmc.createNode("clamp", n="{0}_zero_to_bend_CLAMP".format(self.model.module_name))
        roll_zerotobend_percent = pmc.createNode("setRange",
                                                 n="{0}_zero_to_bend_percent_RANGE".format(self.model.module_name))
        roll_bendtostraight_limit = pmc.createNode("clamp", n="{0}_bend_to_straight_CLAMP".format(self.model.module_name))
        roll_bendtostraight_percent = pmc.createNode("setRange",
                                                     n="{0}_bend_to_straight_percent_RANGE".format(self.model.module_name))
        roll_toe_mult = pmc.createNode("multiplyDivide", n="{0}_toe_roll_mult_MDV".format(self.model.module_name))
        roll_bendtostraight_invertpercent = pmc.createNode("plusMinusAverage",
                                                           n="{0}_invert_percent_RANGE".format(self.model.module_name))
        roll_ball_percent_mult = pmc.createNode("multiplyDivide",
                                                n="{0}_ball_percent_mult_MDV".format(self.model.module_name))
        roll_ball_mult = pmc.createNode("multiplyDivide", n="{0}_ball_roll_mult_MDV".format(self.model.module_name))

        roll_heel_limit.setAttr("minR", -90)
        roll_heel_limit.setAttr("maxR", 0)
        self.leg_ik_ctrl.roll >> roll_heel_limit.inputR
        roll_heel_limit.outputR >> self.created_locs[2].rotateX

        self.leg_ik_ctrl.bendLimitAngle >> roll_bendtostraight_limit.minR
        self.leg_ik_ctrl.toeStraightAngle >> roll_bendtostraight_limit.maxR
        self.leg_ik_ctrl.roll >> roll_bendtostraight_limit.inputR

        roll_bendtostraight_percent.setAttr("minX", 0)
        roll_bendtostraight_percent.setAttr("maxX", 1)
        roll_bendtostraight_limit.inputR >> roll_bendtostraight_percent.valueX
        roll_bendtostraight_limit.minR >> roll_bendtostraight_percent.oldMinX
        roll_bendtostraight_limit.maxR >> roll_bendtostraight_percent.oldMaxX

        roll_toe_mult.setAttr("operation", 1)
        roll_bendtostraight_percent.outValueX >> roll_toe_mult.input1X
        roll_bendtostraight_limit.inputR >> roll_toe_mult.input2X
        roll_toe_mult.outputX >> self.created_locs[1].rotateX

        roll_bendtostraight_invertpercent.setAttr("operation", 2)
        roll_bendtostraight_invertpercent.setAttr("input1D[0]", 1)
        roll_bendtostraight_percent.outValueX >> roll_bendtostraight_invertpercent.input1D[1]

        roll_zerotobend_limit.setAttr("minR", 0)
        self.leg_ik_ctrl.bendLimitAngle >> roll_zerotobend_limit.maxR
        self.leg_ik_ctrl.roll >> roll_zerotobend_limit.inputR

        roll_zerotobend_percent.setAttr("minX", 0)
        roll_zerotobend_percent.setAttr("maxX", 1)
        roll_zerotobend_limit.inputR >> roll_zerotobend_percent.valueX
        roll_zerotobend_limit.minR >> roll_zerotobend_percent.oldMinX
        roll_zerotobend_limit.maxR >> roll_zerotobend_percent.oldMaxX

        roll_ball_percent_mult.setAttr("operation", 1)
        roll_zerotobend_percent.outValueX >> roll_ball_percent_mult.input1X
        roll_bendtostraight_invertpercent.output1D >> roll_ball_percent_mult.input2X

        roll_ball_mult.setAttr("operation", 1)
        roll_ball_percent_mult.outputX >> roll_ball_mult.input1X
        self.leg_ik_ctrl.roll >> roll_ball_mult.input2X
        roll_ball_mult.outputX >> self.created_locs[0].rotateX

        self.leg_ik_ctrl.toeBend >> toe_bend_group.rotateX

        heel_offset = pmc.createNode("plusMinusAverage", n="{0}_heeltwist_offset_PMA".format(self.created_locs[2]))
        heel_offset.setAttr("operation", 1)
        heel_offset.setAttr("input1D[0]", self.created_locs[2].getAttr("rotateY"))
        self.leg_ik_ctrl.heelTwist >> heel_offset.input1D[1]
        heel_offset.output1D >> self.created_locs[2].rotateY

        toe_offset = pmc.createNode("plusMinusAverage", n="{0}_toetwist_offset_PMA".format(self.created_locs[1]))
        toe_offset.setAttr("operation", 1)
        toe_offset.setAttr("input1D[0]", self.created_locs[1].getAttr("rotateY"))
        self.leg_ik_ctrl.toeTwist >> toe_offset.input1D[1]
        toe_offset.output1D >> self.created_locs[1].rotateY

        self.leg_ik_ctrl.lean >> self.created_locs[0].rotateZ

        bank_in_limit = pmc.createNode("clamp", n="{0}_bank_in_CLAMP".format(self.model.module_name))
        bank_out_limit = pmc.createNode("clamp", n="{0}_bank_out_CLAMP".format(self.model.module_name))

        if self.model.side == "Right":
            bank_in_limit.setAttr("minR", -90)
            bank_in_limit.setAttr("maxR", 0)
            self.leg_ik_ctrl.bank >> bank_in_limit.inputR
            bank_in_limit.outputR >> self.created_locs[3].rotateZ
            bank_out_limit.setAttr("minR", 0)
            bank_out_limit.setAttr("maxR", 90)
            self.leg_ik_ctrl.bank >> bank_out_limit.inputR
            bank_out_limit.outputR >> self.created_locs[4].rotateZ
        else:
            bank_invert = pmc.createNode("multiplyDivide", n="{0}_bank_invert_value_MDV".format(self.model.module_name))
            bank_invert.setAttr("input2X", -1)
            self.leg_ik_ctrl.bank >> bank_invert.input1X
            bank_in_limit.setAttr("minR", 0)
            bank_in_limit.setAttr("maxR", 90)
            bank_invert.outputX >> bank_in_limit.inputR
            bank_in_limit.outputR >> self.created_locs[3].rotateZ
            bank_out_limit.setAttr("minR", -90)
            bank_out_limit.setAttr("maxR", 0)
            bank_invert.outputX >> bank_out_limit.inputR
            bank_out_limit.outputR >> self.created_locs[4].rotateZ


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.side = "Left"
        self.fk_ik_type = "one_chain"
        # self.how_many_toes = 1
