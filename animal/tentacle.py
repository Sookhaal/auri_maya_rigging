# create jnts (spine_##_SKN / spine_end_JNT)
# create jnt_OFS (spine_jnt_OFS)
# create ctrl : dupplicate jnt
#               delate end jnt
#               replace jnt by ctrl (spine_##_fk_CTRL / spine_fk_ctrl_OFS)
#               create cv crontols (color green) (spine_##_CTRL)
#               snap each cv to is ctrl
#               select control vertex rotatey 90
#               parent cv shape to ctrl
#               delate grp
#               ctrl > radius jnt = 0
#               create auto grp (spine_##_fk_ctrl_AUTO)
#               snap to inch ctrl
#               parent auto under each ctrl
# create parent constraint for each ctrl > to jnt
# create input grp (spine_ctrl_INPPUT / spine_jnt_INPPUT)
# constraint matrix cog_output
# parent spine_jnt_OFS in spine_jnt_INPUT end parent input in local_CTRL
# parent spine_ctrl_OFS in spine_ctrl_INPUT end parent input in JNT_GRP end hide input
# create jointCurve rename autoswim_CTRL
    # grp rename autoswim_ctrl_OFS (coor yellow)
    # create locator parent in autoswim_CTRL end rename autoswim_OUTPUT
    #snap autoswim_ctrl_OFS to spine_ctrl_OFS
    # select controls vertex scaley 0.46 loc pour snap dessus
    # add attributes :  autoswim 0 (min 0 / max 1) float
    #                   amplitude a regler (min 0) float
    #                   speed a regler (min 0.1) float
    #                   delay a regler float
    #                   spineAttibutes ________ enum
    #                   spineAmplitude a regler (min 0) float
    #                   spineSpeed a regler (min 0.1) float
    #                   spineDelay a regler float
    #                   regler aussi nombre de spine attribute (ex spine1 spine2 ...)

#               create expression on spine_##_fk_ctrl_AUTO : mel
# float $freq = autoswim_CTRL.speed/1;
# float $delay = 1*(autoswim_CTRL.delay);
# float $amp = autoswim_CTRL.amplitude*1;
# float $delay2 = autoswim_CTRL.delay + 1*(autoswim_CTRL.delay);
# float $delay3 = autoswim_CTRL.delay + autoswim_CTRL.delay + 1*(autoswim_CTRL.delay);
# float $delay4 = autoswim_CTRL.delay + autoswim_CTRL.delay + autoswim_CTRL.delay + 1*(autoswim_CTRL.delay);

# float $freqspine = autoswim_CTRL.spineSpeed * autoswim_CTRL.speed/1;
# float $delayspine = autoswim_CTRL.spineDelay + autoswim_CTRL.delay + autoswim_CTRL.delay + autoswim_CTRL.delay + 1*(autoswim_CTRL.delay);
# float $ampspine = autoswim_CTRL.spineAmplitude * autoswim_CTRL.amplitude*1;
# float $delayspine1 = autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.delay + autoswim_CTRL.delay + autoswim_CTRL.delay + 1*(autoswim_CTRL.delay);
# float $delayspine2 = autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.delay + autoswim_CTRL.delay + autoswim_CTRL.delay + 1*(autoswim_CTRL.delay);
# float $delayspine3 = autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.delay + autoswim_CTRL.delay + autoswim_CTRL.delay + 1*(autoswim_CTRL.delay);
# float $delayspine4 = autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.delay + autoswim_CTRL.delay + autoswim_CTRL.delay + 1*(autoswim_CTRL.delay);

# float $freqcaudal = autoswim_CTRL.caudalFinSpeed * autoswim_CTRL.speed/1;
# float $delaycaudal = autoswim_CTRL.caudalFinDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.spineDelay + autoswim_CTRL.delay + autoswim_CTRL.delay + autoswim_CTRL.delay + 1*(autoswim_CTRL.delay);
# float $ampcaudal = autoswim_CTRL.caudalFinAmplitude * autoswim_CTRL.amplitude*1;

