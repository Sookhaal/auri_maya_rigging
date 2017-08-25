from PySide2 import QtWidgets, QtCore, QtGui
from functools import partial

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, is_checked, grpbox
from auri.scripts.Maya_Scripts import rig_lib
from auri.scripts.Maya_Scripts.rig_lib import RigController

reload(rig_lib)


class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        self.modules_cbbox = QtWidgets.QComboBox()
        self.outputs_cbbox = QtWidgets.QComboBox()
        self.object_modules_cbbox = QtWidgets.QComboBox()
        self.objects_cbbox = QtWidgets.QComboBox()
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.prebuild_btn = QtWidgets.QPushButton("Prebuild")
        # self.how_many_toes = QtWidgets.QSpinBox()
        self.side_cbbox = QtWidgets.QComboBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.side_cbbox.setCurrentText(self.model.side)
        # self.how_many_toes.setValue(self.model.how_many_toes)
        self.ctrl.look_for_parent()
        self.ctrl.look_for_out_objects()

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        self.object_modules_cbbox.setModel(self.ctrl.modules_with_out_objects)
        self.object_modules_cbbox.currentTextChanged.connect(self.ctrl.on_object_modules_cbbox_changed)

        self.objects_cbbox.setModel(self.ctrl.objects_model)
        self.objects_cbbox.currentTextChanged.connect(self.ctrl.on_objects_cbbox_changed)

        self.side_cbbox.insertItems(0, ["Left", "Right"])
        self.side_cbbox.currentTextChanged.connect(self.ctrl.on_side_cbbox_changed)

        # self.how_many_toes.setMinimum(1)
        # self.how_many_toes.valueChanged.connect(self.ctrl.on_how_many_toes_changed)

        self.refresh_btn.clicked.connect(self.ctrl.look_for_parent)
        self.refresh_btn.clicked.connect(self.ctrl.look_for_out_objects)
        self.prebuild_btn.clicked.connect(self.ctrl.prebuild)

        main_layout = QtWidgets.QVBoxLayout()

        select_parent_and_object_layout = QtWidgets.QVBoxLayout()

        select_parent_layout = QtWidgets.QVBoxLayout()
        select_parent_grp = grpbox("Select parent", select_parent_layout)
        parent_cbbox_layout = QtWidgets.QHBoxLayout()
        parent_cbbox_layout.addWidget(self.modules_cbbox)
        parent_cbbox_layout.addWidget(self.outputs_cbbox)

        select_object_layout = QtWidgets.QVBoxLayout()
        select_object_grp = grpbox("Leg ik handle", select_object_layout) #TODO: check ik_HDL only
        object_cbbox_layout = QtWidgets.QHBoxLayout()
        object_cbbox_layout.addWidget(self.object_modules_cbbox)
        object_cbbox_layout.addWidget(self.objects_cbbox)

        select_parent_layout.addLayout(parent_cbbox_layout)
        select_object_layout.addLayout(object_cbbox_layout)
        select_parent_and_object_layout.addWidget(select_parent_grp)
        select_parent_and_object_layout.addWidget(select_object_grp)
        select_parent_and_object_layout.addWidget(self.refresh_btn)

        side_layout = QtWidgets.QVBoxLayout()
        side_grp = grpbox("Side", side_layout)
        side_layout.addWidget(self.side_cbbox)

        # options_layout = QtWidgets.QVBoxLayout()
        # options_grp = grpbox("Options", options_layout)
        #
        # toes_layout = QtWidgets.QVBoxLayout()
        # toes_text = QtWidgets.QLabel("How many toes :")
        # toes_layout.addWidget(toes_text)
        # toes_layout.addWidget(self.how_many_toes)
        #
        # options_layout.addLayout(toes_layout)

        main_layout.addLayout(select_parent_and_object_layout)
        main_layout.addWidget(side_grp)
        # main_layout.addWidget(options_grp)
        main_layout.addWidget(self.prebuild_btn)
        self.setLayout(main_layout)


