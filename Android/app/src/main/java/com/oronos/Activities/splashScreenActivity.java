package com.oronos.Activities;

import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.animation.Animation;
import android.view.animation.AnimationUtils;
import android.widget.LinearLayout;

import com.oronos.R;

//*******************************************************************
//  splashScreenActivity
//
//  loading screen when you launch the apps. Display app logo
//*******************************************************************
public class splashScreenActivity extends AppCompatActivity {
    LinearLayout upperLayout,lowerLayout;
    Animation uptodown,downtoup;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_splash);

        upperLayout = (LinearLayout) findViewById(R.id.upperLayout);
        lowerLayout = (LinearLayout) findViewById(R.id.lowerLayout);

        uptodown = AnimationUtils.loadAnimation(this,R.anim.uptodown);
        downtoup = AnimationUtils.loadAnimation(this,R.anim.downtoup);

        upperLayout.setAnimation(uptodown);
        lowerLayout.setAnimation(downtoup);
        // source : https://www.youtube.com/watch?v=YPDfBwPrauI&list=FLLEBJlXXeRrb25SCESvVsKQ&index=6&t=0s
        Thread splashThread = new Thread()
        {
            @Override
            public void run()
            {
                try{
                    int waited = 0;
                    while (waited < 500)
                    {
                        sleep(100);
                        waited+=100;
                    }
                    Intent intent = new Intent(splashScreenActivity.this,MainActivity.class);
                    intent.setFlags(Intent.FLAG_ACTIVITY_NO_ANIMATION);
                    startActivity(intent);
                    splashScreenActivity.this.finish();
                } catch (InterruptedException e)
                {

                }
            }
        };
        splashThread.start();
    }
}