# spine_01_fk_ctrl_AUTO.rotateY = (sin((frame*$freq) + $delay)*$amp) * autoswim_CTRL.autoSwim;
# spine_02_fk_ctrl_AUTO.rotateY = (sin((frame*$freq) + $delay2)*$amp) * autoswim_CTRL.autoSwim;
# spine_03_fk_ctrl_AUTO.rotateY = (sin((frame*$freq) + $delay3)*$amp) * autoswim_CTRL.autoSwim;
# spine_04_fk_ctrl_AUTO.rotateY = (sin((frame*$freq) + $delay4)*$amp) * autoswim_CTRL.autoSwim;
# spine_05_fk_ctrl_AUTO.rotateY = (sin((frame*$freqspine) + $delayspine)*$ampspine) * autoswim_CTRL.autoSwim;
# spine_06_fk_ctrl_AUTO.rotateY = (sin((frame*$freqspine) + $delayspine1)*$ampspine) * autoswim_CTRL.autoSwim;
# spine_07_fk_ctrl_AUTO.rotateY = (sin((frame*$freqspine) + $delayspine2)*$ampspine) * autoswim_CTRL.autoSwim;
# spine_08_fk_ctrl_AUTO.rotateY = (sin((frame*$freqspine) + $delayspine3)*$ampspine) * autoswim_CTRL.autoSwim;
# spine_09_fk_ctrl_AUTO.rotateY = (sin((frame*$freqspine) + $delayspine4)*$ampspine) * autoswim_CTRL.autoSwim;
# spine_10_fk_ctrl_AUTO.rotateY = (sin((frame*$freqcaudal) + $delaycaudal)*$ampcaudal) * autoswim_CTRL.autoSwim;


