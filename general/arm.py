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
        self.refresh_spaces_btn = QtWidgets.QPushButton("Refresh")
        self.add_space_btn = QtWidgets.QPushButton("Add")
        self.remove_space_btn = QtWidgets.QPushButton("Remove")
        self.space_modules_cbbox = QtWidgets.QComboBox()
        self.spaces_cbbox = QtWidgets.QComboBox()
        self.selected_space_module = "No_space_module"
        self.selected_space = "no_space"
        self.space_list_view = QtWidgets.QListView()
        self.space_list = QtGui.QStringListModel()
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
        self.space_list.setStringList(self.model.space_list)
        self.ctrl.look_for_parent(l_cbbox_stringlist=self.ctrl.modules_with_spaces,
                                  l_cbbox_selection=self.selected_space_module,
                                  l_cbbox=self.space_modules_cbbox, r_cbbox_stringlist=self.ctrl.spaces_model,
                                  r_cbbox_selection=self.selected_space, r_cbbox=self.spaces_cbbox)

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        self.space_modules_cbbox.setModel(self.ctrl.modules_with_spaces)
        self.space_modules_cbbox.currentTextChanged.connect(self.ctrl.on_space_modules_cbbox_changed)

        self.spaces_cbbox.setModel(self.ctrl.spaces_model)
        self.spaces_cbbox.currentTextChanged.connect(self.ctrl.on_spaces_cbbox_changed)

        self.space_list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.space_list.setStringList(self.model.space_list)
        self.space_list_view.setModel(self.space_list)

        self.add_space_btn.clicked.connect(self.ctrl.add_space_to_list)
        self.remove_space_btn.clicked.connect(self.ctrl.remove_space_from_list)

        self.refresh_spaces_btn.clicked.connect(self.ctrl.look_for_spaces)

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

        select_spaces_layout = QtWidgets.QVBoxLayout()
        select_spaces_grp = grpbox("Select local spaces :", select_spaces_layout)
        spaces_cbbox_layout = QtWidgets.QHBoxLayout()
        spaces_cbbox_layout.addWidget(self.space_modules_cbbox)
        spaces_cbbox_layout.addWidget(self.spaces_cbbox)
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.addWidget(self.refresh_spaces_btn)
        btn_layout.addWidget(self.add_space_btn)
        select_spaces_layout.addLayout(spaces_cbbox_layout)
        select_spaces_layout.addLayout(btn_layout)

        space_list_layout = QtWidgets.QVBoxLayout()
        space_list_grp = grpbox("local spaces :", space_list_layout)
        space_list_layout.addWidget(self.space_list_view)
        space_list_layout.addWidget(self.remove_space_btn)

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
        main_layout.addWidget(select_spaces_grp)
        main_layout.addWidget(space_list_grp)
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
        self.clavicle_ctrl = None
        self.option_ctrl = None
        self.plane = None
        self.clavicle_ik_ctrl = None
        self.wrist_fk_pos_reader = None
        self.jnt_const_group = None
        RigController.__init__(self,  model, view)

    def prebuild(self):
        if self.model.clavicle_creation_switch:
            self.create_temporary_outputs(["clavicle_OUTPUT", "shoulder_OUTPUT", "elbow_OUTPUT", "wrist_OUTPUT"])
        else:
            self.create_temporary_outputs(["shoulder_OUTPUT", "elbow_OUTPUT", "wrist_OUTPUT"])

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

            if pmc.objExists("{0}_arm_plane".format(self.model.module_name)):
                pmc.delete("{0}_arm_plane".format(self.model.module_name))

            self.plane = pmc.ls(pmc.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                                                    n="{0}_arm_plane".format(self.model.module_name), ch=0))[0]
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
            self.view.refresh_view()
            pmc.select(d=1)
            return

        shoulder_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0])
        elbow_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[1])
        wrist_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[2])

        shoulder_guide.setAttr("translate", (3 * self.side_coef, 18, 0))
        elbow_guide.setAttr("translate", (5 * self.side_coef, 16, -0.5))
        wrist_guide.setAttr("translate", (7 * self.side_coef, 14, 1))

        self.plane = pmc.ls(pmc.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                                                n="{0}_arm_plane".format(self.model.module_name), ch=0))[0]

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
        self.create_output()
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
                                        self.wrist_fk_pos_reader)
            self.create_local_spaces()
        if self.model.fk_ik_type == "one_chain":
            self.create_one_chain_fk()
        self.clean_rig()
        pmc.select(d=1)

    def create_skn_jnts(self):
        duplicates_guides = []
        for guide in self.guides:
            duplicate = guide.duplicate(n="{0}_duplicate".format(guide))[0]
            duplicates_guides.append(duplicate)

        arm_plane = pmc.polyCreateFacet(p=[pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1),
                                           pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1),
                                           pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)],
                                        n="{0}_arm_plane".format(self.model.module_name), ch=1)[0]

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

        if self.model.clavicle_creation_switch:
            pmc.select(d=1)
            self.clavicle_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[3], q=1, ws=1, translation=1)),
                                          n="{0}_clavicle_SKN".format(self.model.module_name))
            self.clavicle_jnt.setAttr("rotateOrder", 4)
            self.clavicle_jnt.setAttr("jointOrientZ", -90 * self.side_coef)
            if self.model.side == "Right":
                self.clavicle_jnt.setAttr("jointOrientX", 180)
            pmc.xform(self.clavicle_jnt, ws=1, rotation=(pmc.xform(duplicates_guides[3], q=1, ws=1, rotation=1)))

            clav_end = pmc.joint(p=(pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1)),
                                 n="{0}_clavicle_end_JNT".format(self.model.module_name))
            clav_end.setAttr("rotateOrder", 4)

            pmc.parent(self.clavicle_jnt, self.jnt_input_grp, r=0)

        pmc.select(d=1)
        shoulder_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1)),
                                 n="{0}_shoulder_SKN".format(self.model.module_name))

        shoulder_jnt.setAttr("rotateOrder", 4)
        shoulder_jnt.setAttr("jointOrientZ", -90 * self.side_coef)
        shoulder_jnt.setAttr("jointOrientX", 90 * (1 - self.side_coef))

        pmc.xform(shoulder_jnt, ws=1, rotation=(pmc.xform(duplicates_guides[0], q=1, ws=1, rotation=1)))

        elbow_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1)),
                              n="{0}_elbow_SKN".format(self.model.module_name))
        elbow_jnt.setAttr("rotateOrder", 4)
        elbow_jnt.setAttr("rotate", pmc.xform(duplicates_guides[1], q=1, rotation=1))

        wrist_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)),
                              n="{0}_wrist_SKN".format(self.model.module_name))
        wrist_jnt.setAttr("rotateOrder", 4)

        pmc.parent(shoulder_jnt, self.jnt_input_grp, r=0)

        self.jnt_const_group = pmc.group(em=1, n="{0}_jnts_const_GRP".format(self.model.module_name))
        self.jnt_const_group.setAttr("translate", pmc.xform(shoulder_jnt, q=1, ws=1, translation=1))
        pmc.parent(self.jnt_const_group, self.jnt_input_grp, r=0)

        if self.model.clavicle_creation_switch:
            pmc.pointConstraint(pmc.listRelatives(self.clavicle_jnt, children=1)[0], self.jnt_const_group, maintainOffset=0)

        pmc.parent(shoulder_jnt, self.jnt_const_group, r=0)

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
        if self.model.clavicle_creation_switch:
            self.option_ctrl.addAttr("clavicleIkCtrl", attributeType="bool", defaultValue=0, hidden=0, keyable=1)

    def create_clavicle_ctrl(self):
        clavicle_ik_handle = pmc.ikHandle(n="{0}_clavicle_ik_HDL".format(self.model.module_name), startJoint=self.clavicle_jnt,
                                               endEffector=pmc.listRelatives(self.clavicle_jnt, children=1)[0],
                                               solver="ikSCsolver")[0]
        ik_effector = pmc.listRelatives(self.clavicle_jnt, children=1)[-1]
        ik_effector.rename("{0}_clavicle_ik_EFF".format(self.model.module_name))

        clav_shape = rig_lib.stick_ball("{0}_clavicle_CTRL_shape".format(self.model.module_name))
        cvs = clav_shape.getShape().cv[:]
        for i, cv in enumerate(cvs):
            if i != 0:
                pmc.xform(cv, ws=1, translation=(pmc.xform(cv, q=1, ws=1, translation=1)[0],
                                                 pmc.xform(cv, q=1, ws=1, translation=1)[1] + (2 * self.side_coef),
                                                 pmc.xform(cv, q=1, ws=1, translation=1)[2] * -self.side_coef))

        self.clavicle_ctrl = rig_lib.create_jnttype_ctrl("{0}_clavicle_CTRL".format(self.model.module_name), clav_shape,
                                                         drawstyle=2, rotateorder=4)
        pmc.select(d=1)
        clav_ofs = pmc.joint(p=(0, 0, 0), n="{0}_clavicle_ctrl_OFS".format(self.model.module_name))
        clav_ofs.setAttr("rotateOrder", 4)
        clav_ofs.setAttr("drawStyle", 2)
        pmc.parent(self.clavicle_ctrl, clav_ofs)
        clav_ofs.setAttr("translate", pmc.xform(self.clavicle_jnt, q=1, ws=1, translation=1))
        clav_ofs.setAttr("jointOrient", (90 * (1 - self.side_coef), 0, -90*self.side_coef))

        pmc.parent(clav_ofs, self.ctrl_input_grp)

        pmc.parentConstraint(self.clavicle_ctrl, self.clavicle_jnt, maintainOffset=1)

        clav_ik_shape = rig_lib.medium_cube("{0}_clavicle_ik_CTRL_shape".format(self.model.module_name))
        self.clavicle_ik_ctrl = rig_lib.create_jnttype_ctrl("{0}_clavicle_ik_CTRL".format(self.model.module_name),
                                                            clav_ik_shape, drawstyle=2, rotateorder=4)
        pmc.select(d=1)
        clav_ik_ofs = pmc.joint(p=(0, 0, 0), n="{0}_clavicle_ik_ctrl_OFS".format(self.model.module_name))
        clav_ik_ofs.setAttr("rotateOrder", 4)
        clav_ik_ofs.setAttr("drawStyle", 2)
        pmc.parent(self.clavicle_ik_ctrl, clav_ik_ofs)
        clav_ik_ofs.setAttr("translate", pmc.xform(pmc.listRelatives(self.clavicle_jnt, children=1)[0], q=1, ws=1,
                                                   translation=1))

        pmc.parent(clav_ik_ofs, self.clavicle_ctrl, r=0)
        pmc.parent(clavicle_ik_handle, self.clavicle_ik_ctrl)
        clavicle_ik_handle.setAttr("visibility", 0)

        self.connect_one_jnt_ik_stretch(pmc.listRelatives(self.clavicle_jnt, children=1)[0], self.clavicle_ctrl,
                                        self.clavicle_ik_ctrl)

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
        pmc.select(d=1)
        shoulder_ofs = pmc.joint(p=(0, 0, 0), n="{0}_shoulder_fk_ctrl_OFS".format(self.model.module_name))
        shoulder_ofs.setAttr("rotateOrder", 4)
        shoulder_ofs.setAttr("drawStyle", 2)
        pmc.parent(shoulder_ctrl, shoulder_ofs)
        shoulder_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[0], q=1, ws=1, translation=1))
        shoulder_ofs.setAttr("jointOrientX", 90 * (1 - self.side_coef))
        shoulder_ofs.setAttr("jointOrientZ", -90 * self.side_coef)

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

        if self.model.clavicle_creation_switch:
            pmc.pointConstraint(pmc.listRelatives(self.clavicle_jnt, children=1)[0], shoulder_ofs, maintainOffset=1)

    def create_ik(self):
        ik_handle = pmc.ikHandle(n=("{0}_ik_HDL".format(self.model.module_name)),
                                 startJoint=self.created_ik_jnts[0], endEffector=self.created_ik_jnts[-1],
                                 solver="ikRPsolver")[0]
        ik_effector = pmc.listRelatives(self.created_ik_jnts[-2], children=1)[1]
        ik_effector.rename("{0}_ik_EFF".format(self.model.module_name))

        ik_shape = rig_lib.medium_cube("{0}_wrist_ik_CTRL_shape".format(self.model.module_name))
        ik_ctrl = rig_lib.create_jnttype_ctrl("{0}_wrist_ik_CTRL".format(self.model.module_name), ik_shape, drawstyle=2,
                                              rotateorder=3)
        pmc.select(d=1)
        ik_ctrl_ofs = pmc.joint(p=(0, 0, 0), n="{0}_wrist_ik_ctrl_OFS".format(self.model.module_name))
        ik_ctrl_ofs.setAttr("rotateOrder", 3)
        ik_ctrl_ofs.setAttr("drawStyle", 2)
        pmc.parent(ik_ctrl, ik_ctrl_ofs)
        fk_ctrl_01_value = pmc.xform(self.created_fk_ctrls[0], q=1, rotation=1)
        fk_ctrl_02_value = pmc.xform(self.created_fk_ctrls[1], q=1, rotation=1)
        fk_ctrl_03_value = pmc.xform(self.created_fk_ctrls[2], q=1, rotation=1)
        self.created_fk_ctrls[0].setAttr("rotate", (0, 0, 0))
        self.created_fk_ctrls[1].setAttr("rotate", (0, 0, 0))
        self.created_fk_ctrls[2].setAttr("rotate", (0, 0, 0))

        ik_ctrl_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[2], q=1, ws=1, translation=1))
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
        const.setAttr("target[0].targetOffsetRotate", (90 * (1 - self.side_coef), 0, 90 * -self.side_coef))
        const.setAttr("target[0].targetOffsetTranslate", (0, 0, 0))
        ik_ctrl.scaleX >> self.created_ik_jnts[-1].scaleY
        ik_ctrl.scaleY >> self.created_ik_jnts[-1].scaleX
        ik_ctrl.scaleZ >> self.created_ik_jnts[-1].scaleZ

        self.created_ik_ctrls = [ik_ctrl, pole_vector]

        self.created_fk_ctrls[0].setAttr("rotate", fk_ctrl_01_value)
        self.created_fk_ctrls[1].setAttr("rotate", fk_ctrl_02_value)
        self.created_fk_ctrls[2].setAttr("rotate", fk_ctrl_03_value)

        pmc.xform(pole_vector, ws=1, translation=(pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)))

        ik_handle.setAttr("visibility", 0)

        self.wrist_fk_pos_reader = pmc.spaceLocator(p=(0, 0, 0), n="{0}_wrist_fk_pos_reader_LOC".format(self.model.module_name))
        self.wrist_fk_pos_reader.setAttr("rotateOrder", 3)
        self.wrist_fk_pos_reader.setAttr("visibility", 0)
        pmc.parent(self.wrist_fk_pos_reader, self.created_fk_ctrls[-1], r=1)
        self.wrist_fk_pos_reader.setAttr("rotate", (90 * (1 - self.side_coef), 0, 90))
        rig_lib.clean_ctrl(self.wrist_fk_pos_reader, 0, trs="trs")

        pmc.xform(ik_ctrl, ws=1,
                  translation=(pmc.xform(self.created_fk_jnts[-1], q=1, ws=1, translation=1)))
        pmc.xform(ik_ctrl, ws=1, rotation=(pmc.xform(self.wrist_fk_pos_reader, q=1, ws=1, rotation=1)))

    def create_local_spaces(self):
        spaces_names = []
        space_locs = []
        for space in self.model.space_list:
            name = str(space).replace("_OUTPUT", "")
            if "local_ctrl" in name:
                name = "world"
            spaces_names.append(name)

            space_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_{1}_SPACELOC".format(self.model.module_name, name))
            space_locs.append(space_loc)

        self.created_fk_ctrls[0].addAttr("space", attributeType="enum", enumName=spaces_names, hidden=0, keyable=1)
        self.created_ik_ctrls[0].addAttr("space", attributeType="enum", enumName=spaces_names, hidden=0, keyable=1)

        for i, space in enumerate(self.model.space_list):
            space_locs[i].setAttr("translate", pmc.xform(self.created_skn_jnts[0], q=1, ws=1, translation=1))
            pmc.parent(space_locs[i], space)

            fk_space_const = pmc.orientConstraint(space_locs[i], self.created_fk_ctrls[0].getParent(), maintainOffset=1)
            ik_space_const = pmc.parentConstraint(space_locs[i], self.created_ik_ctrls[0].getParent(), maintainOffset=1)
            jnt_const_grp_const = pmc.orientConstraint(space_locs[i], self.jnt_const_group, maintainOffset=1)
            pole_vector_const = pmc.parentConstraint(space_locs[i], self.created_ik_ctrls[1].getParent(), maintainOffset=1)

            rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(fk_space_const, space_locs[i], i),
                                                    self.created_fk_ctrls[0].space, i,
                                                    "{0}_{1}_COND".format(self.created_fk_ctrls[0], name))
            rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(ik_space_const, space_locs[i], i),
                                                    self.created_ik_ctrls[0].space, i,
                                                    "{0}_{1}_COND".format(self.created_ik_ctrls[0], name))
            rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(jnt_const_grp_const, space_locs[i], i),
                                                    self.created_fk_ctrls[0].space, i,
                                                    "{0}_{1}_COND".format(self.jnt_const_group, name))
            rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(pole_vector_const, space_locs[i], i),
                                                    self.created_ik_ctrls[0].space, i,
                                                    "{0}_{1}_COND".format(self.created_ik_ctrls[1], name))

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
            rig_lib.clean_ctrl(self.clavicle_ctrl, color_value, trs="s")
            rig_lib.clean_ctrl(self.clavicle_ik_ctrl, color_value, trs="rs",
                               visibility_dependence=self.option_ctrl.clavicleIkCtrl)

        rig_lib.clean_ctrl(self.created_fk_ctrls[0], color_value, trs="ts",
                           visibility_dependence=invert_value.output1D)
        rig_lib.clean_ctrl(self.created_fk_ctrls[0].getParent(), color_value, trs="trs")
        rig_lib.clean_ctrl(self.created_fk_ctrls[1], color_value, trs="ts", visibility_dependence=invert_value.output1D)
        rig_lib.clean_ctrl(self.created_fk_ctrls[2], color_value, trs="t", visibility_dependence=invert_value.output1D)

        rig_lib.clean_ctrl(self.created_ik_ctrls[0], color_value, trs="", visibility_dependence=self.option_ctrl.fkIk)
        rig_lib.clean_ctrl(self.created_ik_ctrls[0].getParent(), color_value, trs="trs")
        rig_lib.clean_ctrl(self.created_ik_ctrls[1], color_value, trs="rs", visibility_dependence=self.option_ctrl.fkIk)

    def create_output(self):
        if self.model.clavicle_creation_switch:
            rig_lib.create_output(name="{0}_clavicle_OUTPUT".format(self.model.module_name), parent=self.clavicle_jnt)
        rig_lib.create_output(name="{0}_shoulder_OUTPUT".format(self.model.module_name), parent=self.created_skn_jnts[0])
        rig_lib.create_output(name="{0}_elbow_OUTPUT".format(self.model.module_name), parent=self.created_skn_jnts[1])
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
        self.space_list = []
