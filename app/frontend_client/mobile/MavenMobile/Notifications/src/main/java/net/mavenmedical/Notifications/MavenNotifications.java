package net.mavenmedical.Notifications;

import android.annotation.TargetApi;
import android.app.Activity;
import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.net.http.AndroidHttpClient;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.text.Html;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.os.Handler;

import org.apache.http.HttpResponse;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.BasicResponseHandler;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

/**
 * Created by Tom on 5/27/14.
 */
public class MavenNotifications extends Activity
{
    private NotificationAdapter mAdap;
    private Handler mHandler;
    final public static String mTag = "Maven";
    private int mGetId;

    final private String SAVED_LIST = "SAVED_LIST";

    public void onCreate(Bundle bundle)
    {
        super.onCreate(bundle);
        mHandler = new Handler();
        mGetId=0;
        setContentView(R.layout.fragment_main);
        ListView lView = new ListView(this);

        List<Map<String, String>> data = null;
        if (bundle != null) {
            data = (List<Map<String,String>>)bundle.getSerializable(SAVED_LIST);
        }
        if (data == null) {
            data = new ArrayList<Map<String,String>>();
//            Map<String,String> map = new HashMap<String,String>();
//            map.put(NotificationAdapter.TEXT, "<a href='http://www.google.com>link</a>");
//            map.put(NotificationAdapter.LINK, "http://www.yahoo.com");
//            data.add(map);
  //          Log.i(mTag, "added to adapter: "+data.toString());
        }
        mAdap = new NotificationAdapter(this,R.layout.list_item, data);
        lView.setAdapter(mAdap);
        lView.setFocusableInTouchMode(true);
        View footerView =  ((LayoutInflater)this.getSystemService(Context.LAYOUT_INFLATER_SERVICE)).inflate(R.layout.list_header, null, false);
        lView.addHeaderView(footerView);
        lView.setDivider(null);
        lView.setDividerHeight(10);
        setContentView(lView);
        (new HttpGetTask(mGetId++)).execute();
    }

    protected void onSaveInstanceState(Bundle bundle) {
        bundle.putSerializable(SAVED_LIST, mAdap.getData());
    }
    public void onDestroy() {
        super.onDestroy();
        Log.i(mTag, "mDestroy");
    }

    public void handleResult(List<Map<String,String>> list, int id) {
        int i=0;
        int delay=0;
        if(list != null) {
            for(Map<String,String> s: list) {
                if (i==0) mAdap.insert(s,i);
                i++;
            }
            delay = 0;
            Log.i(mTag, "got results "+id+", make a shorter delay");
        } else {
            delay = 30 * 1000;
            Log.i(mTag, "no results "+id+", make a longer delay");
        }

        mHandler.postDelayed(new Runnable() {
            public void run() {
                if (!MavenNotifications.this.isDestroyed()) {
                    (new HttpGetTask(mGetId++)).execute();
                }
            }
        }, delay);
    }

     public void clickClear(View footer) {
        mAdap.clear();
    } 
    @TargetApi(Build.VERSION_CODES.JELLY_BEAN)
    private void sendNotification() {
        Intent intent = new Intent(this, MainActivity.class);
        PendingIntent pIntent = PendingIntent.getActivity(this, 0, intent, 0);

// build notification
// the addAction re-use the same intent to keep the example short
        Notification n  = new Notification.Builder(this)
                .setContentTitle("New mail from " + "test@gmail.com")
                .setContentText("Subject")
                .setContentIntent(pIntent)
                .setSmallIcon(R.drawable.ic_launcher)
                .build();


        NotificationManager notificationManager =
                (NotificationManager) getSystemService(NOTIFICATION_SERVICE);

        notificationManager.notify(0, n);
    }

    private class HttpGetTask extends AsyncTask<Void, Void, List<Map<String,String>>> {
        //private String deviceId ="123";
        private String URL ="http://23.251.150.28/broadcaster/poll?key=JHU1093124";
        private String tag="MavenMobile";

        AndroidHttpClient mClient = AndroidHttpClient.newInstance("");
        private int mId;

        public HttpGetTask(int id) {
            super();
            mId=id;
        }


        @Override
        protected List<Map<String,String>> doInBackground(Void... params) {

            HttpGet request = new HttpGet(URL);
            request.addHeader("deviceId", "tom");
            JSONResponseHandler responseHandler = new JSONResponseHandler();
            try {
                return mClient.execute(request, responseHandler);
            } catch (ClientProtocolException e) {
                e.printStackTrace();
            } catch (IOException e) {
                e.printStackTrace();
            }
            return null;
        }

        @Override
        protected void onPostExecute(List<Map<String,String>> result) {
            if (null != mClient)
                mClient.close();
            MavenNotifications.this.handleResult(result, mId);
        }
    }

    private class JSONResponseHandler implements ResponseHandler<List<Map<String,String>>> {

        private static final String LONGITUDE_TAG = "lng";
        private static final String LATITUDE_TAG = "lat";
        private static final String MAGNITUDE_TAG = "magnitude";
        private static final String EARTHQUAKE_TAG = "earthquakes";

        @Override
        public List<Map<String,String>> handleResponse(HttpResponse response)
                throws ClientProtocolException, IOException {
            List<Map<String,String>> result = new ArrayList<Map<String,String>>();
            String JSONResponse = new BasicResponseHandler()
                    .handleResponse(response);
            if (JSONResponse == null) {
                    return result;
            }
            try {

                // Get top-level JSON Object - a Map
                JSONTokener tokener = new JSONTokener(JSONResponse);
                JSONArray responseArray = (JSONArray) tokener.nextValue();

                // Iterate over earthquakes list
                for (int idx = 0; idx < responseArray.length(); idx++) {
                    Map<String, String> map = new HashMap<String,String>();
                    JSONObject jmap = responseArray.getJSONObject(idx);

                    Iterator<String> iter = jmap.keys();
                    while(iter.hasNext()) {
                        String key = iter.next();
                        map.put(key, jmap.getString(key));
                    }
                    result.add(map);

                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
            return result;
        }
    }


}
