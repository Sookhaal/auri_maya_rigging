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
        self.thumb_creation_switch = QtWidgets.QCheckBox()
        self.how_many_fingers = QtWidgets.QSpinBox()
        self.how_many_phalanges = QtWidgets.QSpinBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.side_cbbox.setCurrentText(self.model.side)
        self.thumb_creation_switch.setChecked(self.model.thumb_creation_switch)
        self.how_many_fingers.setValue(self.model.how_many_fingers)
        self.how_many_phalanges.setValue(self.model.how_many_phalanges)
        self.ctrl.look_for_parent()

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        self.thumb_creation_switch.stateChanged.connect(self.ctrl.on_thumb_creation_switch_changed)

        self.side_cbbox.insertItems(0, ["Left", "Right"])
        self.side_cbbox.currentTextChanged.connect(self.ctrl.on_side_cbbox_changed)

        self.how_many_fingers.setMinimum(1)
        self.how_many_fingers.valueChanged.connect(self.ctrl.on_how_many_fingers_changed)

        self.how_many_phalanges.setMinimum(2)
        self.how_many_phalanges.valueChanged.connect(self.ctrl.on_how_many_phalanges_changed)

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

        options_layout = QtWidgets.QVBoxLayout()
        options_grp = grpbox("Options", options_layout)

        thumb_layout = QtWidgets.QHBoxLayout()
        thumb_text = QtWidgets.QLabel("thumb :")
        thumb_layout.addWidget(thumb_text)
        thumb_layout.addWidget(self.thumb_creation_switch)

        fingers_layout = QtWidgets.QVBoxLayout()
        fingers_text = QtWidgets.QLabel("How many fingers :")
        fingers_layout.addWidget(fingers_text)
        fingers_layout.addWidget(self.how_many_fingers)
        phalanges_text = QtWidgets.QLabel("How many phalanges for each fingers :")
        fingers_layout.addWidget(phalanges_text)
        fingers_layout.addWidget(self.how_many_phalanges)

        options_layout.addLayout(thumb_layout)
        options_layout.addLayout(fingers_layout)

        main_layout.addLayout(select_parent_and_object_layout)
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
        self.created_fk_ctrls = []
        self.parent_ankle_fk_ctrl = None
        self.parent_ankle_ik_ctrl = None
        self.parent_option_ctrl = None
        self.jnts_to_skin = []
        RigController.__init__(self, model, view)

    def on_how_many_fingers_changed(self, value):
        self.model.how_many_fingers = value

    def on_how_many_phalanges_changed(self, value):
        self.model.how_many_phalanges = value

    def on_thumb_creation_switch_changed(self, state):
        self.model.thumb_creation_switch = is_checked(state)

    def prebuild(self):
        self.guides_names = []
        self.guides = []

        if self.model.thumb_creation_switch:
            thumb_first_jnt = "{0}_thumb_metacarpus_GUIDE".format(self.model.module_name)
            thumb_curve = "{0}_thumb_phalanges_GUIDE".format(self.model.module_name)
            thumb = [thumb_first_jnt, thumb_curve]
            self.guides_names.append(thumb)

        for i in range(0, self.model.how_many_fingers):
            first_jnt = "{0}_finger{1}_metacarpus_GUIDE".format(self.model.module_name, i + 1)
            finger_curve = "{0}_finger{1}_phalanges_GUIDE".format(self.model.module_name, i + 1)
            finger = [first_jnt, finger_curve]
            self.guides_names.append(finger)

        self.side = {"Left": 1, "Right": -1}
        self.side_coef = self.side.get(self.model.side)

        if self.guide_check(self.guides_names):
            self.guides = [pmc.ls(guide)[:] for guide in self.guides_names]
            for i, guide in enumerate(self.guides):
                if ((self.model.thumb_creation_switch and i != 0) or not self.model.thumb_creation_switch) and \
                                guide[1].getShape().getAttr("spans") != self.model.how_many_phalanges:
                    if self.model.how_many_phalanges > 2:
                        guide[1] = pmc.rebuildCurve(guide[1], rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                                    s=self.model.how_many_phalanges, d=1, ch=0, replaceOriginal=1)[0]
                    else:
                        guide[1] = pmc.rebuildCurve(guide[1], rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                                    s=4, d=1, ch=0, replaceOriginal=1)[0]
                        pmc.delete(guide[1].cv[-2])
                        pmc.delete(guide[1].cv[1])
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            self.guides_grp.setAttr("visibility", 1)
            self.view.refresh_view()
            pmc.select(d=1)
            return

        if self.model.thumb_creation_switch:
            thumb_wrist_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0][0])
            thumb_wrist_guide.setAttr("translate", (2 * self.side_coef, 0.5, -1.5))
            thumb_guide = rig_lib.create_curve_guide(d=1, number_of_points=3, name=self.guides_names[0][1],
                                                     hauteur_curve=2)
            thumb_guide.setAttr("translate", (2 * self.side_coef, 0, -2))
            thumb_guide.setAttr("rotate", (-90, 0, 0))
            thumb = [thumb_wrist_guide, thumb_guide]
            self.guides.append(thumb)

        for i, finger in enumerate(self.guides_names):
            if (self.model.thumb_creation_switch and i != 0) or not self.model.thumb_creation_switch:
                wrist_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[i][0])
                wrist_guide.setAttr("translate", (1.5 * self.side_coef + (0.5 * (i - int(self.model.thumb_creation_switch)) * self.side_coef), 0.5, -0.5))
                finger_guide = rig_lib.create_curve_guide(d=1, number_of_points=(self.model.how_many_phalanges + 1),
                                                          name=finger[1], hauteur_curve=3)
                finger_guide.setAttr("translate", (1.5 * self.side_coef + (0.5 * (i - int(self.model.thumb_creation_switch)) * self.side_coef), 0, 0))
                finger_guide.setAttr("rotate", (90, 0, 0))
                finger = [wrist_guide, finger_guide]
                self.guides.append(finger)

        self.guides_grp = self.group_guides(self.guides)
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()

        self.get_parent_needed_objects()

        self.create_skn_jnts()
        self.create_ctrls()
        self.create_options_attributes()
        self.clean_rig()

    def get_parent_needed_objects(self):
        self.parent_ankle_fk_ctrl = pmc.ls("{0}_ankle_fk_CTRL".format(self.model.selected_module))[0]
        self.parent_ankle_ik_ctrl = pmc.ls("{0}_ankle_ik_CTRL".format(self.model.selected_module))[0]
        self.parent_option_ctrl = pmc.ls("{0}_option_CTRL".format(self.model.selected_module))[0]

    def create_skn_jnts(self):
        duplicate_guides = []
        self.created_skn_jnts = []
        self.jnts_to_skin = []
        # orient_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_wrist_LOC".format(self.model.module_name))
        # orient_loc.setAttr("rotateOrder", 4)
        # orient_loc.setAttr("translate", pmc.xform(self.parent_ankle_fk_ctrl, q=1, ws=1, translation=1))
        #
        # if self.model.thumb_creation_switch:
        #     first_finger = self.guides[1]
        # else:
        #     first_finger = self.guides[0]
        # hand_plane = pmc.ls(pmc.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        #                                         name="{0}_palm_plane".format(self.model.module_name), ch=0))[0]
        # first_finger_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_temp_first_loc".format(self.model.module_name))
        # last_finger_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_temp_last_loc".format(self.model.module_name))
        # first_finger_loc.setAttr("translate", pmc.xform(first_finger[1].cv[0], q=1, ws=1, translation=1))
        # last_finger_loc.setAttr("translate", pmc.xform(self.guides[-1][1].cv[0], q=1, ws=1, translation=1))
        # first_finger[0].getShape().worldPosition[0] >> hand_plane.getShape().pnts[0]
        # first_finger_loc.getShape().worldPosition[0] >> hand_plane.getShape().pnts[1]
        # last_finger_loc.getShape().worldPosition[0] >> hand_plane.getShape().pnts[2]
        # self.guides[-1][0].getShape().worldPosition[0] >> hand_plane.getShape().pnts[3]
        #
        # mid_finger_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_temp_mid_loc".format(self.model.module_name))
        # mid_finger_loc.setAttr("translate", pmc.xform(self.guides[self.model.how_many_fingers / 2][1].cv[0], q=1, ws=1,
        #                                               translation=1))
        #
        # orient_loc_const = pmc.normalConstraint(hand_plane, orient_loc, aimVector=(-1.0, 0.0, 0.0),
        #                                         upVector=(0.0, 1.0 * self.side_coef, 0.0), worldUpType="object",
        #                                         worldUpObject=mid_finger_loc)
        #
        # pmc.xform(self.parent_ankle_fk_ctrl, ws=1, rotation=(pmc.xform(orient_loc, q=1, ws=1, rotation=1)))
        # pmc.xform(self.parent_ankle_ik_ctrl, ws=1,
        #           rotation=(pmc.xform(pmc.listRelatives(self.parent_ankle_fk_ctrl, children=1, type="transform")[0],
        #                               q=1, ws=1, rotation=1)))

        for n, finger in enumerate(self.guides):
            created_finger_jnts = []
            wrist_guide = pmc.spaceLocator(p=(0, 0, 0), n="{0}_duplicate".format(finger[0]))
            wrist_guide.setAttr("rotateOrder", 1)
            pmc.parent(wrist_guide, finger[0], r=1)
            pmc.parent(wrist_guide, world=1)
            finger_crv_vertex_list = finger[1].cv[:]
            finger_new_guides = [wrist_guide]
            for i, cv in enumerate(finger_crv_vertex_list):
                loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_{1}_duplicate".format(finger[1], i + 1))
                loc.setAttr("translate", (pmc.xform(cv, q=1, ws=1, translation=1)))
                loc.setAttr("rotateOrder", 1)
                finger_new_guides.append(loc)
            duplicate_guides.append(finger_new_guides)

            finger_plane = pmc.polyCreateFacet(p=[pmc.xform(finger_new_guides[1], q=1, ws=1, translation=1),
                                                  pmc.xform(finger_new_guides[2], q=1, ws=1, translation=1),
                                                  pmc.xform(finger_new_guides[3], q=1, ws=1, translation=1)],
                                               n="{0}_temporary_finger{1}_plane".format(self.model.module_name, n),
                                               ch=1)[0]
            finger_plane_face = pmc.ls(finger_plane)[0].f[0]

            for i, guide in enumerate(finger_new_guides):
                if not guide == finger_new_guides[-1]:
                    if i == 0:
                        const = pmc.aimConstraint(finger_new_guides[i + 1], guide,
                                                  aimVector=(0.0, 1.0 * self.side_coef, 0.0),
                                                  upVector=(1.0, 0.0, 0.0), worldUpType="objectrotation",
                                                  worldUpVector=(0.0, 1.0, 0.0),
                                                  worldUpObject=self.parent_ankle_fk_ctrl)
                    else:
                        const = pmc.normalConstraint(finger_plane_face, guide, aimVector=(0.0, 0.0, -1.0),
                                                     upVector=(0.0, 1.0 * self.side_coef, 0.0), worldUpType="object",
                                                     worldUpObject=finger_new_guides[i + 1])
                    pmc.delete(const)
                    pmc.select(d=1)
                if i != 0:
                    pmc.parent(guide, finger_new_guides[i - 1])
                    pmc.select(created_finger_jnts[i - 1])

                jnt = pmc.joint(p=(pmc.xform(guide, q=1, ws=1, translation=1)),
                                n="{0}_finger{1}_{2}_SKN".format(self.model.module_name, n + 1, i), rad=0.2)
                jnt.setAttr("rotateOrder", 1)

                if i == 0:
                    pmc.parent(jnt, self.jnt_input_grp, r=0)
                    jnt.setAttr("jointOrient", (0, 0, 0))

                if i != len(finger_new_guides) - 1:
                    pmc.xform(jnt, ws=1, rotation=(pmc.xform(guide, q=1, ws=1, rotation=1)))

                created_finger_jnts.append(jnt)

            created_finger_jnts[-1].rename("{0}_finger{1}_end_JNT".format(self.model.module_name, n + 1))
            pmc.delete(finger_plane)

            self.created_skn_jnts.append(created_finger_jnts)
            self.jnts_to_skin.append(created_finger_jnts[:-1])

        pmc.delete(duplicate_guides[:])
        # pmc.delete(orient_loc)
        # pmc.delete(hand_plane)
        # pmc.delete(first_finger_loc)
        # pmc.delete(last_finger_loc)
        # pmc.delete(mid_finger_loc)

    def create_ctrls(self):
        self.created_fk_ctrls = []
        for n, finger in enumerate(self.created_skn_jnts):
            created_finger_ctrls = []
            for i, jnt in enumerate(finger):
                if 1 < i < len(finger) - 1:
                    ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=0.5, d=3, s=8,
                                            n="{0}_finger{1}_{2}_fk_CTRL_shape".format(self.model.module_name,
                                                                                       (n + 1), i), ch=0)[0]
                    ctrl = rig_lib.create_jnttype_ctrl("{0}_finger{1}_{2}_fk_CTRL".format(self.model.module_name,
                                                                                          (n + 1), i), ctrl_shape,
                                                       drawstyle=0, rotateorder=1)
                    ctrl.setAttr("radius", 0)
                    ctrl.setAttr("translate", pmc.xform(jnt, q=1, ws=1, translation=1))
                    pmc.parent(ctrl, created_finger_ctrls[i - 1], r=0)
                    pmc.reorder(ctrl, front=1)
                    ctrl.setAttr("jointOrient", (0, 0, 0))
                    ctrl.setAttr("rotate", pmc.xform(self.created_skn_jnts[n][i], q=1, rotation=1))

                    ctrl.rotate >> self.created_skn_jnts[n][i].rotate

                    created_finger_ctrls.append(ctrl)

                elif i == 1:
                    ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=0.5, d=3, s=8,
                                            n="{0}_finger{1}_{2}_fk_CTRL_shape".format(self.model.module_name,
                                                                                       (n + 1), i), ch=0)[0]
                    ctrl = rig_lib.create_jnttype_ctrl("{0}_finger{1}_{2}_fk_CTRL".format(self.model.module_name,
                                                                                          (n + 1), i), ctrl_shape,
                                                       drawstyle=0, rotateorder=1)
                    ctrl.setAttr("radius", 0)
                    ctrl.setAttr("translate", pmc.xform(jnt, q=1, ws=1, translation=1))
                    pmc.parent(ctrl, created_finger_ctrls[i - 1], r=0)
                    pmc.reorder(ctrl, front=1)
                    ctrl.setAttr("jointOrient", (0, 0, 0))

                    if (self.model.thumb_creation_switch and n != 0) or not self.model.thumb_creation_switch:
                        ctrl.setAttr("jointOrientX",
                                     pmc.xform(self.created_skn_jnts[n][i - 1], q=1, rotation=1)[0] * -1)

                    pmc.xform(ctrl, ws=1, rotation=pmc.xform(self.created_skn_jnts[n][i], q=1, ws=1, rotation=1))

                    if (self.model.thumb_creation_switch and n != 0) or not self.model.thumb_creation_switch:
                        jnt_offset = pmc.createNode("plusMinusAverage",
                                                    n="{0}_Xoffset_Xctrlvalue_spreadValue_cumul_PMA".format(ctrl))
                        jnt_offset.setAttr("operation", 1)
                        ctrl.rotateX >> jnt_offset.input1D[0]
                        ctrl.jointOrientX >> jnt_offset.input1D[1]
                        jnt_offset.output1D >> self.created_skn_jnts[n][i].rotateX

                    else:
                        ctrl.rotateX >> self.created_skn_jnts[n][i].rotateX

                    ctrl.rotateY >> self.created_skn_jnts[n][i].rotateY
                    ctrl.rotateZ >> self.created_skn_jnts[n][i].rotateZ

                    created_finger_ctrls.append(ctrl)

                elif i == 0:
                    ctrl_shape = rig_lib.oval_curve_y(
                        "{0}_finger{1}_{2}_fk_CTRL".format(self.model.module_name, (n + 1), i), self.side_coef)
                    ctrl = rig_lib.create_jnttype_ctrl("{0}_finger{1}_{2}_fk_CTRL".format(self.model.module_name,
                                                                                          (n + 1), i), ctrl_shape,
                                                       drawstyle=0, rotateorder=1)
                    ctrl.setAttr("radius", 0)
                    ctrl.setAttr("translate", pmc.xform(jnt, q=1, ws=1, translation=1))
                    pmc.parent(ctrl, self.ctrl_input_grp, r=0)
                    ctrl.setAttr("jointOrient", (0, 0, 0))
                    ctrl.setAttr("jointOrientX", pmc.xform(self.created_skn_jnts[n][i], q=1, rotation=1)[0])
                    pmc.xform(ctrl, ws=1, rotation=pmc.xform(self.created_skn_jnts[n][i], q=1, ws=1, rotation=1))
                    jnt_offset = pmc.createNode("plusMinusAverage", n="{0}_raz_jnt_offset_PMA".format(ctrl))
                    jnt_offset.setAttr("operation", 1)
                    ctrl.rotateX >> jnt_offset.input1D[0]
                    ctrl.jointOrientX >> jnt_offset.input1D[1]
                    jnt_offset.output1D >> self.created_skn_jnts[n][i].rotateX
                    ctrl.rotateY >> self.created_skn_jnts[n][i].rotateY
                    ctrl.rotateZ >> self.created_skn_jnts[n][i].rotateZ

                    created_finger_ctrls.append(ctrl)

            self.created_fk_ctrls.append(created_finger_ctrls)

    def create_options_attributes(self):
        if self.model.how_many_fingers > 1:
            self.parent_option_ctrl.addAttr("spread", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        for n, finger in enumerate(self.created_fk_ctrls):
            self.parent_option_ctrl.addAttr("finger{0}Curl".format(n + 1), attributeType="float", defaultValue=0,
                                            hidden=0, keyable=1)

            if self.model.how_many_fingers == 2:
                center_finger = 0.5
            else:
                center_finger = int((float(self.model.how_many_fingers - 2) / 2) + 0.5)

            if self.model.thumb_creation_switch:
                center_finger += 1

            if self.model.how_many_fingers > 1 and ((self.model.thumb_creation_switch and n != 0)
                                                    or not self.model.thumb_creation_switch) \
                    and n != center_finger:
                spread_mult = pmc.createNode("multiplyDivide", n="{0}_spread_mult_MDV".format(self.created_fk_ctrls[n][1]))
                spread_mult.setAttr("operation", 1)
                spread_mult.setAttr("input2X", center_finger - n)
                self.parent_option_ctrl.spread >> spread_mult.input1X
                spread_mult.outputX >> finger[1].rotateAxisX
                finger[1].rotateAxisX >> self.created_skn_jnts[n][1].rotateAxisX

            for i, ctrl in enumerate(finger):
                # if self.model.thumb_creation_switch and n == 0:
                #     self.parent_option_ctrl.connectAttr("finger{0}Curl".format(n + 1), ctrl.rotateAxisZ)
                #     ctrl.rotateAxisZ >> self.created_skn_jnts[n][i].rotateAxisZ
                # elif i != 0:
                if i != 0:
                    self.parent_option_ctrl.connectAttr("finger{0}Curl".format(n + 1), ctrl.rotateAxisZ)
                    ctrl.rotateAxisZ >> self.created_skn_jnts[n][i].rotateAxisZ

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        if self.model.side == "Left":
            color_value = 6
        else:
            color_value = 13

        for finger in self.created_fk_ctrls:
            for ctrl in finger:
                rig_lib.clean_ctrl(ctrl, color_value, trs="ts")

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
        rig_lib.add_parameter_as_extra_attr(info_crv, "how_many_fingers", self.model.how_many_fingers)
        rig_lib.add_parameter_as_extra_attr(info_crv, "thumb_creation", self.model.thumb_creation_switch)
        rig_lib.add_parameter_as_extra_attr(info_crv, "how_many_phalanges", self.model.how_many_phalanges)

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


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.side = "Left"
        self.how_many_fingers = 3
        self.thumb_creation_switch = True
        self.how_many_phalanges = 3
