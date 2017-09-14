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
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.ctrl.look_for_parent()

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

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

        main_layout.addLayout(select_parent_and_object_layout)
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
        self.created_skn_jnts = []
        self.created_ctrls = []
        RigController.__init__(self, model, view)

    def prebuild(self):
        self.guides_names = ["{0}_head_base_GUIDE".format(self.model.module_name), "{0}_head_top_GUIDE".format(self.model.module_name),
                             "{0}_jaw_rotation_GUIDE".format(self.model.module_name), "{0}_jaw_end_GUIDE".format(self.model.module_name),
                             "{0}_left_eye_GUIDE".format(self.model.module_name), "{0}_right_eye_GUIDE".format(self.model.module_name)]

        if self.guide_check(self.guides_names):
            self.guides = pmc.ls(self.guides_names)
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            self.guides_grp.setAttr("visibility", 1)
            return

        head_base_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0])
        head_top_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[1])
        jaw_rotation_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[2])
        jaw_end_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[3])
        left_eye_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[4])
        right_eye_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[5])

        head_base_guide.setAttr("translate", (0, 23, 0))
        head_top_guide.setAttr("translate", (0, 28, 0))
        jaw_rotation_guide.setAttr("translate", (0, 24, 1))
        jaw_end_guide.setAttr("translate", (0, 23.5, 4))
        left_eye_guide.setAttr("translate", (1, 27, 3))
        right_eye_guide.setAttr("translate", (-1, 27, 3))

        self.guides = [head_base_guide, head_top_guide, jaw_rotation_guide, jaw_end_guide, left_eye_guide, right_eye_guide]
        self.guides_grp = self.group_guides(self.guides)
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()

        self.create_skn_jnts()
        self.create_ctrls()

        self.clean_rig()
        pmc.select(d=1)

    def create_skn_jnts(self):
        duplicates_guides = []
        for guide in self.guides:
            duplicate = guide.duplicate(n="{0}_duplicate".format(guide))[0]
            duplicates_guides.append(duplicate)

        head_const = pmc.aimConstraint(duplicates_guides[1], duplicates_guides[0], maintainOffset=0,
                                       aimVector=(0.0, 1.0, 0.0), upVector=(1.0, 0.0, 0.0), worldUpType="vector",
                                       worldUpVector=(1, 0, 0))
        jaw_const = pmc.aimConstraint(duplicates_guides[3], duplicates_guides[2], maintainOffset=0,
                                      aimVector=(0.0, 1.0, 0.0), upVector=(0.0, 0.0, -1.0), worldUpType="scene")
        pmc.delete(head_const)
        pmc.delete(jaw_const)
        pmc.parent(duplicates_guides[1], duplicates_guides[0])
        pmc.parent(duplicates_guides[3], duplicates_guides[2])
        pmc.select(d=1)

        head_base_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1)),
                                  n="{0}_head_SKN".format(self.model.module_name))
        head_base_jnt.setAttr("jointOrient", pmc.xform(duplicates_guides[0], q=1, rotation=1))
        head_end_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1)),
                                 n="{0}_head_end_JNT".format(self.model.module_name))
        pmc.select(d=1)
        jaw_base_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)),
                                 n="{0}_jaw_SKN".format(self.model.module_name))
        jaw_base_jnt.setAttr("jointOrient", pmc.xform(duplicates_guides[2], q=1, rotation=1))
        jaw_end_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[3], q=1, ws=1, translation=1)),
                                n="{0}_jaw_end_JNT".format(self.model.module_name))
        pmc.select(d=1)
        left_eye_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[4], q=1, ws=1, translation=1)),
                                 n="{0}_left_eye_SKN".format(self.model.module_name))
        pmc.select(d=1)
        right_eye_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[5], q=1, ws=1, translation=1)),
                                  n="{0}_right_eye_SKN".format(self.model.module_name))

        pmc.parent(head_base_jnt, self.jnt_input_grp)
        pmc.parent(jaw_base_jnt, self.jnt_input_grp)
        pmc.parent(left_eye_jnt, self.jnt_input_grp)
        pmc.parent(right_eye_jnt, self.jnt_input_grp)

        self.created_skn_jnts = [head_base_jnt, head_end_jnt, jaw_base_jnt, jaw_end_jnt, left_eye_jnt, right_eye_jnt]

        pmc.delete(duplicates_guides[:])

    def create_ctrls(self):
        jaw_shape = pmc.circle(c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=3, d=3, s=8,
                               n="{0}_jaw_CTRL_shape".format(self.model.module_name), ch=0)[0]
        jaw_ctrl = rig_lib.create_jnttype_ctrl(name="{0}_jaw_CTRL".format(self.model.module_name), shape=jaw_shape, drawstyle=2)
        # jaw_ofs = pmc.group(jaw_ctrl, n="{0}_jaw_ctrl_OFS".format(self.model.module_name))
        jaw_cvs = jaw_ctrl.getShape().cv[:]
        for cv in jaw_cvs:
            pmc.xform(cv, ws=1, translation=(pmc.xform(cv, q=1, ws=1, translation=1)[0],
                                             pmc.xform(cv, q=1, ws=1, translation=1)[1] + 2,
                                             pmc.xform(cv, q=1, ws=1, translation=1)[2]))
        jaw_ctrl.setAttr("translate", pmc.xform(self.created_skn_jnts[2], q=1, ws=1, translation=1))
        jaw_ctrl.setAttr("jointOrient", pmc.xform(self.created_skn_jnts[2], q=1, ws=1, rotation=1))
        pmc.parent(jaw_ctrl, self.ctrl_input_grp)
        jaw_ctrl.rotate >> self.created_skn_jnts[2].rotate

        l_eye_shape = pmc.circle(c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=1, d=3, s=8,
                                n="{0}_left_eye_CTRL_shape".format(self.model.module_name), ch=0)[0]
        l_eye_ctrl = rig_lib.create_jnttype_ctrl(name="{0}_left_eye_CTRL".format(self.model.module_name), shape=l_eye_shape,
                                                 drawstyle=2)
        # l_eye_ofs = pmc.group(l_eye_ctrl, n="{0}_left_eye_ctrl_OFS".format(self.model.module_name))
        l_eye_cvs = l_eye_ctrl.getShape().cv[:]
        for cv in l_eye_cvs:
            pmc.xform(cv, ws=1, translation=(pmc.xform(cv, q=1, ws=1, translation=1)[0],
                                             pmc.xform(cv, q=1, ws=1, translation=1)[1],
                                             pmc.xform(cv, q=1, ws=1, translation=1)[2] + 2))
        l_eye_ctrl.setAttr("translate", pmc.xform(self.created_skn_jnts[4], q=1, ws=1, translation=1))
        pmc.parent(l_eye_ctrl, self.ctrl_input_grp)
        l_eye_ctrl. rotate >> self.created_skn_jnts[4].rotate

        r_eye_shape = pmc.circle(c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=1, d=3, s=8,
                                n="{0}_right_eye_CTRL_shape".format(self.model.module_name), ch=0)[0]
        # r_eye_ofs = pmc.group(r_eye_ctrl, n="{0}_right_eye_ctrl_OFS".format(self.model.module_name))
        r_eye_ctrl = rig_lib.create_jnttype_ctrl(name="{0}_right_eye_CTRL".format(self.model.module_name), shape=r_eye_shape,
                                                 drawstyle=2)
        r_eye_cvs = r_eye_ctrl.getShape().cv[:]
        for cv in r_eye_cvs:
            pmc.xform(cv, ws=1, translation=(pmc.xform(cv, q=1, ws=1, translation=1)[0],
                                             pmc.xform(cv, q=1, ws=1, translation=1)[1],
                                             pmc.xform(cv, q=1, ws=1, translation=1)[2] + 2))
        r_eye_ctrl.setAttr("translate", pmc.xform(self.created_skn_jnts[5], q=1, ws=1, translation=1))
        pmc.parent(r_eye_ctrl, self.ctrl_input_grp)
        r_eye_ctrl.rotate >> self.created_skn_jnts[5].rotate

        self.created_ctrls = [jaw_ctrl, l_eye_ctrl, r_eye_ctrl]

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        rig_lib.clean_ctrl(self.created_ctrls[0], 18, trs="ts")
        rig_lib.clean_ctrl(self.created_ctrls[1], 6, trs="ts")
        rig_lib.clean_ctrl(self.created_ctrls[2], 13, trs="ts")


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
