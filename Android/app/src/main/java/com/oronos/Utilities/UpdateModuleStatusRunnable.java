package com.oronos.Utilities;


import android.graphics.Color;
import android.os.Handler;
import android.widget.TextView;

/*
* Classe permettant de mettre à jour les modules status
* */
public class UpdateModuleStatusRunnable implements Runnable {


    private TextView textView;
    private String moduleString;
    private Handler mHandler;
    long before;

    /*
    * Constructeur par paramètre.
    * */
    public UpdateModuleStatusRunnable(TextView textView, String moduleString, Handler mHandler)
    {
        this.textView = textView;
        this.moduleString = moduleString;
        this.mHandler = mHandler;
        before = System.currentTimeMillis();
    }

    /*
    * Méthode permettant d'initier le compteur de temps.
    * */
    public void initCounter(long before)
    {
        this.before = before;
    }

    /*
    * Getter sur le gestionnaire.
    * */
    public Handler getHandler()
    {
        return mHandler;
    }

    /*
    * Méthode run permettant de mettre à jour les module status en fonction du temps de réception
    * d'une donnée d'un module en particulier.
    * */
    @Override
    public void run() {
        long after = System.currentTimeMillis();
        if(after - before > 4000)
        {
            textView.setText(moduleString + "\n OFFLINE");
            textView.setBackgroundColor(Color.rgb(255,0,0));
        }
        else if(after - before > 2000)
        {
            textView.setText(moduleString + "\n DELAY");
            textView.setBackgroundColor(Color.rgb(255,140,0));
        }
        else
        {
            textView.setText(moduleString + "\n ONLINE");
            textView.setBackgroundColor(Color.rgb(0,255,0));
        }
        mHandler.postDelayed(this, 250);
    }
}
