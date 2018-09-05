////BaseAdapter is the base class for concrete adapter implementations on Android.
/// It is abstract, it cannot be directly instantiated.
//// Source : https://github.com/codepath/android_guides/wiki/Using-a-BaseAdapter-with-ListView
package com.oronos.Adapters;

import android.content.Context;
import android.graphics.Typeface;
import android.os.Build;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.TextView;
import android.graphics.Color;
import android.widget.LinearLayout;
import com.oronos.Activities.IDataActivity;

import java.util.List;

/*
* Classe qui permet de créer une GridView
* */
public class CustomFragmentBaseAdapter extends BaseAdapter
{
    private IDataActivity mContext;
    private Integer nGrid;
    private List<LinearLayout> dataDisplayerLayouts;

    //! A constructor
    /*!
      Passe le contexte
    */
    public CustomFragmentBaseAdapter(Context c, Integer nGrid, List<LinearLayout> dataDisplayerLayouts)
    {
        mContext = (IDataActivity) c;
        this.nGrid = nGrid;
        this.dataDisplayerLayouts = dataDisplayerLayouts;
    }

    //! Récupère le
    /*!
      Create the pdf viewer
    */
    @Override
    public int getCount() {
        // TODO Auto-generated method stub
        return (dataDisplayerLayouts != null)? dataDisplayerLayouts.size():nGrid;
    }

    @Override
    public Object getItem(int position) {
        // TODO Auto-generated method stub
        return null;
    }

    //! Retourne l'élément contenu dans la cellule cible
    /*!
    */
    @Override
    public long getItemId(int position) {
        // TODO Auto-generated method stub
        return 0;
    }

    //! Retourne la vue
    /*!
      Ajoute à la vue courante un textview dans chaque cellule de la Gridview
    */
    @Override
    public View getView(int position, View view, ViewGroup parent)
    {
        if (view == null )
        {
            if(dataDisplayerLayouts != null)
            {
                view = dataDisplayerLayouts.get(position);
            }
            else
            {
                TextView textView1 = new TextView((Context) mContext);

                LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.MATCH_PARENT);
                params.setMargins(10,0,0,0);

                textView1.setText("N/A");
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.JELLY_BEAN_MR1) {
                    textView1.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
                }
                textView1.setTextSize(16);
                textView1.setTypeface(textView1.getTypeface(), Typeface.BOLD);
                textView1.setTextColor(Color.rgb(0,0,0));
                textView1.setLayoutParams(params);
                textView1.setHeight(200);
                textView1.setGravity(Gravity.CENTER);
                mContext.addEmptyTextViewModuleStatus(textView1);
                view = textView1;
            }

        }
        return view;
    }
}