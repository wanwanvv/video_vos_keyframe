package com.example.androidapplication.utils;
import android.util.Log;

import com.example.androidapplication.R;

import java.lang.reflect.Field;

/**
 * Created by wjy on 2020/4/8
 **/
public class ResourceUtil {
    private static final String TAG = "ResourceUtil";
    public static int getMixmapResourceIdByImagename(String imageName){
        Class mipmap = R.mipmap.class;
        try {
            Field field = mipmap.getField(imageName);
            int resId = field.getInt(imageName);
            return resId;
        } catch (NoSuchFieldException e) {
            //如果没有在"mipmap"下找到imageName,将会返回0
            Log.d(TAG, "getMixmapResourceIdByImagename: NoSuchField");
            return 0;
        } catch (IllegalAccessException e) {
            Log.d(TAG, "getMixmapResourceIdByImagename: IllegalAccessException");
            return 0;

        }
    }

    /**
     * 根据手机的分辨率从 dp 的单位 转成为 px(像素)
     */
    public static float dip2px(float scale, float dpValue) {
        //final float scale = context.getResources().getDisplayMetrics().density;
        return (dpValue * scale);
    }

    /**
     * 根据手机的分辨率从 px(像素) 的单位 转成为 dp
     */
    public static float px2dip(float scale, float pxValue) {
        //final float scale = context.getResources().getDisplayMetrics().density;
        return (pxValue / scale );
    }
}
