package com.example.androidapplication.utils;

import android.os.Environment;
import android.util.Log;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by wjy on 2020/4/17
 **/
public class StorageUtil {
    private static final String TAG = "StorageUtil";
    public static List<String> getFilesAllName(String path) {
        Log.d(TAG, "***********************"+path+"**********************");
        File file=new File(path);
        File[] files=file.listFiles();
        if (files == null){
            Log.e(TAG+"--error","空目录");return null;}
        List<String> s = new ArrayList<>();
        for(int i =0;i<files.length;i++){
            File filePath=files[i].getAbsoluteFile();
            Log.d(TAG, "filePath="+filePath.toString());
            s.add(files[i].getAbsolutePath());
        }
        Log.d(TAG, "***********************"+path+"**********************");
        return s;

    }

    public static  String getCameraPath(){
        String cameraPath=Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DCIM).getAbsolutePath();
        Log.d(TAG, "CameraPath=="+cameraPath);
        return cameraPath;
    }

    public static boolean isFolderExists(String strFolder)
    {
        File file = new File(strFolder);
        if (!file.exists())
        {
            return false;
        }else{
            return true;
        }

    }

}
