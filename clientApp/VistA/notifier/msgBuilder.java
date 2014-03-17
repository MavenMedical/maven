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
    public static String getNotification(String encounter, int alertLevel) throws Exception
    {
        //System.out.println(encounter);
        String rtn="";
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
            String name=nm.getTextContent();
            costTotal+=getCost(name);
        }
        rtn=getMessage(costTotal);
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
    private static String getMessage(double cost)
    {
        String color="419D50";
        if (cost>500){
           color="CE3144";
        }
        else if (cost>200){
            color="FCE04B";
        }
        java.net.URL imgUrl = TcpPopups.class.getResource("maven_32.gif");
        //System.out.println(String.valueOf(imgUrl));
        String rtn="<html><body bgcolor=#"+color+">"
                + "<table><tr><td valigh='top'><img src='"+imgUrl+"' /></td>"
                + "</td><a href='http://mavenmedical.net'>Encounter Cost Alert</a>";
        rtn+="<br/>This Encounter Costs $"+String.valueOf(cost)+"</td>";
        rtn+="</body></html>";
        return rtn;
    }
    
}
