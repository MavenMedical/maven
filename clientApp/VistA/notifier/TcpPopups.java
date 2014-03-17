/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package tcppopups;

import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Insets;
import java.awt.Toolkit;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.ServerSocket;
import java.net.Socket;
import javax.swing.JEditorPane;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.event.HyperlinkEvent;
import javax.swing.event.HyperlinkListener;
import java.awt.Desktop;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import javax.swing.ImageIcon;
import javax.swing.JWindow;

/**
 *
 * @author Dave
 */
public class TcpPopups {

    /**
     * @param args the command line arguments
     */
    public static void main(String[] args) throws Exception {
        String clientSentence;
        String capitalizedSentence;
        ServerSocket welcomeSocket = new ServerSocket(9090);

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
            //System.out.println(clientSentence.length());
            clientSentence=msgBuilder.getNotification(clientSentence, 0);
            notify2("Header", clientSentence, false);
            clientSentence="";
        }
    }

    public static void notify2(String text, String body, final Boolean fade) throws Exception {
        int wide=400;
        int high=100;
        //System.out.println(body);
        //System.out.println(body.length());
        JEditorPane jep = new JEditorPane("text/html", body);
        jep.setSize(wide, high);
        jep.setEditable(false);
        jep.setOpaque(false);
        jep.addHyperlinkListener(new HyperlinkListener() {
            public void hyperlinkUpdate(HyperlinkEvent hle) {
                if (HyperlinkEvent.EventType.ACTIVATED.equals(hle.getEventType())) {
                    launch(hle.getURL().toString());
                }
            }
        });  
        
        //JLabel heading=new JLabel("");
        //java.net.URL imgUrl = TcpPopups.class.getResource("maven_32.gif");
        //ImageIcon ico=new ImageIcon(imgUrl);
        //heading.setIcon(ico);
        //heading.setOpaque(false);
        
        final JWindow f = new JWindow();
        //f.getContentPane().add(heading,BorderLayout.WEST);
        f.getContentPane().add(jep, BorderLayout.CENTER);
        f.setSize(wide, high);
        f.setAlwaysOnTop(true);
        Dimension scrSize = Toolkit.getDefaultToolkit().getScreenSize();// size of the screen
        Insets toolHeight = Toolkit.getDefaultToolkit().getScreenInsets(f.getGraphicsConfiguration());// height of the task bar
        f.setLocation(scrSize.width - f.getWidth(), scrSize.height - toolHeight.bottom - f.getHeight());
        //f.setUndecorated();
        f.setVisible(true);
        new Thread() {
            @Override
            public void run() {
                try {
                    Thread.sleep(1000);
                    float tl = 1;
                    if (fade) {
                        while (tl > 0.20f) {
                            tl -= .01;
                            Thread.sleep(70); // time after which pop up will be disappeared.
                            f.setOpacity(tl);
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

    public static void notify(String header, String body, final Boolean fade) {
        final JFrame frame = new JFrame();
        frame.setSize(300, 80);
        frame.setUndecorated(true);
        frame.setAlwaysOnTop(true);
        frame.setLayout(new GridBagLayout());
        Dimension scrSize = Toolkit.getDefaultToolkit().getScreenSize();// size of the screen
        Insets toolHeight = Toolkit.getDefaultToolkit().getScreenInsets(frame.getGraphicsConfiguration());// height of the task bar
        frame.setLocation(scrSize.width - frame.getWidth(), scrSize.height - toolHeight.bottom - frame.getHeight());
        GridBagConstraints constraints = new GridBagConstraints();
        constraints.gridx = 0;
        constraints.gridy = 0;
        constraints.weightx = 0f;
        constraints.weighty = 0f;
        constraints.fill = GridBagConstraints.NONE;
        constraints.anchor = GridBagConstraints.NORTH;
        constraints.gridx = 0;
        constraints.gridy++;
        constraints.weightx = 1.0f;
        constraints.weighty = 1.0f;
        constraints.insets = new Insets(5, 5, 5, 5);
        constraints.fill = GridBagConstraints.BOTH;
        JLabel messageLabel = new JLabel("<HTML>" + body); //('<HtMl>'+message);
        frame.add(messageLabel, constraints);
        //frame.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE);
        frame.setVisible(true);
        new Thread() {
            @Override
            public void run() {
                try {
                    float tl = 1;
                    if (fade) {
                        while (tl > 0.20f) {
                            tl -= .01;
                            Thread.sleep(70); // time after which pop up will be disappeared.
                            frame.setOpacity(tl);
                            frame.setVisible(true);
                        }
                    } else {
                        Thread.sleep(5000);
                    }
                    frame.dispose();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        ;
    }

.start();

    }
    
}
