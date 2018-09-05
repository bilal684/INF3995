package com.oronos.Activities;

import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import com.github.barteksc.pdfviewer.PDFView;
import com.oronos.R;

import java.io.InputStream;

//*******************************************************************
//  PDFActivity
//
//  we use this to ask the server to send us a pdf file
//*******************************************************************
public class PDFActivity extends AppCompatActivity {

    PDFView pdfView;
    //! A constructor
    /*!
      Create the pdf viewer
    */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_pdfviewer);

        pdfView = findViewById(R.id.pdfView);
        InputStream inputStream = DataActivity.getInStream();
        pdfView.fromStream(inputStream).load();
    }

    @Override
    public void onBackPressed()
    {
        super.onBackPressed();
        this.finish();
    }
}
