package com.example.androidapplication.fragment;

import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.daimajia.numberprogressbar.NumberProgressBar;
import com.example.androidapplication.FirstActivity;
import com.example.androidapplication.R;
import com.example.androidapplication.base.BaseLazyFragment;
import com.example.androidapplication.bean.BubblenetBean;
import com.example.androidapplication.http.HttpUtil;
import com.example.androidapplication.http.Urls;
import com.example.androidapplication.progress.MyProgressListener;
import com.google.android.material.bottomsheet.BottomSheetBehavior;
import com.google.android.material.bottomsheet.BottomSheetDialog;
import com.google.gson.Gson;
import com.roger.catloadinglibrary.CatLoadingView;
import com.weigan.loopview.LoopView;
import com.weigan.loopview.OnItemSelectedListener;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.salient.artplayer.MediaPlayerManager;
import org.salient.artplayer.VideoView;
import org.salient.artplayer.ui.ControlPanel;
import org.salient.artplayer.ui.listener.OrientationChangeListener;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;
import mehdi.sakout.fancybuttons.FancyButton;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import static com.example.androidapplication.FirstActivity.pixHeight;

public class FragmentOpendir extends BaseLazyFragment {
    private static final String TAG = "FragmentOpendir";
    private static final String ARG_TITLE = "video_path";
    @BindView(R.id.video_player)
    VideoView videoPlayer;
    @BindView(R.id.opendir_button)
    FancyButton opendirButton;
    @BindView(R.id.buttons_linearlayout)
    LinearLayout buttonsLinearlayout;
    @BindView(R.id.upload_button)
    FancyButton uploadButton;
    @BindView(R.id.number_progress)
    NumberProgressBar numberProgress;
    @BindView(R.id.upload_progress_linearlayout)
    LinearLayout uploadProgressLinearlayout;
    @BindView(R.id.get_frames_button)
    FancyButton getFramesButton;
    @BindView(R.id.model_button)
    FancyButton modelButton;
    @BindView(R.id.itertime_button)
    FancyButton itertimeButton;
    //加载对话框
    private CatLoadingView mView;

    private String videoPath;
    private String last_videoPath;
    private String videoName;
    ControlPanel controlPanel;
    private Handler handler;
    FirstActivity activity;

    //model_dialog
    private BottomSheetDialog bottomSheetDialog;
    private BottomSheetBehavior mDialogBehavior;

    //itertime_dialog
    private BottomSheetDialog bottomSheetDialog1;
    private BottomSheetBehavior mDialogBehavior1;
    private LoopView loopView;
    private List<String> itertimeList = new ArrayList<>();

    //选择的模型和迭代次数
    int itertime=5;
    String model="BN0";

    // 上传视频返回data
    String errmsg;
    int errno = 1001;//1001
    String tag;
    int piclength = 0;//0
    String videoname;
    HashMap<String, Integer> video_info_hashmap = new HashMap<String, Integer>();

    public FragmentOpendir() {
    }

    public static FragmentOpendir newInstance() {
        FragmentOpendir fragment = new FragmentOpendir();
//        Bundle bundle = new Bundle();
//        bundle.putString(ARG_TITLE, title);
//        fragment.setArguments(bundle);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
//        videoPath = getArguments().getString(ARG_TITLE);
        activity = (FirstActivity) getActivity();
        initConstant();
        handler = activity.handler;
        activity.setVideoListener(new FirstActivity.ActivityListener() {
            @Override
            public void hasOpenVideo(String s) {
                videoPath = s;
                startPlayer();
                Log.d(TAG, "hasOpenVideo: startPlayer");
            }

        });
    }

    private void initConstant() {
        tag="1586441646";//test
        //video_info_hashmap.put("1586441646", 40);//test
        itertime=5;
        model="BN0";
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        super.onCreateView(inflater, container, savedInstanceState);
        View view = inflater.inflate(R.layout.fragment_opendir_layout, container, false);
        ButterKnife.bind(this, view);
        mIsprepared = true;
        lazyLoad();
        return view;
    }

