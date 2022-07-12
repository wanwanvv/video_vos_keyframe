from __future__ import division
import os,sys
import cv2
import scipy.io as sio
import tensorflow as tf
import tensorflow.contrib.slim as slim
import shutil
import numpy as np
import scipy.linalg
from copy import deepcopy
from scipy import ndimage
root_folder7 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder7=os.path.dirname(root_folder7 )
resources_folder4=os.path.join(parent_folder7,'resources')
sys.path.append(parent_folder7)
sys.path.append(os.path.join(parent_folder7,'InteSeg'))

#清楚文件夹及内容
def removeDir(rootdir):
    filelist=os.listdir(rootdir)
    for f in filelist:
        filepath=os.path.join(rootdir,f)
    if os.path.isfile(filepath):
        os.remove(filepath)
    elif os.path.isdir(filepath):
        shutil.rmtree(filepath,True)
    shutil.rmtree(rootdir,True)

#计算IOU的函数
def compIoU(im1, im2):
    im1_mask = (im1>0.5)
    im2_mask = (im2>0.5)
    iou = np.sum(im1_mask&im2_mask)/np.sum(im1_mask|im2_mask)
    return iou

#激活函数leaky-relu
def lrelu(x):
    return tf.maximum(x*0.2,x)

# 初始化
def identity_initializer():
    def _initializer(shape, dtype=tf.float32, partition_info=None):
        array = np.zeros(shape, dtype=float)
        cx, cy = shape[0]//2, shape[1]//2
        for i in range(min(shape[2],shape[3])):
            array[cx, cy, i, i] = 1
        return tf.constant(array, dtype=dtype)
    return _initializer

#batch_norm的超参数
def nm(x):
    w0=tf.Variable(1.0,name='w0')
    w1=tf.Variable(0.0,name='w1')
    return w0*x+w1*slim.batch_norm(x)

#预处理均值
MEAN_VALUES = np.array([123.6800, 116.7790, 103.9390]).reshape((1,1,1,3))

#卷积和池化层
def build_net(ntype,nin,nwb=None,name=None):
    if ntype=='conv':
        return tf.nn.relu(tf.nn.conv2d(nin,nwb[0],strides=[1,1,1,1],padding='SAME',name=name)+nwb[1])
    elif ntype=='pool':
        return tf.nn.avg_pool(nin,ksize=[1,2,2,1],strides=[1,2,2,1],padding='SAME')

#读取vgg网络的w和b值
def get_weight_bias(vgg_layers,i):
    weights=vgg_layers[i][0][0][2][0][0]
    weights=tf.constant(weights)
    bias=vgg_layers[i][0][0][2][0][1]
    bias=tf.constant(np.reshape(bias,(bias.size)))
    return weights,bias

#构建vgg网络
def build_vgg19(input,reuse=False):
    if reuse:
        tf.get_variable_scope().reuse_variables()
    net={}
    vgg_rawnet=scipy.io.loadmat(parent_folder7+'/models/imagenet-vgg-verydeep-19.mat')
    vgg_layers=vgg_rawnet['layers'][0]
    net['input']=input-MEAN_VALUES
    net['conv1_1']=build_net('conv',net['input'],get_weight_bias(vgg_layers,0),name='vgg_conv1_1')
    net['conv1_2']=build_net('conv',net['conv1_1'],get_weight_bias(vgg_layers,2),name='vgg_conv1_2')
    net['pool1']=build_net('pool',net['conv1_2'])
    net['conv2_1']=build_net('conv',net['pool1'],get_weight_bias(vgg_layers,5),name='vgg_conv2_1')
    net['conv2_2']=build_net('conv',net['conv2_1'],get_weight_bias(vgg_layers,7),name='vgg_conv2_2')
    net['pool2']=build_net('pool',net['conv2_2'])
    net['conv3_1']=build_net('conv',net['pool2'],get_weight_bias(vgg_layers,10),name='vgg_conv3_1')
    net['conv3_2']=build_net('conv',net['conv3_1'],get_weight_bias(vgg_layers,12),name='vgg_conv3_2')
    net['conv3_3']=build_net('conv',net['conv3_2'],get_weight_bias(vgg_layers,14),name='vgg_conv3_3')
    net['conv3_4']=build_net('conv',net['conv3_3'],get_weight_bias(vgg_layers,16),name='vgg_conv3_4')
    net['pool3']=build_net('pool',net['conv3_4'])
    net['conv4_1']=build_net('conv',net['pool3'],get_weight_bias(vgg_layers,19),name='vgg_conv4_1')
    net['conv4_2']=build_net('conv',net['conv4_1'],get_weight_bias(vgg_layers,21),name='vgg_conv4_2')
    net['conv4_3']=build_net('conv',net['conv4_2'],get_weight_bias(vgg_layers,23),name='vgg_conv4_3')
    net['conv4_4']=build_net('conv',net['conv4_3'],get_weight_bias(vgg_layers,25),name='vgg_conv4_4')
    net['pool4']=build_net('pool',net['conv4_4'])
    net['conv5_1']=build_net('conv',net['pool4'],get_weight_bias(vgg_layers,28),name='vgg_conv5_1')
    net['conv5_2']=build_net('conv',net['conv5_1'],get_weight_bias(vgg_layers,30),name='vgg_conv5_2')
    #net['conv5_3']=build_net('conv',net['conv5_2'],get_weight_bias(vgg_layers,32),name='vgg_conv5_3')
    #net['conv5_4']=build_net('conv',net['conv5_3'],get_weight_bias(vgg_layers,34),name='vgg_conv5_4')
    #net['pool5']=build_net('pool',net['conv5_4'])
    return net

