package com.example.androidapplication;

import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.bigkoo.alertview.AlertView;
import com.bigkoo.alertview.OnDismissListener;
import com.bigkoo.alertview.OnItemClickListener;
import com.example.androidapplication.base.BasicActivity;
import com.example.androidapplication.bean.VideoBean;
import com.example.androidapplication.http.HttpUtil;
import com.example.androidapplication.http.MyConstant;
import com.example.androidapplication.http.Urls;
import com.example.androidapplication.utils.StorageUtil;
import com.google.android.material.bottomsheet.BottomSheetBehavior;
import com.google.android.material.bottomsheet.BottomSheetDialog;
import com.obsez.android.lib.filechooser.ChooserDialog;
import com.rengwuxian.materialedittext.MaterialEditText;
import com.weigan.loopview.LoopView;
import com.weigan.loopview.OnItemSelectedListener;
import com.wuhenzhizao.titlebar.widget.CommonTitleBar;
import com.zaaach.toprightmenu.MenuItem;
import com.zaaach.toprightmenu.TopRightMenu;
import com.zkk.view.rulerview.RulerView;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;
import github.ishaan.buttonprogressbar.ButtonProgressBar;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import static com.example.androidapplication.FirstActivity.pixHeight;

/**
 * Created by wjy on 2020/4/16
 **/
public class VideoOutputActivity extends BasicActivity {
    private static final String TAG = "VideoOutputActivity";


    //????????????????????????
    VideoBean videoBean;
    @BindView(R.id.titlebar)
    CommonTitleBar titlebar;
    @BindView(R.id.video_name_textview)
    TextView videoNameTextview;
    @BindView(R.id.video_name_edittext)
    MaterialEditText videoNameEdittext;
    @BindView(R.id.video_name_linearlayout)
    LinearLayout videoNameLinearlayout;
    @BindView(R.id.video_type_textview)
    TextView videoTypeTextview;
    @BindView(R.id.mp4_radiobutton)
    RadioButton mp4Radiobutton;
    @BindView(R.id.avi_radiobutton)
    RadioButton aviRadiobutton;
    @BindView(R.id.video_type_radiogroup)
    RadioGroup videoTypeRadiogroup;
    @BindView(R.id.video_type_linearlayout)
    LinearLayout videoTypeLinearlayout;
    @BindView(R.id.video_fps_textview)
    TextView videoFpsTextview;
    @BindView(R.id.video_fps_edittext)
    MaterialEditText videoFpsEdittext;
    @BindView(R.id.video_fps_linearlayout)
    LinearLayout videoFpsLinearlayout;
    @BindView(R.id.video_scale_textview)
    TextView videoScaleTextview;
    @BindView(R.id.video_scale_edittext)
    MaterialEditText videoScaleEdittext;
    @BindView(R.id.video_scale_linearlayout)
    LinearLayout videoScaleLinearlayout;
    @BindView(R.id.video_folder_textview)
    TextView videoFolderTextview;
    @BindView(R.id.video_folder_edittext)
    MaterialEditText videoFolderEdittext;
    @BindView(R.id.video_folder_linearlayout)
    LinearLayout videoFolderLinearlayout;
    @BindView(R.id.video_fps_downbutton)
    Button videoFpsDownbutton;
    @BindView(R.id.video_scale_downbutton)
    Button videoScaleDownbutton;
    @BindView(R.id.video_folder_downbutton)
    Button videoFolderDownbutton;
    @BindView(R.id.button_progress_bar)
    ButtonProgressBar buttonProgressBar;
    //scale ruler??????
    private BottomSheetDialog scaleBottomSheetDialog;
    private BottomSheetBehavior scaleDialogBehavior;
    //fps????????????
    private BottomSheetDialog bottomSheetDialog;
    private BottomSheetBehavior mDialogBehavior;
    private LoopView loopView;
    private List<String> itertimeList = new ArrayList<>();
    //????????????
    String tag;
    String flag;
    String videoFullName;
    String video_name;
    String video_type;
    String video_flag;
    int video_fps;
    float video_scale;
    String video_path;
    int progress=0;

    //?????????????????????????????????
    String outputvideo;
    String outputtag;
    String outputflag;
    int fps;
    boolean uploadIsBusy=false;

