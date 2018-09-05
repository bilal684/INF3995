package com.oronos.Fragments;

import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.support.design.widget.TabLayout;
import android.support.v4.app.Fragment;
import android.support.v4.view.ViewPager;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.oronos.Adapters.CustomFragmentPagerAdapter;
import com.oronos.R;
import com.oronos.Utilities.CustomPair;
import com.oronos.Utilities.Util;

import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import java.util.ArrayList;
import java.util.List;

/*
* Fragment container, représente les tablayout et les tabs du fichiers XML
* */
public class Container extends Fragment {

    NodeList elements;
    private Boolean darkMode;

    /*
     * Constructeur par défaut
     * */
    public Container() {
        // Required empty public constructor
    }

    /*
    * Methode android oncreate
    * */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    /*
    * Methode android oncreateview
    * */
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_container, container, false);
    }

    /*
    * Methode android onviewcreated
    * */
    @Override
    public void onViewCreated(View view, Bundle savedInstanceState) {
        populateTabs();
    }

    /*
    * Methode android onattach
    * */
    @Override
    public void onAttach(Context context) {
        super.onAttach(context);
    }

    /*
    * Methode android onDetach
    * */
    @Override
    public void onDetach() {
        super.onDetach();
    }

    /*
    * Setter sur l'attribut elements, soit les éléments de la vue enfant.
    * */
    public void setElements(NodeList elements)
    {
        this.elements = elements;
    }

    /*
    * Methode permettant de populer la vue des tabs.
    * */
    private void populateTabs()
    {
        TabLayout tbl = getView().findViewById(R.id.sliding_tabs);
        //tbl.setBackgroundColor(Color.rgb(0,150,136));
        ViewPager vp = getView().findViewById(R.id.viewpager);
        vp.setOffscreenPageLimit(Integer.MAX_VALUE);
        List<CustomPair<String, NodeList>> innerElements = new ArrayList<>();
        for(int i = 0; i < elements.getLength(); i++)
        {
            if(elements.item(i).getNodeType() == Node.ELEMENT_NODE)
            {
                if(elements.item(i).getNodeName().toLowerCase().equals("tab"))
                {
                    if(darkMode)
                    {
                        tbl.setTabTextColors(Color.rgb(150,150,150), Color.WHITE);
                    }
                    else
                    {
                        tbl.setTabTextColors(Color.GRAY, Color.BLACK);
                    }
                    if(elements.item(i).getAttributes().getNamedItem("name") != null && Util.Utilities.checkIfTabContainerHasNonEmptyChilds(elements.item(i)))
                    {
                        tbl.addTab(tbl.newTab().setText(elements.item(i).getAttributes().getNamedItem("name").getTextContent()));
                        innerElements.add(new CustomPair<>(elements.item(i).getAttributes().getNamedItem("name").getTextContent(), elements.item(i).getChildNodes()));
                    }
                }
            }
        }
        CustomFragmentPagerAdapter cfpa = new CustomFragmentPagerAdapter(getChildFragmentManager(), innerElements, darkMode);
        vp.setAdapter(cfpa);
        tbl.setupWithViewPager(vp);
    }


    /*
    * Setter sur l'attribue darkmode pour les thèmes
    * */
    public void setDarkMode(Boolean darkMode) {
        this.darkMode = darkMode;
    }
}
