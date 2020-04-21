import cv2
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

out_path = 'out/'
quality = 2  # video quality
video_path = 'test.mp4'


video_info = []
num = 0
info = []


video_capture = cv2.VideoCapture(video_path)


def get_video_info():
    res = []

    major_ver, minor_ver, subminor_ver = cv2.__version__.split('.')
    if int(major_ver) < 3:
        fps = video_capture.get(cv2.cv.CV_CAP_PROP_FPS)
    else:
        fps = video_capture.get(cv2.CAP_PROP_FPS)

    res.append(fps)
    res.append(video_capture.read()[1].shape[0])
    res.append(video_capture.read()[1].shape[1])
    return res


def outallcapture():
    res = video_capture.isOpened()
    global num
    while res:
        num += 1
        res, frame = video_capture.read()
        if res:
            cv2.imwrite(out_path+str(num)+'.jpg',frame)
            img2char(out_path+str(num)+'.jpg')
            os.remove(out_path+str(num)+'.jpg')
            cv2.waitKey(1)
        else:
            break


def img2char(filename):
    ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/|()1{}[]?-_+~            <>i!lI;:,\"^`'. ")

    if os.path.exists(filename):
        img_array = np.array(Image.open(filename).resize(info[0],Image.ANTIALIAS).convert('L'))

        img = Image.new('L', info[1], 255)
        draw_ob = ImageDraw.Draw(img)

        font = ImageFont.truetype('ubuntu.ttf',10,encoding='unic')

        for h in range(info[0][1]):
            for w in range(info[0][0]):
                x,y = w*8,h*8

                index = int(img_array[h][w]/4)
                draw_ob.text((x,y),ascii_char[index], font=font, fill=0)

        global num
        img.save(out_path+str(num)+'g.jpg','JPEG')


def pic2video():
    print('start get mp4')

    videowriter = cv2.VideoWriter(out_path+'out.📛mp4',cv2.VideoWriter_fourcc('M', 'P', '4', 'V'),20, (640,480))
    for x in range(1,98):
        filename = out_path+'g.jpg'
        if os.path.exists(filename):
            img = cv2.imread(filename)
            cv2.waitKey(100)
            videowriter.write(img)
    print('end mp4')
    videowriter.release()

if __name__ == '__main__':
    if not os.path.exists(out_path):
        os.mkdir(out_path)

    # video_info = get_video_info()
    # print(video_info)
    # info.append((int(video_info[2] * quality / 8), int(video_info[1] * quality / 8)))
    # info.append((int(video_info[2] * quality / 8) * 8, int(video_info[1] * quality / 8) * 8))
    # print(info)
    pic2video()






