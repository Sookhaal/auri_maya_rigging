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
        self.side_cbbox = QtWidgets.QComboBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.side_cbbox.setCurrentText(self.model.side)
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

        main_layout.addLayout(select_parent_and_object_layout)
        main_layout.addWidget(side_grp)
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
        RigController.__init__(self, model, view)

    def look_for_out_objects(self):
        self.look_for_parent("temporary_out_objects",
                             self.modules_with_out_objects, self.model.selected_object_module,
                             self.view.object_modules_cbbox,
                             self.objects_model, self.model.selected_object, self.view.objects_cbbox)

    def on_object_modules_cbbox_changed(self, text):
        if self.has_updated_modules:
            self.model.selected_object_module = text
            self.look_for_out_objects()

    def on_objects_cbbox_changed(self, text):
        if self.has_updated_outputs:
            self.model.selected_object = text

    def prebuild(self):
        pass

    def execute(self):
        pass


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.selected_object_module = None
        self.selected_object = None
        self.side = "Left"