def build(input,sz):
    vgg19_features=build_vgg19(input[:,:,:,0:3])
    for layer_id in range(1,6):
        vgg19_f = vgg19_features['conv%d_2'%layer_id]
        input = tf.concat([input, tf.image.resize_bilinear(vgg19_f,sz)], axis=3)
    input = input/255.0
    net=slim.conv2d(input,64,[1,1],rate=1,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv0')
    net=slim.conv2d(net,64,[3,3],rate=1,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv1')
    net=slim.conv2d(net,64,[3,3],rate=2,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv2')
    net=slim.conv2d(net,64,[3,3],rate=4,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv3')
    net=slim.conv2d(net,64,[3,3],rate=8,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv4')
    net=slim.conv2d(net,64,[3,3],rate=16,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv5')
    net=slim.conv2d(net,64,[3,3],rate=32,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv6')
    net=slim.conv2d(net,64,[3,3],rate=64,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv7')
    net=slim.conv2d(net,64,[3,3],rate=128,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv8')
    net=slim.conv2d(net,64,[3,3],rate=1,activation_fn=lrelu,normalizer_fn=nm,weights_initializer=identity_initializer(),scope='g_conv9')
    net=slim.conv2d(net,6,[1,1],rate=1,activation_fn=None,scope='g_conv_last')
    return tf.tanh(net)


def our_func(data_dir,x,y,pic_id,im_path,cnt,pn):
    # *****创建临时的存储文件夹*****
    tmp_dir = os.path.join(data_dir, pic_id + '_inteSegTmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    inits_dir = os.path.join(tmp_dir, 'inits')
    segs_dir = os.path.join(tmp_dir, 'segs')
    tmps_dir = os.path.join(tmp_dir, 'tmps')
    if not os.path.exists(inits_dir):
        os.makedirs(inits_dir)
    if not os.path.exists(segs_dir):
        os.makedirs(segs_dir)
    if not os.path.exists(tmps_dir):
        os.makedirs(tmps_dir)
    # *****创建临时的存储文件夹*****

    imIdx=0
    sess = tf.Session()
    # 初始化变量
    #if cnt == 0 and imIdx == 0:
    #global network, input, output, sz
    input = tf.placeholder(tf.float32, shape=[None, None, None, 7])
    output = tf.placeholder(tf.float32, shape=[None, None, None, 1])
    sz = tf.placeholder(tf.int32, shape=[2])
    network = build(input, sz)
    # print("cnt:{}".format(cnt))
    # print(input)
    # print("**************")
    # print(output)
    # print("**************")
    # print(sz)
    # ××××加载模型××××
    saver = tf.train.Saver(var_list=[var for var in tf.trainable_variables() if var.name.startswith('g_')])
    sess.run(tf.initialize_all_variables())

    ckpt = tf.train.get_checkpoint_state(os.path.join(parent_folder7,'models','ours_cvpr18'))
    if ckpt:
        # print('loaded '+ckpt.model_checkpoint_path)
        saver.restore(sess, ckpt.model_checkpoint_path)
    # ××××加载模型××××
    input_image = cv2.imread(im_path, -1) #-1表示加载彩色图片包括alpha通道
    iH, iW, _ = input_image.shape
    if cnt == 0:
        int_pos = np.uint8(255*np.ones([iH,iW]))
        int_neg = np.uint8(255*np.ones([iH,iW]))
        tmp_clk = cv2.imread(im_path, -1)
    else:
        pic1 = pic_id+'_pos_dt_%03d.png' %(cnt-1)
        pic2 = pic_id+'_neg_dt_%03d.png' % (cnt - 1)
        pic3 = pic_id+'_clk_%03d.png' % (cnt - 1)
        int_pos = cv2.imread(os.path.join(inits_dir,pic1), -1)
        int_neg = cv2.imread(os.path.join(inits_dir,pic2), -1)
        tmp_clk = cv2.imread(os.path.join(tmps_dir,pic3), -1)
    clk_pos = (int_pos==0) #矩阵初始化值全为0-False
    clk_neg = (int_neg==0) #矩阵初始化值全为0-False
    if pn == 0:#左键按下前景点
        clk_pos[y,x] = 1 #矩阵[clk.y,clk.x]处为1,即True
        int_pos = ndimage.distance_transform_edt(1-clk_pos)# 计算整张图的像素点到标注点的距离
        int_pos = np.uint8(np.minimum(np.maximum(int_pos, 0.0), 255.0)) #将范围取到[0,255]
        pic4=pic_id+'_pos_dt_%03d.png' %(cnt)
        pic5=pic_id+'_neg_dt_%03d.png' %(cnt)
        cv2.imwrite(os.path.join(inits_dir,pic4), int_pos) #存储前景点点击的距离图
        cv2.imwrite(os.path.join(inits_dir,pic5), int_neg) #存储背景点点击的距离图
        cv2.circle(tmp_clk, (x, y), 5, (0, 0, 255), -1) #opencv默认为BGR
    else:#右键按下背景点
        clk_neg[y,x] = 1 #矩阵[clk.y,clk.x]处为1,即True
        int_neg = ndimage.distance_transform_edt(1-clk_neg)
        int_neg = np.uint8(np.minimum(np.maximum(int_neg, 0.0), 255.0))
        pic6 = pic_id+'_pos_dt_%03d.png' % (cnt)
        pic7 = pic_id+'_neg_dt_%03d.png' % (cnt)
        cv2.imwrite(os.path.join(inits_dir,pic6), int_pos)
        cv2.imwrite(os.path.join(inits_dir,pic7), int_neg)
        cv2.circle(tmp_clk, (x, y), 5, (0, 255, 0), -1)
    input_pos_clks = deepcopy(int_pos)
    input_neg_clks = deepcopy(int_neg)
    input_pos_clks[int_pos != 0] = 255
    input_neg_clks[int_neg != 0] = 255
    input_ = np.expand_dims(np.float32(np.concatenate([input_image, np.expand_dims(int_pos, axis=2), np.expand_dims(int_neg, axis=2),
                                                      np.expand_dims(input_pos_clks, axis=2), np.expand_dims(input_neg_clks, axis=2)],axis=2)), axis=0)
    output_image = sess.run([network],feed_dict={input:input_,sz:[iH,iW]})
    output_image = np.minimum(np.maximum(output_image, 0.0), 1.0)
    output_image[np.where(output_image>0.5)]=1
    output_image[np.where(output_image<=0.5)]=0
    seg_filename=pic_id+'_%03d.png' % (cnt)
    seg_path=os.path.join(segs_dir,seg_filename)
    segmask = np.uint8(output_image[0, 0, :, :, 0] * 255.0)

    cv2.imwrite(seg_path, segmask)

    tmp_ol = cv2.imread(im_path, -1)
    tmp_ol[:, :, 0] = 0.5 * tmp_ol[:, :, 0] + 0.5 * segmask
    tmp_ol[:, :, 1] = 0.5 * tmp_ol[:, :, 1] + 0.5 * segmask
    tmp_ol[:, :, 2] = 0.5 * tmp_ol[:, :, 2] + 0.5 * segmask
    tmp_clk_filename=pic_id+'_clk_%03d.png' % (cnt)
    tmp_ol_filename=pic_id+'_ol_%03d.png' % (cnt)
    tmp_clk_path = os.path.join(tmps_dir,tmp_clk_filename)
    tmp_ol_path = os.path.join(tmps_dir,tmp_ol_filename)
    cv2.imwrite(tmp_clk_path, tmp_clk)
    cv2.imwrite(tmp_ol_path, tmp_ol)
    # 打点+mask的图片
    tmp_mix=deepcopy(tmp_ol)
    if pn==0:
        cv2.circle(tmp_mix, (x, y), 5, (0, 0, 255), -1)
    else:
        cv2.circle(tmp_mix, (x, y), 5, (0,255, 0), -1)
    tmp_mix_filename = pic_id + '_mix_%03d.png' % (cnt)
    tmp_mix_path=os.path.join(tmps_dir,tmp_mix_filename)
    cv2.imwrite(tmp_mix_path, tmp_mix)
    # 命名-四种图片[二值图,混合标注图,加了点的原图,加了点的混合标注图]
    pic_paths=[seg_path]
    pic_paths.append(tmp_ol_path)
    pic_paths.append(tmp_clk_path )
    pic_paths.append(tmp_mix_path)
    return  pic_paths
