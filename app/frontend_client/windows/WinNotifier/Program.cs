using System;
using System.Collections.Generic;
using System.Threading;
using System.Windows.Forms;
using System.Data;
using System.Text.RegularExpressions;
using System.Net;
using System.IO;
using System.Diagnostics;

namespace MavenAsDemo
{
    static class Program
    {
        public static string url = "";
        private static bool continueOn = true;
        private static byte[] EncryptedKey = null;
        private static Settings cursettings;

        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            try
            {
                cursettings = new Settings();
                Application.SetCompatibleTextRenderingDefault(false);
                Authenticator.HandleLoginStickiness(); //clear the login settings if we shouldn't be using them
                EncryptedKey = Authenticator.GetEncryptedAuthKey(); //get a new key or login with the existing one
                Application.EnableVisualStyles();
                ThreadStart startTray = new ThreadStart(prepTray);
                Thread traythread = new Thread(startTray);
                traythread.Start();
                Thread t = JobOffPollingThread();
                //stay alive until polling dies
                while (t.IsAlive && continueOn)
                {
                    Thread.Sleep(5000);
                }
            }
            catch (Exception ex)
            {
                //you've just failed at the highest possible level
                //kill yourself and leave a suicide note in the application event log
                LogMessage("Main Program Exception: " + ex.Message+"\r\nGoodbye Cruel World.");
                CloseOut(null, null);
            }
        }
        /// <summary>
        /// I am responsible for creating a thread that shows an alert form. 
        /// </summary>
        private static void JobOffAlertThread()
        {
            ThreadStart start = new ThreadStart(ShowAlertForm);
            Thread thrd = new Thread(start);
            thrd.IsBackground = true;
            thrd.SetApartmentState(ApartmentState.STA);
            thrd.Start();
        }
        /// <summary>
        /// I am responsible for jobbing off a thread that polls the maven cloud for new alerts. 
        /// </summary>
        /// <returns>Returns a thread that allows an observer to watch whether i'm still alive or dead. Schrodinger would be proud.</returns>
        private static Thread JobOffPollingThread()
        {
            ThreadStart start = new ThreadStart(startPolling);
            Thread thrd = new Thread(start);
            thrd.IsBackground = true;
            thrd.SetApartmentState(ApartmentState.STA);
            thrd.Start();
            return thrd;
        }
        /// <summary>
        /// Call to display an alert form which doesnt necessarily conform to the mode in the settings.  
        /// </summary>
        /// <param name="m">The mode for the alert. This doesn't have to match the mode in the settings.</param>
        public static void ShowAlertForm(Settings.AlertMode m)
        {
            if (m == Settings.AlertMode.combo || m == Settings.AlertMode.deskSoft)
            {
                frmAlert frm = new frmAlert(cursettings.fadeSlowness, cursettings.location, url);
                frm.ShowInTaskbar = false;
                frm.Visible = true;
                Application.Run(frm);
            }
            else if (m == Settings.AlertMode.deskHard)
            {
                frmHardAlert frm = new frmHardAlert(url, cursettings.location);
                frm.ShowInTaskbar = false;
                frm.Visible = true;
                Application.Run(frm);
            }
        }
        /// <summary>
        /// Call me to display an alert that conforms to the settings .
        /// </summary>
        private static void ShowAlertForm()
        {
            //if someone just clicked the replay last alert, but there is no previous alert...
            if (url == "")
            {
                return;
            }
            if (cursettings.mode == Settings.AlertMode.combo || cursettings.mode == Settings.AlertMode.deskSoft)
            {
                frmAlert frm = new frmAlert(cursettings.fadeSlowness, cursettings.location, url);
                frm.ShowInTaskbar = false;
                frm.Visible = true;
                Application.Run(frm);
            }
            else if (cursettings.mode == Settings.AlertMode.deskHard)
            {
                frmHardAlert frm = new frmHardAlert(url, cursettings.location);
                frm.ShowInTaskbar = false;
                frm.Visible = true;
                Application.Run(frm);
            }
        }
        /// <summary>
        /// Prepare the system tray for the user. 
        /// </summary>
        private static void prepTray()
        {
            NotifyIcon tray = new NotifyIcon();
            //note that Maven.ico needs to be packaged up with the installer
            string iconpath = System.IO.Path.GetDirectoryName(Application.ExecutablePath)+"\\Maven.ico";
            //MessageBox.Show(iconpath);
            tray.Icon = new System.Drawing.Icon(iconpath);
            ContextMenu ctx = new ContextMenu();

            MenuItem modeitm = new MenuItem("Alert Mode");
            modeitm.MenuItems.Add("Inbox", AlertModeClick);
            modeitm.MenuItems.Add("Mobile", AlertModeClick);
            modeitm.MenuItems.Add("Desktop Soft Alert", AlertModeClick);
            modeitm.MenuItems.Add("Desktop Hard Alert", AlertModeClick);
            modeitm.MenuItems.Add("Combo", AlertModeClick);
            ctx.MenuItems.Add(modeitm);

            MenuItem speeditm = new MenuItem("Soft Alert Fade Slowness");
            speeditm.MenuItems.Add("1", FadeSlownessClick);
            speeditm.MenuItems.Add("2", FadeSlownessClick);
            speeditm.MenuItems.Add("3", FadeSlownessClick);
            speeditm.MenuItems.Add("4", FadeSlownessClick);
            speeditm.MenuItems.Add("5", FadeSlownessClick);
            speeditm.MenuItems.Add("6", FadeSlownessClick);
            speeditm.MenuItems.Add("7", FadeSlownessClick);
            speeditm.MenuItems.Add("8", FadeSlownessClick);
            ctx.MenuItems.Add(speeditm);

            MenuItem locitm = new MenuItem("Alert Location");
            MenuItem vitm = new MenuItem("Vertical");
            vitm.MenuItems.Add("Top", LocationClick);
            vitm.MenuItems.Add("Middle", LocationClick);
            vitm.MenuItems.Add("Bottom", LocationClick);
            locitm.MenuItems.Add(vitm);
            MenuItem hitm = new MenuItem("Horizontal");
            hitm.MenuItems.Add("Left", LocationClick);
            hitm.MenuItems.Add("Center", LocationClick);
            hitm.MenuItems.Add("Right", LocationClick);
            locitm.MenuItems.Add(hitm);
            ctx.MenuItems.Add(locitm);

            //TODO: Actually store the last alert and replay it. Remove dummyAlert. 
            MenuItem itm6 = new MenuItem("Replay Last Alert", LastAlert);
            ctx.MenuItems.Add(itm6);

            MenuItem itmClose = new MenuItem("Exit Maven Tray", CloseOut);
            ctx.MenuItems.Add(itmClose);

            MenuItem itmLogOut = new MenuItem("Log Out", LogOut);
            ctx.MenuItems.Add(itmLogOut);

            tray.ContextMenu = ctx;
            tray.Visible = true;
            Application.Run();
        }
        /// <summary>
        /// Actually does the job of polling the maven cloud for new messages. 
        /// </summary>
        private static void startPolling()
        {

            ServicePointManager.ServerCertificateValidationCallback = new System.Net.Security.RemoteCertificateValidationCallback(AcceptAllCertifications);
            while (continueOn)
            {
                try
                {
                    WebRequest rqst = WebRequest.Create("http://" + cursettings.pollingServer + "/broadcaster/poll?key=" + WindowsDPAPI.Decrypt(EncryptedKey));
                    rqst.Timeout = 600000;
                    HttpWebResponse rsp = (HttpWebResponse)rqst.GetResponse();
                    HttpStatusCode status = rsp.StatusCode;
                    if (status == HttpStatusCode.OK)
                    {
                        Stream dataStream = rsp.GetResponseStream();
                        StreamReader reader = new StreamReader(dataStream);
                        string responseFromServer = reader.ReadToEnd();
                        if (responseFromServer != "[]")
                        {
                            //string alertUrl = responseFromServer.Split(',')[0].Replace("[{\"LINK\": \"", "").Replace("\"", "");
                            string alertUrl = responseFromServer.Replace("[\"", "").Replace("\"]", "");
                            alert("1", "66556", alertUrl);
                        }
                    }
                }
                catch (Exception e)
                {
                    //don't fill up the log with timeouts. but log everything else
                    if (!e.Message.Contains("Timeout"))
                    {
                        LogMessage("Polling Exception: "+e.Message);
                    }
                }
            }
            
        }
        /// <summary>
        /// I'm here simply to force the polling guy to not reject the Maven Cloud Cert. 
        /// </summary>
        public static bool AcceptAllCertifications(object sender, System.Security.Cryptography.X509Certificates.X509Certificate certification, System.Security.Cryptography.X509Certificates.X509Chain chain, System.Net.Security.SslPolicyErrors sslPolicyErrors)
        {
            return true;
        }
        /// <summary>
        /// Fire an alert. 
        /// </summary>
        /// <param name="documentId">The document id of the alert.  Can be safely spoofed. </param>
        /// <param name="patId">The patient ID. Can be spoofed as long as this program isnt responsible for sending an Inbox message. (It is as of when this comment was written.)</param>
        /// <param name="inUrl">The URL of the alert target page. Absolutely essential. Do not spoof.</param>
        private static void alert(string documentId,string patId, string inUrl)
        {
            url = inUrl;
            //Console.WriteLine("Alert now!");
            if (cursettings.mode == Settings.AlertMode.deskSoft || cursettings.mode == Settings.AlertMode.deskHard || cursettings.mode == Settings.AlertMode.combo)
            {
                JobOffAlertThread();
            }
            if (cursettings.mode == Settings.AlertMode.mobile || cursettings.mode == Settings.AlertMode.combo)
            {
                //mobile alert
            }
            if (cursettings.mode == Settings.AlertMode.inbox || cursettings.mode == Settings.AlertMode.combo)
            {
                mail(patId);
            }
        }
   
