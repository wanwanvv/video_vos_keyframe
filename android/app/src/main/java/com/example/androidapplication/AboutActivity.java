package com.example.androidapplication;

import android.content.Intent;
import android.content.res.Configuration;
import android.os.Bundle;

import java.io.InputStream;
import java.util.Calendar;
import android.util.Log;
import android.view.Gravity;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;

import mehdi.sakout.aboutpage.AboutPage;
import mehdi.sakout.aboutpage.Element;
import com.example.androidapplication.http.MyConstant;
import com.wuhenzhizao.titlebar.widget.CommonTitleBar;

import butterknife.BindView;
import butterknife.ButterKnife;

/**
 * Created by wjy on 2020/5/11
 **/
public class AboutActivity extends AppCompatActivity {
    private static final String TAG = "AboutActivity";
    //Element
    public Element adsElement;
    //哪个activity发起的Intent
    private String start_activity;
    //aboutPage view
    private View aboutPage;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        //布局及butterknife
//        setContentView(R.layout.about_activity_layout);
//        ButterKnife.bind(this);
        //设置标题栏及点击事件
//        initTitleBar();
        Intent intent=getIntent();
        start_activity=intent.getStringExtra("start_activity");
        Log.d(TAG, "onCreate: start_activity="+start_activity);
        initAboutView();
        setContentView(aboutPage);
        ButterKnife.bind(this);
    }

    private void initAboutView(){
        simulateDayNight(/* DAY */ 0);
        adsElement = new Element();
        adsElement.setTitle("Advertise with us");
        aboutPage = new AboutPage(this)
                .setDescription(getString(R.string.app_description))
                .isRTL(false)
                .setImage(R.drawable.dummy_splash)
                .addItem(new Element().setTitle("Version 1.0"))
                .addItem(adsElement)
                .addGroup("Connect with us")
                .addEmail("ijingyiwan@gmail.com")
                .addWebsite("https://github.com/wanwanvv")
                .addFacebook("wanwanvv")
                .addYoutube("UCdPQtdWIsg7_pi4mrRu46vA")
                .addInstagram("wanwanvv")
                .addGitHub("wanwanvv")
                .addItem(getCopyRightsElement())
                .create();
    }

    Element getCopyRightsElement() {
        Element copyRightsElement = new Element();
        final String copyrights = String.format(getString(R.string.copy_right), Calendar.getInstance().get(Calendar.YEAR));
        copyRightsElement.setTitle(copyrights);
        //copyRightsElement.setIconDrawable(R.drawable.about_icon_copy_right);
        copyRightsElement.setIconTint(mehdi.sakout.aboutpage.R.color.about_item_icon_color);
        copyRightsElement.setIconNightTint(android.R.color.white);
        copyRightsElement.setGravity(Gravity.CENTER);
        copyRightsElement.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Toast.makeText(AboutActivity.this, copyrights, Toast.LENGTH_SHORT).show();
            }
        });
        return copyRightsElement;
    }

    void simulateDayNight(int currentSetting) {
        final int DAY = 0;
        final int NIGHT = 1;
        final int FOLLOW_SYSTEM = 3;

        int currentNightMode = getResources().getConfiguration().uiMode
                & Configuration.UI_MODE_NIGHT_MASK;
        if (currentSetting == DAY && currentNightMode != Configuration.UI_MODE_NIGHT_NO) {
            AppCompatDelegate.setDefaultNightMode(
                    AppCompatDelegate.MODE_NIGHT_NO);
        } else if (currentSetting == NIGHT && currentNightMode != Configuration.UI_MODE_NIGHT_YES) {
            AppCompatDelegate.setDefaultNightMode(
                    AppCompatDelegate.MODE_NIGHT_YES);
        } else if (currentSetting == FOLLOW_SYSTEM) {
            AppCompatDelegate.setDefaultNightMode(
                    AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM);
        }
    }

//    public void initTitleBar() {
//        //View centerview=LayoutInflater.from(this).inflate(annotate_frame_centerview, null, false);
//        //titlebar.setCenterView(centerview);
//        View rightCustomLayout = titlebar.getRightCustomView();
//        TextView textView = titlebar.getCenterTextView();
//        textView.setText("关于信息");
//        titlebar.setListener(new CommonTitleBar.OnTitleBarListener() {
//            @Override
//            public void onClicked(View v, int action, String extra) {
//                if (action == CommonTitleBar.ACTION_LEFT_BUTTON) {
//                    Log.d(TAG, "onClicked: 左边ImageBtn被点击");
//                    Intent intent = new Intent();
//                    intent.putExtra("return_data", "annotateActivity");
//                    setResult(MyConstant.RESULT_CODE_ANNOTATE_BACK_FRAME, intent);
//                    finish();
//                }
//                // CommonTitleBar.ACTION_LEFT_TEXT;        // 左边TextView被点击
//                // CommonTitleBar.ACTION_LEFT_BUTTON;      // 左边ImageBtn被点击
//                // CommonTitleBar.ACTION_RIGHT_TEXT;       // 右边TextView被点击
//                // CommonTitleBar.ACTION_RIGHT_BUTTON;     // 右边ImageBtn被点击
//                // CommonTitleBar.ACTION_SEARCH;           // 搜索框被点击,搜索框不可输入的状态下会被触发
//                // CommonTitleBar.ACTION_SEARCH_SUBMIT;    // 搜索框输入状态下,键盘提交触发，此时，extra为输入内容
//                // CommonTitleBar.ACTION_SEARCH_VOICE;     // 语音按钮被点击
//                // CommonTitleBar.ACTION_SEARCH_DELETE;    // 搜索删除按钮被点击
//                // CommonTitleBar.ACTION_CENTER_TEXT;      // 中间文字点击
//            }
//        });
//    }

}