    /*****************menu***************/
    //????????????
    private TopRightMenu mTopRightMenu;
    //??????imageView
    private ImageView moreBtn;
    //???????????????
    private AlertView versionAlertView;
    /***************menu*************/

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        Intent intent = getIntent();
        tag = intent.getStringExtra("tag");
        video_name = intent.getStringExtra("videoDefaultName");
        videoFullName = intent.getStringExtra("videoFullName");
        flag=intent.getStringExtra("flag");
        fps=intent.getIntExtra("fps",22);
        Log.d(TAG, "onCreate:  tag-" + tag + " video_name-" + video_name + " videoFullName-" + videoFullName+" flag="+flag);
        super.onCreate(savedInstanceState);
        //?????????butterknife
        setContentView(R.layout.video_activity_layout);
        ButterKnife.bind(this);
        //??????????????????????????????
        initTitleBar();
        //???????????????
        setDefaultValues();
        //radioButton
        videoTypeRadiogroup.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(RadioGroup group, int checkedId) {
                //videoTypeRadiogroup.clearCheck();
                switch (checkedId) {
                    case R.id.mp4_radiobutton:
                        video_type = "MP4";
                        //mp4Radiobutton.setChecked(true);
                        Log.d(TAG, "radiobutton:video_type=" + video_type);
                        break;
                    case R.id.avi_radiobutton:
                        video_type = "AVI";

                        Log.d(TAG, "radiobutton:video_type=" + video_type);
                        break;
                }
            }
        });
        //??????????????????
        videoFpsDownbutton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "onClick: fpsbutton?????????");
                showFpsSheetDialog();
            }
        });
        videoScaleDownbutton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "onClick: scalebutton?????????");
                showScaleSheetDialog();
            }
        });
        videoFolderDownbutton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "onClick: folderbutton?????????");
                new ChooserDialog(VideoOutputActivity.this)
                        .withFilter(true, false)
                        .cancelOnTouchOutside(true)
                        .withStartFile(video_path)
                        .withNavigateUpTo(new ChooserDialog.CanNavigateUp() {
                            @Override
                            public boolean canUpTo(File dir) {
                                Log.d(TAG, "canUpTo:navigate");
                                return true;
                            }
                        })
                        .withIcon(R.drawable.folder_32)
                        //.withLayoutView(R.layout.alert_file_chooser) // (API > 20)
                        // to handle the result(s)
                        .withOnCancelListener(new DialogInterface.OnCancelListener() {
                            public void onCancel(DialogInterface dialog) {
                                Log.d(TAG, "CANCEL");
                            }
                        })
                        .withChosenListener(new ChooserDialog.Result() {
                            @Override
                            public void onChoosePath(String path, File pathFile) {
                                video_path = path;
                                videoFolderEdittext.setText(video_path);
                                Log.d(TAG, "onChoosePath: video_path=" + video_path);
                                Toast.makeText(VideoOutputActivity.this, "FOLDER: " + path, Toast.LENGTH_SHORT).show();
                            }
                        })
                        .build()
                        .show();
            }
        });
        //????????????
        buttonProgressBar.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                boolean isChecked=checkValues();
                if(isChecked){
                    //callHandler();
                    progress=0;
                    buttonProgressBar.startLoader();
                    uploadIsBusy=true;
                    //http util
                    String outputUrl;
                    if(flag.equals("vos")){
                        outputUrl=Urls.outputVosVideoUrl;
                    } else {
                        outputUrl=Urls.outputRemovalVideoUrl;
                    }
                    Log.d(TAG, "onClick: outputUrl="+outputUrl);
                    try {
                        HttpUtil.outputVosVideo(outputUrl, videoBean,new Callback() {
                            @Override
                            public void onFailure(Call call, IOException e) {
                                Log.d(TAG, "onFailure: e==" + e.getMessage());
                            }

                            @Override
                            public void onResponse(Call call, Response response) throws IOException {
                                uploadIsBusy=false;
                                if (response != null) {
                                    String outputResponseData = response.body().string();
                                    Log.d(TAG, "onResponse: result==" + outputResponseData);
                                    //??????json??????
                                    if(outputResponseData.equals("404")){
                                        VideoOutputActivity.this.runOnUiThread(new Runnable() {
                                            @Override
                                            public void run() {
                                                Log.d(TAG, "404");
                                                Toast.makeText(VideoOutputActivity.this, "??????????????????????????????????????????!", Toast.LENGTH_LONG).show();
                                                //buttonProgressBar.setLoaderType(ButtonProgressBar.Type.DETERMINATE);
                                            }
                                        });
                                    }else{
                                        parseOutputJson(outputResponseData);
                                        progress=100;
                                        VideoOutputActivity.this.runOnUiThread(new Runnable() {
                                            @Override
                                            public void run() {
                                                Log.d(TAG, "?????????????????????UI");
                                                buttonProgressBar.stopLoader();
                                                outputCallBack();
                                                //buttonProgressBar.setLoaderType(ButtonProgressBar.Type.INDETERMINATE);
                                            }
                                        });

                                    }
                                }
                            }

                        });
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                }else{
                    uploadIsBusy=false;
                    return;
                }

            }
        });

    }

    //??????FirstActivity??????????????????
    public void outputCallBack(){
        Intent intent = new Intent();
        String downloadUrl=Urls.videoDownloadUrl+"/"+outputflag+"/"+outputtag+"/"+outputvideo;
        String fileUrl=Urls.fileDownloadUrl+"/"+outputflag+"/"+outputtag+"/"+outputvideo;
        String directory=video_path+"/"+outputvideo;
        intent.putExtra("downloadUrl", downloadUrl);
        intent.putExtra("fileUrl", fileUrl); //???????????????????????????url
        intent.putExtra("directory", directory);
        setResult(MyConstant.RESULT_CODE_VIDEO_FRAME, intent);
        finish();
    }

    private void parseOutputJson(String responseData) throws IOException {
        try {
            JSONObject jsonObject=new JSONObject(responseData);
            //JSONArray jsonArray = new JSONArray(responseData);
            //JSONObject jsonObject = jsonArray.getJSONObject(i);
            outputvideo = jsonObject.getString("outputvideo");
            outputtag = jsonObject.getString("outputtag");
            outputflag = jsonObject.getString("outputflag");
            Log.d(TAG, "parseOutputJson: outputvideo="+outputvideo+" ouputtag="+outputtag+" outputflag="+outputflag);
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void callHandler() {
        Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                if (progress <= 100) {
                    updateUI();
                    progress++;
                    callHandler();
                } else {
                    progress = 0;
                    updateUI();
                    progress++;
                    callHandler();
                }
            }
        }, 20);
    }

    public void updateUI() {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                buttonProgressBar.setProgress(progress);
            }
        });
    }

    public boolean checkValues() {
        video_name = videoNameEdittext.getText().toString();
        if (video_name == null || video_name == "") {
            Toast.makeText(VideoOutputActivity.this, "???????????????????????????", Toast.LENGTH_SHORT).show();
            return false;
        }
        video_scale = Float.parseFloat(videoScaleEdittext.getText().toString());
        if (video_scale < 0.1 || video_scale > 10.0) {
            Toast.makeText(VideoOutputActivity.this, "?????????0.1~10.0????????????????????????", Toast.LENGTH_SHORT).show();
            return false;
        }
        video_fps = Integer.parseInt(videoFpsEdittext.getText().toString());
        if (video_fps <= 0 || video_fps >= 100) {
            Toast.makeText(VideoOutputActivity.this, "?????????1~100?????????????????????", Toast.LENGTH_SHORT).show();
            return false;
        }
        video_path = videoFolderEdittext.getText().toString();
        if (video_path == null || video_path.length() == 0) {
            Toast.makeText(VideoOutputActivity.this, "???????????????????????????", Toast.LENGTH_SHORT).show();
            return false;
        } else if (!StorageUtil.isFolderExists(video_path)) {
            Toast.makeText(VideoOutputActivity.this, "????????????????????????????????????", Toast.LENGTH_SHORT).show();
            return false;
        }
        videoBean = new VideoBean();
        videoBean.setVideo_name(video_name);
        videoBean.setVideo_flag(flag);
        videoBean.setVideo_fps(video_fps);
        videoBean.setVideo_path(video_path);
        videoBean.setVideo_scale(video_scale);
        videoBean.setVideo_type(video_type);
        videoBean.setTag(tag);
        Log.d(TAG, "checkValues: tag="+tag+" video_name=" + video_name + " video_type=" + video_type + " video_fps=" + video_fps + " video_scale=" + video_scale + " video_path=" + video_path);
        return true;
    }

    // ????????????????????????
    public void setDefaultValues() {
        //String video_name;
        Log.d(TAG, "setDefaultValues: ");
        video_type = "MP4";
        video_fps = fps;
        video_scale = (float) 1.00;
        //video_path = Environment.getExternalStorageDirectory().getPath();
        //video_path=Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES).toString();
        video_path=Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getPath();
        videoFolderEdittext.setText(video_path);
        videoFpsEdittext.setText(String.valueOf(video_fps));
        videoNameEdittext.setText(video_name);
        videoScaleEdittext.setText(String.valueOf(video_scale));
        videoTypeRadiogroup.clearCheck();
        mp4Radiobutton.setChecked(true);
    }

    public void initTitleBar() {
        //View centerview=LayoutInflater.from(this).inflate(annotate_frame_centerview, null, false);
        //titlebar.setCenterView(centerview);
        View rightCustomLayout = titlebar.getRightCustomView();
        TextView textView = titlebar.getCenterTextView();
        textView.setText("??????????????????");
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
                    if(uploadIsBusy==true){
                        return;
                    }
                    Log.d(TAG, "onClicked: ??????ImageBtn?????????");
                    Intent intent = new Intent();
                    intent.putExtra("return_data", "VideoOutputActivity");
                    setResult(MyConstant.RESULT_CODE_VIDEO_BACK_FRAME, intent);
                    finish();
                }
                // CommonTitleBar.ACTION_LEFT_TEXT;        // ??????TextView?????????
                // CommonTitleBar.ACTION_LEFT_BUTTON;      // ??????ImageBtn?????????
                // CommonTitleBar.ACTION_RIGHT_TEXT;       // ??????TextView?????????
                // CommonTitleBar.ACTION_RIGHT_BUTTON;     // ??????ImageBtn?????????
                // CommonTitleBar.ACTION_SEARCH;           // ??????????????????,?????????????????????????????????????????????
                // CommonTitleBar.ACTION_SEARCH_SUBMIT;    // ????????????????????????,??????????????????????????????extra???????????????
                // CommonTitleBar.ACTION_SEARCH_VOICE;     // ?????????????????????
                // CommonTitleBar.ACTION_SEARCH_DELETE;    // ???????????????????????????
                // CommonTitleBar.ACTION_CENTER_TEXT;      // ??????????????????
            }
        });

    }

    private void showFpsSheetDialog() {
        View view = View.inflate(this, R.layout.fps_dialog_layout, null);
        bottomSheetDialog = new BottomSheetDialog(this, R.style.dialog);
        bottomSheetDialog.setContentView(view);
        ImageView dialogBottomsheetItertimeClose = view.findViewById(R.id.fps_dialog_bottomsheet_iv_close);
        loopView = view.findViewById(R.id.fps_loopView);

        mDialogBehavior = BottomSheetBehavior.from((View) view.getParent());
        int peekHeight = Math.round(pixHeight / 2); //????????????
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

        dialogBottomsheetItertimeClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                bottomSheetDialog.dismiss();
            }
        });

        //???????????????
        for (int i = 1; i <= 100; i++) {
            itertimeList.add(String.valueOf(i));
        }
        loopView.setItems(itertimeList);
        loopView.setCurrentPosition(fps-1);
        //????????????????????????
