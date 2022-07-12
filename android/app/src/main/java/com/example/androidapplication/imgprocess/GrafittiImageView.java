package com.example.androidapplication.imgprocess;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.util.Log;
import android.view.MotionEvent;

import androidx.appcompat.widget.AppCompatImageView;

import java.util.ArrayList;

/**
 * Created by wjy on 2020/4/13
 **/
public class GrafittiImageView extends AppCompatImageView {
    //画笔设置
    private Paint paint = new Paint();

    public boolean isDraw() {
        return isDraw;
    }

    public void setDraw(boolean draw) {
        isDraw = draw;
    }

    /*
     * 是否进行绘制
     */
    private boolean isDraw = true;

    public boolean isClear() {
        return isClear;
    }

    public void setClear(boolean clear) {
        isClear = clear;
    }

    /*
     * 是否进行清空
     */
    private boolean isClear = false;

    public int getColor() {
        return color;
    }

    public void setColor(int color) {
        this.color = color;
    }

    /*
     * 画笔颜色
     */
    private int color = Color.RED;

    public float getStrokeWidth() {
        return strokeWidth;
    }

    public void setStrokeWidth(float strokeWidth) {
        this.strokeWidth = strokeWidth;
    }

    /*
     * 笔尖大小
     */
    private float strokeWidth = 6.0f;

    public int getType() {
        return type;
    }

    public void setType(int type) {
        this.type = type;
    }

    //涂鸦类型
    private int type=1;

    //当前正在画的线-相对坐标
    //当前正在画的线-绝对坐标
    private Line currentClientLine = new Line();
    private Line currentGlobalLine = new Line();

    public void clearStroke(){
        currentClientLine=new Line();
        currentGlobalLine = new Line();
        invalidate();
    }

    private static final String TAG = "GrafittiImageView";
    //画过的所有线
    private ArrayList<Line> lines = new ArrayList<Line>();

    public GrafittiImageView(Context context) {
        super(context);
    }
    public GrafittiImageView(Context context, AttributeSet attrs) {
        super(context, attrs);
    }

    public GrafittiImageView(Context context, AttributeSet attrs, int defStyleAttr) {
        super(context, attrs, defStyleAttr);
    }

    @Override
    public boolean onTouchEvent(MotionEvent event) {
        //获取坐标
        //getX()/getY()：触摸的中间区域相对坐标，相对于事件的视图的左上角的坐标
        //getRawX()/getRawY()：获得的X/Y值是绝对坐标，是相对于屏幕的
        float clickX = event.getX();
        float clickY = event.getY();
        float globalX=event.getRawX();
        float globalY=event.getRawY();
        //ACTION_DOWN-手指的初次触摸
        //ACTION_MOVE-滑动
        //ACTION_UP-抬起
        if(event.getAction()==MotionEvent.ACTION_DOWN) //getAction()返回动作类型
        {
            Log.d(TAG, "onTouchEvent: 初次按下屏幕");
            //刷新屏幕
            currentClientLine=new Line();
            currentGlobalLine = new Line();
            invalidate();

            return true;
        }else if(event.getAction() == MotionEvent.ACTION_MOVE){
            ViewPoint pointClient = new ViewPoint();
            ViewPoint pointGlobal = new ViewPoint();
            pointClient.x = clickX;
            pointClient.y = clickY;
            pointGlobal.x=globalX;
            pointGlobal.y=globalY;
            Log.d(TAG, "move: 相对坐标 ("+clickX+","+clickY+")");
            Log.d(TAG, "move: 绝对坐标 ("+globalX+","+globalY+")");
            currentClientLine.points.add(pointClient);
            currentGlobalLine.points.add(pointGlobal);
            invalidate();
            return true;
        }else if(event.getAction() == MotionEvent.ACTION_UP){
            Log.d(TAG, "点的个数=="+currentGlobalLine.points.size());
            invalidate();
        }
        return super.onTouchEvent(event);
    }

    @Override
    protected void onDraw(Canvas canvas) {
        super.onDraw(canvas);
        paint.setStyle(Paint.Style.STROKE);
        paint.setAntiAlias(true);
        paint.setColor(color);
        paint.setStrokeWidth(strokeWidth);
        if(isDraw==true){
            drawLine(canvas,currentClientLine);
        }
    }

    private void drawLine(Canvas canvas, Line line){
        for(int i = 0; i < line.points.size()-1; i++){
            float x = line.points.get(i).x;
            float y = line.points.get(i).y;
            float nextX = line.points.get(i+1).x;
            float nextY = line.points.get(i+1).y;
            canvas.drawLine(x,y,nextX,nextY,paint);
        }

    }

    public Line getGlobalPoints(){
        return currentGlobalLine;
    }
    public Line getClientPoints(){
        return currentClientLine;
    }
}
