from pymel import core as pmc

pmc.loadPlugin("matrixNodes", qt=1)


def square_arrow_curve(name):
    crv = pmc.curve(d=1, p=[(-5, 0, -5), (-2, 0, -5), (-2, 0, -7), (-3, 0, -7), (0, 0, -9), (3, 0, -7), (2, 0, -7),
                            (2, 0, -5),
                            (5, 0, -5), (5, 0, -2), (7, 0, -2), (7, 0, -3), (9, 0, 0), (7, 0, 3), (7, 0, 2), (5, 0, 2),
                            (5, 0, 5), (2, 0, 5), (2, 0, 7), (3, 0, 7), (0, 0, 9), (-3, 0, 7), (-2, 0, 7), (-2, 0, 5),
                            (-5, 0, 5), (-5, 0, 2), (-7, 0, 2), (-7, 0, 3), (-9, 0, 0), (-7, 0, -3), (-7, 0, -2),
                            (-5, 0, -2),
                            (-5, 0, -5)], n=name)
    return crv


def matrix_constraint(driver, driven, srt="srt"):
    """ Constraint one node to another using their worldMatrix attributes
        if doesn't work, check if plug-in "matrixNodes" is loaded
    """

    # define/create nodes
    mmlt = pmc.createNode("multMatrix", name=driven + "_multMatrix")
    mdcp = pmc.createNode("decomposeMatrix", name=driven + "_decomposeMatrix")

    if driver.type() == "choice":
        driver.output >> mmlt.matrixIn[0]
    else:
        driver.worldMatrix[0] >> mmlt.matrixIn[0]

    driven.parentInverseMatrix[0] >> mmlt.matrixIn[1]
    mmlt.matrixSum >> mdcp.inputMatrix

    for attr in [x + y for x in srt.lower() for y in "xyz"]:
        mdcp.attr("o" + attr) >> driven.attr(attr)

    return mmlt, mdcp


def change_shape_color(selected, color):
    """ 2=dark_grey, 3=light_grey, 6=blue, 13=red 14=green 17=yellow """
    if isinstance(selected, list):
        for obj in selected:
            shape = obj.getShape()
            pmc.setAttr(shape + ".overrideEnabled", 1)
            pmc.setAttr(shape + ".overrideColor", color)
    else:
        shape = selected.getShape()
        pmc.setAttr(shape + ".overrideEnabled", 1)
        pmc.setAttr(shape + ".overrideColor", color)


def exists_check(objects):
    if isinstance(objects, (str, unicode)):
        if not pmc.objExists(objects):
            return False
        return True
    elif type(objects) == list:
        for obj in objects:
            if not pmc.objExists(obj):
                return False
        return True
    else:
        print("Wrong argument given to exists_check fonction")


def list_children(group):
    return [obj.nodeName() for obj in pmc.listRelatives(group, children=1)]


def cbbox_set_selected(selected, cbbox):
    if selected is not None and cbbox.findText(selected) != -1:
        cbbox.setCurrentText(selected)
    else:
        cbbox.setCurrentIndex(0)
        selected = cbbox.currentText()
    return selected


def create_curve_guide(d, number_of_points, name, hauteur_curve=10):
        crv = pmc.curve(d=1, p=[(0, 0, 0), (hauteur_curve, 0, 0)], k=[0, 1])
        crv.setAttr("rotate", (-90, 0, 90))
        crv_rebuilded = pmc.rebuildCurve(crv, rpo=0, rt=0, end=1, kr=0, kep=1, kt=0, s=(number_of_points-1),
                                         d=d, ch=0, replaceOriginal=1)[0]
        crv_rebuilded.rename(name)
        return crv_rebuilded


def create_jnts_from_cv_list_and_return_jnts_list(vertex_list, guide, module_name):
    pmc.select(d=1)
    created_jnts_list = []
    for i, vertex in enumerate(vertex_list):
        if i == 0:
            jnt = pmc.joint(p=(pmc.xform(vertex, q=1, ws=1, translation=1)),
                            o=(pmc.xform(guide, q=1, ws=1, rotation=1)),
                            n="{0}_{1}_JNT".format(module_name, i), rad=0.5)
        else:
            jnt = pmc.joint(p=(pmc.xform(vertex, q=1, ws=1, translation=1)),
                            n="{0}_{1}_JNT".format(module_name, i), rad=0.5)
        created_jnts_list.append(jnt)
    created_jnts_list[-1].rename("{0}_end_JNT".format(module_name))
    return created_jnts_list


def change_jnt_chain_suffix(jnts_chain, new_suffix):
    for jnt in jnts_chain:
        if jnt != jnts_chain[-1]:
            jnt_name = jnt.name().rsplit("|")[-1]
            split_name = jnt_name.rsplit("_")
            split_name.pop(-1)
            new_suffix_list = [new_suffix]
            new_name = "_".join(split_name + new_suffix_list)
            jnt.rename(new_name)
