using System;
using System.Collections.Generic;
using System.Threading;
using System.Windows.Forms;
using System.Data;
using System.Text.RegularExpressions;
using System.Text;
using System.Net;
using System.IO;
using System.Diagnostics;

namespace MavenAsDemo
{
    static class Program
    {
        public static string url = "";
        public static Guid serialnum = Guid.NewGuid();
        private static bool continueOn = true;
        public static byte[] EncryptedKey = null;
        public static Settings cursettings;
        public static Tray mytray;
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {


            //first of all, don't do nuthin if there's already a mavendesktop running
            if (isAlreadyRunning())
            {
                //for citrix, ignore this. 
                //return;
            }
            try
            {
                Application.SetCompatibleTextRenderingDefault(false);
                cursettings = new Settings();
                Authenticator.HandleLoginStickiness(); //clear the login settings if we shouldn't be using them
                EncryptedKey = Authenticator.GetEncryptedAuthKey(); //get a new key or login with the existing one
                if (EncryptedKey == null) { return; } //if you came back with no key, then you haven't successfully logged in. quit. 

                cursettings.logEnvironment();
                Application.EnableVisualStyles();
                mytray = new Tray();
                Thread t = JobOffPollingThread();
                if (cursettings.mode == Settings.AlertMode.deskSoft || cursettings.mode == Settings.AlertMode.deskHard) //if we're in desktop mode, double check that we're set to desktop,off
                {
                    try
                    {
                        mytray.SetAlertMode("desktop", "off");
                    }
                    catch { }//meh, at least we tried
                }
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
                Logger.Log("Main Program Exception: " + ex.Message, "Main Program Exception");
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
                frm.ShowInTaskbar = true;
                frm.Visible = true;
                frm.TopMost = false;
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
                Logger.Log("Displaying soft alert form", "AlertFormDisplay");
                frmAlert frm = new frmAlert(cursettings.fadeSlowness, cursettings.location, url);
                frm.ShowInTaskbar = false;
                frm.Visible = true;
                frm.TopMost = true;
                Application.Run(frm);
            }
            else if (cursettings.mode == Settings.AlertMode.deskHard)
            {
                Logger.Log("Displaying hard alert form", "AlertFormDisplay");
                frmHardAlert frm = new frmHardAlert(url, cursettings.location);
                frm.ShowInTaskbar = true;
                frm.Visible = true;
                frm.TopMost = true;
                Application.Run(frm);
            }
        }

