/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

package tcppopups;

import java.io.StringReader;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;


/**
 *
 * @author Dave
 */
public class msgBuilder {
    public static String getAlternatives(String encounter) throws Exception
    {
        String rtn="";
        String encId=encounter.split("EncID")[1].replace(">", "").replaceAll("</", "").replace("|","%7C");
        String ptId=encounter.split("PatientID")[1].replace(">", "").replaceAll("</", "");
        java.net.URL imgUrl = TcpPopups.class.getResource("info.png");
        String style="border: 1px solid;" +
            //"margin: 10px 0px;" +
            //"padding:15px 10px 15px 50px;" +
            "background-repeat: no-repeat;" +
            "background-position: 10px center left;"+
            "color: #9F6000;"+
            "background-color: #FEEFB3;";
            //"background-image: url('"+imgUrl+"');";
        if (encounter.contains("CT SINUS"))
        {
            rtn="<html><body><div style=\""+style+"\"><table><tr><td><img src='"+imgUrl+"' /></td></td>"
                    +"<td><b>Choosing Wisely&reg;:</b> Sinus CT ($807) - Acute Sinusitis:<br/>"
                    +"<table><tr><td width=10px></td><td>Most acute rhinoinusitis resolves without treatment in two weeks "
                    +"and generally does not require a CT.</td></tr><tr><td></td><td align=right><a href=\"http://demo.mavenmedical.net/#/episode/"
                    +encId+"/patient/"+ptId+"/evi/1\">See the Evidence</a></td></tr></table></td>"
                + "</tr></table></div></body></html>";
        
        }
        else if (encounter.contains("IMMUNOGLOB"))
        {
            rtn="<html><body><div style=\""+style+"\"><table><tr><td><img src='"+imgUrl+"' /></td></td>"
                    +"<td><b>Recent Immunoglobulin Results (3/26/14):</b><br/>"
                    +"&nbsp&nbsp&nbsp IgG: 710 &nbsp&nbsp&nbsp IgM: 95 <br/>"
                    +"&nbsp&nbsp&nbsp IgA: 190 &nbsp&nbsp&nbsp IgE: 7</td>"
                + "</tr></table></div></body></html>";
        
        }
        else if (encounter.contains("CEFIXIME"))
        {
            rtn="<html><body><div style=\""+style+"\"><table><tr><td><img src='"+imgUrl+"' /></td></td>"
                    +"<td><b>Cefiximie is $543.73</b> Gen-3 Cephalosporin Alternatives:<br/>"
                    +"&nbsp&nbsp&nbsp Cefdinir ($21.90)<br/>"
                    +"&nbsp&nbsp&nbsp Cefpodoxime ($93.70)</td>"
                + "</tr></table></div></body></html>";
        
        }
        
        return rtn;
    }
    public static String getNotification(String encounter, int alertLevel) throws Exception
    {
        //System.out.println(encounter);
        java.net.URL logoURL = TcpPopups.class.getResource("maven_32.jpg");
        String rtn="";
        rtn=MavenWebClient.post(encounter);
        rtn=rtn.replace("{{IMGLOGO}}",logoURL.toString());
        rtn=rtn.replace("ACETAMINOPHEN","Acetaminophen");
        rtn=rtn.replace("MG TAB","mg Tab");
        rtn=rtn.replace("IMMUNOGLOBULINS","Immunoglobulins");
        rtn=rtn.replace("CEFIXIME TAB","Cefixime Tab");
        rtn=rtn.replace("CT SINUS COMPLETE W/O CONTRAST","CT Sinus Complete w/o Contrast");
        return rtn;
    }
    public static String getNotification_Local(String encounter, int alertLevel) throws Exception
    {
        //System.out.println(encounter);
        String rtn="";
        String detailStr="";
        double costTotal=0;
        DocumentBuilderFactory factory= DocumentBuilderFactory.newInstance();
        DocumentBuilder builder=factory.newDocumentBuilder();
        InputSource is = new InputSource(new StringReader(encounter));
        Document doc=builder.parse(is);
        Element ordparent=(Element)doc.getElementsByTagName("Orders").item(0);
        NodeList orders=ordparent.getElementsByTagName("Order");
        for (int i = 0; i < orders.getLength(); i++) {
            Element ordble=(Element)orders.item(i);
            Element nm=(Element)ordble.getElementsByTagName("Name").item(0);
            String name=toTitleCase(nm.getTextContent());
            double cost=getCost(name);
            detailStr+=name+": "+String.valueOf(cost)+"<br>";
            costTotal+=cost;
        }
        rtn=getMessage(costTotal,detailStr);
        return rtn;
    }
    protected static double getCost(String name)
    {
        double rtn=147;
        if (name.toUpperCase().contains("ABDOMEN")){
            rtn=263;
        }
        else if(name.toUpperCase().contains(" CT")){
            rtn=775;
        }
        else if(name.toUpperCase().contains("A1C")){
            rtn=44;
        }
        else if(name.toUpperCase().contains("A1C")){
            rtn=44;
        }
        //System.out.println(name);
        return rtn;
    }
    private static String toTitleCase(String input) {
        input=input.toLowerCase();
        StringBuilder titleCase = new StringBuilder();
        boolean nextTitleCase = true;

        for (char c : input.toCharArray()) {
            if (Character.isSpaceChar(c)) {
                nextTitleCase = true;
            } else if (nextTitleCase) {
                c = Character.toTitleCase(c);
                nextTitleCase = false;
            }

            titleCase.append(c);
        }

        return titleCase.toString();
    }
    private static String getMessage(double cost, String detailStr)
    {
        String style="font-family: Arial; " +
            "color: #444; " +
            "word-spacing: normal; " +
            "text-align: left; " +
            "letter-spacing: 0; " +
            //"line-height: 1.5em; " +
            "font-size: 104%;";
        String color="FFFFFF";
        /*if (cost>500){
           color="CE3144";
        }
        else if (cost>200){
            color="FCE04B";
        }*/
        java.net.URL imgUrl = TcpPopups.class.getResource("maven_32.jpg");
        //System.out.println(String.valueOf(imgUrl));
        String rtn="<html><body bgcolor=#"+color+" style='"+style+"'>"
                + "<table><col width=32px><col width=30%><col width=10%><col width=60%><tr><td valign='top'><img src='"+imgUrl+"' /></td>"
                + "<td valign='top'><a href='http://mavenmedical.net'><b>Encounter Cost Alert</b></a>";
        rtn+="<br/>This Encounter Costs<br/>$"+String.valueOf(cost)+"</td>";
        rtn+="<td></td><td valign='top' style='"+style+"'>"+detailStr+"</td>";
        rtn+="</body></html>";
        return rtn;
    }
    
}