    @Override
    protected void lazyLoad() {
        if (!mIsprepared || !mIsVisible || mHasLoadedOnce) {

            return;
        }
        Log.e(TAG, "lazyLoad: 当前的fragment-FragmentOpendir");
        mHasLoadedOnce = true;
        //UI和业务逻辑
        initConstant();
        initVideoPlayer();
        opendirButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                numberProgress.setProgress(0);
                Message message = Message.obtain();
                message.what = 10;
                message.arg1 = 0;
                handler.sendMessage(message);
                Log.d(TAG, "onClick: opendir按钮按下发送message");
            }
        });
        uploadButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                /*String data=null;
                data=HttpUtil.testConnection(testUrl);
                if(data!=null){
                    Log.d(TAG, "data:"+data);
                }else{
                    Log.d(TAG, "data null");
                }*/
                if (videoPath == null) {
                    Toast.makeText(getActivity(), "请选择视频后，再点击上传！", Toast.LENGTH_LONG).show();
                } else {
                    numberProgress.setProgress(0);
                    File file = new File(videoPath);
                    HttpUtil.postFile(Urls.postUrl, new MyProgressListener() {
                        @Override
                        public void onProgress(long currentBytes, long contentLength, boolean done) {
                            Log.d(TAG, "currentBytes==" + currentBytes + " contentLength==" + contentLength + " done==" + done);
                            int progress = (int) (currentBytes * 100 / contentLength);
//                            postProgress.setProgress(progress);
//                            postText.setText(progress + "%");
                            numberProgress.setProgress(progress);
                            if (progress == 100) {
                                Toast.makeText(getActivity(), "视频上传成功！", Toast.LENGTH_LONG).show();
                            }
                        }
                    }, new Callback() {
                        @Override
                        public void onFailure(Call call, IOException e) {
                            Log.d(TAG, "onFailure: e==" + e.getMessage());
                            numberProgress.setProgress(0);
                        }

                        @Override
                        public void onResponse(Call call, Response response) throws IOException {
                            if (response != null) {
                                String responseData = response.body().string();
                                Log.d(TAG, "onResponse: result==" + responseData);
                                //获取json数据
                                parseJsonWithJsonObject(responseData);
                            }
                        }
                    }, file);
                    //在这儿返回数据
                }
            }
        });

        // test加载图片
        getFramesButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //判断是否成功生成了视频帧
                if (!video_info_hashmap.containsKey(tag)) {
                    Toast.makeText(getActivity(), "上传视频有误，请重新上传！", Toast.LENGTH_LONG).show();
                } else {
                    //开始显示加载对话框
                    mView = new CatLoadingView();
                    mView.setBackgroundColor(R.color.catloading_view_background);
                    mView.show(getActivity().getSupportFragmentManager(), "");
                    //Glide.with(getActivity()).load(getFrameUrl).into(testImageview);
                    HttpUtil.getFrame(Urls.getFrameUrl, tag, model, itertime,new Callback() {
                        @Override
                        public void onFailure(Call call, IOException e) {
                            Log.d(TAG, "onFailure: e==" + e.getMessage());
                        }

                        @Override
                        public void onResponse(Call call, Response response) throws IOException {
                            if (response != null) {
                                String responseData = response.body().string();
                                Log.d(TAG, "onResponse: result==" + responseData);
                                getActivity().runOnUiThread(new Runnable() {
                                    @Override
                                    public void run() {
                                        Log.d(TAG, "runOnUiThread: sort frames完毕，关闭加载对话框");
                                        mView.dismiss();
                                    }
                                });
                                //获取json数据
                                getFrameCallback(responseData);
                            }
                        }
                    });
                    //在这儿返回数据
                }
            }
        });

        itertimeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "onClick: 选择迭代次数按钮被按下");
                showItertimeSheetDialog();
            }
        });

        modelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "onClick: 选择模型按钮被按下");
                showModelSheetDialog();
            }
        });
    }

    private void showItertimeSheetDialog(){
        View view = View.inflate(getActivity(), R.layout.itertime_dialog_layout, null);
        bottomSheetDialog1 = new BottomSheetDialog(getActivity(), R.style.dialog);
        bottomSheetDialog1.setContentView(view);
        ImageView dialogBottomsheetItertimeClose=view.findViewById(R.id.itertime_dialog_bottomsheet_iv_close);
        loopView=view.findViewById(R.id.itertime_loopView);

        mDialogBehavior1 = BottomSheetBehavior.from((View) view.getParent());
        int peekHeight = Math.round(pixHeight / 2); //弹窗高度
        mDialogBehavior1.setPeekHeight(peekHeight);
        mDialogBehavior1.setBottomSheetCallback(new BottomSheetBehavior.BottomSheetCallback() {
            @Override
            public void onStateChanged(@NonNull View bottomSheet, int newState) {
                if (newState == BottomSheetBehavior.STATE_HIDDEN) {
                    bottomSheetDialog1.dismiss();
                    mDialogBehavior1.setState(BottomSheetBehavior.STATE_COLLAPSED);
                }
            }

            @Override
            public void onSlide(@NonNull View bottomSheet, float slideOffset) {
            }
        });

        dialogBottomsheetItertimeClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                bottomSheetDialog1.dismiss();
            }
        });

        //初始化数据
        for(int i=1;i<=1000;i++){
            itertimeList.add(String.valueOf(i));
        }
        loopView.setItems(itertimeList);
        loopView.setCurrentPosition(4);
        //设置是否循环播放
