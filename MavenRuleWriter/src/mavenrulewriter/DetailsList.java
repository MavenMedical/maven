package mavenrulewriter;

import java.util.ArrayList;
import javax.swing.DefaultListModel;
import javax.swing.JOptionPane;
import javax.swing.ListModel;
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
public class DetailsList {
    ArrayList<Detail> details;
    private Rule myRule;
    private int ID;
    public DetailsList(Rule myRuleIn){
            details = new ArrayList<Detail>();
            myRule = myRuleIn;
    }
    
    public void addDetail(Detail in){
        if (this.containsID(in.name)){
            removeDetail(in.name);
            myRule.myDB.myView.removeDetail(in.name);
        } else {
            in.name = "" + ID;
            ID++;
        }
        details.add(in);
        myRule.myDB.myView.addDetail(in);
        
    }
    public void removeDetail(String name){
        ArrayList<Detail> newList = new ArrayList<Detail>();
        for (Detail D:details){
            if (!D.getName().equals(name)){
                newList.add(D);
            }
        } 
        details = newList;
        myRule.myDB.myView.removeDetail(name);
        
    }
    public ListModel getModel(){
        DefaultListModel n = new DefaultListModel();
        for (int c=0;c<details.size();c++){
            n.add(c, details.get(c));
        }
        return n;
        
    }
    public void removeDetailFromForm(){
        Detail toRemove = myRule.myDB.myView.getSelectedDetail();
        ArrayList<Detail> newList = new ArrayList<Detail>();
        for (Detail D:details){
            if (!D.getName().equals(toRemove.getName())){
                newList.add(D);
            }
        } 
        details = newList;
        myRule.myDB.myView.removeDetail(toRemove.getName());
        
        
    }
    public boolean containsID(String name){
       
        for (Detail D:details){
            if (D.getName().equals(name)){
                return true;
            }
            
        }
        return false;
        
    }
    public JSONObject getJSON(){
        JSONObject toRet = new JSONObject();
        ArrayList<JSONObject> c = new ArrayList<JSONObject>();
        for (Detail n:details){
            c.add(n.generateJSONString());
        }
        toRet.put("details", c);
        return toRet;
        
    }

   
}
