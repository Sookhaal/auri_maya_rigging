from PySide2 import QtWidgets, QtCore

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, grpbox
from auri.scripts.Maya_Scripts import rig_lib
from auri.scripts.Maya_Scripts.rig_lib import RigController

reload(rig_lib)


class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        pass

    def setup_ui(self):
        main_layout = QtWidgets.QVBoxLayout()

        options_layout = QtWidgets.QVBoxLayout()
        options_grp = grpbox("Options", options_layout)

        ctrls_layout = QtWidgets.QVBoxLayout()
        ctrls_text = QtWidgets.QLabel("Option :")
        ctrls_layout.addWidget(ctrls_text)

        options_layout.addLayout(ctrls_layout)

        main_layout.addWidget(options_grp)
        self.setLayout(main_layout)


class Controller(RigController):
    def __init__(self, model, view):
        """

        Args:
            model (Model):
            view (View):
        """
        RigController.__init__(self,  model, view)

    def prebuild(self):
        pass

    def execute(self):
        self.prebuild()


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
