package mavenrulewriter;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.json.JSONObject;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

/**
 *
 * @author Efisch
 */
public class FHIRWrapper {
    JSONObject data;
    public FHIRWrapper(File fname){
        try {
            BufferedReader JSONIn = new BufferedReader(new FileReader(fname));
            String temp=JSONIn.readLine();
            String JSONText = "";
            while (temp!=null){
                JSONText += (temp+"\n");
                temp = JSONIn.readLine();
            }
            System.out.println(JSONText);
            data = new JSONObject(JSONText);
            System.out.println(data);
            System.out.println(data.getString("date"));
        } catch (FileNotFoundException ex) {
            Logger.getLogger(FHIRWrapper.class.getName()).log(Level.SEVERE, null, ex);
            data = null;
        } catch (IOException ex) {
            Logger.getLogger(FHIRWrapper.class.getName()).log(Level.SEVERE, null, ex);
            data = null;
        }
        
        
    
        
    }
    public FHIRWrapper(String JSONText){
         data = new JSONObject(JSONText);
    }
    public int getAge(){
        JSONObject subject = data.getJSONObject("subject");
        String birthData = subject.getString("birthDate");

        int bYear = Integer.parseInt(birthData.split("-")[0]);
        int bMonth = Integer.parseInt(birthData.split(("-"))[1]);
        Date curDate = new Date();
        
        DateFormat dateFormat = new SimpleDateFormat("yyyy/MM/dd HH:mm:ss");
        String DString = dateFormat.format(curDate);
        int curYear = Integer.parseInt(DString.split("/")[0]);
        int curMonth = Integer.parseInt(DString.split("/")[1]);
        System.out.println(DString);    int age = curYear-bYear;
        if (curMonth<bMonth)
            age--;
        return age;
    }
   
}
