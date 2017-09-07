from PySide2 import QtWidgets, QtCore

from pymel import core as pmc

from auri.auri_lib import AuriScriptView, AuriScriptController, AuriScriptModel, grpbox
from auri.scripts.Maya_Scripts import rig_lib
from auri.scripts.Maya_Scripts.rig_lib import RigController

reload(rig_lib)


class View(AuriScriptView):
    def __init__(self, *args, **kwargs):
        self.how_many_ctrls = QtWidgets.QSpinBox()
        super(View, self).__init__(*args, **kwargs)

    def set_controller(self):
        self.ctrl = Controller(self.model, self)

    def set_model(self):
        self.model = Model()

    def refresh_view(self):
        self.how_many_ctrls.setValue(self.model.how_many_ctrls)

    def setup_ui(self):
        text = QtWidgets.QLabel("Select a curve to rig")

        self.how_many_ctrls.setMinimum(1)
        self.how_many_ctrls.valueChanged.connect(self.ctrl.on_how_many_ctrls_changed)

        main_layout = QtWidgets.QVBoxLayout()

        options_layout = QtWidgets.QVBoxLayout()
        options_grp = grpbox("Options", options_layout)

        ctrls_layout = QtWidgets.QVBoxLayout()
        ctrls_text = QtWidgets.QLabel("How many ctrls :")
        ctrls_layout.addWidget(ctrls_text)
        ctrls_layout.addWidget(self.how_many_ctrls)

        options_layout.addLayout(ctrls_layout)

        main_layout.addWidget(text)
        text.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(options_grp)
        self.setLayout(main_layout)


