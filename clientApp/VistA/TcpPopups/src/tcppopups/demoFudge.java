/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package tcppopups;

/**
 *
 * @author Dave
 */
public class demoFudge {
    public static String fudgeProcCodes(String in){
        
        String rtn="";
        rtn=in.replace("<ProcedureCode>1</ProcedureCode><CodeType></CodeType>", "<ProcedureCode>1</ProcedureCode><CodeType>maven</CodeType>");
        rtn=rtn.replace("<ProcedureCode>2</ProcedureCode><CodeType></CodeType>","<ProcedureCode>2</ProcedureCode><CodeType>maven</CodeType>");
        rtn=rtn.replace("<ProcedureCode>3</ProcedureCode><CodeType></CodeType>","<ProcedureCode>3</ProcedureCode><CodeType>maven</CodeType>");
        rtn=rtn.replace("<ProcedureCode>4</ProcedureCode><CodeType></CodeType>","<ProcedureCode>4</ProcedureCode><CodeType>maven</CodeType>");
        rtn=rtn.replace("<ProcedureCode>5</ProcedureCode><CodeType></CodeType>","<ProcedureCode>5</ProcedureCode><CodeType>maven</CodeType>");
        rtn=rtn.replace("<ProcedureCode>6</ProcedureCode><CodeType></CodeType>","<ProcedureCode>6</ProcedureCode><CodeType>maven</CodeType>");
        return rtn;
    }
    
}
