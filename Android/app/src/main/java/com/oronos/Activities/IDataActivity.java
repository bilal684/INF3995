package com.oronos.Activities;
import android.util.Pair;
import android.widget.TextView;

import com.oronos.Fragments.FragmentFindMe;
import com.oronos.Fragments.GoogleMapFragment;
import com.oronos.Fragments.GraphPlot;
import com.oronos.Utilities.CustomPair;

import java.util.HashSet;
import java.util.List;
import java.util.Map;

/*
* Interface que l'activité DataActivity doit absolument implémenter.
* */
public interface IDataActivity {
    // see the implemented function's comments to understand the functionality
    void registerElementToMap(String key, TextView value, CustomPair<Integer, Integer> counters);
    void registerDataTypeTextView(TextView textView);
    void addEmptyTextViewModuleStatus(TextView textView);
    void registerPlot(List<CustomPair<String, CustomPair<Integer, Integer>>> cans, GraphPlot plot);
    Map<String, String> getConfiguration();
    Map<String, Pair<Float, Float>> getServerPositions();
    int incrementLogWidgetTextViewId();
    void registerMap(GoogleMapFragment map);
    void registerFindMe(FragmentFindMe findMe);
    void registerLogWidget(TextView tv);
    void registerLogWidgetCans(int id, HashSet<String> hss);
    Boolean getDarkMode();
}
