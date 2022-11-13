import nuke
import nukescripts
import nuke.rotopaint as rp
import _curvelib as cl


# CHECK IF NODES ARE SELECTED
def selectSomething(nodes):
    """Check if a camera or a rgb source is selected, if not, in main function it will return a nuke.message()

    :param nodes: dict of rgb source, camera, card
    :type nodes: dict
    :return: return what is selected
    :rtype: int
    """

    try:
        nodes["Cam"]
    except:
        return 1

    try:
        nodes["Source"]
    except:
        return 2

    return 0


# GET SELECTED NODES IN A LIST
def getNodes():
    """Add selected camera, card and source to a dictionnary

    :return: nodes
    :rtype: dict
    """
    sNodes = nuke.selectedNodes()

    nodes = {}

    for node in sNodes:
        if node.Class() == 'Camera2':
            nodes["Cam"] = node
        elif node.Class() == "Card2":
            nodes["Card"] = node
        elif node.Class() == 'Axis2':
            nodes['Axis'] = node
        else:
            nodes["Source"] = node

    if nuke.thisNode().Class() == 'Camera2':
        nodes["Cam"] = nuke.thisNode()

    return nodes


# GET SELECTED VERTEX
def getVerts():
    """Return selected vertices

    :return: verts
    :rtype: list
    """
    sel = nukescripts.snap3d.getSelection()
    verts = sel.points()

    return verts


# GET NUMBER OF VERTEX SELECTED
def getNumVerts(verts):
    """Get number of selected vertices

    :param verts: selected vertices
    :type verts: list
    :return: number of selected vertices
    :rtype: int
    """
    count = 0

    for vert in verts:
        count = count + 1

    return count


# CREATE RECONCILE NODES
def createReconcile(nodes, axis):
    """Create a reconcile node and set its input to the rgb source, camera and an axis

    :param nodes: dict of rgb source, camera, card
    :type nodes: dict
    :param axis: Axis node
    :type axis: Node
    :return: reconcile node
    :rtype: Node
    """
    reconcile = nuke.createNode("Reconcile3D")

    reconcile.setInput(0, nodes["Source"])
    reconcile.setInput(1, nodes["Cam"])
    reconcile.setInput(2, axis)

    return reconcile


def createAxis(vert):
    """Create an Axis node and set its translation to a selected vertex

    :param vert: selected vertex
    :type vert: Vector3
    :return: Axis node
    :rtype: Node
    """

    axis = nuke.createNode("Axis2")
    translate = axis["translate"]
    translate.setValue(vert)
    axis.setInput(0, None)

    return axis


# CREATE NODES
def createTracker(refFrame, nodes):
    """Create tracker node and place it next to camera or card (if it exist) in node graph

    :param refFrame: Reference frame
    :type refFrame: int
    :param nodes: dict of rgb source, camera, card
    :type nodes: dict
    :return: tracker node
    :rtype: Node
    """
    trackerN = nuke.createNode("Tracker3")
    trackerN['reference_frame'].setValue(float(refFrame))

    try:
        trackerN['xpos'].setValue(nodes['Card']['xpos'].value() + 100)
        trackerN['ypos'].setValue(nodes['Card']['ypos'].value())
    except:
        trackerN['xpos'].setValue(nodes['Cam']['xpos'].value() + 100)
        trackerN['ypos'].setValue(nodes['Cam']['ypos'].value())
    try:
        trackerN['xpos'].setValue(nodes['Axis']['xpos'].value() + 100)
        trackerN['ypos'].setValue(nodes['Axis']['ypos'].value())
    except:
        pass

    trackerN.setInput(0, None)

    return trackerN


def createCornerPin(nodes, trackerN):
    """Create CornerPin node and place it next to camera or card (if it exist) in node graph

    :param nodes: dict of rgb source, camera, card
    :type nodes: dict
    :param trackerN: tracker node
    :type trackerN: Node
    :return: cornerpin node
    :rtype: Node
    """

    cornerPin = nuke.createNode("CornerPin2D")
    cornerPin.setInput(0, None)

    try:
        cornerPin['ypos'].setValue(nodes['Card']['ypos'].value())
        cornerPin['xpos'].setValue(nodes['Card']['xpos'].value() + 400)
    except:
        cornerPin['ypos'].setValue(nodes['Cam']['ypos'].value())
        cornerPin['xpos'].setValue(nodes['Cam']['xpos'].value() + 400)
    try:
        cornerPin['ypos'].setValue(nodes['Axis']['ypos'].value())
        cornerPin['xpos'].setValue(nodes['Axis']['xpos'].value() + 400)
    except:
        pass

    return cornerPin


