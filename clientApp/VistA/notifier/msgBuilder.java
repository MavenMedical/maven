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
        java.net.URL imgUrl = TcpPopups.class.getResource("info.png");
        String style="border: 1px solid;" +
            //"margin: 10px 0px;" +
            //"padding:15px 10px 15px 50px;" +
            "background-repeat: no-repeat;" +
            "background-position: 10px center left;"+
            "color: #9F6000;"+
            "background-color: #FEEFB3;";
            //"background-image: url('"+imgUrl+"');";
        if (encounter.contains("Vibramycin"))
        {
            rtn="<html><body><div style=\""+style+"\"><table><tr><td><img src='"+imgUrl+"' /></td></td>"
                    +"<td><b>Generic Alternatives to Vibramicin ($94.03):</b><br/>"
                    +"&nbsp&nbsp&nbsp Doxycycline 50mg x2 ($7.90)<br/>"
                    +"&nbsp&nbsp&nbsp Doxycycline 100mg ($13.70)</td>"
                + "</tr></table></div></body></html>";
        
        }
        return rtn;
    }
    
    public static String getNotification(String encounter, int alertLevel) throws Exception
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
