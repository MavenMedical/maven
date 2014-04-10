/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tcppopups;

import java.awt.AWTException;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Insets;
import java.awt.Toolkit;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import javax.swing.JEditorPane;
import javax.swing.event.HyperlinkEvent;
import javax.swing.event.HyperlinkListener;
import java.awt.Desktop;
import java.awt.Menu;
import java.awt.MenuItem;
import java.awt.PopupMenu;
import java.awt.SystemTray;
import java.awt.TrayIcon;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.imageio.ImageIO;
import javax.swing.JWindow;

/**
 *
 * @author Dave
 */
public class TcpPopups {
    public static int wide=450;
    public static int highOne=150;
    public static int highTwo=90;
    public static int initialSleepTime=5000;
    public static int fadeInterval=150;
    
    public static int activeMessages=0;
    public static String lastMessage="";
    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception {
        String clientSentence;
        String capitalizedSentence;
        ServerSocket welcomeSocket = new ServerSocket(9090);
        prepSysTray();
        while (true) {
            Socket connectionSocket = welcomeSocket.accept();
            BufferedReader inFromClient
                    = new BufferedReader(new InputStreamReader(connectionSocket.getInputStream()));
            //DataOutputStream outToClient = new DataOutputStream(connectionSocket.getOutputStream());
            StringBuilder sb=new StringBuilder();
            String tmp="";
            while ((tmp = inFromClient.readLine()) != null) {
                sb.append(tmp);
            }
            clientSentence=sb.toString();
            handleNewMessage(clientSentence);
            clientSentence="";
        }
    }
    
    
    public static ActionListener performReplay = new ActionListener() {
        public void actionPerformed(ActionEvent e) {
            try {
                handleNewMessage(lastMessage);
            } catch (Exception ex) {
                Logger.getLogger(TcpPopups.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
    };
    
    public static void prepSysTray() throws Exception
    {
        if (!SystemTray.isSupported()) {
            System.out.println("SystemTray is not supported");
            return;
        }
        final PopupMenu popup = new PopupMenu();
        final TrayIcon trayIcon =new TrayIcon(ImageIO.read(TcpPopups.class.getResource("maven_16.png")));
        final SystemTray tray = SystemTray.getSystemTray();
       
        // Create a pop-up menu components
        MenuItem replayMenu = new MenuItem("Replay Previous Message");
        replayMenu.addActionListener(performReplay); 
        MenuItem exitItem = new MenuItem("Exit");
       
        //Add components to pop-up menu
        popup.add(exitItem);
        popup.addSeparator();;
        popup.addSeparator();
        popup.add(replayMenu);
        
       
        trayIcon.setPopupMenu(popup);
       
        try {
            tray.add(trayIcon);
        } catch (AWTException e) {
            System.out.println("TrayIcon could not be added.");
        }
    }
    
    public static void handleNewMessage(String msg) throws Exception
    {
        lastMessage=msg;
         /////////////////////DEMO Fudge////////////////////////////////////
            msg=demoFudge.fudgeProcCodes(msg);
            ///////////////////////////////////////////////////////////////////
            System.out.println(msg);
            String costAlert=msgBuilder.getNotification(msg, 0);
            //System.out.println(costAlert);
            String alternatives=msgBuilder.getAlternatives(msg);
            notify("Header", costAlert, true);
            if(alternatives!=""){
                //System.out.println(alternatives);
                notify2("Header",alternatives, true);
            }
    }
    public static void notify(String text, String body, final Boolean fade) throws Exception {
        //int wide=450;
        //int high=150;
        //System.out.println(body);
        //System.out.println(body.length());
        activeMessages+=1;
        
        JEditorPane jep = new JEditorPane("text/html", body);
        jep.setSize(wide, highOne);
        jep.setEditable(false);
        jep.setOpaque(false);
        jep.addHyperlinkListener(new HyperlinkListener() {
            public void hyperlinkUpdate(HyperlinkEvent hle) {
                if (HyperlinkEvent.EventType.ACTIVATED.equals(hle.getEventType())) {
                    launch(hle.getURL().toString());
                }
            }
        });  
        final JWindow f = new JWindow();
        //f.getContentPane().add(heading,BorderLayout.WEST);
        f.getContentPane().add(jep, BorderLayout.CENTER);
        f.setSize(wide, highOne);
        f.setAlwaysOnTop(true);
        Dimension scrSize = Toolkit.getDefaultToolkit().getScreenSize();// size of the screen
        Insets toolHeight = Toolkit.getDefaultToolkit().getScreenInsets(f.getGraphicsConfiguration());// height of the task bar
        f.setLocation(scrSize.width - f.getWidth(), scrSize.height - toolHeight.bottom - f.getHeight());
        //f.setUndecorated();
        //f.pack();
        f.setVisible(true);
        new Thread() {
            @Override
            public void run() {
                try {
                    Thread.sleep(initialSleepTime);
                    float tl = 1;
                    if (fade) {
                        //System.out.println(activeMessages);
                        while (tl > 0.20f && activeMessages<2 ) {
                            tl -= .01;
                            Thread.sleep(fadeInterval); // time after which pop up will be disappeared.
                            f.setOpacity(tl);
                            f.setVisible(true);
                        }
                    } else {
                        Thread.sleep(5000);
                    }
                    
                    activeMessages-=1;
                    Thread.sleep(fadeInterval);
                    f.dispose();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        ;
    }

    .start();

    }
    public static void notify2(String text, String body, final Boolean fade) throws Exception {
        //int wide=450;
        //int high=150;
        //System.out.println(body);
        //System.out.println(body.length());
        JEditorPane jep = new JEditorPane("text/html", body);
        jep.setSize(wide, highTwo);
        jep.setEditable(false);
        jep.setOpaque(false);
        jep.addHyperlinkListener(new HyperlinkListener() {
            public void hyperlinkUpdate(HyperlinkEvent hle) {
                if (HyperlinkEvent.EventType.ACTIVATED.equals(hle.getEventType())) {
                    launch(hle.getURL().toString());
                }
            }
        });  
        final JWindow f = new JWindow();
        //f.getContentPane().add(heading,BorderLayout.WEST);
        f.setBackground(Color.WHITE);
        f.getContentPane().add(jep, BorderLayout.CENTER);
        f.pack();
        f.setSize(wide, f.getHeight());
        f.setAlwaysOnTop(true);
        Dimension scrSize = Toolkit.getDefaultToolkit().getScreenSize();// size of the screen
        Insets toolHeight = Toolkit.getDefaultToolkit().getScreenInsets(f.getGraphicsConfiguration());// height of the task bar
        f.setLocation(scrSize.width - f.getWidth(), scrSize.height - toolHeight.bottom - f.getHeight()-highOne);
        //f.setUndecorated();
        f.setVisible(true);
        new Thread() {
            @Override
            public void run() {
                try {
                    Thread.sleep(initialSleepTime);
                    float tl = 1;
                    if (fade) {
                        while (tl > 0.20f && activeMessages<2 ) {
                            tl -= .01;
                            Thread.sleep(fadeInterval); // time after which pop up will be disappeared.
                            f.setOpacity(tl);
                            f.setBackground(Color.WHITE);
                            f.setVisible(true);
                        }
                    } else {
                        Thread.sleep(5000);
                    }
                    f.dispose();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        ;
    }

    .start();

    }
    public static void launch(String url) {
        if (Desktop.isDesktopSupported()) {
            Desktop desktop = Desktop.getDesktop();
            try {
                desktop.browse(new URI(url));
            } catch (IOException | URISyntaxException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        } else {
            Runtime runtime = Runtime.getRuntime();
            try {
                runtime.exec("xdg-open " + url);
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }
    }

}