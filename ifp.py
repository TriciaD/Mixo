import naoqi
import time
import almath
import math

NIp = "10.16.96.41"
PORT = 9559

motion = naoqi.ALProxy("ALMotion", NIp, PORT)
posture = naoqi.ALProxy("ALRobotPosture", NIp, PORT)
tts = naoqi.ALProxy("ALTextToSpeech", NIp,PORT)
markProxy = naoqi.ALProxy("ALLandMarkDetection", NIp, PORT)
animatedMode = naoqi.ALProxy("ALAutonomousLife", NIp, PORT)

id = posture.goToPosture("Stand", 1.)

s = tts.post.say("I feel pretty!")
motion.wait(s, 0)
id = motion.post.moveTo(0, 0, math.pi / 2)
motion.wait(id, 0)
s = tts.post.say("Does my ass look fat in this outfit?")
motion.wait(s, 0)
motion.rest()

