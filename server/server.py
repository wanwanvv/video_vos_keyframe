from flask import Flask, render_template, jsonify, request, make_response, send_from_directory, abort,Response,make_response
import time
import os,sys
import base64
import json
import math
from multiprocessing import Process
from multiprocessing import Queue
from flask_sqlalchemy import SQLAlchemy
from shutil import copyfile
root_folder=os.path.dirname(__file__)
sys.path.append(root_folder)
sys.path.append(os.path.join(root_folder,'bubbleNets'))
sys.path.append(os.path.join(root_folder,'ivs'))
sys.path.append(os.path.join(root_folder,'osvos'))
sys.path.append(os.path.join(root_folder,'removal'))

# 导入的自定义的包
import utils
from utils import video_to_frames,getImages,getFrameShape,allowed_file,removeTmpDir,frames_to_video,overlay_vos_src,overlay_mask_src,changeImageSize,changeImageSize1
from BubbleNets_frame_select import BubbleNets_sort
from ResNet_preprocess import resnet_process_data_dir
from propagate_model import vos_model
from interact_model import int_model
from RGMP_thread import VosRGMP_thread
from CPNet_thread import InpaintingCPNet_thread
# 保存上传的视频的文件夹
UPLOAD_FOLDER=os.path.join(root_folder,"upload")
#保存提取的视频帧文件夹
SRC_FRAMES_FOLDER=os.path.join(root_folder,"src_frames")
# 保存模型models的文件夹
MODELS_FOLDER=os.path.join(root_folder,"models")
# 保存目标分割结果的文件夹
VOS_RESULTS_FOLDER=os.path.join(root_folder,"VosResults")
# 保存移除结果图片帧的文件夹
INPAINTING_RESULTS_FOLDER=os.path.join(root_folder,"InpaintingResults")
# 保存目标分割和目标移除的video的文件夹
VOS_VIDEOS_FOLDER=os.path.join(root_folder,"VosVideos")
# 保存removal初始视频
REMOVAL_VIDEOS_FOLDER=os.path.join(root_folder,"RemovalVideos")
# ImageSets存储val.txt的文件夹
IMAGESETS_FOLDER=os.path.join(root_folder,"ImageSets")
# 保存交互式图像分割结果图片
ANNOTATE_FRAMES_FOLDER=os.path.join(root_folder,"annotate_frames")
# 保存缩放后的removal图片帧的文件夹
INPAINTING_RESULTS_SCALE_FOLDER=os.path.join(root_folder,"InpaintingResults_scale")
# 保存vos合并后的原始图片帧的文件夹
VOS_OVERLAY_RESULTS_FOLDER=os.path.join(root_folder,"VosOverlayResults")
# 保存缩放后的vos合并后的原始图片帧的文件夹
VOS_OVERLAY_RESULTS_SCALE_FOLDER=os.path.join(root_folder,"VosOverlayResults_scale")
# 保存缩放后的导出vos视频
VOS_VIDEOS_SCALE_FOLDER=os.path.join(root_folder,"VosVideos_scale")
# 保存removal缩放后的导出视频
REMOVAL_VIDEOS_SCALE_FOLDER=os.path.join(root_folder,"RemovalVideos_scale")
# 保存ResNet.pk以及bubbleNets的txt和排序图片
RESNET_FOLDER=os.path.join(root_folder,"ResNet")