# space : world / cog / local


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
        ctrls_text = QtWidgets.QLabel("How many ctrls :")
        ctrls_layout.addWidget(ctrls_text)
        ctrls_layout.addWidget(self.how_many_ctrls)

        how_many_layout.addLayout(jnts_layout)
        how_many_layout.addLayout(ctrls_layout)

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
        self.created_tentacle_jnts = []
        self.created_tentacle_ctrl = []
        self.nurbs_tentacle = []
        RigController.__init__(self,  model, view)

    def on_how_many_jnts_changed(self, value):
        self.model.how_many_jnts = value
        self.view.how_many_ctrls.setMaximum(self.model.how_many_jnts)

    def prebuild(self):
        self.guide_names = ["{0}_tentacle_start_GUIDE".format(self.model.module_name),
                            "{0}_tentacle_end_GUIDE".format(self.model.module_name)]

        if self.guide_check(self.guide_names):
            self.guides = pmc.ls(self.guide_names)
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            self.guides_grp.setAttr("visibility", 1)
            self.view.refresh_view()
            pmc.select(d=1)
            return

        tentacle_start_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guide_names[0])
        tentacle_end_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guide_names[1])
        tentacle_start_guide.setAttr("translate", (0, 2, 0))
        tentacle_end_guide.setAttr("translate", (0, 0, 0))

        self.guides = [tentacle_start_guide, tentacle_end_guide]
        self.guides_grp = self.group_guides(self.guides)

        self.view.refresh_view()
        pmc.select(d=1)


    def execute(self):
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()
        self.create_jnts()
        self.create_ctrl()
        # self.create_local_spaces()
        # self.clean_rig()
        # self.create_outputs()
        pmc.select(d=1)

    def create_jnts(self):
        tentacle_jnts_crv = pmc.curve(d=1, p=[pmc.xform(self.guides[0], q=1, ws=1, translation=1),
                                           pmc.xform(self.guides[1], q=1, ws=1, translation=1)],
                                   n="{0}_tentacle_curve_1".format(self.model.module_name))
        tentacle_jnts_rebuilded = pmc.rebuildCurve(tentacle_jnts_crv, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                                s=self.model.how_many_jnts, d=1, ch=0, replaceOriginal=1)[0]
        if self.model.how_many_jnts == 2:
            pmc.delete(tentacle_jnts_rebuilded.cv[-2])
            pmc.delete(tentacle_jnts_rebuilded.cv[1])
        vertex_list = tentacle_jnts_rebuilded.cv[:]
        self.created_tentacle_jnts = rig_lib.create_jnts_from_cv_list_and_return_jnts_list(vertex_list,
                                                                                        "{0}_tentacle".format(
                                                                                            self.model.module_name))

        rig_lib.change_jnt_chain_suffix(self.created_tentacle_jnts, new_suffix="SKN")
        pmc.select(d=1)

        skin_selection = list(self.created_tentacle_jnts)

        for i, jnts in enumerate(self.created_tentacle_jnts):
            first_value = i
            second_value = float(((self.model.how_many_jnts)))
            default_value = float(first_value / second_value)
            jnts.addAttr("position", attributeType="float", defaultValue=default_value, hidden=0, keyable=1)


        pmc.select(d=1)

        tentacle_jnts_offset_name = str(self.created_tentacle_jnts[0]).replace("_SKN", "_jnt_OFS")
        tentacle_jnts_offset = pmc.joint(p=pmc.xform(self.created_tentacle_jnts[0], q=1, ws=1, translation=1),
                                      o=pmc.xform(self.created_tentacle_jnts[0], q=1, ws=1, rotation=1),
                                      n=tentacle_jnts_offset_name)

        pmc.parent(self.created_tentacle_jnts[0], tentacle_jnts_offset, r=0)
        pmc.parent(tentacle_jnts_offset, self.jnt_input_grp, r=0)

        tentacle_jnts_rebuilded.setAttr("translate", (0, 0, 0.1))
        tentacle_nurbs_crv_rebuilded = pmc.rebuildCurve(tentacle_jnts_rebuilded, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                                s=self.model.how_many_jnts, d=3, ch=0, replaceOriginal=1)[0]
        tentacle_nurbs_crv = pmc.duplicate(tentacle_nurbs_crv_rebuilded, n="{0}_tentacle_curve_2".format(self.model.module_name))[0]
        tentacle_nurbs_crv.setAttr("translate", (0, 0, -0.1))

        tentacle_jnts_nurbs = pmc.loft(tentacle_nurbs_crv_rebuilded, tentacle_nurbs_crv, u=1, ar=1, ss=1, rn=0, po=0,
                                       rsn=1, d=1,c=0, n="{0}_variableFK_nurbs".format(self.model.module_name))

        pmc.delete(tentacle_nurbs_crv_rebuilded)
        pmc.delete(tentacle_nurbs_crv)

        pmc.select(d=1)

        pmc.skinCluster(skin_selection[0], tentacle_jnts_nurbs[0], sm=0, nw=2, mi=1, rui=1, dr=2, n='VFK_SkinCluster')

        self.nurbs_tentacle = tentacle_jnts_nurbs

        pmc.select(d=1)

    def create_ctrl(self):

        # create curve for controls

        tentacle_ctrl_crv = pmc.curve(d=1, p=[pmc.xform(self.guides[0], q=1, ws=1, translation=1),
                                              pmc.xform(self.guides[1], q=1, ws=1, translation=1)],
                                      n="{0}_tentacle_curve".format(self.model.module_name))

        tentacle_ctrl_rebuilded = pmc.rebuildCurve(tentacle_ctrl_crv, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                               s=self.model.how_many_ctrls, d=1, ch=0, replaceOriginal=1)[0]
        if self.model.how_many_ctrls == 2:
            pmc.delete(tentacle_ctrl_rebuilded.cv[-2])
            pmc.delete(tentacle_ctrl_rebuilded.cv[1])
        vertex_list = tentacle_ctrl_rebuilded.cv[:]
        snap_ctrl = rig_lib.create_jnts_from_cv_list_and_return_jnts_list(vertex_list,
                                                                                       "{0}_tentacle_vfk".format(
                                                                                           self.model.module_name))

        rig_lib.change_jnt_chain_suffix(snap_ctrl, new_suffix="SNAP")
        pmc.delete(snap_ctrl.pop(-1))

        # create controls and follicle and attache controls system

        for i, ctrl in enumerate(snap_ctrl) :
            ctrl_transform = pmc.joint(p=pmc.xform(ctrl, q=1, ws=1, translation=1), o=pmc.xform(ctrl,
                                                            q=1, ws=1, rotation=1), n="{0}".format(ctrl))

            ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=2, d=3, s=8,
                                    n="{0}_shape".format(ctrl))[0]

            pmc.parent(ctrl_shape.getShape(), ctrl_transform, shape=1, r=1)
            ctrl_transform.setAttr("radius", 0)
            ctrl_transform.setAttr("overrideEnabled", 1)
            ctrl_transform.setAttr("overrideColor", 14)
            ctrl_transform.getShape().rename(str(ctrl) + "Shape")
            ctrl_transform.addAttr("falloff", attributeType="float", defaultValue=0.2, hidden=0, keyable=1,
                                   hasMaxValue=1, hasMinValue=1, minValue=0, maxValue=1)
            first_value = float(i)
            second_value = float(((self.model.how_many_ctrls)))
            default_value = float(first_value/second_value)
            ctrl_transform.addAttr("position", attributeType="float", defaultValue=default_value, hidden=0, keyable=1,
                                   hasMaxValue=1, hasMinValue=1, minValue=0, maxValue=1)
            ctrl_transform.addAttr("numberJoints", attributeType="float", defaultValue=0, hidden=0, keyable=1)
            pmc.delete(ctrl_shape)
            self.created_tentacle_ctrl.append(ctrl_transform)
            pmc.select(d=1)

        pmc.delete(snap_ctrl)
        rig_lib.change_jnt_chain_suffix(self.created_tentacle_ctrl, new_suffix="CTRL")

        follicle_grp = pmc.group(em=1, n="vfk_follicle_GRP")

        for i, ctrl in enumerate(self.created_tentacle_ctrl) :
            ctrl_nomove = pmc.joint(p=pmc.xform(ctrl, q=1, ws=1, translation=1), o=pmc.xform(ctrl,
                                                            q=1, ws=1, rotation=1), n="{0}_NoMove".format(ctrl))
            ctrl_nomove.setAttr("radius", 0)
            ctrl_nomove.setAttr("overrideEnabled", 1)
            ctrl_nomove.setAttr("overrideColor", 14)
            pmc.select(d=1)

            ctrl_offset = pmc.joint(p=pmc.xform(ctrl, q=1, ws=1, translation=1), o=pmc.xform(ctrl,
                                                            q=1, ws=1, rotation=1), n="{0}_OFS".format(ctrl))
            ctrl_offset.setAttr("radius", 0)
            ctrl_offset.setAttr("overrideEnabled", 1)
            ctrl_offset.setAttr("overrideColor", 14)
            pmc.select(d=1)

            ctrl_constraint = pmc.joint(p=pmc.xform(ctrl, q=1, ws=1, translation=1), o=pmc.xform(ctrl,
                                                                     q=1, ws=1, rotation=1),n="{0}_CONS".format(ctrl))
            ctrl_constraint.setAttr("radius", 0)
            ctrl_constraint.setAttr("overrideEnabled", 1)
            ctrl_constraint.setAttr("overrideColor", 14)
            pmc.select(d=1)

            pmc.parent(ctrl_offset, ctrl_constraint, shape=1)
            pmc.parent(ctrl_nomove, ctrl_offset, shape=1)
            multiply_nomove = pmc.createNode('multiplyDivide', n=ctrl + 'invertTranslate')
            ctrl.connectAttr('translate', multiply_nomove.input1)
            multiply_nomove.setAttr('input2', (-1, -1, -1))
            multiply_nomove.setAttr('operation', 1)
            multiply_nomove.connectAttr('output', ctrl_nomove.translate)
            pmc.parent(ctrl, ctrl_nomove, shape=1)
            pmc.select(d=1)

            nurbs = self.nurbs_tentacle[0]
            nurbs_shape = nurbs.getShape()
            follicle = pmc.createNode("follicle", n=ctrl + "_FOLLShape")
            nurbs_shape.local.connect(follicle.inputSurface)
            nurbs_shape.worldMatrix[0].connect(follicle.inputWorldMatrix)
            follicle.outRotate.connect(follicle.getParent().rotate)
            follicle.outTranslate.connect(follicle.getParent().translate)
            follicle.parameterU.set(0.5)
            follicle.parameterV.set(0.5)
            follicle.getParent().t.lock()
            follicle.getParent().r.lock()
            print(ctrl)
            ctrl.connectAttr('position', follicle.parameterU)
            follicle.getParent().rename(ctrl + '_FOll')
            pmc.parent(follicle.getParent(), follicle_grp)

            follicle.getParent().translate.connect(ctrl_constraint.translate)
            turn_position = pmc.createNode('plusMinusAverage', n=ctrl + 'cons_rotateX+90')
            follicle.getParent().rotate.connect(turn_position.input3D[0])
            turn_position.input3D[1].input3Dx.set(90)
            turn_position.input3D[1].input3Dz.set(90)
            turn_position.output3D.connect(ctrl_constraint.rotate)

        pmc.delete(tentacle_ctrl_rebuilded)


        # create node connection between joints and controls
        for i,ctrl in enumerate(self.created_tentacle_ctrl) :
            folloff_mult = pmc.createNode('multiplyDivide')
            folloff_mult.rename(ctrl + '_jnt_multdiv')
            folloff_remap = pmc.createNode('setRange')
            folloff_remap.rename(ctrl + '_jnt_remap')

            ctrl.connectAttr('falloff', folloff_mult.input1X)
            folloff_mult.setAttr('input2X', 2)
            folloff_mult.connectAttr('outputX', folloff_remap.valueX)
            folloff_remap.setAttr('minX', 1)
            folloff_remap.setAttr('maxX', float(self.model.how_many_jnts))
            folloff_remap.setAttr('oldMinX', 0)
            folloff_remap.setAttr('oldMaxX', 1)
            folloff_remap.connectAttr('outValueX', ctrl.numberJoints)

            for j, jnts in enumerate(self.created_tentacle_jnts):
                # create nodes
                names = jnts + '_' + str(i)
                nulgreater_pos_min_falloff = pmc.createNode('plusMinusAverage')
                nulgreater_pos_min_falloff.rename(names + '_nulgreater_pos_minus_falloff')
                nulgreater_jntpos_min_result = pmc.createNode('plusMinusAverage')
                nulgreater_jntpos_min_result.rename(names + '_nulgreater_jntPos_minus_result')
                nulgreater_pos_min_result = pmc.createNode('plusMinusAverage')
                nulgreater_pos_min_result.rename(names + '_nulgreater_pos_minus_result')
                greater_result_divide = pmc.createNode('multiplyDivide')
                greater_result_divide.rename(names + '_greater_pos_result_divide')

                nullesser_pos_min_falloff = pmc.createNode('plusMinusAverage')
                nullesser_pos_min_falloff.rename(names + '_nullesser_pos_minus_falloff')
                nullesser_jntpos_min_result = pmc.createNode('plusMinusAverage')
                nullesser_jntpos_min_result.rename(names + '_nullesser_jntPos_minus_result')
                nullesser_pos_min_result = pmc.createNode('plusMinusAverage')
                nullesser_pos_min_result.rename(names + '_nullesser_pos_minus_result')
                lesser_result_divide = pmc.createNode('multiplyDivide')
                lesser_result_divide.rename(names + '_lesser_pos_result_divide')

                nul_condition = pmc.createNode('condition')
                nul_condition.rename(names + '_nul_condition')
                condition_out_mult = pmc.createNode('multiplyDivide')
                condition_out_mult.rename(names + '_rot_times_condition_out')

                num_jnts_divide = pmc.createNode('multiplyDivide')
                num_jnts_divide.rename(names + '_numJnts_div')

                times_num_jnts_divide = pmc.createNode('multiplyDivide')
                times_num_jnts_divide.rename(names + '_times_num_jnts_div')
                result_times = pmc.createNode('multiplyDivide')
                result_times.rename(names + '_result_times')
                final_condition = pmc.createNode('condition')
                final_condition.rename(names + '_final_condition')

                # connect nodes
                ctrl.connectAttr('position', nulgreater_pos_min_falloff.input1D[0])
                ctrl.connectAttr('falloff', nulgreater_pos_min_falloff.input1D[1])
                jnts.connectAttr('position', nulgreater_jntpos_min_result.input1D[0])
                nulgreater_pos_min_falloff.connectAttr('output1D', nulgreater_jntpos_min_result.input1D[1])
                nulgreater_jntpos_min_result.setAttr('operation', 2)
                ctrl.connectAttr('position', nulgreater_pos_min_result.input1D[0])
                nulgreater_pos_min_falloff.connectAttr('output1D', nulgreater_pos_min_result.input1D[1])
                nulgreater_pos_min_result.setAttr('operation', 2)
                nulgreater_jntpos_min_result.connectAttr('output1D', greater_result_divide.input1X)
                nulgreater_pos_min_result.connectAttr('output1D', greater_result_divide.input2X)
                greater_result_divide.setAttr('operation', 2)

                ctrl.connectAttr('position', nullesser_pos_min_falloff.input1D[0])
                ctrl.connectAttr('falloff', nullesser_pos_min_falloff.input1D[1])
                nullesser_pos_min_falloff.setAttr('operation', 2)
                jnts.connectAttr('position', nullesser_jntpos_min_result.input1D[0])
                nullesser_pos_min_falloff.connectAttr('output1D', nullesser_jntpos_min_result.input1D[1])
                nullesser_jntpos_min_result.setAttr('operation', 2)
                ctrl.connectAttr('position', nullesser_pos_min_result.input1D[0])
                nullesser_pos_min_falloff.connectAttr('output1D', nullesser_pos_min_result.input1D[1])
                nullesser_pos_min_result.setAttr('operation', 2)
                nullesser_jntpos_min_result.connectAttr('output1D', lesser_result_divide.input1X)
                nullesser_pos_min_result.connectAttr('output1D', lesser_result_divide.input2X)
                lesser_result_divide.setAttr('operation', 2)

                ctrl.connectAttr('position', nul_condition.firstTerm)
                jnts.connectAttr('position', nul_condition.secondTerm)
                greater_result_divide.connectAttr('outputX', nul_condition.colorIfFalseR)
                lesser_result_divide.connectAttr('outputX', nul_condition.colorIfTrueR)
                nul_condition.setAttr('operation', 3)
                nul_condition.connectAttr('outColorR', condition_out_mult.input1X)
                nul_condition.connectAttr('outColorR', condition_out_mult.input1Y)
                nul_condition.connectAttr('outColorR', condition_out_mult.input1Z)
                ctrl.connectAttr('rotate', condition_out_mult.input2)

                ctrl.connectAttr('numberJoints', num_jnts_divide.input2X)
                ctrl.connectAttr('numberJoints', num_jnts_divide.input2Y)
                ctrl.connectAttr('numberJoints', num_jnts_divide.input2Z)
                num_jnts_divide.setAttr('input1X', 1)
                num_jnts_divide.setAttr('operation', 2)

                num_jnts_divide.connectAttr('outputX', times_num_jnts_divide.input1X)
                num_jnts_divide.connectAttr('outputX', times_num_jnts_divide.input1Y)
                num_jnts_divide.connectAttr('outputX', times_num_jnts_divide.input1Z)
                condition_out_mult.connectAttr('outputX', times_num_jnts_divide.input2X)
                condition_out_mult.connectAttr('outputY', times_num_jnts_divide.input2Y)
                condition_out_mult.connectAttr('outputZ', times_num_jnts_divide.input2Z)
                times_num_jnts_divide.connectAttr('output', result_times.input1)
                result_times.setAttr('input2X', 2)
                result_times.setAttr('input2Y', 2)
                result_times.setAttr('input2Z', 2)
                nul_condition.connectAttr('outColorR', final_condition.firstTerm)
                result_times.connectAttr('output', final_condition.colorIfTrue)
                final_condition.setAttr('operation', 3)

                duplicate_jnt = pmc.duplicate(jnts)
                pmc.delete(pmc.listRelatives(duplicate_jnt, children=True))
                rig_lib.change_jnt_chain_suffix(duplicate_jnt, new_suffix="jnt_{0}_LINK".format(i))
                link_grp = duplicate_jnt[0]
                link_grp.setAttr("drawStyle", 2)
                pmc.parent(jnts, link_grp)
                final_condition.connectAttr('outColor', link_grp.rotate)





                # ctrl.connectAttr('position', nullesser_pos_min_falloff.inpt)

            # connect nodes


            # print(ctrl)


