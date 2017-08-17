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
        self.how_many_jnts = QtWidgets.QSpinBox()
        self.how_many_ctrls = QtWidgets.QSpinBox()
        self.IK_creation_switch = QtWidgets.QCheckBox()
        self.stretch_creation_switch = QtWidgets.QCheckBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.IK_creation_switch.setChecked(self.model.IK_creation_switch)
        self.stretch_creation_switch.setChecked(self.model.stretch_creation_switch)
        self.how_many_ctrls.setValue(self.model.how_many_ctrls)
        self.how_many_jnts.setValue(self.model.how_many_jnts)
        self.ctrl.look_for_parent()

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        self.how_many_jnts.setMinimum(1)
        self.how_many_jnts.valueChanged.connect(self.ctrl.on_how_many_jnts_changed)
        self.how_many_ctrls.setMinimum(2)
        self.how_many_ctrls.valueChanged.connect(self.ctrl.on_how_many_ctrls_changed)

        self.IK_creation_switch.stateChanged.connect(self.ctrl.on_IK_creation_switch_changed)
        self.stretch_creation_switch.stateChanged.connect(self.ctrl.on_stretch_creation_switch_changed)

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

        how_many_layout = QtWidgets.QVBoxLayout()
        jnts_layout = QtWidgets.QVBoxLayout()
        jnts_text = QtWidgets.QLabel("How many jnts :")
        jnts_layout.addWidget(jnts_text)
        jnts_layout.addWidget(self.how_many_jnts)
        ctrls_layout = QtWidgets.QVBoxLayout()
        ctrls_text = QtWidgets.QLabel("How many ctrls :")
        ctrls_layout.addWidget(ctrls_text)
        ctrls_layout.addWidget(self.how_many_ctrls)

        how_many_layout.addLayout(jnts_layout)
        how_many_layout.addLayout(ctrls_layout)

        checkbox_layout = QtWidgets.QVBoxLayout()
        ik_layout = QtWidgets.QHBoxLayout()
        ik_text = QtWidgets.QLabel("IK ctrls :")
        ik_layout.addWidget(ik_text)
        ik_layout.addWidget(self.IK_creation_switch)
        stretch_layout = QtWidgets.QHBoxLayout()
        stretch_text = QtWidgets.QLabel("stretch/squash :")
        stretch_layout.addWidget(stretch_text)
        stretch_layout.addWidget(self.stretch_creation_switch)

        checkbox_layout.addLayout(ik_layout)
        checkbox_layout.addLayout(stretch_layout)

        options_layout.addLayout(how_many_layout)
        options_layout.addLayout(checkbox_layout)

        main_layout.addWidget(select_parent_grp)
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
        self.guide = None
        self.guide_name = "None"
        self.jnt_input_grp = None
        self.ctrl_input_grp = None
        self.parts_grp = None
        self.created_jnts = []
        self.ik_spline = None
        self.created_locs = []
        self.created_ctrls = []
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

    def prebuild(self):
        self.guide_name = "{0}_GUIDE".format(self.model.module_name)
        if self.guide_check():
            self.guide = pmc.rebuildCurve(self.guide_name, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0, s=(self.model.how_many_ctrls - 1),
                             d=3, ch=0, replaceOriginal=1)[0]
            return
        self.guide = rig_lib.create_curve_guide(d=3, number_of_points=self.model.how_many_ctrls, name=self.guide_name)
        if not pmc.objExists("guide_GRP"):
            pmc.group(em=1, n="guide_GRP")
        pmc.parent(self.guide, "guide_GRP")
        self.view.refresh_view()

    def on_how_many_jnts_changed(self, value):
        self.model.how_many_jnts = value

    def on_how_many_ctrls_changed(self, value):
        self.model.how_many_ctrls = value

    def on_IK_creation_switch_changed(self, state):
        self.model.IK_creation_switch = is_checked(state)

    def on_stretch_creation_switch_changed(self, state):
        self.model.stretch_creation_switch = is_checked(state)

    def on_modules_cbbox_changed(self, text):
        if self.has_updated_modules:
            self.model.selected_module = text
            self.look_for_parent()

    def on_outputs_cbbox_changed(self, text):
        if self.has_updated_outputs:
            self.model.selected_output = text

    def execute(self):
        self.created_ctrls = []
        self.created_locs = []
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()
        self.create_jnts()
        self.create_ikspline()
        self.create_fk()
        self.connect_stretch()


    def guide_check(self):
        if not pmc.objExists("guide_GRP"):
            return False
        if not pmc.objExists("guide_GRP|{0}".format(self.guide_name)):
            return False
        return True

    def delete_existing_objects(self):
        if rig_lib.exists_check("{0}_jnt_INPUT".format(self.model.module_name)):
            pmc.delete("{0}_jnt_INPUT".format(self.model.module_name))
        if rig_lib.exists_check("{0}_ctrl_INPUT".format(self.model.module_name)):
            pmc.delete("{0}_ctrl_INPUT".format(self.model.module_name))

    def connect_to_parent(self):
        check_list = ["CTRL_GRP", "JNT_GRP", "PARTS_GRP"]
        if not rig_lib.exists_check(check_list):
            print("No necessary groups created for module {0}".format(self.model.module_name))
            return

        self.jnt_input_grp = pmc.group(em=1, n="{0}_jnt_INPUT".format(self.model.module_name))
        self.ctrl_input_grp = pmc.group(em=1, n="{0}_ctrl_INPUT".format(self.model.module_name))
        self.parts_grp = pmc.group(em=1, n="{0}_parts_GRP".format(self.model.module_name))

        if self.model.selected_module != "No_parent":
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

    def create_jnts(self):
        guide_rebuilded = pmc.rebuildCurve(self.guide, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                           s=self.model.how_many_jnts, d=1, ch=0, replaceOriginal=0)[0]
        guide_rebuilded.rename("{0}_temp_rebuilded_GUIDE".format(self.model.module_name))
        vertex_list = guide_rebuilded.cv[:]
        self.created_jnts = rig_lib.create_jnts_from_cv_list_and_return_jnts_list(vertex_list, guide_rebuilded,
                                                                                  self.model.module_name)
        pmc.parent(self.created_jnts[0], self.jnt_input_grp, r=1)

        rig_lib.change_jnt_chain_suffix(self.created_jnts, new_suffix="SKN")

        pmc.delete(guide_rebuilded)

    def create_ikspline(self):
        self.ik_spline = pmc.rebuildCurve(self.guide, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0, s=(self.model.how_many_ctrls - 1),
                             d=3, ch=0, replaceOriginal=0)[0]
        self.ik_spline.rename("{0}_ik_CRV".format(self.model.module_name))
        ik_handle = pmc.ikHandle(n=("{0}_ik_HDL".format(self.model.module_name)), startJoint=self.created_jnts[0],
                                 endEffector=self.created_jnts[-1], solver="ikSplineSolver", curve=self.ik_spline,
                                 createCurve=False, parentCurve=False)[0]
        pmc.parent(self.ik_spline, self.parts_grp, r=1)
        pmc.parent(ik_handle, self.parts_grp, r=1)
        ik_effector = pmc.listRelatives(self.created_jnts[-2], children=1)[1]
        ik_effector.rename("{0}_ik_EFF".format(self.model.module_name))

    def create_fk(self):
        ik_spline_cv_list = []
        for i, cv in enumerate(self.guide.cv):
            ik_spline_cv_list.append(cv)
        ik_spline_cv_for_ctrls = ik_spline_cv_list
        del ik_spline_cv_for_ctrls[1]
        del ik_spline_cv_for_ctrls[-2]

        ik_spline_controlpoints_list = []
        for i, cv in enumerate(self.ik_spline.controlPoints):
            ik_spline_controlpoints_list.append(cv)
        ik_spline_controlpoints_for_ctrls = ik_spline_controlpoints_list[:]
        del ik_spline_controlpoints_for_ctrls[1]
        del ik_spline_controlpoints_for_ctrls[-2]

        for i, cv in enumerate(ik_spline_cv_for_ctrls):
            cv_loc = self.create_locators(i, cv, ik_spline_controlpoints_for_ctrls)
            self.create_ctrls(i, cv_loc)
            self.created_locs.append(cv_loc)
        self.constrain_ikspline_tan_to_ctrls(ik_spline_controlpoints_list)
        self.ik_spline.setAttr("translate", (0, 0, 0))
        self.ik_spline.setAttr("rotate", (0, 0, 0))

    def create_locators(self, i, cv, ik_spline_controlpoints_for_ctrls):
        cv_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_{1}_pos".format(self.model.module_name, (i + 1)))
        cv_loc.setAttr("translate", pmc.xform(cv, q=1, ws=1, translation=1))
        cv_loc_shape = cv_loc.getShape()
        cv_loc_shape.worldPosition >> ik_spline_controlpoints_for_ctrls[i]
        return cv_loc

    def create_ctrls(self, i, cv_loc):
        ctrl = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=3, d=3, s=8,
                          n="{0}_{1}_CTRL".format(self.model.module_name, (i + 1)), ch=0)[0]
        ctrl_ofs = pmc.group(ctrl, n="{0}_{1}_ctrl_OFS".format(self.model.module_name, (i + 1)))
        value = 1.0 / (self.model.how_many_ctrls - 1) * i
        ctrl_ofs.setAttr("translate", self.guide.getPointAtParam(value, space="world"))
        if i == 0:
            pmc.parent(ctrl_ofs, self.ctrl_input_grp, r=0)
        else:
            pmc.parent(ctrl_ofs, "{0}_{1}_CTRL".format(self.model.module_name, i), r=0)
        pmc.parent(cv_loc, ctrl, r=0)
        self.created_ctrls.append(ctrl)

    def constrain_ikspline_tan_to_ctrls(self, ik_spline_controlpoints_list):
        first_tan_cv_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_first_tan_pos".format(self.model.module_name))
        last_tan_cv_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_last_tan_pos".format(self.model.module_name))
        first_tan_cv_loc.setAttr("translate", pmc.xform(self.ik_spline.cv[1], q=1, ws=1, translation=1))
        last_tan_cv_loc.setAttr("translate", pmc.xform(self.ik_spline.cv[-2], q=1, ws=1, translation=1))
        first_tan_cv_loc_shape = first_tan_cv_loc.getShape()
        last_tan_cv_loc_shape = last_tan_cv_loc.getShape()
        first_tan_cv_loc_shape.worldPosition >> self.ik_spline.controlPoints[1]
        last_tan_cv_loc_shape.worldPosition >> self.ik_spline.controlPoints[len(ik_spline_controlpoints_list) - 2]

        # TODO: a voir si on garde tel quel ou si on change de methode pour gerer les tangentes de la curve ik_spline
        pmc.parent(first_tan_cv_loc, self.created_locs[0], r=0)
        pmc.parent(last_tan_cv_loc, self.created_locs[-1], r=0)

    def connect_stretch(self):
        crv_info = pmc.createNode("curveInfo", n="{0}_CURVEINFO".format(self.model.module_name))
        global_stretch = pmc.createNode("multDoubleLinear", n="{0}_global_stretch_MDL".format(self.model.module_name))
        neck_stretch_div = pmc.createNode("multiplyDivide", n="{0}_stretch_MDIV".format(self.model.module_name))
        neck_stretch_mult = pmc.createNode("multDoubleLinear", n="{0}stretch_MDL".format(self.model.module_name))
        self.jnt_input_grp.addAttr("baseArcLength", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        self.jnt_input_grp.addAttr("baseTranslateX", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        crv_shape = self.ik_spline.getShape()
        global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]

        crv_shape.worldSpace[0] >> crv_info.inputCurve
        base_arc_length = crv_info.getAttr("arcLength")
        self.jnt_input_grp.setAttr("baseArcLength", base_arc_length)
        base_translate_x = self.created_jnts[1].getAttr("translateX")
        self.jnt_input_grp.setAttr("baseTranslateX", base_translate_x)
        global_scale.output >> global_stretch.input1
        self.jnt_input_grp.baseArcLength >> global_stretch.input2
        crv_info.arcLength >> neck_stretch_div.input1X
        global_stretch.output >> neck_stretch_div.input2X
        neck_stretch_div.setAttr("operation", 2)
        neck_stretch_div.outputX >> neck_stretch_mult.input1
        self.jnt_input_grp.baseTranslateX >> neck_stretch_mult.input2

        for jnt in self.created_jnts:
            if not jnt == self.created_jnts[0]:
                neck_stretch_mult.output >> jnt.translateX


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.how_many_jnts = 10
        self.how_many_ctrls = 4
        self.IK_creation_switch = True
        self.stretch_creation_switch = True
