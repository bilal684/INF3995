package com.oronos.Adapters;

import android.support.v4.app.Fragment;
import android.support.v4.app.FragmentManager;
import android.support.v4.app.FragmentPagerAdapter;
import android.widget.LinearLayout;

import com.oronos.Fragments.Container;
import com.oronos.Fragments.EmptyFragment;
import com.oronos.Utilities.CustomPair;
import com.oronos.Utilities.Util;

import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import java.util.ArrayList;
import java.util.List;

/*
* Classe représentant un adapter pour les éléments de la view de type ViewPager. Cette classe permet
* la gestion des fragments à afficher lorsque l'utilisateur effectue un glissement horizontale avec ses
* doigts.
* */
public class CustomFragmentPagerAdapter extends FragmentPagerAdapter {

    private List<CustomPair<String, NodeList>> innerElements;
    private List<Fragment> frags;
    private Boolean darkMode;

    /*
    * Constructeur par paramètre.
    * */
    public CustomFragmentPagerAdapter(FragmentManager fragmentManager, List<CustomPair<String, NodeList>> innerElements, Boolean darkMode) {
        super(fragmentManager);
        frags = new ArrayList<>();
        this.innerElements = innerElements;
        this.darkMode = darkMode;
        constructInnerView();
    }

    /*
    * Méthode android permettant de retourner le titre de l'onglet.
    * */
    @Override
    public CharSequence getPageTitle(int position) {

        return innerElements.get(position).getKey();
    }

    /*
    * Méthode android permettant de retourner le fragments à afficher.
    * */
    @Override
    public Fragment getItem(int position) {
        return frags.get(position);
    }

    /*
    * Méthode android permettant de retourner le nombre de fragments dans le tabcontainer.
    * */
    @Override
    public int getCount() {
        return innerElements.size();
    }

    /*
    * Méthode permettant de construire la vue internet des tabcontainer. Elle crée un container lorsqu'elle
    * rencontre un tabcontainer dans le xml. Sinon, elle crée un empty fragment.
    * */
    public void constructInnerView()
    {
        for(CustomPair<String, NodeList> cp : innerElements)
        {
            for(int i = 0; i < cp.getValue().getLength(); i++)
            {
                if(cp.getValue().item(i).getNodeType() == Node.ELEMENT_NODE)
                {
                    if(cp.getValue().item(i).getNodeName().toLowerCase().equals("tabcontainer"))
                    {
                        if(Util.Utilities.checkIfTabContainerHasNonEmptyChilds(cp.getValue().item(i)))
                        {
                            Container container = new Container();
                            container.setDarkMode(darkMode);
                            container.setElements(cp.getValue().item(i).getChildNodes());
                            frags.add(container);
                        }
                    }
                    else if(cp.getValue().item(i).getNodeName().toLowerCase().equals("dualvwidget"))
                    {
                        EmptyFragment ef = new EmptyFragment();
                        ef.setInnerElements(cp.getValue().item(i).getChildNodes());
                        ef.setLayoutOrientation(LinearLayout.VERTICAL);
                        frags.add(ef);
                    }
                    else if(cp.getValue().item(i).getNodeName().toLowerCase().equals("dualhwidget"))
                    {
                        EmptyFragment ef = new EmptyFragment();
                        ef.setInnerElements(cp.getValue().item(i).getChildNodes());
                        ef.setLayoutOrientation(LinearLayout.HORIZONTAL);
                        frags.add(ef);
                    }
                    else
                    {
                        EmptyFragment ef = new EmptyFragment();
                        ef.setInnerElements(cp.getValue());
                        frags.add(ef);
                    }
                    break;
                }
            }
        }
    }
}
