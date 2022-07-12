package com.example.androidapplication;

import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.util.DisplayMetrics;
import android.util.Log;
import android.view.Display;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;

import com.bigkoo.alertview.AlertView;
import com.bigkoo.alertview.OnDismissListener;
import com.bigkoo.alertview.OnItemClickListener;
import com.bumptech.glide.Glide;
import com.bumptech.glide.request.RequestOptions;
import com.example.androidapplication.base.BasicActivity;
import com.example.androidapplication.bean.ScribbleBean;
import com.example.androidapplication.http.HttpUtil;
import com.example.androidapplication.http.MyConstant;
import com.example.androidapplication.http.Urls;
import com.example.androidapplication.imgprocess.GrafittiImageView;
import com.example.androidapplication.imgprocess.IntViewPoint;
import com.example.androidapplication.imgprocess.Line;
import com.example.androidapplication.imgprocess.ViewPoint;
import com.getbase.floatingactionbutton.FloatingActionButton;
import com.getbase.floatingactionbutton.FloatingActionsMenu;
import com.roger.catloadinglibrary.CatLoadingView;
import com.wuhenzhizao.titlebar.widget.CommonTitleBar;
import com.zaaach.toprightmenu.MenuItem;
import com.zaaach.toprightmenu.TopRightMenu;

import org.json.JSONException;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;
import mehdi.sakout.fancybuttons.FancyButton;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

/**
 * Created by wjy on 2020/4/12
 **/
public class AnnotateActivity extends BasicActivity {
    private static final String TAG = "AnnotateActivity";
    @BindView(R.id.titlebar)
    CommonTitleBar titlebar;
    String imageName;
    String tag;
    String flag = "vos";
    int index;

    //尺寸参数,除了标明的外单位均为像素pix
    int imageWidth;// 图片原宽度
    int imageHeight;// 图片原高度
    float density;// 屏幕手机分辨率
    float dpWidth;// 屏幕宽度dp
    float dpHeight;// 屏幕高度dp
    float pixWidth;// 屏幕宽度
    float pixHeight;// 屏幕高度
    float resize_scale;// 原尺寸/显示尺寸
    int picWidth;// 显示的图片宽度
    int picHeight;// 显示的图片高度
    int[] locationOnScreen;
    int imageViewMeasuredHeight;
    int imageViewMeasuredWidth;
    int centerx;
    int centery;
    int type=1;//涂鸦类型
    ScribbleBean scribbleBean;
    @BindView(R.id.draw_imageview)
    GrafittiImageView drawImageview;
    @BindView(R.id.annotate_btn_clear)
    FancyButton annotateBtnClear;
    @BindView(R.id.annotate_btn_segmentate)
    FancyButton annotateBtnSegmentate;
    @BindView(R.id.annotate_btn_removal)
    FancyButton annotateBtnRemoval;
    //加载对话框
    private CatLoadingView mView;
    //弹出对话框

    /*****************menu***************/
    //弹出菜单
    private TopRightMenu mTopRightMenu;
    //按钮imageView
    private ImageView moreBtn;
    //版本弹出框
    private AlertView versionAlertView;
    /***************menu*************/

    //确认标注变量
    boolean isConfirm = true; //修改默认为false
    boolean isFirst = true;
    boolean isVos = false;
    boolean isRemoval = false;//removal是否调用成功
    String annotateResponseData;
    String vosResponseData;
    String removalResponseData;

    //计算得到的全局坐标
    ArrayList<ViewPoint> globalFloatPathPoses = new ArrayList<>();
    ArrayList<IntViewPoint> globalIntPathPoses = new ArrayList<>();
    @BindView(R.id.annotate_btn_finish)
    FancyButton annotateBtnFinish;
    @BindView(R.id.float_button_front)
    FloatingActionButton floatButtonFront;
    @BindView(R.id.float_button_back)
    FloatingActionButton floatButtonBack;
    @BindView(R.id.float_action_menu)
    FloatingActionsMenu floatActionMenu;

    //定义onResponse回调接口
    public interface NetworkCallback<T> {
        void onGetSuccess(T[] resultList);

        void onGetFail(Exception ex);
    }

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        //参数初始化
        super.onCreate(savedInstanceState);
        Log.d(TAG, "onCreate: ");
        Intent intent = getIntent();
        tag = intent.getStringExtra("tag");
        imageName = intent.getStringExtra("choose_image");
        index = intent.getIntExtra("index", 0);
        imageWidth = intent.getIntExtra("width", 854);
        imageHeight = intent.getIntExtra("height", 480);
        Log.d(TAG, "onCreate:  tag-" + tag + " imageName" + imageName);

