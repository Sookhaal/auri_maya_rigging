from PySide2 import QtWidgets, QtCore, QtGui

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, is_checked, grpbox
from auri.scripts.Maya_Scripts import rig_lib

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


class Controller(AuriScriptController):
    def __init__(self, model, view):
        """

        Args:
            model (Model):
            view (View):
        """
        self.model = model
        self.view = view
        self.modules_with_output = QtGui.QStringListModel()
        self.outputs_model = QtGui.QStringListModel()
        self.has_updated_modules = False
        self.has_updated_outputs = False
        self.current_module = None
        self.guides = []
        self.guides_names = []
        self.side = {}
        self.side_coef = 1
        self.jnt_input_grp = None
        self.ctrl_input_grp = None
        self.parts_grp = None
        self.created_skn_jnts = []
        self.created_fk_jnts = []
        self.created_ik_jnts = []
        self.created_fk_ctrls = []
        self.created_ik_ctrls = []
        self.option_ctrl = None
        AuriScriptController.__init__(self)

    def look_for_parent(self):
        if not pmc.objExists("temporary_output"):
            return
        temp_output = pmc.ls("temporary_output")[0]

        self.has_updated_modules = False
        list_children = rig_lib.list_children(temp_output)
        list_children.append("No_parent")
        self.modules_with_output.setStringList(list_children)
        self.model.selected_module = rig_lib.cbbox_set_selected(self.model.selected_module, self.view.modules_cbbox)
        self.has_updated_modules = True

        if self.model.selected_module == "No_parent":
            self.outputs_model.removeRows(0, self.outputs_model.rowCount())
            return
        self.current_module = pmc.ls(self.model.selected_module)[0]
        self.has_updated_outputs = False
        self.outputs_model.setStringList(rig_lib.list_children(self.current_module))
        self.model.selected_output = rig_lib.cbbox_set_selected(self.model.selected_output, self.view.outputs_cbbox)
        self.has_updated_outputs = True

    def on_ik_creation_switch_changed(self, state):
        self.model.ik_creation_switch = is_checked(state)

    def on_stretch_creation_switch_changed(self, state):
        self.model.stretch_creation_switch = is_checked(state)

    def on_side_cbbox_changed(self, text):
        self.model.side = text

    def on_modules_cbbox_changed(self, text):
        if self.has_updated_modules:
            self.model.selected_module = text
            self.look_for_parent()

    def on_outputs_cbbox_changed(self, text):
        if self.has_updated_outputs:
            self.model.selected_output = text

    def prebuild(self):
        self.guides_names = ["{0}_{1}_shoulder_GUIDE".format(self.model.side, self.model.module_name),
                             "{0}_{1}_elbow_GUIDE".format(self.model.side, self.model.module_name),
                             "{0}_{1}_wrist_GUIDE".format(self.model.side, self.model.module_name)]
        if self.guide_check():
            self.guides = pmc.ls("{0}_{1}_shoulder_GUIDE".format(self.model.side, self.model.module_name),
                                 "{0}_{1}_elbow_GUIDE".format(self.model.side, self.model.module_name),
                                 "{0}_{1}_wrist_GUIDE".format(self.model.side, self.model.module_name))
            return
        shoulder_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0])
        elbow_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[1])
        wrist_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[2])

        self.side = {"Left": 1, "Right": -1}
        self.side_coef = self.side.get(self.model.side)
        shoulder_guide.setAttr("translate", (3 * self.side_coef, 10, 0))
        elbow_guide.setAttr("translate", (5 * self.side_coef, 8, 0))
        wrist_guide.setAttr("translate", (7 * self.side_coef, 6, 0))

        self.guides = [shoulder_guide, elbow_guide, wrist_guide]
        if not pmc.objExists("{0}_{1}_guides".format(self.model.side, self.model.module_name)):
            pmc.group(em=1, n="{0}_{1}_guides".format(self.model.side, self.model.module_name))
        guides_grp = pmc.ls("{0}_{1}_guides".format(self.model.side, self.model.module_name))[0]
        for guide in self.guides:
            pmc.parent(guide, guides_grp, r=0)
        if not pmc.objExists("guide_GRP"):
            pmc.group(em=1, n="guide_GRP")
        pmc.parent(guides_grp, "guide_GRP")
        guides_grp.setAttr("visibility", 1)
        self.view.refresh_view()
        pmc.select(d=1)

    def guide_check(self):
        if not pmc.objExists("guide_GRP"):
            return False
        if not pmc.objExists("guide_GRP|{0}_{1}_guides".format(self.model.side, self.model.module_name)):
            return False
        for guide in self.guides_names:
            if not pmc.objExists("guide_GRP|{0}_{1}_guides|{2}".format(self.model.side, self.model.module_name, guide)):
                return False
        return True

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

    def delete_existing_objects(self):
        if rig_lib.exists_check("{0}_jnt_INPUT".format(self.model.module_name)):
            pmc.delete("{0}_jnt_INPUT".format(self.model.module_name))
        if rig_lib.exists_check("{0}_ctrl_INPUT".format(self.model.module_name)):
            pmc.delete("{0}_ctrl_INPUT".format(self.model.module_name))
        if rig_lib.exists_check("{0}_parts_GRP".format(self.model.module_name)):
            pmc.delete("{0}_parts_GRP".format(self.model.module_name))

    def connect_to_parent(self):
        check_list = ["CTRL_GRP", "JNT_GRP", "PARTS_GRP"]
        if not rig_lib.exists_check(check_list):
            print("No necessary groups created for module {0}".format(self.model.module_name))
            return

        self.jnt_input_grp = pmc.group(em=1, n="{0}_jnt_INPUT".format(self.model.module_name))
        self.ctrl_input_grp = pmc.group(em=1, n="{0}_ctrl_INPUT".format(self.model.module_name))
        self.parts_grp = pmc.group(em=1, n="{0}_parts_GRP".format(self.model.module_name))

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
                                 n="{0}_{1}_shoulder_SKN".format(self.model.side, self.model.module_name))
        shoulder_jnt.setAttr("rotate", pmc.xform(duplicates_guides[0], q=1, rotation=1))
        if self.model.side == "Right":
            shoulder_jnt.setAttr("jointOrientX", -180)
            shoulder_jnt.setAttr("rotate", (pmc.xform(shoulder_jnt, q=1, rotation=1)[0] + 180,
                                            pmc.xform(shoulder_jnt, q=1, rotation=1)[1] * -1,
                                            pmc.xform(shoulder_jnt, q=1, rotation=1)[2] * -1))
        elbow_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1)),
                              n="{0}_{1}_elbow_SKN".format(self.model.side, self.model.module_name))
        elbow_jnt.setAttr("rotate", pmc.xform(duplicates_guides[1], q=1, rotation=1))
        wrist_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)),
                              n="{0}_{1}_wrist_SKN".format(self.model.side, self.model.module_name))

        pmc.parent(shoulder_jnt, self.jnt_input_grp, r=0)
        self.created_skn_jnts = [shoulder_jnt, elbow_jnt, wrist_jnt]

        pmc.delete(duplicates_guides[:])

    def create_options_ctrl(self):
        self.option_ctrl = rig_lib.little_cube("{0}_{1}_option_CTRL".format(self.model.side, self.model.module_name))
        option_ofs = pmc.group(self.option_ctrl, n="{0}_{1}_option_ctrl_OFS".format(self.model.side,
                                                                                    self.model.module_name), r=1)
        pmc.parent(option_ofs, self.ctrl_input_grp)
        rig_lib.matrix_constraint(self.created_skn_jnts[-1], option_ofs, srt="trs")
        ctrl_shape = self.option_ctrl.getShape()
        pmc.move(ctrl_shape, [0, 0, -2 * self.side_coef], relative=1, objectSpace=1, worldSpaceDistance=1)
        self.option_ctrl.addAttr("fkIk", attributeType="float", defaultValue=0, hidden=0, keyable=1, hasMaxValue=1,
                                 hasMinValue=1, maxValue=1, minValue=0)

    def create_and_connect_fk_ik_jnts(self):
        shoulder_fk_jnt = \
        self.created_skn_jnts[0].duplicate(n="{0}_{1}_shoulder_fk_JNT".format(self.model.side, self.model.module_name))[
            0]
        elbow_fk_jnt = \
        pmc.ls("{0}_{1}_shoulder_fk_JNT|{0}_{1}_elbow_SKN".format(self.model.side, self.model.module_name))[0]
        wrist_fk_jnt = pmc.ls("{0}_{1}_shoulder_fk_JNT|{0}_{1}_elbow_SKN|{0}_{1}_wrist_SKN".format(self.model.side,
                                                                                                   self.model.module_name))[
            0]
        elbow_fk_jnt.rename("{0}_{1}_elbow_fk_JNT".format(self.model.side, self.model.module_name))
        wrist_fk_jnt.rename("{0}_{1}_wrist_fk_JNT".format(self.model.side, self.model.module_name))
        self.created_fk_jnts = [shoulder_fk_jnt, elbow_fk_jnt, wrist_fk_jnt]

        shoulder_ik_jnt = \
        self.created_skn_jnts[0].duplicate(n="{0}_{1}_shoulder_ik_JNT".format(self.model.side, self.model.module_name))[
            0]
        elbow_ik_jnt = \
        pmc.ls("{0}_{1}_shoulder_ik_JNT|{0}_{1}_elbow_SKN".format(self.model.side, self.model.module_name))[0]
        wrist_ik_jnt = pmc.ls("{0}_{1}_shoulder_ik_JNT|{0}_{1}_elbow_SKN|{0}_{1}_wrist_SKN".format(self.model.side,
                                                                                                   self.model.module_name))[
            0]
        elbow_ik_jnt.rename("{0}_{1}_elbow_ik_JNT".format(self.model.side, self.model.module_name))
        wrist_ik_jnt.rename("{0}_{1}_wrist_ik_JNT".format(self.model.side, self.model.module_name))
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
                                   n="{0}_{1}_shoulder_fk_CTRL".format(self.model.side, self.model.module_name), ch=0)[
            0]
        shoulder_ofs = pmc.group(shoulder_ctrl,
                                 n="{0}_{1}_shoulder_fk_ctrl_OFS".format(self.model.side, self.model.module_name))
        shoulder_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[0], q=1, ws=1, translation=1))
        shoulder_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[0], q=1, ws=1, rotation=1))
        shoulder_ctrl.setAttr("rotateOrder", 0)
        pmc.parent(shoulder_ofs, self.ctrl_input_grp, r=0)

        elbow_ctrl = pmc.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=2, d=3, s=8,
                                n="{0}_{1}_elbow_fk_CTRL".format(self.model.side, self.model.module_name), ch=0)[0]
        elbow_ofs = pmc.group(elbow_ctrl,
                              n="{0}_{1}_elbow_fk_ctrl_OFS".format(self.model.side, self.model.module_name))
        elbow_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1))
        elbow_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[1], q=1, rotation=1))
        elbow_ctrl.setAttr("rotateOrder", 0)
        pmc.parent(elbow_ofs, shoulder_ctrl, r=0)
        elbow_ofs.setAttr("rotate", (0, 0, 0))

        wrist_ctrl = pmc.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=2, d=3, s=8,
                                n="{0}_{1}_wrist_fk_CTRL".format(self.model.side, self.model.module_name), ch=0)[0]
        wrist_ofs = pmc.group(wrist_ctrl,
                              n="{0}_{1}_wrist_fk_ctrl_OFS".format(self.model.side, self.model.module_name))
        wrist_ofs.setAttr("translate", pmc.xform(self.created_fk_jnts[2], q=1, ws=1, translation=1))
        wrist_ctrl.setAttr("rotate", pmc.xform(self.created_fk_jnts[2], q=1, rotation=1))
        wrist_ctrl.setAttr("rotateOrder", 0)
        pmc.parent(wrist_ofs, elbow_ctrl, r=0)
        wrist_ofs.setAttr("rotate", (0, 0, 0))

        self.created_fk_ctrls = [shoulder_ctrl, elbow_ctrl, wrist_ctrl]

        for i, ctrl in enumerate(self.created_fk_ctrls):
            ctrl.rotate >> self.created_fk_jnts[i].rotate

    def create_ik(self):
        ik_handle = pmc.ikHandle(n=("{0}_{1}_ik_HDL".format(self.model.side, self.model.module_name)),
                                 startJoint=self.created_ik_jnts[0], endEffector=self.created_ik_jnts[-1],
                                 solver="ikRPsolver")[0]
        ik_effector = pmc.listRelatives(self.created_ik_jnts[-2], children=1)[1]
        ik_effector.rename("{0}_{1}_ik_EFF".format(self.model.side, self.model.module_name))

        ik_ctrl = rig_lib.medium_cube("{0}_{1}_wrist_ik_CTRL".format(self.model.side, self.model.module_name))
        ik_ctrl_ofs = pmc.group(ik_ctrl, n="{0}_{1}_wrist_ik_ctrl_OFS".format(self.model.side, self.model.module_name))

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

        pole_vector = rig_lib.jnt_shape_curve("{0}_{1}_poleVector_CTRL".format(self.model.side, self.model.module_name))
        pv_ofs = pmc.group(pole_vector, n="{0}_{1}_poleVector_ctrl_OFS".format(self.model.side, self.model.module_name))
        pv_ofs.setAttr("translate", (pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[0],
                                     pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[1],
                                     pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[2] -
                                     pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)[0]))
        pmc.poleVectorConstraint(pole_vector, ik_handle)
        pmc.parent(pv_ofs, self.ctrl_input_grp, r=0)

        self.created_ik_jnts[1].setAttr("preferredAngleY", -90)

        self.created_fk_ctrls[0].setAttr("rotate", fk_ctrl_01_value)
        self.created_fk_ctrls[1].setAttr("rotate", fk_ctrl_02_value)
        self.created_fk_ctrls[2].setAttr("rotate", fk_ctrl_03_value)

        pmc.xform(pole_vector, ws=1, translation=(pmc.xform(self.created_fk_jnts[1], q=1, ws=1, translation=1)))
        pmc.xform(ik_ctrl, ws=1, translation=(pmc.xform(self.created_fk_jnts[-1], q=1, ws=1, translation=1)))


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.side = "Left"
        self.ik_creation_switch = True
        self.stretch_creation_switch = True
        # self.bend_creation_switch = False
