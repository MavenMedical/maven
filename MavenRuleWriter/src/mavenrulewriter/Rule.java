/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package mavenrulewriter;

import javax.swing.ListModel;

/**
 *
 * @author Efisch
 */
public class Rule {
    private String name;
    public RuleDBModel myDB;
    private boolean needsUpdate = false;
    private String comments;
    private DetailsList details;
    private String minAge;
    private String triggerType;
    
    private String triggerCode;
     private String maxAge;
    private String sex;
    
    public String generateSQL(){
           /* if (!needsUpdate){
                    return null;
            }*/
        
            String retStr = "INSERT INTO sleuth_rule (name, min_age, max_age, sex, trigger_type, trigger_code, rule_details, comments) values ('"+
                   name.replace("'", "''") +"'," +minAge +"," + maxAge + ",'" + sex + "','" + triggerType +"','" + triggerCode 
                    +"','"+details.getJSON().toString()+ "','"+ comments.replace("'", "''")+"');";
            
            return retStr;
    }
    public DetailsList getDetails() {
        return details;
    }

    public String getTriggerCode() {
        return triggerCode;
    }

    public void setTriggerCode(String triggerCode) {
        this.triggerCode = triggerCode;
    }

    public String getComments() {
        return comments;
    }

    public void setComments(String comments) {
        this.comments = comments;
    }
    
    public Rule(String nameIn, RuleDBModel DBIn){
        name = nameIn;
        minAge = "0";
        maxAge = "130";
        triggerType = "Drug Rx";
        triggerCode = "0";
        comments = "";
        sex = "";
        myDB = DBIn;
        details = new DetailsList(this);
    }
    public void setTriggerType(String in){
            triggerType = in;
    }

    public void setSex(String sex) {
        this.sex = sex;
    }

    public String getTriggerType() {
        return triggerType;
    }

    public String getSex() {
        return sex;
    }
    
    public String getName(){
        return name;
        
    }

    public String getMinAge() {
        return minAge;
    }

    public void setMinAge(String minAge) {
        this.minAge = minAge;
    }

    public String getMaxAge() {
        return maxAge;
    }

    public void setMaxAge(String maxAge) {
        this.maxAge = maxAge;
    }
    public void addDetail(Detail d){
        details.addDetail(d);
                
    }

    void removeDetailFromForm() {
        details.removeDetailFromForm();
    }

    public ListModel getDetailModel() {
        return details.getModel();
    }
}
