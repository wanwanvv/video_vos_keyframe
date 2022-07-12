package com.example.androidapplication.progress;

/**
 * Created by wjy on 2020/4/7
 **/
public interface MyProgressListener {
    void onProgress(long currentBytes, long contentLength, boolean done);
}
