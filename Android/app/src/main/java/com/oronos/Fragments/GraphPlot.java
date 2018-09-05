package com.oronos.Fragments;

import android.graphics.Color;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;

import com.jjoe64.graphview.LegendRenderer;
import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.series.DataPoint;
import com.jjoe64.graphview.series.LineGraphSeries;
import com.oronos.Utilities.CustomPair;
import com.oronos.R;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;

//*******************************************************************
//  GraphPlot
//
//  this is a fragment that display a graph that can be scale by the user
//  it also auto scale depending on the number of data
//*******************************************************************
public class GraphPlot extends Fragment implements ICustomFragments {
    private View rootView  = null;
    private volatile GraphView graph = null;
    private volatile Integer graphWidth = 5;
    private EditText graphViewEditText = null;
    private String tag;
    private int parentOrientation;
    private LinkedList<Integer> colorList = new LinkedList<Integer>(){{add(Color.GREEN); add(Color.BLUE); add(Color.CYAN); add(Color.MAGENTA); add(Color.RED); add(Color.YELLOW);}};
    private HashMap<String, LinkedList<Double>> seriesData = new HashMap<>();
    private HashMap<String, CustomPair<Integer, Integer>> seriesCounters = new HashMap<>();
    private HashMap<String, Integer> firstXValue = new HashMap<>();
    private HashMap<String, LineGraphSeries<DataPoint>> series = new HashMap<>();
    private List<CustomPair<String, CustomPair<Integer, Integer>>> cans = new ArrayList<>();
    private String unit;
    private String axis;
    private String name;
    private int themeColor;

    /*
    * creates the graph view. Initializes default parameters.
    * */
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        rootView = inflater.inflate(R.layout.fragment_graph_plot, container, false);

        graph = rootView.findViewById(R.id.graph);
        initGraph(graph);

        graphViewEditText = rootView.findViewById(R.id.graphWidthEditText);

