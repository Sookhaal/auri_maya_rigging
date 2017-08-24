from PySide2 import QtWidgets, QtCore

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

        select_parent_layout = QtWidgets.QVBoxLayout()
        select_parent_grp = grpbox("Select parent", select_parent_layout)
        cbbox_layout = QtWidgets.QHBoxLayout()
        cbbox_layout.addWidget(self.modules_cbbox)
        cbbox_layout.addWidget(self.outputs_cbbox)
        select_parent_layout.addLayout(cbbox_layout)
        select_parent_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(select_parent_grp)
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
        RigController.__init__(self,  model, view)

    def prebuild(self):
        self.create_temporary_outputs(["OUTPUT"])

        self.guide_name = "{0}_GUIDE".format(self.model.module_name)
        if self.guide_check(self.guide_name):
            self.guide = pmc.ls(self.guide_name)
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            return

        self.guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guide_name)
        self.guide.setAttr("translate", (0, 7.5, 0))
        self.guides_grp = self.group_guides(self.guide)
        self.guides_grp.setAttr("visibility", 1)
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()

        cog_ctrl = rig_lib.large_box_curve("{0}_CTRL".format(self.model.module_name))
        cog_ofs = pmc.group(cog_ctrl, n="{0}_ctrl_OFS".format(self.model.module_name))
        cog_ofs.setAttr("translate", pmc.xform(self.guide, q=1, ws=1, translation=1))
        pmc.parent(cog_ofs, self.ctrl_input_grp)

        rig_lib.create_output(name="{0}_OUTPUT".format(self.model.module_name), parent=cog_ctrl)

        rig_lib.clean_ctrl(cog_ctrl, 20, trs="")

        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        pmc.select(d=1)


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
