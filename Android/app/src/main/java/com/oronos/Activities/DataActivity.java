package com.oronos.Activities;

import android.content.Context;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.support.design.widget.TabLayout;
import android.support.v4.app.FragmentTransaction;
import android.text.SpannableString;
import android.text.style.TextAppearanceSpan;
import android.util.Log;
import android.util.Pair;
import android.view.Menu;
import android.view.SubMenu;
import android.view.View;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.MenuItem;
import android.os.StrictMode;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.Toast;
import com.oronos.Fragments.Container;
import com.oronos.Fragments.FragmentFindMe;
import com.oronos.Fragments.GoogleMapFragment;
import com.oronos.Fragments.GraphPlot;
import com.oronos.R;
import com.oronos.REST.RestTaskInterface;
import com.oronos.REST.TaskGetJsonObject;
import com.oronos.REST.TaskGetPDFContent;
import com.oronos.REST.TaskGetXmlContent;
import com.oronos.REST.TaskPostLogout;
import com.oronos.Utilities.UpdateModuleStatusRunnable;
import com.oronos.Utilities.Connection;
import com.oronos.Utilities.CustomPair;
import org.json.JSONException;
import org.json.JSONObject;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import org.apache.commons.collections4.queue.CircularFifoQueue;

//*******************************************************************
//  DataActivity
//
//  Dispatch data as we receive them
//*******************************************************************
public class DataActivity extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener, IDataActivity {
    private boolean darkMode = true;
    private Connection clientThread;
    private Thread thread;

    // contains, ip, username, token, map, layout, port
    private Map<String, String> configuration = null;
    private Map<Integer, CircularFifoQueue<String>> logWidgetFifoQueues;

    private Handler hDataDisplayer;
    private Handler hModuleStatus;
    private Handler hLogWidget;
    private ViewGroup parentLayoutDataActivity = null;

    // constant values
    private String jsonFileName = "configuration.json";
    private HashMap<String, ArrayList<CustomPair<TextView, CustomPair<Integer, Integer>>>> registeredViewGroupElements;
    private LinkedList<TextView> emptyModuleStatusTextView;
    private LinkedList<TextView> dataTypeTextView;
    private int rejected = 0;
    private Map<String, UpdateModuleStatusRunnable> moduleStatusHandler;
    private Map<String, List<GraphPlot>> plots;
    private List<GoogleMapFragment> maps;
    private List<FragmentFindMe> findMes;
    private Map<Integer, HashSet<String>> logWidgetCans;
    private List<TextView> logViewWidgetTextView;
    private Map<Integer, Integer> logViewWidgetTextViewCounter;
    private Map<String, Pair<Float, Float>> serverPositions;
    private int logWidgetTextViewId = 4000;
    private static final int MAX_LOG_WIDGET_MESSAGES = 40;
    private static InputStream mInputStream = null;
    private static HttpURLConnection mHttpURLConnectionPDF = null;
    private NavigationView mNavigationView = null;
    private Toolbar toolbar = null;
    // Log TAG
    private static final String TAG = "DataActivity";

    //TODO :rm
    //Button button;

