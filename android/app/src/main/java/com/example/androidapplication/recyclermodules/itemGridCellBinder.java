package com.example.androidapplication.recyclermodules;

import android.graphics.Color;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;

import com.example.androidapplication.R;
import com.marshalchen.ultimaterecyclerview.UltimateRecyclerviewViewHolder;

/**
 * Created by wjy on 2020/4/8
 **/
public class itemGridCellBinder extends UltimateRecyclerviewViewHolder{
    private static final String TAG = "itemGridCellBinder";
    public static final int layout = R.layout.grid_item;
    public TextView textViewSample;
    public ImageView imageViewSample;
    public View item_view;

    public itemGridCellBinder(View itemView, boolean isItem) {
        super(itemView);
        if (isItem) {
            textViewSample = (TextView) itemView.findViewById(R.id.tv_title);
            imageViewSample = (ImageView) itemView.findViewById(R.id.iv_image);
            item_view = itemView.findViewById(R.id.planview);
        }
    }

    @Override
    public void onItemSelected() {
        itemView.setBackgroundColor(Color.LTGRAY);
        //Log.d(TAG, "onItemSelected: text-"+textViewSample.getText()+" image-"+imageViewSample.toString());
    }

    @Override
    public void onItemClear() {
        itemView.setBackgroundColor(0);
    }


}
