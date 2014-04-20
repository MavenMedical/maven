/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package mavenrulewriter;

import java.util.ArrayList;

/**
 *
 * @author Efisch
 */
public class RuleDBModel {
    ArrayList<Rule> Rules;
    MavenRuleFrontend myView;
    public RuleDBModel(MavenRuleFrontend viewIn){
        myView = viewIn;
        Rules = new ArrayList<Rule>();
    }
    
    public void getDataFromDB(){
        
    }
    public void clear(){
        Rules.clear();
        myView.clearRuleModel();;
        myView.hidePanel();
    }
    public void addRule(String newName){
        if (this.containsID(newName)){
               return;
        }
         Rule newRule = new Rule(newName, this);
         Rules.add(newRule);
         myView.addRule(newRule);
         
    }
    public void addRule(Rule n){
        if (this.containsID(n.getName())){
               return;
        }
         Rules.add(n);
         myView.addRule(n);
        
    }
    public void removeRule(String toRemove){
        ArrayList<Rule> newList = new ArrayList<Rule>();
        for (Rule R:Rules){
               if (!R.getName().equals(toRemove)){
                   newList.add(R);
               } 
        }
        Rules = newList;
        myView.removeRule(toRemove);
    }
    boolean containsID(String name){
        boolean flag = false;
        for (Rule r: Rules){
            if (r.getName().equals(name)){
                flag = true;
                break;
            }            
        }    
        return flag;
    }

    Rule getRuleByName(String text) {
        for (Rule c: Rules){
                if (c.getName().equals(text)){
                    return c;
                }
        }
        return null;
                
    }

   
    
    
}
