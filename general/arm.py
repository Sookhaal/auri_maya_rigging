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
        self.fk_ik_type_cbbox = QtWidgets.QComboBox()
        self.ik_creation_switch = QtWidgets.QCheckBox()
        self.stretch_creation_switch = QtWidgets.QCheckBox()
        self.clavicle_creation_switch = QtWidgets.QCheckBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.ik_creation_switch.setChecked(self.model.ik_creation_switch)
        self.stretch_creation_switch.setChecked(self.model.stretch_creation_switch)
        self.clavicle_creation_switch.setChecked(self.model.clavicle_creation_switch)
        self.side_cbbox.setCurrentText(self.model.side)
        self.fk_ik_type_cbbox.setCurrentText(self.model.fk_ik_type)
        self.ctrl.look_for_parent()

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        self.ik_creation_switch.stateChanged.connect(self.ctrl.on_ik_creation_switch_changed)
        self.ik_creation_switch.setEnabled(False)
        self.stretch_creation_switch.stateChanged.connect(self.ctrl.on_stretch_creation_switch_changed)
        self.clavicle_creation_switch.stateChanged.connect(self.ctrl.on_clavicle_creation_switch_changed)

        self.side_cbbox.insertItems(0, ["Left", "Right"])
        self.side_cbbox.currentTextChanged.connect(self.ctrl.on_side_cbbox_changed)

        self.fk_ik_type_cbbox.insertItems(0, ["one_chain", "three_chains"])
        self.fk_ik_type_cbbox.currentTextChanged.connect(self.ctrl.on_fk_ik_type_changed)

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

        chain_type_layout = QtWidgets.QVBoxLayout()
        chain_type_grp = grpbox("Fk/Ik chain type", chain_type_layout)
        chain_type_layout.addWidget(self.fk_ik_type_cbbox)

        checkbox_layout = QtWidgets.QVBoxLayout()
        ik_layout = QtWidgets.QHBoxLayout()
        ik_text = QtWidgets.QLabel("IK ctrls :")
        ik_layout.addWidget(ik_text)
        ik_layout.addWidget(self.ik_creation_switch)
        stretch_layout = QtWidgets.QHBoxLayout()
        stretch_text = QtWidgets.QLabel("stretch/squash :")
        stretch_layout.addWidget(stretch_text)
        stretch_layout.addWidget(self.stretch_creation_switch)
        clavicle_layout = QtWidgets.QHBoxLayout()
        clavicle_text = QtWidgets.QLabel("clavicle :")
        clavicle_layout.addWidget(clavicle_text)
        clavicle_layout.addWidget(self.clavicle_creation_switch)

        checkbox_layout.addLayout(ik_layout)
        checkbox_layout.addLayout(stretch_layout)
        checkbox_layout.addLayout(clavicle_layout)

        options_layout.addLayout(checkbox_layout)

        main_layout.addWidget(select_parent_grp)
        main_layout.addWidget(side_grp)
        main_layout.addWidget(chain_type_grp)
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
        self.clavicle_jnt = None
        self.created_fk_jnts = []
        self.created_ik_jnts = []
        self.created_fk_ctrls = []
        self.created_ik_ctrls = []
        self.option_ctrl = None
        self.plane = None
        self.clavicle_ik_handle = None
        RigController.__init__(self,  model, view)

    def prebuild(self):
        self.create_temporary_outputs(["wrist_OUTPUT"])

        self.guides_names = ["{0}_shoulder_GUIDE".format(self.model.module_name),
                             "{0}_elbow_GUIDE".format(self.model.module_name),
                             "{0}_wrist_GUIDE".format(self.model.module_name)]
        if self.model.clavicle_creation_switch:
            self.guides_names.append("{0}_clavicle_GUIDE".format(self.model.module_name))

        self.side = {"Left": 1, "Right": -1}
        self.side_coef = self.side.get(self.model.side)

        if self.guide_check(self.guides_names):
            self.guides = pmc.ls("{0}_shoulder_GUIDE".format(self.model.module_name),
                                 "{0}_elbow_GUIDE".format(self.model.module_name),
                                 "{0}_wrist_GUIDE".format(self.model.module_name))
            if self.model.clavicle_creation_switch:
                self.guides.append(pmc.ls("{0}_clavicle_GUIDE".format(self.model.module_name))[0])
            else:
                if pmc.objExists("{0}_clavicle_GUIDE".format(self.model.module_name)):
                    pmc.delete("{0}_clavicle_GUIDE".format(self.model.module_name))

            if pmc.objExists("{0}_leg_plane".format(self.model.module_name)):
                pmc.delete("{0}_leg_plane".format(self.model.module_name))

            self.plane = pmc.ls(pmc.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                                                    n="{0}_leg_plane".format(self.model.module_name), ch=0))[0]
            self.guides[0].getShape().worldPosition[0] >> self.plane.getShape().pnts[0]
            self.guides[1].getShape().worldPosition[0] >> self.plane.getShape().pnts[1]
            self.guides[2].getShape().worldPosition[0] >> self.plane.getShape().pnts[2]

            self.plane.setAttr("translateX", lock=True, keyable=False, channelBox=False)
            self.plane.setAttr("translateY", lock=True, keyable=False, channelBox=False)
            self.plane.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
            self.plane.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
            self.plane.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
            self.plane.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
            self.plane.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
            self.plane.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
            self.plane.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)

            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            pmc.parent(self.plane, self.guides_grp)
            self.guides_grp.setAttr("visibility", 1)
            pmc.select(d=1)
            return

        shoulder_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0])
        elbow_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[1])
        wrist_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[2])

        shoulder_guide.setAttr("translate", (3 * self.side_coef, 18, 0))
        elbow_guide.setAttr("translate", (5 * self.side_coef, 16, 0))
        wrist_guide.setAttr("translate", (7 * self.side_coef, 14, 0))

        self.plane = pmc.ls(pmc.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                                                n="{0}_leg_plane".format(self.model.module_name), ch=0))[0]

        shoulder_guide.getShape().worldPosition[0] >> self.plane.getShape().pnts[0]
        elbow_guide.getShape().worldPosition[0] >> self.plane.getShape().pnts[1]
        wrist_guide.getShape().worldPosition[0] >> self.plane.getShape().pnts[2]

        self.plane.setAttr("translateX", lock=True, keyable=False, channelBox=False)
        self.plane.setAttr("translateY", lock=True, keyable=False, channelBox=False)
        self.plane.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
        self.plane.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
        self.plane.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
        self.plane.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
        self.plane.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
        self.plane.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
        self.plane.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)

        self.guides = [shoulder_guide, elbow_guide, wrist_guide]

        if self.model.clavicle_creation_switch:
            clavicle_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[3])
            clavicle_guide.setAttr("translate", (1 * self.side_coef, 17.5, 0.5))
            self.guides.append(clavicle_guide)

        self.guides_grp = self.group_guides(self.guides)
        pmc.parent(self.plane, self.guides_grp)
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()

        self.create_skn_jnts()
        self.create_options_ctrl()
        if self.model.clavicle_creation_switch:
            self.create_clavicle_ctrl()
        if self.model.fk_ik_type == "three_chains":
            self.create_and_connect_fk_ik_jnts()
            self.create_fk()
            if self.model.ik_creation_switch:
                self.create_ik()
            if self.model.stretch_creation_switch == 1:
                self.connect_fk_stretch(self.created_fk_jnts, self.created_fk_ctrls)
                self.connect_ik_stretch(self.created_ik_jnts, self.created_ik_ctrls, self.side_coef,
                                        self.created_fk_ctrls[0].getParent(), self.created_ik_ctrls[0],
                                        self.created_fk_jnts[-1])
                if self.model.side == "Right":
                    self.created_ik_ctrls[0].setAttr("rotateY", (self.created_ik_ctrls[0].getAttr("rotateY") - 180))
        if self.model.fk_ik_type == "one_chain":
            self.create_one_chain_fk()
        self.clean_rig()
        self.create_output()
        pmc.select(d=1)

    def create_skn_jnts(self):
        duplicates_guides = []
        for guide in self.guides:
            duplicate = guide.duplicate(n="{0}_duplicate".format(guide))[0]
            duplicates_guides.append(duplicate)

        arm_plane = pmc.polyCreateFacet(p=[pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1),
                                           pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1),
                                           pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)],
                                        n="{0}_leg_plane".format(self.model.module_name), ch=1)[0]

        arm_plane_face = pmc.ls(arm_plane)[0].f[0]

        for guide in duplicates_guides:
            guide.setAttr("rotateOrder", 4)

        if self.model.clavicle_creation_switch:
            clav_const = pmc.aimConstraint(duplicates_guides[0], duplicates_guides[3], maintainOffset=0,
                                           aimVector=(0.0, 1.0 * self.side_coef, 0.0),
                                           upVector=(0.0, 0.0, 1.0 * self.side_coef), worldUpType="vector",
                                           worldUpVector=(0.0, 0.0, 1.0))
            pmc.delete(clav_const)

        shoulder_const = pmc.normalConstraint(arm_plane_face, duplicates_guides[0], aimVector=(1.0, 0.0, 0.0),
                                              upVector=(0.0, 1.0 * self.side_coef, 0.0), worldUpType="object",
                                              worldUpObject=duplicates_guides[1])
        elbow_cons = pmc.normalConstraint(arm_plane_face, duplicates_guides[1], aimVector=(1.0, 0.0, 0.0),
                                          upVector=(0.0, 1.0 * self.side_coef, 0.0), worldUpType="object",
                                          worldUpObject=duplicates_guides[2])
        pmc.delete(shoulder_const)
        pmc.delete(elbow_cons)
        pmc.parent(duplicates_guides[1], duplicates_guides[0], r=0)
        pmc.parent(duplicates_guides[2], duplicates_guides[1], r=0)

        pmc.select(d=1)
        if self.model.clavicle_creation_switch:
            self.clavicle_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[3], q=1, ws=1, translation=1)),
                                     n="{0}_clavicle_SKN".format(self.model.module_name))
            self.clavicle_jnt.setAttr("rotateOrder", 4)
            self.clavicle_jnt.setAttr("jointOrientZ", -90 * self.side_coef)
            if self.model.side == "Right":
                self.clavicle_jnt.setAttr("jointOrientX", 180)
            pmc.xform(self.clavicle_jnt, ws=1, rotation=(pmc.xform(duplicates_guides[3], q=1, ws=1, rotation=1)))

            # group = pmc.group(em=1, n="temp_group")
            # group.setAttr("rotateOrder", 4)

            clav_end = pmc.joint(p=(pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1)),
                                 n="{0}_clavicle_end_JNT".format(self.model.module_name))
            clav_end.setAttr("rotateOrder", 4)

            pmc.parent(self.clavicle_jnt, self.jnt_input_grp, r=0)

            # pmc.parent(shoulder_jnt, group, r=1)
            # group.setAttr("translate", pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1))
            # group.setAttr("rotate", (-90 * (1 - self.side_coef), 0, -90 * self.side_coef))

            # pmc.parent(shoulder_jnt, self.clavicle_jnt, r=0)
            # pmc.delete(group)

        pmc.select(d=1)
        shoulder_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1)),
                                 n="{0}_shoulder_SKN".format(self.model.module_name))

        shoulder_jnt.setAttr("rotateOrder", 4)
        shoulder_jnt.setAttr("jointOrientZ", -90 * self.side_coef)
        if self.model.side == "Right":
            shoulder_jnt.setAttr("jointOrientX", 180)

        pmc.xform(shoulder_jnt, ws=1, rotation=(pmc.xform(duplicates_guides[0], q=1, ws=1, rotation=1)))

        elbow_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1)),
                              n="{0}_elbow_SKN".format(self.model.module_name))
        elbow_jnt.setAttr("rotateOrder", 4)
        elbow_jnt.setAttr("rotate", pmc.xform(duplicates_guides[1], q=1, rotation=1))

        wrist_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)),
                              n="{0}_wrist_SKN".format(self.model.module_name))
        wrist_jnt.setAttr("rotateOrder", 4)

        pmc.parent(shoulder_jnt, self.jnt_input_grp, r=0)

        if self.model.clavicle_creation_switch:
            group = pmc.group(em=1, n="{0}_arm_to_clav_const_GRP".format(self.model.module_name))
            group.setAttr("translate", pmc.xform(shoulder_jnt, q=1, ws=1, translation=1))
            pmc.parent(group, self.jnt_input_grp, r=0)
            pmc.pointConstraint(pmc.listRelatives(self.clavicle_jnt, children=1)[0], group, maintainOffset=0)
            pmc.parent(shoulder_jnt, group, r=0)
        #     pmc.parent(shoulder_jnt, pmc.listRelatives(self.clavicle_jnt, children=1)[0], r=0)
        # else:

        self.created_skn_jnts = [shoulder_jnt, elbow_jnt, wrist_jnt]

        pmc.delete(duplicates_guides[:])
        pmc.delete(arm_plane)

    def create_options_ctrl(self):
        self.option_ctrl = rig_lib.little_cube("{0}_option_CTRL".format(self.model.module_name))
        option_ofs = pmc.group(self.option_ctrl, n="{0}_option_ctrl_OFS".format(self.model.module_name), r=1)
        pmc.parent(option_ofs, self.ctrl_input_grp)
        rig_lib.matrix_constraint(self.created_skn_jnts[-1], option_ofs, srt="trs")
        ctrl_shape = self.option_ctrl.getShape()
        pmc.move(ctrl_shape, [0, 0, -3 * self.side_coef], relative=1, objectSpace=1, worldSpaceDistance=1)
        self.option_ctrl.addAttr("fkIk", attributeType="float", defaultValue=0, hidden=0, keyable=1, hasMaxValue=1,
                                 hasMinValue=1, maxValue=1, minValue=0)

    def create_clavicle_ctrl(self):
        self.clavicle_ik_handle = pmc.ikHandle(n="{0}_clavicle_ik_HDL".format(self.model.module_name), startJoint=self.clavicle_jnt,
                                 endEffector=pmc.listRelatives(self.clavicle_jnt, children=1)[0],
                                 solver="ikSCsolver")[0]
        ik_effector = pmc.listRelatives(self.clavicle_jnt, children=1)[-1]
        ik_effector.rename("{0}_clavicle_ik_EFF".format(self.model.module_name))

        self.connect_one_jnt_ik_stretch(pmc.listRelatives(self.clavicle_jnt, children=1)[0], self.clavicle_jnt,
                                        self.clavicle_ik_handle)
        # TODO: trouver ou mettre les loc pour eviter les boucles

        pmc.parent(self.clavicle_ik_handle, self.parts_grp)
        self.clavicle_ik_handle.setAttr("visibility", 0)

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
        shoulder_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=2, d=3, s=8,
                                    n="{0}_shoulder_fk_CTRL_shape".format(self.model.module_name), ch=0)[0]
        shoulder_ctrl = rig_lib.create_jnttype_ctrl("{0}_shoulder_fk_CTRL".format(self.model.module_name), shoulder_shape,
                                                    drawstyle=0, rotateorder=4)
        shoulder_ctrl.setAttr("radius", 0)
        shoulder_ofs = pmc.group(shoulder_ctrl, n="{0}_shoulder_fk_ctrl_OFS".format(self.model.module_name))
        shoulder_ofs.setAttr("rotateOrder", 4)
        shoulder_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[0], q=1, ws=1, translation=1))
        shoulder_ofs.setAttr("rotateX", 90 * (1 - self.side_coef))
        shoulder_ofs.setAttr("rotateZ", -90 * self.side_coef)

        shoulder_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[0], q=1, rotation=1))
        pmc.parent(shoulder_ofs, self.ctrl_input_grp, r=0)

        elbow_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=2, d=3, s=8,
                                 n="{0}_elbow_fk_CTRL_shape".format(self.model.module_name), ch=0)[0]
        elbow_ctrl = rig_lib.create_jnttype_ctrl("{0}_elbow_fk_CTRL".format(self.model.module_name), elbow_shape,
                                                 drawstyle=0, rotateorder=4)
        elbow_ctrl.setAttr("radius", 0)
        elbow_ctrl.setAttr("translate", pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1))
        elbow_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[1], q=1, rotation=1))
        pmc.parent(elbow_ctrl, shoulder_ctrl, r=0)
        pmc.reorder(elbow_ctrl, front=1)
        elbow_ctrl.setAttr("jointOrient", (0, 0, 0))

        wrist_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=2, d=3, s=8,
                                 n="{0}_wrist_fk_CTRL_shape".format(self.model.module_name), ch=0)[0]
        wrist_ctrl = rig_lib.create_jnttype_ctrl("{0}_wrist_fk_CTRL".format(self.model.module_name), wrist_shape,
                                                 drawstyle=0, rotateorder=4)
        wrist_ctrl.setAttr("radius", 0)
        wrist_ctrl.setAttr("translate", pmc.xform(self.created_fk_jnts[2], q=1, ws=1, translation=1))
        wrist_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[2], q=1, rotation=1))
        pmc.parent(wrist_ctrl, elbow_ctrl, r=0)
        pmc.reorder(wrist_ctrl, front=1)
        wrist_ctrl.setAttr("jointOrient", (0, 0, 0))

        self.created_fk_ctrls = [shoulder_ctrl, elbow_ctrl, wrist_ctrl]

        for i, ctrl in enumerate(self.created_fk_ctrls):
            ctrl.rotate >> self.created_fk_jnts[i].rotate

        wrist_ctrl.scale >> self.created_fk_jnts[-1].scale

        pmc.parent(self.clavicle_ik_handle, self.created_fk_ctrls[0])

    def create_ik(self):
        ik_handle = pmc.ikHandle(n=("{0}_ik_HDL".format(self.model.module_name)),
                                 startJoint=self.created_ik_jnts[0], endEffector=self.created_ik_jnts[-1],
                                 solver="ikRPsolver")[0]
        ik_effector = pmc.listRelatives(self.created_ik_jnts[-2], children=1)[1]
        ik_effector.rename("{0}_ik_EFF".format(self.model.module_name))

        ik_shape = rig_lib.medium_cube("{0}_wrist_ik_CTRL_shape".format(self.model.module_name))
        ik_ctrl = rig_lib.create_jnttype_ctrl("{0}_wrist_ik_CTRL".format(self.model.module_name), ik_shape, drawstyle=2,
                                              rotateorder=4)
        ik_ctrl_ofs = pmc.group(ik_ctrl, n="{0}_wrist_ik_ctrl_OFS".format(self.model.module_name))
        ik_ctrl_ofs.setAttr("rotateOrder", 4)
        fk_ctrl_01_value = pmc.xform(self.created_fk_ctrls[0], q=1, rotation=1)
        fk_ctrl_02_value = pmc.xform(self.created_fk_ctrls[1], q=1, rotation=1)
        fk_ctrl_03_value = pmc.xform(self.created_fk_ctrls[2], q=1, rotation=1)
        self.created_fk_ctrls[0].setAttr("rotate", (0, 0, 0))
        self.created_fk_ctrls[1].setAttr("rotate", (0, 0, 0))
        self.created_fk_ctrls[2].setAttr("rotate", (0, 0, 0))

        ik_ctrl_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[2], q=1, ws=1, translation=1))
        ik_ctrl_ofs.setAttr("rotate", (0, 0, -90))
        pmc.parent(ik_handle, ik_ctrl_ofs, r=0)
        ik_ctrl.setAttr("translate", pmc.xform(ik_handle, q=1, translation=1))
        pmc.parent(ik_handle, ik_ctrl, r=0)
        pmc.parent(ik_ctrl_ofs, self.ctrl_input_grp)

        ik_ctrl.setAttr("translate", (0, 0, 0))

        pole_vector_shape = rig_lib.jnt_shape_curve("{0}_poleVector_CTRL_shape".format(self.model.module_name))
        pole_vector = rig_lib.create_jnttype_ctrl("{0}_poleVector_CTRL".format(self.model.module_name), pole_vector_shape,
                                                  drawstyle=2)
        pv_ofs = pmc.group(pole_vector, n="{0}_poleVector_ctrl_OFS".format(self.model.module_name))
        pv_ofs.setAttr("translate", (pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[0],
                                     pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[1],
                                     pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[2] - (
                                   (pmc.xform(self.created_fk_jnts[1], q=1, translation=1)[1]) * self.side_coef)))
        pmc.poleVectorConstraint(pole_vector, ik_handle)
        pmc.parent(pv_ofs, self.ctrl_input_grp, r=0)

        self.created_ik_jnts[1].setAttr("preferredAngleX", 90)

        const = pmc.parentConstraint(ik_ctrl, self.created_ik_jnts[-1], maintainOffset=1, skipTranslate=["x", "y", "z"])
        const.setAttr("target[0].targetOffsetRotate", (0, -90 * (-1 + self.side_coef), 0))
        const.setAttr("target[0].targetOffsetTranslate", (0, 0, 0))
        ik_ctrl.scale >> self.created_ik_jnts[-1].scale

        self.created_ik_ctrls = [ik_ctrl, pole_vector]
        self.created_fk_ctrls[0].setAttr("rotate", fk_ctrl_01_value)
        self.created_fk_ctrls[1].setAttr("rotate", fk_ctrl_02_value)
        self.created_fk_ctrls[2].setAttr("rotate", fk_ctrl_03_value)

        pmc.xform(pole_vector, ws=1, translation=(pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)))

        ik_handle.setAttr("visibility", 0)

        pmc.xform(ik_ctrl, ws=1,
                  translation=(pmc.xform(self.created_fk_jnts[-1], q=1, ws=1, translation=1)))
        pmc.xform(ik_ctrl, ws=1, rotation=(pmc.xform(self.created_fk_jnts[-1], q=1, ws=1, rotation=1)))
        if self.model.side == "Right":
            ik_ctrl.setAttr("rotateY", (ik_ctrl.getAttr("rotateY") - 180))

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        if self.model.side == "Left":
            color_value = 6
        else:
            color_value = 13

        rig_lib.clean_ctrl(self.option_ctrl, 9, trs="trs")

        invert_value = pmc.createNode("plusMinusAverage", n="{0}_fk_visibility_MDL".format(self.model.module_name))
        invert_value.setAttr("input1D[0]", 1)
        invert_value.setAttr("operation", 2)
        self.option_ctrl.fkIk >> invert_value.input1D[1]

        if self.model.clavicle_creation_switch:
            rig_lib.clean_ctrl(self.created_fk_ctrls[0], color_value, trs="s",
                               visibility_dependence=invert_value.output1D)
        else:
            rig_lib.clean_ctrl(self.created_fk_ctrls[0], color_value, trs="ts",
                               visibility_dependence=invert_value.output1D)
        rig_lib.clean_ctrl(self.created_fk_ctrls[1], color_value, trs="ts", visibility_dependence=invert_value.output1D)
        rig_lib.clean_ctrl(self.created_fk_ctrls[2], color_value, trs="t", visibility_dependence=invert_value.output1D)

        rig_lib.clean_ctrl(self.created_ik_ctrls[0], color_value, trs="", visibility_dependence=self.option_ctrl.fkIk)
        rig_lib.clean_ctrl(self.created_ik_ctrls[1], color_value, trs="rs", visibility_dependence=self.option_ctrl.fkIk)

    def create_output(self):
        rig_lib.create_output(name="{0}_wrist_OUTPUT".format(self.model.module_name), parent=self.created_skn_jnts[-1])

    def create_one_chain_fk(self):
        pass


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.side = "Left"
        self.ik_creation_switch = True
        self.stretch_creation_switch = True
        self.clavicle_creation_switch = True
        self.fk_ik_type = "one_chain"
        # self.bend_creation_switch = False