        /// <summary>
        /// Handle a change to the settings for the alert mode. 
        /// </summary>
        /// <param name="sender">can be null. i don't respect this parameter, but it's required by .net</param>
        /// <param name="e">can be null. i don't respect this parameter, but it's required by .net</param>
        private static void AlertModeClick(object sender, EventArgs e)
        {
            MenuItem itm = (MenuItem)sender;
            switch (itm.Text)
            {
                    //send a message to the clinians inbox in the EMR.
                case "Inbox":
                    cursettings.mode = Settings.AlertMode.inbox;
                    break;
                    //send a message to the clinician's mobile app
                case "Mobile":
                    cursettings.mode = Settings.AlertMode.mobile;
                    break;
                    //send a message to the clinician's desktop, but don't pop up the big browser thing. 
                case "Desktop Soft Alert":
                    cursettings.mode = Settings.AlertMode.deskSoft;
                    break;
                    //send  the message to the desktop and go right to the full alert in the browser. 
                case "Desktop Hard Alert":
                    cursettings.mode = Settings.AlertMode.deskHard;
                    break;
                    //blast the clinician with reckless abandon.
                case "Combo":
                    cursettings.mode = Settings.AlertMode.combo;
                    break;
            }
            cursettings.Save();
        }
        /// <summary>
        /// If the softdesktop alert is set, how fast should it fade away? handle a change to the settings. 
        /// </summary>
        /// <param name="sender">can be null. i don't respect this parameter, but it's required by .net</param>
        /// <param name="e">can be null.  i don't respect this parameter, but it's required by .net</param>
        private static void FadeSlownessClick(object sender, EventArgs e)
        {
            //the options must be convertable to numbers. Every 50ms, the alert will fade (1/slowness)%. 
            //So if the setting is 1, we'll fade 1% every 50ms 
            //if the setting is 10, we'll only fade .1% every 50ms
            MenuItem itm = (MenuItem)sender;
            try
            {
                cursettings.fadeSlowness = Convert.ToDouble(itm.Text);
                cursettings.Save();
            }
            catch { LogMessage("An invalid menu option was selected for the fade slowness."); }
        }
        /// <summary>
        /// Where does the alert come up on the screen?
        /// </summary>
        /// <param name="sender">this can be null. i don't look at it, but it's required by .net</param>
        /// <param name="e">this can be null. i don't look at it, but .net wants it</param>
        private static void LocationClick(object sender, EventArgs e)
        {
            //There's a vertical section and a horizontal section that have mutually exclusive options. 
            //(Note that vertical used "middle" and horizontal uses "Center" to ensure that they are mutally exclusive.
            //This is due to laziness and the desire to handle both vertical and horizontal settings in this one function.)
            //we split the screen into a tic-tac-toe board and allow you to choose which box the alert should try to fall into.
            MenuItem itm = (MenuItem)sender;
            switch (itm.Text)
            {
                //First look at the vertical settings. The vertical settings can be T, M, or B and they comprise the FIRST character of the "setting" string
                case "Top":
                    cursettings.location = "T" + cursettings.location.Substring(1);
                    break;
                case "Middle":
                    cursettings.location = "M" + cursettings.location.Substring(1);
                    break;
                case "Bottom":
                    cursettings.location = "B" + cursettings.location.Substring(1);
                    break;
                //Next look at the horizontal settings. The horizontal settings can be L, C, or R and they comprise the SECOND character of the "setting" string
                case "Left":
                    cursettings.location = cursettings.location.Substring(0, 1) + "L";
                    break;
                case "Center":
                    cursettings.location = cursettings.location.Substring(0, 1) + "C";
                    break;
                case "Right":
                    cursettings.location = cursettings.location.Substring(0, 1) + "R";
                    break;
            }
            //Hey, it works. and it's well documented. Don't knock it. 
            //Once the setting is set, it will be handled (or ignored) by the forms themselves. 

            cursettings.Save();//save it
        }
        /// <summary>
        /// replays the previous alert
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        static void LastAlert(object sender, EventArgs e)
        {
            alert("", "", url);
        }
        /// <summary>
        /// TODO: Replace me with a web service call to the cloud. 
        /// </summary>
        /// <param name="patId">The patient id for whom this message is relevant. </param>
        static void mail(string patId)
        {
            string serviceUser = "MavenPathways";
            string servicePwd = "MavenPathways123!!";
            string appName = "MavenPathways.TestApp";
            string appUserName = "cliffhux";
            string namepro=getPatientNameAndPronoun(patId);
            string name=namepro.Split('|')[0];
            string pronoun=namepro.Split('|')[1];
            Unity.UnityServiceClient mailsvc = new Unity.UnityServiceClient();
            string mailtoken = mailsvc.GetSecurityToken(serviceUser, servicePwd);
            DataSet ds = mailsvc.Magic("SaveTask",       // Action    
                                     appUserName,            // UserID    
                                     appName,                // Appname   
                                     patId,                     // PatientID 
                                     mailtoken,                  // Token     
                                     "Send Chart",   // Parameter1 @SINCE
                                     appUserName,                     // Parameter2
                                     "",                     // Parameter3
                                     "During your appointment with "+name+" today, Maven detected that "+pronoun+" matched a pathway from the AUA.\r\nPlease log into Maven to view the protocol.",                     // Parameter4
                                     "AUA Pathway detected for your patient. Please review.",                     // Parameter5
                                     "",                     // Parameter6
                                     null);                  // data                // data 
        }
        /// <summary>
        /// TODO: Remove me as soon as the mail() function is handled in the cloud. 
        /// </summary>
        /// <param name="patId"></param>
        /// <returns></returns>
        static string getPatientNameAndPronoun(string patId)
        {
            string serviceUser = "MavenPathways";
            string servicePwd = "MavenPathways123!!";
            string appName = "MavenPathways.TestApp";
            string appUserName = "cliffhux";
            Unity.UnityServiceClient unitySvc = new Unity.UnityServiceClient();
            string token = unitySvc.GetSecurityToken(serviceUser, servicePwd);
            DataSet ds = unitySvc.Magic("GetPatient",       // Action    
                                     appUserName,            // UserID    
                                     appName,                // Appname   
                                     patId,                     // PatientID 
                                     token,                  // Token     
                                     "",   // Parameter1 @SINCE
                                     "",                     // Parameter2
                                     "",                     // Parameter3
                                     "",
                                     "",
                                     "",                     // Parameter6
                                     null);                  // data                // data 
            DataTableReader reader=ds.CreateDataReader();
            reader.Read();
            string name= reader.GetString(2)+" "+reader.GetString(1);
            string pronoun = "he";
            try
            {
                if (reader.GetString(4) == "F")
                {
                    pronoun = "she";
                }

            }
            catch { }
            return name + "|" + pronoun;
        }
        /// <summary>
        /// On a major error, or when the user request it, I will kill my own process and all child processes. 
        /// </summary>
        /// <param name="sender">can be null. required by .net</param>
        /// <param name="e">can be null. required by .net</param>
        static void CloseOut(object sender, EventArgs e)
        {
            try
            {
                cursettings.Save();
                //inform everyone that we're closing out
                continueOn = false;
                //close out gracefully
                Application.Exit();
            }
            catch(Exception ex)
            {
                //darn it. maybe i'll die anyway. who knows. At least log the message to inform the user that if i'm still running, they need to resort to task manager. 
                LogMessage("Error closing the application. Please try task manager if the process is still running.\r\n"+ex.Message);
            }
           
        }
        /// <summary>
        /// Log out and also clear the key stored in the registry so that next time, you need to log in. 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        static void LogOut(object sender, EventArgs e)
        {
            //clear the setting
            Authenticator.ClearLoginSettings();
            //end the process. consider not ending, but instead calling authenticator.login. 
            CloseOut(null, null);
        }
        /// <summary>
        /// handle logging debug messages
        /// </summary>
        /// <param name="msg">the entire message that should be logged.</param>
        public static void LogMessage(string msg)
        {
            try
            {
                //HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\eventlog\Application\MavenDesktop must exist  
                //Created during install
                EventLog el = new EventLog("Application");
                el.Source = "MavenDesktop";
                el.WriteEntry(msg, System.Diagnostics.EventLogEntryType.Warning,234);
                //TODO: handle an actual registered event id. now it's event 0 which is getting a "desc cannot be found" message
                //http://www.codeproject.com/Articles/4153/Getting-the-most-out-of-Event-Viewer
            }
            catch
            {
                //TODO: Call this function recursively if writing to the error log fails. Just kidding...
            }
        }
    }
}
