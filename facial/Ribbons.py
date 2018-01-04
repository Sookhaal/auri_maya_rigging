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
        self.how_many_top_ctrls_cbbox = QtWidgets.QComboBox()
        self.how_many_bot_ctrls_cbbox = QtWidgets.QComboBox()
        self.set_mesh_btn = QtWidgets.QPushButton("Set Mesh")
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
        self.how_many_top_ctrls_cbbox.setCurrentText(self.model.how_many_top_ctrls)
        self.how_many_bot_ctrls_cbbox.setCurrentText(self.model.how_many_bot_ctrls)

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

        self.how_many_top_ctrls_cbbox.insertItems(0, ["5", "7"])
        self.how_many_top_ctrls_cbbox.currentTextChanged.connect(self.ctrl.on_how_many_top_ctrls_cbbox_changed)
        self.how_many_bot_ctrls_cbbox.insertItems(0, ["5", "7"])
        self.how_many_bot_ctrls_cbbox.currentTextChanged.connect(self.ctrl.on_how_many_bot_ctrls_cbbox_changed)

        self.set_mesh_btn.clicked.connect(self.ctrl.set_mesh_to_follow)

        self.prebuild_btn.clicked.connect(self.ctrl.prebuild)

        main_layout = QtWidgets.QVBoxLayout()

        mesh_to_follow_layout = QtWidgets.QVBoxLayout()
        mesh_to_follow_grp = grpbox("Mesh to attach the ctrls to:", mesh_to_follow_layout)
        mesh_to_follow_layout.addWidget(self.mesh_to_follow)
        mesh_to_follow_layout.addWidget(self.set_mesh_btn)

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

        how_many_top_layout = QtWidgets.QVBoxLayout()
        how_many_top_grp = grpbox("How many ctrls :", how_many_top_layout)
        how_many_top_layout.addWidget(self.how_many_top_ctrls_cbbox)

        how_many_bot_layout = QtWidgets.QVBoxLayout()
        how_many_bot_grp = grpbox("How many ctrls :", how_many_bot_layout)
        how_many_bot_layout.addWidget(self.how_many_bot_ctrls_cbbox)

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
        main_layout.addWidget(how_many_top_grp)
        main_layout.addWidget(self.top_selection_grp)
        main_layout.addLayout(bot_switch_layout)
        main_layout.addWidget(how_many_bot_grp)
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
        self.top_skn_jnts = []
        self.bot_skn_jnts = []
        self.top_surface = None
        self.bot_surface = None
        self.top_follicles = []
        self.bot_follicles = []
        self.top_ctrls_jnt = []
        self.bot_ctrls_jnt = []
        self.top_ctrls_fol = []
        self.bot_ctrls_fol = []
        self.top_ctrls = []
        self.bot_ctrls = []
        self.sides_master_jnts = []
        self.sides_ctrls_fol = []
        self.sides_ctrls = []
        self.jnts_to_skin = []
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

    def on_how_many_top_ctrls_cbbox_changed(self, text):
        self.model.how_many_top_ctrls = text

    def on_how_many_bot_ctrls_cbbox_changed(self, text):
        self.model.how_many_bot_ctrls = text

    def prebuild(self):
        mesh_to_follow_list = pmc.ls(self.model.mesh_to_follow)
        if not mesh_to_follow_list:
            pmc.error("for module \"{0}\", no mesh given, need one to attach the ctrls".format(self.model.module_name))
            return False
        elif len(mesh_to_follow_list) > 1:
            pmc.error("for module \"{0}\", multiple objects match given name, give the long_name of the object to find the chosen one".format(self.model.module_name))
            return False
        elif mesh_to_follow_list[0].getShape() is None or pmc.nodeType(mesh_to_follow_list[0].getShape()) != "mesh":
            pmc.error("for module \"{0}\", given object isn't a mesh".format(self.model.module_name))
            return False
        else:
            self.mesh_to_follow = mesh_to_follow_list[0]

        if self.model.top_creation_switch:
            top_components_vertex_list = pmc.filterExpand(pmc.ls(self.model.top_selection), sm=31)
            top_components_edge_list = pmc.filterExpand(pmc.ls(self.model.top_selection), sm=32)
            top_components_face_list = pmc.filterExpand(pmc.ls(self.model.top_selection), sm=34)

            if not top_components_vertex_list and not top_components_edge_list and not top_components_face_list:
                pmc.error("for module \"{0}\", no components given in top selection".format(self.model.module_name))
                return False
            elif top_components_vertex_list is not None and (top_components_edge_list is not None or top_components_face_list is not None) or \
                    (top_components_edge_list is not None and top_components_face_list is not None):
                pmc.error("for module \"{0}\", more than one component's type given in top selection".format(self.model.module_name))
                return False
            elif (top_components_vertex_list is not None and len(top_components_vertex_list) != len(self.model.top_selection)) or \
                    (top_components_edge_list is not None and len(top_components_edge_list) != len(self.model.top_selection)) or \
                    (top_components_face_list is not None and len(top_components_face_list) != len(self.model.top_selection)):
                pmc.error("for module \"{0}\", non-component type object given in top selection, need components only".format(self.model.module_name))
                return False
            elif (top_components_vertex_list is not None and len(top_components_vertex_list) == 1) or \
                    (top_components_edge_list is not None and len(top_components_edge_list) == 1) or \
                    (top_components_face_list is not None and len(top_components_face_list) == 1):
                pmc.error("for module \"{0}\", only one component given in top selection, need at least 2".format(self.model.module_name))
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
                pmc.error("for module \"{0}\", no components given in bot selection".format(self.model.module_name))
                return False
            elif bot_components_vertex_list is not None and (bot_components_edge_list is not None or bot_components_face_list is not None) or \
                    (bot_components_edge_list is not None and bot_components_face_list is not None):
                pmc.error("for module \"{0}\", more than one component's type given in bot selection".format(self.model.module_name))
                return False
            elif (bot_components_vertex_list is not None and len(bot_components_vertex_list) != len(self.model.bot_selection)) or \
                    (bot_components_edge_list is not None and len(bot_components_edge_list) != len(self.model.bot_selection)) or \
                    (bot_components_face_list is not None and len(bot_components_face_list) != len(self.model.bot_selection)):
                pmc.error("for module \"{0}\", non-component type object given in bot selection, need components only".format(self.model.module_name))
                return False
            elif (bot_components_vertex_list is not None and len(bot_components_vertex_list) == 1) or \
                    (bot_components_edge_list is not None and len(bot_components_edge_list) == 1) or \
                    (bot_components_face_list is not None and len(bot_components_face_list) == 1):
                pmc.error("for module \"{0}\", only one component given in bot selection, need at least 2".format(self.model.module_name))
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
        self.jnts_to_skin = []
        if not self.prebuild():
            return

        self.delete_existing_objects()
        self.connect_to_parent()

        if self.model.top_creation_switch:
            needs = self.create_ribbons("top", self.top_components_type, self.top_components, self.model.how_many_top_ctrls)
            self.top_skn_jnts = needs[0]
            self.top_surface = needs[1]
            self.top_follicles = needs[2]
            self.top_ctrls_jnt = needs[3]
            self.top_ctrls_fol = needs[4]
            self.top_ctrls = needs[5]

        if self.model.bot_creation_switch:
            needs = self.create_ribbons("bot", self.bot_components_type, self.bot_components, self.model.how_many_bot_ctrls)
            self.bot_skn_jnts = needs[0]
            self.bot_surface = needs[1]
            self.bot_follicles = needs[2]
            self.bot_ctrls_jnt = needs[3]
            self.bot_ctrls_fol = needs[4]
            self.bot_ctrls = needs[5]

        if self.model.top_creation_switch and self.model.bot_creation_switch:
            self.create_corner_ctrls()

        self.clean_rig()
        pmc.select(cl=1)

    def create_ribbons(self, side, components_type, selection, how_many_ctrls):
        if components_type != "face":
            if components_type == "edge":
                vertices_from_selection = pmc.polyListComponentConversion(selection, fromEdge=1, toVertex=1)
                vertices = pmc.ls(vertices_from_selection, flatten=1)

                vertices_from_first_edge = pmc.ls(pmc.polyListComponentConversion(selection[0], fromEdge=1, toVertex=1), flatten=1)

                edges_from_point = pmc.ls(pmc.polyListComponentConversion(vertices_from_first_edge[0], fromVertex=1, toEdge=1), flatten=1)
                vertices_from_edges = pmc.ls(pmc.polyListComponentConversion(edges_from_point, toVertex=1, fromEdge=1, border=1), flatten=1)
                next_vertex = [vertex for vertex in vertices_from_edges if vertex in vertices]
                if len(next_vertex) == 1:
                    first_vertex = pmc.ls(vertices_from_first_edge[0])[0]
                else:
                    first_vertex = pmc.ls(vertices_from_first_edge[1])[0]

                vertices.remove(first_vertex)
                vertices.insert(0, first_vertex)

            else:
                vertices = selection

            ordered_vertices = rig_lib.continuous_check_and_reorder_vertex_list(vertices, self.model.module_name)

            vertices_world_pos = []
            skn_jnts = []
            for i, vertex in enumerate(ordered_vertices):
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

            pmc.parent(surface, self.parts_grp)

            self.jnts_to_skin.append(skn_jnts)

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
                pmc.parent(follicle, self.jnt_input_grp)

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

            if how_many_ctrls == "7":
                ctrl_jnts_pos.setAttr("parameterV", 0.3)
            else:
                ctrl_jnts_pos.setAttr("parameterV", 0.25)
            pmc.refresh()
            start_mid_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

            ctrl_jnts_pos.setAttr("parameterV", 0.5)
            pmc.refresh()
            mid_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

            if how_many_ctrls == "7":
                ctrl_jnts_pos.setAttr("parameterV", 0.7)
            else:
                ctrl_jnts_pos.setAttr("parameterV", 0.75)
            pmc.refresh()
            mid_end_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

            ctrl_jnts_pos.setAttr("parameterV", 1.0)
            pmc.refresh()
            end_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

            if how_many_ctrls == "7":
                pmc.select(cl=1)
                start_quarter_jnt = pmc.joint(p=(0, 0, 0), n="{0}_{1}_start_quarter_JNT".format(self.model.module_name, side))
                start_quarter_jnt.setAttr("radius", 0.2)
                pmc.select(cl=1)
                quarter_end_jnt = pmc.joint(p=(0, 0, 0), n="{0}_{1}_quarter_end_JNT".format(self.model.module_name, side))
                quarter_end_jnt.setAttr("radius", 0.2)

                ctrl_jnts_pos.setAttr("parameterV", 0.15)
                pmc.refresh()
                start_quarter_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

                ctrl_jnts_pos.setAttr("parameterV", 0.85)
                pmc.refresh()
                quarter_end_jnt.setAttr("translate", ctrl_jnts_pos.getAttr("position"))

                ctrls_jnt = [start_jnt, start_quarter_jnt, start_mid_jnt, mid_jnt, mid_end_jnt, quarter_end_jnt, end_jnt]
            else:
                ctrls_jnt = [start_jnt, start_mid_jnt, mid_jnt, mid_end_jnt, end_jnt]

            pmc.delete(ctrl_jnts_pos)

            ctrls = []
            ctrls_fol = []
            for jnt in ctrls_jnt:
                if side == "bot":
                    jnt.setAttr("jointOrientX", 180)

                if jnt.getAttr("translateX") < -0.05:
                    jnt.setAttr("jointOrientY", 180)

                follicle_shape = pmc.createNode("follicle", n=str(jnt).replace("_JNT", "_FOLShape"))
                follicle = follicle_shape.getParent()
                follicle.rename(str(jnt).replace("_JNT", "_FOL"))

                follicle_shape.outTranslate >> follicle.translate
                follicle_shape.outRotate >> follicle.rotate
                self.mesh_to_follow.getShape().outMesh >> follicle_shape.inputMesh
                self.mesh_to_follow.getShape().worldMatrix[0] >> follicle_shape.inputWorldMatrix

                point_on_mesh = pmc.createNode("closestPointOnMesh", n=str(jnt) + "CPM")
                self.mesh_to_follow.getShape().outMesh >> point_on_mesh.inMesh
                point_on_mesh.setAttr("inPosition", pmc.xform(jnt, q=1, ws=1, translation=1))

                follicle_shape.setAttr("parameterU", point_on_mesh.getAttr("parameterU"))
                follicle_shape.setAttr("parameterV", point_on_mesh.getAttr("parameterV"))

                pmc.delete(point_on_mesh)
                ctrls_fol.append(follicle)

                pmc.select(clear=1)
                ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=0.5, d=3, s=8,
                                        n=str(jnt).replace("_JNT", "_ctrl_Shape"), ch=0)[0]
                ctrl = rig_lib.create_jnttype_ctrl(name=str(jnt).replace("_JNT", "_CTRL"), shape=ctrl_shape)

                pmc.select(clear=1)
                ctrl_ofs = pmc.joint(p=(0, 0, 0), n=str(ctrl).replace("_CTRL", "_ctrl_OFS"))
                ctrl_ofs.setAttr("drawStyle", 2)

                ctrl_fix_r = pmc.joint(p=(0, 0, 0), n=str(ctrl).replace("_CTRL", "_ctrl_rotate_FIX"))
                ctrl_fix_r.setAttr("drawStyle", 2)
                ctrl_fix_r.setAttr("rotateOrder", 5)

                ctrl_fix_t = pmc.joint(p=(0, 0, 0), n=str(ctrl).replace("_CTRL", "_ctrl_translate_FIX"))
                ctrl_fix_t.setAttr("drawStyle", 2)

                pmc.parent(ctrl, ctrl_fix_t)
                pmc.parent(ctrl_ofs, follicle)

                ctrl_ofs.setAttr("translate", (0, 0, 0))
                ctrl_ofs.setAttr("rotate", (0, 0, 0))
                ctrl_ofs.setAttr("jointOrient", (0, 0, 0))

                ctrl_ofs_orientation_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_orientation_LOC".format(ctrl_ofs))
                pmc.parent(ctrl_ofs_orientation_loc, jnt, r=1)
                pmc.parent(ctrl_ofs_orientation_loc, follicle, r=0)
                ctrl_ofs.setAttr("jointOrient", ctrl_ofs_orientation_loc.getAttr("rotate"))
                pmc.delete(ctrl_ofs_orientation_loc)

                invert_ctrl_translate = pmc.createNode("multiplyDivide", n=str(ctrl) + "invert_translate_MDL")
                invert_ctrl_rotate = pmc.createNode("multiplyDivide", n=str(ctrl) + "invert_rotate_MDL")

                ctrl.translate >> invert_ctrl_translate.input1
                invert_ctrl_translate.setAttr("input2", (-1, -1, -1))
                invert_ctrl_translate.output >> ctrl_fix_t.translate

                ctrl.rotate >> invert_ctrl_rotate.input1
                invert_ctrl_rotate.setAttr("input2", (-1, -1, -1))
                invert_ctrl_rotate.output >> ctrl_fix_r.rotate

                ctrl_cvs = ctrl.cv[:]
                for cv in ctrl_cvs:
                    pmc.move(cv, 0.5, moveZ=1, ws=1, wd=1, r=1)
                    pmc.move(cv, 0.1, moveY=1, ls=1, wd=1, r=1)

                jnt_ofs = pmc.duplicate(jnt, n=str(jnt).replace("_JNT", "_jnt_OFS"))[0]
                jnt_ofs.setAttr("drawStyle", 2)
                pmc.parent(jnt, jnt_ofs)

                ctrl.translate >> jnt.translate
                ctrl.rotate >> jnt.rotate
                ctrl.scale >> jnt.scale

                ctrls.append(ctrl)

                pmc.parent(jnt_ofs, self.parts_grp)
                pmc.parent(follicle, self.ctrl_input_grp)

            pmc.select(cl=1)
            pmc.skinCluster(ctrls_jnt, surface, bm=0, dr=4.0, mi=2, nw=1, sm=0, tsb=1, wd=0)

            return skn_jnts, surface, follicles, ctrls_jnt, ctrls_fol, ctrls
        else:
            pmc.error("faces aren't support yet")

    def create_corner_ctrls(self):
        distance = pmc.createNode("distanceBetween")

        self.top_ctrls_jnt[0].getParent().translate >> distance.point1
        self.bot_ctrls_jnt[0].getParent().translate >> distance.point2
        topstart_botstart_dist = distance.getAttr("distance")

        self.bot_ctrls_jnt[0].getParent().translate // distance.point2
        self.bot_ctrls_jnt[-1].getParent().translate >> distance.point2
        topstart_botend_dist = distance.getAttr("distance")

        pmc.delete(distance)

        if topstart_botstart_dist < topstart_botend_dist:
            side1_jnts = [self.top_ctrls_jnt[0], self.bot_ctrls_jnt[0]]
            side1_ctrls = [self.top_ctrls[0], self.bot_ctrls[0]]
            side2_jnts = [self.top_ctrls_jnt[-1], self.bot_ctrls_jnt[-1]]
            side2_ctrls = [self.top_ctrls[-1], self.bot_ctrls[-1]]
        else:
            side1_jnts = [self.top_ctrls_jnt[0], self.bot_ctrls_jnt[-1]]
            side1_ctrls = [self.top_ctrls[0], self.bot_ctrls[-1]]
            side2_jnts = [self.top_ctrls_jnt[-1], self.bot_ctrls_jnt[0]]
            side2_ctrls = [self.top_ctrls[-1], self.bot_ctrls[0]]

        pmc.select(cl=1)
        side1_master_ofs = pmc.joint(p=(0, 0, 0), n="{0}_corner_01_jnt_OFS".format(self.model.module_name))
        side1_master_jnt = pmc.joint(p=(0, 0, 0), n="{0}_corner_01_JNT".format(self.model.module_name))
        pmc.select(cl=1)
        side2_master_ofs = pmc.joint(p=(0, 0, 0), n="{0}_corner_02_jnt_OFS".format(self.model.module_name))
        side2_master_jnt = pmc.joint(p=(0, 0, 0), n="{0}_corner_02_JNT".format(self.model.module_name))
        side1_master_ofs.setAttr("drawStyle", 2)
        side2_master_ofs.setAttr("drawStyle", 2)
        side1_master_jnt.setAttr("radius", 0.5)
        side2_master_jnt.setAttr("radius", 0.5)

        side1_master_ofs.setAttr("translate",
                                 ((side1_jnts[0].getParent().getAttr("translateX") + side1_jnts[-1].getParent().getAttr("translateX")) / 2,
                                  (side1_jnts[0].getParent().getAttr("translateY") + side1_jnts[-1].getParent().getAttr("translateY")) / 2,
                                  (side1_jnts[0].getParent().getAttr("translateZ") + side1_jnts[-1].getParent().getAttr("translateZ")) / 2,))

        side2_master_ofs.setAttr("translate",
                                 ((side2_jnts[0].getParent().getAttr("translateX") + side2_jnts[-1].getParent().getAttr("translateX")) / 2,
                                  (side2_jnts[0].getParent().getAttr("translateY") + side2_jnts[-1].getParent().getAttr("translateY")) / 2,
                                  (side2_jnts[0].getParent().getAttr("translateZ") + side2_jnts[-1].getParent().getAttr("translateZ")) / 2,))

        if side1_master_ofs.getAttr("translateX") < -0.05:
            side1_master_ofs.setAttr("jointOrientY", 180)
        elif side2_master_ofs.getAttr("translateX") < -0.05:
            side2_master_ofs.setAttr("jointOrientY", 180)

        pmc.parent(side1_jnts[0].getParent(), side1_master_jnt)
        pmc.parent(side1_jnts[-1].getParent(), side1_master_jnt)
        pmc.parent(side2_jnts[0].getParent(), side2_master_jnt)
        pmc.parent(side2_jnts[-1].getParent(), side2_master_jnt)

        self.sides_master_jnts = [side1_master_jnt, side2_master_jnt]

        self.sides_ctrls = []
        self.sides_ctrls_fol = []
        for jnt in self.sides_master_jnts:
            follicle_shape = pmc.createNode("follicle", n=str(jnt).replace("_JNT", "_FOLShape"))
            follicle = follicle_shape.getParent()
            follicle.rename(str(jnt).replace("_JNT", "_FOL"))

            follicle_shape.outTranslate >> follicle.translate
            follicle_shape.outRotate >> follicle.rotate
            self.mesh_to_follow.getShape().outMesh >> follicle_shape.inputMesh
            self.mesh_to_follow.getShape().worldMatrix[0] >> follicle_shape.inputWorldMatrix

            point_on_mesh = pmc.createNode("closestPointOnMesh", n=str(jnt) + "CPM")
            self.mesh_to_follow.getShape().outMesh >> point_on_mesh.inMesh
            point_on_mesh.setAttr("inPosition", pmc.xform(jnt, q=1, ws=1, translation=1))

            follicle_shape.setAttr("parameterU", point_on_mesh.getAttr("parameterU"))
            follicle_shape.setAttr("parameterV", point_on_mesh.getAttr("parameterV"))

            pmc.delete(point_on_mesh)
            self.sides_ctrls_fol.append(follicle)

            pmc.select(clear=1)
            ctrl_shape = pmc.circle(c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=0.8, d=3, s=8,
                                    n=str(jnt).replace("_JNT", "_ctrl_Shape"), ch=0)[0]
            ctrl = rig_lib.create_jnttype_ctrl(name=str(jnt).replace("_JNT", "_CTRL"), shape=ctrl_shape)

            pmc.select(clear=1)
            ctrl_ofs = pmc.joint(p=(0, 0, 0), n=str(ctrl).replace("_CTRL", "_ctrl_OFS"))
            ctrl_ofs.setAttr("drawStyle", 2)

            ctrl_fix_r = pmc.joint(p=(0, 0, 0), n=str(ctrl).replace("_CTRL", "_ctrl_rotate_FIX"))
            ctrl_fix_r.setAttr("drawStyle", 2)
            ctrl_fix_r.setAttr("rotateOrder", 5)

            ctrl_fix_t = pmc.joint(p=(0, 0, 0), n=str(ctrl).replace("_CTRL", "_ctrl_translate_FIX"))
            ctrl_fix_t.setAttr("drawStyle", 2)

            pmc.parent(ctrl, ctrl_fix_t)
            pmc.parent(ctrl_ofs, follicle)

            ctrl_ofs.setAttr("translate", (0, 0, 0))
            ctrl_ofs.setAttr("rotate", (0, 0, 0))
            ctrl_ofs.setAttr("jointOrient", (0, 0, 0))

            ctrl_ofs_orientation_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_orientation_LOC".format(ctrl_ofs))
            pmc.parent(ctrl_ofs_orientation_loc, jnt, r=1)
            pmc.parent(ctrl_ofs_orientation_loc, follicle, r=0)
            ctrl_ofs.setAttr("jointOrient", ctrl_ofs_orientation_loc.getAttr("rotate"))
            pmc.delete(ctrl_ofs_orientation_loc)

            invert_ctrl_translate = pmc.createNode("multiplyDivide", n=str(ctrl) + "invert_translate_MDL")
            invert_ctrl_rotate = pmc.createNode("multiplyDivide", n=str(ctrl) + "invert_rotate_MDL")

            ctrl.translate >> invert_ctrl_translate.input1
            invert_ctrl_translate.setAttr("input2", (-1, -1, -1))
            invert_ctrl_translate.output >> ctrl_fix_t.translate

            ctrl.rotate >> invert_ctrl_rotate.input1
            invert_ctrl_rotate.setAttr("input2", (-1, -1, -1))
            invert_ctrl_rotate.output >> ctrl_fix_r.rotate

            ctrl_cvs = ctrl.cv[:]
            for cv in ctrl_cvs:
                pmc.move(cv, 0.5, moveZ=1, ws=1, wd=1, r=1)

            ctrl.translate >> jnt.translate
            ctrl.rotate >> jnt.rotate
            ctrl.scale >> jnt.scale

            self.sides_ctrls.append(ctrl)

            ctrl.addAttr("cornerSecondaryCtrls", attributeType="bool", defaultValue=0, hidden=0, keyable=1)

            pmc.parent(jnt.getParent(), self.parts_grp)
            pmc.parent(follicle, self.ctrl_input_grp)

        self.sides_ctrls[0].cornerSecondaryCtrls >> side1_ctrls[0].visibility
        self.sides_ctrls[0].cornerSecondaryCtrls >> side1_ctrls[-1].visibility
        self.sides_ctrls[-1].cornerSecondaryCtrls >> side2_ctrls[0].visibility
        self.sides_ctrls[-1].cornerSecondaryCtrls >> side2_ctrls[-1].visibility

    def clean_rig(self):
        self.jnt_input_grp.setAttr("visibility", 0)
        self.parts_grp.setAttr("visibility", 0)

        all_ctrls = self.top_ctrls + self.bot_ctrls + self.sides_ctrls
        all_fol = self.top_ctrls_fol + self.bot_ctrls_fol + self.sides_ctrls_fol

        for i, ctrl in enumerate(all_ctrls):
            if all_fol[i].getAttr("translateX") > 0.02:
                color_value = 6
            elif all_fol[i].getAttr("translateX") < -0.02:
                color_value = 13
            else:
                color_value = 14

            all_fol[i].getShape().setAttr("visibility", 0)

            rig_lib.clean_ctrl(ctrl, color_value, trs="s")
            rig_lib.clean_ctrl(ctrl.getParent(), color_value, trs="trs")
            rig_lib.clean_ctrl(ctrl.getParent().getParent(), color_value, trs="trs")
            rig_lib.clean_ctrl(ctrl.getParent().getParent().getParent(), color_value, trs="trs")

        if not pmc.objExists("facial_jnts_to_SKN_SET"):
            skn_set = pmc.createNode("objectSet", n="facial_jnts_to_SKN_SET")
        else:
            skn_set = pmc.ls("facial_jnts_to_SKN_SET", type="objectSet")[0]
        for jnt in self.jnts_to_skin:
            if type(jnt) == list:
                for obj in jnt:
                    skn_set.add(obj)
            else:
                skn_set.add(jnt)

    def connect_to_parent(self):
        check_list = ["CTRL_GRP", "JNT_GRP", "PARTS_GRP"]
        if not rig_lib.exists_check(check_list):
            print("No necessary groups created for module {0}".format(self.model.module_name))
            return

        self.jnt_input_grp = pmc.group(em=1, n="{0}_jnt_INPUT".format(self.model.module_name))
        self.ctrl_input_grp = pmc.group(em=1, n="{0}_ctrl_INPUT".format(self.model.module_name))
        self.parts_grp = pmc.group(em=1, n="{0}_parts_INPUT".format(self.model.module_name))

        pmc.parent(self.jnt_input_grp, "JNT_GRP", r=1)
        pmc.parent(self.parts_grp, "PARTS_GRP", r=1)
        pmc.parent(self.ctrl_input_grp, "CTRL_GRP", r=1)


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
        self.how_many_top_ctrls = "5"
        self.how_many_bot_ctrls = "5"