        final Button button = rootView.findViewById(R.id.widthAdjust);
        button.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                try
                {
                    graphWidth = Integer.parseInt(graphViewEditText.getText().toString());
                    graph.getViewport().setMinX(0);
                    graph.removeAllSeries();
                    for(CustomPair<String, CustomPair<Integer, Integer>> can:cans)
                    {
                        series.get(can.getKey()).resetData(new DataPoint[]{});
                    }
                    initGraph(graph);
                    graphViewEditText.setText("");
                    InputMethodManager inputManager = (InputMethodManager)
                            getActivity().getSystemService(getActivity().INPUT_METHOD_SERVICE);

                    inputManager.hideSoftInputFromWindow(getActivity().getCurrentFocus().getWindowToken(),
                            InputMethodManager.HIDE_NOT_ALWAYS);
                }catch(NumberFormatException e)
                {
                    return;
                }

            }
        });

        return rootView;
    }

    /*
    * Setter for parent layout orientation.
    * */
    public void setParentLayoutOrientation(int orientation)
    {
        parentOrientation = orientation;
    }

    /*
    * Getter for parent layout orientation
    * */
    public int getParentLayoutOrientation()
    {
        return parentOrientation;
    }

    /*
    * Method that initializes the graph, sets the viewport, title, colors.
    * */
    public void initGraph(GraphView graph) {
        graph.getViewport().setXAxisBoundsManual(true);
        graph.getViewport().setMinX(0);
        graph.getViewport().setMaxX(graphWidth); //ici il faut setter maxWidth

        graph.getGridLabelRenderer().setLabelVerticalWidth(100);
        for(CustomPair<String, CustomPair<Integer, Integer>> can:cans)
        {
            graph.addSeries(series.get(can.getKey()));
            series.get(can.getKey()).setTitle(can.getKey());
        }
        graph.getLegendRenderer().setVisible(true);
        graph.getLegendRenderer().setBackgroundColor(Color.TRANSPARENT);
        graph.setTitle(name);
        graph.getLegendRenderer().setAlign(LegendRenderer.LegendAlign.MIDDLE);
        graph.getLegendRenderer().setAlign(LegendRenderer.LegendAlign.BOTTOM);

        graph.getGridLabelRenderer().setGridColor(themeColor);
        graph.getGridLabelRenderer().setHorizontalLabelsColor(themeColor);
        graph.getGridLabelRenderer().setVerticalLabelsColor(themeColor);
        graph.getGridLabelRenderer().setVerticalAxisTitleColor(themeColor);
        graph.getLegendRenderer().setTextColor(themeColor);
    }

    /*
    * Method that updates the graph. Called by the data activity upon reception of graph data from the server.
    * */
    public void updateGraph(String seriesID, String y, String x)
    {
        try {
            if(series.containsKey(seriesID))
            {
                if(firstXValue.get(seriesID).equals(0))
                {
                    if(seriesCounters.get(seriesID) != null)
                    {
                        if(seriesCounters.get(seriesID).getKey().equals(seriesCounters.get(seriesID).getValue()))
                        {
                            series.get(seriesID).appendData(new DataPoint(0, Double.parseDouble(y)), true, graphWidth*30);
                            firstXValue.put(seriesID, Integer.parseInt(x));
                            seriesCounters.get(seriesID).setValue(0);
                        }
                        else
                        {
                            seriesCounters.get(seriesID).setValue(seriesCounters.get(seriesID).getValue() + 1);
                        }
                    }
                    else
                    {
                        series.get(seriesID).appendData(new DataPoint(0, Double.parseDouble(y)), true, graphWidth*30);
                        firstXValue.put(seriesID, Integer.parseInt(x));
                    }
                }
                else
                {
                    if(seriesCounters.get(seriesID) != null)
                    {
                        if(seriesCounters.get(seriesID).getKey().equals(seriesCounters.get(seriesID).getValue()))
                        {
                            series.get(seriesID).appendData(new DataPoint((((float)((Integer.parseInt(x) - firstXValue.get(seriesID))))/1000.0f), Double.parseDouble(y)), true, graphWidth*20);
                            seriesCounters.get(seriesID).setValue(0);
                        }
                        else
                        {
                            seriesCounters.get(seriesID).setValue(seriesCounters.get(seriesID).getValue() + 1);
                        }
                    }
                    else
                    {
                        series.get(seriesID).appendData(new DataPoint((((float)((Integer.parseInt(x) - firstXValue.get(seriesID))))/1000.0f), Double.parseDouble(y)), true, graphWidth*20);
                    }

                }
            }
        }catch(IllegalArgumentException e)
        {
            Log.d("X value error", e.getMessage());
        }

    }

    /*
    * Method called by Android when application goes in pause state.
    * */
    @Override
    public void onPause() {
        super.onPause();
    }

    /*
    * Method that initializes the data series in the graph.
    * */
    public void initializeSeriesData(List<CustomPair<String, CustomPair<Integer, Integer>>> cans)
    {
        this.cans.addAll(cans);
        for(CustomPair<String, CustomPair<Integer, Integer>> can: cans)
        {
            if(can.getValue() != null)
            {
                seriesCounters.put(can.getKey(), can.getValue());
            }
            seriesData.put(can.getKey(), new LinkedList<>());
            firstXValue.put(can.getKey(), 0);
            LineGraphSeries<DataPoint> lineGraphSeries = new LineGraphSeries<>();
            lineGraphSeries.setDrawDataPoints(true);
            lineGraphSeries.setColor(colorList.removeFirst());
            series.put(can.getKey(), lineGraphSeries);
        }
    }

    /*
    * Setter on name attribute
    * */
    public void setName(String name)
    {
        this.name = name;
    }

    /*
    * Setter on unit attribute.
    * */
    public void setUnit(String unit)
    {
        this.unit = unit;
    }

    /*
    * setter on axis attribute.
    * */
    public void setAxis(String axis)
    {
        this.axis = axis;
    }

    /*
    * method called to refresh the graph upon theme change.
    * */
    public void refreshGraph()
    {
        graph.getViewport().setMinX(0);
        graph.removeAllSeries();
        for(CustomPair<String, CustomPair<Integer, Integer>> can:cans)
        {
            series.get(can.getKey()).resetData(new DataPoint[]{});
        }
        initGraph(graph);
        graphViewEditText.setText("");
    }

    /*
    * setter on themecolor attribute.
    * */
    public void setColorTheme(int colorTheme)
    {
        themeColor = colorTheme;
    }
}