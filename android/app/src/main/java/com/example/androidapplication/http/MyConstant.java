package com.example.androidapplication.http;

/**
 * Created by wjy on 2020/4/12
 **/
public class MyConstant {
    public static final int FRAME_COUNT=3;
    public static final int FRAGMENT0=10;
    public static final int FRAGMENT1=11;
    public static final int FRAGMENT2=12;
    public static final int POPVIEW_HEIGHT=820;

    public static final String[] titles={"打开视频","选择关键帧","导出结果文件"};
    public static final String CHANNEL_ONE_ID="d001";
    public static final String CHANNEL_ONE_NAME="videoDownload";

    public static final int REQUEST_CODE_ANNOTATE_FRAME = 0x500;
    public static final int RESULT_CODE_ANNOTATE_FRAME = 0x501;
    public static final int RESULT_CODE_ANNOTATE_BACK_FRAME = 0x502;
    public static final int REQUEST_CODE_VIDEO_FRAME = 0x503;
    public static final int RESULT_CODE_VIDEO_FRAME = 0x504;
    public static final int RESULT_CODE_VIDEO_BACK_FRAME = 0x505;
    public static final int REQUEST_CODE_ABOUT_FRAME = 0x506;
    public static final int REQUEST_CODE_ABOUT_FRAME_ANNOTATE = 0x507;
    public static final int REQUEST_CODE_ABOUT_FRAME_OUTPUT = 0x508;
}
