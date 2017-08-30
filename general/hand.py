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
        self.how_many_fingers = QtWidgets.QSpinBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.side_cbbox.setCurrentText(self.model.side)
        self.how_many_fingers.setValue(self.model.how_many_fingers)
        self.ctrl.look_for_parent()

    def setup_ui(self):
        self.modules_cbbox.setModel(self.ctrl.modules_with_output)
        self.modules_cbbox.currentTextChanged.connect(self.ctrl.on_modules_cbbox_changed)

        self.outputs_cbbox.setModel(self.ctrl.outputs_model)
        self.outputs_cbbox.currentTextChanged.connect(self.ctrl.on_outputs_cbbox_changed)

        self.side_cbbox.insertItems(0, ["Left", "Right"])
        self.side_cbbox.currentTextChanged.connect(self.ctrl.on_side_cbbox_changed)

        self.how_many_fingers.setMinimum(1)
        self.how_many_fingers.valueChanged.connect(self.ctrl.on_how_many_fingers_changed)

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

        fingers_layout = QtWidgets.QVBoxLayout()
        fingers_text = QtWidgets.QLabel("How many fingers :")
        fingers_layout.addWidget(fingers_text)
        fingers_layout.addWidget(self.how_many_fingers)

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
        self.guides_names = []
        self.side = {}
        self.side_coef = 0
        self.created_skn_jnts = []
        self.parent_wrist_fk_ctrl = None
        self.parent_wrist_ik_ctrl = None
        RigController.__init__(self, model, view)

    def on_how_many_fingers_changed(self, value):
        self.model.how_many_fingers = value

    def prebuild(self):
        self.guides_names = []
        self.guides = []
        first_jnt = "{0}_wrist_GUIDE".format(self.model.module_name)
        for i in range(0, self.model.how_many_fingers):
            finger_curve = "{0}_finger{1}_phalanges_GUIDE".format(self.model.module_name, i+1)
            finger = [first_jnt, finger_curve]
            self.guides_names.append(finger)

        self.side = {"Left": 1, "Right": -1}
        self.side_coef = self.side.get(self.model.side)

        if self.guide_check(self.guides_names):
            self.guides = [pmc.ls(guide)[:] for guide in self.guides_names]
            self.guides_grp = pmc.ls("{0}_guides".format(self.model.module_name))[0]
            return

        wrist_guide = pmc.spaceLocator(p=(0, 0, 0), n=first_jnt)
        wrist_guide.setAttr("translate", (7 * self.side_coef, 14, 0))
        for i, finger in enumerate(self.guides_names):
            finger_guide = rig_lib.create_curve_guide(d=1, number_of_points=4, name=finger[1], hauteur_curve=3)
            if i == 0:
                finger_guide.setAttr("translate", (8 * self.side_coef, 14, 1))
            else:
                finger_guide.setAttr("translate", (9 * self.side_coef, 14, 1 - (0.5 * i)))
            finger_guide.setAttr("rotate", (0, 90 * (1 - self.side_coef), 0))
            finger = [wrist_guide, finger_guide]
            self.guides.append(finger)
        self.guides_grp = self.group_guides(self.guides)
        self.guides_grp.setAttr("visibility", 1)
        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()

        self.delete_existing_objects()
        self.connect_to_parent()

        self.get_parent_needed_objects()

        self.create_skn_jnts()
        self.create_ctrls()

    def get_parent_needed_objects(self):
        self.parent_wrist_fk_ctrl = pmc.ls("{0}_wrist_fk_CTRL".format(self.model.selected_module))[0]
        self.parent_wrist_ik_ctrl = pmc.ls("{0}_wrist_ik_CTRL".format(self.model.selected_module))[0]

    def create_skn_jnts(self):
        duplicate_guides = []
        self.created_skn_jnts = []
        orient_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_wrist_LOC".format(self.model.module_name))
        orient_loc.setAttr("translate", pmc.xform(self.guides[0][0], q=1, ws=1, translation=1))
        loc_const = pmc.aimConstraint(self.guides[len(self.guides)/2][1], orient_loc, maintainOffset=0,
                                      aimVector=(1.0 * self.side_coef, 0.0, 0.0),
                                      upVector=(0.0, 1.0 * self.side_coef, 0.0), worldUpType="scene")
        pmc.xform(self.parent_wrist_fk_ctrl, ws=1, rotation=(pmc.xform(orient_loc, q=1, ws=1, rotation=1)))
        pmc.xform(self.parent_wrist_ik_ctrl, ws=1, rotation=(pmc.xform(orient_loc, q=1, ws=1, rotation=1)))
        pmc.delete(loc_const)
        for n, finger in enumerate(self.guides):
            created_finger_jnts = []
            wrist_guide = finger[0].duplicate(n="{0}_duplicate".format(finger[0]))[0]
            wrist_guide.setAttr("rotateOrder", 3)
            finger_crv_vertex_list = finger[1].cv[:]
            finger_new_guides = [wrist_guide]
            for i, cv in enumerate(finger_crv_vertex_list):
                loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_{1}_duplicate".format(finger[1], i+1))
                loc.setAttr("translate", (pmc.xform(cv, q=1, ws=1, translation=1)))
                loc.setAttr("rotateOrder", 3)
                finger_new_guides.append(loc)
            duplicate_guides.append(finger_new_guides)

            for i, guide in enumerate(finger_new_guides):
                if not guide == finger_new_guides[-1]:
                    const = pmc.aimConstraint(finger_new_guides[i+1], guide, maintainOffset=0,
                                              aimVector=(1.0 * self.side_coef, 0.0, 0.0),
                                              upVector=(0.0, 1.0 * self.side_coef, 0.0), worldUpType="scene")
                    pmc.delete(const)
                    pmc.select(d=1)
                if i != 0:
                    pmc.parent(guide, finger_new_guides[i-1])
                    pmc.select(created_finger_jnts[i-1])

                jnt = pmc.joint(p=(pmc.xform(guide, q=1, ws=1, translation=1)),
                                n="{0}_finger{1}_{2}_SKN".format(self.model.module_name, n+1, i), rad=0.2)
                jnt.setAttr("rotateOrder", 3)

                if i == 0:
                    pmc.parent(jnt, self.jnt_input_grp, r=0)
                    jnt.setAttr("jointOrient", (0, 0, 0))

                if i != len(finger_new_guides)-1:
                    pmc.xform(jnt, ws=1, rotation=(pmc.xform(guide, q=1, ws=1, rotation=1)))

                if i == 0 and self.model.side == "Right":
                    jnt.setAttr("jointOrientX", -180)
                    jnt.setAttr("rotate", (pmc.xform(jnt, q=1, rotation=1)[0] + 180,
                                           pmc.xform(jnt, q=1, rotation=1)[1] * -1,
                                           pmc.xform(jnt, q=1, rotation=1)[2] * -1))

                created_finger_jnts.append(jnt)

            created_finger_jnts[-1].rename("{0}_finger{1}_end_JNT".format(self.model.module_name, n+1))

            self.created_skn_jnts.append(created_finger_jnts)

        pmc.delete(duplicate_guides[:])
        pmc.delete(orient_loc)

    def create_ctrls(self):
        pass
    # TODO: penser a creer un node d'offset pour garder la valeur de rotate Y des jnt (pour l'ecartement des doigts)


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.selected_module = None
        self.selected_output = None
        self.side = "Left"
        self.how_many_fingers = 5
