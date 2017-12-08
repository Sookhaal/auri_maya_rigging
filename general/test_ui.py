from PySide2 import QtWidgets, QtCore, QtGui

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, is_checked, grpbox
from auri.scripts.Maya_Scripts import rig_lib
from auri.scripts.Maya_Scripts.rig_lib import RigController

reload(rig_lib)


class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        self.refresh_spaces_btn = QtWidgets.QPushButton("Refresh")
        self.add_space_btn = QtWidgets.QPushButton("Add")
        self.remove_space_btn = QtWidgets.QPushButton("Remove")
        self.prebuild_btn = QtWidgets.QPushButton("Prebuild")
        self.space_modules_cbbox = QtWidgets.QComboBox()
        self.spaces_cbbox = QtWidgets.QComboBox()
        self.selected_space_module = "No_space_module"
        self.selected_space = "no_space"
        self.space_list_view = QtWidgets.QListView()
        self.space_list = QtGui.QStringListModel()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.space_list.setStringList(self.model.space_list)
        self.ctrl.look_for_parent(l_cbbox_stringlist=self.ctrl.modules_with_spaces, l_cbbox_selection=self.selected_space_module,
                                  l_cbbox=self.space_modules_cbbox, r_cbbox_stringlist=self.ctrl.spaces_model,
                                  r_cbbox_selection=self.selected_space, r_cbbox=self.spaces_cbbox)

    def setup_ui(self):
        self.space_modules_cbbox.setModel(self.ctrl.modules_with_spaces)
        self.space_modules_cbbox.currentTextChanged.connect(self.ctrl.on_space_modules_cbbox_changed)

        self.spaces_cbbox.setModel(self.ctrl.spaces_model)
        self.spaces_cbbox.currentTextChanged.connect(self.ctrl.on_spaces_cbbox_changed)

        self.space_list_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.space_list.setStringList(self.model.space_list)
        self.space_list_view.setModel(self.space_list)

        self.add_space_btn.clicked.connect(self.ctrl.add_space_to_list)
        self.remove_space_btn.clicked.connect(self.ctrl.remove_space_from_list)

        self.refresh_spaces_btn.clicked.connect(self.ctrl.look_for_spaces)
        self.prebuild_btn.clicked.connect(self.ctrl.prebuild)

        main_layout = QtWidgets.QVBoxLayout()

        select_spaces_layout = QtWidgets.QVBoxLayout()
        select_spaces_grp = grpbox("Select local spaces :", select_spaces_layout)
        spaces_cbbox_layout = QtWidgets.QHBoxLayout()
        spaces_cbbox_layout.addWidget(self.space_modules_cbbox)
        spaces_cbbox_layout.addWidget(self.spaces_cbbox)
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.addWidget(self.refresh_spaces_btn)
        btn_layout.addWidget(self.add_space_btn)
        select_spaces_layout.addLayout(spaces_cbbox_layout)
        select_spaces_layout.addLayout(btn_layout)

        space_list_layout = QtWidgets.QVBoxLayout()
        space_list_grp = grpbox("local spaces :", space_list_layout)
        space_list_layout.addWidget(self.space_list_view)
        space_list_layout.addWidget(self.remove_space_btn)

        main_layout.addWidget(select_spaces_grp)
        main_layout.addWidget(space_list_grp)
        main_layout.addWidget(self.prebuild_btn)
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
        print self.model.space_list

        self.view.refresh_view()
        pmc.select(d=1)

    def execute(self):
        self.prebuild()

    def create_local_spaces(self):
        parent_spaces = pmc.ls(regex="{0}_ctrl_INPUT\|.*end_OUTPUT$".format(self.model.selected_module))
        spine_start_space = (pmc.ls(regex="{0}_ctrl_INPUT\|.*1_fk_CTRL$".format(self.model.selected_module)))
        spaces = ["World", "Shoulder", "{0}_fk_start".format(self.model.selected_module)]
        world_space_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_world_SPACELOC".format(self.model.module_name))
        shoulder_space_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_shoulder_SPACELOC".format(self.model.module_name))
        spine_start_space_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_spine_fk_start_SPACELOC".format(self.model.module_name))
        space_locs = [world_space_loc, shoulder_space_loc, spine_start_space_loc]
        for space in parent_spaces:
            name = str(space)
            name = name.replace("_OUTPUT", "")
            spaces.append(name)
            space_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_{1}_SPACELOC".format(self.model.module_name, name))
            space_locs.append(space_loc)

        self.created_fk_ctrls[0].addAttr("space", attributeType="enum", enumName=spaces, hidden=0, keyable=1)
        self.created_ik_ctrls[0].addAttr("space", attributeType="enum", enumName=spaces, hidden=0, keyable=1)

        for loc in space_locs:
            loc.setAttr("translate", pmc.xform(self.created_skn_jnts[0], q=1, ws=1, translation=1))

        pmc.parent(space_locs[0], pmc.ls(regex=".*_local_CTRL$")[0])
        pmc.parent(space_locs[1], self.clavicle_ik_ctrl)
        pmc.parent(space_locs[2], spine_start_space)
        for i, space in enumerate(parent_spaces):
            pmc.parent(space_locs[i+3], space)

        fk_space_const = pmc.orientConstraint(space_locs[0], self.created_fk_ctrls[0].getParent(), maintainOffset=1)
        ik_space_const = pmc.parentConstraint(space_locs[0], self.created_ik_ctrls[0].getParent(), maintainOffset=1)
        pmc.orientConstraint(space_locs[1], self.created_fk_ctrls[0].getParent(), maintainOffset=1)
        pmc.parentConstraint(space_locs[1], self.created_ik_ctrls[0].getParent(), maintainOffset=1)
        pmc.orientConstraint(space_locs[2], self.created_fk_ctrls[0].getParent(), maintainOffset=1)
        pmc.parentConstraint(space_locs[2], self.created_ik_ctrls[0].getParent(), maintainOffset=1)
        for i, space in enumerate(parent_spaces):
            pmc.orientConstraint(space_locs[i+3], self.created_fk_ctrls[0].getParent(), maintainOffset=1)
            pmc.parentConstraint(space_locs[i+3], self.created_ik_ctrls[0].getParent(), maintainOffset=1)

        rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(fk_space_const, space_locs[0], 0),
                                             self.created_fk_ctrls[0].space, 0,
                                             "{0}_worldSpace_COND".format(self.created_fk_ctrls[0]))
        rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(ik_space_const, space_locs[0], 0),
                                             self.created_ik_ctrls[0].space, 0,
                                             "{0}_worldSpace_COND".format(self.created_ik_ctrls[0]))

        rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(fk_space_const, space_locs[1], 1),
                                             self.created_fk_ctrls[0].space, 1,
                                             "{0}_shoulderSpace_COND".format(self.created_fk_ctrls[0]))
        rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(ik_space_const, space_locs[1], 1),
                                             self.created_ik_ctrls[0].space, 1,
                                             "{0}_shoulderSpace_COND".format(self.created_ik_ctrls[0]))
        rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(fk_space_const, space_locs[2], 2),
                                                self.created_fk_ctrls[0].space, 2,
                                                "{0}_shoulderSpace_COND".format(self.created_fk_ctrls[0]))
        rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(ik_space_const, space_locs[2], 2),
                                                self.created_ik_ctrls[0].space, 2,
                                                "{0}_shoulderSpace_COND".format(self.created_ik_ctrls[0]))

        for i, space in enumerate(parent_spaces):
            name = str(space)
            name = name.replace("_OUTPUT", "Space")
            rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(fk_space_const, space_locs[i+3], i+3),
                                                    self.created_fk_ctrls[0].space, i+3,
                                                    "{0}_{1}_COND".format(self.created_fk_ctrls[0], name))
            rig_lib.connect_condition_to_constraint("{0}.{1}W{2}".format(ik_space_const, space_locs[i+3], i+3),
                                                    self.created_ik_ctrls[0].space, i+3,
                                                    "{0}_{1}_COND".format(self.created_ik_ctrls[0], name))


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.space_list = ["test", "test2"]
