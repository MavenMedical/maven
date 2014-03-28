/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package tcppopups;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 *
 * @author Dave
 */
public class MavenWebClient {
    public static String post(String query) throws Exception
    {
        String rtn="";
        HttpURLConnection cnx;
        URL url=new URL("http://demo.mavenmedical.net/api");
        cnx=(HttpURLConnection) url.openConnection();
        cnx.setDoInput(true);
        cnx.setDoOutput(true);
        cnx.addRequestProperty("Content-Type", "application/" + "POST");
        if (query != null) {
            cnx.setRequestProperty("Content-Length", Integer.toString(query.length()));
            cnx.getOutputStream().write(query.getBytes("UTF8"));

            DataOutputStream out = new DataOutputStream(cnx.getOutputStream());
            BufferedReader in=new BufferedReader(new InputStreamReader(cnx.getInputStream()));
            String tmp=in.readLine(); 
            while (tmp!=null)
            {
                rtn+=tmp;
                tmp=in.readLine();
            }
            out.flush();  
            out.close();  
        }
        return rtn;
    }
}