# in for create cons groupe parent to offs groue and parent to no move and parent to ctrl
# connect cons to foll
# before all create foll
# set position ctrl


        # rig_lib.change_jnt_chain_suffix(duplicate_jnts, new_suffix="CTRL")
        # for i, ctrl in enumerate(duplicate_jnts):
        #     ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=2, d=3, s=8,
        #                             n="{0}_shape".format(ctrl))[0]
        #     pmc.parent(ctrl_shape.getShape(), ctrl, shape=1, r=1)
        #     ctrl.setAttr("radius", 0)
        #     ctrl.setAttr("overrideEnabled", 1)
        #     ctrl.setAttr("overrideColor", 14)
        #     ctrl.getShape().rename(str(ctrl) + "Shape")
        #     pmc.delete(ctrl_shape)
        # tail_jnts = pmc.ls(regex=(".*_CTRL\|{1}_caudalfin_0_jnt_OFS.*".format(duplicate_jnts[-1], self.model.module_name)))
        # pmc.delete(tail_jnts.pop(-1))
        # for i, ctrl in enumerate(tail_jnts):
        #     if i == 0:
        #         ctrl.rename(str(ctrl).replace("_SKN", "_CTRL"))
        #         ctrl.setAttr("drawStyle", 2)
        #     else:
        #         ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=2, d=3, s=8,
        #                                 n="{0}_shape".format(ctrl))[0]
        #         pmc.parent(ctrl_shape.getShape(), ctrl, shape=1, r=1)
        #         ctrl.setAttr("radius", 0)
        #         ctrl.setAttr("overrideEnabled", 1)
        #         ctrl.setAttr("overrideColor", 14)
        #         ctrl.rename(str(ctrl).replace("_SKN", "_CTRL"))
        #         ctrl.getShape().rename(str(ctrl) + "Shape")
        #         pmc.delete(ctrl_shape)
        #
        # tail_jnts.pop(0)
        # self.created_spine_ctrl = duplicate_jnts
        # for jnt in tail_jnts:
        #     self.created_spine_ctrl.append(jnt)
        #
        # pmc.select(d=1)
        #
        # spine_ctrl_offset_name = str(self.created_spine_ctrl[0]).replace("_CTRL", "_ctrl_OFS")
        # spine_ctrl_offset = pmc.joint(p=pmc.xform(self.created_spine_ctrl[0], q=1, ws=1, translation=1),
        #                               o=pmc.xform(self.created_spine_ctrl[0], q=1, ws=1, rotation=1),
        #                               n=spine_ctrl_offset_name, radius= 0)
        #
        # pmc.parent(self.created_spine_ctrl[0], spine_ctrl_offset, r=0)
        # pmc.parent(spine_ctrl_offset, self.ctrl_input_grp, r=0)
        #
        # for i, ctrl in enumerate(self.created_spine_ctrl):
        #     pmc.parentConstraint(ctrl, self.all_spine_jnt[i], maintainOffset=1)
        #     ctrl.jointOrient >> self.all_spine_jnt[i].jointOrient
        #     ctrl.scale >> self.all_spine_jnt[i].scale

# delte curev


# in clean lock transform group follicle


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.how_many_jnts = 10
        self.how_many_ctrls = 3
        self.space_list = []
