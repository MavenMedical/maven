
/*************************************************************************
 *  Copyright (c) 2014 - Maven Medical
 * __________________
 * 
 *  Description: This program is a utility that will rebuild the concept
 *      Ancestry mappings for Snomed. It should only be run once and delivered
 *      to the customer as a pre-populated table.
 *  Author: Dave
 *  Assumes: Snomed has been pre-populated in the standard schema 
 *  Side Effects: Population of ConceptAncestry table
 *  Last Modified: MAV-16
 * *************************************************************************/

package Maven.MiscUtilities;



import java.sql.DriverManager;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.PreparedStatement;
import java.util.ArrayList;
import java.util.Scanner;

public class DxChildrenGen {
    
    public static String user="";
    public static String pass="";
    public static String url="";
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) {
        try 
        {
                //register the drivers
		Class.forName("org.postgresql.Driver");
                System.out.println("Postgres JDBC Registered");
                
                //prompt for database login info
                System.out.printf("JDBC URL (jdbc:postgresql://host/db): ");
                Scanner scan=new Scanner(System.in);
                url=scan.nextLine();
                System.out.printf("Database Username: ");
                user=scan.nextLine();
                System.out.printf("Database Password: ");
                pass=scan.nextLine();
 
                try
                {       //connect to the db and get the concepts that haven't already been populated
                        //(Allows you to stop and restart without truncating and going back to the begining)
                        Connection db=DriverManager.getConnection(url,user,pass);
                        Statement st=db.createStatement();
                        ResultSet rs=st.executeQuery("select distinct id from concept where id not in (select distinct ancestor from conceptancestry);");
                        while (rs.next())
                        {
                            //get variable to track whether snomed has listed the concept as a child of itself 
                            //we track this because we need a row where the child and parent are identical for proper mapping
                            Boolean selfAsChild=false;
                            long curconcept=rs.getLong(1); //get the current concept we're working on
                            System.out.println(curconcept); //inform the user that the program is still moving forward
                            ArrayList<Long> al=childConcepts(curconcept,"|"); //prepare a list of the children
                            try
                            {
                                Connection insertDb=DriverManager.getConnection(url,user,pass); //create a database connectino to insert the children
                                PreparedStatement insertSt=insertDb.prepareStatement("insert into conceptAncestry values (?,?)");
                                for (Long child : al)
                                {
                                    insertSt.setLong(1, curconcept); //set the params in the insert statement
                                    insertSt.setLong(2,child); 
                                    insertSt.execute(); //insert the data
                                    //track whether we've inserted a row with the parent as a child of itself
                                    if (child==curconcept)
                                    {
                                        selfAsChild=true;
                                    }
                                }
                                //if we never inserted a row where the parent and child are identical, do that now
                                if (!selfAsChild)
                                {
                                    insertSt.setLong(1, curconcept);
                                    insertSt.setLong(2,curconcept);
                                    insertSt.execute();
                                }
                                insertDb.close(); //close up shop
                            }
                                catch(SQLException ex){
                                    System.out.println(ex.getMessage());}
                            
                            
                        } 
                }
                catch (SQLException ex){
                System.out.println(ex.getMessage());} 
        } 
        catch (ClassNotFoundException e) {       
            System.out.println(e.getMessage());}
    }
    
    public static ArrayList childConcepts(Long ParentConcept,String curlist)
    {
        ArrayList<Long> rtn=new ArrayList();
        try
        {
            //connect to the DB and get all children using the "is a" relationship type
            Connection db=DriverManager.getConnection(url,user,pass);
            Statement st=db.createStatement();
            String sql="select distinct child.id child " +
                "from concept child " +
                "inner join relationships rel on rel.sourceid=child.id " +
                "inner join concept parent on parent.id=rel.destinationid " +
                "where rel.typeid=116680003 /*isa*/ " +
                "and  rel.active=1 and parent.active=1 and child.active=1 and parent.id="+ParentConcept.toString();
            ResultSet rs=st.executeQuery(sql);
            //for each of the children, 
            while (rs.next())
            {
                Long child=rs.getLong(1);
                //track who we've worked on so we don't do the same concept twice
                if (!curlist.contains("|"+child.toString()+"|"))
                {
                    //If this is a new child, add the child concept
                    rtn.add(child);jdbc:postgresql://host/db
                    curlist+=child.toString()+"|";
                    //add the child's child concepts and so forth recursively
                    ArrayList<Long> granKids=childConcepts(child,curlist);
                    for (Long l : granKids)
                    {
                        if (!curlist.contains("|"+l.toString()+"|"))
                        {
                            rtn.add(l);
                            curlist+=l.toString()+"|";
                        }
                    }
                }
                
            }
            //clean up shop and return the current array up the stack
            db.close(); st.close(); rs.close();
            return rtn;
         }
        catch (SQLException ex)
        {
            System.out.println(ex.getMessage());
        }
        return rtn;
    }
}
