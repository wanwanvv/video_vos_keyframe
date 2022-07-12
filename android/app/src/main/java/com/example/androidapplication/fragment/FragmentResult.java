package com.example.androidapplication.fragment;

import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.bigkoo.alertview.AlertView;
import com.bigkoo.alertview.OnDismissListener;
import com.bigkoo.alertview.OnItemClickListener;
import com.bumptech.glide.Glide;
import com.bumptech.glide.request.target.SimpleTarget;
import com.bumptech.glide.request.transition.Transition;
import com.example.androidapplication.FirstActivity;
import com.example.androidapplication.R;
import com.example.androidapplication.base.BaseLazyFragment;
import com.example.androidapplication.bean.VideoNameBean;
import com.example.androidapplication.http.Urls;
import com.getbase.floatingactionbutton.FloatingActionButton;
import com.google.android.material.bottomsheet.BottomSheetBehavior;
import com.google.android.material.bottomsheet.BottomSheetDialog;
import com.weigan.loopview.LoopView;
import com.weigan.loopview.OnItemSelectedListener;

import org.salient.artplayer.MediaPlayerManager;
import org.salient.artplayer.VideoView;
import org.salient.artplayer.ui.ControlPanel;
import org.salient.artplayer.ui.listener.OrientationChangeListener;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

import butterknife.BindView;
import butterknife.ButterKnife;
import mehdi.sakout.fancybuttons.FancyButton;

import static com.example.androidapplication.FirstActivity.pixHeight;

/**
 * Created by wjy on 2020/4/15
 **/
public class FragmentResult extends BaseLazyFragment {
    private static final String TAG = "FragmentResult";
    @BindView(R.id.result_player)
    VideoView resultPlayer;
    @BindView(R.id.output_button)
    FancyButton outputButton;
    @BindView(R.id.save_annotation_button)
    FancyButton saveAnnotationButton;
    @BindView(R.id.save_mask_button)
    FancyButton saveMaskButton;
    @BindView(R.id.maskindex_floating_button)
    FloatingActionButton maskindexFloatingButton;
    private Handler handler;
    FirstActivity activity;
    private String videoUrl;
    private String flag; //vos or removal
    private String videoFullName;
    private String videoName;
    private String videoDefaultName;
    private String tag;
    public VideoNameBean videoNameBean;
    ControlPanel controlPanel;

    //下载保存图片的变量
    private int fileindex;//选择标注的帧序号
    private String filetype;//下载标注mask图片还是annotation图片
    private int filenum;//视频帧总数
    private int mask_index = 0;//选择标导出的mask序号
    private List<String> maskindexesList = new ArrayList<>();

    //底部sheetDialog变量
    private BottomSheetDialog bottomSheetDialog1;
    private BottomSheetBehavior mDialogBehavior1;
    private LoopView loopView;
    private boolean isMask = false;//是否选择了mask_index

    //弹出alert窗口的变量
    private AlertView mAlertView;

    public FragmentResult() {
    }

