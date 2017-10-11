from PySide2 import QtWidgets, QtCore

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, grpbox
from auri.scripts.Maya_Scripts import rig_lib
from auri.scripts.Maya_Scripts.rig_lib import RigController

reload(rig_lib)


class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        self.orientation_cbbox = QtWidgets.QComboBox()
        self.rotate_order_cbbox = QtWidgets.QComboBox()
        self.size = QtWidgets.QDoubleSpinBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.size.setValue(self.model.size)
        self.orientation_cbbox.setCurrentText(self.model.orientation)
        self.rotate_order_cbbox.setCurrentText(self.model.rotate_order)

    def setup_ui(self):
        self.size.valueChanged.connect(self.ctrl.on_size_changed)

        self.orientation_cbbox.insertItems(0, ["X", "Y", "Z"])
        self.orientation_cbbox.currentTextChanged.connect(self.ctrl.on_orientation_changed)

        self.rotate_order_cbbox.insertItems(0, ["xyz", "yzx", "zxy", "xzy", "yxz", "zyx"])
        self.rotate_order_cbbox.currentTextChanged.connect(self.ctrl.on_rotate_order_changed)

        main_layout = QtWidgets.QVBoxLayout()

        orientation_layout = QtWidgets.QVBoxLayout()
        orientation_grp = grpbox("Orientation :", orientation_layout)
        orientation_layout.addWidget(self.orientation_cbbox)

        size_layout = QtWidgets.QVBoxLayout()
        size_grp = grpbox("Size :", size_layout)
        size_layout.addWidget(self.size)

        rotate_order_layout = QtWidgets.QVBoxLayout()
        rotate_order_grp = grpbox("Rotate_Order :", rotate_order_layout)
        rotate_order_layout.addWidget(self.rotate_order_cbbox)

        main_layout.addWidget(orientation_grp)
        main_layout.addWidget(size_grp)
        main_layout.addWidget(rotate_order_grp)
        self.setLayout(main_layout)


class Controller(RigController):
    def __init__(self, model, view):
        """

        Args:
            model (Model):
            view (View):
        """
        self.ctrl_name = ["Basic_CTRL"]
        self.selection = []
        self.orientation_values = {}
        self.orientation = None
        self.rotate_order_values = {}
        self.rotate_order = None
        RigController.__init__(self,  model, view)

    def on_size_changed(self, value):
        self.model.size = value

    def on_orientation_changed(self, text):
        self.model.orientation = text

    def on_rotate_order_changed(self, text):
        self.model.rotate_order = text

    def prebuild(self):
        self.selection = pmc.ls(sl=1, type=["transform", "joint"])

        self.orientation_values = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}
        self.orientation = self.orientation_values.get(self.model.orientation)

        self.rotate_order_values = {"xyz": 0, "yzx": 1, "zxy": 2, "xzy": 3, "yxz": 4, "zyx": 5}
        self.rotate_order = self.rotate_order_values.get(self.model.rotate_order)

    def execute(self):
        self.prebuild()

        for obj in self.selection:
            if pmc.objExists("{0}_ctrl_OFS".format(obj)):
                pmc.delete("{0}_ctrl_OFS".format(obj))

            pmc.select(d=1)

            ctrl_shape = pmc.circle(c=(0, 0, 0), nr=self.orientation, sw=360, r=self.model.size, d=3, s=8,
                                    n="{0}_CTRLShape".format(obj), ch=0)[0]
            ctrl = rig_lib.create_jnttype_ctrl("{0}_CTRL".format(obj), ctrl_shape, drawstyle=2,
                                               rotateorder=self.rotate_order)

            pmc.select(d=1)

            ctrl_ofs = pmc.joint(p=(0, 0, 0), n="{0}_ctrl_OFS".format(obj))
            ctrl_ofs.setAttr("rotateOrder", self.rotate_order)
            ctrl_ofs.setAttr("drawStyle", 2)
            pmc.parent(ctrl, ctrl_ofs)

            pmc.xform(ctrl_ofs, ws=1, matrix=pmc.xform(obj, q=1, ws=1, matrix=1))

        pmc.select(self.selection)


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.orientation = "Y"
        self.rotate_order = "xyz"
        self.size = 1.0
