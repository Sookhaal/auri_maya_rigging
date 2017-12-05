from PySide2 import QtWidgets, QtCore, QtGui

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, grpbox
from auri.scripts.Maya_Scripts import rig_lib
from auri.scripts.Maya_Scripts.rig_lib import RigController

reload(rig_lib)


class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        self.prebuild_btn = QtWidgets.QPushButton("Prebuild")
        self.mesh_to_follow = QtWidgets.QLineEdit()
        self.Set_top_btn = QtWidgets.QPushButton("Set Selection")
        self.Set_bot_btn = QtWidgets.QPushButton("Set Selection")
        self.top_selection_view = QtWidgets.QListView()
        self.top_selection = QtGui.QStringListModel()
        self.bot_selection_view = QtWidgets.QListView()
        self.bot_selection = QtGui.QStringListModel()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.mesh_to_follow.setText(self.model.mesh_to_follow)
        self.top_selection.setStringList(self.model.top_selection)
        self.bot_selection.setStringList(self.model.bot_selection)

    def setup_ui(self):
        self.mesh_to_follow.textChanged.connect(self.ctrl.on_mesh_to_follow_changed)

        self.top_selection_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.top_selection.setStringList(self.model.top_selection)
        self.top_selection_view.setModel(self.top_selection)

        self.Set_top_btn.clicked.connect(self.ctrl.set_top_selection)

        self.bot_selection_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.bot_selection.setStringList(self.model.bot_selection)
        self.bot_selection_view.setModel(self.bot_selection)

        self.Set_bot_btn.clicked.connect(self.ctrl.set_bot_selection)

        self.prebuild_btn.clicked.connect(self.ctrl.prebuild)

        main_layout = QtWidgets.QVBoxLayout()

        mesh_to_follow_layout = QtWidgets.QVBoxLayout()
        mesh_to_follow_grp = grpbox("Mesh to attach the ctrls to:", mesh_to_follow_layout)
        mesh_to_follow_layout.addWidget(self.mesh_to_follow)

        # TODO ajouter le visuel de selection

        options_layout = QtWidgets.QVBoxLayout()
        options_grp = grpbox("Options", options_layout)

        ctrls_layout = QtWidgets.QVBoxLayout()
        ctrls_text = QtWidgets.QLabel("Option :")
        ctrls_layout.addWidget(ctrls_text)

        options_layout.addLayout(ctrls_layout)

        main_layout.addWidget(mesh_to_follow_grp)
        main_layout.addWidget(options_grp)
        self.setLayout(main_layout)


class Controller(RigController):
    def __init__(self, model, view):
        """

        Args:
            model (Model):
            view (View):
        """
        self.mesh_to_follow = None
        self.have_a_mesh = False
        RigController.__init__(self,  model, view)

    def on_mesh_to_follow_changed(self, text):
        self.model.mesh_to_follow = text

    def set_top_selection(self):
        selection = pmc.ls(sl=1, flatten=1)
        self.model.top_selection = [selection]
        self.view.top_selection.setStringList(self.model.top_selection)

    def set_bot_selection(self):
        selection = pmc.ls(sl=1, flatten=1)
        self.model.bot_selection = [selection]
        self.view.bot_selection.setStringList(self.model.bot_selection)

    def prebuild(self):
        mesh_to_follow_list = pmc.ls(self.model.mesh_to_follow)
        if not mesh_to_follow_list:
            print "no mesh given, need one to attach the ctrls"
            self.have_a_mesh = False
        elif len(mesh_to_follow_list) > 1:
            print "multiple objects match given name, give the long_name of the object to find the chosen one"
            self.have_a_mesh = False
        elif mesh_to_follow_list[0].getShape() is None or pmc.nodeType(mesh_to_follow_list[0].getShape()) != "mesh":
            print "given object isn't a mesh"
            self.have_a_mesh = False
        else:
            self.mesh_to_follow = mesh_to_follow_list[0]
            self.have_a_mesh = True

        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        # self.selected_module = None
        # self.selected_output = None
        # self.side = "Center"
        self.top_selection = None
        self.bot_selection = None
        self.mesh_to_follow = None