    public static FragmentResult newInstance() {
        FragmentResult fragment = new FragmentResult();
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
        handler = activity.handler;
        videoNameBean = new VideoNameBean();
        activity.setResultListener(new FirstActivity.Activity2ResultListener() {
            @Override
            public void hasShowVideo(String s, String s1, int i1, int i2) {
                videoUrl = s;
                flag = s1;
                fileindex = i1;
                filenum = i2;
                mask_index = fileindex;
                Log.d(TAG, "hasShowVideo: videoUrl=" + videoUrl);
                //获得video名字
                String[] strs = videoUrl.split("/"); // 如果是\\需要转义符\\\\
//                for(String str :strs){
//                    Log.d(TAG, "hasShowVideo: s="+str);
//                }
                tag = strs[strs.length - 2];
                ;
                videoFullName = strs[strs.length - 1];
                String[] strs1 = videoFullName.split("\\.");
                videoName = strs1[0];
                if (flag == "vos") {
                    videoDefaultName = strs1[0];
                } else {
                    videoDefaultName = strs1[0];
                }

                //hasShowVideo(videoUrl);
                startPlayer();
                Log.d(TAG, "tag=" + tag + " videoFullName" + " videoName=" + videoName + " videoDefaultName=" + videoDefaultName + " fileindex=" + fileindex + " filenum=" + filenum);
                Log.d(TAG, "hasShowVideo: startPlayer");
            }

        });


    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        super.onCreateView(inflater, container, savedInstanceState);
        View view = inflater.inflate(R.layout.fragment_result_layout, container, false);
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
        initVideoPlayer();
        outputButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "outputbutton被按下，显示video_activity");
                //showVideoSheetDialog();
                videoNameBean.setTag(tag);
                videoNameBean.setVideoDefaultName(videoDefaultName);
                videoNameBean.setVideoFullName(videoFullName);
                videoNameBean.setVideoName(videoName);
                videoNameBean.setVideoUrl(videoUrl);
                videoNameBean.setFlag(flag);
                Message msg = Message.obtain();
                msg.what = 12;
                msg.arg1 = 0;
                msg.obj = videoNameBean;
                handler.sendMessage(msg);
            }
        });

        saveAnnotationButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                filetype = "annotation";
                String iamgeUrl = Urls.imageDownloadUrl + "/" + filetype + "/" + tag + "/" + String.valueOf(fileindex);
                Glide.with(getActivity())
                        .asBitmap()
                        .load(iamgeUrl)
                        .into(new SimpleTarget<Bitmap>() {
                            @Override
                            public void onResourceReady(@NonNull Bitmap resource, @Nullable Transition<? super Bitmap> transition) {
                                saveImage(resource);
                            }
                        });
            }
        });
        
        maskindexFloatingButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "onClick: FloatingButton被按下");
                showIndexSheetDialog();
            }
        });

        saveMaskButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                filetype = "mask";
                String iamgeUrl = Urls.imageDownloadUrl + "/" + filetype + "/" + tag + "/" + String.valueOf(mask_index);
                Glide.with(getActivity())
                        .asBitmap()
                        .load(iamgeUrl)
                        .into(new SimpleTarget<Bitmap>() {
                            @Override
                            public void onResourceReady(@NonNull Bitmap resource, @Nullable Transition<? super Bitmap> transition) {
                                saveImage(resource);
                            }
                        });

            }
        });

    }

    private void showAlertDialog() {
        mAlertView = new AlertView("查看图片", "图片已保存到相册，要现在打开吗？", "取消", new String[]{"确定"}, null, getActivity(), AlertView.Style.Alert, new OnItemClickListener() {
            @Override
            public void onItemClick(Object o, int position) {
                mAlertView.dismiss();
                if (position == AlertView.CANCELPOSITION) {
                    Log.d(TAG, "onItemClick:OnItemClickListener 点击了取消");
                }else{
                    Log.d(TAG, "onItemClick:OnItemClickListener 点击了确定");
                    //跳转到相册
                    Intent photointent = new Intent(Intent.ACTION_PICK);  //跳转到 ACTION_IMAGE_CAPTURE
                    photointent.setType("image/*");
                    startActivityForResult(photointent, 100);
                }

            }
        }).setCancelable(true).setOnDismissListener(new OnDismissListener() {
            @Override
            public void onDismiss(Object o) {
                Log.d(TAG, "onDismiss:setOnDismissListener ");
            }
        });
        mAlertView.show();
    }

    private void saveImage(Bitmap image) {
        String saveImagePath = null;
        Random random = new Random();
        String imageFileName = "dowonload_" + random.nextInt(10) + ".jpg";
        if (filetype.equals("annotation")) {
            imageFileName = tag + "_annotation_" + String.valueOf(fileindex) + ".jpg";
            Log.d(TAG, "saveImage-annotation:imageFileName=" + imageFileName);
        } else if (filetype.equals("mask")) {
            imageFileName = tag + "_mask_" + String.valueOf(mask_index) + ".jpg";
            Log.d(TAG, "saveImage-mask:imageFileName=" + imageFileName);
        }
        File storageDir = new File(Environment.getExternalStoragePublicDirectory
                (Environment.DIRECTORY_PICTURES) + "vos");
        boolean success = true;
        if (!storageDir.exists()) {
            success = storageDir.mkdirs();
        }
        if (success) {
            File imageFile = new File(storageDir, imageFileName);
            saveImagePath = imageFile.getAbsolutePath();
            try {
                OutputStream fout = new FileOutputStream(imageFile);
                image.compress(Bitmap.CompressFormat.JPEG, 100, fout);
                fout.close();
            } catch (Exception e) {
                e.printStackTrace();
            }

            // Add the image to the system gallery
            galleryAddPic(saveImagePath);
            Toast.makeText(getActivity(), "IMAGE SAVED", Toast.LENGTH_LONG).show();
            showAlertDialog();
        }
        //        return saveImagePath;
    }

    private void galleryAddPic(String imagePath) {
        Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
        File f = new File(imagePath);
        Uri contentUri = Uri.fromFile(f);
        mediaScanIntent.setData(contentUri);
        getActivity().sendBroadcast(mediaScanIntent);
    }

    private void showIndexSheetDialog() {
        View view = View.inflate(getActivity(), R.layout.maskindex_dialog_layout, null);
        bottomSheetDialog1 = new BottomSheetDialog(getActivity(), R.style.dialog);
        bottomSheetDialog1.setContentView(view);
        ImageView dialogBottomsheetItertimeClose = view.findViewById(R.id.maskindex_dialog_bottomsheet_iv_close);
        loopView = view.findViewById(R.id.maskindex_loopView);
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
        for (int i = 0; i <= filenum - 1; i++) {
            maskindexesList.add(String.valueOf(i));
        }
        loopView.setItems(maskindexesList);
        loopView.setCurrentPosition(mask_index);
        //设置是否循环播放
//        loopView.setNotLoop();
        loopView.setListener(new OnItemSelectedListener() {
            @Override
            public void onItemSelected(int index) {
                mask_index = index;
                Log.d(TAG, "onItemSelected: 选择的maks_index为" + mask_index);
                Toast.makeText(getActivity(), "选择保存的掩膜图片帧序号为为" + mask_index + "!", Toast.LENGTH_LONG).show();
                bottomSheetDialog1.dismiss();
            }
        });
        bottomSheetDialog1.show();
    }

    private void initVideoPlayer() {
        controlPanel = new ControlPanel(getActivity());
        resultPlayer.setControlPanel(controlPanel);
        MediaPlayerManager.instance().setOnOrientationChangeListener(new OrientationChangeListener());
    }

    private void startPlayer() {
        //设置标题
        TextView tvTitle = controlPanel.findViewById(R.id.tvTitle);
        tvTitle.setText(videoFullName);
        resultPlayer.setUp(videoUrl);
        Log.d(TAG, "initVideoPlayer: videoFullName-" + videoFullName);
        Log.d(TAG, "initVideoPlayer: videoPath-" + videoUrl);
        //MediaPlayerManager.instance().setMediaPlayer(new ExoPlayer(getActivity()));
        MediaPlayerManager.instance().setLooping(true); //循环
        resultPlayer.start();
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

}
