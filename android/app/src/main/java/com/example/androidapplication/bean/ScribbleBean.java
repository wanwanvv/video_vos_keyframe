package com.example.androidapplication.bean;

/**
 * Created by wjy on 2020/4/14
 **/
public class ScribbleBean {
    private int size;
    private int index;
    private String tag;
//    private ArrayList<ViewPoint> path;
    private float[] xposes;
    private float[] yposes;
    private int[] xposes_line;
    private int[] yposes_line;

    public int[] getXposes_line() {
        return xposes_line;
    }

    public void setXposes_line(int[] xposes_line) {
        this.xposes_line = xposes_line;
    }


    public int[] getYposes_line() {
        return yposes_line;
    }

    public void setYposes_line(int[] yposes_line) {
        this.yposes_line = yposes_line;
    }


    private int add;//0是第一次,1是后续添加

    public int getType() {
        return type;
    }

    public void setType(int type) {
        this.type = type;
    }

    private int type; //0是前景点，1是背景点

    public int getAdd() {
        return add;
    }

    public void setAdd(int add) {
        this.add = add;
    }


    public int getIndex() {
        return index;
    }

    public void setIndex(int index) {
        this.index = index;
    }

//    public ArrayList<ViewPoint> getPath() {
//        return path;
//    }

    public float[] getYposes() {
        return yposes;
    }

    public void setYposes(float[] yposes) {
        this.yposes = yposes;
    }

    public float[] getXposes() {
        return xposes;
    }

    public void setXposes(float[] xposes) {
        this.xposes = xposes;
    }

    public String getTag() {
        return tag;
    }

    public void setTag(String tag) {
        this.tag = tag;
    }

    public int getSize() {
        return size;
    }

    public void setSize(int size) {
        this.size = size;
    }

//    public void setPath(ArrayList<ViewPoint> path) {
//        this.path = path;
//    }


}
