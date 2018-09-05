package com.oronos.Fragments;

import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentTransaction;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.view.ViewTreeObserver;
import android.widget.GridView;
import android.widget.LinearLayout;
import android.widget.RelativeLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import com.oronos.Activities.IDataActivity;
import com.oronos.Adapters.CustomFragmentBaseAdapter;
import com.oronos.R;
import com.oronos.Utilities.CustomPair;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

/*
* Cette classe consiste en un conteneur pour au plus deux fragments
* */
public class EmptyFragment extends Fragment {

    private NodeList innerElements;
    private Integer layoutOrientation = null;
    private int layout_index = 0;
    /*
    * Constructeur par défaut
    * */
    public EmptyFragment() {
    }

    /*
    * Méthode android onCreate
    * */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    /*
    * Méthode android onCreateView
    * */
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_empty, container, false);
    }

    /*
    * Méthode android onViewCreated, elle popule les éléments de la vue lorsque cette dernière est créée
    * */
    @Override
    public void onViewCreated(View view, Bundle savedInstanceState)
    {
        populateElements();
    }

    /*
    * Setter sur l'attribut innerElements
    * */
    public void setInnerElements(NodeList innerElements)
    {
        this.innerElements = innerElements;
    }

    /*
    * Setter sur l'attribut layoutOrientation
    * */
    public void setLayoutOrientation(Integer layoutOrientation)
    {
        this.layoutOrientation = layoutOrientation;
    }

    /*
    * Méthode android onAttach
    * */
    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
    }

    /*
    * Méthode android onDetach
    * */
    @Override
    public void onDetach() {
        super.onDetach();
    }

    /*
    * Méthode permettant de créer la vue correspondant en fonction des éléments enfants (innerElements). C'est la méthode qui place tous les fragments
    * dans la vue.
    * */
    private void populateElements()
    {
        for(int i = 0; i < innerElements.getLength(); i++)
        {
            if(innerElements.item(i).getNodeType() == Node.ELEMENT_NODE)
            {
                LinearLayout ll = getView().findViewById(R.id.emptyFragmentContainer);
                if(layoutOrientation != null && ll.getOrientation() != layoutOrientation)
                {
                    ll.setOrientation(layoutOrientation);
                }
                else if(layoutOrientation == null)
                {
                    RelativeLayout rl0 = getView().findViewById(getResources().getIdentifier("emptyFragmentContainerRL"+ 0, "id", getActivity().getPackageName()));
                    RelativeLayout rl1 = getView().findViewById(getResources().getIdentifier("emptyFragmentContainerRL"+ 1, "id", getActivity().getPackageName()));
                    if(rl0 != null)
                    {
                        ((LinearLayout)rl0.getParent()).removeView(rl0);
                    }
                    if(rl1 != null)
                    {
                        ((LinearLayout)rl1.getParent()).removeView(rl1);
                    }

                }
                if(innerElements.item(i).getNodeName().toLowerCase().equals("datadisplayer"))
                {
                    Log.i("EF: ", "Found datadisplayer tag");
                    GridView grid = new GridView(getActivity());
                    if((layoutOrientation != null && layoutOrientation.equals(LinearLayout.VERTICAL)) || layoutOrientation == null)
                    {
                        grid.setNumColumns(4);
                    }
                    else
                    {
                        grid.setNumColumns(2);
                    }
                    grid.setPadding(10, 30, 10, 10);
                    grid.setLayoutParams(new GridView.LayoutParams(GridView.LayoutParams.MATCH_PARENT, GridView.LayoutParams.WRAP_CONTENT));
                    List<CustomPair<String, CustomPair<Integer, Integer>>> cans = getCans(innerElements.item(i).getChildNodes());
                    List<LinearLayout> dataDisplayerLayouts = createAndRegisterDataDisplayerTextViews(cans);
                    CustomFragmentBaseAdapter gridAdapter = new CustomFragmentBaseAdapter(getActivity(), null, dataDisplayerLayouts);
                    grid.setVerticalSpacing(15);
                    grid.setAdapter(gridAdapter);
                    if(layoutOrientation != null)
                    {
                        RelativeLayout rl = getView().findViewById(getResources().getIdentifier("emptyFragmentContainerRL"+ layout_index++, "id", getActivity().getPackageName()));
                        rl.addView(grid);
                    }
                    else
                    {
                        ll.addView(grid);
                    }
                }
                else if(innerElements.item(i).getNodeName().toLowerCase().equals("plot"))
                {
                    Log.i("EF: ", "Found plot tag");
                    GraphPlot plot = new GraphPlot();
                    int plotColorRender = ((IDataActivity)getActivity()).getDarkMode() ? Color.WHITE : Color.BLACK;
                    plot.setColorTheme(plotColorRender);
                    List<CustomPair<String, CustomPair<Integer, Integer>>> cans = getCans(innerElements.item(i).getChildNodes());
                    if(cans.size() > 6)
                    {
                        Log.e("EF: ", "XML format illegal, plot with more than 6 cans");
                    }
                    plot.initializeSeriesData(cans);
                    plot.setUnit(innerElements.item(i).getAttributes().getNamedItem("unit").getNodeValue());
                    plot.setAxis(innerElements.item(i).getAttributes().getNamedItem("axis").getNodeValue());
                    plot.setName(innerElements.item(i).getAttributes().getNamedItem("name").getNodeValue());
                    ((IDataActivity)getActivity()).registerPlot(cans, plot);
                    FragmentTransaction ft = getChildFragmentManager().beginTransaction();
                    if(layoutOrientation != null)
                    {
                        ft.add(getResources().getIdentifier("emptyFragmentContainerRL"+ layout_index++, "id", getActivity().getPackageName()), plot);
                    }
                    else
                    {
                        ft.add(R.id.emptyFragmentContainer, plot);
                    }
                    ft.commit();

                }
                else if(innerElements.item(i).getNodeName().toLowerCase().equals("map"))
                {
                    Log.i("EF: ", "Found map");
                    GoogleMapFragment map = new GoogleMapFragment();
                    map.initializeMap(((IDataActivity)getActivity()).getConfiguration().get("map"));
                    ((IDataActivity)getActivity()).registerMap(map);
                    FragmentTransaction ft = getChildFragmentManager().beginTransaction();
                    if(layoutOrientation != null)
                    {
                        ft.add(getResources().getIdentifier("emptyFragmentContainerRL"+ layout_index++, "id", getActivity().getPackageName()), map);
                    }
                    else
                    {
                        ft.add(R.id.emptyFragmentContainer, map);
                    }
                    ft.commit();
                }
                else if(innerElements.item(i).getNodeName().toLowerCase().equals("findme"))
                {
                    Log.i("EF: ", "Found findMe");
                    FragmentFindMe findMe = new FragmentFindMe();
                    findMe.setInitPos(((IDataActivity)getActivity()).getServerPositions().get(((IDataActivity)getActivity()).getConfiguration().get("map")));
                    ((IDataActivity)getActivity()).registerFindMe(findMe);
                    FragmentTransaction ft = getChildFragmentManager().beginTransaction();
                    if(layoutOrientation != null)
                    {
                        ft.add(getResources().getIdentifier("emptyFragmentContainerRL"+ layout_index++, "id", getActivity().getPackageName()), findMe);

                    }
                    else
                    {
                        ft.add(R.id.emptyFragmentContainer, findMe);
                    }
                    ft.commit();
                }
                else if(innerElements.item(i).getNodeName().toLowerCase().equals("modulestatus"))
                {
                    Log.i("EF: ", "Found moduleStatus");
                    GridView grid = new GridView(getActivity());
                    grid.setNumColumns(Integer.parseInt(innerElements.item(i).getAttributes().getNamedItem("nColumns").getNodeValue().toString()));
                    grid.setPadding(10, 30, 10, 10);
                    grid.setLayoutParams(new GridView.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.MATCH_PARENT));
                    grid.setHorizontalSpacing(40);
                    grid.setVerticalSpacing(40);
                    CustomFragmentBaseAdapter gridAdapter = new CustomFragmentBaseAdapter(getActivity(), Integer.parseInt(innerElements.item(i).getAttributes().getNamedItem("nGrid").getNodeValue().toString()), null);
                    grid.setAdapter(gridAdapter);
                    if(layoutOrientation != null)
                    {
                        RelativeLayout parentLayout = getView().findViewById(getResources().getIdentifier("emptyFragmentContainerRL"+ layout_index++, "id", getActivity().getPackageName()));
                        parentLayout.addView(grid);
                    }
                    else
                    {
                        ll.addView(grid);
                    }

                }
                else if(innerElements.item(i).getNodeName().toLowerCase().equals("displaylogwidget"))
                {
                    Log.i("EF: ", "Found displaylogwidget");
                    final ScrollView sv = new ScrollView(getActivity());
                    LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.MATCH_PARENT);
                    sv.setLayoutParams(params);
                    sv.setVerticalScrollBarEnabled(false);
                    sv.setHorizontalScrollBarEnabled(false);
                    sv.getViewTreeObserver().addOnGlobalLayoutListener(new ViewTreeObserver.OnGlobalLayoutListener() {
                        @Override
                        public void onGlobalLayout() {
                            sv.post(new Runnable() {
                                public void run() {
                                    sv.fullScroll(View.FOCUS_DOWN);
                                }
                            });
                        }
                    });
                    TextView tv = new TextView(getActivity());
                    int textViewColorRender = ((IDataActivity)getActivity()).getDarkMode() ? Color.WHITE : Color.BLACK;
                    tv.setTextColor(textViewColorRender);
                    tv.setId(((IDataActivity)getActivity()).incrementLogWidgetTextViewId());
                    ((IDataActivity)getActivity()).registerLogWidget(tv);
                    HashSet<String> hss = new HashSet<>();
                    List<CustomPair<String, CustomPair<Integer, Integer>>> cans = getCans(innerElements.item(i).getChildNodes());
                    for(CustomPair<String, CustomPair<Integer, Integer>> p : cans)
                    {
                        hss.add(p.getKey());
                    }
                    if(hss.size() > 0)
                    {
                        ((IDataActivity)getActivity()).registerLogWidgetCans(tv.getId(), hss);
                    }
                    sv.addView(tv);
                    if(layoutOrientation != null)
                    {
                        RelativeLayout rl = getView().findViewById(getResources().getIdentifier("emptyFragmentContainerRL"+ layout_index++, "id", getActivity().getPackageName()));
                        rl.addView(sv);
                    }
                    else
                    {
                        ll.addView(sv);
                    }
                }
            }
        }
    }

    /*
    * Methode permettant de créer les texts views pour les datadisplayer et les enregistrers dans une hashmap au niveau de
    * l'activité dataActivity. L'enregistrement est nécessaire pour les mises à jours futures.
    * */
    private List<LinearLayout> createAndRegisterDataDisplayerTextViews(List<CustomPair<String, CustomPair<Integer, Integer>>> cans)
    {
        List<LinearLayout> dataDisplayerLayouts = new ArrayList<>();
        for(CustomPair<String, CustomPair<Integer, Integer>> can : cans)
        {
            TextView dataDisplayerName = new TextView(getActivity());
            TextView dataDisplayerValue = new TextView(getActivity());

            LinearLayout.LayoutParams params1 = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            params1.setMargins(10,0,0,0);
            params1.weight = 0.0f;

            LinearLayout.LayoutParams params2 = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, LinearLayout.LayoutParams.WRAP_CONTENT);
            params2.setMargins(10,0,0,0);
            params2.weight = 1.0f;

            dataDisplayerName.setText(can.getKey().split("ج")[0]);
            dataDisplayerName.setLayoutParams(params1);
            int textViewColor = ((IDataActivity)getActivity()).getDarkMode() ? Color.WHITE : Color.BLACK ;
            dataDisplayerName.setTextColor(textViewColor);
            dataDisplayerValue.setLayoutParams(params2);

            dataDisplayerName.setMaxLines(1);
            dataDisplayerValue.setMaxLines(1);
            dataDisplayerValue.setTextColor(Color.rgb(0,0,0));
            ((IDataActivity)getActivity()).registerDataTypeTextView(dataDisplayerName);
            ((IDataActivity)getActivity()).registerElementToMap(can.getKey(), dataDisplayerValue, can.getValue());
            LinearLayout layout = new LinearLayout(getActivity());
            layout.setLayoutParams(new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.MATCH_PARENT));
            layout.addView(dataDisplayerName);
            layout.addView(dataDisplayerValue);
            dataDisplayerLayouts.add(layout);
        }
        return dataDisplayerLayouts;
    }

    /*
    * Méthode permettant de chercher les noeuds de type CANS dans les enfants
    * */
    private List<CustomPair<String, CustomPair<Integer, Integer>>> getCans(NodeList elements)
    {
        List<CustomPair<String, CustomPair<Integer, Integer>>> cans = new ArrayList<>();
        for(int i = 0; i < elements.getLength(); i++)
        {
            if(elements.item(i).getNodeType() == Node.ELEMENT_NODE)
            {
                if(elements.item(i).getNodeName().toLowerCase().equals("can"))
                {
                    CustomPair<String, CustomPair<Integer, Integer>> thePair;
                    if(!((Element)elements.item(i)).getAttribute("name").isEmpty())
                    {
                        Log.i("EF: ", "Found can " + ((Element)elements.item(i)).getAttribute("name"));

                        if(!((Element)elements.item(i)).getAttribute("updateEach").isEmpty())
                        {
                            try
                            {
                                thePair = new CustomPair<>(((Element) elements.item(i)).getAttribute("name") + "ج" + ((Element) elements.item(i)).getAttribute("id"), new CustomPair<>(Integer.parseInt(((Element) elements.item(i)).getAttribute("updateEach")), Integer.parseInt(((Element) elements.item(i)).getAttribute("updateEach"))));
                            }
                            catch(NumberFormatException e)
                            {
                                thePair = new CustomPair<>(((Element)elements.item(i)).getAttribute("name") + "ج" + ((Element)elements.item(i)).getAttribute("id"), null);
                            }
                        }
                        else
                        {
                            thePair = new CustomPair<>(((Element)elements.item(i)).getAttribute("name") + "ج" + ((Element)elements.item(i)).getAttribute("id"), null);
                        }
                        cans.add(thePair);
                    }
                    else if(!(elements.item(i)).getParentNode().getNodeName().toLowerCase().equals("datadisplayer"))
                    {
                        Log.w("EF: ", "Found can with empty name");
                        if(!((Element)elements.item(i)).getAttribute("updateEach").isEmpty())
                        {
                            try
                            {
                                thePair = new CustomPair<>(((Element)elements.item(i)).getAttribute("id"), new CustomPair<>(Integer.parseInt(((Element)elements.item(i)).getAttribute("updateEach")), Integer.parseInt(((Element)elements.item(i)).getAttribute("updateEach"))));
                            }
                            catch(NumberFormatException e)
                            {
                                thePair = new CustomPair<>(((Element)elements.item(i)).getAttribute("id"), null);
                            }
                        }
                        else
                        {
                            thePair = new CustomPair<>(((Element)elements.item(i)).getAttribute("id"), null);
                        }
                        cans.add(thePair);
                    }
                }
            }
        }
        return cans;
    }
}