def createRotoNode(nodes, trackerN, layerName):
    """Create roto node and place it next to camera or card (if it exist) in node graph.
        Create the roto layer containing animation and name it

    :param nodes: dict of rgb source, camera, card
    :type nodes: dict
    :param trackerN: tracker node
    :type trackerN: Node
    :param layerName: Name that will have roto layer
    :type layerName: str
    :return: roto node
    :rtype: Node
    """
    rotoN = nuke.createNode('Roto')

    rotoN.setInput(0, None)

    try:
        rotoN['ypos'].setValue(nodes['Card']['ypos'].value())
        rotoN['xpos'].setValue(nodes['Card']['xpos'].value() + 200)
    except:
        rotoN['ypos'].setValue(nodes['Cam']['ypos'].value())
        rotoN['xpos'].setValue(nodes['Cam']['xpos'].value() + 200)
    try:
        rotoN['ypos'].setValue(nodes['Axis']['ypos'].value())
        rotoN['xpos'].setValue(nodes['Axis']['xpos'].value() + 200)
    except:
        pass

    cu = rotoN['curves']
    root = cu.rootLayer
    nLayer = rp.Layer(cu)
    root.append(nLayer)
    nLayer.name = layerName
    layer = cu.toElement(layerName)
    layerTransform = layer.getTransform()

    return rotoN, layerTransform


def createTransform(nodes, trackerN):
    """Create Transform node and place it next to camera or card (if it exist) in node graph.

    :param nodes: dict of rgb source, camera, card
    :type nodes: dict
    :param trackerN: tracker node
    :type trackerN: Node
    :return: Transform Node
    :rtype: Node
    """
    transformN = nuke.createNode("Transform")
    transformN.setInput(0, None)

    try:
        transformN['ypos'].setValue(nodes['Card']['ypos'].value())
        transformN['xpos'].setValue(nodes['Card']['xpos'].value() + 300)
    except:
        transformN['ypos'].setValue(nodes['Cam']['ypos'].value())
        transformN['xpos'].setValue(nodes['Cam']['xpos'].value() + 300)
        try:
            transformN['ypos'].setValue(nodes['Axis']['ypos'].value())
            transformN['xpos'].setValue(nodes['Axis']['xpos'].value() + 300)
        except:
            pass

    return transformN


# APPLY
def applyToRoto(rotoN, layerTransform, trackerN, vertNum, fFrame, lFrame):
    """Apply reconcile node's animation to roto layer

    :param rotoN: roto node
    :type rotoN: Node
    :param layerTransform: Transform knobs from a roto layer
    :type layerTransform: nuke.rotopaint.Layer.getTransform
    :param trackerN: tracker node
    :type trackerN: Node
    :param vertNum: number of vertices
    :type vertNum: int
    :param fFrame: first frame from framerange
    :type fFrame: int
    :param lFrame: last frame from framerange
    :type lFrame: int
    :return: None
    :rtype: None
    """
    transX = cl.AnimCurve()
    transY = cl.AnimCurve()

    trackerNodeName = trackerN.name()

    transX.expressionString = '{0}.translate.x'.format(trackerNodeName)
    transY.expressionString = '{0}.translate.y'.format(trackerNodeName)
    transX.useExpression = True
    transY.useExpression = True

    for f in xrange(fFrame, lFrame):
        transX.addKey(f, transX.evaluate(f))
        transY.addKey(f, transY.evaluate(f))

    layerTransform.setTranslationAnimCurve(0, transX)
    layerTransform.setTranslationAnimCurve(1, transY)
    layerTransform.getTranslationAnimCurve(0).expressionString = 'curve'
    layerTransform.getTranslationAnimCurve(1).expressionString = 'curve'

    if vertNum >= 2:

        # Rotation

        rot = cl.AnimCurve()

        rot.expressionString = '{0}.rotate'.format(trackerNodeName)
        rot.useExpression = True

        for f in xrange(fFrame, lFrame):
            rot.addKey(f, rot.evaluate(f))

        layerTransform.setRotationAnimCurve(2, rot)
        layerTransform.getRotationAnimCurve(2).expressionString = 'curve'

    if vertNum >= 3:

        # Scale

        scaleW = cl.AnimCurve()
        scaleH = cl.AnimCurve()

        scaleW.expressionString = '{0}.scale.w'.format(trackerNodeName)
        scaleH.expressionString = '{0}.scale.h'.format(trackerNodeName)
        scaleW.useExpression = True
        scaleH.useExpression = True

        for f in xrange(fFrame, lFrame):
            scaleW.addKey(f, scaleW.evaluate(f))
            scaleH.addKey(f, scaleH.evaluate(f))

        layerTransform.setScaleAnimCurve(0, scaleW)
        layerTransform.setScaleAnimCurve(1, scaleH)
        layerTransform.getScaleAnimCurve(0).expressionString = 'curve'
        layerTransform.getScaleAnimCurve(1).expressionString = 'curve'

    # Center

    centerx = cl.AnimCurve()
    centery = cl.AnimCurve()

    centerx.expressionString = '{0}.center.x'.format(trackerNodeName)
    centery.expressionString = '{0}.center.y'.format(trackerNodeName)
    centerx.useExpression = True
    centery.useExpression = True

    for f in xrange(fFrame, lFrame):
        centerx.addKey(f, centerx.evaluate(f))
        centery.addKey(f, centery.evaluate(f))

    layerTransform.setPivotPointAnimCurve(0, centerx)
    layerTransform.setPivotPointAnimCurve(1, centery)
    layerTransform.getPivotPointAnimCurve(0).expressionString = 'curve'
    layerTransform.getPivotPointAnimCurve(1).expressionString = 'curve'


