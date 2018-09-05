package com.oronos.REST;

import android.os.AsyncTask;
import android.util.Log;
import android.util.Pair;


import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Map;

// source : https://stackoverflow.com/questions/34691175/how-to-send-httprequest-and-get-json-response-in-android

//*******************************************************************
//  TaskPostLogout
//
//  Class used to logout the user with a rest call
//*******************************************************************
public class TaskPostLogout extends AsyncTask<Map<String, String>,Void,Pair<Boolean, String>> {

    public TaskPostLogout(RestTaskInterface mListener)
    {
        this.mListener = mListener;
    }

    private RestTaskInterface mListener;

    @Override
    protected Pair<Boolean, String> doInBackground(Map<String, String>... params)
    {
        Boolean requestStatus = false;
        String line = "";

        Map<String, String> credentials = params[0];

        try {
            // initiate connexion
            String uri = new String("http://" + credentials.get("ip") + "/users/logout" + "?token=" + credentials.get("token"));

            URL serverAddress = new URL(uri);
            HttpURLConnection connection = (HttpURLConnection) serverAddress.openConnection();
            connection.setDoOutput(true);
            connection.setDoInput(true);
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestMethod("POST");
            connection.connect();

            // send POST
            OutputStream os = connection.getOutputStream();
            BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(os, "UTF-8"));

            JSONObject postDataParams = new JSONObject();
            postDataParams.put("username", credentials.get("username"));

            writer.write(postDataParams.toString());
            writer.flush();
            writer.close();
            os.close();

            int status = connection.getResponseCode();

            if (status != HttpURLConnection.HTTP_OK)
            {
                BufferedReader in = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
                line = in.readLine();
                in.close();
                Log.d("DEBUG",line);
            }
            else
            {
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
        } catch (JSONException e) {
            e.printStackTrace();
        } catch (Exception e) {
            e.printStackTrace();
        }
        Pair<Boolean, String>  response = new Pair<>(requestStatus, line);
        return response;
    }

    @Override
    protected void onPostExecute(Pair<Boolean, String> result)
    {
        if (mListener != null)
            mListener.callback(result);
    }
}
