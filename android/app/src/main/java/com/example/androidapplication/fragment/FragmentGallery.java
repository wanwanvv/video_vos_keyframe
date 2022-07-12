package com.example.androidapplication.fragment;

import android.content.Context;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.ActionMode;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.widget.Toolbar;
import androidx.recyclerview.widget.DefaultItemAnimator;
import androidx.recyclerview.widget.ItemTouchHelper;

import com.example.androidapplication.FirstActivity;
import com.example.androidapplication.R;
import com.example.androidapplication.adapter.GridJRAdapter;
import com.example.androidapplication.base.BaseLazyFragment;
import com.example.androidapplication.bean.BubblenetBean;
import com.example.androidapplication.http.Urls;
import com.example.androidapplication.recyclermodules.JRitem;
import com.marshalchen.ultimaterecyclerview.RecyclerItemClickListener;
import com.marshalchen.ultimaterecyclerview.UltimateRecyclerView;
import com.marshalchen.ultimaterecyclerview.grid.BasicGridLayoutManager;

import java.util.ArrayList;
import java.util.List;

import butterknife.BindView;
import butterknife.ButterKnife;

import static com.example.androidapplication.FirstActivity.bubblenetBean;
import static com.example.androidapplication.FirstActivity.pixHeight;
import static com.example.androidapplication.FirstActivity.pixWidth;

public class FragmentGallery extends BaseLazyFragment {
    private static final String TAG = "FragmentGallery";
    //private static final String TAG = "GLV";
    private static final String ARG_TITLE = "arg_title";
    protected GridJRAdapter mGridAdapter = null;
    @BindView(R.id.ultimate_recyclerview)
    UltimateRecyclerView ultimateRecyclerview;
    private BasicGridLayoutManager mGridLayoutManager;
    private int moreNum = 2, columns = 2;
    private ActionMode actionMode;
    private Toolbar mToolbar;
    boolean isDrag = true;
    private ItemTouchHelper mItemTouchHelper;
    Handler f;
    private Context mcontext;
    int load_position;//加载的position
    boolean disableLoadMore;//是否允许加载
    int maxLength; //最多加载的num
    int initLoadnum=2;
    public int scaleWidth;//图片宽度
    public int scaleHeight;//图片高度
    FirstActivity activity;
    private Handler handler;
    private String mTitle;
    private String tag;

    public FragmentGallery() {
    }

    private void initConstant(){
        load_position=0;//加载的position
        disableLoadMore=false;//是否允许加载
        maxLength=0; //最多加载的num
        initLoadnum=2;
    }

    public static FragmentGallery newInstance() {
        FragmentGallery fragment = new FragmentGallery();
        //Bundle bundle = new Bundle();
        //fragment.setArguments(bundle);
        return fragment;
    }


    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        initConstant();
        activity = (FirstActivity) getActivity();
        handler = activity.handler;
    }

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        super.onCreateView(inflater, container, savedInstanceState);
        View view = inflater.inflate(R.layout.recyclerview_layout, container, false);
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
        if(bubblenetBean==null||pixHeight==0||pixHeight==0){
            return;
        }
        mHasLoadedOnce = true;
        initConstant();
        //UI和业务逻辑
        dimension_columns(pixWidth,pixHeight,bubblenetBean.getWidth(),bubblenetBean.getHeight());
        mGridAdapter = new GridJRAdapter(getJRList(load_position, load_position+initLoadnum),getActivity(),scaleWidth,scaleHeight);
        tag=activity.bubblenetBean.getTag();
        mGridAdapter.setSpanColumns(columns);
        mGridLayoutManager = new BasicGridLayoutManager(getActivity(), columns, mGridAdapter);
        ultimateRecyclerview.setLayoutManager(mGridLayoutManager);
        ultimateRecyclerview.setHasFixedSize(true);
        ultimateRecyclerview.setSaveEnabled(true);
        ultimateRecyclerview.setClipToPadding(false);
        //mGridAdapter.setCustomLoadMoreView(LayoutInflater.from(getActivity()).inflate(R.layout.custom_bottom_progressbar, null));
