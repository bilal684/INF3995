package com.oronos.REST;

import android.os.AsyncTask;
import android.os.Build;
import android.support.annotation.RequiresApi;
import com.oronos.Utilities.CustomPair;

import java.io.BufferedInputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Map;

// source : https://stackoverflow.com/questions/45315408/parse-the-url-to-other-activity-to-load-pdf-from-that-url
//*******************************************************************
//  TaskGetPDFContent
//
//  Class used to get the select PDF content after a rest call
//*******************************************************************
public class TaskGetPDFContent extends AsyncTask<Map<String, String>,Void,CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>>> {

    public TaskGetPDFContent(String pdfFileName, RestTaskInterface mListener) {

        this.mListener = mListener;
        this.pdfFileName = pdfFileName;
    }

    private RestTaskInterface mListener;
    private String pdfFileName;

    @RequiresApi(api = Build.VERSION_CODES.KITKAT)
    @Override
    protected CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> doInBackground(Map<String, String>... params) {
        Boolean requestStatus = false;
        Map<String, String> restArguments = params[0];
        HttpURLConnection connection = null;
        InputStream inputStream = null;
        CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> response = null;

        try {
            // initiate connexion
            String uri = new String("http://"+ restArguments.get("ip") + "/config/miscFiles/" + pdfFileName + "?token=" + restArguments.get("token"));

            URL url = new URL(uri);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setReadTimeout(10000);
            connection.setConnectTimeout(15000);
            connection.connect();

            if (connection.getResponseCode() == 200)
            {
                inputStream = new BufferedInputStream(connection.getInputStream());
                requestStatus = true;
            }
        }
        catch (Exception e)
        {
            e.printStackTrace();
            response = new CustomPair<>(requestStatus, new CustomPair<>(connection, inputStream));
            return response;
        }
        response = new CustomPair<>(requestStatus, new CustomPair<>(connection, inputStream));
        return response;
    }

    @Override
    protected void onPostExecute(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> result)
    {
        if (mListener != null)
            mListener.callbackPDF(result);
    }
}