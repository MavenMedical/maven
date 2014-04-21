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
public class HistoricProcedureDetail extends Detail{
    int frameMin;
    int frameMax;
    int CPT;
    boolean negative;
    public HistoricProcedureDetail(String nameIn) {
        super(nameIn);
    }
    public void setNegative(boolean negative){
            this.negative = negative;
    }
    public int getMinDays(){
          return frameMin;
    }
    public int getMaxDays(){
            return frameMax;
    }
    public void setCPT(int CPT) {
        this.CPT = CPT;
    }

    public void setFrameMax(int frameMax) {
        this.frameMax = frameMax;
    }

    public void setFrameMin(int frameMin) {
        this.frameMin = frameMin;
    }

    public void setName(String name) {
        this.name = name;
    }
    
    public String toString() {
        if (negative){
              return "Rule will not be used if the patient has undergone or will undergo procedure with CPT CODE: " + CPT + " in the time frame between " + frameMin + 
                      " and " + frameMax  + " days"; 
        } else {
              return "Rule will be used only if the patient has undergone or will undergo procedure with CPT CODE: " + CPT + " in the time frame between " + frameMin + 
                      " and " + frameMax  + " days from present";        }
    }
    @Override
    public JSONObject generateJSONString() {
         JSONObject toRet = new JSONObject();
        toRet.put("id", name);
        toRet.put("type", "historic_proc");
        toRet.put("exists", negative);
        toRet.put("cpt", CPT);
        toRet.put("frame_min", frameMin);
        toRet.put("frame_max", frameMax);
        return toRet;
    }
    
}
