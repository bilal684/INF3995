package com.oronos.REST;

import android.util.Pair;

import com.oronos.Utilities.CustomPair;

import java.io.InputStream;
import java.net.HttpURLConnection;

//*******************************************************************
//  RestTaskInterface
//
//  interface to the rest server
//*******************************************************************
// source : https://stackoverflow.com/questions/16752073/how-do-i-return-a-boolean-from-asynctask
public interface RestTaskInterface {
    void callback(Pair<Boolean, String> result);
    void callbackPDF(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> result);
}
