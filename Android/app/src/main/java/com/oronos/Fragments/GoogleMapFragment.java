package com.oronos.Fragments;

import android.annotation.SuppressLint;
import android.content.DialogInterface;
import android.os.Bundle;
import android.support.v4.app.Fragment;
import android.support.v7.app.AlertDialog;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Toast;

import com.mapbox.mapboxsdk.Mapbox;
import com.mapbox.mapboxsdk.annotations.Marker;
import com.mapbox.mapboxsdk.annotations.MarkerOptions;
import com.mapbox.mapboxsdk.camera.CameraPosition;
import com.mapbox.mapboxsdk.camera.CameraUpdateFactory;
import com.mapbox.mapboxsdk.constants.Style;
import com.mapbox.mapboxsdk.geometry.LatLng;
import com.mapbox.mapboxsdk.geometry.LatLngBounds;
import com.mapbox.mapboxsdk.maps.MapView;
import com.mapbox.mapboxsdk.maps.MapboxMap;
import com.mapbox.mapboxsdk.maps.OnMapReadyCallback;
import com.mapbox.mapboxsdk.offline.OfflineManager;
import com.mapbox.mapboxsdk.offline.OfflineRegion;
import com.mapbox.mapboxsdk.offline.OfflineRegionError;
import com.mapbox.mapboxsdk.offline.OfflineRegionStatus;
import com.mapbox.mapboxsdk.offline.OfflineTilePyramidRegionDefinition;
import com.oronos.R;

import org.json.JSONObject;
import java.util.ArrayList;

//*******************************************************************
//  GoogleMapFragment
//
//  This is the fragment that display a map using mapBox map
//  we can download regions and track oronos rocket
//*******************************************************************
@SuppressLint("ValidFragment")
public class GoogleMapFragment extends Fragment implements ICustomFragments, OnMapReadyCallback {
    private View view_;
    private Mapbox mMap;
    private MapView mapView;
    private MapboxMap map;
    private ProgressBar progressBar;
    private Button downloadButton;
    private Button listButton;
    private boolean isEndNotified;
    private int regionSelected;
    // Offline objects
    private OfflineManager offlineManager;
    private OfflineRegion offlineRegion;
    // JSON encoding/decoding
    public static final String JSON_CHARSET = "UTF-8";
    public static final String JSON_FIELD_REGION_NAME = "FIELD_REGION_NAME";
    //Initial coordinates
    private static final LatLng spareportAmericaPos = new LatLng(32.9401475, -106.9193209);
    private static final LatLng Motel6Pos = new LatLng(32.3417429, -106.7628682);
    private static final LatLng ConventionCenterPos = new LatLng(32.2799304, -106.7468314);
    private static final LatLng StPieDeGuirePos = new LatLng(46.0035479, -72.7311097);

    private static LatLng positionInitiale;
    private static LatLng rocketPo = new LatLng();
    private String mapName = "";
    private Marker rocketMarker = null;
    private Marker serveurMarker = null;
    private LatLngBounds latLngBounds = null;
    private int parentLayoutOrientation = 0;
    private static final double zoom = 13.75;
    private static final String TAG = "OffManActivity";

    //! default constructor.
    /*!
    */
    public GoogleMapFragment()
    {

    }

