from PySide2 import QtWidgets, QtCore, QtGui

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, grpbox
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
        self.how_many_levels = QtWidgets.QSpinBox()
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
        self.how_many_ctrls.setValue(self.model.how_many_ctrls)
        self.how_many_jnts.setValue(self.model.how_many_jnts)
        self.how_many_levels.setValue(self.model.how_many_levels)
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

        self.how_many_jnts.setMinimum(1)
        self.how_many_jnts.valueChanged.connect(self.ctrl.on_how_many_jnts_changed)
        self.how_many_ctrls.setMinimum(2)
        self.how_many_ctrls.setMaximum(self.model.how_many_jnts)
        self.how_many_ctrls.valueChanged.connect(self.ctrl.on_how_many_ctrls_changed)

        self.how_many_levels.setMinimum(2)
        self.how_many_levels.setMaximum(self.model.how_many_jnts)
        self.how_many_levels.valueChanged.connect(self.ctrl.on_how_many_levels_changed)

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
        ctrls_text = QtWidgets.QLabel("How many ctrls sections in spine :")
        ctrls_layout.addWidget(ctrls_text)
        ctrls_layout.addWidget(self.how_many_ctrls)
        levels_layout = QtWidgets.QVBoxLayout()
        levels_text = QtWidgets.QLabel("How many autoswim levels :")
        levels_layout.addWidget(levels_text)
        levels_layout.addWidget(self.how_many_levels)

        how_many_layout.addLayout(jnts_layout)
        how_many_layout.addLayout(ctrls_layout)
        how_many_layout.addLayout(levels_layout)

        options_layout.addLayout(how_many_layout)

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
        self.guide_names = []
        self.guides = []
        self.guides_grp = None
        self.created_spine_jnts = []
        self.created_spine_ctrl = []
        self.created_caudalfin_jnts = []
        self.all_spine_jnt = []
        self.option_ctrl = None
        self.jnt_const_group = None

        RigController.__init__(self,  model, view)

    def on_how_many_jnts_changed(self, value):
        self.model.how_many_jnts = value
        self.view.how_many_ctrls.setMaximum(self.model.how_many_jnts)
        self.view.how_many_levels.setMaximum(self.model.how_many_jnts)

    def prebuild(self):

        temp_outputs = []
        for i in xrange(self.model.how_many_jnts):
            temp_output = "jnt_{0}_OUTPUT".format(i)
            temp_outputs.append(temp_output)
        self.create_temporary_outputs(temp_outputs)


        self.guide_names = ["{0}_spine_start_GUIDE".format(self.model.module_name),
                            "{0}_spine_end_GUIDE".format(self.model.module_name),
                            "{0}_caudalfin_end_GUIDE".format(self.model.module_name)]

        if self.guide_check(self.guide_names):
            self.guides = pmc.ls(self.guide_names)
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            self.guides_grp.setAttr("visibility", 1)
            self.view.refresh_view()
            pmc.select(d=1)
            return

        spine_start_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guide_names[0])
        spine_end_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guide_names[1])
        caudalfin_end_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guide_names[2])
        spine_start_guide.setAttr("translate", (0, 2, 0))
        spine_end_guide.setAttr("translate", (0, 2, -3))
        caudalfin_end_guide.setAttr("translate", (0, 2, -4))

        self.guides = [spine_start_guide, spine_end_guide, caudalfin_end_guide]
        self.guides_grp = self.group_guides(self.guides)

        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()
        self.create_jnts()
        self.create_option_ctrl()
        self.create_ctrl()
        self.create_local_spaces()
        self.create_autoswim()
        self.clean_rig()
        self.create_outputs()
        pmc.select(d=1)

    def create_jnts(self):
        spine_jnts_crv = pmc.curve(d=1, p=[pmc.xform(self.guides[0], q=1, ws=1, translation=1),
                                           pmc.xform(self.guides[1], q=1, ws=1, translation=1)],
                                   n="{0}_spine_curve".format(self.model.module_name))
        spine_jnts_rebuilded = pmc.rebuildCurve(spine_jnts_crv, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                                s=self.model.how_many_jnts, d=1, ch=0, replaceOriginal=1)[0]
        if self.model.how_many_jnts == 2:
            pmc.delete(spine_jnts_rebuilded.cv[-2])
            pmc.delete(spine_jnts_rebuilded.cv[1])
        vertex_list = spine_jnts_rebuilded.cv[:]
        self.created_spine_jnts = rig_lib.create_jnts_from_cv_list_and_return_jnts_list(vertex_list,
                                                                                        "{0}_spine".format(self.model.module_name))

        rig_lib.change_jnt_chain_suffix(self.created_spine_jnts, new_suffix="SKN")
        pmc.select(d=1)
        spine_jnts_offset_name = str(self.created_spine_jnts[0]).replace("_SKN", "_jnt_OFS")
        spine_jnts_offset = pmc.joint(p=pmc.xform(self.created_spine_jnts[0], q=1, ws=1, translation=1),
                                      o=pmc.xform(self.created_spine_jnts[0], q=1, ws=1, rotation=1), n=spine_jnts_offset_name)

        pmc.parent(self.created_spine_jnts[0], spine_jnts_offset, r=0)
        pmc.parent(spine_jnts_offset, self.jnt_input_grp, r=0)

        pmc.delete(spine_jnts_rebuilded)

        caudalfin_jnts_crv = pmc.curve(d=1, p=[pmc.xform(self.guides[1], q=1, ws=1, translation=1),
                                           pmc.xform(self.guides[2], q=1, ws=1, translation=1)],
                                   n="{0}_caudalfin_curve".format(self.model.module_name))
        caudalfin_jnts_rebuilded = pmc.rebuildCurve(caudalfin_jnts_crv, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                                s=2, d=1, ch=0, replaceOriginal=1)[0]

        pmc.delete(caudalfin_jnts_rebuilded.cv[-2])
        pmc.delete(caudalfin_jnts_rebuilded.cv[1])
        vertex_list = caudalfin_jnts_rebuilded.cv[:]
        self.created_caudalfin_jnts = rig_lib.create_jnts_from_cv_list_and_return_jnts_list(vertex_list,
                                                                                            "{0}_caudalfin".format(self.model.module_name))

        rig_lib.change_jnt_chain_suffix(self.created_caudalfin_jnts, new_suffix="SKN")

        pmc.select(d=1)
        caudalfin_jnts_offset_name = str(self.created_caudalfin_jnts[0]).replace("_SKN", "_jnt_OFS")
        caudalfin_jnts_offset = pmc.joint(p=pmc.xform(self.created_caudalfin_jnts[0], q=1, ws=1, translation=1),
                                      o=pmc.xform(self.created_caudalfin_jnts[0], q=1, ws=1, rotation=1),
                                      n=caudalfin_jnts_offset_name)

        pmc.parent(self.created_caudalfin_jnts[0], caudalfin_jnts_offset, r=0)
        pmc.delete(self.created_spine_jnts.pop(-1))
        pmc.parent(caudalfin_jnts_offset, self.created_spine_jnts[-1], r=0)

        pmc.delete(caudalfin_jnts_rebuilded)

        self.all_spine_jnt = self.created_spine_jnts + self.created_caudalfin_jnts

    def create_ctrl(self):
        duplicate_jnts = pmc.duplicate(self.created_spine_jnts)
        rig_lib.change_jnt_chain_suffix(duplicate_jnts, new_suffix="CTRL")
        for i, ctrl in enumerate(duplicate_jnts):
            ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=2, d=3, s=8,
                                    n="{0}_shape".format(ctrl))[0]
            pmc.parent(ctrl_shape.getShape(), ctrl, shape=1, r=1)
            ctrl.setAttr("radius", 0)
            ctrl.setAttr("overrideEnabled", 1)
            ctrl.setAttr("overrideColor", 14)
            ctrl.getShape().rename(str(ctrl) + "Shape")
            pmc.delete(ctrl_shape)
        tail_jnts = pmc.ls(regex=(".*_CTRL\|{1}_caudalfin_0_jnt_OFS.*".format(duplicate_jnts[-1], self.model.module_name)))
        pmc.delete(tail_jnts.pop(-1))
        for i, ctrl in enumerate(tail_jnts):
            if i == 0:
                ctrl.rename(str(ctrl).replace("_SKN", "_CTRL"))
                ctrl.setAttr("drawStyle", 2)
            else:
                ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=2, d=3, s=8,
                                        n="{0}_shape".format(ctrl))[0]
                pmc.parent(ctrl_shape.getShape(), ctrl, shape=1, r=1)
                ctrl.setAttr("radius", 0)
                ctrl.setAttr("overrideEnabled", 1)
                ctrl.setAttr("overrideColor", 14)
                ctrl.rename(str(ctrl).replace("_SKN", "_CTRL"))
                ctrl.getShape().rename(str(ctrl) + "Shape")
                pmc.delete(ctrl_shape)

        tail_jnts.pop(0)
        self.created_spine_ctrl = duplicate_jnts
        for jnt in tail_jnts:
            self.created_spine_ctrl.append(jnt)

        pmc.select(d=1)

        spine_ctrl_offset_name = str(self.created_spine_ctrl[0]).replace("_CTRL", "_ctrl_OFS")
        spine_ctrl_offset = pmc.joint(p=pmc.xform(self.created_spine_ctrl[0], q=1, ws=1, translation=1),
                                      o=pmc.xform(self.created_spine_ctrl[0], q=1, ws=1, rotation=1),
                                      n=spine_ctrl_offset_name, radius= 0)

        pmc.parent(self.created_spine_ctrl[0], spine_ctrl_offset, r=0)
        pmc.parent(spine_ctrl_offset, self.ctrl_input_grp, r=0)

        for i, ctrl in enumerate(self.created_spine_ctrl):
            pmc.parentConstraint(ctrl, self.all_spine_jnt[i], maintainOffset=1)
            ctrl.jointOrient >> self.all_spine_jnt[i].jointOrient
            ctrl.scale >> self.all_spine_jnt[i].scale

    def create_option_ctrl(self):
        option_ctrl_shape = rig_lib.jnt_shape_curve(name="{0}_option_ctrl_shape".format(self.model.module_name))
        self.option_ctrl = rig_lib.create_jnttype_ctrl(name="{0}_option_CTRL".format(self.model.module_name),
                                                               shape=option_ctrl_shape)
        self.option_ctrl.setAttr("translate", pmc.xform(self.created_spine_jnts[0], q=1, ws=1, translation=1))

        heigh = 0

        if pmc.objExists("mod_hd"):
            mod_hd_grp = pmc.ls("mod_hd")[0]

            mod_hd_bbox = mod_hd_grp.getBoundingBox()
            mod_hd_bbox_low_corner = mod_hd_bbox[0]
            mod_hd_bbox_hi_corner = mod_hd_bbox[1]

            mod_hd_bbox_heigh = mod_hd_bbox_hi_corner[1] - mod_hd_bbox_low_corner[1]

            if mod_hd_bbox_heigh > heigh:
                heigh = mod_hd_bbox_heigh

        if pmc.objExists("mod_proxy"):
            mod_proxy_grp = pmc.ls("mod_proxy")[0]

            mod_proxy_bbox = mod_proxy_grp.getBoundingBox()
            mod_proxy_bbox_low_corner = mod_proxy_bbox[0]
            mod_proxy_bbox_hi_corner = mod_proxy_bbox[1]

            mod_proxy_bbox_heigh = mod_proxy_bbox_hi_corner[1] - mod_proxy_bbox_low_corner[1]

            if mod_proxy_bbox_heigh > heigh:
                heigh = mod_proxy_bbox_heigh

        if pmc.objExists("mod_sliced"):
            mod_sliced_grp = pmc.ls("mod_sliced")[0]

            mod_sliced_bbox = mod_sliced_grp.getBoundingBox()
            mod_sliced_bbox_low_corner = mod_sliced_bbox[0]
            mod_sliced_bbox_hi_corner = mod_sliced_bbox[1]

            mod_sliced_bbox_heigh = mod_sliced_bbox_hi_corner[1] - mod_sliced_bbox_low_corner[1]

            if mod_sliced_bbox_heigh > heigh:
                heigh = mod_sliced_bbox_heigh

        ctrl_cvs = self.option_ctrl.cv[:]
        for i, cv in enumerate(ctrl_cvs):
            pmc.xform(self.option_ctrl.getShape().controlPoints[i], ws=1, translation=(pmc.xform(cv, q=1, ws=1, translation=1)[0],
                                                                                               pmc.xform(cv, q=1, ws=1, translation=1)[1] + heigh,
                                                                                               pmc.xform(cv, q=1, ws=1, translation=1)[2]))

        self.option_ctrl.addAttr("ctrlsPrincipaux", attributeType="bool", defaultValue=1, hidden=0, keyable=1)
        self.option_ctrl.addAttr("ctrlsSecondaires", attributeType="bool", defaultValue=0, hidden=0, keyable=1)
        self.option_ctrl.addAttr("autoSwim", attributeType="float", defaultValue=0, hidden=0, keyable=1, hasMaxValue=1,
                                         hasMinValue=1, maxValue=1, minValue=0)
        self.option_ctrl.addAttr("amplitude", attributeType="float", defaultValue=2, hidden=0, keyable=1,
                                         hasMaxValue=0, hasMinValue=1, minValue=0)
        self.option_ctrl.addAttr("speed", attributeType="float", defaultValue=2, hidden=0, keyable=1,
                                         hasMaxValue=0, hasMinValue=1, minValue=0.1)
        self.option_ctrl.addAttr("delay", attributeType="float", defaultValue=-0.5, hidden=0, keyable=1,
                                         hasMaxValue=0, hasMinValue=0)
        i = 1
        while i <= self.model.how_many_levels:
            if i == self.model.how_many_levels:
                name = "caudalfin"
            else:
                name = "level{0}".format(i)
            self.option_ctrl.addAttr("{0}Attributes".format(name), attributeType="enum", enumName="_________", hidden=0, keyable=0)
            self.option_ctrl.setAttr("{0}Attributes".format(name), lock=1, channelBox=1)
            self.option_ctrl.addAttr("{0}Offset".format(name), attributeType="float", defaultValue=0, hidden=0, keyable=1,
                                     hasMinValue=1, minValue=0,
                                     hasMaxValue=1, maxValue=self.model.how_many_jnts + 2)
            self.option_ctrl.addAttr("{0}Amplitude".format(name), attributeType="float", defaultValue=1, hidden=0, keyable=1,
                                     hasMaxValue=0, hasMinValue=1, minValue=0)
            self.option_ctrl.addAttr("{0}Frequence".format(name), attributeType="float", defaultValue=1, hidden=0, keyable=1,
                                     hasMaxValue=0, hasMinValue=0)
            self.option_ctrl.addAttr("{0}Delay".format(name), attributeType="float", defaultValue=1, hidden=0, keyable=1,
                                     hasMaxValue=0, hasMinValue=0)
            i += 1

        option_ctrl_offset = pmc.group(em=1, n="{0}_option_ctrl_OFS".format(self.model.module_name))
        option_ctrl_offset.setAttr("translate", pmc.xform(self.option_ctrl, q=1, ws=1, translation=1))
        option_ctrl_offset.setAttr("rotate", pmc.xform(self.option_ctrl, q=1, ws=1, rotation=1))

        pmc.parent(self.option_ctrl, option_ctrl_offset, r=0)
        pmc.parent(option_ctrl_offset, self.ctrl_input_grp, r=0)

    def create_autoswim(self):
        if pmc.objExists("{0}_autoswim_EXP".format(self.model.module_name)):
            pmc.delete("{0}_autoswim_EXP".format(self.model.module_name))
        exp = pmc.createNode("expression", n="{0}_autoswim_EXP".format(self.model.module_name))
        exp_text = ""

        for i, ctrl in enumerate(self.created_spine_ctrl):
            autoswim_ctrl_name = str(ctrl).replace("_CTRL", "_ctrl_AUTOSWIM")
            autoswim_ctrl = pmc.joint(p=pmc.xform(ctrl, q=1, ws=1, translation=1), o=pmc.xform(ctrl, q=1, ws=1, rotation=1), n=autoswim_ctrl_name)
            pmc.parent(autoswim_ctrl, ctrl.getParent())
            pmc.parent(ctrl, autoswim_ctrl)
            autoswim_ctrl.setAttr("drawStyle", 2)

            if pmc.objExists("{0}_autoswim_merge_PMA".format(ctrl)):
                pmc.delete("{0}_autoswim_merge_PMA".format(ctrl))
            add = pmc.createNode("plusMinusAverage", n="{0}_autoswim_merge_PMA".format(ctrl))

            n = 0
            while n < self.model.how_many_levels:
                if pmc.objExists("{0}_level{1}_offset_clamp".format(ctrl, n+1)):
                    pmc.delete("{0}_level{1}_offset_clamp".format(ctrl, n+1))
                clamp = pmc.createNode("clamp", n="{0}_level{1}_offset_clamp".format(ctrl, n+1))

                if pmc.objExists("{0}_level{1}_offset_percent_range".format(ctrl, n + 1)):
                    pmc.delete("{0}_level{1}_offset_percent_range".format(ctrl, n + 1))
                range = pmc.createNode("setRange", n="{0}_level{1}_offset_percent_range".format(ctrl, n+1))

                if pmc.objExists("{0}_level{1}_offset_invert_percent".format(ctrl, n + 1)):
                    pmc.delete("{0}_level{1}_offset_invert_percent".format(ctrl, n + 1))
                plus = pmc.createNode("plusMinusAverage", n="{0}_level{1}_offset_invert_percent".format(ctrl, n+1))

                if pmc.objExists("{0}_level{1}_offset_multiply".format(ctrl, n + 1)):
                    pmc.delete("{0}_level{1}_offset_multiply".format(ctrl, n + 1))
                mult = pmc.createNode("multDoubleLinear", n="{0}_level{1}_offset_multiply".format(ctrl, n+1))

                level_attr_prefix = "level{0}".format(n+1)
                if n == self.model.how_many_levels-1:
                    level_attr_prefix = "caudalfin"

                self.option_ctrl.connectAttr("{0}Offset".format(level_attr_prefix), clamp+".inputR")
                clamp.setAttr("minR", i)
                clamp.setAttr("maxR", i+1)
                clamp.outputR >> range.valueX
                range.setAttr("oldMinX", i)
                range.setAttr("oldMaxX", i+1)
                range.setAttr("minX", 0)
                range.setAttr("maxX", 1)
                plus.setAttr("operation", 2)
                plus.setAttr("input1D[0]", 1)
                range.outValueX >> plus.input1D[1]
                plus.output1D >> mult.input1

                exp_text += "\n{0}.input2 = ( {2}/float({4}) * {1}.amplitude * {1}.{3}Amplitude * {1}.autoSwim )  *   sin( ( time* {1}.speed  + {2} * {1}.delay * {1}.{3}Delay )* {1}.{3}Frequence" \
                            "  ) ;".format(mult, self.option_ctrl, i+1, level_attr_prefix,self.model.how_many_jnts)

                mult.output >> add.input1D[n]

                n += 1

            add.output1D >> autoswim_ctrl.rotateZ

        exp.setExpression(exp_text)

    def create_local_spaces(self):
        spaces_names = []
        space_locs = []
        for space in self.model.space_list:
            name = str(space).replace("_OUTPUT", "")
            if "local_ctrl" in name:
                name = "world"
            spaces_names.append(name)

            if pmc.objExists("{0}_{1}_SPACELOC".format(self.model.module_name, name)):
                pmc.delete("{0}_{1}_SPACELOC".format(self.model.module_name, name))
            space_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_{1}_SPACELOC".format(self.model.module_name, name))
            space_locs.append(space_loc)

        spaces_names.append("local")

        fk_ctrls = self.created_spine_ctrl

        fk_ctrls[0].addAttr("space", attributeType="enum", enumName=spaces_names, hidden=0, keyable=1)

        for i, space in enumerate(self.model.space_list):
            space_locs[i].setAttr("translate", pmc.xform(self.created_spine_jnts[0], q=1, ws=1, translation=1))
            pmc.parent(space_locs[i], space)

            fk_space_const = pmc.parentConstraint(space_locs[i], fk_ctrls[0].getParent(), maintainOffset=1)

            rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(fk_space_const, space_locs[i], i),
                                                    fk_ctrls[0].space, i,
                                                    "{0}_{1}_COND".format(fk_ctrls[0], spaces_names[i]))

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        for ctrl in self.created_spine_ctrl:
            rig_lib.clean_ctrl(ctrl, 14, trs="ts")

        second_ctrl_list = self.created_spine_ctrl[:]
        princ_ctrl_list = []

        step_princ_ctrl = int(self.model.how_many_jnts / self.model.how_many_ctrls)

        for i in range(0, self.model.how_many_jnts, step_princ_ctrl):
            princ_ctrl_list.append(second_ctrl_list[i])

        for ctrl in second_ctrl_list:
            if "_caudalfin_" in str(ctrl):
                princ_ctrl_list.append(ctrl)

        for jnt in princ_ctrl_list:
            second_ctrl_list.remove(jnt)

        for ctrl in princ_ctrl_list:
            self.option_ctrl.ctrlsPrincipaux >> ctrl.getShape().visibility
        for ctrl in second_ctrl_list:
            self.option_ctrl.ctrlsSecondaires >> ctrl.getShape().visibility

        rig_lib.clean_ctrl(self.option_ctrl, 17, trs="trs")

    def create_outputs(self):
        for i, jnt in enumerate(self.all_spine_jnt):
            name = "{0}_jnt_{1}_OUTPUT".format(self.model.module_name, i)
            rig_lib.create_output(name=name, parent=jnt)

class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.how_many_jnts = 10
        self.how_many_ctrls = 4
        self.how_many_levels = 2
        self.space_list = []