        //布局及butterknife
        setContentView(R.layout.annotate_activity_layout);
        ButterKnife.bind(this);

        //设置标题栏及点击事件
        initTitleBar();

        //获取屏幕尺寸
        getDimensions();
        Log.d(TAG, "屏幕分辨率density==" + density);
        Log.d(TAG, "屏幕dpWidth==" + dpWidth);
        Log.d(TAG, "屏幕dpHeight==" + dpHeight);
        Log.d(TAG, "屏幕pixWidth==" + pixWidth);
        Log.d(TAG, "屏幕pixHeight==" + pixHeight);
        Log.d(TAG, "图片imageWidth==" + imageWidth);
        Log.d(TAG, "图片imageHeight==" + imageHeight);

        //加载图片
        String downloadUrl = Urls.imageResourceUrl + "/" + tag + "/" + imageName;
        loadImage(downloadUrl,imageWidth,imageHeight);
        Log.d(TAG, "图片显示picWidth==" + picWidth);
        Log.d(TAG, "图片显示picHeight==" + picHeight);
        Log.d(TAG, "缩放大小resize_scale==" + resize_scale);

        //floatButton点击事件
        floatButtonBack.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "onClick: 背景涂鸦");
                type=0;
                drawImageview.setType(type);
                drawImageview.setColor(Color.GREEN);
            }
        });
        floatButtonFront.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "onClick: 前景涂鸦");
                type=1;
                drawImageview.setType(type);
                drawImageview.setColor(Color.RED);
            }
        });

        //onTouch事件
        annotateBtnClear.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "重新标注按钮被按下");
                isConfirm = false;
                isFirst = true;
                drawImageview.clearStroke();
                String downloadUrl = Urls.imageResourceUrl + "/" + tag + "/" + imageName;
                loadImage(downloadUrl,imageWidth,imageHeight);
                drawImageview.setDraw(true);
            }
        });
        annotateBtnRemoval.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isConfirm == false) {
                    Toast.makeText(AnnotateActivity.this, "请先在目标物体上进行涂鸦!", Toast.LENGTH_LONG).show();
                } else {
                    flag = "removal";
                    isConfirm = false;
                    drawImageview.setDraw(false);
                    //开始显示加载对话框
                    mView = new CatLoadingView();
                    mView.show(getSupportFragmentManager(), "");
                    mView.setBackgroundColor(R.color.catloading_view_background);
                    HttpUtil.startRemoval(Urls.removalUrl, tag, index, new Callback() {
                        @Override
                        public void onFailure(Call call, IOException e) {
                            Log.d(TAG, "onFailure: e==" + e.getMessage());
                        }

                        @Override
                        public void onResponse(Call call, Response response) throws IOException {
                            if (response != null) {
                                removalResponseData = response.body().string();
                                Log.d(TAG, "onResponse: result==" + removalResponseData);
                                drawImageview.clearStroke();
                                if (removalResponseData.equals("404")) {
                                    isRemoval = false;
                                    AnnotateActivity.this.runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            Log.d(TAG, "onResponse: removal=false");
                                            Toast.makeText(AnnotateActivity.this, "移除目标物体失败，请重新移除!", Toast.LENGTH_LONG).show();
                                            //getAnnotateButtonSet(true);
                                        }
                                    });
                                } else {
                                    isRemoval = true;
                                    Log.d(TAG, "onResponse: isRemoval=" + isRemoval);
                                    AnnotateActivity.this.runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            mView.dismiss();
                                            removalCallback(removalResponseData); //返回消息给FirstActivity关闭当前activity打开fragmentResult
                                        }
                                    });
                                }

                            }
                        }
                    });
                }

                Log.d(TAG, "移除目标物体按钮被按下");
            }
        });
        annotateBtnSegmentate.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (isConfirm == false) {
                    Toast.makeText(AnnotateActivity.this, "请先在目标物体上进行涂鸦!", Toast.LENGTH_LONG).show();
                } else {
                    flag = "vos";
                    isConfirm = false;
                    //getAnnotateButtonSet(false);
                    drawImageview.setDraw(false);
                    //开始显示加载对话框
                    mView = new CatLoadingView();
                    mView.show(getSupportFragmentManager(), "");
                    mView.setBackgroundColor(R.color.catloading_view_background);
                    HttpUtil.startVos(Urls.ivsVosUrl, tag, index, new Callback() {
                        @Override
                        public void onFailure(Call call, IOException e) {
                            Log.d(TAG, "onFailure: e==" + e.getMessage());
                        }

                        @Override
                        public void onResponse(Call call, Response response) throws IOException {
                            if (response != null) {
                                vosResponseData = response.body().string();
                                Log.d(TAG, "onResponse: result==" + vosResponseData);
                                drawImageview.clearStroke();
                                if (vosResponseData.equals("404")) {
                                    isVos = false;
                                    AnnotateActivity.this.runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            Log.d(TAG, "onResponse: isVos=false");
                                            Toast.makeText(AnnotateActivity.this, "分割失败，请重新分割!", Toast.LENGTH_LONG).show();
                                            //getAnnotateButtonSet(true);
                                        }
                                    });
                                } else {
                                    isVos = true;
                                    Log.d(TAG, "onResponse: isVos=" + isVos);
                                    AnnotateActivity.this.runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            mView.dismiss();
                                            vosCallback(vosResponseData); //返回消息给FirstActivity关闭当前activity打开fragmentResult
                                        }
                                    });
                                }

                            }
                        }
                    });

                }
                Log.d(TAG, "分割目标物体按钮被按下");
            }
        });
        annotateBtnFinish.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "确认标注按钮被按下");
                Line line = drawImageview.getClientPoints();
                if (line.points.size() == 0) {
                    Toast.makeText(AnnotateActivity.this, "请先在目标物体上进行涂鸦!", Toast.LENGTH_LONG).show();
                } else {
                    drawImageview.setDraw(false);
                    scribbleBean = posPreprocess1(line);
                    //getAnnotateButtonSet(false);
                    try {
                        HttpUtil.getAnnotate(Urls.getAnnotateUrl, scribbleBean, new Callback() {
                            @Override
                            public void onFailure(Call call, IOException e) {
                                Log.d(TAG, "onFailure: e==" + e.getMessage());
                            }

                            @Override
                            public void onResponse(Call call, Response response) throws IOException {
                                if (response != null) {
                                    annotateResponseData = response.body().string();
                                    Log.d(TAG, "onResponse: result==" + annotateResponseData);
                                    //获取json数据
                                    //getFrameCallback(responseData);
                                    //getAnnotateButtonSet(true); //按钮设置enable=true
                                    drawImageview.clearStroke();
                                    drawImageview.setDraw(true);
                                    if (annotateResponseData.equals("404")) {
                                        isConfirm = false;
                                        AnnotateActivity.this.runOnUiThread(new Runnable() {
                                            @Override
                                            public void run() {
                                                Toast.makeText(AnnotateActivity.this, "目标分割失败，请重新标注！", Toast.LENGTH_LONG).show();
                                            }
                                        });
                                    } else{
                                        isConfirm = true;
                                        isFirst = false;
                                        AnnotateActivity.this.runOnUiThread(new Runnable() {
                                            @Override
                                            public void run() {
                                                annotateCallBack(); //返回消息给FirstActivity关闭当前activity打开fragmentResult
                                            }
                                        });
                                    }
                                }
                            }

                        });
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    //在这儿返回数据
                }

            }
        });

        drawImageview.post(new Runnable() {
            @Override
            public void run() {
                getSizes();
                getImgaeViewInfo();
            }
        });
    }

    public void annotateCallBack( ) {
        //加载图片
        String downloadUrl = Urls.annotateResourceUrl  + "/" + tag + "/" + String.valueOf(index);
        loadImage(downloadUrl,imageWidth,imageHeight);
    }


    public void removalCallback(String responseData) {
        //传递给FisrtActivity，关闭当前activity
        String videoUrl = Urls.removalVideoUrl + "/" + responseData;
        Intent intent = new Intent();
        intent.putExtra("videoUrl", videoUrl);
        intent.putExtra("flag", flag);
        setResult(MyConstant.RESULT_CODE_ANNOTATE_FRAME, intent);
        finish();
    }

    public void vosCallback(String responseData) {

        //传递给FisrtActivity，关闭当前activity
        String videoUrl = Urls.vosVideoUrl + "/" + responseData;
        Intent intent = new Intent();
        intent.putExtra("videoUrl", videoUrl);
        intent.putExtra("flag", flag);
        setResult(MyConstant.RESULT_CODE_ANNOTATE_FRAME, intent);
        finish();
    }

    public void getAnnotateButtonSet(boolean bool) {
        annotateBtnClear.setEnabled(bool);
        annotateBtnFinish.setEnabled(bool);
        annotateBtnRemoval.setEnabled(bool);
        annotateBtnSegmentate.setEnabled(bool);
    }

    private ScribbleBean posPreprocess1(Line line) {
        ArrayList<ViewPoint> clientPathPoses = new ArrayList<ViewPoint>();
        ViewPoint viewPoint = new ViewPoint();
        int pointSize = line.points.size();
        float[] xposes = new float[pointSize];
        float[] yposes = new float[pointSize];
        int[] xposes_line = new int[pointSize];
        int[] yposes_line = new int[pointSize];
        for (int i = 0; i < pointSize; i++) {
            float x = line.points.get(i).x;
            float y = line.points.get(i).y;
            float globalFloatX = x / (float) picWidth;
            float globalFloatY = y / (float) picHeight;
            viewPoint.x = globalFloatX;
            viewPoint.y = globalFloatY;
            clientPathPoses.add(viewPoint);
            xposes[i] = globalFloatX;
            yposes[i] = globalFloatY;
            xposes_line[i] = Math.round(globalFloatX*imageWidth);
            yposes_line[i] = Math.round(globalFloatY*imageHeight);
            Log.d(TAG, "比例: (" + globalFloatX + "," + globalFloatY + ")");
        }

        ScribbleBean scribbleBean1 = new ScribbleBean();
        scribbleBean1.setIndex(index);
        scribbleBean1.setSize(pointSize);
        scribbleBean1.setTag(tag);
        scribbleBean1.setXposes(xposes);
        scribbleBean1.setYposes(yposes);
        scribbleBean1.setType(type);
        scribbleBean1.setXposes_line(xposes_line);
        scribbleBean1.setYposes_line(yposes_line);
        if (isFirst == true) {
            scribbleBean1.setAdd(0);
        } else {
            scribbleBean1.setAdd(1);
        }
        return scribbleBean1;
    }


    private void getSizes() {
        Log.d(TAG, "***********************getSizes********************");
        int imageViewHeight = drawImageview.getHeight();
        Log.d(TAG, "imageViewHeight=" + imageViewHeight);
        imageViewMeasuredHeight = drawImageview.getMeasuredHeight();
        Log.d(TAG, "imageViewMeasuredHeight=" + imageViewMeasuredHeight);
        int imageViewWidth = drawImageview.getWidth();
        Log.d(TAG, "imageViewWidth=" + imageViewWidth);
        imageViewMeasuredWidth = drawImageview.getMeasuredWidth();
        Log.d(TAG, "imageViewMeasuredWidth=" + imageViewMeasuredWidth);
        Log.d(TAG, "***********************getSizes********************");
    }

    private void getDimensions() {
        Log.d(TAG, "***********************getDimensions********************");
        Display display = getWindowManager().getDefaultDisplay();//可能会空指针
        DisplayMetrics outMetrics = new DisplayMetrics();
        display.getMetrics(outMetrics);
        pixHeight = outMetrics.heightPixels; //屏幕高度
        pixWidth = outMetrics.widthPixels; //屏幕宽度
        density = getResources().getDisplayMetrics().density; //依赖于手机系统，获取到的是系统的屏幕信息
        dpWidth = outMetrics.widthPixels / density; //是获取到Activity的实际屏幕信息
        dpHeight = outMetrics.heightPixels / density;
        Log.d(TAG, "***********************getDimensions********************");
    }

    public void getImgaeViewInfo() {
        Log.d(TAG, "***********************getImgaeViewInfo********************");
        //imageView的坐标
        int[] locationInWindow = new int[2];
        locationOnScreen = new int[2];
        drawImageview.getLocationInWindow(locationInWindow);
        drawImageview.getLocationOnScreen(locationOnScreen);
        int left = drawImageview.getLeft();
        int top = drawImageview.getTop();
        int bottom = drawImageview.getBottom();
        int right = drawImageview.getRight();
        Log.d(TAG, "locationInWindow:x=" + locationInWindow[0] + " y=" + locationInWindow[1]);
        Log.d(TAG, "locationOnScreen:x=" + locationOnScreen[0] + " y=" + locationOnScreen[1]);
        Log.d(TAG, "left=" + left + " top=" + top + " bottom=" + bottom + " right=" + right);
        Log.d(TAG, "***********************getImgaeViewInfo********************");
    }

    public void loadImage(String downloadUrl,int imageWidth1,int imageHeight1) {
        picWidth = Math.round(pixWidth - 2 * 10 * density);
        resize_scale = (float) imageWidth1 / (float) picWidth;
        picHeight = Math.round((float) imageHeight1 / resize_scale);
        RequestOptions options = new RequestOptions()
                .override(picWidth, picHeight).fitCenter();
        Glide.with(this).load(downloadUrl).apply(options).into(drawImageview);
    }

    public void initTitleBar() {
        //View centerview=LayoutInflater.from(this).inflate(annotate_frame_centerview, null, false);
        //titlebar.setCenterView(centerview);
        View rightCustomLayout = titlebar.getRightCustomView();
        TextView textView = titlebar.getCenterTextView();
        textView.setText("关键帧标注");
        // 布局child view添加监听事件
        moreBtn=rightCustomLayout.findViewById(R.id.right_title_imageview);
        rightCustomLayout.findViewById(R.id.right_title_imageview).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showTopRightMenu();
                Log.d(TAG, "onClick: right_title_imageview");
            }
        });
        titlebar.setListener(new CommonTitleBar.OnTitleBarListener() {
            @Override
            public void onClicked(View v, int action, String extra) {
                if (action == CommonTitleBar.ACTION_LEFT_BUTTON) {
                    Log.d(TAG, "onClicked: 左边ImageBtn被点击");
                    Intent intent = new Intent();
                    intent.putExtra("return_data", "annotateActivity");
                    setResult(MyConstant.RESULT_CODE_ANNOTATE_BACK_FRAME, intent);
                    finish();
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

    }

//    private void posPreprocess(Line line){
//        int imageView_half_width=imageViewMeasuredWidth/2;
//        int imageView_half_height=imageViewMeasuredHeight/2;
//        centerx=imageView_half_width+locationOnScreen[0];
//        centery=imageView_half_height+locationOnScreen[1];
//        int startx=locationOnScreen[0];
//        int starty=locationOnScreen[1];
//        Log.d(TAG, "startx="+startx+" starty="+starty);
//        ArrayList<ViewPoint> globalLinePathPoses = new ArrayList<ViewPoint>();//轨迹绝对坐标
//        globalFloatPathPoses = new ArrayList<ViewPoint>();//轨迹绝对坐标
//        ViewPoint viewPoint=new ViewPoint();
//        ViewPoint viewLinePoint=new ViewPoint();
//        IntViewPoint intViewPoint=new IntViewPoint();
//        for(int i = 0; i < line.points.size(); i++){
//            float x = line.points.get(i).x;
//            float y = line.points.get(i).y;
//            float globalFloatX=(x-startx)/picWidth;
//            float globalFloatY=(y-starty)/picHeight;
//            float globalLineFloatX=(x-startx);
//            float globalLineFloatY=(y-starty);
//            viewPoint.x=globalFloatX;
//            viewPoint.y=globalFloatY;
//            viewLinePoint.x=globalLineFloatX;
//            viewLinePoint.y=globalLineFloatY;
//            globalFloatPathPoses.add(viewPoint); //可用的
//            globalLinePathPoses.add(viewLinePoint);
//            Log.d(TAG, "比例: ("+globalFloatX+","+globalFloatY+")");
//            Log.d(TAG, "绝对值: ("+globalLineFloatX+","+globalLineFloatY+")");
//        }
//    }
    /************************menu**********************/
    private void showTopRightMenu() {
        mTopRightMenu = new TopRightMenu(AnnotateActivity.this);
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
                                Intent about_intent=new Intent(AnnotateActivity.this,AboutActivity.class);
                                about_intent.putExtra("start_activity","AnnotateActivity");
                                startActivityForResult(about_intent,MyConstant.REQUEST_CODE_ABOUT_FRAME_ANNOTATE);
                                break;
                            case 3:
                                showVersionAlertDialog();
                                break;
                            case 5:
                                String sort_uri=Urls.sortResultloadUrl+"/"+tag;
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
        versionAlertView = new AlertView("应用更新", "最新版本v1.0\n更新内容:暂无更新,敬请期待", "", new String[]{"以后再说","立即更新"}, null, AnnotateActivity.this, AlertView.Style.Alert, new OnItemClickListener() {
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