class Controller(RigController):
    def __init__(self, model, view):
        """

        Args:
            model (Model):
            view (View):
        """
        self.curves_to_rig = None
        self.created_locs = []
        self.created_ctrls = []
        RigController.__init__(self,  model, view)

    def prebuild(self):
        self.curves_to_rig = pmc.ls(sl=1)

    def execute(self):
        self.prebuild()

        if type(self.curves_to_rig) == list:
            if rig_lib.exists_check("{0}_rig_GRP".format(self.curves_to_rig[0].name())):
                pmc.delete("{0}_rig_GRP".format(self.curves_to_rig[0].name()))
            group = pmc.group(em=1, n="{0}_rig_GRP".format(self.curves_to_rig[0].name()))
            for obj in self.curves_to_rig:
                if rig_lib.exists_check("{0}_1_fk_ctrl_OFS".format(obj.name())):
                    pmc.delete("{0}_1_fk_ctrl_OFS".format(obj.name()))

                if pmc.nodeType(obj.getShape()) == "nurbsCurve":
                    self.rig_curve(obj)
                    pmc.parent(self.created_ctrls[0].getParent(), group, r=0)

                for ctrl in self.created_ctrls:
                    rig_lib.clean_ctrl(ctrl, 18, trs="ts")

        else:
            if rig_lib.exists_check("{0}_1_fk_ctrl_OFS".format(self.curves_to_rig.name())):
                pmc.delete("{0}_1_fk_ctrl_OFS".format(self.curves_to_rig.name()))

            self.rig_curve()

            for ctrl in self.created_ctrls:
                rig_lib.clean_ctrl(ctrl, 18, trs="ts")

        pmc.select(d=1)

    def rig_curve(self, selection=None):
        if selection is None:
            selection = self.curves_to_rig
        self.created_locs = []
        self.created_ctrls = []

        degree = selection.getShape().getAttr("degree")
        curve = pmc.rebuildCurve(selection, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0,
                                 s=self.model.how_many_ctrls, d=degree, ch=0, replaceOriginal=1)[0]

        ik_spline_cv_list = []
        for i, cv in enumerate(curve.cv):
            ik_spline_cv_list.append(cv)
        ik_spline_cv_for_ctrls = ik_spline_cv_list
        del ik_spline_cv_for_ctrls[1]
        del ik_spline_cv_for_ctrls[-2]

        ik_spline_controlpoints_list = []
        for i, cv in enumerate(curve.controlPoints):
            ik_spline_controlpoints_list.append(cv)
        ik_spline_controlpoints_for_ctrls = ik_spline_controlpoints_list[:]
        del ik_spline_controlpoints_for_ctrls[1]
        del ik_spline_controlpoints_for_ctrls[-2]

        for i, cv in enumerate(ik_spline_cv_for_ctrls):
            cv_loc = self.create_locators(i, cv, ik_spline_controlpoints_for_ctrls, selection.name())
            ctrl = self.create_ctrls(i, cv_loc, curve, selection.name())
            self.created_locs.append(cv_loc)
            self.created_ctrls.append(ctrl)

        self.constrain_ikspline_tan_to_ctrls(ik_spline_controlpoints_list, curve, selection.name())

        for i, ctrl in enumerate(self.created_ctrls):
            pmc.parent(self.created_locs[i], ctrl, r=0)

        curve.setAttr("translate", (0, 0, 0))
        curve.setAttr("rotate", (0, 0, 0))
        curve.setAttr("scale", (1, 1, 1))

    def create_locators(self, i, cv, ik_spline_controlpoints_for_ctrls, name):
        cv_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_loc{1}_pos".format(name, (i + 1)))
        cv_loc.setAttr("translate", pmc.xform(cv, q=1, ws=1, translation=1))
        cv_loc_shape = cv_loc.getShape()
        cv_loc_shape.worldPosition >> ik_spline_controlpoints_for_ctrls[i]
        cv_loc.setAttr("visibility", 0)
        return cv_loc

    def create_ctrls(self, i, cv_loc, curve, name):
        ctrl = pmc.circle(c=(0, 0, 0), nr=(1, 0, 0), sw=360, r=0.05, d=3, s=8,
                          n="{0}_{1}_fk_CTRL".format(name, (i + 1)), ch=0)[0]
        ctrl_ofs = pmc.group(ctrl, n="{0}_{1}_fk_ctrl_OFS".format(name, (i + 1)))
        value = 1.0 / self.model.how_many_ctrls * i
        ctrl_ofs.setAttr("translate", curve.getPointAtParam(value, space="world"))
        if i != 0:
            const = pmc.aimConstraint(ctrl_ofs, "{0}_{1}_fk_ctrl_OFS".format(name, i), maintainOffset=0,
                                      aimVector=(1.0, 0.0, 0.0), upVector=(0.0, 0.0, 1.0), worldUpType="vector",
                                      worldUpVector=(-1.0, 0.0, 0.0))
            pmc.delete(const)
            if i == (self.model.how_many_ctrls - 1):
                const = pmc.aimConstraint(cv_loc, ctrl_ofs, maintainOffset=0,
                                          aimVector=(1.0, 0.0, 0.0), upVector=(0.0, 0.0, 1.0), worldUpType="vector",
                                          worldUpVector=(-1.0, 0.0, 0.0))
                pmc.delete(const)
            pmc.parent(ctrl_ofs, "{0}_{1}_fk_CTRL".format(name, i), r=0)

        ctrl.setAttr("rotateOrder", 1)
        return ctrl

    def constrain_ikspline_tan_to_ctrls(self, ik_spline_controlpoints_list, curve, name):
        first_tan_cv_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_first_tan_pos".format(name))
        last_tan_cv_loc = pmc.spaceLocator(p=(0, 0, 0), n="{0}_last_tan_pos".format(name))
        first_tan_cv_loc.setAttr("translate", pmc.xform(curve.cv[1], q=1, ws=1, translation=1))
        last_tan_cv_loc.setAttr("translate", pmc.xform(curve.cv[-2], q=1, ws=1, translation=1))
        first_tan_cv_loc_shape = first_tan_cv_loc.getShape()
        last_tan_cv_loc_shape = last_tan_cv_loc.getShape()
        first_tan_cv_loc_shape.worldPosition >> curve.controlPoints[1]
        last_tan_cv_loc_shape.worldPosition >> curve.controlPoints[len(ik_spline_controlpoints_list) - 2]

        pmc.parent(first_tan_cv_loc, self.created_locs[0], r=0)
        pmc.parent(last_tan_cv_loc, self.created_locs[-1], r=0)

        first_tan_cv_loc_shape.setAttr("visibility", 0)
        last_tan_cv_loc_shape.setAttr("visibility", 0)


class Model(AuriScriptModel):
    def __init__(self):
        AuriScriptModel.__init__(self)
        self.how_many_ctrls = 4