//        loopView.setNotLoop();
        loopView.setListener(new OnItemSelectedListener() {
            @Override
            public void onItemSelected(int index) {
                itertime=index+1;
                Log.d(TAG, "onItemSelected: 选择的迭代次数为"+itertime);
                Toast.makeText(getActivity(), "选择的BubbleNet迭代次数为"+itertime+"!", Toast.LENGTH_LONG).show();
                bottomSheetDialog1.dismiss();
            }
        });


        bottomSheetDialog1.show();
    }

    private void showModelSheetDialog() {
        View view = View.inflate(getActivity(), R.layout.model_dialog_layout, null);
        bottomSheetDialog = new BottomSheetDialog(getActivity(), R.style.dialog);
        bottomSheetDialog.setContentView(view);
        mDialogBehavior = BottomSheetBehavior.from((View) view.getParent());
        int peekHeight = Math.round(pixHeight / 4); //弹窗高度
        mDialogBehavior.setPeekHeight(peekHeight);
        mDialogBehavior.setBottomSheetCallback(new BottomSheetBehavior.BottomSheetCallback() {
            @Override
            public void onStateChanged(@NonNull View bottomSheet, int newState) {
                if (newState == BottomSheetBehavior.STATE_HIDDEN) {
                    bottomSheetDialog.dismiss();
                    mDialogBehavior.setState(BottomSheetBehavior.STATE_COLLAPSED);
                }
            }

            @Override
            public void onSlide(@NonNull View bottomSheet, float slideOffset) {
            }
        });
        ImageView dialogBottomsheetIvClose=view.findViewById(R.id.dialog_bottomsheet_iv_close);
        TextView BN0ModelTextview=(TextView)view.findViewById(R.id.BN0_model_textview);
        TextView BNLFModelTextview=view.findViewById(R.id.BNLF_model_textview);
        dialogBottomsheetIvClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                bottomSheetDialog.dismiss();
            }
        });
        BN0ModelTextview.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "BN0ModelTextview onClick: ");
                Toast.makeText(getActivity(), "选择的BubbleNet模型配置为BN0", Toast.LENGTH_LONG).show();
                model="BN0";
                bottomSheetDialog.dismiss();
            }
        });

        BNLFModelTextview.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "BNLFModelTextview onClick: ");
                model="BNLF";
                Toast.makeText(getActivity(), "选择的BubbleNet模型配置为BNLF", Toast.LENGTH_LONG).show();
                bottomSheetDialog.dismiss();
            }
        });

        bottomSheetDialog.show();
    }


    //解析返回的图片数据并回调通知activity更新UI
    public void getFrameCallback(String responseData) {
        Gson gson = new Gson();
        BubblenetBean bean = gson.fromJson(responseData, BubblenetBean.class);
//        final Bean bean = gson.fromJson(response.body().charStream(), Bean.class);
//        mlist=(ArrayList<Bean.StoriesBean>) bean.getStories();
//        md.setdata((ArrayList<Bean.StoriesBean>) mlist);
//        md.notifyDataSetChanged();
        List<String> images = bean.getImages();
        List<Integer> indexes = bean.getIndexes();
        String tag = bean.getTag();
        int width = bean.getWidth();
        int height = bean.getHeight();
        int fps=bean.getFps();
        Log.d(TAG, "getFrameCallback\n images:" + images + " indexes:" + indexes + " tag-" + tag + " width-" + width + " height-" + height+"fps-"+fps);
        Message msg = Message.obtain();
        msg.what = 10;
        msg.arg1 = 1;
        msg.arg2 = piclength;
        msg.obj = bean;
        handler.sendMessage(msg);
    }

    //解析视频上传成功后返回的的jsonify
    private void parseJsonWithJsonObject(String responseData) throws IOException {
        try {
            JSONArray jsonArray = new JSONArray(responseData);
            for (int i = 0; i < jsonArray.length(); i++) {
                JSONObject jsonObject = jsonArray.getJSONObject(i);
                errmsg = jsonObject.getString("errmsg");
                errno = jsonObject.getInt("errno");
                tag = jsonObject.getString("tag");
                piclength = jsonObject.getInt("piclength");
                videoname = jsonObject.getString("videoname");
                Log.d(TAG, "parseJsonWithJsonObject: errmsg-" + errmsg + " errno-" + errno + " tag-" + tag + " piclength-" + piclength + " videoname-" + videoname);
                if (errno == 0) {
                    video_info_hashmap.put(tag, piclength);
                }
            }
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void initVideoPlayer() {
//        videoPath = activity.video_file;
//        last_videoPath = videoPath;
//        String[] strs = videoPath.split("/"); // 如果是\\需要转义符\\\\
//        videoName = strs[strs.length - 1];
        controlPanel = new ControlPanel(getActivity());
        videoPlayer.setControlPanel(controlPanel);
//        TextView tvTitle = controlPanel.findViewById(R.id.tvTitle);
//        tvTitle.setText(videoName);
//        videoPlayer.setUp(videoPath);
        //MediaPlayerManager.instance().setMediaPlayer(new ExoPlayer(getActivity()));
        //MediaPlayerManager.instance().setLooping(true); //循环
        MediaPlayerManager.instance().setOnOrientationChangeListener(new OrientationChangeListener());
    }

    private void startPlayer() {
        last_videoPath = videoPath;
        String[] strs = videoPath.split("/"); // 如果是\\需要转义符\\\\
        videoName = strs[strs.length - 1];
        //设置标题
        TextView tvTitle = controlPanel.findViewById(R.id.tvTitle);
        tvTitle.setText(videoName);
        videoPlayer.setUp(videoPath);
        Log.d(TAG, "initVideoPlayer: videoName-" + videoName);
        Log.d(TAG, "initVideoPlayer: videoPath-" + videoPath);
        //MediaPlayerManager.instance().setMediaPlayer(new ExoPlayer(getActivity()));
        //MediaPlayerManager.instance().setLooping(true); //循环
        videoPlayer.start();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        MediaPlayerManager.instance().releasePlayerAndView(getActivity());
    }

    @Override
    public void onPause() {
        super.onPause();
        MediaPlayerManager.instance().pause();
    }

    public String getTitle() {
        return videoPath;
    }
}
