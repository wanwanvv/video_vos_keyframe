package com.example.androidapplication.bean;

/**
 * Created by wjy on 2020/4/17
 **/
public class VideoNameBean {
    private String flag;

    public String getFlag() {
        return flag;
    }

    public void setFlag(String flag) {
        this.flag = flag;
    }

    private String videoUrl;
    private String videoFullName;
    private String videoName;
    private String videoDefaultName;
    private String tag;

    public String getVideoFullName() {
        return videoFullName;
    }

    public String getVideoUrl() {
        return videoUrl;
    }

    public void setVideoUrl(String videoUrl) {
        this.videoUrl = videoUrl;
    }

    public String getVideoName() {
        return videoName;
    }

    public void setVideoName(String videoName) {
        this.videoName = videoName;
    }

    public void setVideoFullName(String videoFullName) {
        this.videoFullName = videoFullName;
    }

    public String getVideoDefaultName() {
        return videoDefaultName;
    }

    public void setVideoDefaultName(String videoDefaultName) {
        this.videoDefaultName = videoDefaultName;
    }

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }
}
