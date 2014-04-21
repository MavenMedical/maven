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
public class EncounterProbListDetail extends Detail{
    private int snomed;
    private boolean negative;
    public EncounterProbListDetail(String name){
           super(name);
           snomed = 0;
           negative = false;
    }

    @Override
    public JSONObject generateJSONString() {
        JSONObject toRet = new JSONObject();
        toRet.put("id", name);
        toRet.put("type", "problemlist_dx");
        toRet.put("exists", negative);
        toRet.put("snomed", snomed);
        return toRet;
    }
    public int getSnomed(){
            return snomed;
    }
    public boolean isNegative(){
          return negative;
    }
    public void setSnomed(int i){
        snomed = i;
        
    }
    public void setNegative(boolean b){
        negative = b;
    }

    
    public String toString() {
        if (negative){
              return "Rule will not be used if the encounter problem list contains Dx with SnomedID: " + snomed; 
        } else {
             return "Rule will be used only if the encounter problem list contains Dx with Snomed ID: " + snomed; 
        }
    }
            
}
