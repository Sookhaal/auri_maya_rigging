from PySide2 import QtWidgets, QtCore, QtGui

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, is_checked, grpbox
from auri.scripts.Maya_Scripts import rig_lib
from auri.scripts.Maya_Scripts.rig_lib import RigController

reload(rig_lib)

try:
    pref = pmc.selectPref(query=True, trackSelectionOrder=True)
    if not pref:
        pmc.selectPref(trackSelectionOrder=True)
        pmc.select(clear=True)
        pmc.warning("Turning on 'Selection-Order Tracking' option.")
except TypeError:
    pmc.error("Can't find the 'Selection Order' option in Maya Preferences.")


class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        self.prebuild_btn = QtWidgets.QPushButton("Prebuild")
        self.mesh_to_follow = QtWidgets.QLineEdit()
        self.set_top_btn = QtWidgets.QPushButton("Set Selection")
        self.set_bot_btn = QtWidgets.QPushButton("Set Selection")
        self.add_top_btn = QtWidgets.QPushButton("Add to Selection")
        self.add_bot_btn = QtWidgets.QPushButton("Add to Selection")
        self.remove_top_btn = QtWidgets.QPushButton("Remove from Selection")
        self.remove_bot_btn = QtWidgets.QPushButton("Remove from Selection")
        self.top_selection_view = QtWidgets.QListView()
        self.top_selection = QtGui.QStringListModel()
        self.bot_selection_view = QtWidgets.QListView()
        self.bot_selection = QtGui.QStringListModel()
        self.top_creation_switch = QtWidgets.QCheckBox()
        self.bot_creation_switch = QtWidgets.QCheckBox()
        self.top_selection_grp = None
        self.bot_selection_grp = None
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.mesh_to_follow.setText(self.model.mesh_to_follow)
        self.top_selection.setStringList(self.model.top_selection)
        self.bot_selection.setStringList(self.model.bot_selection)
        self.top_creation_switch.setChecked(self.model.top_creation_switch)
        self.bot_creation_switch.setChecked(self.model.bot_creation_switch)
        self.top_selection_grp.setVisible(self.model.top_creation_switch)
        self.bot_selection_grp.setVisible(self.model.bot_creation_switch)

    def setup_ui(self):
        self.mesh_to_follow.textChanged.connect(self.ctrl.on_mesh_to_follow_changed)

        self.top_selection_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.top_selection.setStringList(self.model.top_selection)
        self.top_selection_view.setModel(self.top_selection)

        self.set_top_btn.clicked.connect(self.ctrl.set_top_selection)
        self.add_top_btn.clicked.connect(self.ctrl.add_top_selection)
        self.remove_top_btn.clicked.connect(self.ctrl.remove_from_top_selection)

        self.bot_selection_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.bot_selection.setStringList(self.model.bot_selection)
        self.bot_selection_view.setModel(self.bot_selection)

        self.set_bot_btn.clicked.connect(self.ctrl.set_bot_selection)
        self.add_bot_btn.clicked.connect(self.ctrl.add_bot_selection)
        self.remove_bot_btn.clicked.connect(self.ctrl.remove_from_bot_selection)

        self.top_creation_switch.stateChanged.connect(self.ctrl.on_top_creation_switch_changed)
        self.bot_creation_switch.stateChanged.connect(self.ctrl.on_bot_creation_switch_changed)

        self.prebuild_btn.clicked.connect(self.ctrl.prebuild)

        main_layout = QtWidgets.QVBoxLayout()

        mesh_to_follow_layout = QtWidgets.QVBoxLayout()
        mesh_to_follow_grp = grpbox("Mesh to attach the ctrls to:", mesh_to_follow_layout)
        mesh_to_follow_layout.addWidget(self.mesh_to_follow)

        top_selection_layout = QtWidgets.QVBoxLayout()
        self.top_selection_grp = grpbox("Select top Components :", top_selection_layout)
        top_selection_layout.addWidget(self.set_top_btn)
        top_selection_layout.addWidget(self.top_selection_view)
        top_btn_layout = QtWidgets.QHBoxLayout()
        top_btn_layout.addWidget(self.add_top_btn)
        top_btn_layout.addWidget(self.remove_top_btn)
        top_selection_layout.addLayout(top_btn_layout)

        bot_selection_layout = QtWidgets.QVBoxLayout()
        self.bot_selection_grp = grpbox("Select bot Components :", bot_selection_layout)
        bot_selection_layout.addWidget(self.set_bot_btn)
        bot_selection_layout.addWidget(self.bot_selection_view)
        bot_btn_layout = QtWidgets.QHBoxLayout()
        bot_btn_layout.addWidget(self.add_bot_btn)
        bot_btn_layout.addWidget(self.remove_bot_btn)
        bot_selection_layout.addLayout(bot_btn_layout)

        top_switch_layout = QtWidgets.QHBoxLayout()
        top_switch_text = QtWidgets.QLabel("Create Top Ribbon:")
        top_switch_layout.addWidget(top_switch_text)
        top_switch_layout.addWidget(self.top_creation_switch)

        bot_switch_layout = QtWidgets.QHBoxLayout()
        bot_switch_text = QtWidgets.QLabel("Create Bot Ribbon:")
        bot_switch_layout.addWidget(bot_switch_text)
        bot_switch_layout.addWidget(self.bot_creation_switch)

        # options_layout = QtWidgets.QVBoxLayout()
        # options_grp = grpbox("Options", options_layout)
        #
        # ctrls_layout = QtWidgets.QVBoxLayout()
        # ctrls_text = QtWidgets.QLabel("Option :")
        # ctrls_layout.addWidget(ctrls_text)
        #
        # options_layout.addLayout(ctrls_layout)

        main_layout.addWidget(mesh_to_follow_grp)
        main_layout.addLayout(top_switch_layout)
        main_layout.addWidget(self.top_selection_grp)
        main_layout.addLayout(bot_switch_layout)
        main_layout.addWidget(self.bot_selection_grp)
        # main_layout.addWidget(options_grp)
        self.setLayout(main_layout)


