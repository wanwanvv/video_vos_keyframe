package com.example.androidapplication;

import android.Manifest;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.IBinder;
import android.os.Message;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.Display;
import android.view.View;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.multidex.MultiDex;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;
import androidx.viewpager.widget.ViewPager;

import com.bigkoo.alertview.AlertView;
import com.bigkoo.alertview.OnDismissListener;
import com.bigkoo.alertview.OnItemClickListener;
import com.example.androidapplication.adapter.MyViewPager;
import com.example.androidapplication.adapter.ViewPagerAdapter;
import com.example.androidapplication.base.BaseLazyFragment;
import com.example.androidapplication.base.BasicActivity;
import com.example.androidapplication.bean.BubblenetBean;
import com.example.androidapplication.bean.VideoNameBean;
import com.example.androidapplication.downloadservice.DownloadService;
import com.example.androidapplication.http.MyConstant;
import com.example.androidapplication.http.Urls;
import com.example.androidapplication.utils.StorageUtil;
import com.vincent.filepicker.Constant;
import com.vincent.filepicker.activity.VideoPickActivity;
import com.vincent.filepicker.filter.entity.VideoFile;
import com.wuhenzhizao.titlebar.widget.CommonTitleBar;
import com.zaaach.toprightmenu.MenuItem;
import com.zaaach.toprightmenu.TopRightMenu;

import java.util.ArrayList;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;

import static com.vincent.filepicker.activity.BaseActivity.IS_NEED_FOLDER_LIST;
import static com.vincent.filepicker.activity.ImagePickActivity.IS_NEED_CAMERA;

public class FirstActivity extends BasicActivity {
    private static final String TAG = "FirstActivity";
    @BindView(R.id.titlebar)
    CommonTitleBar titlebar;
    @BindView(R.id.view_pager)
    MyViewPager viewPager;
    @BindView(R.id.swiper_linearlayout)
    LinearLayout swiperLinearlayout;
    @BindView(R.id.swiper_refresh_layout)
    SwipeRefreshLayout swiperRefreshLayout;

    /*****************menu***************/
    //弹出菜单
    private TopRightMenu mTopRightMenu;
    //按钮imageView
    private ImageView moreBtn;
    //版本弹出框
    private AlertView versionAlertView;
    /***************menu*************/

    public static float density;
    public static float dpWidth;
    public static float dpHeight;
    public static float pixWidth;
    public static float pixHeight;
    public VideoNameBean videoNameBean;
    public int choose_position;
    public String annotate_tag="1500000000";
    public String result_videoUrl;
    public String result_flag;
    public String downloadUrl;//下载视频的Url
    public String directory;//保存下载视频的文件存储路径
    public String fileUrl;//获取下载视频文件总字节数的Url
    public int choose_index=0;//选择标注的索引号
    public int picLength=0;//视频图片帧数

    private ViewPagerAdapter mAdapter;
    //titleBar变量
    private TextView titlebar_textView;

    //下载变量
    private DownloadService.DownloadBinder downloadBinder;
    private Intent serviceIntent;
    //private ServiceConnection connection;
    private ServiceConnection connection=new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            //获取binder实例来在活动中调用服务提供的方法
            Log.d(TAG, "onServiceConnected: 获取downloadBinder实例");
            downloadBinder=(DownloadService.DownloadBinder) service;
        }
        @Override
        public void onServiceDisconnected(ComponentName name) {
        }
    };

    private BaseLazyFragment current_fragment_item; //当前显示的fragment
    private int current_fragment_id; //当前显示的fragment的id
    ArrayList<String> video_files=new ArrayList<String>();
    public static String video_file;
    Intent intent1;
    private ActivityListener activityListener;
    private  Activity2ResultListener activity2ResultListener;
    //BubblenetBean对象
    public static BubblenetBean bubblenetBean;

    //annotateActivity
    Intent annotate_intent;

    //videoActivity
    Intent video_intent;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        Log.d(TAG, "onCreate: ");

        super.onCreate(savedInstanceState);
        //showStorageInfo();
        showExternalStorageInfo();
        setContentView(R.layout.first_layout);
        getDimensions();
        ButterKnife.bind(this);