//        ultimateRecyclerview.setNormalHeader(setupHeaderView());
        f = new Handler();
        ultimateRecyclerview.setOnLoadMoreListener(new UltimateRecyclerView.OnLoadMoreListener() {
            @Override
            public void loadMore(int itemsCount, final int maxLastVisiblePosition) {
                Log.d(TAG, "itemsCount :: " + itemsCount);
                f.postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        mGridAdapter.insert(getJRList(load_position, load_position+moreNum));
                        afterAdd();
                    }
                }, 2000);
            }
        });
        //ultimateRecyclerview.enableDefaultSwipeRefresh();
        ultimateRecyclerview.reenableLoadmore();
        //ultimateRecyclerview.disableLoadmore();
        ultimateRecyclerview.setLoadMoreView(R.layout.custom_bottom_progressbar);
        ultimateRecyclerview.setAdapter(mGridAdapter);
        ultimateRecyclerview.setItemAnimator(new DefaultItemAnimator());
        //harness_control();
        Log.e(TAG, "lazyLoad: 当前的fragment mTitle=:" + TAG);

        //点击事件
        mGridAdapter.setOnItemClickListener(new RecyclerItemClickListener.OnItemClickListener(){

            @Override
            public void onItemClick(View view, int position) {
                Log.d(TAG, "onItemClick: position="+position);
                int choose_index=activity.bubblenetBean.getIndexes().get(position);
                String choose_image=activity.bubblenetBean.getImages().get(position);
                Log.d(TAG, "onItemClick: choose_index-"+choose_index+" choose_image-"+choose_image);
                Message message = Message.obtain();
                message.what = 11;
                message.arg1 = 0;
                message.arg2 = position;
                message.obj=tag;
                handler.sendMessage(message);
            }
        });

    }

    private void dimension_columns(float pixWidth,float pixHeight,int picWith,int picHeight) {
        float picPixWidth=pixWidth / 2;
        float resize_scale= picWith / picPixWidth;
        float picPixHeight = picHeight /resize_scale;
        initLoadnum=(int)( pixHeight / picPixHeight)*2; //向下取整
        scaleHeight=Math.round(picPixHeight);
        scaleWidth= Math.round(picPixWidth);
    }

    private View setupHeaderView() {
        View custom_header = LayoutInflater.from(getActivity()).inflate(R.layout.header_love, null, false);
        return custom_header;
    }

/*    private View setupHeaderView() {
        View custom_header = LayoutInflater.from(this).inflate(R.layout.header_love, null, false);
        return custom_header;
    }*/

/*    private void harness_control() {
        findViewById(R.id.add).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mGridAdapter.insert(SampleDataboxset.genJRList(4));
            }
        });

        findViewById(R.id.del).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mGridAdapter.removeLast();
            }
        });

        findViewById(R.id.delall).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mGridAdapter.removeAll();
            }
        });
        findViewById(R.id.add_one).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                mGridAdapter.insertFirst(SampleDataboxset.genJRSingle());
            }
        });

        findViewById(R.id.refresh).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                listuv.reenableLoadmore();
            }
        });

    }*/

    protected void afterAdd() {
        if(disableLoadMore==true){
            ultimateRecyclerview.disableLoadmore();
        }
    }

    private List<JRitem> getJRList(int start, int end) {
        int startx=start;
        int endx=end;
        List<JRitem> team = new ArrayList<>();
        BubblenetBean bean=activity.bubblenetBean;
        List<Integer> indexes=bean.getIndexes();
        List<String> images=bean.getImages();
        String tag=bean.getTag();
        maxLength=indexes.size();
        if(maxLength==0){
            return team;
        }
        Log.d(TAG, "getJRList: maxLength=="+maxLength);
        if(endx>=maxLength||startx>=maxLength){
            endx=maxLength;
            disableLoadMore=true;
        }
        for (int i = startx; i < endx; i++) {
            String indexName = String.format("%05d", indexes.get(i));
            String imageName=images.get(i);
            String imageResourceUrl= Urls.imageResourceUrl+"/"+tag+"/"+imageName;
            //String iamgeName=imageId+".jpg";
            //int imageResourceId = ResourceUtil.getMixmapResourceIdByImagename(iamgeName);
            Log.d(TAG, "getJRList: iamgeName-" + imageName + " indexName-" + indexName);
            JRitem item = new JRitem(imageResourceUrl, indexName);
            team.add(item);
        }
        load_position=endx;
        return team;
    }

    public String getTitle() {
        return mTitle;
    }
}