//        loopView.setNotLoop();
        loopView.setListener(new OnItemSelectedListener() {
            @Override
            public void onItemSelected(int index) {
                int fps = index + 1;
                Log.d(TAG, "onItemSelected: ?????????fps??????" + fps);
                video_fps = fps;
                videoFpsEdittext.setText(String.valueOf(video_fps));
                Toast.makeText(VideoOutputActivity.this, "?????????BubbleNet???????????????" + fps + "!", Toast.LENGTH_LONG).show();
                bottomSheetDialog.dismiss();
            }
        });


        bottomSheetDialog.show();
    }

    private void showScaleSheetDialog() {
        View view = View.inflate(this, R.layout.scale_dialog_layout, null);
        scaleBottomSheetDialog = new BottomSheetDialog(this, R.style.dialog);
        scaleBottomSheetDialog.setContentView(view);

        ImageView dialogBottomsheetItertimeClose = view.findViewById(R.id.scale_dialog_bottomsheet_iv_close);
        RulerView rulerView = view.findViewById(R.id.scale_rulerview);
        TextView scaleTextView = view.findViewById(R.id.scale_value_textview);

        scaleDialogBehavior = BottomSheetBehavior.from((View) view.getParent());
        int peekHeight = Math.round(pixHeight / 2); //????????????
        scaleDialogBehavior.setPeekHeight(peekHeight);
        scaleDialogBehavior.setBottomSheetCallback(new BottomSheetBehavior.BottomSheetCallback() {
            @Override
            public void onStateChanged(@NonNull View bottomSheet, int newState) {
                if (newState == BottomSheetBehavior.STATE_HIDDEN) {
                    scaleBottomSheetDialog.dismiss();
                    scaleDialogBehavior.setState(BottomSheetBehavior.STATE_COLLAPSED);
                }
            }

            @Override
            public void onSlide(@NonNull View bottomSheet, float slideOffset) {
            }
        });

        dialogBottomsheetItertimeClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                scaleBottomSheetDialog.dismiss();
            }
        });
        rulerView.setOnValueChangeListener(new RulerView.OnValueChangeListener() {
            @Override
            public void onValueChange(float value) {
                String value_decimal = String.format("%.1f", value);
                scaleTextView.setText(value_decimal + "");
                video_scale = Float.parseFloat(value_decimal);
                videoScaleEdittext.setText(String.valueOf(video_scale));
                Log.d(TAG, "onValueChange: video_scale=" + video_scale);
                //scaleBottomSheetDialog.dismiss();
            }
        });
        rulerView.setValue(1.0f, 0.1f, 10.0f, 0.1f);
        scaleBottomSheetDialog.show();
    }

    /************************menu**********************/
    private void showTopRightMenu() {
        mTopRightMenu = new TopRightMenu(VideoOutputActivity.this);
        //???????????????
        List<MenuItem> menuItems = new ArrayList<>();
        menuItems.add(new MenuItem(R.mipmap.about_black_32, "??????"));
        menuItems.add(new MenuItem(R.mipmap.share_black_32, "??????"));
        menuItems.add(new MenuItem(R.mipmap.setting_black_32, "??????"));
        menuItems.add(new MenuItem(R.mipmap.update_black_32, "????????????"));
        menuItems.add(new MenuItem(R.mipmap.feedback1_black_32, "???????????????"));
        menuItems.add(new MenuItem(R.mipmap.sort_black_32, "??????????????????"));
        mTopRightMenu
                .setHeight(MyConstant.POPVIEW_HEIGHT)     //????????????480
//                .setWidth(320)      //????????????wrap_content
                .showIcon(true)     //??????????????????????????????true
                .dimBackground(true)        //????????????????????????true
                .needAnimationStyle(true)   //????????????????????????true
                .setAnimationStyle(R.style.TRM_ANIM_STYLE)
                .addMenuList(menuItems)
                .setOnMenuItemClickListener(new TopRightMenu.OnMenuItemClickListener() {
                    @Override
                    public void onMenuItemClick(int position) {
                        Log.d(TAG, "onMenuItemClick: ??????????????????position=" + position);
                        switch (position){
                            case 0:
                                Intent about_intent=new Intent(VideoOutputActivity.this,AboutActivity.class);
                                about_intent.putExtra("start_activity","VideoOutputActivity");
                                startActivityForResult(about_intent,MyConstant.REQUEST_CODE_ABOUT_FRAME_OUTPUT);
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
                .showAsDropDown(moreBtn, -225, 0);	//????????????
//      		.showAsDropDown(moreBtn)
    }
    private void showVersionAlertDialog() {
        versionAlertView = new AlertView("????????????", "????????????v1.0\n????????????:????????????,????????????", "", new String[]{"????????????","????????????"}, null, VideoOutputActivity.this, AlertView.Style.Alert, new OnItemClickListener() {
            @Override
            public void onItemClick(Object o, int position) {
                Log.d(TAG, "onItemClick:OnItemClickListener ???????????????");
                if (position == AlertView.CANCELPOSITION) {
                    Log.d(TAG, "onItemClick:OnItemClickListener ???????????????");
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
