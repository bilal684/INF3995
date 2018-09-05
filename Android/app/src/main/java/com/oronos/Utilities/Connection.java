package com.oronos.Utilities;

import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;
import java.net.UnknownHostException;

import static android.content.ContentValues.TAG;

// source : https://stackoverflow.com/questions/25093546/android-os-networkonmainthreadexception-at-android-os-strictmodeandroidblockgua
// source : http://www.coderzheaven.com/2017/05/01/client-server-programming-in-android-send-message-to-the-client-and-back/
//*******************************************************************
//  Connection
//
//  Class used to handle a socket connection with the server
//*******************************************************************
public class Connection implements Runnable{

    private Socket socket;
    private Handler hDataDisplayer;
    private Handler hModuleStatus;
    private Handler hLogWidget;
    private String SERVER_IP;
    private int SERVER_PORT;
    private String token;

    /*!
    ! A Constructor
    */
    public Connection(String server_ip, int server_port, Handler dataDisplayer, Handler moduleStatus, Handler logWidget, String token)
    {
        SERVER_IP = server_ip;
        SERVER_PORT = server_port;
        this.hDataDisplayer = dataDisplayer;
        this.hModuleStatus = moduleStatus;
        this.hLogWidget = logWidget;
        this.token = token;
    }

    @Override
    public void run() {

       try {
            InetAddress serverAddr = InetAddress.getByName(SERVER_IP);
            socket = new Socket(serverAddr, SERVER_PORT);
            send(token);
            Log.i(TAG, "Connection established with server: " + SERVER_IP);
            while(socket !=null)
            {
                String[] tripleData;
                String received = receive();
                while(received != null && received.length() > 0 && received.matches("\\d+") && received.split(";").length - 1 != Integer.parseInt(received.split(";")[0]))
                {
                    send("NO");
                    received = receive();
                }
                send("ok");
                try{
                    if(received != null)
                    {
                        tripleData = received.split("@");
                        if(tripleData.length > 2)
                        {
                            Bundle bDataDisplayer = new Bundle();
                            bDataDisplayer.putString("data", tripleData[0]);
                            Message mDataDisplayer = new Message();
                            mDataDisplayer.setData(bDataDisplayer);
                            hDataDisplayer.sendMessage(mDataDisplayer);
                            Bundle bModuleStatus = new Bundle();
                            bModuleStatus.putString("data", tripleData[1]);
                            Message mModuleStatus = new Message();
                            mModuleStatus.setData(bModuleStatus);
                            hModuleStatus.sendMessage(mModuleStatus);
                            Bundle bLogWidget = new Bundle();
                            bLogWidget.putString("data", tripleData[2]);
                            Message mLogWidget = new Message();
                            mLogWidget.setData(bLogWidget);
                            hLogWidget.sendMessage(mLogWidget);
                        }
                    }
                } catch(NumberFormatException e)
                {
                    Log.e("Number Format Exception", e.getMessage());
                }
            }
        } catch (UnknownHostException e1) {
            e1.printStackTrace();
        } catch (IOException e1) {
           e1.printStackTrace();
        }
    }

    /*!
    ! A method called to send a message to the server
    */
    private void send(String message) {
        try {
            if (socket != null) {
                PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(socket.getOutputStream())), true);
                out.write(message);
                out.flush();
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /*!
    ! A method called to get reference to the socket used to communicate with the server
    */
    public Socket getSocket()
    {
        return socket;
    }

    /*!
    ! A method called to receive a message from the server
    */
    private String receive() throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        String ret = br.readLine();
        return ret;

    }
}