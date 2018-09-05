package com.oronos.Fragments;

import android.content.Context;
import android.opengl.GLSurfaceView;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Pair;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.oronos.OpenGL.GL_Cone;
import com.oronos.OpenGL.GL_Cube;
import com.oronos.OpenGL.GL_Line;
import com.oronos.OpenGL.GL_OpenGLRenderer;

//*******************************************************************
//  FragmentFindMe
//
//  Fragment that draws an arrow to indicate the rocket position relative to the
//  tablet location
//*******************************************************************
public class FragmentFindMe extends Fragment implements ICustomFragments {

    private Context context_;

    private GL_Cube GLCube_ = new GL_Cube();
    private GL_Line GLLine_ = new GL_Line();
    private GL_Cone GLCone_ = new GL_Cone();
    private int parentOrientation = 0;

    private GL_OpenGLRenderer glRenderer;
    private float[] rocketPosition = {0.0f, 0.0f, 0.0f};

    private Pair<Float, Float> initPos;

    private static final int DEGREE_TO_METER_FACTOR = 111320;

    //! A default constructor
    /*!
    */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    //! A method to initialize the view.
    /*!
      initialize the findMe Fragment
    */
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        // Inflate the layout for this fragment

        GLCube_ = new GL_Cube();
        GLLine_ = new GL_Line();
        GLCone_ = new GL_Cone();

        GLSurfaceView view_ = new GLSurfaceView(context_);
        glRenderer = new GL_OpenGLRenderer(GLCube_, GLLine_, GLCone_);
        view_.setRenderer(glRenderer);

        return view_;
    }

    //! A method to set the context when the fragment is attached
    /*!
      set the context
    */
    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
        context_ = context;
    }

    @Override
    public void onDetach() {
        super.onDetach();
    }

    //! A method to update the rocket position
    /*!
      Set the latitude, longitude and altitude of the rocket position
    */
    public void updateRocketPosition()
    {
        double norm = Math.sqrt(Math.pow(rocketPosition[0], 2.0) + Math.pow(rocketPosition[1], 2.0) + Math.pow(rocketPosition[2], 2.0));

        float [] normalizedPosition = { 6*(rocketPosition[1] / (float) norm), 6*(rocketPosition[2]/ (float) norm), -6*(rocketPosition[0]/ (float) norm)};
        GLLine_.setRocketPosition(normalizedPosition);
        GLCone_.setRocketPosition(normalizedPosition);
    }

    //! A method to update the rocket position
    /*!
      Set the latitude
    */
    public void setLatitude(Float latitude) {
        if(initPos != null)
        {
            rocketPosition[0] = (latitude - initPos.first) * DEGREE_TO_METER_FACTOR;
            updateRocketPosition();
        }

    }
    //! A method to update the rocket position
    /*!
      Set the longitude
    */
    public void setLongitude(Float longitude) {
        if(initPos != null)
        {
            if (longitude * initPos.second < 0)
            {
                longitude = -1*longitude;
            }
            rocketPosition[1] = (longitude - initPos.second)* DEGREE_TO_METER_FACTOR;
            updateRocketPosition();
        }

    }

    //! A method to update the rocket position
    /*!
      Set the altitude of the rocket position
    */
    public void setAltitude(Float altitude) {
        rocketPosition[2] = altitude;
        updateRocketPosition();
    }

    public void setInitPos(Pair<Float, Float> initPos) {
        this.initPos = initPos;
    }

    //! A method to get the FindMe layout orientation
    /*!
      Set the latitude, longitude and altitude of the rocket position
    */
    @Override
    public int getParentLayoutOrientation() {
        return parentOrientation;
    }

    //! A method to set the FindMe layout orientation
    /*!
      Set the latitude, longitude and altitude of the rocket position
    */
    @Override
    public void setParentLayoutOrientation(int orientation) {
        parentOrientation = orientation;
    }
}