# Simple pygame program
# Import and initialize the pygame library
import ffmpeg
import pygame
import pygame.camera
from pygame.locals import *
import shutil
from datetime import datetime
import RPi.GPIO as GPIO
from subprocess import Popen, PIPE
import signal
import os
from os import listdir
from os.path import isfile, join
import netifaces as ni
import serial
#import ffmpeg

os.environ["SDL_FBDEV"] = "/dev/fb0"
pygame.init()
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
myfont = pygame.font.Font('VCR_OSD_MONO.ttf', 32)

#CAMENABLED = True

capres = (720, 480, 30)
capturing = False
playing = False
oldPlaying = False
oldCapturing = False
selectedvid = 0
vidpath = "./Vids/"
ip = ""
#Arduino vars
volts = 0.0
mag1 = 0.0
mag2 = 0.0
mag1buf = [0,0,0,0,0,0,0,0,0,0]
mag2buf = [0,0,0,0,0,0,0,0,0,0]

CAMIMAGE = None
pygame.camera.init()
CAM = pygame.camera.Camera("/dev/video0", (640, 480))
CAM.start()

capled = 21
btn1 = 23
btn2 = 22
btn3 = 27
btn4 = 18

btn5 = 5
btn6 = 6
btn7 = 13
btn8 = 19

relay = 7

GPIO.setmode(GPIO.BCM)
GPIO.setup(capled, GPIO.OUT)
GPIO.setup(btn1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(btn4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
oldBtn1 = False
oldBtn2 = False
oldBtn3 = False
oldBtn4 = False

GPIO.setup(relay, GPIO.OUT)
GPIO.output(relay, GPIO.HIGH)

BLUE = (0, 255, 255)
GREEN = (20, 255, 70)
YELLOW = (255, 255, 0)
RED = (255, 20, 10)
DARK_RED = (120, 2, 1)
GREY = (180, 180, 180)


ffmpegproc = None


# Set up the drawing window
screen = pygame.display.set_mode([640, 480], pygame.FULLSCREEN)

ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

def DrawText(screen, text, pos, color):
    textsurface = myfont.render(text, True, color)
    screen.blit(textsurface,pos)

# Run until the user asks to quit
running = True
while running:
    if GPIO.input(btn1) == False:
        if not oldBtn1:
            capturing = not capturing
            if capturing:
                now = datetime.now()
                dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
                ffmpegproc = Popen("ffmpeg -y -f v4l2 -input_format mjpeg -video_size "+str(capres[0])+"x"+str(capres[1])+" -r "+str(capres[2])+" -i /dev/video0 -c:v copy "+vidpath+dt_string+".avi", shell = True)
            else:
                ffmpegproc = Popen("pkill ffmpeg", shell = True)
                print ("killed ffmpeg!")
        oldBtn1 = True
    else:
        oldBtn1 = False
    if GPIO.input(btn2) == False:
        if not oldBtn2:
            playing = not playing
            if playing:
                
                ffmpegproc = Popen("ffplay "+vidpath+sorted(listdir(vidpath), reverse=True)[selectedvid]+" -x 1920 -y 1280", shell = True)
            else:
                ffmpegproc = Popen("pkill ffplay", shell = True)
                print ("killed ffplay!")
        oldBtn2 = True
    else:
        oldBtn2 = False
    if GPIO.input(btn3) == False:
        if not oldBtn3:
            selectedvid -= 1
            if(selectedvid < 0):
                selectedvid = 4
        oldBtn3 = True
    else:
        oldBtn3 = False
    if GPIO.input(btn4) == False:
        if not oldBtn4:
            selectedvid += 1
            if(selectedvid > 4):
                selectedvid = 0
        oldBtn4 = True
    else:
        oldBtn4 = False
    #Play vid sorted(listdir(vidpath), reverse=True)
    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill the background
    screen.fill((0, 0, 0))

    if(CAMIMAGE != None):
        screen.blit(CAMIMAGE, (0, 0))

    # Draw Time
    now = datetime.now()
    dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
    DrawText(screen, dt_string, (0,0), YELLOW)

    # Draw res
    textsurface = myfont.render('Current Resolution: ', True, BLUE)
    screen.blit(textsurface,(0,40))

    textsurface = myfont.render(str(capres[0]) + 'x' + str(capres[1]) + 'p' + str(capres[2]), True, GREEN)
    screen.blit(textsurface,(355,40))

    # Draw Storage
    total, used, free = shutil.disk_usage("/")
    textsurface = myfont.render('Available Storage: ', True, BLUE)
    screen.blit(textsurface,(0,80))

    textsurface = myfont.render(str((free // (2**30))) + " GiB (SDHC)", True, GREEN)
    screen.blit(textsurface,(335,80))

    textsurface = myfont.render('Ext Storage: ', True, BLUE)
    screen.blit(textsurface,(0,120))

    textsurface = myfont.render("NULL", True, GREEN)
    screen.blit(textsurface,(225,120))

    if(capturing):
        GPIO.output(capled, GPIO.LOW)
        if (int(now.strftime("%S")) % 2) == 0:
            pygame.draw.circle(screen, RED, (616, 24), 16)
        else:
            GPIO.output(capled, GPIO.HIGH)
            pygame.draw.circle(screen, DARK_RED, (616, 24), 16)
    else:
        GPIO.output(capled, GPIO.HIGH)
        pygame.draw.circle(screen, GREY, (616, 24), 16)


    textsurface = myfont.render("Recent Recordings:", True, BLUE)
    screen.blit(textsurface,(0,160))

    i = 0
    for f in sorted(listdir(vidpath)[:5], reverse=True):
        if isfile(join(vidpath, f)):
            if(i == selectedvid):
                DrawText(screen, ">"+f, (0, 200+i*40), YELLOW)
            else:
                DrawText(screen, f, (0, 200+i*40), YELLOW)
            i += 1

    #Draw IP
    if (int(now.strftime("%S")) % 2) == 0:
        #ni.ifaddresses('wlan0')
        try:
            ip = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
        except:
            pass
    DrawText(screen, ip, (0,440), BLUE)

    #Serial stuff
    li = ""
    while ser.in_waiting:  # Or: while ser.inWaiting():
        li = ser.readline().decode('utf-8')
    #li = "V:8.34"
    if(len(li) > 2):
        split = li.split(":")
        if(split[0] == "V"):
            volts = float(split[1])
        if(split[0] == "1"):
            mag1 = float(split[1])
            mag1buf.pop(0)
            mag1buf.append(mag1)
        if(split[0] == "2"):
            mag2 = float(split[1])
            mag2buf.pop(0)
            mag2buf.append(mag2)
    DrawText(screen, "mag1:"+str(mag1), (450,360), YELLOW)
    DrawText(screen, "mag2:"+str(mag2), (450,400), YELLOW)
    DrawText(screen, str(volts), (450,440), GREEN)

    if(mag1 > 400 and mag2 > 400):
        pygame.draw.rect(screen, GREY, (0,0,640,480))
        CAMIMAGE = CAM.get_image()
        dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")
        pygame.image.save(CAMIMAGE, "./Images/img_"+dt_string+"_Points-"+str(mag1+mag2)+".jpg")
    
    # Flip the display
    pygame.display.flip()

# Done! Time to quit.
pygame.quit()