//        button1.setOnClickListener(this);
        View rightCustomLayout = titlebar.getRightCustomView();
        titlebar_textView=titlebar.getCenterTextView();
        /**页面切换
         *
         */
        mAdapter=new ViewPagerAdapter(getSupportFragmentManager(), MyConstant.FRAME_COUNT);
        viewPager.setAdapter(mAdapter);
        viewPager.setCurrentItem(0);
        titlebar_textView.setText(MyConstant.titles[0]);
        viewPager.setOffscreenPageLimit(MyConstant.FRAME_COUNT-1); //缓存页面
        swiperRefreshLayout.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener() {
            @Override
            public void onRefresh() {
                Log.d(TAG, "onRefresh: ");
            }
        });
        viewPager.addOnPageChangeListener(new ViewPager.OnPageChangeListener() {
            @Override
            public void onPageScrolled(int position, float positionOffset, int positionOffsetPixels) {

            }

            @Override
            public void onPageSelected(int position) {

            }

            @Override
            public void onPageScrollStateChanged(int state) {

            }
        });

        // 布局child view添加监听事件
        moreBtn=rightCustomLayout.findViewById(R.id.right_title_imageview);
        rightCustomLayout.findViewById(R.id.right_title_imageview).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showTopRightMenu();
                Log.d(TAG, "onClick: right_title_imageview");
            }
        });
