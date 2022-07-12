package com.example.androidapplication.bean;

import java.util.List;

/**
 * Created by wjy on 2020/4/10
 **/
public class BubblenetBean {
    private List<Integer> indexes;
    private List<String> images;
    private String tag;
    private int width;
    private int height;
    private int fps;

    public int getFps() {
        return fps;
    }

    public void setFps(int fps) {
        this.fps = fps;
    }

    public int getWidth() { return width; }

    public int getHeight() { return height; }

    public String getTag(){
        return tag;
    }

    public List<String> getImages(){
        return  images;
    }

    public List<Integer> getIndexes(){
        return indexes;
    }

    public void setTag(String tag){
        this.tag=tag;
    }

    public void setImages(List<String> images){
        this.images=images;
    }

    public void setIndexes(List<Integer> indexes){
        this.indexes=indexes;
    }

    public void setHeight(int height) { this.height = height; }

    public void setWidth(int width) { this.width = width; }

}