def applyToTrack(reconcilen, num, trackerN):
    """Apply reconcile node's animation to tracker node, it will check check boxes based on number vertices

    :param reconcilen: reconcile node
    :type reconcilen: Node
    :param num: Number of vertices
    :type num: int
    :param trackerN: tracker node
    :type trackerN: Node
    :return: None
    :rtype: None
    """

    if num == 2:
        trackerN["enable2"].setValue(True)
        trackerN["use_for1"].setValue('T R')
        trackerN["use_for2"].setValue('T R')
    if num == 3:
        trackerN["enable3"].setValue(True)
        trackerN["use_for1"].setValue('all')
        trackerN["use_for2"].setValue('all')
        trackerN["use_for3"].setValue('all')
    if num == 4:
        trackerN["enable4"].setValue(True)
        trackerN["use_for4"].setValue('all')
    output = reconcilen['output']
    # SET ANIM ON ONE TRACKER
    track = trackerN['track{0}'.format(num)]
    outputAnimX = output.animation(0)
    outputAnimY = output.animation(1)
    track.copyAnimation(0, outputAnimX)
    track.copyAnimation(1, outputAnimY)


def applyToCornerPin(reconcilen, num, cornerPin, refFrame):
    """Apply reconcile node's animation to cornerpin node

    :param reconcilen: reconcile node
    :type reconcilen: Node
    :param num: number of vertices
    :type num: int
    :param cornerPin: cornerpin node
    :type cornerPin: Node
    :param refFrame: reference frame
    :type refFrame: int
    :return: None
    :rtype: None
    """

    # GENERATE RECONCILE NODE

    output = reconcilen['output']
    outputAnimX = output.animation(0)
    outputAnimY = output.animation(1)


    # SET ANIM ON CORNERPIN

    to = cornerPin["to{0}".format(num)]
    fromK = cornerPin["from{0}".format(num)]
    to.copyAnimation(0, outputAnimX)
    to.copyAnimation(1, outputAnimY)

    fromK.clearAnimated()
    fromK.setValue(to.valueAt(float(refFrame)))


def applyTransform(transformN, trackerN, vertnum):
    """Apply reconcile node's animation to Transform node

    :param transformN: Transform node
    :type transformN: Node
    :param trackerN: Tracker node
    :type trackerN: node
    :param vertnum: number of vertices
    :type vertnum: int
    :return: None
    :rtype: None
    """
    transTranslate = transformN['translate']
    transCenter = transformN['center']

    sourceT = trackerN['translate']
    sourceC = trackerN['center']

    # CENTER
    outputAnimX = sourceC.animation(0)
    outputAnimY = sourceC.animation(1)
    transCenter.copyAnimation(0, outputAnimX)
    transCenter.copyAnimation(1, outputAnimY)

    # TRANSLATE
    outputAnimX = sourceT.animation(0)
    outputAnimY = sourceT.animation(1)
    transTranslate.copyAnimation(0, outputAnimX)
    transTranslate.copyAnimation(1, outputAnimY)

    # ROTATE
    if vertnum >= 2:
        transRotate = transformN['rotate']
        sourceR = trackerN['rotate']
        outputAnimX = sourceR.animation(0)
        transRotate.copyAnimation(0, outputAnimX)

    # SCALE
    if vertnum >= 3:
        transScale = transformN['scale']
        sourceS = trackerN['scale']
        outputAnimX = sourceS.animation(0)
        transScale.copyAnimation(0, outputAnimX)


