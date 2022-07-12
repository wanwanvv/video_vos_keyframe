package com.example.androidapplication.adapter;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;

import com.bumptech.glide.Glide;
import com.bumptech.glide.request.RequestOptions;
import com.example.androidapplication.recyclermodules.JRitem;
import com.example.androidapplication.recyclermodules.itemGridCellBinder;
import com.marshalchen.ultimaterecyclerview.RecyclerItemClickListener;
import com.marshalchen.ultimaterecyclerview.UltimateGridLayoutAdapter;
import com.marshalchen.ultimaterecyclerview.UltimateRecyclerviewViewHolder;

import java.util.List;

/**
 * Created by wjy on 2020/4/8
 **/
public class GridJRAdapter extends UltimateGridLayoutAdapter<JRitem, itemGridCellBinder> {
    public Context mcontext;
    public int picWidth;
    public int picHeight;
    private RecyclerItemClickListener.OnItemClickListener listener;
    private OnItemLongClickListener longClickListener;

    public GridJRAdapter(List<JRitem> hand,Context mcontext,int width,int height) {
        super(hand);
        this.mcontext=mcontext;
        picHeight=height;
        picWidth=width;
    }
    /**
     * the layout id for the normal data
     *
     * @return the ID
     */
    @Override
    protected int getNormalLayoutResId() {
        return itemGridCellBinder.layout;
    }

    /**
     * this is the Normal View Holder initiation
     *
     * @param view view
     * @return holder
     */
    @Override
    protected itemGridCellBinder newViewHolder(View view) {
        return new itemGridCellBinder(view, true);
    }

    @Override
    public long generateHeaderId(int position) {
        return 0;
    }

    /**
     * binding normal view holder
     *
     * @param holder   holder class
     * @param data     data
     * @param position position
     */
    @Override
    protected void withBindHolder(itemGridCellBinder holder, JRitem data, int position) {

    }

    @Override
    protected void bindNormal(itemGridCellBinder b, JRitem jRitem, int position) {
        b.textViewSample.setText(jRitem.train_name);
        //b.imageViewSample.setImageResource(jRitem.photo_id);
        //Glide.with(mcontext).load(jRitem.photo_name).into(b.imageViewSample);
        RequestOptions options = new RequestOptions()
                .override(picWidth, picHeight).fitCenter();
        Glide.with(mcontext).load(jRitem.photo_name).apply(options).into(b.imageViewSample);
        b.itemView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(listener!=null){
                    listener.onItemClick(v,position);
                }
            }
        });
    }

    @Override
    public UltimateRecyclerviewViewHolder onCreateHeaderViewHolder(ViewGroup parent) {
        return new UltimateRecyclerviewViewHolder(parent);
    }

    @Override
    public itemGridCellBinder newFooterHolder(View view) {
        return new itemGridCellBinder(view, false);
    }

    @Override
    public itemGridCellBinder newHeaderHolder(View view) {
        return new itemGridCellBinder(view, false);
    }

    @Override
    public long getItemId(int position) {
        return super.getItemId(position);
    }

    //定义点击接口
    //第一步 定义接口
    public interface OnItemClickListener {
        void onClick(int position);
    }

    //第二步， 写一个公共的方法
    public void setOnItemClickListener(RecyclerItemClickListener.OnItemClickListener listener) {
        this.listener = listener;
    }

    public interface OnItemLongClickListener {
        void onClick(int position);
    }

    public void setOnItemLongClickListener(OnItemLongClickListener longClickListener) {
        this.longClickListener = longClickListener;
    }

}