class Controller(RigController):
    def __init__(self, model, view):
        """

        Args:
            model (Model):
            view (View):
        """
        self.mesh_to_follow = None
        self.top_components = []
        self.bot_components = []
        self.top_components_type = None
        self.bot_components_type = None
        RigController.__init__(self,  model, view)

    def on_mesh_to_follow_changed(self, text):
        self.model.mesh_to_follow = text

    def set_top_selection(self):
        selection = pmc.ls(orderedSelection=1, flatten=1)
        self.model.top_selection = [str(obj) for obj in selection]
        self.view.top_selection.setStringList(self.model.top_selection)

    def add_top_selection(self):
        selection = pmc.ls(orderedSelection=1, flatten=1)
        for obj in selection:
            self.model.top_selection.append(str(obj))
        self.view.top_selection.setStringList(self.model.top_selection)

    def remove_from_top_selection(self):
        indexes = self.view.top_selection_view.selectedIndexes()
        indexes_to_del = []
        for index in indexes:
            space_index = index.row()
            indexes_to_del.append(space_index)

        indexes_to_del_set = set(indexes_to_del)
        self.model.top_selection = [self.model.top_selection[i] for i in xrange(len(self.model.top_selection)) if
                                                                                            i not in indexes_to_del_set]

        self.view.top_selection.setStringList(self.model.top_selection)

    def set_bot_selection(self):
        selection = pmc.ls(orderedSelection=1, flatten=1)
        self.model.bot_selection = [str(obj) for obj in selection]
        self.view.bot_selection.setStringList(self.model.bot_selection)

    def add_bot_selection(self):
        selection = pmc.ls(orderedSelection=1, flatten=1)
        for obj in selection:
            self.model.bot_selection.append(str(obj))
        self.view.bot_selection.setStringList(self.model.bot_selection)

    def remove_from_bot_selection(self):
        indexes = self.view.bot_selection_view.selectedIndexes()
        indexes_to_del = []
        for index in indexes:
            space_index = index.row()
            indexes_to_del.append(space_index)

        indexes_to_del_set = set(indexes_to_del)
        self.model.bot_selection = [self.model.bot_selection[i] for i in xrange(len(self.model.bot_selection)) if
                                    i not in indexes_to_del_set]

        self.view.bot_selection.setStringList(self.model.bot_selection)

    def on_top_creation_switch_changed(self, state):
        self.model.top_creation_switch = is_checked(state)
        self.view.top_selection_grp.setVisible(is_checked(state))

    def on_bot_creation_switch_changed(self, state):
        self.model.bot_creation_switch = is_checked(state)
        self.view.bot_selection_grp.setVisible(is_checked(state))

    def prebuild(self):
        mesh_to_follow_list = pmc.ls(self.model.mesh_to_follow)
        if not mesh_to_follow_list:
            pmc.error("no mesh given, need one to attach the ctrls")
            return False
        elif len(mesh_to_follow_list) > 1:
            pmc.error("multiple objects match given name, give the long_name of the object to find the chosen one")
            return False
        elif mesh_to_follow_list[0].getShape() is None or pmc.nodeType(mesh_to_follow_list[0].getShape()) != "mesh":
            pmc.error("given object isn't a mesh")
            return False
        else:
            self.mesh_to_follow = mesh_to_follow_list[0]

        if self.model.top_creation_switch:
            top_components_vertex_list = pmc.filterExpand(pmc.ls(self.model.top_selection), sm=31)
            top_components_edge_list = pmc.filterExpand(pmc.ls(self.model.top_selection), sm=32)
            top_components_face_list = pmc.filterExpand(pmc.ls(self.model.top_selection), sm=34)

            if not top_components_vertex_list and not top_components_edge_list and not top_components_face_list:
                pmc.error("no components given in top selection")
                return False
            elif top_components_vertex_list is not None and (top_components_edge_list is not None or top_components_face_list is not None) or \
                    (top_components_edge_list is not None and top_components_face_list is not None):
                pmc.error("more than one component's type given in top selection")
                return False
            elif (top_components_vertex_list is not None and len(top_components_vertex_list) != len(self.model.top_selection)) or \
                    (top_components_edge_list is not None and len(top_components_edge_list) != len(self.model.top_selection)) or \
                    (top_components_face_list is not None and len(top_components_face_list) != len(self.model.top_selection)):
                pmc.error("non-component type object given in top selection, need components only")
                return False
            elif (top_components_vertex_list is not None and len(top_components_vertex_list) == 1) or \
                    (top_components_edge_list is not None and len(top_components_edge_list) == 1) or \
                    (top_components_face_list is not None and len(top_components_face_list) == 1):
                pmc.error("only one component given in top selection, need at least 2")
                return False
            elif top_components_vertex_list is not None:
                self.top_components = pmc.ls(self.model.top_selection)
                self.top_components_type = "vertex"
            elif top_components_edge_list is not None:
                self.top_components = pmc.ls(self.model.top_selection)
                self.top_components_type = "edge"
            elif top_components_face_list is not None:
                self.top_components = pmc.ls(self.model.top_selection)
                self.top_components_type = "face"

        if self.model.bot_creation_switch:
            bot_components_vertex_list = pmc.filterExpand(pmc.ls(self.model.bot_selection), sm=31)
            bot_components_edge_list = pmc.filterExpand(pmc.ls(self.model.bot_selection), sm=32)
            bot_components_face_list = pmc.filterExpand(pmc.ls(self.model.bot_selection), sm=34)

            if not bot_components_vertex_list and not bot_components_edge_list and not bot_components_face_list:
                pmc.error("no components given in bot selection")
                return False
            elif bot_components_vertex_list is not None and (bot_components_edge_list is not None or bot_components_face_list is not None) or \
                    (bot_components_edge_list is not None and bot_components_face_list is not None):
                pmc.error("more than one component's type given in bot selection")
                return False
            elif (bot_components_vertex_list is not None and len(bot_components_vertex_list) != len(self.model.bot_selection)) or \
                    (bot_components_edge_list is not None and len(bot_components_edge_list) != len(self.model.bot_selection)) or \
                    (bot_components_face_list is not None and len(bot_components_face_list) != len(self.model.bot_selection)):
                pmc.error("non-component type object given in bot selection, need components only")
                return False
            elif (bot_components_vertex_list is not None and len(bot_components_vertex_list) == 1) or \
                    (bot_components_edge_list is not None and len(bot_components_edge_list) == 1) or \
                    (bot_components_face_list is not None and len(bot_components_face_list) == 1):
                pmc.error("only one component given in bot selection, need at least 2")
                return False
            elif bot_components_vertex_list is not None:
                self.bot_components = pmc.ls(self.model.bot_selection)
                self.bot_components_type = "vertex"
            elif bot_components_edge_list is not None:
                self.bot_components = pmc.ls(self.model.bot_selection)
                self.bot_components_type = "edge"
            elif bot_components_face_list is not None:
                self.bot_components = pmc.ls(self.model.bot_selection)
                self.bot_components_type = "face"

        self.view.refresh_view()
        pmc.select(d=1)
        return True

    def execute(self):
        if not self.prebuild():
            return

        if self.model.top_creation_switch:
            print self.top_components
            print self.top_components_type
        if self.model.bot_creation_switch:
            print self.bot_components
            print self.bot_components_type

        if self.model.top_creation_switch:
            self.create_ribbons("top", self.top_components_type, self.top_components)

        if self.model.bot_creation_switch:
            self.create_ribbons("bot", self.bot_components_type, self.bot_components)

    def create_ribbons(self, side, components_type, selection):
        if components_type != "face":
            if components_type == "edge":
                vertices_from_selection = pmc.polyListComponentConversion(selection, fromEdge=1, toVertex=1)
                vertices = pmc.ls(vertices_from_selection, flatten=1)
            else:
                vertices = selection

            vertices_world_pos = []
            skn_jnts = []
            for i, vertex in enumerate(vertices):
                vertices_world_pos.append(pmc.xform(vertex, q=1, ws=1, translation=1))
                pmc.select(cl=1)
                jnt = pmc.joint(p=(0, 0, 0), n="{0}_{1}_{2}_SKN".format(self.model.module_name, side, i))
                jnt.setAttr("translate", vertices_world_pos[i])
                jnt.setAttr("radius", 0.1)
                skn_jnts.append(jnt)

            front_curve = pmc.curve(d=3, p=vertices_world_pos, n="{0}_{1}_nurbsSurface_guide_01".format(self.model.module_name, side))
            back_curve = pmc.duplicate(front_curve, n="{0}_{1}_nurbsSurface_guide_02".format(self.model.module_name, side))[0]
            front_curve.setAttr("translateZ", 0.1)
            back_curve.setAttr("translateZ", -0.1)

            surface = pmc.loft(back_curve, front_curve, ar=1, ch=0, d=1, uniform=0, n="{0}_{1}_ribbons_NURBSSURFACE".format(self.model.module_name, side))[0]
            surface = pmc.rebuildSurface(surface, ch=0, du=1, dv=3, dir=2, kcp=1, kr=0, rt=0, rpo=1)[0]

            pmc.delete(front_curve)
            pmc.delete(back_curve)

            follicles = []
            for i, jnt in enumerate(skn_jnts):
                follicle_shape = pmc.createNode("follicle", n="{0}_{1}_{2}_FOLShape".format(self.model.module_name, side, i))
                follicle = follicle_shape.getParent()
                follicle.rename("{0}_{1}_{2}_FOL".format(self.model.module_name, side, i))

                follicle_shape.outTranslate >> follicle.translate
                follicle_shape.outRotate >> follicle.rotate
                surface.getShape().local >> follicle_shape.inputSurface
                surface.getShape().worldMatrix[0] >> follicle_shape.inputWorldMatrix

                point_on_surface = pmc.createNode("closestPointOnSurface", n=str(jnt) + "CPS")
                surface.getShape().local >> point_on_surface.inputSurface
                point_on_surface.setAttr("inPosition", pmc.xform(jnt, q=1, ws=1, translation=1))

                follicle_shape.setAttr("parameterU", point_on_surface.getAttr("parameterU"))
                follicle_shape.setAttr("parameterV", point_on_surface.getAttr("parameterV"))

                pmc.delete(point_on_surface)

                pmc.parent(jnt, follicle, r=0)

                follicles.append(follicle)

            pmc.select(cl=1)
            start_jnt = pmc.joint(p=(0, 0, 0), n="{0}_{1}_start_JNT".format(self.model.module_name, side))
            start_jnt.setAttr("radius", 0.2)
            pmc.select(cl=1)
            end_jnt = pmc.joint(p=(0, 0, 0), n="{0}_{1}_end_JNT".format(self.model.module_name, side))
            end_jnt.setAttr("radius", 0.2)
            pmc.select(cl=1)
            mid_jnt = pmc.joint(p=(0, 0, 0), n="{0}_{1}_mid_JNT".format(self.model.module_name, side))
            mid_jnt.setAttr("radius", 0.2)
            pmc.select(cl=1)
            start_mid_jnt = pmc.joint(p=(0, 0, 0), n="{0}_{1}_start_mid_JNT".format(self.model.module_name, side))
            start_mid_jnt.setAttr("radius", 0.2)
            pmc.select(cl=1)
            mid_end_jnt = pmc.joint(p=(0, 0, 0), n="{0}_{1}_mid_end_JNT".format(self.model.module_name, side))
            mid_end_jnt.setAttr("radius", 0.2)

            ctrl_jnts_pos = pmc.createNode("pointOnSurfaceInfo", n="{0}_{1}_PSI".format(self.model.module_name, side))
            surface.getShape().local >> ctrl_jnts_pos.inputSurface
            ctrl_jnts_pos.setAttr("parameterU", 0.5)

            ctrl_jnts_pos.setAttr("parameterV", 0.0)
            pmc.refresh()
            start_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

            ctrl_jnts_pos.setAttr("parameterV", 0.25)
            pmc.refresh()
            start_mid_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

            ctrl_jnts_pos.setAttr("parameterV", 0.5)
            pmc.refresh()
            mid_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

            ctrl_jnts_pos.setAttr("parameterV", 0.75)
            pmc.refresh()
            mid_end_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

            ctrl_jnts_pos.setAttr("parameterV", 1.0)
            pmc.refresh()
            end_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

            pmc.delete(ctrl_jnts_pos)

            pmc.select(cl=1)
            pmc.skinCluster(start_jnt, start_mid_jnt, mid_jnt, mid_end_jnt, end_jnt, surface, bm=0, dr=4.0, mi=2, nw=1,
                            sm=0, tsb=1, wd=0)


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        # self.selected_module = None
        # self.selected_output = None
        # self.side = "Center"
        self.top_selection = []
        self.bot_selection = []
        self.top_creation_switch = True
        self.bot_creation_switch = False
        self.mesh_to_follow = None
