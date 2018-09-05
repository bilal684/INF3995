package com.oronos.Activities;

import android.animation.Animator;
import android.animation.AnimatorListenerAdapter;
import android.annotation.TargetApi;
import android.content.Context;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.graphics.drawable.Drawable;
import android.media.MediaScannerConnection;
import android.os.Build;
import android.os.Bundle;
import android.support.v4.view.ViewCompat;
import android.text.Editable;
import android.text.InputFilter;
import android.text.Spanned;
import android.text.TextWatcher;
import android.util.Pair;
import android.view.View;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.util.Calendar;
import android.util.Log;
import com.oronos.R;
import com.oronos.REST.RestTaskInterface;
import com.oronos.REST.TaskPostLogin;
import com.oronos.Utilities.CustomPair;

//*******************************************************************
//  MainActivity
//
//  we use it at connexion, we use it to navigate between views
//*******************************************************************
public class MainActivity extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener {

    // Log settings
    private String logpath = "Log";
    private static final String TAG = "MainActivity";
    private static final String RUNNINGACTIVITY = "MainActivity:D DataActivity:D MohamethActivity:D";
    // login and credential view
    View mLoginFormView = null;
    View mProgressView = null;
    private EditText[] IpAdresseInput;
    private EditText username = null;
    private EditText password = null;
    private TextWatcher mTextWatcher = null;
    private Button connexionButton = null;
    private NavigationView navigationView = null;
    private Toolbar toolbar = null;

    // credentials and IP address used for authentication (REST calls)
    private String usernameString = null;
    private String token = null;
    private String ipString = null;
    private Boolean darkMode = true;
    private Bundle extra = null;

    // constant values
    private String jsonFileName = "configuration.json";

    @Override
    public void onSaveInstanceState(Bundle savedInstanceState) {
        super.onSaveInstanceState(savedInstanceState);
        // Save UI state changes to the savedInstanceState.
        // This bundle will be passed to onCreate if the process is
        // killed and restarted.
        savedInstanceState.putBoolean("darkMode", darkMode);
    }

    //! A constructor.
    /*!
      Create the view and save it as an android Bundle object.
    */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        extra = getIntent().getExtras();
        if (extra != null)
        {
            darkMode = extra.getBoolean("darkMode", true);
        }

        if (savedInstanceState != null)
        {
            darkMode = savedInstanceState.getBoolean("darkMode");
        }

        setContentView(R.layout.activity_main);
        // create log directory and file
        File logDirectory = new File(getExternalFilesDir(logpath),Calendar.getInstance().getTime() + ".txt");
        // refresh data to be visible by laptop
        MediaScannerConnection.scanFile(this, new String[] {logDirectory.getPath()}, null, null);
        // clear the previous logcat and then write the new one to the file
        try {
            Process process = Runtime.getRuntime().exec( "logcat -c");
            process = Runtime.getRuntime().exec(new String[]{"logcat", "-f", logDirectory.getPath(), RUNNINGACTIVITY, "*:S"});
        } catch ( IOException e ) {
            e.printStackTrace();
        }
        // set toolbar
        toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // get the connexion button
        connexionButton = findViewById(R.id.buttonConnecter);

        // get the main view elements
        mLoginFormView = findViewById(R.id.login_form);
        mProgressView = findViewById(R.id.login_progress);

        // get the four IP address fields
        IpAdresseInput = new EditText[4];
        IpAdresseInput[0] = findViewById(R.id.IpAdresseInput1);
        IpAdresseInput[1] = findViewById(R.id.IpAdresseInput2);
        IpAdresseInput[2] = findViewById(R.id.IpAdresseInput3);
        IpAdresseInput[3] = findViewById(R.id.IpAdresseInput4);

        // read token, username, JSON saving file creation
        try {
            readCachedJSONFile();
        }catch (Exception e)
        {
            //Toast.makeText(MainActivity.this, "Error while loading JSON", Toast.LENGTH_SHORT).show();
            Log.e(TAG, "ERROR while loading JSON");
        }
        // Disable the connexion button if the username and the password fields are empty
        username = findViewById(R.id.editTextUsername);
        password = findViewById(R.id.editTextPassword);
        checkFieldsForEmptyValues();

        // set listeners to enable the connexion button
        createTextWatcherForUsernamePassword();
        username.addTextChangedListener(mTextWatcher);
        password.addTextChangedListener(mTextWatcher);

        // add Navigation drawer and listeners
        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();

        // get the navigation view and set listeners
        navigationView = findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        // create and apply filters for the IP address fields
        InputFilter[][] filters = createTextViewFiltrer();
        applyTextViewFilter(filters);