def createcopySetUp():
    """Create a 3D setup (copy of that card and axis on its corners) that will match selected card

    :return: dict of 3D setup nodes, dict of Axis nodes
    :rtype: dict, dict
    """
    copySetUp = {}

    axisDict = {}

    copyAxis = nuke.createNode("Axis2")
    copyAxis.setName("copyAxis")
    copyAxis.setInput(0, None)

    root = nuke.root()
    format = root.format()
    aspectRatio = format.width() / format.height()
    yValue = 0.5 / float(aspectRatio)

    axis1 = nuke.createNode("Axis2")
    axis1['translate'].setValue((0.5, yValue, 0))
    axis1.setInput(0, None)
    axis1.setInput(0, copyAxis)

    axis2 = nuke.createNode("Axis2")
    axis2['translate'].setValue((-0.5, yValue, 0))
    axis2.setInput(0, None)
    axis2.setInput(0, copyAxis)

    axis3 = nuke.createNode("Axis2")
    axis3['translate'].setValue((-0.5, -yValue, 0))
    axis3.setInput(0, None)
    axis3.setInput(0, copyAxis)

    axis4 = nuke.createNode("Axis2")
    axis4['translate'].setValue((0.5, -yValue, 0))
    axis4.setInput(0, None)
    axis4.setInput(0, copyAxis)

    copySetUp['copyAxis'] = copyAxis

    axisDict[0] = axis1
    axisDict[1] = axis2
    axisDict[2] = axis3
    axisDict[3] = axis4

    return copySetUp, axisDict


def matchOriginalCard(nodes, copySetUp):
    """Copy card and axis match selected card

    :param nodes: dict of rgb source, camera, card
    :type nodes: dict
    :param copySetUp: dict of 3D setup nodes
    :type copySetUp: dict
    """
    copySetUp["copyAxis"]['translate'].setValue(nodes["Card"]['translate'].value())
    copySetUp["copyAxis"]['rotate'].setValue(nodes["Card"]['rotate'].value())
    copySetUp["copyAxis"]['scaling'].setValue(nodes["Card"]['scaling'].value())

    copySetUp["copyAxis"]['uniform_scale'].setValue(nodes["Card"]['uniform_scale'].value())


def getVertexPanel(verts):
    """pop panel for vertex to track (card to track but with selected vertex

    :param verts: selected vertices
    :type verts: list
    :return: Panel
    :rtype: nuke.Panel()
    """
    panel = nuke.Panel('{0} Vertex to Track'.format(getNumVerts(verts)))

    panel.addEnumerationPulldown('Get nodes:', 'all "CornerPin (4 vertices or Card)" Transform Tracker Roto')
    panel.addEnumerationPulldown('Full SetUp', 'No Yes')
    panel.addSingleLineInput('FrameRange', "{0}-{1}".format(nuke.root().firstFrame(), nuke.root().lastFrame()))
    panel.addSingleLineInput('Ref Frame', nuke.frame())
    panel.addSingleLineInput('Roto layer name', "C2T")

    panel.setWidth(300)

    return panel


def getCardPanel():
    """pop panel for card to track

    :return: Panel
    :rtype: nuke.Panel()
    """

    panel = nuke.Panel('Card to Track')
    panel.addEnumerationPulldown('Get nodes:', 'all "CornerPin (4 vertices or Card)" Transform Tracker Roto')
    panel.addEnumerationPulldown('Full SetUp', 'No Yes')
    panel.addSingleLineInput('FrameRange', "{0}-{1}".format(nuke.root().firstFrame(), nuke.root().lastFrame()))
    panel.addSingleLineInput('Ref Frame', nuke.frame())
    panel.addSingleLineInput('Roto layer name', "C2T")
    panel.setWidth(300)

    return panel


