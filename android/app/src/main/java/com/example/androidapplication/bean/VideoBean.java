package com.example.androidapplication.bean;

/**
 * Created by wjy on 2020/4/16
 **/
public class VideoBean {
    //导出视频参数变量
    private String video_name;
    private String video_type;
    private int video_fps;
    private float video_scale;
    private String video_path;
    private String video_flag;
    private String tag;

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    public String getVideo_flag() {
        return video_flag;
    }

    public void setVideo_flag(String video_flag) {
        this.video_flag = video_flag;
    }

    public float getVideo_scale() {
        return video_scale;
    }

    public String getVideo_type() {
        return video_type;
    }

    public void setVideo_type(String video_type) {
        this.video_type = video_type;
    }

    public void setVideo_scale(float video_scale) {
        this.video_scale = video_scale;
    }

    public String getVideo_path() {
        return video_path;
    }

    public void setVideo_path(String video_path) {
        this.video_path = video_path;
    }

    public String getVideo_name() {
        return video_name;
    }

    public void setVideo_name(String video_name) {
        this.video_name = video_name;
    }

    public int getVideo_fps() {
        return video_fps;
    }

    public void setVideo_fps(int video_fps) {
        this.video_fps = video_fps;
    }


}