    //! A method to initialize map.
    /*!
      Initialize rocket position and initial positions as received by the server.
    */
    public void initializeMap(String mapName)
    {
        // buttonName_ = buttonName;
        if (mapName.equals("Spaceport_America"))
        {
            rocketPo.setLongitude(spareportAmericaPos.getLongitude() + 0.000001);
            rocketPo.setLatitude(spareportAmericaPos.getLatitude() + 0.000001);
            positionInitiale = spareportAmericaPos;
        }
        else if(mapName.equals("Motel_6"))
        {
            rocketPo.setLongitude(Motel6Pos.getLongitude() + 0.000001);
            rocketPo.setLatitude(Motel6Pos.getLatitude() + 0.000001);
            positionInitiale = Motel6Pos;
        }
        else if(mapName.equals("Convention_Center"))
        {
            rocketPo.setLongitude(ConventionCenterPos.getLongitude() + 0.000001);
            rocketPo.setLatitude(ConventionCenterPos.getLatitude() + 0.000001);
            positionInitiale = ConventionCenterPos;
        }
        else if(mapName.equals("St_Pie_de_Guire"))
        {
            rocketPo.setLongitude(StPieDeGuirePos.getLongitude() + 0.000001);
            rocketPo.setLatitude(StPieDeGuirePos.getLatitude() + 0.000001);
            positionInitiale = StPieDeGuirePos;
        }
        else
        {
            rocketPo.setLongitude(spareportAmericaPos.getLongitude() + 0.000001);
            rocketPo.setLatitude(spareportAmericaPos.getLatitude() + 0.000001);
        }
        this.mapName = mapName;
    }

    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
    }

    //! A method to initialize the view.
    /*!
      initialize the mapBox API with the acces token and create an instance of this map.
    */
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {

       view_ = inflater.inflate(R.layout.fragment_google_map, container, false);

       mMap = Mapbox.getInstance(getActivity(),
               "pk.eyJ1IjoibGFkZXNmIiwiYSI6ImNqZjAwYmxvMDBob2kydm9kejNhbzAxaGoifQ.m0KQ7v3sIBfUuu3fUGazTg");

       mapView = (MapView) view_.findViewById(R.id.mapView);
       mapView.setStyleUrl(Style.SATELLITE_STREETS);

        mapView.getMapAsync(this);
       // Assign progressBar for later use
        progressBar = (ProgressBar) view_.findViewById(R.id.progressBar3);
        // Set up the offlineManager
        offlineManager = OfflineManager.getInstance(getActivity());
        // Bottom navigation bar button clicks are handled here.
        // Download offline button
        downloadButton = (Button) view_.findViewById(R.id.button4);
        downloadButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                downloadRegionDialog();
            }
        });
        // List offline regions
        listButton = (Button) view_.findViewById(R.id.btn_calibrate);
        listButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                downloadedRegionList();
            }
        });
        try {
            //MapsInitializer.initialize(getActivity().getApplicationContext());
        } catch (Exception e) {
            e.printStackTrace();
        }

        return view_;
    }

    @Override
    public void onStart() {
        super.onStart();
        mapView.onStart();
    }

    @Override
    public void onResume() {
        super.onResume();
        mapView.onResume();
    }

    @Override
    public void onPause() {
        super.onPause();
        mapView.onPause();
    }

    @Override
    public void onStop() {
        super.onStop();
        mapView.onStop();
    }

    @Override
    public void onLowMemory() {
        super.onLowMemory();
        mapView.onLowMemory();
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        //mapView.onDestroy();
    }

    //! A metod to destroy the map view.
    /*!
      Destroy the map when the destroyView is call.
    */
    @Override
    public void onDestroyView() {
        super.onDestroyView();
        mapView.onDestroy();
    }

    //! A method to initialize a dark theme.
    /*!
      toggle the Theme to the dark one at launch.
    */
    @Override
    public void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        mapView.onSaveInstanceState(outState);
    }

    //! A method to initialize a window dialog.
    /*!
      the dialog window prompt the user to enter a name for it offline region.
    */
    private void downloadRegionDialog() {
        // Set up download interaction. Display a dialog
        // when the user clicks download button and require
        // a user-provided region name
        AlertDialog.Builder builder = new AlertDialog.Builder(getActivity());

        final EditText regionNameEdit = new EditText(getActivity());
        regionNameEdit.setHint("RegionName");

        // Build the dialog box
        builder.setTitle("Save the requested Region")
                .setView(regionNameEdit)
                .setMessage("Save the requested Region")
                .setPositiveButton("Download", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        String regionName = regionNameEdit.getText().toString();
                        // Require a region name to begin the download.
                        // If the user-provided string is empty, display
                        // a toast message and do not begin download.
                        if (regionName.length() == 0) {
                            Toast.makeText(getContext(), "Please Enter a Title", Toast.LENGTH_SHORT).show();
                        } else {
                            // Begin download process
                            downloadRegion(regionName);
                        }
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.cancel();
                    }
                });
        // Display the dialog
        builder.show();
    }

    //! A method to download a region that the user can name.
    /*!
      Start the progress bar and get the current camera view to download the region.
    */
    private void downloadRegion(final String regionName) {
        // Define offline region parameters, including bounds,
        // min/max zoom, and metadata

        // Start the progressBar
        startProgress();

        // Create offline definition using the current
        // style and boundaries of visible map area
        String styleUrl = map.getStyleUrl();
        LatLngBounds bounds = map.getProjection().getVisibleRegion().latLngBounds;
        double minZoom = map.getCameraPosition().zoom;
        double maxZoom = map.getCameraPosition().zoom;
        float pixelRatio = this.getResources().getDisplayMetrics().density/4;
        OfflineTilePyramidRegionDefinition definition = new OfflineTilePyramidRegionDefinition(
                styleUrl, bounds, minZoom, maxZoom, pixelRatio);

        // Build a JSONObject using the user-defined offline region title,
        // convert it into string, and use it to create a metadata variable.
        // The metadata variable will later be passed to createOfflineRegion()
        byte[] metadata;
        try {
            JSONObject jsonObject = new JSONObject();
            jsonObject.put(JSON_FIELD_REGION_NAME, regionName);
            String json = jsonObject.toString();
            metadata = json.getBytes(JSON_CHARSET);
        } catch (Exception exception) {
            Log.e(TAG, "Failed to encode metadata: " + exception.getMessage());
            metadata = null;
        }

        // Create the offline region and launch the download
        offlineManager.createOfflineRegion(definition, metadata, new OfflineManager.CreateOfflineRegionCallback() {
            @Override
            public void onCreate(OfflineRegion offlineRegion_) {
                Log.d(TAG, "Offline region created: " + regionName);
                offlineRegion = offlineRegion_;
                launchDownload();
            }

            @Override
            public void onError(String error) {
                Log.e(TAG, "Error: " + error);
            }
        });
    }

    //! A method to start a download.
    /*!
      start a download of a limited zone.
    */
    private void launchDownload() {
        // Set up an observer to handle download progress and
        // notify the user when the region is finished downloading
        offlineRegion.setObserver(new OfflineRegion.OfflineRegionObserver() {
            @Override
            public void onStatusChanged(OfflineRegionStatus status) {
                // Compute a percentage
                double percentage = status.getRequiredResourceCount() >= 0
                        ? (100.0 * status.getCompletedResourceCount() / status.getRequiredResourceCount()) :
                        0.0;

                if (status.isComplete()) {
                    // Download complete
                    endProgress("Download Finished");
                    return;
                } else if (status.isRequiredResourceCountPrecise()) {
                    // Switch to determinate state
                    setPercentage((int) Math.round(percentage));
                }

                // Log what is being currently downloaded
                Log.d(TAG, String.format("%s/%s resources; %s bytes downloaded.",
                        String.valueOf(status.getCompletedResourceCount()),
                        String.valueOf(status.getRequiredResourceCount()),
                        String.valueOf(status.getCompletedResourceSize())));
            }

            @Override
            public void onError(OfflineRegionError error) {
                Log.e(TAG, "onError reason: " + error.getReason());
                Log.e(TAG, "onError message: " + error.getMessage());
            }

            @Override
            public void mapboxTileCountLimitExceeded(long limit) {
                Log.e(TAG, "Mapbox tile count limit exceeded: " + limit);
            }
        });

        // Change the region state
        offlineRegion.setDownloadState(OfflineRegion.STATE_ACTIVE);
    }

    //! A method to create a list of offline region
    /*!
      the offline region is save in a JSON file.
    */
    private void downloadedRegionList() {
        // Build a region list when the user clicks the list button

        // Reset the region selected int to 0
        regionSelected = 0;

        // Query the DB asynchronously
        offlineManager.listOfflineRegions(new OfflineManager.ListOfflineRegionsCallback() {
            @Override
            public void onList(final OfflineRegion[] offlineRegions) {
                // Check result. If no regions have been
                // downloaded yet, notify user and return
                if (offlineRegions == null || offlineRegions.length == 0) {
                    Toast.makeText(getContext(), "You don't have Any Zone yet", Toast.LENGTH_SHORT).show();
                    return;
                }

                // Add all of the region names to a list
                ArrayList<String> offlineRegionsNames = new ArrayList<>();
                for (OfflineRegion offlineRegion : offlineRegions) {
                    offlineRegionsNames.add(getRegionName(offlineRegion));
                }
                final CharSequence[] items = offlineRegionsNames.toArray(new CharSequence[offlineRegionsNames.size()]);

                // Build a dialog containing the list of regions
                AlertDialog dialog = new AlertDialog.Builder(getActivity())
                        .setTitle("List of region")
                        .setSingleChoiceItems(items, 0, new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int which) {
                                // Track which region the user selects
                                regionSelected = which;
                            }
                        })
                        .setPositiveButton("Done", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int id) {

                                Toast.makeText(getActivity(), items[regionSelected], Toast.LENGTH_LONG).show();

                                // Get the region bounds and zoom
                                LatLngBounds bounds = ((OfflineTilePyramidRegionDefinition)
                                        offlineRegions[regionSelected].getDefinition()).getBounds();
                                double regionZoom = ((OfflineTilePyramidRegionDefinition)
                                        offlineRegions[regionSelected].getDefinition()).getMinZoom();

                                // Create new camera position
                                CameraPosition cameraPosition = new CameraPosition.Builder()
                                        .target(bounds.getCenter())
                                        .zoom(regionZoom)
                                        .build();

                                // Move camera to new position
                                map.moveCamera(CameraUpdateFactory.newCameraPosition(cameraPosition));

                            }
                        })
                        .setNeutralButton("Delete Region", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int id) {
                                // Make progressBar indeterminate and
                                // set it to visible to signal that
                                // the deletion process has begun
                                progressBar.setIndeterminate(true);
                                progressBar.setVisibility(View.VISIBLE);

                                // Begin the deletion process
                                offlineRegions[regionSelected].delete(new OfflineRegion.OfflineRegionDeleteCallback() {
                                    @Override
                                    public void onDelete() {
                                        // Once the region is deleted, remove the
                                        // progressBar and display a toast
                                        progressBar.setVisibility(View.INVISIBLE);
                                        progressBar.setIndeterminate(false);
                                        Toast.makeText(getContext(),"deleted",
                                                Toast.LENGTH_LONG).show();
                                    }

                                    @Override
                                    public void onError(String error) {
                                        progressBar.setVisibility(View.INVISIBLE);
                                        progressBar.setIndeterminate(false);
                                        Log.e(TAG, "Error: " + error);
                                    }
                                });
                            }
                        })
                        .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                            @Override
                            public void onClick(DialogInterface dialog, int id) {
                                // When the user cancels, don't do anything.
                                // The dialog will automatically close
                            }
                        }).create();
                dialog.show();

            }

            @Override
            public void onError(String error) {
                Log.e(TAG, "Error: " + error);
            }
        });
    }

    //! A method to get saved map.
    /*!
      get the saved Json file that contains the saved region.
    */
    private String getRegionName(OfflineRegion offlineRegion) {
        // Get the region name from the offline region metadata
        String regionName;

        try {
            byte[] metadata = offlineRegion.getMetadata();
            String json = new String(metadata, JSON_CHARSET);
            JSONObject jsonObject = new JSONObject(json);
            regionName = jsonObject.getString(JSON_FIELD_REGION_NAME);
        } catch (Exception exception) {
            Log.e(TAG, "Failed to decode metadata: " + exception.getMessage());
            regionName = String.format("Failed to load", offlineRegion.getID());
        }
        return regionName;
    }

    //! A method to initialize a download progress bar.
    /*!
      initialize a progress bar for the download status.
    */
    // Progress bar methods
    private void startProgress() {
        // Disable buttons
        downloadButton.setEnabled(false);
        listButton.setEnabled(false);

        // Start and show the progress bar
        isEndNotified = false;
        progressBar.setIndeterminate(true);
        progressBar.setVisibility(View.VISIBLE);
    }

    //! A method to set a progress in a progress bar.
    /*!
      Set the progress in percentage of a progress bar.
    */
    private void setPercentage(final int percentage) {
        progressBar.setIndeterminate(false);
        progressBar.setProgress(percentage);
    }

    //! A method to notify progression bar.
    /*!
      notify the download progression bar that the download is finish.
    */
    private void endProgress(final String message) {
        // Don't notify more than once
        if (isEndNotified) {
            return;
        }
        // Enable buttons
        downloadButton.setEnabled(true);
        listButton.setEnabled(true);
        // Stop and hide the progress bar
        isEndNotified = true;
        progressBar.setIndeterminate(false);
        progressBar.setVisibility(View.GONE);
        // Show a toast
        Toast.makeText(getActivity(), message, Toast.LENGTH_LONG).show();
    }

    //! A method to update a marker on the map.
    /*!
      this is use to trace the rocket position in real time on the map.
    */
    public void upDateMarker()
    {

        if (rocketMarker == null && map != null) {
            rocketMarker = map.addMarker(new MarkerOptions()
                    .position(rocketPo)
                    .title("Rocket"));
            map.updateMarker(rocketMarker);
            latLngBounds = new LatLngBounds.Builder().include(positionInitiale).include(rocketPo).build();

        }

        else if (map != null && rocketMarker != null && latLngBounds != null)
        {
            rocketMarker.setPosition(rocketPo);
            map.updateMarker(rocketMarker);
            latLngBounds= new LatLngBounds.Builder().include(positionInitiale).include(rocketPo).build();
            map.animateCamera(CameraUpdateFactory.newLatLngBounds(latLngBounds, 200));
        }
    }

    //! A method to update the rocket latitude.
    /*!
      this is call everytime we receive new data position from the server.
    */
    public void updateRocketLat(double lat)
    {
        rocketPo.setLatitude(lat);
        upDateMarker();
    }

    //! A method to update the rocket longitude.
    /*!
      this is call everytime we receive new data position from the server.
    */
    public void updateRocketLng(double lng)
    {
        if (lng * rocketPo.getLongitude() < 0)
        {
            lng = -1*lng;
        }
        rocketPo.setLongitude(lng);
        upDateMarker();
    }

    //! A method to get the layout orientation.
    /*!
      return the orientation of the parent layout (horizontal or vertical).
    */
    @Override
    public int getParentLayoutOrientation() {
        return parentLayoutOrientation;
    }

    //! A method for the map layout.
    /*!
      set the map layout to fit the one from its parent.
    */
    @Override
    public void setParentLayoutOrientation(int orientation) {
        parentLayoutOrientation = orientation;
    }

    //! A method that is call whe the mapView is ready.
    /*!
      initialize the map view by placing the camera to the initial position.
    */
    @Override
    public void onMapReady(MapboxMap mapboxMap) {
        map = mapboxMap;

        serveurMarker = map.addMarker(new MarkerOptions()
                .position(positionInitiale) /////
                .title(mapName));
        map.updateMarker(serveurMarker);
        CameraPosition position = new CameraPosition.Builder()
                .target(positionInitiale) // Sets the new camera position
                .zoom(zoom) // Sets the zoom
                .build(); // Creates a CameraPosition from the builder
        map.animateCamera(CameraUpdateFactory.newCameraPosition(position),700,new MapboxMap.CancelableCallback() {
            @Override
            public void onFinish() {

            }

            @Override
            public void onCancel() {

            }
        });
    }
}