def getAxisPanel():
    """pop panel for card to track

    :return: Panel
    :rtype: nuke.Panel()
    """

    panel = nuke.Panel('Axis to Track')
    panel.addEnumerationPulldown('Get nodes:', 'all Transform Tracker Roto')
    panel.addEnumerationPulldown('Full SetUp', 'No Yes')
    panel.addSingleLineInput('FrameRange', "{0}-{1}".format(nuke.root().firstFrame(), nuke.root().lastFrame()))
    panel.addSingleLineInput('Ref Frame', nuke.frame())
    panel.addSingleLineInput('Roto layer name', "C2T")
    panel.setWidth(300)

    return panel


def getFullSetUp(nodes, refFrame):
    """Create a setup that is ready to comp

    :param nodes: dict of rgb source, camera, card
    :type nodes: dict
    :param refFrame: reference frame
    :type refFrame: int
    """
    setUp = {}

    try:
        nodes['transform']['ypos'].setValue(nodes['Card']['ypos'].value() + 600)
        nodes['transform']['xpos'].setValue(nodes['Card']['xpos'].value())
    except:
        nodes['transform']['ypos'].setValue(nodes['Cam']['ypos'].value() + 600)
        nodes['transform']['xpos'].setValue(nodes['Cam']['xpos'].value())
    try:
        nodes['transform']['ypos'].setValue(nodes['Axis']['ypos'].value() + 600)
        nodes['transform']['xpos'].setValue(nodes['Axis']['xpos'].value())
    except:
        pass

    setUp['element'] = nuke.createNode('Dot', inpanel=False)
    setUp['element']['label'].setValue('element')
    setUp['element']['xpos'].setValue(nodes['transform']['xpos'].value())
    setUp['element']['ypos'].setValue(nodes['transform']['ypos'].value()-300)
    setUp['element'].setInput(0, None)
    setUp['transform'] = nuke.createNode('Transform', inpanel=False)
    setUp['transform']['label'].setValue('>THIS<')
    setUp['transform']['xpos'].setValue(nodes['transform']['xpos'].value())
    setUp['transform']['ypos'].setValue(nodes['transform']['ypos'].value() - 100)
    setUp['transform']['center'].setExpression('input.width/2', 0)
    setUp['transform']['center'].setExpression('input.height/2', 1)
    setUp['transform'].setInput(0, setUp['element'])

    setUp['bg1'] = nuke.createNode('Dot', inpanel=False)
    setUp['bg1']['label'].setValue('BG')
    setUp['bg1']['xpos'].setValue(nodes['transform']['xpos'].value() + 200)
    setUp['bg1']['ypos'].setValue(nodes['transform']['ypos'].value() - 300)
    setUp['bg1'].setInput(0, None)
    setUp['remove'] = nuke.createNode('Remove', inpanel=False)
    setUp['remove']['operation'].setValue('remove')
    setUp['remove']['channels'].setValue('all')
    setUp['remove']['xpos'].setValue(nodes['transform']['xpos'].value() + 200)
    setUp['remove']['ypos'].setValue(nodes['transform']['ypos'].value() -200)
    setUp['remove'].setInput(0, setUp['bg1'])
    try:
        nodes['Cam']['create_distort'].execute()
        setUp['undistorted1'] = nuke.allNodes('Group')[0]
        setUp['undistorted1']['xpos'].setValue(nodes['transform']['xpos'].value() + 200)
        setUp['undistorted1']['ypos'].setValue(nodes['transform']['ypos'].value() + -100)
        setUp['undistorted1'].setInput(0, setUp['remove'])
    except:
        pass
    setUp['merge1'] = nuke.createNode('Merge2')
    setUp['merge1']['xpos'].setValue(nodes['transform']['xpos'].value() + 200)
    setUp['merge1']['ypos'].setValue(nodes['transform']['ypos'].value())
    try:
        setUp['merge1'].setInput(0, setUp['undistorted1'])
    except:
        setUp['merge1'].setInput(0, setUp['remove'])
    setUp['merge1'].setInput(1, nodes['transform'])

    try:
        nodes['Cam']['create_distort'].execute()
        setUp['undistorted2'] = nuke.allNodes('Group')[0]
        setUp['undistorted2']['xpos'].setValue(nodes['transform']['xpos'].value() + 400)
        setUp['undistorted2']['ypos'].setValue(nodes['transform']['ypos'].value()-25)
        setUp['undistorted2'].setInput(0, setUp['merge1'])
        setUp['undistorted2']['mode'].setValue('Distort')
    except:
        pass
    setUp['bg2'] = nuke.createNode('Dot', inpanel=False)
    setUp['bg2']['label'].setValue('BG')
    setUp['bg2']['xpos'].setValue(nodes['transform']['xpos'].value() + 650)
    setUp['bg2']['ypos'].setValue(nodes['transform']['ypos'].value() - 300)
    setUp['bg2'].setInput(0, None)

    setUp['merge2'] = nuke.createNode('Merge2')
    setUp['merge2']['xpos'].setValue(nodes['transform']['xpos'].value() + 650)
    setUp['merge2']['ypos'].setValue(nodes['transform']['ypos'].value())
    try:
        setUp['merge2'].setInput(0, setUp['undistorted2'])
    except:
        setUp['merge2'].setInput(0, setUp['merge1'])
    setUp['merge2'].setInput(1, setUp['bg2'])

    nodes['transform'].setInput(0, setUp['transform'])
    setUp['bg1'].setInput(0, setUp['bg2'])

    for node in setUp.values():
        node.setSelected(True)

    nuke.autoplace_snap_all()

    for node in setUp.values():
        node.setSelected(False)