//        rightCustomLayout.findViewById(R.id.right_title_textview).setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View v) {
//                Log.d(TAG, "onClick: right_title_textview");
//            }
//        });

        titlebar.setListener(new CommonTitleBar.OnTitleBarListener() {
            @Override
            public void onClicked(View v, int action, String extra) {
                if (action == CommonTitleBar.ACTION_LEFT_BUTTON) {
                    int current=viewPager.getCurrentItem();
                    if(current==2){
                        int choose_index=bubblenetBean.getIndexes().get(choose_position);
                        String choose_image=bubblenetBean.getImages().get(choose_position);
                        int width=bubblenetBean.getWidth();
                        int height=bubblenetBean.getHeight();
                        openAnnotateActivity(annotate_tag,choose_image,width,height,choose_index);
                        Log.d(TAG, "onClicked: 返回到annotateActivity");
                    }
                    else if(current>0){
                        viewPager.setCurrentItem(current-1);
                        titlebar_textView.setText(MyConstant.titles[current-1]);
                    }
                    Log.d(TAG, "onClicked: 左边ImageBtn被点击");
                } else if (action == CommonTitleBar.ACTION_RIGHT_TEXT) {
                    Log.d(TAG, "onClicked: 右边TextView被点击");
                }
                // CommonTitleBar.ACTION_LEFT_TEXT;        // 左边TextView被点击
                // CommonTitleBar.ACTION_LEFT_BUTTON;      // 左边ImageBtn被点击
                // CommonTitleBar.ACTION_RIGHT_TEXT;       // 右边TextView被点击
                // CommonTitleBar.ACTION_RIGHT_BUTTON;     // 右边ImageBtn被点击
                // CommonTitleBar.ACTION_SEARCH;           // 搜索框被点击,搜索框不可输入的状态下会被触发
                // CommonTitleBar.ACTION_SEARCH_SUBMIT;    // 搜索框输入状态下,键盘提交触发，此时，extra为输入内容
                // CommonTitleBar.ACTION_SEARCH_VOICE;     // 语音按钮被点击
                // CommonTitleBar.ACTION_SEARCH_DELETE;    // 搜索删除按钮被点击
                // CommonTitleBar.ACTION_CENTER_TEXT;      // 中间文字点击
            }
        });

        viewPager.setScrollble(true);
        swiperRefreshLayout.setEnabled(false);
        //文件下载
        serviceIntent=new Intent(this, DownloadService.class);
        // startService(intent);

        //bindService(serviceIntent,connection,BIND_AUTO_CREATE);//绑定服务
        //判断是否有权限，没有马上申请
        if(ContextCompat.checkSelfPermission(FirstActivity.this, Manifest.permission.WRITE_EXTERNAL_STORAGE)!= PackageManager.PERMISSION_GRANTED){
            ActivityCompat.requestPermissions(FirstActivity.this,new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},1);
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        //停止服务
        stopService(serviceIntent);
        //活动被销毁需要对服务进行解绑，避免内存泄漏
        unbindService(connection);
    }

    @Override
    protected void attachBaseContext(Context newBase) {
        super.attachBaseContext(newBase);
        MultiDex.install(this);
    }

    //定义handler接受fragment发送返回的消息
    public Handler handler=new Handler(){
        @Override
        public void handleMessage(@NonNull Message msg) {
            super.handleMessage(msg);
            if(msg!=null){
                switch (msg.what){
                    case MyConstant.FRAGMENT0:
                        if(msg.arg1==0){
                            openVideoPicker();
                            Log.d(TAG, "handleMessage: fragmentButton发送来的handler打开文件选择器");
                        }
                        if(msg.arg1==1){
                            picLength=msg.arg2;
                            bubblenetBean= (BubblenetBean) msg.obj;
                            Log.d(TAG, "handleMessage: fragmentOpendir发来的bubblenetBean");
                            Log.d(TAG, " width="+bubblenetBean.getWidth()+" height="+bubblenetBean.getHeight());;
                            viewPager.setCurrentItem(1);
                            titlebar_textView.setText(MyConstant.titles[1]);
                        }
                        break;
                    case MyConstant.FRAGMENT1:
                        if(msg.arg1==0){
                            choose_position=(int) msg.arg2;
                            annotate_tag=(String)msg.obj;
                            choose_index=bubblenetBean.getIndexes().get(choose_position);
                            String choose_image=bubblenetBean.getImages().get(choose_position);
                            int width=bubblenetBean.getWidth();
                            int height=bubblenetBean.getHeight();
                            openAnnotateActivity(annotate_tag,choose_image,width,height,choose_index);
                            Log.d(TAG, "handleMessage: fragmentGallery发送来的handler选中图片标注涂鸦");
                        }
                        break;
                    case MyConstant.FRAGMENT2:
                        if(msg.arg1==0){
                            videoNameBean=(VideoNameBean) msg.obj;
                            String tag=videoNameBean.getTag();
                            String videoDefaultName=videoNameBean.getVideoDefaultName();
                            String videoFullName=videoNameBean.getVideoFullName();
                            String flag=videoNameBean.getFlag();
                            int fps=bubblenetBean.getFps();
                            openVideoActivity(tag,videoDefaultName,videoFullName,flag,fps);
                            Log.d(TAG, "handleMessage: fragmentResult发送来的handler消息打开Video_activity设置参数");
                        }
                        break;
                    default:
                        break;
                }
            }
        }
    };

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        switch (requestCode){
            case Constant.REQUEST_CODE_PICK_VIDEO:
                if (resultCode == RESULT_OK) {
                    ArrayList<VideoFile> list = data.getParcelableArrayListExtra(Constant.RESULT_PICK_VIDEO);
                    StringBuilder builder = new StringBuilder();
                    video_files.clear();
                    for (VideoFile file : list) {
                        String path = file.getPath();
                        builder.append(path + "\n");
                        video_files.add(path);
                    }
                    video_file=video_files.get(0);
                    Log.d(TAG, "onActivityResult: "+builder.toString());
                    Log.d(TAG, "onActivityResult: video_file-"+video_file);
                    if(!video_files.isEmpty()){
                        activityListener.hasOpenVideo(video_file);
                        Log.d(TAG, "FilePickerActivity-onActivityResult: 播放视频");
                    }

                }
                break;
            case MyConstant.REQUEST_CODE_ANNOTATE_FRAME:
                if (resultCode == MyConstant.RESULT_CODE_ANNOTATE_FRAME) {
                    result_videoUrl=data.getStringExtra("videoUrl");
                    result_flag=data.getStringExtra("flag");
                    Log.d(TAG, "AnnotateAcitivity-onActivityResult: imageUrl=="+result_videoUrl);
                    viewPager.setCurrentItem(2);
                    titlebar_textView.setText(MyConstant.titles[2]);
                    activity2ResultListener.hasShowVideo(result_videoUrl,result_flag,choose_index,picLength);
                }else if(resultCode==MyConstant.RESULT_CODE_ANNOTATE_BACK_FRAME){
                    String return_data=data.getStringExtra("return_data");
                    Log.d(TAG, "AnnotateAcitivity-onActivityResult: 从"+return_data+"返回back");
                    viewPager.setCurrentItem(1);
                    titlebar_textView.setText(MyConstant.titles[1]);
                }
                break;
            case MyConstant.REQUEST_CODE_VIDEO_FRAME:
                if (resultCode == MyConstant.RESULT_CODE_VIDEO_FRAME) {
                    viewPager.setCurrentItem(2);
                    titlebar_textView.setText(MyConstant.titles[2]);
                    activity2ResultListener.hasShowVideo(result_videoUrl,result_flag,choose_index,picLength);
                    Log.d(TAG, "VideoOutputActivity-onActivityResult: 开始进行文件视频下载！");
                    downloadUrl=data.getStringExtra("downloadUrl");
                    fileUrl=data.getStringExtra("fileUrl");
                    directory=data.getStringExtra("directory");
                    //启动服务,判断系统版本
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                        //android8.0以上通过startForegroundService启动service
                        Log.d(TAG, "onActivityResult: 启动服务startForegroundService");
                        serviceIntent.putExtra("type",1);
                        serviceIntent.putExtra("downloadUrl",downloadUrl);
                        serviceIntent.putExtra("fileUrl",fileUrl);
                        serviceIntent.putExtra("directory",directory);
                        startForegroundService(serviceIntent);
                    } else {
                        serviceIntent.putExtra("type",2);
                        serviceIntent.putExtra("downloadUrl",downloadUrl);
                        serviceIntent.putExtra("fileUrl",fileUrl);
                        serviceIntent.putExtra("directory",directory);
                        startService(serviceIntent);
                        Log.d(TAG, "onActivityResult: 启动服务startService");
                    }
                    bindService(serviceIntent,connection,BIND_AUTO_CREATE);//绑定服务
                    Log.d(TAG, "onActivityResult: 绑定服务BindService");
                    //downloadBinder.startDownload(downloadUrl,fileUrl,directory);
                    //Log.d(TAG, "onActivityResult: startDownload.......");
                }else if(resultCode==MyConstant.RESULT_CODE_VIDEO_BACK_FRAME){
                    viewPager.setCurrentItem(2);
                    titlebar_textView.setText(MyConstant.titles[2]);
                    activity2ResultListener.hasShowVideo(result_videoUrl,result_flag,choose_index,picLength);
                    String return_data=data.getStringExtra("return_data");
                    Log.d(TAG, "VideoOutputActivity-onActivityResult:"+return_data);
                }
                break;
            default:
                break;
        }
    }

    public void showExternalStorageInfo(){
        //获得SD卡目录/mnt/sdcard（获取的是手机外置sd卡的路径）
        String externalPath=Environment.getExternalStorageDirectory().getPath();
        Log.d("StorageUtil", "***********************"+externalPath+"********************");

        List<String> downloadFiles = new ArrayList<>();
        List<String> moviesFiles = new ArrayList<>();
        List<String> picturesFiles = new ArrayList<>();
        List<String> dcimFiles = new ArrayList<>();
        List<String> cameraFiles = new ArrayList<>();
        List<String> sdkFiles = new ArrayList<>();
        sdkFiles=StorageUtil.getFilesAllName(externalPath);
        Log.d("StorageUtil", "Environment.getExternalStorageDirectory():");
        downloadFiles=StorageUtil.getFilesAllName("/storage/emulated/0/Download");
        moviesFiles=StorageUtil.getFilesAllName("/storage/emulated/0/Movies");
        picturesFiles=StorageUtil.getFilesAllName("/storage/emulated/0/Pictures");
        dcimFiles=StorageUtil.getFilesAllName("/storage/emulated/0/DCIM");
        cameraFiles=StorageUtil.getFilesAllName("/storage/emulated/0/DCIM/Camera");
        Log.d("StorageUtil", "***********************"+externalPath+"********************");
    }

    public void showStorageInfo(){
        //获取默认相册路径
        String cameraPath=StorageUtil.getCameraPath();
        /**
         * 通过Environment获取
         */
//获得根目录/data内部存储路径
        System.out.println("Environment.getDataDirectory(): " + Environment.getDataDirectory().getPath());
        Log.d("StorageUtil", "Environment.getDataDirectory()");
        StorageUtil.getFilesAllName(Environment.getDataDirectory().getPath());
//获得缓存目录/cache
        System.out.println("Environment.getDownloadCacheDirectory(): " + Environment.getDownloadCacheDirectory().getPath());
        Log.d("StorageUtil", "Environment.getDownloadCacheDirectory():");
        StorageUtil.getFilesAllName(Environment.getDownloadCacheDirectory().getPath());
//获得SD卡目录/mnt/sdcard（获取的是手机外置sd卡的路径）
        System.out.println("Environment.getExternalStorageDirectory(): " + Environment.getExternalStorageDirectory().getPath());
        Log.d("StorageUtil", "Environment.getExternalStorageDirectory():");
        StorageUtil.getFilesAllName(Environment.getExternalStorageDirectory().getPath());
//获得系统目录/system
        System.out.println("Environment.getRootDirectory(): " + Environment.getRootDirectory().getPath());
        Log.d("StorageUtil", "Environment.getRootDirectory():");
        StorageUtil.getFilesAllName(Environment.getRootDirectory().getPath());
/**
 * 通过Context获取
 */
//用于获取APP的cache目录 /data/data/<application
        System.out.println("getCacheDir(): " + getCacheDir().getPath());
        Log.d("StorageUtil", "getCacheDir():");
        StorageUtil.getFilesAllName(getCacheDir().getPath());
//用于获取APP的在SD卡中的cache目
        System.out.println("getExternalCacheDir(): " + getExternalCacheDir().getPath());
        Log.d("StorageUtil", "getExternalCacheDir():");
        StorageUtil.getFilesAllName(getExternalCacheDir().getPath());
//用于获取APP的files目录 /data/data/<application
        System.out.println("getFilesDir(): " + getFilesDir());
        Log.d("StorageUtil", "getFilesDir():");
        StorageUtil.getFilesAllName(getFilesDir().toString());
//用于获取APPSDK中的obb目录
        System.out.println("getObbDir: " + getObbDir().getPath());
//用于获取APP的所在包目录
        System.out.println("getPackageName: " + getPackageName());
//来获得当前应用程序对应的 apk 文件的路径
        System.out.println("getPackageCodePath: " + getPackageCodePath());
//获取该程序的安装包路径
        System.out.println("getPackageResourcePath: " + getPackageResourcePath());
    }

    protected void openAnnotateActivity(String tag,String choose_image,int width,int height,int index){
        annotate_intent=new Intent(this, AnnotateActivity.class);
        annotate_intent.putExtra("tag",tag);
        annotate_intent.putExtra("choose_image",choose_image);
        annotate_intent.putExtra("width",width);
        annotate_intent.putExtra("height",height);
        annotate_intent.putExtra("index",index);
        startActivityForResult(annotate_intent, MyConstant.REQUEST_CODE_ANNOTATE_FRAME);
    }
    protected void openVideoActivity(String tag,String videoDefaultName,String videoFullName,String flag,int fps){
        video_intent=new Intent(this, VideoOutputActivity.class);
        video_intent.putExtra("tag",tag);
        video_intent.putExtra("videoDefaultName",videoDefaultName);
        video_intent.putExtra("videoFullName",videoFullName);
        video_intent.putExtra("flag",flag);
        video_intent.putExtra("fps",fps);
        startActivityForResult(video_intent, MyConstant.REQUEST_CODE_VIDEO_FRAME);
    }

    public  interface ActivityListener{
        /**
         * 里面传个值
         * @param s
         */
        public void hasOpenVideo(String s);
    }

    public void setVideoListener(ActivityListener activityListener){
        this.activityListener=activityListener;
    }

    public  interface Activity2ResultListener{
        /**
         * 里面传个值
         * @param
         */
        public void hasShowVideo(String s,String s1,int i1,int i2);
    }

    public void setResultListener(Activity2ResultListener activity2ResultListener){
        this.activity2ResultListener=activity2ResultListener;
    }

    protected void openVideoPicker(){

        intent1=new Intent(this, VideoPickActivity.class);
        intent1.putExtra(IS_NEED_CAMERA, true);
        intent1.putExtra(Constant.MAX_NUMBER, 1);
        intent1.putExtra(IS_NEED_FOLDER_LIST, false);
        startActivityForResult(intent1, Constant.REQUEST_CODE_PICK_VIDEO);
    }

    private void getDimensions() {
        Display display = getWindowManager().getDefaultDisplay();//可能会空指针
        DisplayMetrics outMetrics = new DisplayMetrics();
        display.getMetrics(outMetrics);
        pixHeight = outMetrics.heightPixels; //屏幕高度
        pixWidth  = outMetrics.widthPixels; //屏幕宽度
        density = getResources().getDisplayMetrics().density; //依赖于手机系统，获取到的是系统的屏幕信息
        dpWidth = outMetrics.widthPixels / density; //是获取到Activity的实际屏幕信息
        dpHeight = outMetrics.heightPixels / density;

    }

    /************************menu**********************/
    private void showTopRightMenu() {
        mTopRightMenu = new TopRightMenu(FirstActivity.this);
        //添加菜单项
        List<MenuItem> menuItems = new ArrayList<>();
        menuItems.add(new MenuItem(R.mipmap.about_black_32, "关于"));
        menuItems.add(new MenuItem(R.mipmap.share_black_32, "分享"));
        menuItems.add(new MenuItem(R.mipmap.setting_black_32, "设置"));
        menuItems.add(new MenuItem(R.mipmap.update_black_32, "版本更新"));
        menuItems.add(new MenuItem(R.mipmap.feedback1_black_32, "帮助与反馈"));
        menuItems.add(new MenuItem(R.mipmap.sort_black_32, "查看排序结果"));
        mTopRightMenu
                .setHeight(MyConstant.POPVIEW_HEIGHT)     //默认高度480
//                .setWidth(320)      //默认宽度wrap_content
                .showIcon(true)     //显示菜单图标，默认为true
                .dimBackground(true)        //背景变暗，默认为true
                .needAnimationStyle(true)   //显示动画，默认为true
                .setAnimationStyle(R.style.TRM_ANIM_STYLE)
                .addMenuList(menuItems)
                .setOnMenuItemClickListener(new TopRightMenu.OnMenuItemClickListener() {
                    @Override
                    public void onMenuItemClick(int position) {
                        Log.d(TAG, "onMenuItemClick: 点击菜单选项position=" + position);
                        switch (position){
                            case 0:
                                Intent about_intent=new Intent(FirstActivity.this,AboutActivity.class);
                                about_intent.putExtra("start_activity","FirstActivity");
                                startActivityForResult(about_intent,MyConstant.REQUEST_CODE_ABOUT_FRAME);
                                break;
                            case 3:
                                showVersionAlertDialog();
                                break;
                            case 5:
                                String sort_uri=Urls.sortResultloadUrl+"/"+annotate_tag;
                                Uri uri = Uri.parse(sort_uri);
                                Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                                startActivity(intent);
                                break;
                            default:
                                break;
                        }
                    }
                })
                .showAsDropDown(moreBtn, -225, 0);	//带偏移量
//      		.showAsDropDown(moreBtn)
    }
    private void showVersionAlertDialog() {
        versionAlertView = new AlertView("应用更新", "最新版本v1.0\n更新内容:暂无更新,敬请期待", "", new String[]{"以后再说","立即更新"}, null, FirstActivity.this, AlertView.Style.Alert, new OnItemClickListener() {
            @Override
            public void onItemClick(Object o, int position) {
                Log.d(TAG, "onItemClick:OnItemClickListener 点击了确定");
                if (position == AlertView.CANCELPOSITION) {
                    Log.d(TAG, "onItemClick:OnItemClickListener 点击了取消");
                }
                versionAlertView.dismiss();
            }
        }).setCancelable(true).setOnDismissListener(new OnDismissListener() {
            @Override
            public void onDismiss(Object o) {
                Log.d(TAG, "onDismiss:setOnDismissListener ");
            }
        });
        versionAlertView.show();
    }
    /************************menu**********************/
}
