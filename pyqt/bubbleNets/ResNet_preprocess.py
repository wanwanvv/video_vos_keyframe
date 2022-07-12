from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from tensorflow.contrib import slim
import os;
import pickle as pickle

import resnet_v2
import inception_preprocessing
## Functions ##################################################################
def resnet_process_data_dir(work_dir,data_dir,model_dir):
    resNet_path=os.path.join(work_dir,'ResNet')
    pickle_out = os.path.join(resNet_path, 'ResNet_preprocess.pk')
    if not os.path.exists(resNet_path):
        os.makedirs(resNet_path)
    if os.path.isfile(pickle_out):
        os.remove(pickle_out)
    print('ResNet preprocessing for ' + resNet_path)
    # Image directory info.
    img_files = sorted([name for name in os.listdir(data_dir) if _is_img(name)])
    print('data_dir:{}'.format(data_dir))
    print('frames_num:{}'.format(len(img_files)))
    print('img_files:')
    print(img_files)
    img_list = []
    for pic in img_files:
        img_list.append(os.path.join(data_dir, pic))
    # Pre-process using ResNet.
    img_size = resnet_v2.resnet_v2.default_image_size
    resnet_v2_model=os.path.join(model_dir,'resnet_v2_50.ckpt')
    print('resnet_v2_model:{}'.format(resnet_v2_model))
    with tf.Graph().as_default():
        processed_images = []
        for i, img in enumerate(img_list):
            # 读取图片并按照jpg格式转化为3通道的张量
            image = tf.image.decode_jpeg(tf.read_file(img), channels=3)
            # 预处理：双线性插值resize固定尺寸(224),中心裁剪0.875,float类型并且[0,1],normalization去均值化除以标准差
            processed_images.append(inception_preprocessing.preprocess_image(
                image, img_size, img_size, is_training=False))
        processed_images = tf.convert_to_tensor(processed_images)

        with slim.arg_scope(resnet_v2.resnet_arg_scope()):
            # Return ResNet 2048 vector.
            logits, _ = resnet_v2.resnet_v2_50(processed_images,
                                               num_classes=None, is_training=False)
        init_fn = slim.assign_from_checkpoint_fn(resnet_v2_model,slim.get_variables_to_restore())

        with tf.Session() as sess:
            init_fn(sess)
            np_images, resnet_vectors = sess.run([processed_images, logits])
            resnet_vectors = resnet_vectors[:, 0, 0, :]
    print('form pickle_data......')
    # Save preprocessed data to pickle file.
    pickle_data = {'frame_resnet_vectors': resnet_vectors}

    pickle.dump(pickle_data, open(pickle_out, 'wb'))
    print('resNet finished!')
    print('{} has been dumped over!'.format(pickle_out))

def _is_img(file_name):
    ext = file_name.split('.')[-1]
    return ext in ['jpg', 'jpeg', 'png', 'bmp']