class Controller(RigController):
    def __init__(self, model, view):
        """

        Args:
            model (Model):
            view (View):
        """
        self.modules_with_out_objects = QtGui.QStringListModel()
        self.objects_model = QtGui.QStringListModel()
        self.current_object_module = None
        self.guides_grp = None
        self.guides = []
        self.guides_names = []
        self.side = {}
        self.side_coef = 0
        self.created_skn_jnts = []
        RigController.__init__(self, model, view)

    def look_for_out_objects(self):
        self.look_for_parent("temporary_out_objects",
                             self.modules_with_out_objects, self.model.selected_object_module,
                             self.view.object_modules_cbbox,
                             self.objects_model, self.model.selected_object, self.view.objects_cbbox)

    # def on_how_many_toes_changed(self, value):
    #     self.model.how_many_toes = value

    def on_object_modules_cbbox_changed(self, text):
        if self.has_updated_modules:
            self.model.selected_object_module = text
            self.look_for_out_objects()

    def on_objects_cbbox_changed(self, text):
        self.model.selected_object = text

    def prebuild(self):
        self.guides_names = ["{0}_ankle_GUIDE".format(self.model.module_name), "{0}_ball_GUIDE".format(self.model.module_name),
                             "{0}_toe_GUIDE".format(self.model.module_name), "{0}_heel_GUIDE".format(self.model.module_name),
                             "{0}_infoot_GUIDE".format(self.model.module_name), "{0}_outfoot_GUIDE".format(self.model.module_name), ]

        self.side = {"Left": 1, "Right": -1}
        self.side_coef = self.side.get(self.model.side)

        if self.guide_check(self.guides_names):
            self.guides = pmc.ls(self.guides_names)
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            return

        ankle_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0])
        ball_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[1])
        toe_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[2])
        heel_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[3])
        infoot_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[4])
        outfoot_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[5])

        ankle_guide.setAttr("translate", (2 * self.side_coef, 1, 0))
        ball_guide.setAttr("translate", (2 * self.side_coef, 0.5, 1.5))
        toe_guide.setAttr("translate", (2 * self.side_coef, 0, 3))
        heel_guide.setAttr("translate", (2 * self.side_coef, 0, -1))
        infoot_guide.setAttr("translate", (1 * self.side_coef, 0, 1))
        outfoot_guide.setAttr("translate", (3 * self.side_coef, 0, 1))

        self.guides = [ankle_guide, ball_guide, toe_guide, heel_guide, infoot_guide, outfoot_guide]
        self.guides_grp = self.group_guides(self.guides)
        self.guides_grp.setAttr("visibility", 1)
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()

        self.create_skn_jnts()

    def create_skn_jnts(self):
        duplicates_guides = []
        for guide in self.guides:
            duplicate = guide.duplicate(n="{0}_duplicate".format(guide))[0]
            duplicates_guides.append(duplicate)

        ankle_const = pmc.aimConstraint(duplicates_guides[1], duplicates_guides[0], maintainOffset=0,
                                        aimVector=(1.0 * self.side_coef, 0.0, 0.0),
                                        upVector=(0.0, -1.0 * self.side_coef, 0.0), worldUpType="scene")
        ball_cons = pmc.aimConstraint(duplicates_guides[2], duplicates_guides[1], maintainOffset=0,
                                      aimVector=(1.0 * self.side_coef, 0.0, 0.0),
                                      upVector=(0.0, -1.0 * self.side_coef, 0.0), worldUpType="scene")

        pmc.delete(ankle_const)
        pmc.delete(ball_cons)
        pmc.parent(duplicates_guides[1], duplicates_guides[0])
        pmc.parent(duplicates_guides[2], duplicates_guides[1])

        temp_guide_orient = pmc.group(em=1, n="temp_guide_orient_grp")
        temp_guide_orient.setAttr("translate", pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1))
        temp_guide_orient.setAttr("rotate", 90 * (self.side_coef + 1), -90 * self.side_coef, 0)
        pmc.parent(duplicates_guides[0], temp_guide_orient, r=0)
        pmc.select(d=1)

        ankle_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1)),
                              n="{0}_foot_JNT".format(self.model.module_name))
        ankle_jnt.setAttr("rotate", pmc.xform(duplicates_guides[0], q=1, rotation=1))
        ankle_jnt.setAttr("jointOrientX", 90 * (self.side_coef + 1))
        ankle_jnt.setAttr("jointOrientY", -90 * self.side_coef)
        ankle_jnt.setAttr("jointOrientZ", 0)

        ball_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1)),
                             n="{0}_ball_SKN".format(self.model.module_name))
        ball_jnt.setAttr("rotate", pmc.xform(duplicates_guides[1], q=1, rotation=1))
        toe_jnt = pmc.joint(p=(pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1)),
                            n="{0}_toe_SKN".format(self.model.module_name))

        pmc.parent(ankle_jnt, self.jnt_input_grp, r=0)
        self.created_skn_jnts = [ankle_jnt, ball_jnt, toe_jnt]

        pmc.delete(duplicates_guides[:])


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.selected_object_module = None
        self.selected_object = None
        self.side = "Left"
        # self.how_many_toes = 1
