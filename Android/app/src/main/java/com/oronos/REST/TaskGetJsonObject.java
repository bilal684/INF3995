package com.oronos.REST;

import android.os.AsyncTask;
import android.os.Build;
import android.support.annotation.RequiresApi;
import android.util.Log;
import android.util.Pair;


import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Map;

// source : https://stackoverflow.com/questions/34691175/how-to-send-httprequest-and-get-json-response-in-android
//*******************************************************************
//  TaskGetJsonObject
//
//  Class used to get a json object after a rest call
//*******************************************************************
public class TaskGetJsonObject extends AsyncTask<Map<String, String>,Void,Pair<Boolean, String>> {

    public TaskGetJsonObject(String requestType, RestTaskInterface mListener) {
        this.mListener = mListener;
        this.mRequestType = requestType;
    }

    private RestTaskInterface mListener;
    private String mRequestType;

    @RequiresApi(api = Build.VERSION_CODES.KITKAT)
    @Override
    protected Pair<Boolean, String> doInBackground(Map<String, String>... params) {
        Boolean requestStatus = false;
        String line = null;
        Map<String, String> restArguments = params[0];

        try {
            // initiate connexion
            String uri = new String("http://"+ restArguments.get("ip") + mRequestType +"?token=" + restArguments.get("token"));

            HttpURLConnection connection = null;
            URL url = new URL(uri);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setReadTimeout(10000);
            connection.setConnectTimeout(15000);
            connection.connect();

            int status = connection.getResponseCode();

            if (status != HttpURLConnection.HTTP_OK) {
                BufferedReader in = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
                line = in.readLine();
                in.close();
                Log.d("DEBUG", line);
            } else {
                requestStatus = true;
                BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                line = in.readLine();
                in.close();
            }
            connection.disconnect();

            } catch (MalformedURLException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (Exception e) {
                e.printStackTrace();
            }

        Pair<Boolean, String> response = new Pair<>(requestStatus, line);
        return response;
    }

    @Override
    protected void onPostExecute(Pair<Boolean, String> result) {
        if (mListener != null)
            mListener.callback(result);
    }
}