        /// <summary>
        /// Actually does the job of polling the maven cloud for new messages. 
        /// </summary>
        private static void startPolling()
        {
            string lastExceptionMessage = "";
            ServicePointManager.ServerCertificateValidationCallback = new System.Net.Security.RemoteCertificateValidationCallback(AcceptAllCertifications);
            AllScriptsProLoginTracker tracker = new AllScriptsProLoginTracker(Authenticator.getMavenUserName());
            tracker.Start();
            /////debug only 
            //Thread.Sleep(50000);
            //alert("", "", "https://dev.mavenmedical.net/#/pathway/1022/node/1/patient/66632/2014-10-18");


            while (continueOn)
            {

                try
                {
                    //if you're not even logged in, then just sit around and wait for a while
                    if (!tracker.isEmrUserLoggedIn)
                    {
                        System.Threading.Thread.Sleep(10000);
                    }
                    else //ok, you're logged in. poll. 
                    {
                        string rqstUrl = "https://" + cursettings.pollingServer + "/broadcaster/poll?userAuth=" + WindowsDPAPI.Decrypt(EncryptedKey)
                            + "&osUser=" + cursettings.osUser + "&machine=" + cursettings.machine + "&osVersion=" + cursettings.os
                            + "&user=" + Authenticator.getMavenUserName() + "&customer_id=" + cursettings.custId
                            + "&provider=" + Authenticator.getProviderId() + "&roles[]=notification&userid=" + Authenticator.getMavenUserID() + "&ver=" + cursettings.softwareVersion;
                        WebRequest rqst = WebRequest.Create(rqstUrl);
                        rqst.Timeout = 600000;
                        HttpWebResponse rsp = (HttpWebResponse)rqst.GetResponse();
                        HttpStatusCode status = rsp.StatusCode;
                        if (status == HttpStatusCode.OK)
                        {
                            mytray.SetConnected();
                            Stream dataStream = rsp.GetResponseStream();
                            StreamReader reader = new StreamReader(dataStream);
                            string responseFromServer = reader.ReadToEnd();
                            if (responseFromServer != "[]")
                            {
                                //string alertUrl = responseFromServer.Split(',')[0].Replace("[{\"LINK\": \"", "").Replace("\"", "");
                                string alertUrl = responseFromServer.Replace("[\"", "").Replace("\"]", "");
                                alert("", "", alertUrl);
                            }
                        }
                    }
                }
                catch (Exception e)
                {
                    //don't fill up the log with timeouts. but log everything else
                    //also don't log the exception multiple multiple times. only log it if it is a new exception
                    if (!e.Message.Contains("Timeout") && e.Message != lastExceptionMessage)
                    {
                        Logger.Log("Polling Exception: " + e.Message, "Polling exception");
                    }
                    if (!e.Message.Contains("Timeout"))
                    {
                        Thread.Sleep(10000); //we just got an error. wait a few seconds before going on unless it was a timeout (which could be normal if there is no alert). 
                    }
                    //if we got an "unauthorized", then simply re-login
                    if (e.Message.Contains("Unauthorized"))
                    {
                        //this next line is to FORCE a new login and not to get a new session key with the saved oauth token. TODO: review periodically. 
                        Authenticator.ClearLoginSettings();
                        checkAuth(); //ensure you haven't timed out
                    }
                    if (e.Message.Contains("Unable to connect"))
                    {
                        mytray.SetDisconnected();
                    }
                    lastExceptionMessage = e.Message;
                }
            }
            //continueon=false. stop the tracker and exit gracefully
            tracker.Stop();
            
        }
        /// <summary>
        /// Checks for token expiration and re-prompts for a login if expired
        /// </summary>
        private static void checkAuth()
        {
            //if the key is valid, return without doing anything
            //otherwise, prompt for a new login IN THE CURRENT THREAD. don't job off, or it will prompt for lots of login forms. 
            //all of this logic is currently handled in the authenticator.
            url = ""; //clear people out from replaying the previous alert.
            EncryptedKey = Authenticator.GetEncryptedAuthKey("Login Timeout");
            if (EncryptedKey == null)
            {
                continueOn = false;
                CloseOut(null, null);
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
        public static void alert(string documentId, string patId, string inUrl)
        {
            url = inUrl.Replace("http:", "https:");
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
                //mail handled by the cloud. nothing to do
                //mail(patId);
            }
        }
        /// <summary>
        /// On a major error, or when the user request it, I will kill my own process and all child processes. 
        /// </summary>
        /// <param name="sender">can be null. required by .net</param>
        /// <param name="e">can be null. required by .net</param>
        public static void CloseOut(object sender, EventArgs e)
        {
            try
            {
                cursettings.Save();
                //inform everyone that we're closing out
                continueOn = false;
                //close the tray
                mytray.Close();
                //close out gracefully
                Application.Exit();
            }
            catch (Exception ex)
            {
                //darn it. maybe i'll die anyway. who knows. At least log the message to inform the user that if i'm still running, they need to resort to task manager. 
                Logger.Log("Error closing the application. Please try task manager if the process is still running.\r\n" + ex.Message, "CloseOutError");
            }

        }


        /// <summary>
        /// checks to see if the maven notifier is already running.
        /// </summary>
        static bool isAlreadyRunning()
        {
            Process[] pname = Process.GetProcessesByName("MavenDesktop");
            if (pname.Length < 2)
            {
                return false;
            }
            else
            {
                return true;
            }
        }
    }
}
