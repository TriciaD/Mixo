import naoqi
import time
import almath
import math

NIp = "10.16.96.23"
PORT = 9559

motion = naoqi.ALProxy("ALMotion", NIp, PORT)
posture = naoqi.ALProxy("ALRobotPosture", NIp, PORT)
tts = naoqi.ALProxy("ALTextToSpeech", NIp,PORT)
markProxy = naoqi.ALProxy("ALLandMarkDetection", NIp, PORT)
animatedMode = naoqi.ALProxy("ALAutonomousLife", NIp, PORT)

def main():
    startUp()
    recCan()
    data = findInitialLM()
    #print data
    moveCoords = orient(data)
    #print moveCoords
    moveLM(moveCoords.r1_c4,moveCoords.r2_c4)

def startUp():
    state = "disabled"
    if animatedMode.getState() != state:
        animatedMode.setState(state)
    motion.setStiffnesses("Body", 1.0)
    id = posture.goToPosture("Crouch", 1.0)
    posture.wait(id,0)
    id = posture.goToPosture("Stand", 1.0)
    posture.wait(id,0)
    motion.setAngles("HeadYaw",0.0,.1)
    motion.setAngles("HeadPitch",.5,.1)

def recCan():
    LSP = "LShoulderPitch"
    LWY = "LWristYaw"
    motion.setAngles(LSP, 0.0, 1.0)
    #motion.setAngles("LShoulderRoll", 1.0, .0)
    motion.setAngles(LWY,-1.5,.1)
    motion.post.openHand("LHand")
    time.sleep(3)
    motion.post.closeHand("LHand")
    time.sleep(1)
    motion.setAngles(LSP,1.0,0.1)
    time.sleep(1)
    motion.setMoveArmsEnabled(False,True)
    time.sleep(.1)

def findInitialLM():
    # Subscribe to the ALLandMarkDetection extractor
    period = 500
    markProxy.subscribe("Test_Mark", period, 0.0 )
    # Create a proxy to ALMemory.
    memProxy = naoqi.ALProxy("ALMemory", NIp, PORT)
    # Get data from landmark detection (assuming landmark detection has been activated).
    data = None
    while not data:
        #motion.post.moveTo(0,0,.2)
        data = memProxy.getData("LandmarkDetected")
    return data

def orient(data):
    #actual landmark size
    LMSize = .175

    #camera in use
    currentCamera = "CameraTop"

    #landmark position in relation to camera in radians
    zCamera = data[1][0][0][1]
    yCamera = data[1][0][0][2]

    #angular size of the landmark in radians along the x-axis
    angularSize = data[1][0][0][3]

    #distance from the top camera to the landmark
    distCtoLM = LMSize / (2 * math.tan(angularSize/2))

    #camera position in NAO space
    transform = motion.getTransform(currentCamera,2,True)
    transformList = almath.vectorFloat(transform)
    mixoToCamera = almath.Transform(transformList)

    #rotation to point at LM
    rotTransform = almath.Transform_from3DRotation(0,yCamera,zCamera)

    #translation to langmark
    transTransform = almath.Transform(distCtoLM,0,0)

    #combine everything
    mixoToLM = mixoToCamera * rotTransform * transTransform

    return mixoToLM
    
def moveLM(a,b):
    motion.moveInit()
    a = math.sqrt(a**2 - .48**2)
    print a
    print b
    id = motion.post.moveTo(0.0,0.0,b)
    motion.wait(id,0)
    id = motion.post.moveTo(a/2,b/2,0.0)
    '''
    data = None
    while not data:
        data = getLM()
    if data[1][0][1][0] == 170:
        id = motion.setAngles("LShoulderPitch", 0.0, .1)
        motion.wait(id, 0)
        id = motion.post.openHand("LHand")
        motion.wait(id,0)
    id = motion.post.moveTo(-.1,0,0)
    motion.wait(id,0)
    '''
    posture.goToPosture("Crouch",1.0)
    
def getLM():
    # Subscribe to the ALLandMarkDetection extractor
    period = 500
    markProxy.subscribe("Test_Mark", period, 0.0 )
    # Create a proxy to ALMemory.
    memProxy = naoqi.ALProxy("ALMemory", NIp, PORT)
    # Get data from landmark detection (assuming landmark detection has been activated).
    return memProxy.getData("LandmarkDetected")
    
main()

