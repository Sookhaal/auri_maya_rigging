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
        self.side_cbbox = QtWidgets.QComboBox()
        self.thumb_creation_switch = QtWidgets.QCheckBox()
        self.how_many_fingers = QtWidgets.QSpinBox()
        self.how_many_phalanges = QtWidgets.QSpinBox()
        self.ik_creation_switch = QtWidgets.QCheckBox()
        self.stretch_creation_switch = QtWidgets.QCheckBox()
        self.raz_ik_ctrls = QtWidgets.QCheckBox()
        self.raz_fk_ctrls = QtWidgets.QCheckBox()
        self.roll_creation_switch = QtWidgets.QCheckBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.side_cbbox.setCurrentText(self.model.side)
        self.thumb_creation_switch.setChecked(self.model.thumb_creation_switch)
        self.how_many_fingers.setValue(self.model.how_many_fingers)
        self.how_many_phalanges.setValue(self.model.how_many_phalanges)
        self.ctrl.look_for_parent()
        self.ik_creation_switch.setChecked(self.model.ik_creation_switch)
        self.stretch_creation_switch.setChecked(self.model.stretch_creation_switch)
        self.raz_ik_ctrls.setChecked(self.model.raz_ik_ctrls)
        self.raz_fk_ctrls.setChecked(self.model.raz_fk_ctrls)
        self.roll_creation_switch.setChecked(self.model.roll_creation_switch)

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        self.thumb_creation_switch.stateChanged.connect(self.ctrl.on_thumb_creation_switch_changed)

        self.side_cbbox.insertItems(0, ["Left", "Right"])
        self.side_cbbox.currentTextChanged.connect(self.ctrl.on_side_cbbox_changed)

        self.how_many_fingers.setMinimum(1)
        self.how_many_fingers.valueChanged.connect(self.ctrl.on_how_many_fingers_changed)

        self.how_many_phalanges.setMinimum(2)
        self.how_many_phalanges.valueChanged.connect(self.ctrl.on_how_many_phalanges_changed)

        self.ik_creation_switch.stateChanged.connect(self.ctrl.on_ik_creation_switch_changed)

        self.stretch_creation_switch.stateChanged.connect(self.ctrl.on_stretch_creation_switch_changed)

        self.raz_ik_ctrls.stateChanged.connect(self.ctrl.on_raz_ik_ctrls_changed)
        self.raz_fk_ctrls.stateChanged.connect(self.ctrl.on_raz_fk_ctrls_changed)

        self.roll_creation_switch.stateChanged.connect(self.ctrl.on_roll_creation_switch_changed)

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

        side_layout = QtWidgets.QVBoxLayout()
        side_grp = grpbox("Side", side_layout)
        side_layout.addWidget(self.side_cbbox)

        options_layout = QtWidgets.QVBoxLayout()
        options_grp = grpbox("Options", options_layout)

        thumb_layout = QtWidgets.QHBoxLayout()
        thumb_text = QtWidgets.QLabel("thumb :")
        thumb_layout.addWidget(thumb_text)
        thumb_layout.addWidget(self.thumb_creation_switch)

        fingers_layout = QtWidgets.QVBoxLayout()
        fingers_text = QtWidgets.QLabel("How many fingers :")
        fingers_layout.addWidget(fingers_text)
        fingers_layout.addWidget(self.how_many_fingers)
        phalanges_text = QtWidgets.QLabel("How many phalanges for each fingers :")
        fingers_layout.addWidget(phalanges_text)
        fingers_layout.addWidget(self.how_many_phalanges)

        ik_creation_layout = QtWidgets.QHBoxLayout()
        ik_creation_text = QtWidgets.QLabel("IK fingers :")
        ik_creation_layout.addWidget(ik_creation_text)
        ik_creation_layout.addWidget(self.ik_creation_switch)

        stretch_layout = QtWidgets.QHBoxLayout()
        stretch_text = QtWidgets.QLabel("stretch/squash :")
        stretch_layout.addWidget(stretch_text)
        stretch_layout.addWidget(self.stretch_creation_switch)

        roll_creation_layout = QtWidgets.QHBoxLayout()
        roll_creation_text = QtWidgets.QLabel("Hand Roll :")
        roll_creation_layout.addWidget(roll_creation_text)
        roll_creation_layout.addWidget(self.roll_creation_switch)

        raz_ik_ctrls_layout = QtWidgets.QHBoxLayout()
        raz_ik_ctrls_text = QtWidgets.QLabel("\"Freez\" ik ctrls :")
        raz_ik_ctrls_layout.addWidget(raz_ik_ctrls_text)
        raz_ik_ctrls_layout.addWidget(self.raz_ik_ctrls)
        raz_fk_ctrls_layout = QtWidgets.QHBoxLayout()
        raz_fk_ctrls_text = QtWidgets.QLabel("\"Freez\" fk ctrls :")
        raz_fk_ctrls_layout.addWidget(raz_fk_ctrls_text)
        raz_fk_ctrls_layout.addWidget(self.raz_fk_ctrls)

        options_layout.addLayout(thumb_layout)
        options_layout.addLayout(ik_creation_layout)
        options_layout.addLayout(stretch_layout)
        options_layout.addLayout(roll_creation_layout)
        options_layout.addLayout(raz_ik_ctrls_layout)
        options_layout.addLayout(raz_fk_ctrls_layout)
        options_layout.addLayout(fingers_layout)

        main_layout.addLayout(select_parent_and_object_layout)
        main_layout.addWidget(side_grp)
        main_layout.addWidget(options_grp)
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
        self.roll_guides = []
        self.guides_names = []
        self.roll_guides_names = []
        self.side = {}
        self.side_coef = 0
        self.created_skn_jnts = []
        self.created_fk_ctrls = []
        self.parent_ankle_fk_ctrl = None
        self.parent_ankle_ik_ctrl = None
        self.parent_option_ctrl = None
        self.parent_ik_handle = None
        self.parent_ik_length_end_loc = None
        self.parent_ankle_rotation_handle = None
        self.jnts_to_skin = []
        self.ik_ctrls = []
        self.ik_setup_chain = []
        RigController.__init__(self, model, view)

    def on_how_many_fingers_changed(self, value):
        self.model.how_many_fingers = value

    def on_how_many_phalanges_changed(self, value):
        self.model.how_many_phalanges = value

    def on_thumb_creation_switch_changed(self, state):
        self.model.thumb_creation_switch = is_checked(state)

    def on_roll_creation_switch_changed(self, state):
        self.model.roll_creation_switch = is_checked(state)

    def prebuild(self):
        self.guides_names = []
        self.guides = []

        if self.model.thumb_creation_switch:
            thumb_first_jnt = "{0}_thumb_metacarpus_GUIDE".format(self.model.module_name)
            thumb_curve = "{0}_thumb_phalanges_GUIDE".format(self.model.module_name)
            thumb = [thumb_first_jnt, thumb_curve]
            self.guides_names.append(thumb)

        for i in range(0, self.model.how_many_fingers):
            first_jnt = "{0}_finger{1}_metacarpus_GUIDE".format(self.model.module_name, i + 1)
            finger_curve = "{0}_finger{1}_phalanges_GUIDE".format(self.model.module_name, i + 1)
            finger = [first_jnt, finger_curve]
            self.guides_names.append(finger)

        self.side = {"Left": 1, "Right": -1}
        self.side_coef = self.side.get(self.model.side)

        if self.guide_check(self.guides_names):
            self.guides = [pmc.ls(guide)[:] for guide in self.guides_names]

            if pmc.objExists("{0}_fingers_planes_GRP".format(self.model.module_name)):
                pmc.delete("{0}_fingers_planes_GRP".format(self.model.module_name))

            planes_group = pmc.group(em=1, n="{0}_fingers_planes_GRP".format(self.model.module_name))
            planes_group.setAttr("translateX", lock=True, keyable=False, channelBox=False)
            planes_group.setAttr("translateY", lock=True, keyable=False, channelBox=False)
            planes_group.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
            planes_group.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
            planes_group.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
            planes_group.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
            planes_group.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
            planes_group.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
            planes_group.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)

            for i, guide in enumerate(self.guides):
                if ((self.model.thumb_creation_switch and i != 0) or not self.model.thumb_creation_switch) and \
                                guide[1].getShape().getAttr("spans") != self.model.how_many_phalanges:
                    if self.model.how_many_phalanges > 2:
                        guide[1] = pmc.rebuildCurve(guide[1], rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                                    s=self.model.how_many_phalanges, d=1, ch=0, replaceOriginal=1)[0]
                    else:
                        guide[1] = pmc.rebuildCurve(guide[1], rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                                    s=4, d=1, ch=0, replaceOriginal=1)[0]
                        pmc.delete(guide[1].cv[-2])
                        pmc.delete(guide[1].cv[1])

                planes_loc_01 = pmc.spaceLocator(p=(0, 0, 0), n="{0}_start_LOC".format(guide[1]))
                planes_loc_02 = pmc.spaceLocator(p=(0, 0, 0), n="{0}_mid_LOC".format(guide[1]))
                planes_loc_03 = pmc.spaceLocator(p=(0, 0, 0), n="{0}_end_LOC".format(guide[1]))

                if self.model.thumb_creation_switch and i == 0 or self.model.how_many_phalanges == 2:
                    loc_01_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_01))
                    guide[1].getShape().worldSpace[0] >> loc_01_pos.geometryPath
                    loc_01_pos.setAttr("uValue", 0)
                    loc_01_pos.allCoordinates >> planes_loc_01.translate
                    planes_loc_01.setAttr("visibility", 0)

                    loc_02_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_02))
                    guide[1].getShape().worldSpace[0] >> loc_02_pos.geometryPath
                    loc_02_pos.setAttr("uValue", 1)
                    loc_02_pos.allCoordinates >> planes_loc_02.translate
                    planes_loc_02.setAttr("visibility", 0)

                    loc_03_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_03))
                    guide[1].getShape().worldSpace[0] >> loc_03_pos.geometryPath
                    loc_03_pos.setAttr("uValue", 2)
                    loc_03_pos.allCoordinates >> planes_loc_03.translate
                    planes_loc_03.setAttr("visibility", 0)
                else:
                    loc_01_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_01))
                    guide[1].getShape().worldSpace[0] >> loc_01_pos.geometryPath
                    loc_01_pos.setAttr("uValue", 0)
                    loc_01_pos.allCoordinates >> planes_loc_01.translate
                    planes_loc_01.setAttr("visibility", 0)

                    loc_02_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_02))
                    guide[1].getShape().worldSpace[0] >> loc_02_pos.geometryPath
                    loc_02_pos.setAttr("uValue", 0.5)
                    loc_02_pos.allCoordinates >> planes_loc_02.translate
                    planes_loc_02.setAttr("visibility", 0)

                    loc_03_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_03))
                    guide[1].getShape().worldSpace[0] >> loc_03_pos.geometryPath
                    loc_03_pos.setAttr("uValue", 1)
                    loc_03_pos.allCoordinates >> planes_loc_03.translate
                    planes_loc_03.setAttr("visibility", 0)

                plane = pmc.ls(pmc.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                                                   n="{0}_plane".format(guide[1]), ch=0))[0]

                planes_loc_01.getShape().worldPosition[0] >> plane.getShape().pnts[0]
                planes_loc_02.getShape().worldPosition[0] >> plane.getShape().pnts[1]
                planes_loc_03.getShape().worldPosition[0] >> plane.getShape().pnts[2]

                plane.setAttr("translateX", lock=True, keyable=False, channelBox=False)
                plane.setAttr("translateY", lock=True, keyable=False, channelBox=False)
                plane.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
                plane.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
                plane.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
                plane.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
                plane.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
                plane.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
                plane.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)
                plane.setAttr("overrideEnabled", 1)
                plane.setAttr("overrideDisplayType", 2)

                finger_group = pmc.group(em=1, n="{0}_plane_GRP".format(guide[1]))
                pmc.parent(planes_loc_01, finger_group)
                pmc.parent(planes_loc_02, finger_group)
                pmc.parent(planes_loc_03, finger_group)
                pmc.parent(plane, finger_group)
                pmc.parent(finger_group, planes_group)

            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            pmc.parent(planes_group, self.guides_grp)
            self.guides_grp.setAttr("visibility", 1)

            self.roll_prebuild()

            self.view.refresh_view()
            pmc.select(d=1)
            return

        planes_group = pmc.group(em=1, n="{0}_fingers_planes_GRP".format(self.model.module_name))
        planes_group.setAttr("translateX", lock=True, keyable=False, channelBox=False)
        planes_group.setAttr("translateY", lock=True, keyable=False, channelBox=False)
        planes_group.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
        planes_group.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
        planes_group.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
        planes_group.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
        planes_group.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
        planes_group.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
        planes_group.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)

        if self.model.thumb_creation_switch:
            thumb_ankle_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[0][0])
            thumb_ankle_guide.setAttr("translate", (2 * self.side_coef, 0.5, -1.5))
            thumb_guide = rig_lib.create_curve_guide(d=1, number_of_points=3, name=self.guides_names[0][1],
                                                     hauteur_curve=2)
            thumb_guide.setAttr("translate", (2 * self.side_coef, 0, -2))
            thumb_guide.setAttr("rotate", (-90, 0, 0))
            thumb = [thumb_ankle_guide, thumb_guide]
            self.guides.append(thumb)

            planes_loc_01 = pmc.spaceLocator(p=(0, 0, 0), n="{0}_start_LOC".format(thumb[1]))
            planes_loc_02 = pmc.spaceLocator(p=(0, 0, 0), n="{0}_mid_LOC".format(thumb[1]))
            planes_loc_03 = pmc.spaceLocator(p=(0, 0, 0), n="{0}_end_LOC".format(thumb[1]))

            loc_01_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_01))
            thumb[1].getShape().worldSpace[0] >> loc_01_pos.geometryPath
            loc_01_pos.setAttr("uValue", 0)
            loc_01_pos.allCoordinates >> planes_loc_01.translate
            planes_loc_01.setAttr("visibility", 0)

            loc_02_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_02))
            thumb[1].getShape().worldSpace[0] >> loc_02_pos.geometryPath
            loc_02_pos.setAttr("uValue", 1)
            loc_02_pos.allCoordinates >> planes_loc_02.translate
            planes_loc_02.setAttr("visibility", 0)

            loc_03_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_03))
            thumb[1].getShape().worldSpace[0] >> loc_03_pos.geometryPath
            loc_03_pos.setAttr("uValue", 2)
            loc_03_pos.allCoordinates >> planes_loc_03.translate
            planes_loc_03.setAttr("visibility", 0)

            plane = pmc.ls(pmc.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                                               n="{0}_plane".format(thumb[1]), ch=0))[0]

            planes_loc_01.getShape().worldPosition[0] >> plane.getShape().pnts[0]
            planes_loc_02.getShape().worldPosition[0] >> plane.getShape().pnts[1]
            planes_loc_03.getShape().worldPosition[0] >> plane.getShape().pnts[2]

            plane.setAttr("translateX", lock=True, keyable=False, channelBox=False)
            plane.setAttr("translateY", lock=True, keyable=False, channelBox=False)
            plane.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
            plane.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
            plane.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
            plane.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
            plane.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
            plane.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
            plane.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)
            plane.setAttr("overrideEnabled", 1)
            plane.setAttr("overrideDisplayType", 2)

            finger_group = pmc.group(em=1, n="{0}_plane_GRP".format(thumb[1]))
            pmc.parent(planes_loc_01, finger_group)
            pmc.parent(planes_loc_02, finger_group)
            pmc.parent(planes_loc_03, finger_group)
            pmc.parent(plane, finger_group)
            pmc.parent(finger_group, planes_group)

        for i, finger in enumerate(self.guides_names):
            if (self.model.thumb_creation_switch and i != 0) or not self.model.thumb_creation_switch:
                ankle_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.guides_names[i][0])
                ankle_guide.setAttr("translate", (1.5 * self.side_coef + (0.5 * (i - int(self.model.thumb_creation_switch)) * self.side_coef), 0.5, -0.5))
                finger_guide = rig_lib.create_curve_guide(d=1, number_of_points=(self.model.how_many_phalanges + 1),
                                                          name=finger[1], hauteur_curve=3)
                finger_guide.setAttr("translate", (1.5 * self.side_coef + (0.5 * (i - int(self.model.thumb_creation_switch)) * self.side_coef), 0, 0))
                finger_guide.setAttr("rotate", (90, 0, 0))
                finger = [ankle_guide, finger_guide]
                self.guides.append(finger)

                planes_loc_01 = pmc.spaceLocator(p=(0, 0, 0), n="{0}_start_LOC".format(finger[1]))
                planes_loc_02 = pmc.spaceLocator(p=(0, 0, 0), n="{0}_mid_LOC".format(finger[1]))
                planes_loc_03 = pmc.spaceLocator(p=(0, 0, 0), n="{0}_end_LOC".format(finger[1]))

                if self.model.how_many_phalanges == 2:
                    loc_01_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_01))
                    finger[1].getShape().worldSpace[0] >> loc_01_pos.geometryPath
                    loc_01_pos.setAttr("uValue", 0)
                    loc_01_pos.allCoordinates >> planes_loc_01.translate
                    planes_loc_01.setAttr("visibility", 0)

                    loc_02_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_02))
                    finger[1].getShape().worldSpace[0] >> loc_02_pos.geometryPath
                    loc_02_pos.setAttr("uValue", 1)
                    loc_02_pos.allCoordinates >> planes_loc_02.translate
                    planes_loc_02.setAttr("visibility", 0)

                    loc_03_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_03))
                    finger[1].getShape().worldSpace[0] >> loc_03_pos.geometryPath
                    loc_03_pos.setAttr("uValue", 2)
                    loc_03_pos.allCoordinates >> planes_loc_03.translate
                    planes_loc_03.setAttr("visibility", 0)
                else:
                    loc_01_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_01))
                    finger[1].getShape().worldSpace[0] >> loc_01_pos.geometryPath
                    loc_01_pos.setAttr("uValue", 0)
                    loc_01_pos.allCoordinates >> planes_loc_01.translate
                    planes_loc_01.setAttr("visibility", 0)

                    loc_02_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_02))
                    finger[1].getShape().worldSpace[0] >> loc_02_pos.geometryPath
                    loc_02_pos.setAttr("uValue", 0.5)
                    loc_02_pos.allCoordinates >> planes_loc_02.translate
                    planes_loc_02.setAttr("visibility", 0)

                    loc_03_pos = pmc.createNode("motionPath", n="{0}_position_MP".format(planes_loc_03))
                    finger[1].getShape().worldSpace[0] >> loc_03_pos.geometryPath
                    loc_03_pos.setAttr("uValue", 1)
                    loc_03_pos.allCoordinates >> planes_loc_03.translate
                    planes_loc_03.setAttr("visibility", 0)

                plane = pmc.ls(pmc.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0)],
                                                   n="{0}_plane".format(finger[1]), ch=0))[0]

                planes_loc_01.getShape().worldPosition[0] >> plane.getShape().pnts[0]
                planes_loc_02.getShape().worldPosition[0] >> plane.getShape().pnts[1]
                planes_loc_03.getShape().worldPosition[0] >> plane.getShape().pnts[2]

                plane.setAttr("translateX", lock=True, keyable=False, channelBox=False)
                plane.setAttr("translateY", lock=True, keyable=False, channelBox=False)
                plane.setAttr("translateZ", lock=True, keyable=False, channelBox=False)
                plane.setAttr("rotateX", lock=True, keyable=False, channelBox=False)
                plane.setAttr("rotateY", lock=True, keyable=False, channelBox=False)
                plane.setAttr("rotateZ", lock=True, keyable=False, channelBox=False)
                plane.setAttr("scaleX", lock=True, keyable=False, channelBox=False)
                plane.setAttr("scaleY", lock=True, keyable=False, channelBox=False)
                plane.setAttr("scaleZ", lock=True, keyable=False, channelBox=False)
                plane.setAttr("overrideEnabled", 1)
                plane.setAttr("overrideDisplayType", 2)

                finger_group = pmc.group(em=1, n="{0}_plane_GRP".format(finger[1]))
                pmc.parent(planes_loc_01, finger_group)
                pmc.parent(planes_loc_02, finger_group)
                pmc.parent(planes_loc_03, finger_group)
                pmc.parent(plane, finger_group)
                pmc.parent(finger_group, planes_group)

        self.guides_grp = self.group_guides(self.guides)
        pmc.parent(planes_group, self.guides_grp)

        self.roll_prebuild()

        self.view.refresh_view()
        pmc.select(d=1)

    def roll_prebuild(self):
        self.roll_guides_names = ["{0}_ball_GUIDE".format(self.model.module_name),
                                  # "{0}_fingers_roll_GUIDE".format(self.model.module_name),
                                  "{0}_inHand_GUIDE".format(self.model.module_name),
                                  "{0}_ouHhand_GUIDE".format(self.model.module_name)]

        if self.model.roll_creation_switch and self.guide_check(self.roll_guides_names):
            self.roll_guides = pmc.ls(self.roll_guides_names)
            return

        elif self.model.roll_creation_switch:
            ball_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.roll_guides_names[0])
            ball_guide.setAttr("rotateOrder", 2)
            # fingers_roll_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.roll_guides_names[1])
            inhand_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.roll_guides_names[1])
            inhand_guide.setAttr("rotateOrder", 2)
            outhand_guide = pmc.spaceLocator(p=(0, 0, 0), n=self.roll_guides_names[2])
            outhand_guide.setAttr("rotateOrder", 2)

            ball_guide.setAttr("translate", ((1.25 + (0.25 * self.model.how_many_fingers)) * self.side_coef , 0, 0))
            # fingers_roll_guide.setAttr("translate", (12.5 * self.side_coef, 14, 1.75 - (0.25 * self.model.how_many_fingers)))
            inhand_guide.setAttr("translate", (1.5 * self.side_coef, 0, -0.5))
            outhand_guide.setAttr("translate", ((1 + (0.5 * self.model.how_many_fingers)) * self.side_coef, 0, -0.5))

            # self.roll_guides = [ball_guide, fingers_roll_guide, inhand_guide, outhand_guide]
            self.roll_guides = [ball_guide, inhand_guide, outhand_guide]

            roll_group = pmc.group(em=1, n="{0}_roll_guides".format(self.model.module_name))

            for guide in self.roll_guides:
                pmc.parent(guide, roll_group)

            pmc.parent(roll_group, self.guides_grp)

        else:
            if pmc.objExists("{0}_roll_guides".format(self.model.module_name)):
                pmc.delete("{0}_roll_guides".format(self.model.module_name))

    def execute(self):
        self.ik_ctrls = []
        self.ik_setup_chain = []

        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()

        self.get_parent_needed_objects()

        self.create_skn_jnts()
        self.create_fk_ctrls()

        if self.model.ik_creation_switch:
            if self.model.how_many_phalanges == 2:
                self.create_2phalanges_ik(self.created_fk_ctrls)

            elif self.model.how_many_phalanges == 3 and self.model.thumb_creation_switch:
                self.create_2phalanges_ik(self.created_fk_ctrls[:1])
                self.create_3phalanges_ik(self.created_fk_ctrls[1:], 2)

            elif self.model.how_many_phalanges == 3:
                self.create_3phalanges_ik(self.created_fk_ctrls[:], 1)

            elif self.model.thumb_creation_switch:
                self.create_2phalanges_ik(self.created_fk_ctrls[:1])
                self.create_x_phalanges_ik(self.created_fk_ctrls[1:], 2)

            else:
                self.create_x_phalanges_ik(self.created_fk_ctrls[:], 1)

            if self.model.roll_creation_switch:
                self.create_ik_roll()

            if self.model.raz_ik_ctrls:
                for n, finger in enumerate(self.ik_ctrls):
                    rig_lib.raz_one_chain_ik_ctrl_translate_rotate(finger[0])
                    pmc.xform(finger[1], ws=1,
                              translation=(pmc.xform(self.created_fk_ctrls[n][len(self.created_fk_ctrls[n]) / 2],
                                                     q=1, ws=1, translation=1)))

            self.create_ik_local_spaces()

            if self.model.raz_fk_ctrls:
                for n, finger in enumerate(self.created_fk_ctrls):
                    for i, ctrl in enumerate(finger):
                        if i == 0:
                            rig_lib.raz_one_chain_ikfk_fk_ctrl_rotate(ctrl, self.created_skn_jnts[n][i],
                                                                      raz_ctrl_shape_axe="")
                        else:
                            rig_lib.raz_one_chain_ikfk_fk_ctrl_rotate(ctrl, self.created_skn_jnts[n][i],
                                                                      raz_ctrl_shape_axe="z")

        self.create_options_attributes()
        self.clean_rig()
        pmc.select(cl=1)

    def get_parent_needed_objects(self):
        self.parent_ankle_fk_ctrl = pmc.ls("{0}_ankle_fk_CTRL".format(self.model.selected_module))[0]
        self.parent_ankle_ik_ctrl = pmc.ls("{0}_ankle_ik_CTRL".format(self.model.selected_module))[0]
        self.parent_option_ctrl = pmc.ls("{0}_option_CTRL".format(self.model.selected_module))[0]
        try:
            self.parent_ik_handle = pmc.ls("{0}_ik_HDL".format(self.model.selected_module))[0]
        except:
            self.parent_ik_handle = pmc.ls("{0}_all_leg_ik_HDL".format(self.model.selected_module))[0]
        self.parent_ik_length_end_loc = pmc.ls("{0}_ik_length_end_LOC".format(self.model.selected_module))[0]
        if pmc.objExists("{0}_ankle_rotation_ik_HDL".format(self.model.selected_module)):
            self.parent_ankle_rotation_handle = pmc.ls("{0}_ankle_rotation_ik_HDL".format(self.model.selected_module))[0]

    def create_skn_jnts(self):
        duplicate_guides = []
        self.created_skn_jnts = []
        self.jnts_to_skin = []
        # orient_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ankle_LOC".format(self.model.module_name))
        # orient_loc.setAttr("rotateOrder", 4)
        # orient_loc.setAttr("translate", pmc.xform(self.parent_ankle_fk_ctrl, q=1, ws=1, translation=1))
        #
        # if self.model.thumb_creation_switch:
        #     first_finger = self.guides[1]
        # else:
        #     first_finger = self.guides[0]
        # hand_plane = pmc.ls(pmc.polyCreateFacet(p=[(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
        #                                         name="{0}_palm_plane".format(self.model.module_name), ch=0))[0]
        # first_finger_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_temp_first_loc".format(self.model.module_name))
        # last_finger_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_temp_last_loc".format(self.model.module_name))
        # first_finger_loc.setAttr("translate", pmc.xform(first_finger[1].cv[0], q=1, ws=1, translation=1))
        # last_finger_loc.setAttr("translate", pmc.xform(self.guides[-1][1].cv[0], q=1, ws=1, translation=1))
        # first_finger[0].getShape().worldPosition[0] >> hand_plane.getShape().pnts[0]
        # first_finger_loc.getShape().worldPosition[0] >> hand_plane.getShape().pnts[1]
        # last_finger_loc.getShape().worldPosition[0] >> hand_plane.getShape().pnts[2]
        # self.guides[-1][0].getShape().worldPosition[0] >> hand_plane.getShape().pnts[3]
        #
        # mid_finger_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_temp_mid_loc".format(self.model.module_name))
        # mid_finger_loc.setAttr("translate", pmc.xform(self.guides[self.model.how_many_fingers / 2][1].cv[0], q=1, ws=1,
        #                                               translation=1))
        #
        # orient_loc_const = pmc.normalConstraint(hand_plane, orient_loc, aimVector=(-1.0, 0.0, 0.0),
        #                                         upVector=(0.0, 1.0 * self.side_coef, 0.0), worldUpType="object",
        #                                         worldUpObject=mid_finger_loc)
        #
        # pmc.xform(self.parent_ankle_fk_ctrl, ws=1, rotation=(pmc.xform(orient_loc, q=1, ws=1, rotation=1)))
        # pmc.xform(self.parent_ankle_ik_ctrl, ws=1,
        #           rotation=(pmc.xform(pmc.listRelatives(self.parent_ankle_fk_ctrl, children=1, type="transform")[0],
        #                               q=1, ws=1, rotation=1)))

        for n, finger in enumerate(self.guides):
            created_finger_jnts = []
            ankle_guide = pmc.spaceLocator(p=(0, 0, 0), n="{0}_duplicate".format(finger[0]))
            ankle_guide.setAttr("rotateOrder", 4)
            pmc.parent(ankle_guide, finger[0], r=1)
            pmc.parent(ankle_guide, world=1)
            finger_crv_vertex_list = finger[1].cv[:]
            finger_new_guides = [ankle_guide]
            for i, cv in enumerate(finger_crv_vertex_list):
                loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_{1}_duplicate".format(finger[1], i + 1))
                loc.setAttr("translate", (pmc.xform(cv, q=1, ws=1, translation=1)))
                loc.setAttr("rotateOrder", 4)
                finger_new_guides.append(loc)
            duplicate_guides.append(finger_new_guides)

            finger_plane = pmc.polyCreateFacet(p=[pmc.xform(finger_new_guides[1], q=1, ws=1, translation=1),
                                                  pmc.xform(finger_new_guides[2], q=1, ws=1, translation=1),
                                                  pmc.xform(finger_new_guides[3], q=1, ws=1, translation=1)],
                                               n="{0}_temporary_finger{1}_plane".format(self.model.module_name, n),
                                               ch=1)[0]
            finger_plane_face = pmc.ls(finger_plane)[0].f[0]

            for i, guide in enumerate(finger_new_guides):
                if not guide == finger_new_guides[-1]:
                    if i == 0:
                        const = pmc.aimConstraint(finger_new_guides[i + 1], guide,
                                                  aimVector=(0.0, 1.0 * self.side_coef, 0.0),
                                                  upVector=(0.0, 0.0, -1.0), worldUpType="objectrotation",
                                                  worldUpVector=(0.0, 1.0, 0.0),
                                                  worldUpObject=self.parent_ankle_fk_ctrl)
                    else:
                        const = pmc.normalConstraint(finger_plane_face, guide, aimVector=(-1.0, 0.0, 0.0),
                                                     upVector=(0.0, 1.0 * self.side_coef, 0.0), worldUpType="object",
                                                     worldUpObject=finger_new_guides[i + 1])
                    pmc.delete(const)
                    pmc.select(d=1)
                if i != 0:
                    pmc.parent(guide, finger_new_guides[i - 1])
                    pmc.select(created_finger_jnts[i - 1])

                jnt = pmc.joint(p=(pmc.xform(guide, q=1, ws=1, translation=1)),
                                n="{0}_finger{1}_{2}_SKN".format(self.model.module_name, n + 1, i), rad=0.2)
                jnt.setAttr("rotateOrder", 4)

                if i == 0:
                    pmc.parent(jnt, self.jnt_input_grp, r=0)
                    jnt.setAttr("jointOrient", (0, 0, 0))

                if i != len(finger_new_guides) - 1:
                    pmc.xform(jnt, ws=1, rotation=(pmc.xform(guide, q=1, ws=1, rotation=1)))

                created_finger_jnts.append(jnt)

            created_finger_jnts[-1].rename("{0}_finger{1}_end_JNT".format(self.model.module_name, n + 1))
            pmc.delete(finger_plane)

            self.created_skn_jnts.append(created_finger_jnts)
            self.jnts_to_skin.append(created_finger_jnts[:-1])

        pmc.delete(duplicate_guides[:])
        # pmc.delete(orient_loc)
        # pmc.delete(hand_plane)
        # pmc.delete(first_finger_loc)
        # pmc.delete(last_finger_loc)
        # pmc.delete(mid_finger_loc)

    def create_fk_ctrls(self):
        self.created_fk_ctrls = []
        for n, finger in enumerate(self.created_skn_jnts):
            created_finger_ctrls = []
            for i, jnt in enumerate(finger):
                if 1 < i < len(finger) - 1:
                    ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=0.5, d=3, s=8,
                                            n="{0}_finger{1}_{2}_fk_CTRL_shape".format(self.model.module_name,
                                                                                       (n + 1), i), ch=0)[0]
                    ctrl = rig_lib.create_jnttype_ctrl("{0}_finger{1}_{2}_fk_CTRL".format(self.model.module_name,
                                                                                          (n + 1), i), ctrl_shape,
                                                       drawstyle=0, rotateorder=4)
                    ctrl.setAttr("radius", 0)
                    ctrl.setAttr("translate", pmc.xform(jnt, q=1, ws=1, translation=1))
                    pmc.parent(ctrl, created_finger_ctrls[i - 1], r=0)
                    pmc.reorder(ctrl, front=1)

                    ctrl.setAttr("jointOrient", (0, 0, 0))

                    ctrl.setAttr("rotate", pmc.xform(self.created_skn_jnts[n][i], q=1, rotation=1))

                    # ctrl.rotate >> self.created_skn_jnts[n][i].rotate

                    created_finger_ctrls.append(ctrl)

                elif i == 1:
                    ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=0.5, d=3, s=8,
                                            n="{0}_finger{1}_{2}_fk_CTRL_shape".format(self.model.module_name,
                                                                                       (n + 1), i), ch=0)[0]
                    ctrl = rig_lib.create_jnttype_ctrl("{0}_finger{1}_{2}_fk_CTRL".format(self.model.module_name,
                                                                                          (n + 1), i), ctrl_shape,
                                                       drawstyle=0, rotateorder=4)
                    ctrl.setAttr("radius", 0)
                    ctrl.setAttr("translate", pmc.xform(jnt, q=1, ws=1, translation=1))
                    pmc.parent(ctrl, created_finger_ctrls[i - 1], r=0)
                    pmc.reorder(ctrl, front=1)

                    ctrl.setAttr("jointOrient", (0, 0, 0))

                    temp_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_temp_loc".format(self.model.module_name))
                    pmc.parent(temp_loc, self.created_skn_jnts[n][i], r=1)
                    pmc.parent(temp_loc, finger[i-1], r=0)

                    ctrl.setAttr("jointOrient", pmc.xform(temp_loc, q=1, rotation=1))

                    pmc.xform(ctrl, ws=1, rotation=pmc.xform(self.created_skn_jnts[n][i], q=1, ws=1, rotation=1))

                    # if (self.model.thumb_creation_switch and n != 0) or not self.model.thumb_creation_switch:
                    #     jnt_offset = pmc.createNode("plusMinusAverage",
                    #                                 n="{0}_Xoffset_Xctrlvalue_spreadValue_cumul_PMA".format(ctrl))
                    #     jnt_offset.setAttr("operation", 1)
                    #     ctrl.rotateX >> jnt_offset.input1D[0]
                    #     ctrl.jointOrientX >> jnt_offset.input1D[1]
                    #     jnt_offset.output1D >> self.created_skn_jnts[n][i].rotateX
                    #
                    # else:
                    #     ctrl.rotateX >> self.created_skn_jnts[n][i].rotateX
                    #
                    # ctrl.rotateY >> self.created_skn_jnts[n][i].rotateY
                    # ctrl.rotateZ >> self.created_skn_jnts[n][i].rotateZ

                    pmc.delete(temp_loc)

                    created_finger_ctrls.append(ctrl)

                elif i == 0:
                    ctrl_shape = rig_lib.oval_curve_z(
                        "{0}_finger{1}_{2}_fk_CTRL".format(self.model.module_name, (n + 1), i), self.side_coef)
                    ctrl = rig_lib.create_jnttype_ctrl("{0}_finger{1}_{2}_fk_CTRL".format(self.model.module_name,
                                                                                          (n + 1), i), ctrl_shape,
                                                       drawstyle=0, rotateorder=4)
                    ctrl.setAttr("radius", 0)
                    ctrl.setAttr("translate", pmc.xform(jnt, q=1, ws=1, translation=1))
                    pmc.parent(ctrl, self.ctrl_input_grp, r=0)

                    ctrl.setAttr("jointOrient", (0, 0, 0))

                    temp_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_temp_loc".format(self.model.module_name))
                    pmc.parent(temp_loc, self.created_skn_jnts[n][i], r=1)
                    pmc.parent(temp_loc, self.jnt_input_grp, r=0)

                    ctrl.setAttr("jointOrient", pmc.xform(temp_loc, q=1, rotation=1))

                    pmc.xform(ctrl, ws=1, rotation=pmc.xform(self.created_skn_jnts[n][i], q=1, ws=1, rotation=1))

                    # jnt_offset = pmc.createNode("plusMinusAverage", n="{0}_raz_jnt_offset_PMA".format(ctrl))
                    # jnt_offset.setAttr("operation", 1)
                    # ctrl.rotateX >> jnt_offset.input1D[0]
                    # ctrl.jointOrientX >> jnt_offset.input1D[1]
                    # jnt_offset.output1D >> self.created_skn_jnts[n][i].rotateX
                    # ctrl.rotateY >> self.created_skn_jnts[n][i].rotateY
                    # ctrl.rotateZ >> self.created_skn_jnts[n][i].rotateZ

                    pmc.delete(temp_loc)

                    created_finger_ctrls.append(ctrl)

                elif i == len(finger) - 1:
                    pmc.select(d=1)
                    ctrl = pmc.joint(p=(0, 0, 0),
                                     n="{0}_finger{1}_{2}_fk_JNT".format(self.model.module_name, (n + 1), i))
                    ctrl.setAttr("drawStyle", 2)
                    ctrl.setAttr("rotateOrder", 4)
                    ctrl.setAttr("translate", pmc.xform(jnt, q=1, ws=1, translation=1))
                    pmc.parent(ctrl, created_finger_ctrls[i - 1], r=0)
                    ctrl.setAttr("visibility", 0)

                    ctrl.setAttr("jointOrient", (0, 0, 0))

                    ctrl.setAttr("rotate", pmc.xform(self.created_skn_jnts[n][i], q=1, rotation=1))

                    created_finger_ctrls.append(ctrl)

                ctrl.translate >> self.created_skn_jnts[n][i].translate
                ctrl.rotate >> self.created_skn_jnts[n][i].rotate
                ctrl.jointOrient >> self.created_skn_jnts[n][i].jointOrient
                ctrl.scale >> self.created_skn_jnts[n][i].scale

            self.created_fk_ctrls.append(created_finger_ctrls)

    def create_options_attributes(self):
        if self.model.how_many_fingers > 1:
            if "spread" in pmc.listAttr(self.parent_option_ctrl, keyable=1):
                self.parent_option_ctrl.deleteAttr("spread")
            self.parent_option_ctrl.addAttr("spread", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        for n, finger in enumerate(self.created_fk_ctrls):
            if "finger{0}Curl".format(n + 1) in pmc.listAttr(self.parent_option_ctrl, keyable=1):
                self.parent_option_ctrl.deleteAttr("finger{0}Curl".format(n + 1))
            self.parent_option_ctrl.addAttr("finger{0}Curl".format(n + 1), attributeType="float", defaultValue=0,
                                            hidden=0, keyable=1)

            if self.model.how_many_fingers == 2:
                center_finger = 0.5
            else:
                center_finger = int((float(self.model.how_many_fingers - 2) / 2) + 0.5)

            if self.model.thumb_creation_switch:
                center_finger += 1

            if self.model.how_many_fingers > 1 and ((self.model.thumb_creation_switch and n != 0)
                                                    or not self.model.thumb_creation_switch) \
                    and n != center_finger:
                spread_mult = pmc.createNode("multiplyDivide", n="{0}_spread_mult_MDV".format(self.created_fk_ctrls[n][1]))
                spread_mult.setAttr("operation", 1)
                spread_mult.setAttr("input2X", center_finger - n)
                self.parent_option_ctrl.spread >> spread_mult.input1X
                spread_mult.outputX >> finger[1].rotateAxisZ
                finger[1].rotateAxisZ >> self.created_skn_jnts[n][1].rotateAxisZ

            for i, ctrl in enumerate(finger):
                # if self.model.thumb_creation_switch and n == 0:
                #     self.parent_option_ctrl.connectAttr("finger{0}Curl".format(n + 1), ctrl.rotateAxisZ)
                #     ctrl.rotateAxisZ >> self.created_skn_jnts[n][i].rotateAxisZ
                # elif i != 0:
                if i != 0:
                    self.parent_option_ctrl.connectAttr("finger{0}Curl".format(n + 1), ctrl.rotateAxisX)
                    ctrl.rotateAxisX >> self.created_skn_jnts[n][i].rotateAxisX

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)
        self.guides_grp.setAttr("visibility", 0)

        if self.model.side == "Left":
            color_value = 6
        else:
            color_value = 13

        for n, finger in enumerate(self.created_fk_ctrls):
            if self.model.ik_creation_switch:
                invert_value = pmc.createNode("plusMinusAverage",
                                              n="{0}_finger{1}_fk_visibility_MDL".format(self.model.module_name, n + 1))
                invert_value.setAttr("input1D[0]", 1)
                invert_value.setAttr("operation", 2)
                finger[0].fkIk >> invert_value.input1D[1]

                for i, ctrl in enumerate(finger):
                    if i > 0:
                        rig_lib.clean_ctrl(ctrl, color_value, trs="ts", visibility_dependence=invert_value.output1D)
                    else:
                        rig_lib.clean_ctrl(ctrl, color_value, trs="ts")
            else:
                for ctrl in finger:
                    rig_lib.clean_ctrl(ctrl, color_value, trs="ts")

        if self.model.ik_creation_switch:
            for n, finger in enumerate(self.ik_ctrls):
                rig_lib.clean_ctrl(finger[0], color_value, trs="s",
                                   visibility_dependence=self.created_fk_ctrls[n][0].fkIk)
                rig_lib.clean_ctrl(finger[1], color_value, trs="trs")

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

        rig_lib.add_parameter_as_extra_attr(info_crv, "parent_Module", self.model.selected_module)
        rig_lib.add_parameter_as_extra_attr(info_crv, "parent_output", self.model.selected_output)
        rig_lib.add_parameter_as_extra_attr(info_crv, "side", self.model.side)
        rig_lib.add_parameter_as_extra_attr(info_crv, "how_many_fingers", self.model.how_many_fingers)
        rig_lib.add_parameter_as_extra_attr(info_crv, "thumb_creation", self.model.thumb_creation_switch)
        rig_lib.add_parameter_as_extra_attr(info_crv, "how_many_phalanges", self.model.how_many_phalanges)
        rig_lib.add_parameter_as_extra_attr(info_crv, "ik_creation", self.model.ik_creation_switch)
        rig_lib.add_parameter_as_extra_attr(info_crv, "stretch_creation", self.model.stretch_creation_switch)
        rig_lib.add_parameter_as_extra_attr(info_crv, "raz_ik_ctrls", self.model.raz_ik_ctrls)
        rig_lib.add_parameter_as_extra_attr(info_crv, "raz_fk_ctrls", self.model.raz_fk_ctrls)
        rig_lib.add_parameter_as_extra_attr(info_crv, "roll_creation", self.model.roll_creation_switch)

        if not pmc.objExists("jnts_to_SKN_SET"):
            skn_set = pmc.createNode("objectSet", n="jnts_to_SKN_SET")
        else:
            skn_set = pmc.ls("jnts_to_SKN_SET", type="objectSet")[0]
        for jnt in self.jnts_to_skin:
            if type(jnt) == list:
                for obj in jnt:
                    skn_set.add(obj)
            else:
                skn_set.add(jnt)

    def create_3phalanges_ik(self, fk_ctrls, x):
        for n, finger in enumerate(fk_ctrls):
            metacarpus_fk_ctrl_value = pmc.xform(finger[0], q=1, rotation=1)
            finger_fk_ctrl_01_value = pmc.xform(finger[1], q=1, rotation=1)
            finger_fk_ctrl_02_value = pmc.xform(finger[2], q=1, rotation=1)
            finger_fk_ctrl_03_value = pmc.xform(finger[3], q=1, rotation=1)
            finger_fk_ctrl_04_value = pmc.xform(finger[4], q=1, rotation=1)

            metacarpus_ik_setup_jnt = finger[0].duplicate(n="{0}_finger{1}_0_ik_setup_JNT".format(
                self.model.module_name, (n + x)))[0]
            first_phalanx_ik_setup_jnt = pmc.ls("{0}_finger{1}_0_ik_setup_JNT|{0}_finger{1}_1_fk_CTRL".format(
                self.model.module_name, (n + x)))[0]
            second_phalanx_ik_setup_jnt = \
            pmc.ls("{0}_finger{1}_0_ik_setup_JNT|{0}_finger{1}_1_fk_CTRL|{0}_finger{1}_2_fk_CTRL".format(
                self.model.module_name, (n + x)))[0]
            third_phalanx_ik_setup_jnt = pmc.ls(
                "{0}_finger{1}_0_ik_setup_JNT|{0}_finger{1}_1_fk_CTRL|{0}_finger{1}_2_fk_CTRL|{0}_finger{1}_3_fk_CTRL".format(
                    self.model.module_name, (n + x)))[0]
            end_ik_setup_jnt = pmc.ls(
                "{0}_finger{1}_0_ik_setup_JNT|{0}_finger{1}_1_fk_CTRL|{0}_finger{1}_2_fk_CTRL|{0}_finger{1}_3_fk_CTRL|{0}_finger{1}_4_fk_JNT".format(
                    self.model.module_name, (n + x)))[0]

            first_phalanx_ik_setup_jnt.rename("{0}_finger{1}_1_ik_setup_JNT".format(self.model.module_name, (n + x)))
            second_phalanx_ik_setup_jnt.rename("{0}_finger{1}_2_ik_setup_JNT".format(self.model.module_name, (n + x)))
            third_phalanx_ik_setup_jnt.rename("{0}_finger{1}_3_ik_setup_JNT".format(self.model.module_name, (n + x)))
            end_ik_setup_jnt.rename("{0}_finger{1}_4_ik_setup_JNT".format(self.model.module_name, (n + x)))

            ik_setup_chain = [metacarpus_ik_setup_jnt, first_phalanx_ik_setup_jnt,
                              second_phalanx_ik_setup_jnt, third_phalanx_ik_setup_jnt, end_ik_setup_jnt]

            self.ik_setup_chain.append(ik_setup_chain)

            for jnt in ik_setup_chain:
                if jnt != ik_setup_chain[-1]:
                    pmc.delete(jnt.getShape())
                jnt.setAttr("radius", 0.1)

            metacarpus_ik_setup_jnt.setAttr("visibility", 0)

            global_ik_handle = pmc.ikHandle(n=("{0}_finger{1}_finger_ik_HDL".format(self.model.module_name, (n + x))),
                                            startJoint=first_phalanx_ik_setup_jnt, endEffector=end_ik_setup_jnt,
                                            solver="ikRPsolver")[0]
            global_ik_effector = pmc.listRelatives(third_phalanx_ik_setup_jnt, children=1)[-1]
            global_ik_effector.rename("{0}_finger{1}_finger_ik_EFF".format(self.model.module_name, (n + x)))
            global_ik_handle.setAttr("snapEnable", 0)

            start_ik_handle = pmc.ikHandle(n=("{0}_finger{1}_first_part_ik_HDL".format(self.model.module_name, (n + x))),
                                           startJoint=finger[1], endEffector=finger[3], solver="ikRPsolver")[0]
            start_ik_effector = pmc.listRelatives(finger[2], children=1)[-1]
            start_ik_effector.rename("{0}_finger{1}_first_part_ik_EFF".format(self.model.module_name, (n + x)))
            start_ik_handle.setAttr("snapEnable", 0)
            start_ik_handle.setAttr("ikBlend", 0)

            end_ik_handle = pmc.ikHandle(n=("{0}_finger{1}_end_ik_HDL".format(self.model.module_name, (n + x))),
                                         startJoint=finger[3], endEffector=finger[4], solver="ikSCsolver")[0]
            end_ik_effector = pmc.listRelatives(finger[3], children=1)[-1]
            end_ik_effector.rename("{0}_finger{1}_end_ik_EFF".format(self.model.module_name, (n + x)))
            end_ik_handle.setAttr("snapEnable", 0)
            end_ik_handle.setAttr("ikBlend", 0)

            pmc.xform(start_ik_handle, ws=1, translation=pmc.xform(third_phalanx_ik_setup_jnt, q=1, ws=1, translation=1))
            pmc.xform(end_ik_handle, ws=1, translation=pmc.xform(end_ik_setup_jnt, q=1, ws=1, translation=1))

            pmc.parent(start_ik_handle, end_ik_setup_jnt)
            pmc.parent(end_ik_handle, third_phalanx_ik_setup_jnt)

            ik_shape = rig_lib.medium_cube("{0}__finger{1}_ik_CTRL_shape".format(self.model.module_name, (n + x)))
            ik_ctrl = rig_lib.create_jnttype_ctrl("{0}_finger{1}_ik_CTRL".format(self.model.module_name, (n + x)),
                                                  ik_shape, drawstyle=2, rotateorder=2)
            pmc.select(d=1)
            ik_ctrl_ofs = pmc.joint(p=(0, 0, 0), n="{0}_finger{1}_ik_ctrl_OFS".format(self.model.module_name, (n + x)))
            ik_ctrl_ofs.setAttr("rotateOrder", 2)
            ik_ctrl_ofs.setAttr("drawStyle", 2)
            pmc.parent(ik_ctrl, ik_ctrl_ofs)

            finger[0].setAttr("rotate", (0, 0, 0))
            finger[1].setAttr("rotate", (0, 0, 0))
            finger[2].setAttr("rotate", (0, 0, 0))
            finger[3].setAttr("rotate", (0, 0, 0))
            finger[4].setAttr("rotate", (0, 0, 0))

            ik_ctrl_ofs.setAttr("translate", pmc.xform(finger[-1], q=1, ws=1, translation=1))
            pmc.parent(global_ik_handle, ik_ctrl_ofs, r=0)
            ik_ctrl.setAttr("translate", pmc.xform(global_ik_handle, q=1, translation=1))
            pmc.parent(global_ik_handle, ik_ctrl, r=0)

            pmc.parent(ik_ctrl_ofs, self.ctrl_input_grp)

            ik_ctrl.setAttr("translate", (0, 0, 0))

            pmc.select(finger[-1])
            fk_rotation_jnt = pmc.joint(p=(0, 0, 0), n="{0}_finger{1}_fk_end_JNT".format(self.model.module_name, (n + x)))
            fk_rotation_jnt.setAttr("translate", (0, self.side_coef, 0))
            fk_rotation_jnt.setAttr("rotate", (0, 0, 0))
            fk_rotation_jnt.setAttr("jointOrient", (0, 0, 0))

            fk_rotation_hdl = pmc.ikHandle(n="{0}_finger{1}_end_rotation_ik_HDL".format(self.model.module_name, (n + x)),
                                           startJoint=finger[-1], endEffector=fk_rotation_jnt, solver="ikSCsolver")[0]
            fk_rotation_effector = pmc.listRelatives(finger[-1], children=1)[-1]
            fk_rotation_effector.rename("{0}_finger{1}_end_rotation_ik_EFF".format(self.model.module_name, (n + x)))
            fk_rotation_hdl.setAttr("snapEnable", 0)
            fk_rotation_hdl.setAttr("ikBlend", 0)
            pmc.parent(fk_rotation_hdl, ik_ctrl, r=0)

            finger[0].addAttr("fkIk", attributeType="float", defaultValue=0, hidden=0, keyable=1, hasMaxValue=1,
                              hasMinValue=1, maxValue=1, minValue=0)

            finger[0].fkIk >> fk_rotation_hdl.ikBlend

            fk_rotation_hdl.setAttr("visibility", 0)
            fk_rotation_jnt.setAttr("visibility", 0)

            auto_pole_vector_shape = rig_lib.jnt_shape_curve("{0}_finger{1}_auto_poleVector_CTRL_shape".format(
                self.model.module_name, (n + x)))
            auto_pole_vector = rig_lib.create_jnttype_ctrl("{0}_finger{1}_auto_poleVector_CTRL".format(
                self.model.module_name, (n + x)), auto_pole_vector_shape, drawstyle=2)
            auto_pv_ofs = pmc.group(auto_pole_vector, n="{0}_finger{1}_auto_poleVector_ctrl_OFS".format(
                self.model.module_name, (n + x)))
            auto_pv_ofs.setAttr("translate", (pmc.xform(finger[1], q=1, ws=1, translation=1)[0],
                                              pmc.xform(finger[1], q=1, ws=1, translation=1)[1],
                                              pmc.xform(finger[1], q=1, ws=1, translation=1)[2]))

            pmc.parent(auto_pv_ofs, self.ctrl_input_grp, r=0)
            auto_pv_ofs.setAttr("visibility", 0)

            pmc.poleVectorConstraint(auto_pole_vector, global_ik_handle)

            start_handle_pole_vector_shape = rig_lib.jnt_shape_curve(
                "{0}_finger{1}_start_handle_poleVector_CTRL_shape".format(
                    self.model.module_name, (n + x)))
            start_handle_pole_vector = rig_lib.create_jnttype_ctrl("{0}_finger{1}_start_handle_poleVector_CTRL".format(
                self.model.module_name, (n + x)), start_handle_pole_vector_shape, drawstyle=2)
            start_handle_pv_ofs = pmc.group(start_handle_pole_vector,
                                            n="{0}_finger{1}_start_handle_poleVector_ctrl_OFS".format(
                                                self.model.module_name, (n + x)))

            pmc.parent(start_handle_pv_ofs, second_phalanx_ik_setup_jnt, r=1)
            auto_pv_ofs.setAttr("visibility", 0)

            pmc.poleVectorConstraint(start_handle_pole_vector, start_ik_handle)

            second_phalanx_ik_setup_jnt.setAttr("preferredAngleX", finger_fk_ctrl_02_value[0])
            third_phalanx_ik_setup_jnt.setAttr("preferredAngleX", finger_fk_ctrl_03_value[0])
            finger[2].setAttr("preferredAngleX", finger_fk_ctrl_02_value[0])
            finger[3].setAttr("preferredAngleX", finger_fk_ctrl_03_value[0])

            pmc.pointConstraint(finger[1], auto_pv_ofs, maintainOffset=1)

            ik_ctrl.addAttr("fingerTwist", attributeType="float", defaultValue=0, hidden=0, keyable=1)
            pmc.aimConstraint(global_ik_handle, auto_pv_ofs,
                              maintainOffset=0, aimVector=(self.side_coef, 0.0, 0.0),
                              upVector=(0.0, 0.0, 1.0), worldUpType="objectrotation",
                              worldUpVector=(1.0, 0.0, 0.0), worldUpObject=ik_ctrl)

            ik_ctrl.fingerTwist >> global_ik_handle.twist

            start_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_finger{1}_ik_length_start_LOC".format(
                self.model.module_name, (n + x)))
            end_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_finger{1}_ik_length_end_LOC".format(
                self.model.module_name, (n + x)))
            pmc.parent(start_loc, finger[1], r=1)
            pmc.parent(start_loc, finger[0], r=0)
            pmc.parent(end_loc, ik_ctrl, r=1)
            start_loc.setAttr("visibility", 0)
            end_loc.setAttr("visibility", 0)

            length_measure = pmc.createNode("distanceDimShape",
                                            n="{0}_finger{1}_ik_length_measure_DDMShape".format(
                                                self.model.module_name, (n + x)))
            length_measure.getParent().rename("{0}_finger{1}_ik_length_measure_DDM".format(
                self.model.module_name, (n + x)))
            pmc.parent(length_measure.getParent(), self.parts_grp, r=0)
            start_loc.getShape().worldPosition[0] >> length_measure.startPoint
            end_loc.getShape().worldPosition[0] >> length_measure.endPoint

            ik_global_scale = pmc.createNode("multiplyDivide", n="{0}_finger{1}_ik_global_scale_MDV".format(
                self.model.module_name, (n + x)))
            ik_stretch_value = pmc.createNode("multiplyDivide", n="{0}_finger{1}_ik_stretch_value_MDV".format(
                self.model.module_name, (n + x)))
            global_scale = pmc.ls(regex=".*_global_mult_local_scale_MDL$")[0]
            base_length = pmc.createNode("plusMinusAverage", n="{0}_finger{1}_ik_base_length_PMA".format(
                self.model.module_name, (n + x)))

            ik_global_scale.setAttr("operation", 2)
            length_measure.distance >> ik_global_scale.input1X
            global_scale.output >> ik_global_scale.input2X
            ik_stretch_value.setAttr("operation", 2)
            base_length.output1D >> ik_stretch_value.input2X
            ik_global_scale.outputX >> ik_stretch_value.input1X

            for i, ctrl in enumerate(finger[1:]):
                if i < (len(finger) - 2):
                    ctrl.addAttr("baseLength", attributeType="float",
                                 defaultValue=pmc.xform(finger[i + 2], q=1, translation=1)[1] * self.side_coef,
                                 hidden=0, keyable=0)
                    ctrl.setAttr("baseLength", lock=1, channelBox=0)
                    if self.model.stretch_creation_switch:
                        ctrl.addAttr("stretch", attributeType="float", defaultValue=1, hidden=0, keyable=1,
                                     hasMinValue=1, minValue=0)
                        jnt_length = pmc.createNode("multiplyDivide",
                                                    n="{0}_finger{1}_jnt_{2}_length_MDV".format(self.model.module_name,
                                                                                                (n + x), i))
                        ctrl.baseLength >> jnt_length.input1Y
                        ctrl.stretch >> jnt_length.input2Y
                        jnt_length.outputY >> base_length.input1D[i]
                    else:
                        ctrl.baseLength >> base_length.input1D[i]

            ik_ctrl.addAttr("lastPhalanxBend", attributeType="float", defaultValue=0, hidden=0, keyable=1)
            ik_ctrl.addAttr("lastPhalanxBend_decrease_range_start", attributeType="float", defaultValue=0.8, hidden=0,
                            keyable=0, readable=1, writable=1, hasMinValue=1, minValue=0, hasMaxValue=1, maxValue=1)
            last_phalanx_bend_decrease_range = pmc.createNode("clamp",
                                                              n="{0}_finger{1}_bend_decrease_range_CLAMP".format(
                                                                  self.model.module_name, (n + x)))
            last_phalanx_bend_decrease_percent = pmc.createNode("setRange",
                                                                n="{0}_finger{1}_bend_decrease_percent_RANGE".format(
                                                                    self.model.module_name, (n + x)))
            last_phalanx_bend_decrease_percent_invert = pmc.createNode("plusMinusAverage",
                                                                       n="{0}_finger{1}_bend_decrease_percent_invert_PMA".format(
                                                                           self.model.module_name, (n + x)))
            last_phalanx_bend_value = pmc.createNode("multDoubleLinear",
                                                     n="{0}_finger{1}_bend_decrease_percent_invert_MDL".format(
                                                         self.model.module_name, (n + x)))

            ik_ctrl.lastPhalanxBend_decrease_range_start >> last_phalanx_bend_decrease_range.minR
            last_phalanx_bend_decrease_range.setAttr("maxR", 1)
            ik_stretch_value.outputX >> last_phalanx_bend_decrease_range.inputR
            last_phalanx_bend_decrease_percent.setAttr("minX", 0)
            last_phalanx_bend_decrease_percent.setAttr("maxX", 1)
            ik_ctrl.lastPhalanxBend_decrease_range_start >> last_phalanx_bend_decrease_percent.oldMinX
            last_phalanx_bend_decrease_percent.setAttr("oldMaxX", 1)
            last_phalanx_bend_decrease_range.outputR >> last_phalanx_bend_decrease_percent.valueX
            last_phalanx_bend_decrease_percent_invert.setAttr("operation", 2)
            last_phalanx_bend_decrease_percent_invert.setAttr("input1D[0]", 1)
            last_phalanx_bend_decrease_percent.outValueX >> last_phalanx_bend_decrease_percent_invert.input1D[1]
            ik_ctrl.lastPhalanxBend >> last_phalanx_bend_value.input1
            last_phalanx_bend_decrease_percent_invert.output1D >> last_phalanx_bend_value.input2
            last_phalanx_bend_value.output >> end_ik_setup_jnt.rotateX

            created_ik_ctrls = [ik_ctrl, auto_pole_vector]

            finger[0].translate >> metacarpus_ik_setup_jnt.translate
            finger[0].jointOrient >> metacarpus_ik_setup_jnt.jointOrient
            finger[0].rotate >> metacarpus_ik_setup_jnt.rotate
            finger[0].scale >> metacarpus_ik_setup_jnt.scale

            finger[0].setAttr("rotate", metacarpus_fk_ctrl_value)
            finger[1].setAttr("rotate", finger_fk_ctrl_01_value)
            finger[2].setAttr("rotate", finger_fk_ctrl_02_value)
            finger[3].setAttr("rotate", finger_fk_ctrl_03_value)
            finger[4].setAttr("rotate", finger_fk_ctrl_04_value)

            global_ik_handle.setAttr("visibility", 0)

            finger_end_fk_pos_reader = pmc.spaceLocator(p=(0, 0, 0),
                                                        n="{0}_finger{1}_fk_pos_reader_LOC".format(
                                                            self.model.module_name, (n + x)))
            finger_end_fk_pos_reader.setAttr("rotateOrder", 2)
            finger_end_fk_pos_reader.setAttr("visibility", 0)
            pmc.parent(finger_end_fk_pos_reader, finger[-1], r=1)
            finger_end_fk_pos_reader.setAttr("rotate", (-90 * self.side_coef, -90 * (1 - self.side_coef), 90 * (1 + self.side_coef)))
            rig_lib.clean_ctrl(finger_end_fk_pos_reader, 0, trs="trs")

            pmc.xform(ik_ctrl, ws=1, translation=(pmc.xform(finger[-1], q=1, ws=1, translation=1)))
            pmc.xform(ik_ctrl, ws=1, rotation=(pmc.xform(finger_end_fk_pos_reader, q=1, ws=1, rotation=1)))

            pmc.xform(auto_pole_vector, ws=1,
                      translation=(pmc.xform(finger[2], q=1, ws=1, translation=1)[0],
                                   pmc.xform(finger[2], q=1, ws=1, translation=1)[1],
                                   pmc.xform(finger[2], q=1, ws=1, translation=1)[2]))

            finger[0].fkIk >> start_ik_handle.ikBlend
            finger[0].fkIk >> end_ik_handle.ikBlend

            finger[0].setAttr("fkIk", 1)
            pmc.move(ik_ctrl, [0.1, 0, 0], relative=1)
            pmc.refresh()
            pmc.move(ik_ctrl, [-0.1, 0, 0], relative=1)
            pmc.refresh()
            finger[0].setAttr("fkIk", 0)

            self.ik_ctrls.append(created_ik_ctrls)

            if self.model.stretch_creation_switch:
                self.connect_quadruped_one_chain_fk_ik_stretch(finger[1:], created_ik_ctrls[0], finger[0],
                                                               ik_setup_chain[1:], self.created_skn_jnts[n + x - 1][1:],
                                                               self.side_coef,
                                                               name="{0}_finger{1}".format(self.model.module_name, n + x),
                                                               finger=1)

    def create_2phalanges_ik(self, fk_ctrls):
        for n, finger in enumerate(fk_ctrls):
            metacarpus_fk_ctrl_value = pmc.xform(finger[0], q=1, rotation=1)
            finger_fk_ctrl_01_value = pmc.xform(finger[1], q=1, rotation=1)
            finger_fk_ctrl_02_value = pmc.xform(finger[2], q=1, rotation=1)
            finger_fk_ctrl_03_value = pmc.xform(finger[3], q=1, rotation=1)

            ik_handle = pmc.ikHandle(n=("{0}_finger{1}_ik_HDL".format(self.model.module_name, n + 1)),
                                     startJoint=finger[1], endEffector=finger[-1], solver="ikRPsolver")[0]
            ik_effector = pmc.listRelatives(finger[-2], children=1)[-1]
            ik_effector.rename("{0}_finger{1}_ik_EFF".format(self.model.module_name, n + 1))
            ik_handle.setAttr("snapEnable", 0)
            ik_handle.setAttr("ikBlend", 0)

            ik_shape = rig_lib.medium_cube("{0}_finger{1}_ik_CTRL_shape".format(self.model.module_name, n + 1))
            ik_ctrl = rig_lib.create_jnttype_ctrl("{0}_finger{1}_ik_CTRL".format(self.model.module_name, n + 1), ik_shape,
                                                  drawstyle=2, rotateorder=2)
            pmc.select(d=1)
            ik_ctrl_ofs = pmc.joint(p=(0, 0, 0), n="{0}_finger{1}_ik_ctrl_OFS".format(self.model.module_name, n + 1))
            ik_ctrl_ofs.setAttr("rotateOrder", 2)
            ik_ctrl_ofs.setAttr("drawStyle", 2)
            pmc.parent(ik_ctrl, ik_ctrl_ofs)

            finger[0].setAttr("rotate", (0, 0, 0))
            finger[1].setAttr("rotate", (0, 0, 0))
            finger[2].setAttr("rotate", (0, 0, 0))
            finger[3].setAttr("rotate", (0, 0, 0))

            ik_ctrl_ofs.setAttr("translate", pmc.xform(finger[-1], q=1, ws=1, translation=1))
            pmc.parent(ik_handle, ik_ctrl_ofs, r=0)
            ik_ctrl.setAttr("translate", pmc.xform(ik_handle, q=1, translation=1))
            pmc.parent(ik_handle, ik_ctrl, r=0)
            pmc.parent(ik_ctrl_ofs, self.ctrl_input_grp)

            ik_ctrl.setAttr("translate", (0, 0, 0))

            pmc.select(finger[-1])
            fk_rotation_jnt = pmc.joint(p=(0, 0, 0), n="{0}_finger{1}_fk_end_JNT".format(self.model.module_name, n + 1))
            fk_rotation_jnt.setAttr("translate", (0, self.side_coef, 0))
            fk_rotation_jnt.setAttr("rotate", (0, 0, 0))
            fk_rotation_jnt.setAttr("jointOrient", (0, 0, 0))

            fk_rotation_hdl = pmc.ikHandle(n="{0}_finger{1}_rotation_ik_HDL".format(self.model.module_name, n + 1),
                                           startJoint=finger[-1], endEffector=fk_rotation_jnt, solver="ikRPsolver")[0]
            fk_rotation_effector = pmc.listRelatives(finger[-1], children=1)[-1]
            fk_rotation_effector.rename("{0}_finger{1}_rotation_ik_EFF".format(self.model.module_name, n + 1))
            fk_rotation_hdl.setAttr("snapEnable", 0)
            fk_rotation_hdl.setAttr("ikBlend", 0)
            # fk_rotation_hdl.setAttr("poleVector", (-1, 0, 0))
            pmc.parent(fk_rotation_hdl, ik_ctrl, r=0)

            finger[0].addAttr("fkIk", attributeType="float", defaultValue=0, hidden=0, keyable=1, hasMaxValue=1,
                              hasMinValue=1, maxValue=1, minValue=0)

            finger[0].fkIk >> fk_rotation_hdl.ikBlend

            fk_rotation_hdl.setAttr("visibility", 0)
            fk_rotation_jnt.setAttr("visibility", 0)

            pole_vector_shape = rig_lib.jnt_shape_curve("{0}_finger{1}_poleVector_CTRL_shape".format(
                self.model.module_name, n + 1))
            pole_vector = rig_lib.create_jnttype_ctrl("{0}_finger{1}_poleVector_CTRL".format(self.model.module_name, n + 1),
                                                      pole_vector_shape, drawstyle=2)
            pv_ofs = pmc.group(pole_vector, n="{0}_finger{1}_poleVector_ctrl_OFS".format(self.model.module_name, n + 1))
            pv_ofs.setAttr("translate", (pmc.xform(finger[1], q=1, ws=1, translation=1)[0],
                                         pmc.xform(finger[1], q=1, ws=1, translation=1)[1],
                                         pmc.xform(finger[1], q=1, ws=1, translation=1)[2]))

            pmc.parent(pv_ofs, self.ctrl_input_grp, r=0)
            pv_ofs.setAttr("visibility", 0)

            pmc.poleVectorConstraint(pole_vector, ik_handle)

            finger[2].setAttr("preferredAngleX", -90)

            pmc.pointConstraint(finger[1], pv_ofs, maintainOffset=1)

            ik_ctrl.addAttr("fingerTwist", attributeType="float", defaultValue=0, hidden=0, keyable=1)
            pmc.aimConstraint(ik_handle, pv_ofs, maintainOffset=0, aimVector=(self.side_coef, 0.0, 0.0),
                              upVector=(0.0, 0.0, 1.0), worldUpType="objectrotation",
                              worldUpVector=(1.0, 0.0, 0.0), worldUpObject=ik_ctrl)

            ik_ctrl.fingerTwist >> ik_handle.twist

            created_ik_ctrls = [ik_ctrl, pole_vector]

            finger[0].setAttr("rotate", metacarpus_fk_ctrl_value)
            finger[1].setAttr("rotate", finger_fk_ctrl_01_value)
            finger[2].setAttr("rotate", finger_fk_ctrl_02_value)
            finger[3].setAttr("rotate", finger_fk_ctrl_03_value)

            ik_handle.setAttr("visibility", 0)

            finger_end_fk_pos_reader = pmc.spaceLocator(p=(0, 0, 0),
                                                        n="{0}_finger{1}_fk_pos_reader_LOC".format(self.model.module_name,
                                                                                                   n + 1))
            finger_end_fk_pos_reader.setAttr("rotateOrder", 2)
            finger_end_fk_pos_reader.setAttr("visibility", 0)
            pmc.parent(finger_end_fk_pos_reader, finger[-1], r=1)
            finger_end_fk_pos_reader.setAttr("rotate", (-90 * self.side_coef, -90 * (1 - self.side_coef), 90 * (1 + self.side_coef)))
            rig_lib.clean_ctrl(finger_end_fk_pos_reader, 0, trs="trs")

            pmc.xform(ik_ctrl, ws=1, translation=(pmc.xform(finger[-1], q=1, ws=1, translation=1)))
            pmc.xform(ik_ctrl, ws=1, rotation=(pmc.xform(finger_end_fk_pos_reader, q=1, ws=1, rotation=1)))

            pmc.xform(pole_vector, ws=1, translation=(pmc.xform(finger[2], q=1, ws=1, translation=1)[0],
                                                      pmc.xform(finger[2], q=1, ws=1, translation=1)[1],
                                                      pmc.xform(finger[2], q=1, ws=1, translation=1)[2]))

            finger[0].fkIk >> ik_handle.ikBlend

            finger[0].setAttr("fkIk", 1)
            pmc.move(ik_ctrl, [0.1, 0, 0], relative=1)
            pmc.refresh()
            pmc.move(ik_ctrl, [-0.1, 0, 0], relative=1)
            pmc.refresh()
            finger[0].setAttr("fkIk", 0)

            self.ik_ctrls.append(created_ik_ctrls)

            if self.model.stretch_creation_switch:
                self.connect_one_chain_fk_ik_stretch(finger[1:], created_ik_ctrls[0], finger[0],
                                                     self.created_skn_jnts[n][1:],
                                                     name="{0}_finger{1}".format(self.model.module_name, n + 1), finger=1)

    def create_x_phalanges_ik(self, fk_ctrls, x):
        for n, finger in enumerate(fk_ctrls):
            finger_fk_ctrl_values = []
            for phalanx in finger:
                finger_fk_ctrl_values.append(pmc.xform(phalanx, q=1, rotation=1))

            ik_handle = pmc.ikHandle(n=("{0}_finger{1}_ik_HDL".format(self.model.module_name, n + x)),
                                     startJoint=finger[1], endEffector=finger[-1], solver="ikRPsolver")[0]
            ik_effector = pmc.listRelatives(finger[-2], children=1)[-1]
            ik_effector.rename("{0}_finger{1}_ik_EFF".format(self.model.module_name, n + x))
            ik_handle.setAttr("snapEnable", 0)
            ik_handle.setAttr("ikBlend", 0)

            ik_shape = rig_lib.medium_cube("{0}_finger{1}_ik_CTRL_shape".format(self.model.module_name, n + x))
            ik_ctrl = rig_lib.create_jnttype_ctrl("{0}_finger{1}_ik_CTRL".format(self.model.module_name, n + x),
                                                  ik_shape,
                                                  drawstyle=2, rotateorder=2)
            pmc.select(d=1)
            ik_ctrl_ofs = pmc.joint(p=(0, 0, 0), n="{0}_finger{1}_ik_ctrl_OFS".format(self.model.module_name, n + x))
            ik_ctrl_ofs.setAttr("rotateOrder", 2)
            ik_ctrl_ofs.setAttr("drawStyle", 2)
            pmc.parent(ik_ctrl, ik_ctrl_ofs)

            for phalanx in finger:
                phalanx.setAttr("rotate", (0, 0, 0))

            ik_ctrl_ofs.setAttr("translate", pmc.xform(finger[-1], q=1, ws=1, translation=1))
            pmc.parent(ik_handle, ik_ctrl_ofs, r=0)
            ik_ctrl.setAttr("translate", pmc.xform(ik_handle, q=1, translation=1))
            pmc.parent(ik_handle, ik_ctrl, r=0)
            pmc.parent(ik_ctrl_ofs, self.ctrl_input_grp)

            ik_ctrl.setAttr("translate", (0, 0, 0))

            pmc.select(finger[-1])
            fk_rotation_jnt = pmc.joint(p=(0, 0, 0), n="{0}_finger{1}_fk_end_JNT".format(self.model.module_name, n + x))
            fk_rotation_jnt.setAttr("translate", (0, self.side_coef, 0))
            fk_rotation_jnt.setAttr("rotate", (0, 0, 0))
            fk_rotation_jnt.setAttr("jointOrient", (0, 0, 0))

            fk_rotation_hdl = pmc.ikHandle(n="{0}_finger{1}_rotation_ik_HDL".format(self.model.module_name, n + x),
                                           startJoint=finger[-1], endEffector=fk_rotation_jnt, solver="ikRPsolver")[0]
            fk_rotation_effector = pmc.listRelatives(finger[-1], children=1)[-1]
            fk_rotation_effector.rename("{0}_finger{1}_rotation_ik_EFF".format(self.model.module_name, n + x))
            fk_rotation_hdl.setAttr("snapEnable", 0)
            fk_rotation_hdl.setAttr("ikBlend", 0)
            # fk_rotation_hdl.setAttr("poleVector", (-1, 0, 0))
            pmc.parent(fk_rotation_hdl, ik_ctrl, r=0)

            finger[0].addAttr("fkIk", attributeType="float", defaultValue=0, hidden=0, keyable=1, hasMaxValue=1,
                              hasMinValue=1, maxValue=1, minValue=0)

            finger[0].fkIk >> fk_rotation_hdl.ikBlend

            fk_rotation_hdl.setAttr("visibility", 0)
            fk_rotation_jnt.setAttr("visibility", 0)

            pole_vector_shape = rig_lib.jnt_shape_curve("{0}_finger{1}_poleVector_CTRL_shape".format(
                self.model.module_name, n + x))
            pole_vector = rig_lib.create_jnttype_ctrl(
                "{0}_finger{1}_poleVector_CTRL".format(self.model.module_name, n + x),
                pole_vector_shape, drawstyle=2)
            pv_ofs = pmc.group(pole_vector, n="{0}_finger{1}_poleVector_ctrl_OFS".format(self.model.module_name, n + x))
            pv_ofs.setAttr("translate", (pmc.xform(finger[1], q=1, ws=1, translation=1)[0],
                                         pmc.xform(finger[1], q=1, ws=1, translation=1)[1],
                                         pmc.xform(finger[1], q=1, ws=1, translation=1)[2]))

            pmc.parent(pv_ofs, self.ctrl_input_grp, r=0)
            pv_ofs.setAttr("visibility", 0)

            pmc.poleVectorConstraint(pole_vector, ik_handle)

            for i, phalanx in enumerate(finger):
                if 1 < i < len(finger) - 1:
                    phalanx.setAttr("preferredAngleX", finger_fk_ctrl_values[i][1])

            pmc.pointConstraint(finger[1], pv_ofs, maintainOffset=1)

            ik_ctrl.addAttr("fingerTwist", attributeType="float", defaultValue=0, hidden=0, keyable=1)
            pmc.aimConstraint(ik_handle, pv_ofs, maintainOffset=0, aimVector=(self.side_coef, 0.0, 0.0),
                              upVector=(0.0, 0.0, 1.0), worldUpType="objectrotation",
                              worldUpVector=(0.0, 0.0, 1.0), worldUpObject=ik_ctrl)

            ik_ctrl.fingerTwist >> ik_handle.twist

            created_ik_ctrls = [ik_ctrl, pole_vector]

            for i, phalanx in enumerate(finger):
                phalanx.setAttr("rotate", finger_fk_ctrl_values[i])

            ik_handle.setAttr("visibility", 0)

            finger_end_fk_pos_reader = pmc.spaceLocator(p=(0, 0, 0),
                                                        n="{0}_finger{1}_fk_pos_reader_LOC".format(
                                                            self.model.module_name, n + x))
            finger_end_fk_pos_reader.setAttr("rotateOrder", 2)
            finger_end_fk_pos_reader.setAttr("visibility", 0)
            pmc.parent(finger_end_fk_pos_reader, finger[-1], r=1)
            finger_end_fk_pos_reader.setAttr("rotate", (-90 * self.side_coef, -90 * (1 - self.side_coef), 90 * (1 + self.side_coef)))
            rig_lib.clean_ctrl(finger_end_fk_pos_reader, 0, trs="trs")

            pmc.xform(ik_ctrl, ws=1, translation=(pmc.xform(finger[-1], q=1, ws=1, translation=1)))
            pmc.xform(ik_ctrl, ws=1, rotation=(pmc.xform(finger_end_fk_pos_reader, q=1, ws=1, rotation=1)))

            pmc.xform(pole_vector, ws=1, translation=(pmc.xform(finger[len(finger) / 2], q=1, ws=1, translation=1)[0],
                                                      pmc.xform(finger[len(finger) / 2], q=1, ws=1, translation=1)[1],
                                                      pmc.xform(finger[len(finger) / 2], q=1, ws=1, translation=1)[2]))

            finger[0].fkIk >> ik_handle.ikBlend

            finger[0].setAttr("fkIk", 1)
            pmc.move(ik_ctrl, [0.1, 0, 0], relative=1)
            pmc.refresh()
            pmc.move(ik_ctrl, [-0.1, 0, 0], relative=1)
            pmc.refresh()
            finger[0].setAttr("fkIk", 0)

            self.ik_ctrls.append(created_ik_ctrls)

            if self.model.stretch_creation_switch:
                self.connect_one_chain_fk_ik_stretch(finger[1:], created_ik_ctrls[0], finger[0],
                                                     self.created_skn_jnts[n + x - 1][1:],
                                                     name="{0}_finger{1}".format(self.model.module_name, n + x), finger=1)

    def create_ik_local_spaces(self):
        for n, finger in enumerate(self.ik_ctrls):
            finger[0].addAttr("space", attributeType="enum", enumName=["world", "local"], hidden=0, keyable=1)

            if pmc.objExists("{0}_finger{1}_world_SPACELOC".format(self.model.module_name, n + 1)):
                pmc.delete("{0}_finger{1}_world_SPACELOC".format(self.model.module_name, n + 1))

            world_loc = pmc.spaceLocator(p=(0, 0, 0),
                                         n="{0}_finger{1}_world_SPACELOC".format(self.model.module_name, n + 1))
            world_loc.setAttr("translate", pmc.xform(self.created_skn_jnts[n][1], q=1, ws=1, translation=1))
            world_parent = pmc.ls(regex=".*_local_ctrl_OUTPUT$")[0]
            pmc.parent(world_loc, world_parent)

            ik_const = pmc.parentConstraint(world_loc, finger[0].getParent(), maintainOffset=1)
            rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(ik_const, world_loc, 0), finger[0].space, 0,
                                                    "{0}_worldSpace_COND".format(finger[0]))

    def create_ik_roll(self):
        duplicates_guides = []
        for guide in self.roll_guides:
            duplicate = guide.duplicate(n="{0}_duplicate".format(guide))[0]
            duplicates_guides.append(duplicate)

        # # if self.model.thumb_creation_switch:
        # #     fk_ctrls = self.created_fk_ctrls[1:]
        # # else:
        # #     fk_ctrls = self.created_fk_ctrls[:]
        # #
        # # fingers_ball_ik_handles = []
        # # for n, finger in enumerate(fk_ctrls):
        # #     ball_ik_handle = pmc.ikHandle(n=("{0}_ball_ik_HDL".format(finger[0])), startJoint=finger[0],
        # #                                   endEffector=finger[1], solver="ikSCsolver")[0]
        # #     ik_effector = pmc.listRelatives(finger[0], children=1)[-1]
        # #     ik_effector.rename("{0}_ball_ik_EFF".format(finger[0]))
        # #
        # #     finger[0].fkIk >> ball_ik_handle.ikBlend
        # #
        # #     fingers_ball_ik_handles.append(ball_ik_handle)
        # #
        # #     if self.model.how_many_phalanges == 3:
        # #         ik_setup_ball_ik_handle = pmc.ikHandle(n=("{0}_ball_ik_HDL".format(self.ik_setup_chain[n][0])), startJoint=self.ik_setup_chain[n][0],
        # #                                                endEffector=self.ik_setup_chain[n][1], solver="ikSCsolver")[0]
        # #         ik_setup_ik_effector = pmc.listRelatives(self.ik_setup_chain[n][0], children=1)[-1]
        # #         ik_setup_ik_effector.rename("{0}_ball_ik_EFF".format(self.ik_setup_chain[n][0]))
        # #
        # #         finger[0].fkIk >> ik_setup_ball_ik_handle.ikBlend
        # #
        # #         fingers_ball_ik_handles.append(ik_setup_ball_ik_handle)

        ball_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_ball_LOC".format(self.model.module_name))
        ball_loc.setAttr("rotateOrder", 2)
        # finger_roll_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_finger_roll_LOC".format(self.model.module_name))
        inhand_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_inhand_LOC".format(self.model.module_name))
        inhand_loc.setAttr("rotateOrder", 2)
        outhand_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_outhand_LOC".format(self.model.module_name))
        outhand_loc.setAttr("rotateOrder", 2)

        ball_loc.setAttr("translate", pmc.xform(duplicates_guides[0], q=1, ws=1, translation=1))
        ball_loc.setAttr("rotate", pmc.xform(duplicates_guides[0], q=1, ws=1, rotation=1))
        # finger_roll_loc.setAttr("translate", pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1))
        inhand_loc.setAttr("translate", pmc.xform(duplicates_guides[1], q=1, ws=1, translation=1))
        inhand_loc.setAttr("rotate", pmc.xform(duplicates_guides[1], q=1, ws=1, rotation=1))
        outhand_loc.setAttr("translate", pmc.xform(duplicates_guides[2], q=1, ws=1, translation=1))
        outhand_loc.setAttr("rotate", pmc.xform(duplicates_guides[2], q=1, ws=1, rotation=1))

        pmc.parent(outhand_loc, self.ctrl_input_grp)
        pmc.parent(inhand_loc, outhand_loc)
        # pmc.parent(finger_roll_loc, inhand_loc)
        # pmc.parent(ball_loc, finger_roll_loc)

        # ball_ofs = pmc.group(em=1, n="{0}_ball_loc_OFS".format(self.model.module_name))
        # pmc.parent(ball_ofs, inhand_loc)
        # ball_const = pmc.parentConstraint(finger_roll_loc, ball_ofs)
        # finger_translate_invert = pmc.createNode("multiplyDivide",
        #                                          n="{0}_finger_roll_translate_invert_value_MD".format(self.model.module_name))
        # finger_translate_invert.setAttr("input2", (-1, -1, -1))
        # finger_roll_loc.translate >> finger_translate_invert.input1
        # finger_translate_invert.output >> ball_const.target[0].targetOffsetTranslate
        #
        # pmc.parent(ball_loc, ball_ofs, r=0)

        pmc.parent(ball_loc, inhand_loc)

        # # for ik_hdl in fingers_ball_ik_handles:
        # #     pmc.parent(ik_hdl, ball_loc, r=0)

        # created_locs = [ball_loc, finger_roll_loc, inhand_loc, outhand_loc]

        pmc.delete(duplicates_guides[:])

        pmc.parent(self.parent_ik_handle, world=1)
        pmc.parent(self.parent_ik_length_end_loc, world=1)
        if self.parent_ankle_rotation_handle is not None:
            pmc.parent(self.parent_ankle_rotation_handle, world=1)

        if pmc.objExists("{0}_roll_OFS".format(self.model.module_name)):
            pmc.delete("{0}_roll_OFS".format(self.model.module_name))
        locs_offset = pmc.group(em=1, n="{0}_roll_OFS".format(self.model.module_name))
        locs_offset.setAttr("translate", pmc.xform(self.parent_ankle_ik_ctrl, q=1, ws=1, translation=1))
        locs_offset.setAttr("rotateOrder", 2)
        locs_offset.setAttr("visibility", 0)
        pmc.parent(locs_offset, self.parent_ankle_ik_ctrl, r=0)
        pmc.parent(outhand_loc, locs_offset, r=0)
        pmc.parent(self.parent_ik_handle, ball_loc, r=0)
        pmc.parent(self.parent_ik_length_end_loc, ball_loc, r=0)

        if self.parent_ankle_rotation_handle is not None:
            pmc.parent(self.parent_ankle_rotation_handle, ball_loc)

        if "roll" in pmc.listAttr(self.parent_ankle_ik_ctrl, keyable=1):
            self.parent_ankle_ik_ctrl.deleteAttr("roll")
        self.parent_ankle_ik_ctrl.addAttr("roll", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        # self.parent_ankle_ik_ctrl.addAttr("roll", attributeType="float", defaultValue=0, hasMinValue=1, minValue=0,
        #                                   hidden=0, keyable=1)
        # if "bendLimitAngle" in pmc.listAttr(self.parent_ankle_ik_ctrl, keyable=1):
        #     self.parent_ankle_ik_ctrl.deleteAttr("bendLimitAngle")
        # self.parent_ankle_ik_ctrl.addAttr("bendLimitAngle", attributeType="float", defaultValue=45, hidden=0, keyable=1)
        # if "palmStraightAngle" in pmc.listAttr(self.parent_ankle_ik_ctrl, keyable=1):
        #     self.parent_ankle_ik_ctrl.deleteAttr("palmStraightAngle")
        # self.parent_ankle_ik_ctrl.addAttr("palmStraightAngle", attributeType="float", defaultValue=70, hidden=0, keyable=1)
        if "bank" in pmc.listAttr(self.parent_ankle_ik_ctrl, keyable=1):
            self.parent_ankle_ik_ctrl.deleteAttr("bank")
        self.parent_ankle_ik_ctrl.addAttr("bank", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        if "lean" in pmc.listAttr(self.parent_ankle_ik_ctrl, keyable=1):
            self.parent_ankle_ik_ctrl.deleteAttr("lean")
        self.parent_ankle_ik_ctrl.addAttr("lean", attributeType="float", defaultValue=0, hidden=0, keyable=1)
        # if "fingerTwist" in pmc.listAttr(self.parent_ankle_ik_ctrl, keyable=1):
        #     self.parent_ankle_ik_ctrl.deleteAttr("fingerTwist")
        # self.parent_ankle_ik_ctrl.addAttr("fingerTwist", attributeType="float", defaultValue=0, hidden=0, keyable=1)

        # roll_zerotobend_limit = pmc.createNode("clamp", n="{0}_zero_to_bend_CLAMP".format(self.model.module_name))
        # roll_zerotobend_percent = pmc.createNode("setRange",
        #                                          n="{0}_zero_to_bend_percent_RANGE".format(self.model.module_name))
        # roll_bendtostraight_limit = pmc.createNode("clamp",
        #                                            n="{0}_bend_to_straight_CLAMP".format(self.model.module_name))
        # roll_bendtostraight_percent = pmc.createNode("setRange",
        #                                              n="{0}_bend_to_straight_percent_RANGE".format(
        #                                                  self.model.module_name))
        # roll_finger_mult = pmc.createNode("multiplyDivide", n="{0}_finger_roll_mult_MDV".format(self.model.module_name))
        # roll_bendtostraight_invertpercent = pmc.createNode("plusMinusAverage",
        #                                                    n="{0}_invert_percent_RANGE".format(
        #                                                        self.model.module_name))
        # roll_ball_percent_mult = pmc.createNode("multiplyDivide",
        #                                         n="{0}_ball_percent_mult_MDV".format(self.model.module_name))
        # roll_ball_mult = pmc.createNode("multiplyDivide", n="{0}_ball_roll_mult_MDV".format(self.model.module_name))
        # roll_finger_invert_value = pmc.createNode("multDoubleLinear", n="{0}_finger_roll_invert_value_MDL".format(self.model.module_name))
        # roll_ball_invert_value = pmc.createNode("multDoubleLinear", n="{0}_ball_roll_invert_value_MDL".format(self.model.module_name))

        # self.parent_ankle_ik_ctrl.bendLimitAngle >> roll_bendtostraight_limit.minR
        # self.parent_ankle_ik_ctrl.palmStraightAngle >> roll_bendtostraight_limit.maxR
        # self.parent_ankle_ik_ctrl.roll >> roll_bendtostraight_limit.inputR
        #
        # roll_bendtostraight_percent.setAttr("minX", 0)
        # roll_bendtostraight_percent.setAttr("maxX", 1)
        # roll_bendtostraight_limit.inputR >> roll_bendtostraight_percent.valueX
        # roll_bendtostraight_limit.minR >> roll_bendtostraight_percent.oldMinX
        # roll_bendtostraight_limit.maxR >> roll_bendtostraight_percent.oldMaxX
        #
        # roll_finger_mult.setAttr("operation", 1)
        # roll_bendtostraight_percent.outValueX >> roll_finger_mult.input1X
        # roll_bendtostraight_limit.inputR >> roll_finger_mult.input2X
        #
        # roll_finger_invert_value.setAttr("input2", -1)
        # roll_finger_mult.outputX >> roll_finger_invert_value.input1
        # roll_finger_invert_value.output >> finger_roll_loc.rotateZ
        #
        # roll_bendtostraight_invertpercent.setAttr("operation", 2)
        # roll_bendtostraight_invertpercent.setAttr("input1D[0]", 1)
        # roll_bendtostraight_percent.outValueX >> roll_bendtostraight_invertpercent.input1D[1]
        #
        # roll_zerotobend_limit.setAttr("minR", 0)
        # self.parent_ankle_ik_ctrl.bendLimitAngle >> roll_zerotobend_limit.maxR
        # self.parent_ankle_ik_ctrl.roll >> roll_zerotobend_limit.inputR
        #
        # roll_zerotobend_percent.setAttr("minX", 0)
        # roll_zerotobend_percent.setAttr("maxX", 1)
        # roll_zerotobend_limit.inputR >> roll_zerotobend_percent.valueX
        # roll_zerotobend_limit.minR >> roll_zerotobend_percent.oldMinX
        # roll_zerotobend_limit.maxR >> roll_zerotobend_percent.oldMaxX
        #
        # roll_ball_percent_mult.setAttr("operation", 1)
        # roll_zerotobend_percent.outValueX >> roll_ball_percent_mult.input1X
        # roll_bendtostraight_invertpercent.output1D >> roll_ball_percent_mult.input2X
        #
        # roll_ball_mult.setAttr("operation", 1)
        # roll_ball_percent_mult.outputX >> roll_ball_mult.input1X
        # self.parent_ankle_ik_ctrl.roll >> roll_ball_mult.input2X
        #
        # roll_ball_invert_value.setAttr("input2", -1)
        # roll_ball_mult.outputX >> roll_ball_invert_value.input1
        # roll_ball_invert_value.output >> ball_loc.rotateZ

        roll_ofs = pmc.createNode("plusMinusAverage", n="{0}_roll_ofs_PMA".format(self.model.module_name))
        roll_ofs.setAttr("input1D[0]", ball_loc.getAttr("rotateX"))

        self.parent_ankle_ik_ctrl.roll >> roll_ofs.input1D[1]
        roll_ofs.output1D >> ball_loc.rotateX
        # self.parent_ankle_ik_ctrl.roll >> ball_loc.rotateZ

        # finger_roll_offset = pmc.createNode("plusMinusAverage", n="{0}_fingertwist_offset_PMA".format(finger_roll_loc))
        # finger_roll_offset.setAttr("operation", 1)
        # finger_roll_offset.setAttr("input1D[0]", finger_roll_loc.getAttr("rotateY"))
        # self.parent_ankle_ik_ctrl.fingerTwist >> finger_roll_offset.input1D[1]
        # finger_roll_offset.output1D >> finger_roll_loc.rotateY

        lean_ofs = pmc.createNode("plusMinusAverage", n="{0}_lean_ofs_PMA".format(self.model.module_name))
        lean_ofs.setAttr("input1D[0]", ball_loc.getAttr("rotateZ"))

        self.parent_ankle_ik_ctrl.lean >> lean_ofs.input1D[1]
        lean_ofs.output1D >> ball_loc.rotateZ
        # self.parent_ankle_ik_ctrl.lean >> ball_loc.rotateX

        bank_in_limit = pmc.createNode("clamp", n="{0}_bank_in_CLAMP".format(self.model.module_name))
        bank_out_limit = pmc.createNode("clamp", n="{0}_bank_out_CLAMP".format(self.model.module_name))

        bank_in_ofs = pmc.createNode("plusMinusAverage", n="{0}_bank_in_ofs_PMA".format(self.model.module_name))
        bank_in_ofs.setAttr("input1D[0]", inhand_loc.getAttr("rotateZ"))
        bank_out_ofs = pmc.createNode("plusMinusAverage", n="{0}_bank_out_ofs_PMA".format(self.model.module_name))
        bank_out_ofs.setAttr("input1D[0]", outhand_loc.getAttr("rotateZ"))

        if self.model.side == "Right":
            bank_in_limit.setAttr("minR", -90)
            bank_in_limit.setAttr("maxR", 0)
            self.parent_ankle_ik_ctrl.bank >> bank_in_limit.inputR
            bank_in_limit.outputR >> bank_in_ofs.input1D[1]
            bank_in_ofs.output1D >> inhand_loc.rotateZ
            # bank_in_limit.outputR >> inhand_loc.rotateX
            bank_out_limit.setAttr("minR", 0)
            bank_out_limit.setAttr("maxR", 90)
            self.parent_ankle_ik_ctrl.bank >> bank_out_limit.inputR
            bank_out_limit.outputR >> bank_out_ofs.input1D[1]
            bank_out_ofs.output1D >> outhand_loc.rotateZ
        else:
            bank_invert = pmc.createNode("multiplyDivide", n="{0}_bank_invert_value_MDV".format(self.model.module_name))
            bank_invert.setAttr("input2X", -1)
            self.parent_ankle_ik_ctrl.bank >> bank_invert.input1X
            bank_in_limit.setAttr("minR", 0)
            bank_in_limit.setAttr("maxR", 90)
            bank_invert.outputX >> bank_in_limit.inputR
            bank_in_limit.outputR >> bank_in_ofs.input1D[1]
            bank_in_ofs.output1D >> inhand_loc.rotateZ
            # bank_in_limit.outputR >> inhand_loc.rotateX
            bank_out_limit.setAttr("minR", -90)
            bank_out_limit.setAttr("maxR", 0)
            bank_invert.outputX >> bank_out_limit.inputR
            bank_out_limit.outputR >> bank_out_ofs.input1D[1]
            bank_out_ofs.output1D >> outhand_loc.rotateZ
        # bank_out_limit.outputR >> outhand_loc.rotateX

        # if self.model.thumb_creation_switch:
        #     self.ik_ctrls[0][0].addAttr("thumb", dataType="string", hidden=0, keyable=0, readable=1, writable=1)
        #     self.ik_ctrls[0][0].setAttr("thumb", lock=True, channelBox=False)
        #
        # finger_roll_loc_position_script = """import pymel.core as pmc
        # \ndef finger_roll_position_change():
        # \n    ik_positions_x = []
        # \n    ik_positions_y = []
        # \n    ik_positions_z = []
        #
        # \n    for ik_ctrl in pmc.ls(regex="{0}_ctrl_INPUT\|{0}_finger.*_ik_CTRL$"):
        # \n        finger_ik_switch = pmc.ls(str(ik_ctrl).replace("ik", "0_fk"))[0]
        # \n        if pmc.getAttr(finger_ik_switch.fkIk) == 1:
        # \n            try:
        # \n                pmc.listAttr(ik_ctrl.thumb)
        # \n            except:
        # \n                ik_positions_x.append(pmc.xform(ik_ctrl, q=1, ws=1, translation=1)[0])
        # \n                ik_positions_y.append(pmc.xform(ik_ctrl, q=1, ws=1, translation=1)[1])
        # \n                ik_positions_z.append(pmc.xform(ik_ctrl, q=1, ws=1, translation=1)[2])
        #
        # \n    if len(ik_positions_x) == 0:
        # \n        return
        #
        # \n    finger_roll_loc_pos_x = 0.0
        # \n    finger_roll_loc_pos_y = 0.0
        # \n    finger_roll_loc_pos_z = 0.0
        #
        # \n    for x in ik_positions_x:
        # \n        finger_roll_loc_pos_x += x
        # \n    finger_roll_loc_pos_x = finger_roll_loc_pos_x / len(ik_positions_x)
        #
        # \n    for y in ik_positions_y:
        # \n        finger_roll_loc_pos_y += y
        # \n    finger_roll_loc_pos_y = finger_roll_loc_pos_y / len(ik_positions_y)
        #
        # \n    for z in ik_positions_z:
        # \n        finger_roll_loc_pos_z += z
        # \n    finger_roll_loc_pos_z = finger_roll_loc_pos_z / len(ik_positions_z)
        #
        # \n    pmc.xform("{0}_finger_roll_LOC", ws=1, translation=(finger_roll_loc_pos_x, finger_roll_loc_pos_y, finger_roll_loc_pos_z))
        #
        # \n    pmc.setKeyframe("{0}_finger_roll_LOC", at="tx", inTangentType="stepnext", outTangentType="step", value=pmc.getAttr("{0}_finger_roll_LOC.translateX"))
        # \n    pmc.setKeyframe("{0}_finger_roll_LOC", at="ty", inTangentType="stepnext", outTangentType="step", value=pmc.getAttr("{0}_finger_roll_LOC.translateY"))
        # \n    pmc.setKeyframe("{0}_finger_roll_LOC", at="tz", inTangentType="stepnext", outTangentType="step", value=pmc.getAttr("{0}_finger_roll_LOC.translateZ"))
        #
        # \npmc.scriptJob(attributeChange=["{1}.roll", finger_roll_position_change])
        # """.format(self.model.module_name, self.parent_ankle_ik_ctrl)

        # if pmc.objExists("{0}_finger_roll_loc_position_SN".format(self.model.module_name)):
        #     pmc.delete("{0}_finger_roll_loc_position_SN".format(self.model.module_name))
        # pmc.scriptNode(scriptType=2, beforeScript=finger_roll_loc_position_script.replace("'''", "''"),
        #                n="{0}_finger_roll_loc_position_SN".format(self.model.module_name), sourceType="python")


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.side = "Left"
        self.how_many_fingers = 3
        self.thumb_creation_switch = True
        self.how_many_phalanges = 3
        self.ik_creation_switch = False
        self.stretch_creation_switch = False
        self.raz_ik_ctrls = False
        self.raz_fk_ctrls = False
        self.roll_creation_switch = False
