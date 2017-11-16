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
        self.how_many_jnts = QtWidgets.QSpinBox()
        self.how_many_ctrls = QtWidgets.QSpinBox()
        self.ik_creation_switch = QtWidgets.QCheckBox()
        self.stretch_creation_switch = QtWidgets.QCheckBox()
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
        self.how_many_ctrls.setValue(self.model.how_many_ctrls)
        self.how_many_jnts.setValue(self.model.how_many_jnts)
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

        self.how_many_jnts.setMinimum(1)
        self.how_many_jnts.valueChanged.connect(self.ctrl.on_how_many_jnts_changed)
        self.how_many_ctrls.setMinimum(2)
        self.how_many_ctrls.valueChanged.connect(self.ctrl.on_how_many_ctrls_changed)

        self.ik_creation_switch.stateChanged.connect(self.ctrl.on_ik_creation_switch_changed)
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
        ik_layout.addWidget(self.ik_creation_switch)
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
        self.guide = None
        self.guide_name = "None"
        self.created_jnts = []
        self.ik_spline = None
        self.created_locs = []
        self.created_fk_ctrls = []
        self.created_ik_ctrls = []
        self.jnts_to_skin = []
        RigController.__init__(self,  model, view)

    def prebuild(self):
        temp_outputs = ["start_OUTPUT", "end_OUTPUT"]
        for i in xrange(self.model.how_many_jnts):
            temp_output = "jnt_{0}_OUTPUT".format(i)
            temp_outputs.append(temp_output)
        self.create_temporary_outputs(temp_outputs)

        self.guide_name = "{0}_GUIDE".format(self.model.module_name)
        d = 3
        nb_points = self.model.how_many_ctrls - 2
        if self.model.how_many_ctrls < 4:
            d = 3 + self.model.how_many_ctrls - 4
            nb_points = 2
        if self.guide_check(self.guide_name):
            self.guide = pmc.ls(self.guide_name)[0]
            if d != 2 and (self.guide.getShape().getAttr("spans") != nb_points - 1 or
                           self.guide.getShape().getAttr("degree") != d):
                self.guide = pmc.rebuildCurve(self.guide_name, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                              s=(nb_points - 1), d=d, ch=0, replaceOriginal=1)[0]
            elif self.guide.getShape().getAttr("spans") != nb_points - 1 or self.guide.getShape().getAttr("degree") != d:
                self.guide = pmc.rebuildCurve(self.guide_name, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                              s=3, d=d, ch=0, replaceOriginal=1)[0]
                pmc.delete(self.guide.cv[-2])
                pmc.delete(self.guide.cv[1])
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            self.guides_grp.setAttr("visibility", 1)
            self.view.refresh_view()
            pmc.select(d=1)
            return

        self.guide = rig_lib.create_curve_guide(d=d, number_of_points=nb_points, name=self.guide_name, hauteur_curve=3)
        self.guides_grp = self.group_guides(self.guide)
        self.guide.setAttr("translate", (0, 20, 0))
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.created_locs = []
        self.created_fk_ctrls = []
        self.created_ik_ctrls = []
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()
        self.create_jnts()
        self.create_ikspline()
        self.create_fk()
        self.activate_twist()
        if self.model.stretch_creation_switch == 1:
            if self.model.how_many_ctrls == 2:
                self.connect_ik_spline_stretch(self.ik_spline, self.created_jnts)
            else:
                self.connect_ik_spline_stretch(self.ik_spline, self.created_jnts, measure_type="accurate")
        if self.model.ik_creation_switch == 1:
            self.create_ik()
        self.create_outputs()
        self.create_local_spaces()
        self.clean_rig()
        pmc.select(d=1)

    def create_jnts(self):
        guide_rebuilded = pmc.rebuildCurve(self.guide, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                           s=self.model.how_many_jnts, d=1, ch=0, replaceOriginal=0)[0]
        if self.model.how_many_jnts == 2:
            pmc.delete(guide_rebuilded.cv[-2])
            pmc.delete(guide_rebuilded.cv[1])
        guide_rebuilded.rename("{0}_temp_rebuilded_GUIDE".format(self.model.module_name))
        vertex_list = guide_rebuilded.cv[:]
        self.created_jnts = rig_lib.create_jnts_from_cv_list_and_return_jnts_list(vertex_list, self.model.module_name)
        pmc.parent(self.created_jnts[0], self.jnt_input_grp, r=0)

        rig_lib.change_jnt_chain_suffix(self.created_jnts[0:-1], new_suffix="SKN")

        pmc.delete(guide_rebuilded)

        self.jnts_to_skin = self.created_jnts[:-1]

    def create_ikspline(self):
        self.ik_spline = pmc.duplicate(self.guide, n="{0}_ik_CRV".format(self.model.module_name))[0]
        ik_handle = pmc.ikHandle(n=("{0}_ik_HDL".format(self.model.module_name)), startJoint=self.created_jnts[0],
                                 endEffector=self.created_jnts[-1], solver="ikSplineSolver", curve=self.ik_spline,
                                 createCurve=False, parentCurve=False)[0]
        pmc.parent(self.ik_spline, self.parts_grp, r=1)
        pmc.parent(ik_handle, self.parts_grp, r=1)
        ik_effector = pmc.listRelatives(self.created_jnts[-2], children=1)[1]
        ik_effector.rename("{0}_ik_EFF".format(self.model.module_name))

        if self.model.how_many_jnts == 1:
            pmc.parent(ik_effector, self.created_jnts[-1])

    def create_fk(self):
        ik_spline_cv_list = []
        for i, cv in enumerate(self.guide.cv):
            ik_spline_cv_list.append(cv)

        ik_spline_controlpoints_list = []
        for i, cv in enumerate(self.ik_spline.controlPoints):
            ik_spline_controlpoints_list.append(cv)

        for i, cv in enumerate(ik_spline_cv_list):
            cv_loc = self.create_locators(i, cv, ik_spline_controlpoints_list)
            self.create_ctrls(i, cv_loc)
            self.created_locs.append(cv_loc)
        self.ik_spline.setAttr("translate", (0, 0, 0))
        self.ik_spline.setAttr("rotate", (0, 0, 0))
        self.ik_spline.setAttr("scale", (1, 1, 1))

    def create_locators(self, i, cv, ik_spline_controlpoints_for_ctrls):
        cv_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_{1}_pos".format(self.model.module_name, (i + 1)))
        cv_loc.setAttr("translate", pmc.xform(cv, q=1, ws=1, translation=1))
        cv_loc_shape = cv_loc.getShape()
        cv_loc_shape.worldPosition >> ik_spline_controlpoints_for_ctrls[i]
        return cv_loc

    def create_ctrls(self, i, cv_loc):
        pmc.select(d=1)
        ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=3, d=3, s=8,
                                n="{0}_{1}_fk_CTRL_shape".format(self.model.module_name, (i + 1)), ch=0)[0]
        ctrl = rig_lib.create_jnttype_ctrl(name="{0}_{1}_fk_CTRL".format(self.model.module_name, (i + 1)), shape=ctrl_shape,
                                           drawstyle=2, rotateorder=2)

        nearest_point_on_curve = pmc.createNode("nearestPointOnCurve", n="temp_NPOC")
        self.guide.worldSpace >> nearest_point_on_curve.inputCurve
        cv_loc.getShape().worldPosition >> nearest_point_on_curve.inPosition
        ctrl.setAttr("translate", nearest_point_on_curve.getAttr("position"))
        # nearest_point_on_curve.position >> ctrl.translate
        pmc.delete(nearest_point_on_curve)

        # ctrl.setAttr("translate", pmc.xform(cv_loc, q=1, ws=1, translation=1))
        if i == 0:
            pmc.parent(ctrl, self.ctrl_input_grp, r=0)
        else:
            pmc.parent(ctrl, "{0}_{1}_fk_CTRL".format(self.model.module_name, i), r=0)
            pmc.reorder(ctrl, front=1)
        pmc.parent(cv_loc, ctrl, r=0)
        self.created_fk_ctrls.append(ctrl)

    def create_ik(self):
        start_shape = rig_lib.box_curve("{0}_start_ik_CTRL_shape".format(self.model.module_name))
        start_ctrl = rig_lib.create_jnttype_ctrl(name="{0}_start_ik_CTRL".format(self.model.module_name), shape=start_shape,
                                                 drawstyle=2, rotateorder=3)

        end_shape = rig_lib.box_curve("{0}_end_ik_CTRL_shape".format(self.model.module_name))
        end_ctrl = rig_lib.create_jnttype_ctrl(name="{0}_end_ik_CTRL".format(self.model.module_name), shape=end_shape,
                                               drawstyle=2, rotateorder=1)

        start_ofs = pmc.group(start_ctrl, n="{0}_start_ik_ctrl_OFS".format(self.model.module_name))
        start_ofs.setAttr("rotateOrder", 3)
        end_ofs = pmc.group(end_ctrl, n="{0}_end_ik_ctrl_OFS".format(self.model.module_name))
        end_ofs.setAttr("rotateOrder", 1)

        start_ofs.setAttr("translate", pmc.xform(self.created_fk_ctrls[0], q=1, ws=1, translation=1))
        start_ofs.setAttr("rotate", pmc.xform(self.created_fk_ctrls[0], q=1, ws=1, rotation=1))
        end_ofs.setAttr("translate", pmc.xform(self.created_fk_ctrls[-1], q=1, ws=1, translation=1))
        end_ofs.setAttr("rotate", pmc.xform(self.created_fk_ctrls[-1], q=1, ws=1, rotation=1))

        pmc.parent(start_ofs, self.ctrl_input_grp, r=0)
        pmc.parent(end_ofs, self.created_fk_ctrls[-2], r=0)
        pmc.parent(self.created_fk_ctrls[-1], end_ctrl, r=0)

        pmc.parent(self.created_locs[0], start_ctrl, r=0)

        self.created_fk_ctrls[-1].setAttr("visibility", 0)

        self.created_ik_ctrls.append(start_ctrl)
        self.created_ik_ctrls.append(end_ctrl)

        if not self.model.how_many_ctrls == 2:
            center_ctrl = (self.model.how_many_ctrls / 2.0) - 0.5
            # for i, loc in enumerate(self.created_locs):
            #     if i == center_ctrl:
            #         const = pmc.parentConstraint(start_ctrl, end_ctrl, loc, maintainOffset=1,
            #                                      skipRotate=["x", "y", "z"])
            #         const.setAttr("{0}W0".format(start_ctrl), 1)
            #         const.setAttr("{0}W1".format(end_ctrl), 1)
            #     elif i < center_ctrl:
            #         const = pmc.parentConstraint(start_ctrl, end_ctrl, loc, maintainOffset=1,
            #                                      skipRotate=["x", "y", "z"])
            #         const.setAttr("{0}W0".format(start_ctrl), 1)
            #         const.setAttr("{0}W1".format(end_ctrl), ((1 / (self.model.how_many_ctrls / 2.0)) * (i / 2.0)))
            #     elif i > center_ctrl:
            #         const = pmc.parentConstraint(start_ctrl, end_ctrl, loc, maintainOffset=1,
            #                                      skipRotate=["x", "y", "z"])
            #         const.setAttr("{0}W0".format(start_ctrl), ((1 / (self.model.how_many_ctrls / 2.0)) *
            #                                                    (((len(self.created_locs) - 1) - i) / 2.0)))
            #         const.setAttr("{0}W1".format(end_ctrl), 1)

            for i, loc in enumerate(self.created_locs):
                if i == center_ctrl:
                    const = pmc.parentConstraint(start_ctrl, end_ctrl, self.created_fk_ctrls[i], loc, maintainOffset=1,
                                                 skipRotate=["x", "y", "z"])
                    const.setAttr("{0}W0".format(start_ctrl), 1)
                    const.setAttr("{0}W1".format(end_ctrl), 1)
                    const.setAttr("{0}W2".format(self.created_fk_ctrls[i]), 1)
                elif i < center_ctrl:
                    const = pmc.parentConstraint(start_ctrl, self.created_fk_ctrls[i], loc, maintainOffset=1,
                                                 skipRotate=["x", "y", "z"])
                    const.setAttr("{0}W0".format(start_ctrl), 1)
                    const.setAttr("{0}W1".format(self.created_fk_ctrls[i]), ((1 / (self.model.how_many_ctrls / 2.0)) *
                                                                             (
                                                                             ((len(self.created_locs) - 1) - i) / 2.0)))
                elif i > center_ctrl:
                    const = pmc.parentConstraint(self.created_fk_ctrls[i], end_ctrl, loc, maintainOffset=1,
                                                 skipRotate=["x", "y", "z"])
                    const.setAttr("{0}W0".format(self.created_fk_ctrls[i]), ((1 / (self.model.how_many_ctrls / 2.0)) *
                                                                             (i / 2.0)))
                    const.setAttr("{0}W1".format(end_ctrl), 1)

    def activate_twist(self):
        ik_handle = pmc.ls("{0}_ik_HDL".format(self.model.module_name))[0]
        ik_handle.setAttr("dTwistControlEnable", 1)
        ik_handle.setAttr("dWorldUpType", 4)
        ik_handle.setAttr("dForwardAxis", 2)
        ik_handle.setAttr("dWorldUpAxis", 4)
        ik_handle.setAttr("dWorldUpVectorX", 0)
        ik_handle.setAttr("dWorldUpVectorY", 0)
        ik_handle.setAttr("dWorldUpVectorZ", -1)
        ik_handle.setAttr("dWorldUpVectorEndX", 0)
        ik_handle.setAttr("dWorldUpVectorEndY", 0)
        ik_handle.setAttr("dWorldUpVectorEndZ", -1)
        self.created_locs[0].worldMatrix[0] >> ik_handle.dWorldUpMatrix
        self.created_locs[-1].worldMatrix[0] >> ik_handle.dWorldUpMatrixEnd

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

        spaces_names.append("local")

        if self.model.ik_creation_switch == 0:
            self.created_fk_ctrls[-1].addAttr("space", attributeType="enum", enumName=spaces_names, hidden=0, keyable=1)
            pmc.group(self.created_fk_ctrls[-1], p=self.created_fk_ctrls[-2],
                      n="{0}_CONSTGRP".format(self.created_fk_ctrls[-1]))

        else:
            self.created_ik_ctrls[-1].addAttr("space", attributeType="enum", enumName=spaces_names, hidden=0, keyable=1)

        for i, space in enumerate(self.model.space_list):
            space_locs[i].setAttr("translate", pmc.xform(self.created_jnts[-1], q=1, ws=1, translation=1))
            pmc.parent(space_locs[i], space)

            if self.model.ik_creation_switch == 0:
                fk_space_const = pmc.orientConstraint(space_locs[i], self.created_fk_ctrls[-1].getParent(), maintainOffset=1)

                rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(fk_space_const, space_locs[i], i),
                                                        self.created_fk_ctrls[-1].space, i,
                                                        "{0}_{1}Space_COND".format(self.created_fk_ctrls[-1], spaces_names[i]))
            else:
                ik_space_const = pmc.orientConstraint(space_locs[i], self.created_ik_ctrls[-1].getParent(), maintainOffset=1)

                rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(ik_space_const, space_locs[i], i),
                                                        self.created_ik_ctrls[-1].space, i,
                                                        "{0}_{1}Space_COND".format(self.created_ik_ctrls[-1], spaces_names[i]))

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        for loc in self.created_locs:
            loc_shape = loc.getShape()
            loc_shape.setAttr("visibility", 0)

        for ctrl in self.created_fk_ctrls:
            rig_lib.clean_ctrl(ctrl, 14, trs="ts")

        if self.model.ik_creation_switch == 1:
            rig_lib.clean_ctrl(self.created_ik_ctrls[0], 17, trs="s")
            rig_lib.clean_ctrl(self.created_ik_ctrls[1], 17, trs="")

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
        rig_lib.add_parameter_as_extra_attr(info_crv, "how_many_jnts", self.model.how_many_jnts)
        rig_lib.add_parameter_as_extra_attr(info_crv, "how_many_ctrls", self.model.how_many_ctrls)
        rig_lib.add_parameter_as_extra_attr(info_crv, "ik_creation", self.model.ik_creation_switch)
        rig_lib.add_parameter_as_extra_attr(info_crv, "stretch_creation", self.model.stretch_creation_switch)
        rig_lib.add_parameter_as_extra_attr(info_crv, "local_spaces", self.model.space_list)

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

    def create_outputs(self):
        rig_lib.create_output(name="{0}_start_OUTPUT".format(self.model.module_name), parent=self.created_locs[0])
        rig_lib.create_output(name="{0}_end_OUTPUT".format(self.model.module_name), parent=self.created_locs[-1])

        for i, jnt in enumerate(self.created_jnts):
            if jnt != self.created_jnts[-1]:
                name = "{0}_jnt_{1}_OUTPUT".format(self.model.module_name, i)
                rig_lib.create_output(name=name, parent=jnt)


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.how_many_jnts = 5
        self.how_many_ctrls = 3
        self.ik_creation_switch = True
        self.stretch_creation_switch = True
        self.space_list = []
