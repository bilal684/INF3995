package com.oronos.OpenGL;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;

import javax.microedition.khronos.opengles.GL10;

// source : https://github.com/hilsonshrestha/android-compass3d/tree/master/compass3d-test

public class GL_Cone {
    private double mHeight = 1;
    private double mRadius = 1;
    private int mSegments = 4;
    private FloatBuffer mVertexBuffer;
    private ByteBuffer mConeIndexBuffer;
    private FloatBuffer mNormalBuffer;
    private ByteBuffer mBaseIndexBuffer;
    private boolean mDrawBase;
    private float mRocketPosition[] = {0.0f,  0.0f,  0.0f};

    /*!
    ! A method that set the cone's height
    */
    public void setHeight(double height) {
        mHeight = height;
    }

    /*!
    ! A method that set the cone's radius
    */
    public void setRadius(double radius) {
        mRadius = radius;
        //mGeometryValid = false;
    }

    /*!
    ! A method that set the cone's segment
    */
    public void setSegments(int segments) {
        mSegments = segments;
        //mGeometryValid = false;
    }

    public void drawBase(boolean enable) {
        mDrawBase = enable;
    }

    /*!
    ! A method that calculate the cone's geometry
    */
    private void calculateGeometry() {
        //if (mGeometryValid) return;

        assert mSegments < 255;

        float[] verticies = new float[3 * (mSegments + 1)];
        byte[] coneIndicies = new byte[mSegments + 2];
        byte[] baseIndicies = new byte[mSegments];

        // Nose of the cone
        verticies[0] =  mRocketPosition[0] + mRocketPosition[0]/2;
        verticies[1] = mRocketPosition[1] + mRocketPosition[1]/2;
        verticies[2] =  mRocketPosition[2] + mRocketPosition[2]/2;

        coneIndicies[0] = 0;
        double perAngle = 2 * Math.PI / mSegments;
        for (int i = 0; i < mSegments; i++) {
            double angle = i * perAngle;
            int offset = 3 * i + 3;
            verticies[offset + 0] = mRocketPosition[0] + (float)(Math.cos(angle) * mRadius);
            verticies[offset + 1] = mRocketPosition[1] + (float)(Math.sin(angle) * mRadius) ;
            verticies[offset + 2] = mRocketPosition[2];
            coneIndicies[i + 1] = (byte)(i + 1);
            baseIndicies[i] = (byte)(i + 1);
        }
        coneIndicies[mSegments + 1] = 1;

        mVertexBuffer = asBuffer(verticies);
        mNormalBuffer = mVertexBuffer;  // turns out to be the same
        mConeIndexBuffer = asBuffer(coneIndicies);
        mBaseIndexBuffer = asBuffer(baseIndicies);
        //mGeometryValid = true;
    }

    /*!
     ! A method the draw the cone
    */
    public void draw(GL10 gl) {
        calculateGeometry();
        gl.glEnableClientState(GL10.GL_NORMAL_ARRAY);
        gl.glNormalPointer(GL10.GL_FLOAT, 0, mNormalBuffer);
        gl.glEnableClientState(GL10.GL_VERTEX_ARRAY);
        gl.glVertexPointer(3, GL10.GL_FLOAT, 0, mVertexBuffer);
        gl.glDrawElements(GL10.GL_TRIANGLE_FAN, mSegments + 2, GL10.GL_UNSIGNED_BYTE, mConeIndexBuffer);
        gl.glDisableClientState(GL10.GL_NORMAL_ARRAY);
        if (mDrawBase)
            gl.glDrawElements(GL10.GL_TRIANGLE_FAN, mSegments, GL10.GL_UNSIGNED_BYTE, mBaseIndexBuffer);
        gl.glDisableClientState(GL10.GL_VERTEX_ARRAY);
    }

    /*!
     ! A method to return a byteBuffer
    */
    static ByteBuffer asBuffer(byte[] bytes) {
        ByteBuffer buf = ByteBuffer.allocateDirect(bytes.length);
        buf.put(bytes);
        buf.position(0);
        return buf;
    }

    /*!
     ! A method to return a floatBuffer
    */
    static FloatBuffer asBuffer(float[] floats) {
        ByteBuffer buf = ByteBuffer.allocateDirect(floats.length
                * (Float.SIZE/Byte.SIZE));
        buf.order(ByteOrder.nativeOrder());
        FloatBuffer fbuf = buf.asFloatBuffer();
        fbuf.put(floats);
        fbuf.position(0);
        return fbuf;
    }

    /*!
     ! A method to update the rocket position
    */
    public void setRocketPosition(float[] rocketPosition) {
        // rocket position
        mRocketPosition = rocketPosition;
        calculateGeometry();
    }
}