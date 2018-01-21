"""
:created: 2017-12
:author: Alex BROSSARD <abrossard@artfx.fr>
"""
from PySide2 import QtWidgets, QtCore

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, grpbox
from auri.scripts.Maya_Scripts import rig_lib
from auri.scripts.Maya_Scripts.rig_lib import RigController

reload(rig_lib)


class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        # self.modules_cbbox = QtWidgets.QComboBox()
        # self.outputs_cbbox = QtWidgets.QComboBox()
        # self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.prebuild_btn = QtWidgets.QPushButton("Prebuild")
        # self.side_cbbox = QtWidgets.QComboBox()
        self.how_many_ctrls = QtWidgets.QSpinBox()
        self.mesh_to_follow = QtWidgets.QLineEdit()
        self.set_mesh_btn = QtWidgets.QPushButton("Set Mesh")
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        # self.side_cbbox.setCurrentText(self.model.side)
        self.how_many_ctrls.setValue(self.model.how_many_ctrls)
        self.mesh_to_follow.setText(self.model.mesh_to_follow)
        # self.ctrl.look_for_parent()

    def setup_ui(self):
        # self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        # self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)
        #
        # self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        # self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        # self.side_cbbox.insertItems(0, ["Left", "Center", "Right"])
        # self.side_cbbox.currentTextChanged.connect(self.ctrl.on_side_cbbox_changed)

        self.how_many_ctrls.setMinimum(1)
        self.how_many_ctrls.valueChanged.connect(self.ctrl.on_how_many_ctrls_changed)

        self.mesh_to_follow.textChanged.connect(self.ctrl.on_mesh_to_follow_changed)

        self.set_mesh_btn.clicked.connect(self.ctrl.set_mesh_to_follow)

        # self.refresh_btn.clicked.connect(self.ctrl.look_for_parent)
        self.prebuild_btn.clicked.connect(self.ctrl.prebuild)

        main_layout = QtWidgets.QVBoxLayout()

        # select_parent_layout = QtWidgets.QVBoxLayout()
        # select_parent_grp = grpbox("Select parent", select_parent_layout)
        # cbbox_layout = QtWidgets.QHBoxLayout()
        # cbbox_layout.addWidget(self.modules_cbbox)
        # cbbox_layout.addWidget(self.outputs_cbbox)
        # select_parent_layout.addLayout(cbbox_layout)
        # select_parent_layout.addWidget(self.refresh_btn)

        # side_layout = QtWidgets.QVBoxLayout()
        # side_grp = grpbox("Side", side_layout)
        # side_layout.addWidget(self.side_cbbox)

        options_layout = QtWidgets.QVBoxLayout()
        options_grp = grpbox("Options", options_layout)

        ctrls_layout = QtWidgets.QVBoxLayout()
        ctrls_text = QtWidgets.QLabel("How many ctrls :")
        ctrls_layout.addWidget(ctrls_text)
        ctrls_layout.addWidget(self.how_many_ctrls)

        mesh_to_follow_layout = QtWidgets.QVBoxLayout()
        mesh_to_follow_grp = grpbox("Mesh to attach the ctrls to:", mesh_to_follow_layout)
        mesh_to_follow_layout.addWidget(self.mesh_to_follow)
        mesh_to_follow_layout.addWidget(self.set_mesh_btn)

        options_layout.addLayout(ctrls_layout)

        # main_layout.addWidget(select_parent_grp)
        main_layout.addWidget(mesh_to_follow_grp)
        # main_layout.addWidget(side_grp)
        main_layout.addWidget(options_grp)
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
        # self.side = {}
        # self.side_coef = 0
        self.mesh_to_follow = None
        self.follicles = []
        self.ctrls = []
        RigController.__init__(self,  model, view)

    def on_mesh_to_follow_changed(self, text):
        self.model.mesh_to_follow = text

    def prebuild(self):
        # self.side = {"Left": 1, "Center": 0, "Right": -1}
        # self.side_coef = self.side.get(self.model.side)

        mesh_to_follow_list = pmc.ls(self.model.mesh_to_follow)
        if not mesh_to_follow_list:
            pmc.error("for module \"{0}\", no mesh given, need one to attach the ctrls".format(self.model.module_name))
            return False
        elif len(mesh_to_follow_list) > 1:
            pmc.error("for module \"{0}\", multiple objects match given name, give the long_name of the object to find the chosen one".format(self.model.module_name))
            return False
        elif mesh_to_follow_list[0].getShape() is None or pmc.nodeType(mesh_to_follow_list[0].getShape()) != "mesh":
            pmc.error("for module \"{0}\", given object isn't a mesh".format(self.model.module_name))
            return False
        else:
            self.mesh_to_follow = mesh_to_follow_list[0]

        self.guides_names = []
        for i in range(self.model.how_many_ctrls):
            self.guides_names.append("{0}_{1}_GUIDE".format(self.model.module_name, i + 1))

        if self.guide_check(self.guides_names):
            self.guides = pmc.ls(self.guides_names)

            for guide in self.guides:
                pmc.parent(guide, world=1)

            # self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            self.guides_grp = self.group_guides(self.guides)

            self.guides_grp.setAttr("visibility", 1)
            self.view.refresh_view()
            pmc.select(cl=1)
            return True

        self.guides = []
        for guide in self.guides_names:
            self.guides.append(pmc.spaceLocator(p=(0, 0, 0), n=guide))

        self.guides_grp = self.group_guides(self.guides)
        self.view.refresh_view()
        pmc.select(cl=1)
        return True

    def execute(self):
        if not self.prebuild():
            return

        self.create_follicles()
        self.create_ctrls()
        self.clean_rig()

        pmc.select(clear=1)

    def create_follicles(self):
        self. follicles = []

        for guide in self.guides:
            if pmc.objExists(str(guide).replace("_GUIDE", "_FOL")):
                pmc.delete(str(guide).replace("_GUIDE", "_FOL"))
            follicle_shape = pmc.createNode("follicle", n=str(guide).replace("_GUIDE", "_FOLShape"))
            follicle = follicle_shape.getParent()
            follicle.rename(str(guide).replace("_GUIDE", "_FOL"))

            follicle_shape.outTranslate >> follicle.translate
            follicle_shape.outRotate >> follicle.rotate
            self.mesh_to_follow.getShape().outMesh >> follicle_shape.inputMesh
            self.mesh_to_follow.getShape().worldMatrix[0] >> follicle_shape.inputWorldMatrix

            point_on_mesh = pmc.createNode("closestPointOnMesh", n=str(guide)+"CPM")
            self.mesh_to_follow.getShape().outMesh >> point_on_mesh.inMesh
            self.mesh_to_follow.getShape().worldMatrix[0] >> point_on_mesh.inputMatrix
            guide.getShape().worldPosition[0] >> point_on_mesh.inPosition

            follicle_shape.setAttr("parameterU", point_on_mesh.getAttr("parameterU"))
            follicle_shape.setAttr("parameterV", point_on_mesh.getAttr("parameterV"))

            pmc.delete(point_on_mesh)

            self.follicles.append(follicle)

    def create_ctrls(self):
        self.ctrls = []

        for fol in self.follicles:
            pmc.select(clear=1)
            ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=1, d=3, s=8,
                                    n=str(fol).replace("_FOL", "_ctrl_Shape"), ch=0)[0]
            ctrl = rig_lib.create_jnttype_ctrl(name=str(fol).replace("_FOL", "_CTRL"), shape=ctrl_shape)

            pmc.select(clear=1)
            ctrl_ofs = pmc.joint(p=(0, 0, 0), n=str(ctrl).replace("_CTRL", "_ctrl_OFS"))
            ctrl_ofs.setAttr("drawStyle", 2)

            ctrl_fix_r = pmc.joint(p=(0, 0, 0), n=str(ctrl).replace("_CTRL", "_ctrl_rotate_FIX"))
            ctrl_fix_r.setAttr("drawStyle", 2)
            ctrl_fix_r.setAttr("rotateOrder", 5)

            ctrl_fix_t = pmc.joint(p=(0, 0, 0), n=str(ctrl).replace("_CTRL", "_ctrl_translate_FIX"))
            ctrl_fix_t.setAttr("drawStyle", 2)

            pmc.parent(ctrl, ctrl_fix_t)
            pmc.parent(ctrl_ofs, fol)

            ctrl_ofs.setAttr("translate", (0, 0, 0))
            ctrl_ofs.setAttr("rotate", (0, 0, 0))
            ctrl_ofs.setAttr("jointOrient", (0, 0, 0))

            invert_ctrl_translate = pmc.createNode("multiplyDivide", n=str(ctrl)+"invert_translate_MDL")
            invert_ctrl_rotate = pmc.createNode("multiplyDivide", n=str(ctrl)+"invert_rotate_MDL")

            ctrl.translate >> invert_ctrl_translate.input1
            invert_ctrl_translate.setAttr("input2", (-1, -1, -1))
            invert_ctrl_translate.output >> ctrl_fix_t.translate

            ctrl.rotate >> invert_ctrl_rotate.input1
            invert_ctrl_rotate.setAttr("input2", (-1, -1, -1))
            invert_ctrl_rotate.output >> ctrl_fix_r.rotate

            ctrl_cvs = ctrl.cv[:]
            for i, cv in enumerate(ctrl_cvs):
                    pmc.xform(ctrl.getShape().controlPoints[i],
                              translation=(pmc.xform(cv, q=1, translation=1)[0],
                                           pmc.xform(cv, q=1, translation=1)[1],
                                           pmc.xform(cv, q=1, translation=1)[2] + 1))

            self.ctrls.append(ctrl)

    def clean_rig(self):
        self.guides_grp.setAttr("visibility", 0)

        for i, fol in enumerate(self.follicles):
            fol.getShape().setAttr("visibility", 0)

            if fol.getAttr("translateX") > 0.02:
                color_value = 6
            elif fol.getAttr("translateX") < -0.02:
                color_value = 13
            else:
                color_value = 14

            rig_lib.clean_ctrl(self.ctrls[i], color_value, trs="s")
            rig_lib.clean_ctrl(self.ctrls[i].getParent(), color_value, trs="trs")
            rig_lib.clean_ctrl(self.ctrls[i].getParent().getParent(), color_value, trs="trs")

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

            rig_lib.add_parameter_as_extra_attr(info_crv, "Module", "blendshapes_ctrls")
            rig_lib.add_parameter_as_extra_attr(info_crv, "mesh_to_follow", self.model.mesh_to_follow)
            rig_lib.add_parameter_as_extra_attr(info_crv, "how_many_ctrls", self.model.how_many_ctrls)


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        # self.selected_module = None
        # self.selected_output = None
        # self.side = "Left"
        self.how_many_ctrls = 1
        self.mesh_to_follow = None
