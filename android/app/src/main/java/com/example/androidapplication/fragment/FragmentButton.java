package com.example.androidapplication.fragment;

import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.example.androidapplication.FirstActivity;
import com.example.androidapplication.R;
import com.example.androidapplication.base.BaseLazyFragment;

import butterknife.BindView;
import mehdi.sakout.fancybuttons.FancyButton;
import butterknife.ButterKnife;

/**
 * Created by wjy on 2020/4/5
 **/
public class FragmentButton extends BaseLazyFragment {
    private static final String TAG = "FragmentButton";
    public View view=null;
    @BindView(R.id.opendir_button)
    FancyButton opendirButton;
    private Handler handler;

    public FragmentButton() {
    }

    public static FragmentButton newInstance() {
        FragmentButton fragment = new FragmentButton();
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        FirstActivity activity=(FirstActivity) getActivity();
        handler=activity.handler;
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        super.onCreateView(inflater, container, savedInstanceState);
        view = inflater.inflate(R.layout.fragment_openbuttton_layout, container, false);
        ButterKnife.bind(this, view);
        mIsprepared = true;
        lazyLoad();
        return view;
    }

    @Override
    protected void lazyLoad() {
        if (!mIsprepared || !mIsVisible || mHasLoadedOnce) {
            return;
        }
        mHasLoadedOnce = true;
        //UI和业务逻辑
        opendirButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Log.d(TAG, "onClick: 打开视频按钮被按下");
                Message message=Message.obtain();
                message.what=10;
                message.arg1=0;
                handler.sendMessage(message);
            }
        });
        Log.d(TAG, "lazyLoad: 当前的fragment-FragmentButton");
    }
}
