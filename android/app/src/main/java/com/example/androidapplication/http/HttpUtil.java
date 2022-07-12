package com.example.androidapplication.http;
import java.io.File;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import android.util.Log;

import com.example.androidapplication.bean.ScribbleBean;
import com.example.androidapplication.bean.VideoBean;
import com.example.androidapplication.progress.MyProgressListener;
import com.example.androidapplication.progress.ProgressRequestBody;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.FormBody;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * Created by wjy on 2020/4/7
 **/
public class HttpUtil {
    private static final String TAG = "HttpUtil";
    //创建client对象
    private static OkHttpClient okHttpClient = new OkHttpClient.Builder().connectTimeout(10000, TimeUnit.MILLISECONDS)
            .readTimeout(10000,TimeUnit.MILLISECONDS)
            .writeTimeout(10000, TimeUnit.MILLISECONDS).build();//设置调用、连接和读写的超时时间
    public static final MediaType JSON=MediaType.parse("application/json; charset=utf-8");
    public static final MediaType MEDIA_TYPE_MARKDOWN = MediaType.parse("text/x-markdown; charset=utf-8");
    public static void postFile(String url, final MyProgressListener listener, okhttp3.Callback callback, File...files){
        MultipartBody.Builder builder = new MultipartBody.Builder();
        builder.setType(MultipartBody.FORM);
        Log.d(TAG, "files[0].getName()=="+files[0].getName());

        //RequestBody.create()方法的返回值也是一个RequestBody对象
        //"application/octet-stream"，这是二进制流传输，在不知道文件类型的情况下可以这么操作
        // 添加表单参数.addFormDataPart(key,value)
        builder.addFormDataPart("myfile",files[0].getName(), RequestBody.create(MediaType.parse("application/octet-stream"),files[0]));

        //MultipartBody则是可以支持多种以及多个RequestBody对象
        MultipartBody multipartBody = builder.build();
        Request request  = new Request.Builder().url(url).post(new ProgressRequestBody(multipartBody,listener)).build();
        okHttpClient.newCall(request).enqueue(callback);
    }
    // 用于连接测试,接受返回字符串
    public static String testConnection(String url){
        final String[] data = new String[1];
        Request request  = new Request.Builder().url(url).get().build();
        Call call = okHttpClient.newCall(request);
        call.enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.d(TAG,"请求失败！！！");
                Log.d(TAG,"e=="+e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                Log.d(TAG,"请求成功！！！");
                data[0] = response.body().string();
                Log.d(TAG,"返回数据data =="+ data[0]);
                //可以在这里更新UI
            }
        });
        //在这里返回数据
        return data[0];
    }
    //用于发送
    public static void send(String url){
        OkHttpClient mOkHttpClient=new OkHttpClient();
        RequestBody formBody = new FormBody.Builder()
                .add("url", url)
                .build();
        Request request = new Request.Builder()
                .url(url)
                .post(formBody)
                .build();
        Call call = mOkHttpClient.newCall(request);
        call.enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
            }
            @Override
            public void onResponse(Call call, Response response) throws IOException {
                String str = response.body().string();
                Log.e(TAG,"内容上传成功！！！！"+str);
            }
        });
    }

    //获取图片
    public static void getFrame(String url,String tag,String model,int itertime,okhttp3.Callback callback){
        //初始化一个 OkHttpClient 并且设置连接和读取超时时间        //构造一个Request对象
        RequestBody formBody = new FormBody.Builder()
                .add("tag", tag)
                .add("model",model)
                .add("itertime",String.valueOf(itertime))
                .build();
        Request request = new Request.Builder()
                .url(url)
                .post(formBody)
                .build();
        OkHttpClient okHttpBubbleNet = new OkHttpClient.Builder().connectTimeout(10000, TimeUnit.MILLISECONDS)
                .readTimeout(160000,TimeUnit.MILLISECONDS)
                .writeTimeout(160000, TimeUnit.MILLISECONDS).build();
        okHttpBubbleNet.newCall(request).enqueue(callback);

    }

    //开始进行分割
    public static void startVos(String url,String tag,int index,okhttp3.Callback callback){
        //初始化一个 OkHttpClient 并且设置连接和读取超时时间        //构造一个Request对象
        RequestBody formBody = new FormBody.Builder()
                .add("tag", tag)
                .add("target",String.valueOf(index))
                .build();
        Request request = new Request.Builder()
                .url(url)
                .post(formBody)
                .build();
        OkHttpClient okHttpClientVos = new OkHttpClient.Builder().connectTimeout(10000, TimeUnit.MILLISECONDS)
                .readTimeout(160000,TimeUnit.MILLISECONDS)
                .writeTimeout(160000, TimeUnit.MILLISECONDS).build();
        okHttpClientVos.newCall(request).enqueue(callback);

    }

    //开始进行目标移除
    public static void startRemoval(String url,String tag,int index,okhttp3.Callback callback){
        //初始化一个 OkHttpClient 并且设置连接和读取超时时间        //构造一个Request对象
        RequestBody formBody = new FormBody.Builder()
                .add("tag", tag)
                .add("target",String.valueOf(index))
                .build();
        Request request = new Request.Builder()
                .url(url)
                .post(formBody)
                .build();
        OkHttpClient okHttpClientVos = new OkHttpClient.Builder().connectTimeout(10000, TimeUnit.MILLISECONDS)
                .readTimeout(160000,TimeUnit.MILLISECONDS)
                .writeTimeout(160000, TimeUnit.MILLISECONDS).build();
        okHttpClientVos.newCall(request).enqueue(callback);

    }

    //目标分割发送scriblle信息
    public static void getAnnotate(String url, ScribbleBean scribbleBean, okhttp3.Callback callback) throws JSONException {
        //初始化一个 OkHttpClient 并且设置连接和读取超时时间        //构造一个Request对象
        String tag=scribbleBean.getTag();
        int size=scribbleBean.getSize();
        int index=scribbleBean.getIndex();
        int type=scribbleBean.getType();
        float[] xposes=scribbleBean.getXposes();
        float[] yposes=scribbleBean.getYposes();
        int[] xposes_line=scribbleBean.getXposes_line();
        int[] yposes_line=scribbleBean.getYposes_line();
        int add=scribbleBean.getAdd(); //为1继续添加,为0是新的
        // 创建json对象
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("add", add);
        jsonObject.put("tag", tag);
        jsonObject.put("size", size);
        jsonObject.put("index", index);
        jsonObject.put("type", type);
        JSONArray xArray = new JSONArray();
        JSONArray yArray = new JSONArray();
        for (float x : xposes) {
            xArray.put(x);
        }for (float y : yposes) {
            yArray.put(y);
        }
        jsonObject.put("xposes", xArray);
        jsonObject.put("yposes", yArray);

        JSONArray xArray_line = new JSONArray();
        JSONArray yArray_line = new JSONArray();
        for (int x_line : xposes_line) {
            xArray_line.put(x_line);
        }for (int y_line : yposes_line) {
            yArray_line.put(y_line);
        }
        jsonObject.put("xposes_line", xArray_line);
        jsonObject.put("yposes_line", yArray_line);

        String data = jsonObject.toString();
        Log.d(TAG, "data:"+data);
        RequestBody body = RequestBody.create(okhttp3.MediaType.parse("application/json;charset=UTF-8"), data);
        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();
        OkHttpClient okHttpClientAnnotate = new OkHttpClient.Builder().connectTimeout(10000, TimeUnit.MILLISECONDS)
                .readTimeout(160000,TimeUnit.MILLISECONDS)
                .writeTimeout(160000, TimeUnit.MILLISECONDS).build();
        okHttpClientAnnotate.newCall(request).enqueue(callback);

    }

    //获取图片
    public static void outputVosVideo(String url, VideoBean videoBean,okhttp3.Callback callback) throws JSONException {
        //初始化一个 OkHttpClient 并且设置连接和读取超时时间        //构造一个Request对象
        String tag=videoBean.getTag();
        String video_name=videoBean.getVideo_name();
        String video_type=videoBean.getVideo_type();
        int video_fps=videoBean.getVideo_fps();
        float video_scale=videoBean.getVideo_scale();
        JSONObject jsonObject = new JSONObject();
        jsonObject.put("tag", tag);
        jsonObject.put("video_name", video_name);
        jsonObject.put("video_type", video_type);
        jsonObject.put("video_fps", video_fps);
        jsonObject.put("video_scale", video_scale);
        String data = jsonObject.toString();
        Log.d(TAG, "data:"+data);
        RequestBody body = RequestBody.create(okhttp3.MediaType.parse("application/json;charset=UTF-8"), data);
        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();
        OkHttpClient okHttpClientAnnotate = new OkHttpClient.Builder().connectTimeout(10000, TimeUnit.MILLISECONDS)
                .readTimeout(10000,TimeUnit.MILLISECONDS)
                .writeTimeout(10000, TimeUnit.MILLISECONDS).build();
        okHttpClientAnnotate.newCall(request).enqueue(callback);

    }

}
