import naoqi
import time
import almath
import math

NIp = "10.16.96.41"
PORT = 9559
period = 50

motion = naoqi.ALProxy("ALMotion", NIp, PORT)
posture = naoqi.ALProxy("ALRobotPosture", NIp, PORT)
tts = naoqi.ALProxy("ALTextToSpeech", NIp,PORT)
markProxy = naoqi.ALProxy("ALLandMarkDetection", NIp, PORT)
animatedMode = naoqi.ALProxy("ALAutonomousLife", NIp, PORT)

def main():
    startUp()
    recCan()
    data = findInitialLM(1)
    moveCoords = orient(data, data[1][0][1][0])
    print data    
    #print moveCoords
    while moveCoords.r1_c4 > .4:
        print data
        moveCoords = orient(data, data[1][0][1][0])
        data = findLM(moveCoords.r2_c4)
        moveLM(moveCoords.r1_c4, moveCoords.r2_c4, data[1][0][1][0])
    dropCan(orient(data, data[1][0][1][0]).r2_c4)


def startUp():
    state = "disabled"
    if animatedMode.getState() != state:
        animatedMode.setState(state)
    motion.setStiffnesses("Body", 1.0)
    id = posture.goToPosture("Crouch", 1.0)
    posture.wait(id, 0)
    id = posture.goToPosture("Stand", 1.0)
    posture.wait(id, 0)
    motion.setAngles("HeadYaw", 0.0, .1)
    motion.setAngles("HeadPitch", .2, .1)


def recCan():
    LSP = "LShoulderPitch"
    LWY = "LWristYaw"
    motion.setAngles(LSP, 0.0, 1.0)
    motion.setAngles(LWY, -1.5, .1)
    motion.post.openHand("LHand")
    time.sleep(3)
    motion.post.closeHand("LHand")
    time.sleep(1)
    motion.setAngles(LSP, 1.0, 0.1)
    time.sleep(1)
    motion.setMoveArmsEnabled(False, True)
    time.sleep(.1)


def findLM(y):
    # Subscribe to the ALLandMarkDetection extractor
    markProxy.subscribe("Test_Mark", period, 0.0)
    # Create a proxy to ALMemory.
    memProxy = naoqi.ALProxy("ALMemory", NIp, PORT)
    if y >= 0:
        a = 1
    else:
        a = -1
    # Get data from landmark detection (assuming landmark detection has been activated).
    data = None
    count = 0
    while not data and count < 20:
        data = memProxy.getData("LandmarkDetected")
        count += 1
    if count >= 20:
        data = findInitialLM(a)
    return data


def orient(data, LMNum):
    #actual landmark size
    if LMNum == 130:
        LMSize = .178
    else:
        LMSize = .105

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
    transform = motion.getTransform(currentCamera, 2, True)
    transformList = almath.vectorFloat(transform)
    mixoToCamera = almath.Transform(transformList)

    #rotation to point at LM
    rotTransform = almath.Transform_from3DRotation(0, yCamera, zCamera)

    #translation to langmark
    transTransform = almath.Transform(distCtoLM, 0, 0)

    #combine everything
    mixoToLM = mixoToCamera * rotTransform * transTransform

    return mixoToLM


def moveLM(a, b, c):
    if c == 130:
        d = .48
    else:
        d = .18
    motion.moveInit()
    print a
    a = math.sqrt(a**2 - d**2)
    print a
    print b
    id = motion.post.moveTo(0.0, 0.0, b)
    motion.wait(id, 0)
    id = motion.post.moveTo(a/3, 0.0, 0.0)
    motion.wait(id, 0)
    #motion.rest()


def dropCan(k):
    data = None
    motion.setStiffnesses("Body", 1.0)
    while not data:
        data = findLM(k)
    print data
    if data[1][0][1][0] == 170:
        motion.moveInit()
        coords = orient(data, 170)
        dToR = coords.r1_c4
        print dToR
        if dToR < .5:
            id = motion.post.moveTo(-.4, 0.0, 0.0)
            motion.wait(id, 0)
            id = motion.post.setAngles("LShoulderPitch", -.5, .1)
            motion.wait(id, 0)
            id = motion.post.setAngles("LWristYaw", 0.0, .1)
            motion.wait(id, 0)
            id = motion.post.moveTo(0.0, 0.0, coords.r2_c4)
            motion.wait(id, 0)
            id = motion.post.moveTo(.4, 0.0, 0.0)
            motion.wait(id, 0)
        else:
            id = motion.post.setAngles("LShoulderPitch", -.5, .1)
            motion.wait(id, 0)
            id = motion.post.setAngles("LWristYaw", 0.0, .1)
            motion.wait(id, 0)
            id = motion.post.moveTo(0.0, 0.0, coords.r2_c4)
            motion.wait(id, 0)
            id = motion.post.moveTo((dToR - .3), 0.0, 0.0)
            motion.wait(id, 0)
    '''
    id = motion.post.setAngles("LShoulderPitch", 0.0, .1)
    motion.wait(id, 0)'''
    id = motion.post.openHand("LHand")
    motion.wait(id, 0)
    tts.say("Suck it bitches!")
    id = motion.post.moveTo(-.3, 0, 0)
    motion.wait(id, 0)

    motion.rest()
    
    
def findInitialLM(a):
    # Subscribe to the ALLandMarkDetection extractor
    a = a * .5
    motion.setStiffnesses("Body", 1.0)
    motion.moveInit()
    markProxy.subscribe("Test_Mark", period, 0.0)
    # Create a proxy to ALMemory.
    memProxy = naoqi.ALProxy("ALMemory", NIp, PORT)
    # Get data from landmark detection (assuming landmark detection has been activated).
    data = None
    while not data:
        for i in range(5):
            data = memProxy.getData("LandmarkDetected")
            if data:
                break
        if not data:
            id = motion.post.moveTo(0.0, 0.0, a)
            motion.wait(id, 0)
    return data

    
main()
