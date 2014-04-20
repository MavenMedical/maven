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
public class EncounterProcDetail extends Detail{
    private int cpt;
    private boolean negative;
    public EncounterProcDetail(String name){
            super(name);
           cpt = 0;
           negative = false;
    }

    @Override
    public JSONObject generateJSONString() {
        JSONObject toRet = new JSONObject();
        toRet.put("id", name);
        toRet.put("type", "encounter_proc");
        toRet.put("exists", negative);
        toRet.put("cpt", cpt);
        return toRet;
    }
    public int getCPT(){
            return cpt;
    }
    public boolean isNegative(){
          return negative;
    }
    public void setCPT(int i){
        cpt = i;
        
    }
    public void setNegative(boolean b){
        negative = b;
    }

    
    public String toString() {
        if (negative){
              return "Rule will not be used if the encounter contains procedure with CPT CODE: " + cpt; 
        } else {
             return "Rule will be used only if the encounter contains procedure with CPT CODE: " + cpt; 
        }
    }
            
}