def cardToTrack():
    """Main function of card to track."""
    # GET NODES

    nodes = getNodes()

    # CHECK IF WHAT NEEDED IS SELECTED

    if selectSomething(nodes) == 0:
        pass
    elif selectSomething(nodes) == 1:
        nuke.message("Select a camera")
        return None
    elif selectSomething(nodes) == 2:
        nuke.message("Select RGB Source")
        return None

    # VARIABLES
    reconcileDict = {}
    axisDict = {}
    copySetUp = {}
    verts = None
    refFrame = nuke.frame()
    fFrame = int(nuke.root().firstFrame())
    lFrame = int(nuke.root().lastFrame())
    fullSetUp = 'Yes'

    # PANEL
    panel = getCardPanel()

    if panel.show() == 0:
        return None

    refFrame = panel.value('Ref Frame')
    getN = panel.value('Get nodes:')
    layerName = panel.value("Roto layer name")
    frameRange = panel.value("FrameRange")
    fullSetUp = panel.value('Full SetUp')

    frames = frameRange.split("-")
    fFrame = int(frames[0])
    lFrame = int(frames[1])

    copySetUp, axisDict = createcopySetUp()
    matchOriginalCard(nodes, copySetUp)

    num = 0
    for axis in axisDict:
        reconcileDict[num] = createReconcile(nodes, axisDict[num])
        num = num + 1

    # EXECUTE RECONCILE
    root = nuke.root()
    nuke.executeMultiple(reconcileDict.values(), ((fFrame, lFrame, 1),))

    # TRACKER
    trackerN = createTracker(refFrame, nodes)

    # APPLY TO TRACK
    num = 1

    for reconcilen in reconcileDict.values():
        applyToTrack(reconcilen, num, trackerN)
        num = num + 1

    # APPLY TO ROTO
    if getN == 'all' or getN == 'Roto':
        rotoN, layerTransform = createRotoNode(nodes, trackerN, layerName)
        applyToRoto(rotoN, layerTransform, trackerN, 4, fFrame, lFrame)

    # APPLY TO TRANSFORM
    if getN == 'all' or getN == 'Transform':
        transformN = createTransform(nodes, trackerN)
        applyTransform(transformN, trackerN, 4)

    # APPLY TO CORNERPIN (4 VERTICES)
    num = 1

    if getN == 'all' or getN == "CornerPin (4 vertices or Card)":
        cornerPin = createCornerPin(nodes, trackerN)
        for reconcilen in reconcileDict.values():
            applyToCornerPin(reconcilen, num, cornerPin, refFrame)
            num = num + 1

    # FULL SETUP
    if fullSetUp == 'Yes':
        nodes['transform'] = createTransform(nodes, trackerN)
        applyTransform(nodes['transform'], trackerN, 4)
        getFullSetUp(nodes, refFrame)

    # DELETE NODES
    if getN != 'all' and getN != 'Tracker':
        nuke.delete(trackerN)

    for reconcilen in reconcileDict.values():
        nuke.delete(reconcilen)

    del reconcileDict

    for axis in axisDict.values():
        nuke.delete(axis)

    # DELETE VARIABLES
    del axisDict


    for node in copySetUp.values():
        nuke.delete(node)

    del(copySetUp)
