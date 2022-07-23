import cv2
import sys,os
import math
import numpy as np
from PIL import Image
import shutil
from datetime import  datetime
import glob

def frames_to_video(fps,save_path,frames_path,type='MP4'):
    if type=="MP4":
        fourcc=cv2.VideoWriter_fourcc(*'mp4v')
    elif type=="AVI":
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #videoWriter=cv2.VideoWriter(save_path,fourcc,fps,(966,540))
    imgs=sorted(os.listdir(frames_path))
    image1= os.path.join(frames_path,imgs[0])
    [height,width,pix]=cv2.imread(image1).shape
    print('h:{} w:{} pix:{}'.format(height,width,pix))
    print('value--save_path:{} fourcc:{} fps:{} scale_width:{} scale_height:{}'.format(save_path,fourcc,fps,width,height))
    videoWriter = cv2.VideoWriter(save_path, fourcc, fps, (width, height))
    frames_num=len(imgs)
    for i in range(frames_num):
        image=frames_path+imgs[i]
        frame=cv2.imread(image)
        videoWriter.write(frame)
    videoWriter.release()
    return

def removeTmpDir(rootdir):
    filelist=os.listdir(rootdir)
    if filelist:
        for f in filelist:
            filepath=os.path.join(rootdir,f)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath,True)
    shutil.rmtree(rootdir,True)

def video_to_frames(video_name,video_path,result_path):
    num=0
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    capture=cv2.VideoCapture(video_path)
    fps=capture.get(cv2.CAP_PROP_FPS)
    while True:
        ret,img=capture.read()
        if not ret:
            break
        picname=video_name+'_'+'{:05d}.jpg'.format(num)
        cv2.imwrite(os.path.join(result_path,picname),img)
        num+=1
    capture.release()
    return [num,fps]

def getFrameShape(path):
    img_files=os.listdir(path)
    pic1=os.path.join(path,img_files[0])
    shape=cv2.imread(pic1).shape
    return shape

def getImages(path):
    results_images=[]
    images=sorted(os.listdir(path))
    img_num=len(images)
    for i in range(img_num):
        img=os.path.join(path,images[i])
        results_images.append(img)
    return results_images


# 用于判断文件后缀
def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'xls', 'JPG', 'PNG', 'xlsx', 'gif', 'GIF','mp4'])
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#改变图片尺寸
def changeImageSize(src_path,dst_path,width,height,scale=1.0):
    imgs = sorted(os.listdir(src_path))
    scale_width = int(width * scale)
    scale_height = int(height * scale)
    frames_num = len(imgs)
    for i in range(frames_num):
        img=os.path.join(src_path, imgs[i])
        img_array=cv2.imread(img)
        img_resize=cv2.resize(img_array,(scale_width,scale_height),interpolation=cv2.INTER_LINEAR)
        img_output=os.path.join(dst_path,imgs[i])
        cv2.imwrite(img_output,img_resize)

#改变图片尺寸
def changeImageSize1(src_path,dst_path,scale_width,scale_height):
    imgs = sorted(os.listdir(src_path))
    frames_num = len(imgs)
    for i in range(frames_num):
        img=os.path.join(src_path, imgs[i])
        img_array=cv2.imread(img)
        img_resize=cv2.resize(img_array,(scale_width,scale_height),interpolation=cv2.INTER_LINEAR)
        img_output=os.path.join(dst_path,imgs[i])
        cv2.imwrite(img_output,img_resize)

def vosvideo_overlay_fade(image, mask):
    #image - shape: (480, 854, 3)
    #mask - shape: (480, 854)
    from scipy.ndimage.morphology import binary_erosion, binary_dilation
    im_overlay = image.copy()

    # Overlay color on  binary mask
    binary_mask = mask == 255
    not_mask = mask != 255

    # Compose image
    im_overlay[not_mask] = 0.4 * im_overlay[not_mask]


    countours = binary_dilation(binary_mask) ^ binary_mask
    im_overlay[countours,0] = 0
    im_overlay[countours,1] = 255
    im_overlay[countours,2] = 255

    return im_overlay.astype(image.dtype)

def frames_to_video(fps,save_path,frames_path,type='MP4'):
    if type=='MP4':
        fourcc=cv2.VideoWriter_fourcc(*'mp4v')
    elif type=='AVI':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    #videoWriter=cv2.VideoWriter(save_path,fourcc,fps,(966,540))
    imgs=sorted(os.listdir(frames_path))
    image1= os.path.join(frames_path,imgs[0])
    [height,width,pix]=cv2.imread(image1).shape
    print('h:{} w:{} pix:{}'.format(height,width,pix))
    print('value--save_path:{} fourcc:{} fps:{} width:{} height:{}'.format(save_path,fourcc,fps,width,height))
    videoWriter = cv2.VideoWriter(save_path, fourcc, fps, (width, height))
    frames_num=len(imgs)
    for i in range(frames_num):
        image=os.path.join(frames_path,imgs[i])
        frame=cv2.imread(image)
        videoWriter.write(frame)
    videoWriter.release()
    return

def overlay_vos_src(src_imagesa_path,mask_images_path,result_path):
    overlay_color=[255,0,0]
    transparency=0.6
    src_images=getImages(src_imagesa_path)
    mask_images=getImages(mask_images_path)
    num=len(src_images)
    for i in range(num):
        srcImage=src_images[i]
        maskImage=mask_images[i]
        img = np.array(Image.open(srcImage))
        mask = np.array(Image.open(maskImage))
        mask=mask//np.max(mask)
        im_over=np.ndarray(img.shape)
        nchannel = cv2.imread(srcImage).shape[2]
        im_over[:, :, 0] = (1 - mask) * img[:, :, 0] + mask * (overlay_color[0] * transparency + (1 - transparency) * img[:, :, 0])
        im_over[:, :, 1] = (1 - mask) * img[:, :, 1] + mask * (overlay_color[1] * transparency + (1 - transparency) * img[:, :, 1])
        im_over[:, :, 2] = (1 - mask) * img[:, :, 2] + mask * (overlay_color[2] * transparency + (1 - transparency) * img[:, :, 2])
        limg2=im_over.astype(np.uint8)
        save_path=os.path.join(result_path,'{:05d}.jpg'.format(i))
        cv2.imwrite(save_path, limg2[..., ::-1])
        

def overlay_mask_src(src_frames_path, mask_frames_path,result_frames_path):
    #RGB方式load
    src_frames=sorted(os.listdir(src_frames_path))
    pic_length = len(src_frames)
    mask_frames=sorted(os.listdir(mask_frames_path))
    print("src_frames:")
    print(src_frames)
    print("mask_frames:")
    print(mask_frames)
    for i in range(pic_length):
        pic_name='{:05d}.jpg'.format(i)
        src_frame = os.path.join(src_frames_path,src_frames[i])
        mask_frame = os.path.join(mask_frames_path,mask_frames[i])
        mask_frame_array=np.array(Image.open(mask_frame))
        src_frame_array = np.array(Image.open(src_frame).convert('RGB'), dtype=np.uint8)
        overlay_array=vosvideo_overlay_fade(src_frame_array, mask_frame_array)
        save_path=os.path.join(result_frames_path,pic_name)
        cv2.imwrite(save_path, overlay_array[..., ::-1])

