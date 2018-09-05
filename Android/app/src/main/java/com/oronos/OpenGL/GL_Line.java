package com.oronos.OpenGL;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.ShortBuffer;

import javax.microedition.khronos.opengles.GL10;

// source: https://github.com/snowdream/opengl-es-tutorial-for-android

public class GL_Line {
    // Our vertices.
    private float mVertices[] = {
            0.0f,  0.0f, 0.0f,
            2.0f, 2.0f, 4.0f,
    };

    // The order we like to connect them.
    private short[] mIndices = { 0, 1};

    // Our vertex buffer.
    private FloatBuffer mVertexBuffer;

    // Our index buffer.
    private ShortBuffer mIndexBuffer;

    /*!
    ! A method that initialize the line
    */
    public GL_Line()
    {
        // a float is 4 bytes, therefore we multiply the number if vertices with 4.
        ByteBuffer vbb = ByteBuffer.allocateDirect(mVertices.length * 4);
        vbb.order(ByteOrder.nativeOrder());
        mVertexBuffer = vbb.asFloatBuffer();
        mVertexBuffer.put(mVertices);
        mVertexBuffer.position(0);

        // short is 2 bytes, therefore we multiply the number if vertices with 2.
        ByteBuffer ibb = ByteBuffer.allocateDirect(mIndices.length * 2);
        ibb.order(ByteOrder.nativeOrder());
        mIndexBuffer = ibb.asShortBuffer();
        mIndexBuffer.put(mIndices);
        mIndexBuffer.position(0);
    }

    /*!
    ! A method to set the end of the line which is the rocket position
    */
    public void setRocketPosition(float rocketPosition[]) {

        mIndexBuffer.clear();
        mVertexBuffer.clear();

        mVertices[3] = rocketPosition[0];
        mVertices[4] = rocketPosition[1];
        mVertices[5] = rocketPosition[2];

        // a float is 4 bytes, therefore we multiply the number if vertices with 4.
        ByteBuffer vbb = ByteBuffer.allocateDirect(mVertices.length * 4);
        vbb.order(ByteOrder.nativeOrder());
        mVertexBuffer = vbb.asFloatBuffer();
        mVertexBuffer.put(mVertices);
        mVertexBuffer.position(0);

        // short is 2 bytes, therefore we multiply the number if vertices with 2.
        ByteBuffer ibb = ByteBuffer.allocateDirect(mIndices.length * 2);
        ibb.order(ByteOrder.nativeOrder());
        mIndexBuffer = ibb.asShortBuffer();
        mIndexBuffer.put(mIndices);
        mIndexBuffer.position(0);
    }

    /*!
    ! A method to draws the line
    */
    public void draw(GL10 gl) {
        // Counter-clockwise winding.
        gl.glFrontFace(GL10.GL_CCW);
        // Enable face culling.
        gl.glEnable(GL10.GL_CULL_FACE);
        // What faces to remove with the face culling.
        gl.glCullFace(GL10.GL_BACK);

        // Enabled the vertices buffer for writing and to be used during rendering.
        gl.glEnableClientState(GL10.GL_VERTEX_ARRAY);
        // Specifies the location and data format of an array of vertex
        // coordinates to use when rendering.
        gl.glVertexPointer(3, GL10.GL_FLOAT, 0, mVertexBuffer);

        gl.glLineWidth(10.5f);

        gl.glDrawElements(GL10.GL_LINES, mIndices.length, GL10.GL_UNSIGNED_SHORT, mIndexBuffer);

        //gl.glDrawElements(GL10.GL_TRIANGLES, mIndices.length, GL10.GL_UNSIGNED_SHORT, mIndexBuffer);

        // Disable the vertices buffer.
        gl.glDisableClientState(GL10.GL_VERTEX_ARRAY);

        // Disable face culling.
        gl.glDisable(GL10.GL_CULL_FACE);
    }
}