package com.oronos.OpenGL;

import android.opengl.GLSurfaceView;
import android.opengl.GLU;

import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

// source : https://github.com/snowdream/opengl-es-tutorial-for-android

public class GL_OpenGLRenderer implements GLSurfaceView.Renderer {

    private GL_Cube mGLCube;
    private GL_Line mGLLine;
    private GL_Cone mGLCone;
    /*!
    ! A method to initialize the rendering view
    */
    public GL_OpenGLRenderer(GL_Cube GLCube, GL_Line GLLine, GL_Cone GLCone)
    {
        this.mGLCube = GLCube;
        this.mGLLine = GLLine;
        this.mGLCone = GLCone;

        mGLCone.setSegments(32);
        mGLCone.setHeight(2);
        mGLCone.setRadius(0.5);
    }

    /*!
    ! A method to set the setting of the rendering view
    */
    @Override
    public void onSurfaceCreated(GL10 gl, EGLConfig config) {
        gl.glClearColor(0.0f, 0.0f, 0.0f, 0.5f);

        gl.glClearDepthf(1.0f);
        gl.glEnable(GL10.GL_DEPTH_TEST);
        gl.glDepthFunc(GL10.GL_LEQUAL);

        gl.glHint(GL10.GL_PERSPECTIVE_CORRECTION_HINT, GL10.GL_NICEST);
    }

    /*!
    ! A method to refresh the rendering view
    */
    @Override
    public void onDrawFrame(GL10 gl) {
        gl.glClear(GL10.GL_COLOR_BUFFER_BIT | GL10.GL_DEPTH_BUFFER_BIT);
        gl.glLoadIdentity();

        gl.glTranslatef(0.0f, 0.0f, -10.0f);
        gl.glRotatef(90, 0.0f, 1.0f, 0.0f);

        mGLCube.draw(gl);

        mGLLine.draw(gl);

        gl.glColor4f(1.0f, 0.0f, 0.0f, 1.0f);
        mGLCone.draw(gl);
        gl.glColor4f(1.0f, 1.0f, 1.0f, 1.0f);

        gl.glLoadIdentity();
    }

    /*!
    ! A method to set the view settings
    */
    @Override
    public void onSurfaceChanged(GL10 gl, int width, int height) {
        gl.glViewport(0, 0, width, height);

        gl.glMatrixMode(GL10.GL_PROJECTION);
        gl.glLoadIdentity();

        GLU.gluPerspective(gl, 45.0f, (float)width / (float)height, 0.1f, 100.0f);

        //GLU.gluLookAt(gl, 10.0f, 10.0f, 20.0f, 0, 0,-1, 0, 1, 0);
        GLU.gluLookAt(gl, 0.0f, 0.0f, 10.0f, 0, 0,-1, 0, 1, 0);

        gl.glViewport(0, 0, width, height);

        gl.glMatrixMode(GL10.GL_MODELVIEW);
        gl.glLoadIdentity();
    }
}