app=Flask(__name__)
app.config['INPAINTING_RESULTS_SCALE_FOLDER'] = INPAINTING_RESULTS_SCALE_FOLDER
app.config['VOS_OVERLAY_RESULTS_FOLDER'] = VOS_OVERLAY_RESULTS_FOLDER
app.config['VOS_OVERLAY_RESULTS_SCALE_FOLDER'] = VOS_OVERLAY_RESULTS_SCALE_FOLDER
app.config['VOS_VIDEOS_SCALE_FOLDER'] = VOS_VIDEOS_SCALE_FOLDER
app.config['REMOVAL_VIDEOS_SCALE_FOLDER'] = REMOVAL_VIDEOS_SCALE_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SRC_FRAMES_FOLDER'] = SRC_FRAMES_FOLDER
app.config['MODELS_FOLDER'] = MODELS_FOLDER
app.config['VOS_RESULTS_FOLDER'] = VOS_RESULTS_FOLDER
app.config['INPAINTING_RESULTS_FOLDER'] = INPAINTING_RESULTS_FOLDER
app.config['VOS_VIDEOS_FOLDER'] = VOS_VIDEOS_FOLDER
app.config['REMOVAL_VIDEOS_FOLDER'] = REMOVAL_VIDEOS_FOLDER
app.config['IMAGESETS_FOLDER'] = IMAGESETS_FOLDER
app.config['ANNOTATE_FRAMES_FOLDER'] = ANNOTATE_FRAMES_FOLDER
app.config['RESNET_FOLDER'] = RESNET_FOLDER
# mysql数据库文件存放地址
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:123456@localhost:3306/videoInfo?charset=utf8'
#配置flask配置对象中键：SQLALCHEMY_COMMIT_TEARDOWN,设置为True,应用会自动在每次请求结束后提交数据库中变动
app.config['SQLALCHEMY_COMMIT_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 创建数据库对象
db = SQLAlchemy(app)

class VideoInfo(db.Model):
    __tablename__='videos'#表名
    # 定义列对象
    videoTag = db.Column(db.String(10), primary_key=True)
    videoName = db.Column(db.String(50))
    srcFps = db.Column(db.Integer)
    srcWidth = db.Column(db.Integer)
    srcHeight = db.Column(db.Integer)
    framesNum = db.Column(db.Integer)
    #repr()方法显示一个可读字符串
    def __repr__(self):
        return 'Role:%s'% self.videoName

#*********自定义函数**********
def interact_thread(scribbles,frames_path,model_prefix):
    ivs_model=int_model(frames_path,model_prefix)
    ivs_model.Run_interaction(scribbles)
    ivs_model.get_result_pics(scribbles)

def ivs_vos_thread(target,scribbles,frames_path,model_prefix,vos_mask_dir,vos_viz_dir):
    ivs_model=vos_model(frames_path,model_prefix)
    ivs_model.Run_interaction(scribbles)
    ivs_model.Run_propagation(target,mode='linear', at_least=-1)
    ivs_model.get_vos_mask_pics(vos_mask_dir,vos_viz_dir)

def rgmp_vos_thread(choose_mask_pic,src_frames_path,vos_mask_dir,model_prefix,ImageSets_path,filename):
    rgmpInfo={}
    rgmpInfo['MO']=False
    rgmpInfo['annotation_path'] = os.path.dirname(choose_mask_pic)
    rgmpInfo['frmas_path'] = src_frames_path
    rgmpInfo['mask_img'] = choose_mask_pic
    rgmpInfo['result_dir'] = vos_mask_dir
    rgmpInfo['model_dir'] = model_prefix
    rgmpInfo['ImageSets_path'] = ImageSets_path
    rgmpInfo['imset'] = filename
    rgmp_object=VosRGMP_thread(rgmpInfo)
    rgmp_object.Vosrgmp_work()

def removal_thread(model_prefix,frameWidth,frameHeight,removal_video_dir,vos_mask_dir,frames_path,removal_result_dir,ImageSets_path,filename1):
    maskInfo={}
    maskInfo['model_folder'] = model_prefix
    maskInfo['width'] = frameWidth
    maskInfo['height'] = frameHeight
    maskInfo['video_dir'] = removal_video_dir
    maskInfo['annotation_path'] = vos_mask_dir
    maskInfo['frames_path'] = frames_path
    maskInfo['result_dir'] = removal_result_dir
    maskInfo['ImageSets_path'] = ImageSets_path
    maskInfo['imset'] = filename1
    inpainting_object=InpaintingCPNet_thread(maskInfo)
    inpainting_object.InpaintingCPNet_work()

# 连接测试
@app.route('/vos/test')
def connect_test():
    return "Welcome to VOS api!"

# 上传文件
@app.route('/vos/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(app.config['UPLOAD_FOLDER'],"video")
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = f.filename
        print("fname:{}".format(fname))
        ext = fname.rsplit('.', 1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename = str(unix_time) + '.' + ext  # 修改了上传的文件名
        f.save(os.path.join(file_dir, new_filename))  # 保存文件到upload目录
        video_path=os.path.join(file_dir, new_filename)
        print("new_filename:{}".format(new_filename))
        video_name=fname.split('.')[0]
        unix_time_str=str(unix_time)
        #videoNames[unix_time_str] = video_name
        result_path = os.path.join(app.config['SRC_FRAMES_FOLDER'],unix_time_str)
        current_frames_folder = result_path
        [piclength,fps]=video_to_frames(video_name,video_path,result_path)
        # 存储tag对应的原图片尺寸
        (height,width,channel)=getFrameShape(result_path)
        videoin=VideoInfo(videoTag=unix_time_str,videoName=video_name,srcFps=int(fps),srcWidth=height,srcHeight=width,framesNum=piclength)
        db.session.add(videoin)
        db.session.commit()
        #frameSize[unix_time_str]=[width,height]
        return jsonify([{"errno": 0, "errmsg": "upload sucess","tag":unix_time_str,"piclength":piclength,"videoname":video_name}])
    else:
        return jsonify([{"errno": 1001, "errmsg": "upload failed","tag":"","piclength":0,"videoname":""}])
    
# 获取加载图片
@app.route("/vos/download/<filedir>/<filename>")
def download(filedir,filename):
    #if request.method == "GET":
    pic_folder=os.path.join(app.config['SRC_FRAMES_FOLDER'],filedir)
    if os.path.isfile(os.path.join(pic_folder, filename)):
        return send_from_directory(pic_folder, filename, as_attachment=True)
    else:
        #abort(404)立即停止视图函数的执行，并且把相对应的信息返回到前端中
        return "404"

@app.route("/vos/sortresult/<tag>")
def showSortResult(tag):
    #if request.method == "GET":
    res_folder = os.path.join(app.config['RESNET_FOLDER'],tag)
    #ok_html_path=os.path.join(app.config['RESNET_FOLDER'],'sort_result.html')
    #no_html_path=os.path.join(app.config['RESNET_FOLDER'],'no_result.html')
    file_name = os.path.join(res_folder,'BN0.txt')
    sort_file = '/static/images/sort.png'
    src_sort_file = os.path.join(res_folder,'sort.png')
    dst_sort_file = os.path.join(root_folder,'static','images','sort.png')
    if os.path.isfile(sort_file):
        os.remove(sort_file)    
    model='BN0'
    index=0
    if os.path.exists(res_folder):
        try:
            copyfile(src_sort_file,dst_sort_file)
        except:
            print("Unexpected error:", sys.exc_info())
        read_list = open(file_name,'r').readlines()
        model=read_list[0].strip('\n')
        index = read_list[1].strip('\n')
        print("model:{} index:{}".format(model,index))
        return render_template('sort_result.html',model=model,index=index,sort_file=sort_file)
    else:
        # 返回无结果html
        return render_template('no_result.html')

# 下载保存服务器上的图片
@app.route("/vos/imagedownload/<filetype>/<filetag>/<fileindex>")
def downloadImage(filetype,filetag,fileindex):
    #if request.method == "GET":
    image_folder=None
    image_name=None
    if filetype=="mask":
        print("***************download image mask:***************")
        mask_index = int(fileindex)
        image_folder=os.path.join(app.config['VOS_RESULTS_FOLDER'],filetag)
        image_name='{:05d}.png'.format(mask_index)
    else:
        print("***************download image annotation:***************")
        image_folder=os.path.join(app.config['ANNOTATE_FRAMES_FOLDER'],filetag,fileindex+'_ivsTmp')
        image_name=fileindex+"_viz.jpg"
    image=os.path.join(image_folder, image_name)
    if os.path.isfile(image):
        print("存在下载图片:{}".format(image))
        return send_from_directory(image_folder, image_name, as_attachment=True)
    else:
        #abort(404)立即停止视图函数的执行，并且把相对应的信息返回到前端中
        return "404"

#bubblenets返回图片帧顺序
@app.route("/vos/bubblenet",methods = ['GET','POST'])
def bubblenet( ):
    model=request.form['model']
    iterTime=int(request.form['itertime'])    
    tag=request.form['tag']
    dataDir=os.path.join(app.config['SRC_FRAMES_FOLDER'],tag)
    workDir=os.path.join(app.config['RESNET_FOLDER'],tag)
    if not os.path.exists(workDir):
        os.makedirs(workDir)
    modelDir=app.config['MODELS_FOLDER']
    p1 = Process(target=resnet_process_data_dir, args=(workDir,dataDir,modelDir))
    p1.start()
    p1.join()
    p1.terminate()
    q = Queue()
    p2 = Process(target=BubbleNets_sort, args=(dataDir,workDir, modelDir,q,iterTime,model))
    p2.start()
    p2.join()
    results=q.get()
    print("results:")
    print(results)
    q.close()
    p2.terminate()
    #resnet_process_data_dir(workDir,dataDir,modelDir)  # 在每个data文件夹下生成经过resnet预处理的pk文件
    #return_json=BubbleNets_sort(dataDir,workDir, modelDir,iterTime,model)  # 输出用BN模型预测的最佳性能帧,放在data目录下的txt文件中
    return_json=results
    return_json['tag']=tag
    videoin2=VideoInfo.query.filter_by(videoTag=tag).first()
    return_json['fps']=videoin2.srcFps
    return jsonify(return_json)

# 移除目标物体
@app.route("/vos/removal",methods = ['POST'])
def removal( ):    
    tag=request.form["tag"]
    target=request.form["target"]
    frames_path=getImages(os.path.join(app.config['SRC_FRAMES_FOLDER'],tag))
    model_prefix = app.config['MODELS_FOLDER']
    vos_mask_dir=os.path.join(app.config['VOS_RESULTS_FOLDER'],tag)
    if not os.path.exists(vos_mask_dir):
        os.makedirs(vos_mask_dir)
    vos_viz_dir=os.path.join(app.config['VOS_OVERLAY_RESULTS_FOLDER'],tag)
    if not os.path.exists(vos_viz_dir):
        os.makedirs(vos_viz_dir)
    choose_mask_pic = os.path.join(app.config['ANNOTATE_FRAMES_FOLDER'],tag,target+'_ivsTmp',target+'_mask.png')
    src_frames_path = os.path.join(app.config['SRC_FRAMES_FOLDER'],tag)
    ImageSets_path=os.path.join(app.config['IMAGESETS_FOLDER'],tag)
    if not os.path.exists(ImageSets_path):
        os.makedirs(ImageSets_path)
    filename='val.txt'
    videoin1=VideoInfo.query.filter_by(videoTag=tag).first()
    video_name=videoin1.videoName
    fps=videoin1.srcFps
    with open(os.path.join(ImageSets_path,filename),'w') as valfile:
        valfile.write(video_name+'\n')
    print("rgmp_thread start.......")
    p6 = Process(target=rgmp_vos_thread, args=(choose_mask_pic,src_frames_path,vos_mask_dir,model_prefix,ImageSets_path,filename))
    p6.start()
    p6.join()
    #p6.terminate()
    print("rgmp_thread finish.......") 
    # inpainting
    (frameHeight,frameWidth,channel)=getFrameShape(src_frames_path)
    removal_video_dir=os.path.join(app.config['REMOVAL_VIDEOS_FOLDER'],tag)
    removal_result_dir=os.path.join(app.config['INPAINTING_RESULTS_FOLDER'],tag)
    if not os.path.exists(removal_video_dir):
        os.makedirs(removal_video_dir)
    if not os.path.exists(removal_result_dir):
        os.makedirs(removal_result_dir)
    filename1 = 'val1.txt'
    with open(os.path.join(ImageSets_path,filename1),'w') as valfile:
        valfile.write(video_name+'\n')
    valfile.close()
    print("removal_thread start.......")
    p7 = Process(target=removal_thread,args=(model_prefix,frameWidth,frameHeight,removal_video_dir,vos_mask_dir,src_frames_path,removal_result_dir,ImageSets_path,filename1))
    p7.start()
    p7.join()
    #p7.terminate()
    print("removal_thread finish.......")
    removalVideoName=video_name+"_removal.mp4"
    save_path_prefix=os.path.join(app.config['REMOVAL_VIDEOS_FOLDER'],tag)
    if not os.path.exists(save_path_prefix):
        os.makedirs(save_path_prefix)
    save_path=os.path.join(save_path_prefix,removalVideoName)
    frames_to_video(fps,save_path,removal_result_dir,type='MP4')
    print('removal frames_to_video完成.......')
    return_string=tag+"/"+removalVideoName
    if os.path.isfile(save_path):
        return return_string
    else:
        return "404"

# 分割目标物体
@app.route("/vos/ivs",methods = ['POST'])
def ivsVos( ):
    tag=request.form["tag"]
    target=request.form["target"]
    frames_path=getImages(os.path.join(app.config['SRC_FRAMES_FOLDER'],tag))
    model_prefix = app.config['MODELS_FOLDER']
    vos_mask_dir=os.path.join(app.config['VOS_RESULTS_FOLDER'],tag)
    if not os.path.exists(vos_mask_dir):
        os.makedirs(vos_mask_dir)
    vos_viz_dir=os.path.join(app.config['VOS_OVERLAY_RESULTS_FOLDER'],tag)
    if not os.path.exists(vos_viz_dir):
        os.makedirs(vos_viz_dir)
    #json_file=os.path.join(root_folder,'scribbles.json')
    #scribbles = {}
    #with open(json_file,'r') as fileR:   #打开文本读取状态
            #scribbles = json.load(fileR)  #解析读到的文本内容 转为python数据 以一个变量接收
            #fileR.close()  #关闭文件
    #p5 = Process(target=ivs_vos_thread, args=(target,scribbles,frames_path,model_prefix,vos_mask_dir,vos_viz_dir))
    #p5.start()
    #p5.join()
    #p5.terminate()
    choose_mask_pic = os.path.join(app.config['ANNOTATE_FRAMES_FOLDER'],tag,target+'_ivsTmp',target+'_mask.png')
    src_frames_path = os.path.join(app.config['SRC_FRAMES_FOLDER'],tag)
    ImageSets_path=os.path.join(app.config['IMAGESETS_FOLDER'],tag)
    if not os.path.exists(ImageSets_path):
        os.makedirs(ImageSets_path)
    filename='val.txt'
    videoin1=VideoInfo.query.filter_by(videoTag=tag).first()
    video_name=videoin1.videoName
    fps=videoin1.srcFps
    with open(os.path.join(ImageSets_path,filename),'w') as valfile:
        valfile.write(video_name+'\n')
    valfile.close()
    print("rgmp_thread start.......")
    p5 = Process(target=rgmp_vos_thread, args=(choose_mask_pic,src_frames_path,vos_mask_dir,model_prefix,ImageSets_path,filename))
    p5.start()
    p5.join()
    p5.terminate()        
    print("rgmp_thread finish.......")
    overlay_vos_src(src_frames_path,vos_mask_dir,vos_viz_dir)
    print("form mask_images,overlay_images finish......")
    vosVideoName=video_name+"_vos.mp4"
    save_path_prefix=os.path.join(app.config['VOS_VIDEOS_FOLDER'],tag)
    if not os.path.exists(save_path_prefix):
        os.makedirs(save_path_prefix)
    save_path=os.path.join(save_path_prefix,vosVideoName)
    frames_to_video(fps,save_path,vos_viz_dir,type='MP4') 
    print('vos frames_to_video完成.......')
    vosVideoPath=os.path.join(app.config['VOS_VIDEOS_FOLDER'],tag)
    vosVideo=os.path.join(vosVideoPath,vosVideoName)
    return_string=tag+"/"+vosVideoName
    if os.path.isfile(vosVideo):
        return return_string
    else:
        return "404"

# 获取vos默认结果视频
@app.route("/vos/vosvideo/<filedir>/<filename>")
def downloadVideo(filedir,filename):
    #if request.method == "GET":
    vosVideoPath=os.path.join(app.config['VOS_VIDEOS_FOLDER'],filedir)
    vosVideo=os.path.join(vosVideoPath,filename)
    if os.path.isfile(os.path.join(vosVideoPath, filename)):
        print("存在分割结果视频：{}".format(vosVideo))
        return send_from_directory(vosVideoPath, filename, as_attachment=True)
    else:
        #abort(404)立即停止视图函数的执行，并且把相对应的信息返回到前端中
        return "404"

# 获取removal默认结果视频
@app.route("/vos/removalvideo/<filedir>/<filename>")
def downloadRemovalVideo(filedir,filename):
    #if request.method == "GET":
    removalVideoPath=os.path.join(app.config['REMOVAL_VIDEOS_FOLDER'],filedir)
    removalVideo=os.path.join(removalVideoPath,filename)
    if os.path.isfile(removalVideo):
        print("存在removal结果视频：{}".format(removalVideo))
        return send_from_directory(removalVideoPath, filename, as_attachment=True)
    else:
        #abort(404)立即停止视图函数的执行，并且把相对应的信息返回到前端中
        return "404"
    
# 返回标注的单帧图片
@app.route("/vos/annotate",methods = ['POST'])
def annotate( ):
    jsonString=request.data.decode()
    jsonObject=eval(jsonString)
    add=jsonObject["add"]
    tag=jsonObject["tag"]
    size=jsonObject["size"]
    index=jsonObject["index"]
    xposes=jsonObject["xposes"]
    yposes=jsonObject["yposes"]
    xposes_line=jsonObject["xposes_line"]
    yposes_line=jsonObject["yposes_line"]
    anno_type=jsonObject["type"]
    print("anno_type:{} anno_type:{}".format(anno_type,type(anno_type)))
    #****交互式图像分割标注线程*********
    frames_path=getImages(os.path.join(app.config['SRC_FRAMES_FOLDER'],tag))
    num_frames=len(frames_path)
    model_prefix = app.config['MODELS_FOLDER']
    json_file=os.path.join(root_folder,'scribbles.json')
    scribbles = {}
    # 添加到scribbles里
    if add==0:
        scribbles = {}
        scribbles['scribbles'] = [[] for _ in range(num_frames)]
        print("add=0 reset Scribbles......")
    elif add==1:
        print("add=1")
        with open(json_file,'r') as fileR:   #打开文本读取状态
            scribbles = json.load(fileR)  #解析读到的文本内容 转为python数据 以一个变量接收
            fileR.close()  #关闭文件
    scribbles['annotated_frame'] = index
    anno_frames_folder=os.path.join(app.config['ANNOTATE_FRAMES_FOLDER'],tag)
    if not os.path.exists(anno_frames_folder):
        os.makedirs(anno_frames_folder)
    annotate_frame_dir= os.path.join(anno_frames_folder,str(index) + '_ivsTmp')
    if os.path.exists(annotate_frame_dir):
        removeTmpDir(annotate_frame_dir)
    os.makedirs(annotate_frame_dir) 
    scribbles['annotate_frame_dir'] = annotate_frame_dir
    stroke = {}
    stroke['path']=[]
    stroke['line_path']=[]
    for i in range(len(xposes)):
        stroke['path'].append([xposes[i],yposes[i]])
    for i in range(len(xposes_line)):
        stroke['line_path'].append([xposes_line[i],yposes_line[i]])
    stroke['object_id'] = anno_type
    scribbles['scribbles'][index].append(stroke)
    print("type:{} scribbles:".format(type(scribbles)))
    print(scribbles)
    #运行模型
    print("start int_model......")
    p3 = Process(target=interact_thread, args=(scribbles,frames_path,model_prefix))
    p3.start()
    p3.join()
    p3.terminate()
    print("finish int_model......")    
    result_viz_pic=os.path.join(annotate_frame_dir,str(index)+'_viz.jpg')
    #if os.path.isfile(json_file):
        #os.remove(json_file)
    with open(json_file,'w') as fileW:  #如果该文件已存在则将其覆盖。如果该文件不存在，创建新文件。
        json.dump(scribbles, fileW)  #data转换为json数据格式并写入文件
        fileW.close()  #关闭文件
    #****交互式图像分割标注线程*********
    #返回图像分割结果图片
    if os.path.isfile(result_viz_pic):
        return "100"
    else:
        return "404"

# 获取交互式分割结果图片
@app.route("/vos/annotateres/<filedir>/<fileindex>")
def annotateResource(filedir,fileindex):
    #if request.method == "GET":
    pic_folder=os.path.join(app.config['ANNOTATE_FRAMES_FOLDER'],filedir,fileindex+'_ivsTmp')
    viz_pic=fileindex+'_viz.jpg'
    if os.path.isfile(os.path.join(pic_folder, viz_pic)):
        print("存在viz图片......")
        return send_from_directory(pic_folder, viz_pic, as_attachment=True)
    else:
        #abort(404)立即停止视图函数的执行，并且把相对应的信息返回到前端中
        return "404"

# 导出vosVideo视频
@app.route("/vos/output/vosvideo",methods = ['POST'])
def outpputVosVideo( ):
    print("****************output/vosvideo*************")
    jsonString=request.data.decode()
    jsonObject=eval(jsonString)
    print("jsonObject:")
    print(jsonObject)
    video_name=jsonObject["video_name"]
    video_type=jsonObject["video_type"]
    video_fps=jsonObject["video_fps"]
    video_scale=jsonObject["video_scale"]
    tag=jsonObject["tag"]
    video_full_name = video_name+'.mp4'
    if video_type=="AVI":
        video_full_name= video_name+'.avi'
    save_path_prefix=os.path.join(app.config['VOS_VIDEOS_SCALE_FOLDER'],tag)
    if not os.path.exists(save_path_prefix):
        os.makedirs(save_path_prefix)
    save_path=os.path.join(save_path_prefix,video_full_name)
    vos_frames_dir=os.path.join(app.config['VOS_OVERLAY_RESULTS_FOLDER'],tag)    
    vos_frames_scale_dir=os.path.join(app.config['VOS_OVERLAY_RESULTS_SCALE_FOLDER'],tag)
    (height,width,channel)=getFrameShape(vos_frames_dir)
    #修改尺寸
    if math.isclose(video_scale, 1.0, rel_tol=1e-9):
        frames_to_video(video_fps,save_path,vos_frames_dir,video_type)
        print("scale=1.0 frames_to_videos finish......")
    else:
        if not os.path.exists(vos_frames_scale_dir):
            os.makedirs(vos_frames_scale_dir)
        changeImageSize(vos_frames_dir,vos_frames_scale_dir,width,height,video_scale)        
        frames_to_video(video_fps,save_path,vos_frames_scale_dir,video_type)
        print("scale={} frames_to_videos finish......".format(video_scale))
    #返回数据
    return_json={}
    return_json['outputtag']=tag
    return_json['outputflag']="vos"
    return_json['outputvideo']=video_full_name
    if os.path.isfile(save_path):
        return jsonify(return_json)
    else:
        return "404"

#直接返回视频文件
@app.route("/vos/output/filedownload/<outputflag>/<outputtag>/<outputvideo>")
def downloadUserVideo(outputflag,outputtag,outputvideo):
    #if request.method == "GET":
    downloadVideo_prefix=os.path.join(app.config['VOS_VIDEOS_SCALE_FOLDER'],outputtag)
    if outputflag=="removal":
       downloadVideo_prefix=os.path.join(app.config['REMOVAL_VIDEOS_SCALE_FOLDER'],outputtag)
    response = make_response(send_from_directory(downloadVideo_prefix, outputvideo, as_attachment=True))
    #文件名包括中文
    response.headers["Content-Disposition"] = "attachment; filename{}".format(outputvideo.encode().decode('latin-1'))
    return response

# 流式下载视频文件
@app.route("/vos/output/videodownload/<outputflag>/<outputtag>/<outputvideo>")
def downloadUserVideoStream(outputflag,outputtag,outputvideo):
    #if request.method == "GET"
    tag=outputtag
    downloadedLength = int(request.headers.get("RANGE"))
    downloadVideo_prefix=os.path.join(app.config['VOS_VIDEOS_SCALE_FOLDER'],tag)
    print("从{}字节开始下载.......".format(downloadedLength))
    if outputflag=="removal":
       downloadVideo_prefix=os.path.join(app.config['REMOVAL_VIDEOS_SCALE_FOLDER'],tag)
    video_path=os.path.join(downloadVideo_prefix, outputvideo)
    print("video_path:{}".format(video_path))
    def send_chunk():  # 流式读取
        store_path=video_path
        downloadLength=downloadedLength
        #with open(store_path,'rb') as target_file:
        #    target_file.seek(downloadLength,0)
        #    print("开始下载的位置:{}".format(target_file.tell()))
        #    data=target_file.read()
        with open(store_path,'rb') as target_file:
            target_file.seek(downloadLength,0)
            print("开始下载的位置:{}".format(target_file.tell()))
            while 1:
                data=target_file.read()
                print("data length:{}".format(len(data)))
                if not data:
                    break
                yield data
    if os.path.isfile(video_path):
        response = Response(send_chunk(), content_type='application/octet-stream')
        response.headers["Content-Disposition"] = 'attachment; filename='+outputvideo
        return response
        #return send_from_directory(downloadVideo_prefix, outputvideo, as_attachment=True)
    else:
        #abort(404)立即停止视图函数的执行，并且把相对应的信息返回到前端中
        return "404"

# 导出removalVideo视频
@app.route("/vos/output/removalvideo",methods = ['POST'])
def outputRemovalVideo( ):
    print("****************output/removalvideo*************")
    jsonString=request.data.decode()
    jsonObject=eval(jsonString)
    print("jsonObject:")
    print(jsonObject)
    video_name=jsonObject["video_name"]
    video_type=jsonObject["video_type"]
    video_fps=jsonObject["video_fps"]
    video_scale=jsonObject["video_scale"]
    tag=jsonObject["tag"]
    video_full_name = video_name+'.mp4'
    if video_type=="AVI":
        video_full_name= video_name+'.avi'
    save_path_prefix=os.path.join(app.config['REMOVAL_VIDEOS_SCALE_FOLDER'],tag)
    if not os.path.exists(save_path_prefix):
        os.makedirs(save_path_prefix)
    save_path=os.path.join(save_path_prefix,video_full_name)
    vos_frames_dir=os.path.join(app.config['INPAINTING_RESULTS_FOLDER'],tag)
    vos_frames_scale_dir=os.path.join(app.config['INPAINTING_RESULTS_SCALE_FOLDER'],tag)
    if not os.path.exists(vos_frames_scale_dir):
        os.makedirs(vos_frames_scale_dir)
    #(height,width,channel)=getFrameShape(vos_frames_dir)
    videoin3=VideoInfo.query.filter_by(videoTag=tag).first()
    scale_width=videoin3.srcWidth
    scale_height=videoin3.srcHeight
    #修改尺寸
    if math.isclose(video_scale, 1.0, rel_tol=1e-9):
        print("scale=1.0 scale_width:{} scale_height:{} frames_to_videos start......".format(scale_width,scale_height))
    else:
        scale_width=int(scale_width*video_scale)
        scale_height=int(scale_height*video_scale)
        print("scale!=1.0 scale_width:{} scale_height:{} frames_to_videos start......".format(scale_width,scale_height))
    changeImageSize1(vos_frames_dir,vos_frames_scale_dir,scale_width,scale_height)
    frames_to_video(video_fps,save_path,vos_frames_scale_dir,video_type)
    #返回数据
    return_json={}
    return_json['outputtag']=tag
    return_json['outputflag']="removal"
    return_json['outputvideo']=video_full_name
    if os.path.isfile(save_path):
        return jsonify(return_json)
    else:
        return "404"


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    print("建立数据表......")
    app.run(host="0.0.0.0",port="11044",debug=True)
