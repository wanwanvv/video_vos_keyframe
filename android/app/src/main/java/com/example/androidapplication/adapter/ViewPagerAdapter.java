package com.example.androidapplication.adapter;

import android.util.Log;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentStatePagerAdapter;

import com.example.androidapplication.fragment.FragmentGallery;
import com.example.androidapplication.fragment.FragmentOpendir;
import com.example.androidapplication.fragment.FragmentResult;

import java.util.ArrayList;
import java.util.List;

public class ViewPagerAdapter extends FragmentStatePagerAdapter {
    private static final String TAG = "ViewPagerAdapter";
    int page_count;
    private int action=0; //不需要增加或删除fragment
    private int updateId=0;//需要更新的第几个fragment
    private boolean flag=false;//false表示只更新一个fragment，true表示全部更新
    private List<Integer> itemID=new ArrayList<>();//用来返回getItemId的值

    public ViewPagerAdapter(@NonNull FragmentManager fm, int frame_count) {
        super(fm);
        page_count=frame_count;

    }

    @NonNull
    @Override
    public Fragment getItem(int position) {
        switch (position){
            case 0:
                FragmentOpendir fragment0=FragmentOpendir.newInstance();
                Log.d(TAG, "getItem: FragmentOpendir");
                return fragment0;
            case 1:
                FragmentGallery fragment1=FragmentGallery.newInstance();
                Log.d(TAG, "getItem: FragmentGallery");
                return fragment1;
            case 2:
                FragmentResult fragment2=FragmentResult.newInstance();
                Log.d(TAG, "getItem: FragmentResult");
                return fragment2;
            default:
                FragmentOpendir fragment=FragmentOpendir.newInstance();
                Log.d(TAG, "getItem: FragmentOpendir");
                return fragment;
        }
    }

    @Override
    public int getCount() {
        return page_count;
    }

    @NonNull
    @Override
    public Object instantiateItem(@NonNull ViewGroup container, int position) {
        Log.d(TAG, "instantiateItem: 当前位置position=" + position);
        return super.instantiateItem(container, position);
    }
//    如果FragmentManager能通过Tag找到Fragment的实例，那么就直接attch()上这个Fragment2、如果找不到，才会调 用getItem()去初始化这个Fragment基于这个实现
//    如果item的位置如果没有发生变化，则返回POSITION_UNCHANGED；如果item的位置已经不存在了，则回了POSITION_NONE。
    @Override
    public int getItemPosition(Object object) {
        return POSITION_NONE;
    }//当调用notifyDataSetChanged时,强行返回POSITION_NONE，从而让ViewPager重绘所有item



}
