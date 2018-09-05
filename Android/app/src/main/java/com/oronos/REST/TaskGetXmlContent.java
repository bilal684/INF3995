package com.oronos.REST;

import android.os.AsyncTask;
import android.os.Build;
import android.support.annotation.RequiresApi;
import android.util.Pair;



import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Map;

// source : https://stackoverflow.com/questions/16752073/how-do-i-return-a-boolean-from-asynctask
// https://stackoverflow.com/questions/36833798/sending-json-object-via-http-post-method-in-android
//*******************************************************************
//  TaskGetXmlContent
//
//  Class used to get the select XML content after a rest call
//*******************************************************************
public class TaskGetXmlContent extends AsyncTask<Map<String, String>,Void,Pair<Boolean, String>> {

    public TaskGetXmlContent(String xmlFileName, RestTaskInterface mListener) {

        this.mListener = mListener;
        this.xmlFileName = xmlFileName;
    }

    private RestTaskInterface mListener;
    private String xmlFileName;

    @RequiresApi(api = Build.VERSION_CODES.KITKAT)
    @Override
    protected Pair<Boolean, String> doInBackground(Map<String, String>... params) {
        Boolean requestStatus = false;
        StringBuilder sb = null;
        Map<String, String> restArguments = params[0];

        try {
            // initiate connexion
            String uri = new String("http://"+ restArguments.get("ip") + "/config/rockets/" + xmlFileName + "?token=" + restArguments.get("token"));

            HttpURLConnection connection = null;
            URL url = new URL(uri);
            connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setReadTimeout(10000);
            connection.setConnectTimeout(15000);
            connection.connect();

            BufferedReader br = null;
            try {
                br = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                String line;
                sb = new StringBuilder();
                while ((line = br.readLine()) != null) {
                    sb.append(line).append("\n");
                }

            } catch (Exception e) {
                e.printStackTrace();
                return null;
            } finally {
                try {
                    if (br != null) br.close();
                    requestStatus = true;
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            connection.disconnect();

        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }

        Pair<Boolean, String> response = new Pair<>(requestStatus, sb.toString());
        return response;
    }

    @Override
    protected void onPostExecute(Pair<Boolean, String> result) {
        if (mListener != null)
            mListener.callback(result);
    }
}