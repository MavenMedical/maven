package net.mavenmedical.Notifications;

import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.text.Html;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.WebView;
import android.widget.ArrayAdapter;
import android.widget.BaseAdapter;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Created by Tom on 5/28/14.
 */
public class NotificationAdapter extends ArrayAdapter<Map<String,String>> {

    private Context mContext;
    private int mLayout;
    private List<Map<String, String>> mAdapter;
    final public static String TEXT = "TEXT";
    final public static String LINK = "LINK";

    public NotificationAdapter(Context context, int layout) {
        super(context, layout);
    }

    public NotificationAdapter(Context context, int layout, List<Map<String, String>> adapter) {
        super(context, layout, adapter);
        mAdapter=adapter;
    }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
        Map<String,String> data = getItem(position);
        Log.i(MavenNotifications.mTag,data.toString());
        LayoutInflater inflater = (LayoutInflater) getContext()
                .getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        View view = inflater.inflate(R.layout.list_item, parent, false);
        TextView tv = (TextView)view.findViewById(R.id.item_text);
        //tv.setText(Html.fromHtml(data.get(TEXT)));
        tv.setText(data.get(TEXT));
        if (data.containsKey(LINK)) {
            view.setOnClickListener(new LinkClickListener(data.get(LINK)));
        }
        return view;
    }

    public ArrayList<Map<String, String>> getData() {
        return (ArrayList<Map<String, String>>) mAdapter;
    }

    private class LinkClickListener implements View.OnClickListener {
        private String mLink;

        public LinkClickListener(String link) {
            mLink = link;
        }

        public void onClick(View v) {
            Intent i = new Intent(Intent.ACTION_VIEW);
            i.setData(Uri.parse(mLink));
            getContext().startActivity(i);
        }
    }
}