        if(darkMode)
        {
            //setTheme(android.R.style.ThemeOverlay_Material_Dark);
            toggleDarkMode();
        }
        else
        {
            setTheme(android.R.style.Theme_DeviceDefault_Light_NoActionBar);
            toggleDarkMode();
        }

    }

    //! A method used to handle events of textView and to enable the button
    /*!
      Used to make the UI more user friendly
    */
    void createTextWatcherForUsernamePassword()
    {
        mTextWatcher = new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence charSequence, int i, int i2, int i3) {
            }

            @Override
            public void onTextChanged(CharSequence charSequence, int i, int i2, int i3) {
            }

            @Override
            public void afterTextChanged(Editable editable) {
                checkFieldsForEmptyValues();
            }
        };
    }

    //! A method used to filter the entered values by the user in the textView
    /*!
      Used to avoid bugs, glitch and crashes
    */
    void applyTextViewFilter(InputFilter[][] filters)
    {
        // source : https://stackoverflow.com/questions/12470067/how-to-automatically-move-to-the-next-edit-text-in-android
        for (int i = 0; i< 4; i++)
        {
            IpAdresseInput[i].setFilters(filters[i]);
            final int finalI = i;
            IpAdresseInput[i].addTextChangedListener(new TextWatcher() {

                @Override
                public void beforeTextChanged(CharSequence charSequence, int i, int i1, int i2) {}

                public void onTextChanged(CharSequence s, int start, int before, int count) {}

                @Override
                public void afterTextChanged(Editable editable)
                {
                    if (IpAdresseInput[finalI].getText().toString().length() == 3 && finalI <= 2)
                    {
                        IpAdresseInput[finalI +1].requestFocus();
                    }
                    checkFieldsForEmptyValues();
                }
            });
        }
    }

    //! A method used create a filter for the entered values by the user in the textView
    /*!
      Used to avoid bugs, glitch and crashes
    */
    InputFilter[][] createTextViewFiltrer()
    {
        // source : https://stackoverflow.com/questions/8661915/what-androidinputtype-should-i-use-for-entering-an-ip-address
        // source : http://www.easyinfogeek.com/2015/02/android-example-ip-address-input-control.html
        InputFilter[][] filters = new InputFilter[4][1];
        for (int i = 0; i < 4; i++)
        {
            final int finalI = i;
            filters[i][0] = new InputFilter() {
                @Override
                public CharSequence filter(CharSequence source, int start, int end, Spanned dest, int dstart, int dend) {
                    if (end > start) {
                        String destTxt = dest.toString();
                        String resultingTxt = destTxt.substring(0, dstart) + source.subSequence(start, end) + destTxt.substring(dend);
                        // source : https://stackoverflow.com/questions/31684083/validate-if-input-string-is-a-number-between-0-255-using-regex
                        if (!resultingTxt.matches ("([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-4][0-9]|25[0-5])")) {
                            return "";
                        } else {
                            String[] splits = resultingTxt.split("\\.");
                            for (int i=0; i<splits.length; i++) {
                                if (Integer.valueOf(splits[i]) > 255) {
                                    return "";
                                }
                            }
                        }
                    }
                    return null;
                }
            };
        }
        return filters;
    }

    //! A method used to read the JSON file present in cache
    /*!
      Used to load the last configuration
    */
    void readCachedJSONFile() throws IOException, JSONException {
        // read configuration file
        FileInputStream ipProfil = openFileInput(jsonFileName);
        int size = ipProfil.available();
        byte[] buffer = new byte[size];
        ipProfil.read(buffer);
        ipProfil.close();

        // get a JSON object with the file content
        String readContentFromJson = new String(buffer, "UTF-8");
        JSONObject obj = new JSONObject(readContentFromJson);

        //token = obj.getString("token");
        //usernameString = obj.getString("username");

        if (obj.has("theme"))
        {
            darkMode = obj.getBoolean("theme");
        }

        if(obj.has("ip"))
        {
            ipString = obj.getString("ip");
            //Splitting ip address and fill ip address EditText fields
            String[] IP_address_split = ipString.split("\\.");
            for (int i=0; i < 4; i++)
            {
                IpAdresseInput[i].setText(IP_address_split[i], TextView.BufferType.EDITABLE);
            }
        }

        Toast.makeText(MainActivity.this, "Previous profile loaded", Toast.LENGTH_SHORT).show();
    }

    //! A method used to verify if a file exists in cache
    /*!
      Used to handle exceptions if the cashed file does not exists
    */
    public boolean fileExists(Context context, String filename)
    {
        File file = context.getFileStreamPath(filename);
        if(file == null || !file.exists()) {
            return false;
        }
        return true;
    }

    //! A method used to write in a cached file the current configuration
    /*!
      Used to save the current configuration
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

    //! A method used to write in a cached file the current configuration
    /*!
      Used to save the current configuration
    */
    void writeCashedJSONFile() throws IOException, JSONException
    {
        JSONObject obj = new JSONObject();
        obj.put("ip", ipString);
        obj.put("token", token);
        obj.put("username", usernameString);
        String objString = obj.toString();

        FileOutputStream ipProfil = openFileOutput(jsonFileName, Context.MODE_PRIVATE);
        ipProfil.write(objString.getBytes());
        ipProfil.close();
    }

    //! A method used to check if the textview field are empty
    /*!
      Used to save the enable and disable the connect button
    */
    void checkFieldsForEmptyValues()
    {
        String s1 = username.getText().toString();
        String s2 = password.getText().toString();
        String s3 = IpAdresseInput[0].getText().toString();
        String s4 = IpAdresseInput[1].getText().toString();
        String s5 = IpAdresseInput[2].getText().toString();
        String s6 = IpAdresseInput[3].getText().toString();

        if(s1.equals("")|| s2.equals("") || s3.equals("") || s4.equals("") || s5.equals("") || s6.equals(""))
        {
            connexionButton.setEnabled(false);
        } else
        {
            connexionButton.setEnabled(true);
        }
    }

    //! A method called when the connect button is pressed
    /*!
      Used to start the authentication launch DatatActivity
    */
    public void onConnexionButton(View view)
    {
        //Get username and password TextView fields
        final String[] credentials = new String[3];
        credentials[0] = username.getText().toString();
        credentials[1] = password.getText().toString();
        ipString = "";

        // Get ip address TextView fields
        for (int i = 0; i < 4; i++)
        {
            ipString += IpAdresseInput[i].getText().toString();
            if (i <= 2)
            {
                ipString += ".";
            }
        }

        credentials[2] = ipString;
        showProgress(true);
        startLoginTask(credentials);
    }

    //! A method that starts the authentication
    /*!
      Start a rest call and handle the authentication response
    */
    void startLoginTask(final String[] credentials)
    {
        TaskPostLogin POST_TASK_LOGIN = new TaskPostLogin(new RestTaskInterface() {
            @Override
            public void callback(Pair<Boolean,String> result) {

                if (result.first == true) {
                    Toast.makeText(MainActivity.this, "Authentication succeeded", Toast.LENGTH_SHORT).show();

                    usernameString = credentials[0];
                    token = result.second;
                    //On recupere l'adresse IP entrer par l'usager
                    try
                    {
                        writeCashedJSONFile();
                        Toast.makeText(MainActivity.this, "Profile saved", Toast.LENGTH_SHORT).show();
                    } catch (Exception e)
                    {
                        e.printStackTrace();
                        // Toast.makeText(MainActivity.this, "Profile was not saved", Toast.LENGTH_SHORT).show();
                        Log.e(TAG, "ERROR Profile was not saved");
                    }
                    Log.i(TAG, "User " + usernameString + " successfully authenticated");

                    // go to the dataActivity and pass arguments
                    Intent mainActivity= new Intent(MainActivity.this,DataActivity.class);
                    mainActivity.putExtra("ip", ipString);
                    mainActivity.putExtra("username", usernameString);
                    mainActivity.putExtra("token", token);
                    mainActivity.putExtra("darkMode", darkMode);
                    startActivity(mainActivity);

                } else
                {
                    //Toast.makeText(MainActivity.this, "Authentication failed", Toast.LENGTH_SHORT).show();
                    Log.i(TAG, "Authentication failed");
                    if (result.second.isEmpty())
                    {
                        Toast.makeText(MainActivity.this, "Authentication failed: server offline", Toast.LENGTH_SHORT).show();
                    }
                    else
                    {
                        Toast.makeText(MainActivity.this, "Authentication failed: " + result.second, Toast.LENGTH_SHORT).show();
                    }
                    showProgress(false);
                }
            }

            @Override
            public void callbackPDF(CustomPair<Boolean, CustomPair<HttpURLConnection, InputStream>> response) {}
        });
        POST_TASK_LOGIN.execute(credentials);
    }

    //! Shows the progress UI and hides the login form.
    /*!
      Used to improve the user experience
    */
    @TargetApi(Build.VERSION_CODES.HONEYCOMB_MR2)
    private void showProgress(final boolean show) {

        // On Honeycomb MR2 we have the ViewPropertyAnimator APIs, which allow
        // for very easy animations. If available, use these APIs to fade-in
        // the progress spinner.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.HONEYCOMB_MR2) {
            int shortAnimTime = getResources().getInteger(android.R.integer.config_shortAnimTime);


            mLoginFormView.setVisibility(show ? View.GONE : View.VISIBLE);
            mLoginFormView.animate().setDuration(shortAnimTime).alpha(
                    show ? 0 : 1).setListener(new AnimatorListenerAdapter() {
                @Override
                public void onAnimationEnd(Animator animation) {
                    mLoginFormView.setVisibility(show ? View.GONE : View.VISIBLE);
                }
            });

            mProgressView.setVisibility(show ? View.VISIBLE : View.GONE);
            mProgressView.animate().setDuration(shortAnimTime).alpha(
                    show ? 1 : 0).setListener(new AnimatorListenerAdapter() {
                @Override
                public void onAnimationEnd(Animator animation) {
                    mProgressView.setVisibility(show ? View.VISIBLE : View.GONE);
                }
            });
        } else {
            // The ViewPropertyAnimator APIs are not available, so simply show
            // and hide the relevant UI components.
            mProgressView.setVisibility(show ? View.VISIBLE : View.GONE);
            mLoginFormView.setVisibility(show ? View.GONE : View.VISIBLE);
        }
    }

    //! Used to hide the hamburger menu
    /*!
      Called when the back button is pressed
    */
    @Override
    public void onBackPressed()
    {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    //! Called when a navigation menu item is selected by the user
    /*!
      Used to handle the choice of the server
    */
    @SuppressWarnings("StatementWithEmptyBody")
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();

        if (id == R.id.Theme)
        {
            darkMode = !darkMode;
            //recreate();
            try {
                saveThemeInJSONFile();
            } catch (IOException e) {
                e.printStackTrace();
            } catch (JSONException e) {
                e.printStackTrace();
            }
            toggleDarkMode();
        }

        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    //! Called when the application is closed
    /*!
      Used save the theme selected
    */
    @Override
    public void onDestroy()
    {
        //extra.removeExtra("darkMode");
        if (extra != null)
        {
            extra.remove("darkMode");
        }
        finish();
        super.onDestroy();
    }

    //! Called when the user trie to swap the theme
    /*!
      Iterate over all the view and swap the color
    */
    private void toggleDarkMode()
    {
        int backgroundColor = darkMode ? Color.rgb(48,48,48) : Color.WHITE;
        int textColor = darkMode ? Color.WHITE : Color.BLACK;

        findViewById(R.id.mainLayout).setBackgroundColor(backgroundColor);

        ColorStateList colorStateList = ColorStateList.valueOf(textColor);

        for (int i = 0; i< 4; i++)
        {
            IpAdresseInput[i].setTextColor(textColor);
            ViewCompat.setBackgroundTintList(IpAdresseInput[i], colorStateList);
        }

        ((TextView) findViewById(R.id.textView1)).setTextColor(textColor);
        ((TextView) findViewById(R.id.textView2)).setTextColor(textColor);
        ((TextView) findViewById(R.id.textView3)).setTextColor(textColor);
        ((TextView) findViewById(R.id.textView4)).setTextColor(textColor);
        ((TextView) findViewById(R.id.textView5)).setTextColor(textColor);
        ((TextView) findViewById(R.id.textView7)).setTextColor(textColor);

        username.setTextColor(textColor);
        password.setTextColor(textColor);
        ViewCompat.setBackgroundTintList(username, colorStateList);
        ViewCompat.setBackgroundTintList(password, colorStateList);

        ((Button) findViewById(R.id.buttonConnecter)).setTextColor(Color.WHITE);
        ((Button) findViewById(R.id.buttonConnecter)).setHighlightColor(Color.GRAY);

        toolbar.setTitleTextColor(textColor);
        toolbar.setBackgroundColor(backgroundColor);
        final Drawable immutableNavIcon = toolbar.getNavigationIcon();
        if (immutableNavIcon != null)
        {
            Drawable navIcon = immutableNavIcon.mutate();
            navIcon.setColorFilter(textColor, PorterDuff.Mode.SRC_ATOP);
            toolbar.setNavigationIcon(navIcon);
        }

        navigationView.setBackgroundColor(backgroundColor);
        navigationView.setItemIconTintList(ColorStateList.valueOf(textColor));
        navigationView.setItemTextColor(ColorStateList.valueOf(textColor));

        String theme = darkMode ? "Light theme" : "Dark theme";
        MenuItem menuItem = navigationView.getMenu().findItem(R.id.Theme);
        menuItem.setTitle(theme);
        navigationView.setNavigationItemSelectedListener(this);
    }
}