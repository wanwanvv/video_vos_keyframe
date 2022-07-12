package com.example.androidapplication;

import android.content.Intent;
import android.os.Bundle;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import static android.os.SystemClock.sleep;

/**
 * Created by wjy on 2020/5/10
 **/
public class SplashActivity extends AppCompatActivity {
    private static final int WHAT_DELAY = 0x11;// 启动页的延时跳转
    private static final int DELAY_TIME = 3000;// 延时时间

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        new Thread( new Runnable( ) {
            @Override
            public void run() {
                //耗时任务，比如加载网络数据
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        // 这里可以睡几秒钟，如果要放广告的话
                        sleep(DELAY_TIME);
                        goFirstActivity();
                    }
                });
            }
        } ).start();
//        handler.sendEmptyMessageDelayed(WHAT_DELAY, DELAY_TIME);//第一个参数是int表示是什么消息，第二个参数是long-延时发送的时间
//        private Handler handler = new Handler(){
//        @Override
//        public void handleMessage(@NonNull Message msg) {
//            super.handleMessage(msg);
//            switch (msg.what){
//                case WHAT_DELAY:// 延时3秒跳转
//                    goFirstActivity();
//                    break;
//            }
//        }
//    };

    }

    private void goFirstActivity(){
        startActivity(new Intent(SplashActivity.this,FirstActivity.class));
        SplashActivity.this.finish();//销毁当前活动界面
    }

}
