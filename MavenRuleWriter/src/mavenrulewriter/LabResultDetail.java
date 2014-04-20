package mavenrulewriter;

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
public class LabResultDetail extends Detail{
    private String Result;
    private String labType;
    private String relation;
    public LabResultDetail(String name){
            super(name);
           Result = "0";
           labType = "Lipid Panel: LDL";
           relation = "Equal To";
    }

    @Override
    public JSONObject generateJSONString() {
         JSONObject toRet = new JSONObject();
        toRet.put("id", name);
        toRet.put("type", "lab");
        toRet.put("lab_type", labType);
        String rel = "=";
        if (relation.equals("Greater Than")){
            rel =">";
        } else if (relation.equals("Less Than")){
            rel = "<";
        }
        toRet.put("relation", rel);
        try {
            toRet.put("result", Float.parseFloat(Result));
        } catch (Exception ex){
            System.err.println("Invalid Floating Point Result, using 0.0");
            toRet.put("result", 0.0);
        }
        
        return toRet;
    }
    public String getType(){
            return labType;
    }
    public String getRelation(){
          return relation;
    }
    public void setType(String in){
        labType = in;
        
    }
    public void setRelation(String i){
        relation = i;
    }

    
    public String toString() {
        String result = "Rule will be used only if the result of " + labType + " has a value " + relation + " " + Result;
        return result;
    }

    public String getValue() {
        return Result;
    }
    public void setValue(String in){
        Result = in;
    }
            
}
