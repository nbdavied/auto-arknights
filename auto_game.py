# -*- coding:utf-8 -*-
# @author：LuffyLSX
# @version：1.0
# @update time：2019/8/31

import os,time
import cv2
import random
import pytesseract
import winsound
from PIL import Image

def connect():
    try:
        os.system('adb connect 127.0.0.1:7555')
    except:
        print('连接失败')

def click(center):
    x = center[0]
    y = center[1]
    pn_x = random.random()
    pn_y = random.random()
    dis_x = random.random() * center[2]
    dis_y = random.random() * center[3]
    if(pn_x < 0.5):
        x = x - dis_x
    else:
        x = x + dis_x
    if(pn_y < 0.5):
        y = y - dis_y
    else:
        y = y + dis_y
    print('x:',x, 'y:', y)
    os.system('adb shell input tap %s %s' % (x, y))

def screenshot():
    path = os.path.abspath('.') + '\images'
    os.system('adb shell screencap /data/screen.png')
    os.system('adb pull /data/screen.png %s' % path)

def resize_img(img_path):
    img1 = cv2.imread(img_path, 0)
    img2 = cv2.imread('images/screen.png', 0)
    height, width = img1.shape[:2]
    ratio = 2560 / img2.shape[1]
    size = (int(width/ratio), int(height/ratio))
    return cv2.resize(img1, size, interpolation = cv2.INTER_AREA)

def Image_to_position(image, m = 0):
    image_path = 'images/' + str(image) + '.png'
    screen = cv2.imread('images/screen.png', 0)
    if image == 'stone':
        template = cv2.imread(image_path, 0)
    else:
        template = resize_img(image_path)
    methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_SQDIFF_NORMED, cv2.TM_CCORR_NORMED]
    image_y, image_x = template.shape[:2]
    result = cv2.matchTemplate(screen, template, methods[m])
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # print(max_val)
    MIN = 0.7
    # if image =='stone':
    #     MIN = 0.6
    if max_val > MIN:
        global center
        center = (max_loc[0] + image_x / 2, max_loc[1] + image_y / 2, image_x/2, image_y/2)
        print(center)
        return center
    else:
        return False
def revertColor(img):
    # 灰度图片反色，处理成黑白两色
    x, y = img.shape
    for i in range(x):
        for j in range(y):
            if img[i,j] > 128:
                img[i,j] = 0
            else:
                img[i,j] = 255
    return img

def enlarge(img):
    # 图片外围填充白色边控
    # 不然tesseract无法识别
    largepic = cv2.copyMakeBorder(img, 30,30,30,30,cv2.BORDER_CONSTANT,value = [255,255,255])
    return largepic

def ocrRead(img):
    # 读取图片中的文字
    text = pytesseract.image_to_string(img)
    print(text)
    return text

def read_battle_progress():
    screen = cv2.imread('images/screen.png', 0)
    progressimg = screen[20:70,660:770]
    progressimg = revertColor(progressimg)
    cv2.imwrite('images/tmp.png',progressimg)
    progressimg = cv2.imread('images/tmp.png')
    progressimg = enlarge(progressimg)
    progressimg = Image.fromarray(cv2.cvtColor(progressimg, cv2.COLOR_BGR2RGB))
    text = ocrRead(progressimg)
    return text

def sleepAccordingProgress(progress):
    if progress == '':
        time.sleep(5)
        return
    kill,all = progress.split('/')
    kill = int(kill)
    all = int(all)
    rest = all - kill
    sleeptime = rest / all * 60
    if sleeptime < 2:
        sleeptime = 2
    print('sleep ', sleeptime, ' seconds')
    time.sleep(sleeptime)
def beepAlert():
    freq = 1500
    duration = 1000
    for i in range(5):
        winsound.Beep(freq, duration)
        time.sleep(0.5)

def beepSuccess():
    duration = 1000
    freq = 300
    for i in range(4):
        winsound.Beep(freq, duration)
        freq += 80
def run(n):
    images = {
        'unknown':['start-go1', 'start-go2', 'end', 'level up', 'stone'],
        'start-go1':['start-go2','stone','start-go1'],
        'start-go2':['end','level up', 'start-go2'],
        'end':['start-go1','level up', 'end'],
        'stone':['start-go1', 'stone'],
        'level up':['end', 'start-go1','level up']
        }
    round = 0
    # Image_to_position('start-go1')
    # time.sleep(2)
    # Image_to_position('start-go2')
    # while not Image_to_position('end'):
    #     time.sleep(5)
    current='unknown'
    repeat = 0
    while True:
        screenshot()
        now = ''
        repeat += 1
        if repeat >=200:
            print('长时间未捕获正常状态，程序结束')
            beepAlert()
            break
        for image in images[current]:
            if Image_to_position(image, m = 0) != False:
                print(image)
                now = image
                current=image
                time.sleep(0.5)
                click(center)
                repeat = 0
                break
                
        if now == 'end':
            time.sleep(0.8)
            round = round + 1
            print('打完第%i/%i次'%(round,n))
            if round == n:
                break
        if now == 'stone':
            time.sleep(1.5)
        if current == 'start-go2':
            print('ready for ocr')
            p = read_battle_progress()
            sleepAccordingProgress(p)

if __name__ == '__main__':
    connect()
    '''for i in range(int(input('输入刷图次数' + '\n'))):
        run()
        time.sleep(3)'''
    try:
        run(int(input('输入刷图次数' + '\n')))
    except Exception as e:
        print(e)
        beepAlert()
    os.system('adb kill-server')
    beepSuccess()

