/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package mavenrulewriter;

import org.json.JSONObject;

/**
 *
 * @author Efisch
 */
public abstract class Detail {
    
    static Detail generateDetailFromJSON(JSONObject current) {
        String type = current.get("type").toString();
        if (type.equals("historic_proc")){
            HistoricProcedureDetail toRet = new HistoricProcedureDetail(current.getString("id"));
            
            toRet.CPT=current.getInt("cpt");
            toRet.frameMax = current.getInt("frame_max");
            toRet.frameMin = current.getInt("frame_min");            
            toRet.negative = current.getBoolean("exists");
            return toRet;
        }
        if (type.equals("problemlist_dx")){
            EncounterProbListDetail toRet = new EncounterProbListDetail(current.getString("id"));
       
            toRet.setSnomed(current.getInt("snomed"));
            toRet.setNegative(current.getBoolean("exists"));
            return toRet;
        }
        if (type.equals("encounter_proc")){
            EncounterProcDetail toRet = new EncounterProcDetail(current.getString("id"));
       
            toRet.setCPT(current.getInt("cpt"));
            toRet.setNegative(current.getBoolean("exists"));
            return toRet;
        }
        if (type.equals("lab")){
            LabResultDetail toRet = new LabResultDetail(current.getString("id"));
            toRet.setType(current.getString("lab_type"));
            String rel = current.getString("relation");
            toRet.setRelation("Equal To");
            if (rel.equals(">"))
                toRet.setRelation("Greater Than");
            if (rel.equals("<"))
                toRet.setRelation("Less Than");
            toRet.setValue(current.getString("result"));
            return toRet;
        }
        return null;
    }
   
    public String name;
    public abstract JSONObject generateJSONString();
    public Detail(String nameIn){
            name = nameIn;
    }
      public abstract String toString();
    public String getName(){
        return name;
    }
   
}
