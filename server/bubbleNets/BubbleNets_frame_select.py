import os,sys
import cv2
import time
import tensorflow as tf
from tensorflow.contrib import slim
import numpy as np
from copy import deepcopy
from matplotlib import pyplot as plt
root_folder2 = os.path.dirname(os.path.realpath(__file__))#当前py所在目录
parent_folder2 = os.path.dirname(root_folder2 )
sys.path.append(os.path.join(parent_folder2,'bubbleNets'))

#def BubbleNets_sort(data_dir,work_dir, model_dir,iter_time,model='BN0'):

#导入自定义模块
import bn_input
import bn_models
import bn_utils

def _is_img(file_name):
    ext = file_name.split('.')[-1]
    return ext in ['jpg', 'jpeg', 'png', 'bmp']

def BubbleNets_sort(data_dir,work_dir, model_dir,q,iter_time=5,model='BN0'):
    # Sorting parameters.
    num_frames = 0
    n_frames = 5
    n_ref = n_frames - 2
    n_batch = 5
    n_sorts=iter_time
    res_dir=work_dir
    # Prepare the tf input data.
    tf.logging.set_verbosity(tf.logging.INFO)
    input_vector = tf.placeholder(tf.float32, [None, (2048 + 1) * n_frames])
    input_label = tf.placeholder(tf.float32, [None, 1])
    # Select network model.
    if model == 'BNLF':
        ckpt_filename = os.path.join(model_dir,'BNLF_181030.ckpt-10000000')
        predict, end_pts = bn_models.BNLF(input_vector, is_training=False, n_frames=n_frames)
    else:
        ckpt_filename = os.path.join(model_dir,'BN0_181029.ckpt-10000000')
        predict, end_pts = bn_models.BN0(input_vector, is_training=False, n_frames=n_frames)
    # Initialize network and select frame.
    init = tf.global_variables_initializer()
    tic = time.time()
    print('开始进行bubbleNets排序.......')
    with tf.Session() as sess:
        #如果ckpt中记录的图结构或者一小部分tensor的name和我们程序里面构建的图不一样，用这个函数解决这个问题导入权重值
        init_fn = slim.assign_from_checkpoint_fn(ckpt_filename,slim.get_variables_to_restore())
        #参数(ckpt,variables_to_restore,ignore_missing_vars=True)True表明如果variables_to_restore中记录的tensor在ckpt中没有，那么就不对该tensor赋值
        init_fn(sess) #调用该函数
        select_dir = work_dir
        if not os.path.isdir(select_dir):
            os.makedirs(select_dir)
        text_out = os.path.join(select_dir, 'BN0.txt')
        if os.path.isfile(text_out):
            os.remove(text_out)
        print('\nRunning BubbleNets %s for video %s' % (model, work_dir))
        # Load ResNet vectors for network input.
        vector_file = os.path.join(res_dir, 'ResNet_preprocess.pk')
        input_data = bn_input.BN_Input(vector_file, n_ref=n_ref)
        num_frames = input_data.n_frames  # 图片数
        rank_bn = list(range(0, num_frames))
        rank_ids = list(range(0, num_frames))
        #存储预测的每帧的性能用于绘制条形图
        performances=list(range(0, num_frames))
        #performances[0]=10.0
        # BubbleNets Deep Sort.
        bubble_step = 1
        while bubble_step <= n_sorts:
            a = deepcopy(rank_bn[0])
            if bubble_step == n_sorts:
                performances[a]=10.0
            for i in range(1, num_frames):
                b = deepcopy(rank_bn[i])
                batch_vector = input_data.video_batch_n_ref_no_label(a, b, batch=n_batch)
                frame_select = sess.run(predict, feed_dict={input_vector: batch_vector})
                # If frame b is preferred, use frame b for next comparison.
                #print("i={} frame_select[0]={}".format(i,frame_select[0]))
                if bubble_step==n_sorts:
                    performances[b]=performances[a]-frame_select[0][0]*1000
                #print(frame_select)
                if np.mean(frame_select[0]) < 0:
                    rank_bn[i - 1] = a
                    rank_bn[i] = b
                    a = deepcopy(b)
                else:
                    rank_bn[i - 1] = b
                    rank_bn[i] = a
            bubble_step += 1
            print('bubble_step-{} rank_bn:'.format(bubble_step))
            print(rank_bn)
        # Write out frame selection to text file.
        select_idx = rank_bn[-1]
        img_files=sorted([name for name in os.listdir(data_dir) if _is_img(name)])
        img_file = img_files[select_idx]
        statements = [model, '\n', str(select_idx), '\n', img_file, '\n']
        bn_utils.print_statements(text_out, statements)
        sess.close()
    tf.reset_default_graph()
    toc = time.time()
    print('bubbleNets排序完成...time:{}'.format(toc-tic))
    #倒序
    for i in range(0,num_frames):
        rank_ids[i]=rank_bn[num_frames-i-1]
    rank_performances = list(range(0, num_frames))
    for index in range(0,num_frames):
        rank_performances[index]=performances[rank_bn[index]]
    print('rank_performances:')
    print(rank_performances)
    print('rank_ids')
    print(rank_ids)
    #matplotlib绘制条形图
    fig=plt.figure(figsize=(10,5))
    y_pos=np.arange(len(rank_performances))
    y_pos=[x for x in rank_performances]
    bar_labels=np.arange(len(rank_bn))
    bar_labels=[str(r) for r in rank_bn]
    x_pos=list(range(len(bar_labels)))
    last = len(bar_labels) - 1
    #rank_performances_bk=rank_performances[0:last-1]
    plt.bar(x_pos,rank_performances,color='skyBlue')
    #plt.bar(last,rank_performances[last],color='green')
    #设置y轴高度
    max_y=max(rank_performances)
    plt.ylim(0,max_y*1.1)
    #设置轴标签和标题
    plt.ylabel('predict performances y')
    plt.xticks(x_pos,bar_labels)
    plt.tick_params(labelsize=6) #刻度字体大小
    plt.title('BubbleNets Frame Sort')
    #显示和保存图片
    #plt.show()
    sort_pic_path=os.path.join(work_dir,'sort.png')
    plt.savefig(sort_pic_path)
    print('绘制条形结果图:{}'.format(sort_pic_path))
    #返回视频帧的尺寸
    pic1=os.path.join(data_dir,img_files[0])
    (height,width,channel)=cv2.imread(pic1).shape
    #按顺序返回图片名
    img_files_sort = []
    for i in range(num_frames):
        img_files_sort.append(img_files[rank_ids[i]])
    return_json={}
    return_json['images']=img_files_sort
    return_json['indexes']=rank_ids
    return_json['width']=width
    return_json['height']=height
    q.put(return_json)
    #return return_json

#if __name__=="__main__":
#    pic1='/home/workspace/project/src_frames/1586441646/car-shadow_00000.jpg'
#    (height,width,channel)=cv2.imread(pic1).shape
#    print("height:{}".format(height))
#    print("width:{}".format(width))
