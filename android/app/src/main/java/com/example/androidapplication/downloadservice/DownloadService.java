package com.example.androidapplication.downloadservice;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.graphics.BitmapFactory;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;
import android.widget.Toast;

import com.example.androidapplication.FirstActivity;
import com.example.androidapplication.R;
import com.example.androidapplication.http.MyConstant;

import java.io.File;

public class DownloadService extends Service {
    private DownloadTask downloadTask;
    private String downloadUrl;
    private String fileUrl;
    private String filePath;
    private static final String TAG = "DownloadService";

    public DownloadService() {
    }

    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "onCreate: ");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        int type=intent.getIntExtra("type",1);
        downloadUrl=intent.getStringExtra("downloadUrl");
        fileUrl=intent.getStringExtra("fileUrl");
        filePath=intent.getStringExtra("directory");
        Log.d(TAG, "onStartCommand: type="+type+" downloadUrl+"+downloadUrl+" fileUrl="+fileUrl+" filePath="+filePath);
        downloadTask=new DownloadTask(listener);
        downloadTask.execute(downloadUrl,fileUrl,filePath);
        Log.d(TAG, "onStartCommand: downloadTask.execute");
        //前台服务，在系统状态栏持续运行
        startForeground(1,getNotification("Downloading...",0));
        Log.d(TAG, "onStartCommand: 执行完startForeground");
        Toast.makeText(DownloadService.this,"Downloadin...",Toast.LENGTH_SHORT).show();
        return super.onStartCommand(intent, flags, startId);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        stopForeground(true);
        Log.d(TAG, "onDestroy: stopForeground(true)");
    }

    private DownloadListener listener=new DownloadListener() {
        @Override
        public void onProgress(int progress) {
            //notify让通知显示，第一个参数是id,保证每个通知的id不同
            getNotificationManager().notify(1,getNotification("Downloading...",progress));
        }

        @Override
        public void onSuccess() {
            downloadTask=null;
            //下载成功时将前台服务通知关闭，并创建一个下载成功的通知
            getNotificationManager().notify(1,getNotification("Download Success",-1));
            Log.d(TAG, "onSuccess: notify完毕");
            stopForeground(true);
            Log.d(TAG, "onSuccess: stopForeground(true)");
            Toast.makeText(DownloadService.this,"Download Success",Toast.LENGTH_SHORT).show();
            stopSelf();
        }

        @Override
        public void onFailed() {
            downloadTask=null;
            getNotificationManager().notify(1,getNotification("Download Failed",-1));
            Log.d(TAG, "onFailed: notify完毕");
            stopForeground(true);
            Log.d(TAG, "onFailed: stopForeground(true)");
            Toast.makeText(DownloadService.this,"Download Failed",Toast.LENGTH_SHORT).show();
            stopSelf();
        }

        @Override
        public void onPaused() {
            downloadTask=null;
            Toast.makeText(DownloadService.this,"Paused",Toast.LENGTH_SHORT).show();
        }

        @Override
        public void onCanceled() {
            downloadTask=null;
            stopForeground(true);
            Toast.makeText(DownloadService.this,"Canceled",Toast.LENGTH_SHORT).show();
        }
    };

    private DownloadBinder mBinder=new DownloadBinder();

    @Override
    public IBinder onBind(Intent intent) {
        // TODO: Return the communication channel to the service.
        Log.d(TAG, "onBind: return mBinder");
        return mBinder;
    }

    //DownloadBinder是为了让活动和服务进行通信
    public class DownloadBinder extends Binder{
        public void startDownload(String downloadurl,String fileurl,String filepath){
            if(downloadTask==null){
                downloadUrl=downloadurl;
                fileUrl=fileurl;
                filePath=filepath;
                downloadTask=new DownloadTask(listener);
                downloadTask.execute(downloadUrl,fileUrl,filePath);
                Log.d(TAG, "startDownload.execute");
                //前台服务，在系统状态栏持续运行
                startForeground(1,getNotification("Downloading...",0));
                Log.d(TAG, "startDownload: 执行完startForeground");
                Toast.makeText(DownloadService.this,"Downloadin...",Toast.LENGTH_SHORT).show();
            }
        }

        private void PauseDownload(){
            if(downloadTask!=null){
                downloadTask.pauseDownload();
            }
        }

        private void cancelDownload(){
            if(downloadTask!=null){
                downloadTask.cancelDownload();
            }
            if(downloadUrl!=null){
                //取消下载时需将文件删除，并将通知关闭
                File file=new File(filePath);
                if(file.exists()){
                    file.delete();
                }
                getNotificationManager().cancel(1);
                stopForeground(true);
                Toast.makeText(DownloadService.this,"Canceled",Toast.LENGTH_SHORT).show();
            }
        }

    }

    /**
     * 获取通知管理器的实例
     * @return
     */
    private NotificationManager getNotificationManager(){
        return (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
    }

    /**
     * 向用户提供信息，而程序不在前台运行
     * @param title
     * @param progress
     * @return
     */
    private Notification getNotification(String title,int progress){
        Intent intent=new Intent(this, FirstActivity.class);
        PendingIntent pi=PendingIntent.getActivity(this,0,intent,0);
        //NotificationCompat.Builder builder=new NotificationCompat.Builder(this);
        Notification.Builder builder=new Notification.Builder(this);
        builder.setSmallIcon(R.mipmap.ic_download);//通知的小图标
        builder.setLargeIcon(BitmapFactory.decodeResource(getResources(),R.mipmap.ic_download));
        builder.setContentIntent(pi);
        builder.setContentTitle(title); //通知的标题内容
        //当进度大于等于0时才需要显示下载进度
        if(progress>=0){
            builder.setContentText(progress+"%"); //通知的正文内容
            //第三个参数是否使用模糊进度条
            builder.setProgress(100,progress,false);
        }

        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            Log.d(TAG, "getNotification: 创建notification Channel");
            //修改安卓8.1以上系统报错
            NotificationChannel notificationChannel = new NotificationChannel(MyConstant.CHANNEL_ONE_ID, MyConstant.CHANNEL_ONE_NAME,NotificationManager.IMPORTANCE_HIGH);
            notificationChannel.enableLights(false);//如果使用中的设备支持通知灯，则说明此通知通道是否应显示灯
            notificationChannel.setShowBadge(true);//是否显示角标
            notificationChannel.enableVibration(true);//设置通知出现时的震动（如果 android 设备支持的话）
            notificationChannel.setLockscreenVisibility(Notification.VISIBILITY_SECRET);
            //manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            getNotificationManager().createNotificationChannel(notificationChannel);
            builder.setChannelId(MyConstant.CHANNEL_ONE_ID);
        }

        return builder.build();
    }

}
