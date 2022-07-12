package com.example.androidapplication.downloadservice;

/**
 * Created by wjy on 2020/5/7
 **/
public interface DownloadListener {
    void onProgress(int progress);
    void onSuccess();
    void onFailed();
    void onPaused();
    void onCanceled();
}