    //! A constructor.
    /*!
      Create the view and save it as an android Bundle object.
    */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        logWidgetFifoQueues = new HashMap<>();
        serverPositions = new HashMap<>();
        maps = new ArrayList<>();
        findMes = new ArrayList<>();
        logViewWidgetTextView = new ArrayList<>();
        logViewWidgetTextViewCounter = new HashMap<>();
        logWidgetCans = new HashMap<>();
        registeredViewGroupElements = new HashMap<>();
        emptyModuleStatusTextView = new LinkedList<>();
        dataTypeTextView = new LinkedList<>();
        moduleStatusHandler = new HashMap<>();
        plots = new HashMap<>();
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_data);
        toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        parentLayoutDataActivity = findViewById(R.id.parentLayoutDataActivity);
        // get and assign passed arguments from MainActivity
        final Bundle extra = getIntent().getExtras();
        configuration = new HashMap<String, String>();
        configuration.put("ip", extra.getString("ip"));
        configuration.put("username", extra.getString("username"));
        configuration.put("token", extra.getString("token"));
        serverPositions.put("Spaceport_America", new Pair<>(32.9401475f, -106.9193209f));
        serverPositions.put("Motel_6", new Pair<>(32.3417429f, -106.7628682f));
        serverPositions.put("Convention_Center", new Pair<>(32.2799304f, -106.746831f));
        serverPositions.put("St_Pie_de_Guire", new Pair<>(46.003547f, -72.7311097f));

        // draw actionBar button
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();

        // add the navigation view with listeners
        mNavigationView = (NavigationView) findViewById(R.id.nav_view);
        mNavigationView.setNavigationItemSelectedListener(this);

        // set the username in the navigation view
        View headerView = mNavigationView.getHeaderView(0);
        TextView navUsername = (TextView) headerView.findViewById(R.id.usernameHeaderNavigationView);
        navUsername.setText(configuration.get("username"));

        // assign the layout name, the port and the map to load
        // get the content of the layout and write it in memory
        onGetBasicConfig();
        onGetPDFNames();

        darkMode = extra.getBoolean("darkMode");
    }

    //! A constructor.
    /*!
      Create the view group from XML file.
    */
    private ViewGroup constructView(NodeList elements, ViewGroup parentElement)
    {
        for(int i = 0; i < elements.getLength(); i++)
        {
            if(elements.item(i).getNodeType() == Node.ELEMENT_NODE)
            {
                if(elements.item(i).getNodeName().toLowerCase().equals("tabcontainer") && elements.item(i).getParentNode().getNodeName().toLowerCase().equals("grid"))
                {
                    Container container = new Container();
                    container.setDarkMode(darkMode);
                    FragmentTransaction t = getSupportFragmentManager().beginTransaction();
                    container.setElements(elements.item(i).getChildNodes());
                    t.add(parentElement.getId(), container);
                    t.commit();
                }
                else
                {
                    constructView(elements.item(i).getChildNodes(), parentElement);
                }
            }
        }
        return parentElement;
    }

    //! A destructor.
    /*!
      this is call whenever the client disconnect or close apps.
    */
    @Override
    protected void onDestroy() {

        try {
            onDisconnect();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (ExecutionException e) {
            e.printStackTrace();
        }
        Log.d(TAG, "Application closed.");
        super.onDestroy();
    }

    //! A method that is call when you press the Android back Button.
    /*!
      handle the backButton press action of Android.
    */
    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    //! A method for the UI.
    /*!
      Handle navigation view item clicks here
    */
    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.Disconnect)
        {
            try {
                onDisconnect();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (JSONException e) {
                e.printStackTrace();
            } catch (InterruptedException e) {
                e.printStackTrace();
            } catch (ExecutionException e) {
                e.printStackTrace();
            }
            // go to the MainActivity
            Intent mainActivity = new Intent(DataActivity.this, MainActivity.class);
            mainActivity.putExtra("darkMode", darkMode);
            startActivity(mainActivity);
        }
        else if(id == R.id.Theme)
        {
            darkMode = !darkMode;
            toggleDarkMode();
            try {
                saveThemeInJSONFile();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
        else
        {
            onGePDFContent(item.toString());
        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    //! A method for file validation.
    /*!
      check if a file exist on the Android phone/tablet.
    */
    public boolean fileExists(Context context, String filename)
    {
        File file = context.getFileStreamPath(filename);
        if(file == null || !file.exists()) {
            return false;
        }
        return true;
    }

    //! A method for saving JSON config files.
    /*!
      write the Theme selected by the user into a JSON file and save it
    */
    void saveThemeInJSONFile() throws IOException, JSONException {
        JSONObject obj;
        if (fileExists(this, jsonFileName))
        {
            FileInputStream configJSON = openFileInput(jsonFileName);
            int size = configJSON.available();
            byte[] buffer = new byte[size];
            configJSON.read(buffer);
            configJSON.close();

            String readContentFromJson = new String(buffer, "UTF-8");
            obj = new JSONObject(readContentFromJson);
        }
        else
        {
            obj = new JSONObject();
        }
        obj.put("theme", darkMode);

        String objString = obj.toString();
        FileOutputStream configJSONOutput = openFileOutput(jsonFileName, Context.MODE_PRIVATE);
        configJSONOutput.write(objString.getBytes());
        configJSONOutput.close();
    }

    //! A method to change the app Theme.
    /*!
      this is use to toggle the app Theme from dark to bright
    */
    private void toggleTabLayoutDarkMode(ViewGroup viewElement)
    {
        for(int i = 0; i < viewElement.getChildCount(); i++)
        {
            if(viewElement instanceof TabLayout)
            {
                TabLayout tl = (TabLayout) viewElement;
                if(darkMode)
                {
                    tl.setTabTextColors(Color.rgb(150,150,150), Color.WHITE);
                }
                else
                {
                    tl.setTabTextColors(Color.GRAY, Color.BLACK);
                }
            }
            else
            {
                if(viewElement.getChildAt(i) instanceof ViewGroup)
                {
                    toggleTabLayoutDarkMode((ViewGroup)viewElement.getChildAt(i));
                }
            }
        }
    }

    //! A method to initialize a dark theme.
    /*!
      toggle the Theme to the dark one at launch.
    */
    @Override
    public void onResume()
    {
        super.onResume();
        toggleDarkMode();
    }

    //! A method to toggle to dark theme.
    /*!
      toggle the Theme to the dark.
    */
    private void toggleDarkMode()
    {
        int backgroundColor = darkMode ? Color.rgb(48,48,48) : Color.WHITE;
        int textColor = darkMode ? Color.WHITE : Color.BLACK;
        int textAppearance = darkMode ? R.style.WhiteTextAppearance : R.style.BlackTextAppearance ;

        findViewById(R.id.parentLayoutDataActivity).setBackgroundColor(backgroundColor);

        for (List<GraphPlot> gps : plots.values())
        {
            for(GraphPlot gp : gps)
            {
                gp.setColorTheme(textColor);
                gp.refreshGraph();
            }
        }
        for(TextView tv: dataTypeTextView)
        {
            tv.setTextColor(textColor);
        }
        for(TextView tv: logViewWidgetTextView)
        {
            tv.setTextColor(textColor);
        }

        for(int i =0; i<mNavigationView.getMenu().size(); i++)
        {
            MenuItem menuItem = mNavigationView.getMenu().getItem(i);
            SpannableString s = new SpannableString(menuItem.getTitle());
            s.setSpan(new TextAppearanceSpan(this, textAppearance), 0, s.length(), 0);
            menuItem.setTitle(s);
            mNavigationView.setNavigationItemSelectedListener(this);
        }

        mNavigationView.setBackgroundColor(backgroundColor);
        mNavigationView.setItemIconTintList(ColorStateList.valueOf(textColor));
        mNavigationView.setItemTextColor(ColorStateList.valueOf(textColor));
        toggleTabLayoutDarkMode(findViewById(R.id.parentLayoutDataActivity));

        toolbar.setTitleTextColor(textColor);
        toolbar.setBackgroundColor(backgroundColor);
        final Drawable immutableNavIcon = toolbar.getNavigationIcon();
        if (immutableNavIcon != null) {
            Drawable navIcon = immutableNavIcon.mutate();
            navIcon.setColorFilter(textColor, PorterDuff.Mode.SRC_ATOP);
            toolbar.setNavigationIcon(navIcon);
        }

        String theme = darkMode ? "Light theme" : "Dark theme";
        MenuItem menuItem = mNavigationView.getMenu().findItem(R.id.Theme);
        menuItem.setTitle(theme);
        mNavigationView.setNavigationItemSelectedListener(this);
    }

    //! A method to handle client disconnection.
    /*!
      Handle disconnection properly so that the state of the app is saved and can be resume. Doing REST call
    */
    private void onDisconnect() throws IOException, JSONException, InterruptedException, ExecutionException {
        if(clientThread != null && clientThread.getSocket() != null && !clientThread.getSocket().isClosed())
        {
            clientThread.getSocket().close();
        }

        TaskPostLogout POST_TASK_LOGOUT = new TaskPostLogout(new RestTaskInterface()
        {
            @Override
            public void callback(Pair<Boolean, String> result) {
                if (result.first == true) {
                    Toast.makeText(DataActivity.this, "Disconnection succeeded", Toast.LENGTH_SHORT).show();
                    Log.i(TAG, "User " + configuration.get("username") + " has logged out");
                } else {
                    Toast.makeText(DataActivity.this, "Disconnection failed", Toast.LENGTH_SHORT).show();
                    Log.i(TAG, "Disconnection failed for the user " + configuration.get("username"));
                }
            }

            @Override
            public void callbackPDF(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> response) {}
        });
        POST_TASK_LOGOUT.execute(configuration).get();
        emptyCachedJSONFile();
    }

    //! A method to fill view with default values.
    /*!
      toggle the Theme to the dark one at launch.
    */
    private void emptyCachedJSONFile() throws IOException, JSONException {
        FileInputStream inputConfigurationFile = openFileInput(jsonFileName);
        int size = inputConfigurationFile.available();
        byte[] buffer = new byte[size];
        inputConfigurationFile.read(buffer);
        inputConfigurationFile.close();
        String readContentFromJson = new String(buffer, "UTF-8");
        JSONObject obj = new JSONObject(readContentFromJson);
        obj.remove("token");
        obj.put("token", "");

        FileOutputStream outputConfigurationFile = openFileOutput(jsonFileName, Context.MODE_PRIVATE);
        String objString = obj.toString();
        outputConfigurationFile.write(objString.getBytes());
        outputConfigurationFile.close();
    }

    //! A method to get basic app config.
    /*!
      receive system config from server and set them.
    */
    private void onGetBasicConfig() {
        TaskGetJsonObject GET_TASK_BASIC_CONFIG = new TaskGetJsonObject("/config/basic", new RestTaskInterface()
        {
            @Override
            public void callback(Pair<Boolean, String> result)
            {
                if (result.first == true) {
                    Toast.makeText(DataActivity.this, "Get basic config succeeded", Toast.LENGTH_SHORT).show();
                    try {
                        JSONObject obj = new JSONObject(result.second);
                        configuration.put("port", obj.getString("otherPort"));
                        configuration.put("layout", obj.getString("layout"));
                        configuration.put("map", obj.getString("map"));
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }
                    Log.i(TAG, "Request basic config succeeded");
                    onGetXmlContentAndWrite(configuration.get("layout"));
                } else
                {
                    Toast.makeText(DataActivity.this, "Get basic config failed", Toast.LENGTH_SHORT).show();
                    Log.i(TAG, "Request basic config failed");
                }
            }

            @Override
            public void callbackPDF(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> response) {}
        });
        GET_TASK_BASIC_CONFIG.execute(configuration);
    }

    //! A method to get the XML file.
    /*!
      Required in specification but never used.
    */
    private void onGetXmlNames() {
        TaskGetJsonObject GET_TASK_XML_NAMES = new TaskGetJsonObject("/config/rockets", new RestTaskInterface() {
            @Override
            public void callback(Pair<Boolean, String> result) {

                ArrayList<String> filenames = new ArrayList<String>();

                if (result.first == true) {
                    Toast.makeText(DataActivity.this, "Get XML names succeeded", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(DataActivity.this, "Get XML names failed", Toast.LENGTH_SHORT).show();
                }

                try {
                    JSONObject obj = new JSONObject(result.second);

                    Iterator<?> keys = obj.keys();

                    while (keys.hasNext()) {
                        String key = (String) keys.next();
                        filenames.add((String) obj.get(key));
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }

            @Override
            public void callbackPDF(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> response) {}
        });
        GET_TASK_XML_NAMES.execute(configuration);
    }

    //! A method to get the map initial config.
    /*!
      Required in specification but never used.
    */
    private void onGetMapConfig() {
        TaskGetJsonObject GET_TASK_MAP_CONFIG = new TaskGetJsonObject("/config/map", new RestTaskInterface() {
            @Override
            public void callback(Pair<Boolean, String> result) {
                if (result.first == true) {
                    Toast.makeText(DataActivity.this, "Get map config succeeded", Toast.LENGTH_SHORT).show();
                } else{
                    Toast.makeText(DataActivity.this, "Get map config failed", Toast.LENGTH_SHORT).show();
                }
                try {
                    JSONObject obj = new JSONObject(result.second);
                    configuration.put("map", obj.getString("map"));
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }

            @Override
            public void callbackPDF(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> response) {}
        });
        GET_TASK_MAP_CONFIG.execute(configuration);
    }

    //! A method used to get an XML file with a rest call and write it on cache
    /*!
      This is the last step before starting the connection with the server using socket
    */
    private void onGetXmlContentAndWrite(String xmlFileName)
    {
        TaskGetXmlContent GET_TASK_XML_CONTENT = new TaskGetXmlContent(xmlFileName, new RestTaskInterface() {
            @Override
            public void callback(Pair<Boolean, String> result) {

                if (result.first == true) {
                    Toast.makeText(DataActivity.this, "Get XML content succeeded", Toast.LENGTH_SHORT).show();
                    try {
                        Log.i(TAG, "User "  + configuration.get("username") + " requested rocket data description file " + xmlFileName);
                        writeXMLFile("ui.xml", result.second);
                        Element xmlRoot = getXmlRoot("ui.xml");
                        if(xmlRoot.getAttributes().getNamedItem("name") != null && xmlRoot.getAttributes().getNamedItem("id") != null)
                        {
                            setTitle("Rocket : " + xmlRoot.getAttributes().getNamedItem("name").getNodeValue() + " id:" + xmlRoot.getAttributes().getNamedItem("id").getNodeValue());
                        }
                        parentLayoutDataActivity = constructView(xmlRoot.getChildNodes(), parentLayoutDataActivity);
                        // create thread to handle a socket connexion with the server
                        hDataDisplayer = getDataDisplayerHandler();
                        hModuleStatus = getModuleStatusHandler();
                        hLogWidget = getLogWidgetHandler();
                        clientThread = new Connection(configuration.get("ip"), Integer.parseInt(configuration.get("port")), hDataDisplayer, hModuleStatus, hLogWidget, configuration.get("token"));
                        thread = new Thread(clientThread);
                        if (android.os.Build.VERSION.SDK_INT > 9) {
                            StrictMode.ThreadPolicy policy = new StrictMode.ThreadPolicy.Builder().permitAll().build();
                            StrictMode.setThreadPolicy(policy);
                        }
                        thread.start();
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                } else {
                    Log.i(TAG, "Get XML content failed");
                    Toast.makeText(DataActivity.this, "Get XML content failed", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void callbackPDF(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> response) {}
        });
        GET_TASK_XML_CONTENT.execute(configuration);
    }

    //! A method used to get a PDF file with a rest call
    /*!
      Called to get the PDF content as a stream
    */
    private void onGePDFContent(String PDFFileName)
    {
        TaskGetPDFContent GET_TASK_XML_CONTENT = new TaskGetPDFContent(PDFFileName, new RestTaskInterface() {
            @Override
            public void callbackPDF(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> result) {

                if (result.getKey() == true) {
                    Toast.makeText(DataActivity.this, "Get PDF content succeeded", Toast.LENGTH_SHORT).show();
                    Log.i(TAG, "User "  + configuration.get("username") + " requested misc file " + PDFFileName);

                    mInputStream = result.getValue().getValue();
                    mHttpURLConnectionPDF = result.getValue().getKey();

                    Intent PDFActivity= new Intent(DataActivity.this,PDFActivity.class);
                    startActivity(PDFActivity);

                } else {
                    Log.i(TAG, "Get PDF content failed");
                    Toast.makeText(DataActivity.this, "PDF loading failed - server unreachable", Toast.LENGTH_SHORT).show();
                }
            }

            @Override
            public void callback(Pair<Boolean, String> response) {}
        });
        GET_TASK_XML_CONTENT.execute(configuration);
    }

    //! A method used to get the PDF file present in the server
    /*!
      Called to populate the hamburger menu
    */
    private void onGetPDFNames() {
        TaskGetJsonObject GET_TASK_XML_NAMES = new TaskGetJsonObject("/config/miscFiles", new RestTaskInterface() {
            @Override
            public void callback(Pair<Boolean, String> result) {

                if (result.first == true) {
                    Toast.makeText(DataActivity.this, "Get PDF names succeeded", Toast.LENGTH_SHORT).show();
                } else {
                    Toast.makeText(DataActivity.this, "Get PDF names failed", Toast.LENGTH_SHORT).show();
                }
                try {
                    JSONObject obj = new JSONObject(result.second);


                    Menu menu = mNavigationView.getMenu();
                    MenuItem pdfFilesItem = menu.findItem(R.id.pdfFile);
                    SubMenu pdfFilesItemSubMenu = pdfFilesItem.getSubMenu();

                    Iterator<?> keys = obj.keys();

                    while (keys.hasNext())
                    {
                        String key = (String) keys.next();
                        MenuItem pdfFile = pdfFilesItemSubMenu.add((String) obj.get(key));
                        pdfFile.setIcon(R.drawable.ic_menu_slideshow);
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
            @Override
            public void callbackPDF(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> response) {}
        });
        GET_TASK_XML_NAMES.execute(configuration);
    }

    //! A method used to get a stream
    /*!
      It is used to close the stream
    */
    public static InputStream getInStream() {
        return mInputStream;
    }

    public static HttpURLConnection getHttpURLConnectionPDF()
    {
        return mHttpURLConnectionPDF;
    }

    // source : https://github.com/melardev/TutsStorages
    private Element getXmlRoot(String filename)
    {
        org.w3c.dom.Document doc = null;
        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        DocumentBuilder db;
        Element root = null;
        try {
            db = dbf.newDocumentBuilder();
            FileInputStream fis = openFileInput("ui.xml");
            doc = db.parse(fis);
            root = doc.getDocumentElement();
        } catch (ParserConfigurationException e) {
            e.printStackTrace();
        } catch (SAXException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return root;
    }

    // source : https://github.com/melardev/TutsStorage
    // source : https://stackoverflow.com/questions/14376807/how-to-read-write-string-from-a-file-in-android
    //! A method used to write a string in a file located in the cache
    /*!
      Created an outputStream and redirect it to a file
    */
    void writeXMLFile(String fileName, String content) throws IOException {
        OutputStreamWriter outputStreamWriter = new OutputStreamWriter(this.openFileOutput("ui.xml", Context.MODE_PRIVATE));
        outputStreamWriter.write(content);
        outputStreamWriter.close();
        Log.i(TAG, "Requested rocket data description file written in cache as: " + fileName);
    }

    //! A method used to update every logWidget
    /*!
      Receive data from the server and iterate over all logWidgets to refresh their content
    */
    private Handler getLogWidgetHandler()
    {
        return new Handler()
        {
            @Override
            public void handleMessage(Message msg) {
                String receivedData = msg.getData().getString("data");

                for(TextView tv : logViewWidgetTextView)
                {
                    if(logWidgetCans.containsKey(tv.getId()))
                    {
                        if(logWidgetCans.get(tv.getId()).contains(receivedData.split(";")[6]))
                        {
                            logWidgetFifoQueues.get(tv.getId()).add(receivedData);
                            tv.setText(transformQueueToString(logWidgetFifoQueues.get(tv.getId())).toString());
                        }
                    }
                    else
                    {
                        logWidgetFifoQueues.get(tv.getId()).add(receivedData);
                        tv.setText(transformQueueToString(logWidgetFifoQueues.get(tv.getId())).toString());
                    }
                }

            }
        };
    }

    //! A method used to update every ModuleStatus
    /*!
      Receive data from the server and iterate over all ModuleStatus to refresh their content
    */
    private Handler getModuleStatusHandler()
    {
        return new Handler()
        {
            @Override
            public void handleMessage(Message msg) {
                String [] dataMessage = msg.getData().getString("data").split(";");
                if(dataMessage.length == 8)
                {
                    //Module Status
                    String key = dataMessage[1];

                    if(moduleStatusHandler.containsKey(key))
                    {
                        moduleStatusHandler.get(key).initCounter(System.currentTimeMillis());
                    }
                    else
                    {
                        if(emptyModuleStatusTextView.size() > 0)
                        {
                            TextView textView = emptyModuleStatusTextView.removeFirst();
                            textView.setText(dataMessage[1] + "\n ONLINE");
                            textView.setBackgroundColor(Color.rgb(0,255,0));
                            textView.setId(dataMessage[1].hashCode());
                            //registeredViewGroupElements.put(dataMessage[1], textView);
                            registerElementToMap(dataMessage[1], textView, null);
                            UpdateModuleStatusRunnable r = new UpdateModuleStatusRunnable(textView, dataMessage[1], new Handler());
                            moduleStatusHandler.put(dataMessage[1], r);
                            r.getHandler().post(r);
                        }
                    }
                    //Plots module
                    if(plots.containsKey(dataMessage[0]))
                    {
                        for(GraphPlot gp : plots.get(dataMessage[0]))
                        {
                            gp.updateGraph(dataMessage[0], dataMessage[5], dataMessage[7]);
                        }
                    }
                    if(dataMessage[0].contains("LATITUDE"))
                    {
                        for(FragmentFindMe fm : findMes)
                        {
                            fm.setLatitude(Float.parseFloat(dataMessage[5]));
                        }
                        for(GoogleMapFragment mapToUpdate : maps)
                        {
                            mapToUpdate.updateRocketLat(Double.parseDouble(dataMessage[5]));
                        }
                    }
                    else if(dataMessage[0].contains("LONGITUDE"))
                    {
                        for(FragmentFindMe fm : findMes)
                        {
                            fm.setLongitude(Float.parseFloat(dataMessage[5]));
                        }
                        for(GoogleMapFragment mapToUpdate : maps)
                        {
                            mapToUpdate.updateRocketLng(Double.parseDouble(dataMessage[5]));
                        }
                    }
                    else if(dataMessage[0].contains("ALT_MSL"))
                    {
                        for(FragmentFindMe fm : findMes)
                        {
                            fm.setAltitude(Float.parseFloat(dataMessage[5]));
                        }
                    }
                }
            }
        };
    }

    //! A method used to update every dataDisplayer
    /*!
      Receive data from the server and iterate over all dataDisplayers to refresh their content
    */
    private Handler getDataDisplayerHandler() {
        return new Handler() {
            @Override
            public void handleMessage(Message msg) {
                String[] dataDisplayer;
                String receivedData = msg.getData().getString("data");
                try
                {
                    //if (receivedData.length() > 0 && receivedData.split(";").length - 1 == Integer.parseInt(receivedData.split(";")[0]))
                    //{
                    //button.setText(receivedData);
                    dataDisplayer = receivedData.split(";");
                    if(dataDisplayer.length > 2 && Integer.parseInt(dataDisplayer[1]) > 0 && dataDisplayer.length - 2 == Integer.parseInt(dataDisplayer[1]) /*&& dataMessage.length == 8*/)
                    {
                        int textViewIndex = 0;
                        for(int i = 2; i < dataDisplayer.length; i+=4)
                        {
                            String key = dataDisplayer[i];
                            String data = dataDisplayer[i+1];
                            String color = dataDisplayer[i+2];
                            String toUpdate = dataDisplayer[i+3];
                            if(toUpdate.equals("no"))
                            {
                                textViewIndex++;
                                continue;
                            }
                            if(registeredViewGroupElements.containsKey(key))
                            {
                                if(registeredViewGroupElements.get(key) != null && textViewIndex < registeredViewGroupElements.get(key).size())
                                {
                                    CustomPair<TextView, CustomPair<Integer, Integer>>p = registeredViewGroupElements.get(key).get(textViewIndex++);
                                    if(p.getValue() != null)
                                    {
                                        if(p.getValue().getKey().equals(p.getValue().getValue()))
                                        {
                                            p.getKey().setText(data);
                                            if(color.toLowerCase().equals("red"))
                                            {
                                                p.getKey().setBackgroundColor(Color.rgb(255,0,0));
                                            }
                                            else
                                            {
                                                p.getKey().setBackgroundColor(Color.rgb(0,255,0));
                                            }
                                            p.getValue().setValue(0);
                                        }
                                        else
                                        {
                                            p.getValue().setValue(p.getValue().getValue() + 1);
                                        }
                                    }
                                    else
                                    {
                                        p.getKey().setText(data);
                                        if(color.toLowerCase().equals("red"))
                                        {
                                            p.getKey().setBackgroundColor(Color.rgb(255,0,0));
                                        }
                                        else
                                        {
                                            p.getKey().setBackgroundColor(Color.rgb(0,255,0));
                                        }
                                    }
                                }
                            }
                        }
                    }
                    //}
                }catch(NumberFormatException  e)
                {
                    rejected++;
                    Log.e(TAG, "Format error : " + receivedData + " - Rejected # " + String.valueOf(rejected));
                    return;
                }catch(ArrayIndexOutOfBoundsException e)
                {
                    rejected++;
                    Log.e(TAG, "Format error : " + receivedData + " - Rejected # " + String.valueOf(rejected));
                    return;
                }
            }
        };
    }

    //! A method used to get a reference to every map
    /*!
      Used to update the rocket position in the map
    */
    @Override
    public void registerElementToMap(String key, TextView tv, CustomPair<Integer, Integer> counters) {
        if(key.contains("ج") && key.split("ج").length > 1)
        {
            if( registeredViewGroupElements.containsKey(key.split("ج")[1]))
            {
                ArrayList<CustomPair<TextView, CustomPair<Integer, Integer>>> allTextViewsForKey = registeredViewGroupElements.get(key.split("ج")[1]);
                allTextViewsForKey.add(new CustomPair<>(tv, counters));
                registeredViewGroupElements.put(key.split("ج")[1], allTextViewsForKey);
            }
            else
            {
                ArrayList<CustomPair<TextView, CustomPair<Integer, Integer>>> allTextViews = new ArrayList<>();
                allTextViews.add(new CustomPair<>(tv, counters));
                registeredViewGroupElements.put(key.split("ج")[1], allTextViews);
            }
        }
        else
        {
            if(registeredViewGroupElements.containsKey(key))
            {
                ArrayList<CustomPair<TextView, CustomPair<Integer, Integer>>> allTextViewsForKey = registeredViewGroupElements.get(key);
                allTextViewsForKey.add(new CustomPair<>(tv, counters));
                registeredViewGroupElements.put(key, allTextViewsForKey);
            }
            else
            {
                ArrayList<CustomPair<TextView, CustomPair<Integer, Integer>>> allTextViews = new ArrayList<>();
                allTextViews.add(new CustomPair<>(tv, counters));
                registeredViewGroupElements.put(key, allTextViews);
            }
        }
    }

    //! A method used to get a reference to every TextView
    /*!
      Used to update the dataDisplayer's content
    */
    @Override
    public void registerDataTypeTextView(TextView textView)
    {
        dataTypeTextView.add(textView);
    }

    //! A method used to get a reference to every ModuleStatus
    /*!
      Used to update the ModuleStatus's content
    */
    @Override
    public void addEmptyTextViewModuleStatus(TextView textView) {
        emptyModuleStatusTextView.add(textView);
    }

    //! A method used to get a reference to every plot
    /*!
      Used to update the the plot values
    */
    @Override
    public void registerPlot(List<CustomPair<String, CustomPair<Integer, Integer>>> cans, GraphPlot plot) {
        for(CustomPair<String, CustomPair<Integer, Integer>> can:cans)
        {
            if(plots.containsKey(can.getKey()))
            {
                plots.get(can.getKey()).add(plot);
            }
            else
            {
                List<GraphPlot> listOfGraphPlots = new ArrayList<>();
                listOfGraphPlots.add(plot);
                plots.put(can.getKey(), listOfGraphPlots);
            }
        }
    }

    //! A method used to return the server configuration
    /*!
      Used to get the server position, the connection port used, the credentials
    */
    @Override
    public Map<String, String> getConfiguration() {
        return configuration;
    }

    //! A method used to return the server position
    /*!
      Used to initialise the server position on the map
    */
    @Override
    public Map<String, Pair<Float, Float>> getServerPositions() {
        return serverPositions;
    }

    //! A method used to increment the logWidgetTextView Id
    /*!
      Used to initialise to assign for each textView a unique ID
    */
    @Override
    public int incrementLogWidgetTextViewId() {
        return logWidgetTextViewId++;
    }

    //! A method used to get a reference to every map
    /*!
      Used to update the rocket position
    */
    @Override
    public void registerMap(GoogleMapFragment map) {
        maps.add(map);
    }

    //! A method used to get a reference to findMe fragment
    /*!
      Used to update the arrow giving the rocket position from the server position
    */
    @Override
    public void registerFindMe(FragmentFindMe findMe) {
        findMes.add(findMe);
    }

    //! A method used to get a reference to logWidget fragment
    /*!
      Used to update the logWidget fragment
    */
    @Override
    public void registerLogWidget(TextView tv) {
        logViewWidgetTextView.add(tv);
        logWidgetFifoQueues.put(tv.getId(), new CircularFifoQueue<>(MAX_LOG_WIDGET_MESSAGES));
    }

    //! A method used to get a reference to every textView forming the logWidget
    /*!
      Used to update the logWidget fragment
    */
    @Override
    public void registerLogWidgetCans(int id, HashSet<String> hss) {
        logWidgetCans.put(id, hss);
    }

    //! A method used to get the current theme
    /*!
      Used to toggle the theme
    */
    @Override
    public Boolean getDarkMode()
    {
        return darkMode;
    }

    //! A method used to transform a queue to string
    /*!
      Used to update the content of the dataLogWidget
    */
    private StringBuilder transformQueueToString(CircularFifoQueue<String> queue)
    {
        StringBuilder sb = new StringBuilder("");
        for(String s : queue)
        {
            sb.append(s + "\n");
        }
        return sb;
    }
}