from PySide2 import QtWidgets, QtCore

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel
from auri.auri_lib import grpbox
from auri.scripts.Maya_Scripts import rig_lib

reload(rig_lib)


class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        self.character_name = QtWidgets.QLineEdit()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.character_name.setText(self.model.character_name)

    def setup_ui(self):
        text = QtWidgets.QLabel("Module de base")
        self.character_name.textChanged.connect(self.ctrl.on_character_name_changed)

        main_layout = QtWidgets.QVBoxLayout()

        character_name_layout = QtWidgets.QVBoxLayout()
        character_name_grp = grpbox("Character name", character_name_layout)

        character_name_layout.addWidget(self.character_name)

        main_layout.addWidget(text)
        text.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(character_name_grp)
        self.setLayout(main_layout)


class Controller(AuriScriptController):
    def __init__(self, model):
        self.model = model
        AuriScriptController.__init__(self)

    def on_character_name_changed(self, text):
        self.model.character_name = text

    def execute(self):
        check_list = ["{0}".format(self.model.character_name), "GEO_GRP", "CTRL_GRP", "JNT_GRP", "MESH_GRP", "PARTS_GRP",
                      "global_CTRL", "global_OUTPUT", "local_INPUT", "local_ctrl_OFS", "local_CTRL", "global_scale_MDL"]
        if rig_lib.exists_check(check_list):
            pmc.select(d=1)
            return

        if rig_lib.exists_check("{0}".format(self.model.character_name)):
            pmc.delete("{0}".format(self.model.character_name))

        main_grp = pmc.group(em=1, n="{0}".format(self.model.character_name))
        geo_grp = pmc.group(em=1, n="GEO_GRP")
        ctrl_grp = pmc.group(em=1, n="CTRL_GRP")
        jnt_grp = pmc.group(em=1, n="JNT_GRP")
        mesh_grp = pmc.group(em=1, n="MESH_GRP")
        parts_grp = pmc.group(em=1, n="PARTS_GRP")
        global_ctrl = rig_lib.square_arrow_curve("global_CTRL")
        global_output = pmc.spaceLocator(p=(0, 0, 0), n="global_OUTPUT")
        global_output.visibility.set(0)

        pmc.parent(geo_grp, ctrl_grp, jnt_grp, mesh_grp, parts_grp, global_ctrl, main_grp)
        pmc.parent(global_output, global_ctrl, r=1)
        local_input = pmc.group(em=1, n="local_INPUT")
        pmc.parent(local_input, ctrl_grp, r=1)

        rig_lib.matrix_constraint(global_output, local_input, srt="trs")

        local_ctrl = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=5, d=3, s=8, n="local_CTRL", ch=0)[0]
        local_ofs = pmc.group(local_ctrl, n="local_ctrl_OFS")
        pmc.parent(local_ofs, local_input, r=1)

        rig_lib.change_shape_color(global_ctrl, 3)
        rig_lib.change_shape_color(local_ctrl, 17)

        global_scale_mult_node = pmc.createNode("multDoubleLinear", n="global_scale_MDL")

        global_ctrl.scaleY >> global_ctrl.scaleX
        global_ctrl.scaleY >> global_ctrl.scaleZ
        local_ctrl.scaleY >> local_ctrl.scaleX
        local_ctrl.scaleY >> local_ctrl.scaleZ
        global_ctrl.scaleY >> global_scale_mult_node.input1
        local_ctrl.scaleY >> global_scale_mult_node.input2

        pmc.select(d=1)


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.character_name = "No_name"
