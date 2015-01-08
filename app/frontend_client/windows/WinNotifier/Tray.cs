using System;
using System.Collections.Generic;
using System.Text;
using System.Windows.Forms;
using System.Threading;
using System.Net;

namespace MavenAsDemo
{
    class Tray
    {
        private Thread mythread;
        private string iconpath = System.IO.Path.GetDirectoryName(Application.ExecutablePath) + "\\Maven.ico";
        private NotifyIcon tray;
        public Tray()
        {
            mythread = starttray();
        }
        private Thread starttray()
        {
            ThreadStart start = new ThreadStart(run);
            Thread thrd = new Thread(start);
            thrd.IsBackground = true;
            thrd.SetApartmentState(ApartmentState.STA);
            thrd.Start();
            return thrd;
        }
        public void SetDisconnected()
        {
            iconpath = System.IO.Path.GetDirectoryName(Application.ExecutablePath) + "\\disconnect.ico";
            tray.Icon = new System.Drawing.Icon(iconpath);
        }
        public void SetConnected()
        {
            iconpath = System.IO.Path.GetDirectoryName(Application.ExecutablePath) + "\\Maven.ico";
            tray.Icon = new System.Drawing.Icon(iconpath);
        }
        private void unloadTray()
        {
            tray.Icon = null;
            tray.Dispose();
        }
        public void Close()
        {
            unloadTray();
            Application.Exit();
        }
        private void run()
        {
            tray = new NotifyIcon();
            //note that Maven.ico needs to be packaged up with the installer
            //MessageBox.Show(iconpath);
            tray.Icon = new System.Drawing.Icon(iconpath);
            tray.Text = "Maven Desktop - " + Program.cursettings.softwareVersion;


            tray.ContextMenu = getContextMenu();
            tray.Visible = true;
            Application.Run();
        }
        private ContextMenu getContextMenu()
        {
            ContextMenu ctx = new ContextMenu();

            MenuItem modeitm = new MenuItem("Alert Mode");
            //modeitm.MenuItems.Add("Mobile", AlertModeClick);
            modeitm.MenuItems.Add("Desktop Soft Alert", AlertModeClick);
            modeitm.MenuItems.Add("Desktop Hard Alert", AlertModeClick);
            modeitm.MenuItems.Add("Inbox", AlertModeClick);
            if (Program.cursettings.mode == Settings.AlertMode.deskSoft) { modeitm.MenuItems[0].Checked = true; }
            else if (Program.cursettings.mode == Settings.AlertMode.deskHard) { modeitm.MenuItems[1].Checked = true; }
            else if (Program.cursettings.mode == Settings.AlertMode.inbox) { modeitm.MenuItems[2].Checked = true; }
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
            int i = Convert.ToInt16( Program.cursettings.fadeSlowness - 1);
            speeditm.MenuItems[i].Checked = true;
            ctx.MenuItems.Add(speeditm);

            MenuItem locitm = new MenuItem("Alert Location");
            MenuItem vitm = new MenuItem("Vertical");
            vitm.MenuItems.Add("Top", LocationClick);
            vitm.MenuItems.Add("Middle", LocationClick);
            vitm.MenuItems.Add("Bottom", LocationClick);
            if (Program.cursettings.location.StartsWith("T")) { vitm.MenuItems[0].Checked = true; }
            else if (Program.cursettings.location.StartsWith("M")) { vitm.MenuItems[1].Checked = true; }
            else if (Program.cursettings.location.StartsWith("B")) { vitm.MenuItems[2].Checked = true; }
            locitm.MenuItems.Add(vitm);
            MenuItem hitm = new MenuItem("Horizontal");
            hitm.MenuItems.Add("Left", LocationClick);
            hitm.MenuItems.Add("Center", LocationClick);
            hitm.MenuItems.Add("Right", LocationClick);
            if (Program.cursettings.location.EndsWith("L")) { hitm.MenuItems[0].Checked = true; }
            else if (Program.cursettings.location.EndsWith("C")) { hitm.MenuItems[1].Checked = true; }
            else if (Program.cursettings.location.EndsWith("R")) { hitm.MenuItems[2].Checked = true; }
            locitm.MenuItems.Add(hitm);
            ctx.MenuItems.Add(locitm);

            MenuItem itm6 = new MenuItem("Replay Last Alert", LastAlert);
            ctx.MenuItems.Add(itm6);

            MenuItem itmClose = new MenuItem("Exit Maven Tray", CloseOut);
            ctx.MenuItems.Add(itmClose);

            string strLogout = ("Log Out (" + Authenticator.GetUserName() + ")").Replace(" ()", "");
            MenuItem itmLogOut = new MenuItem(strLogout, LogOut);
            ctx.MenuItems.Add(itmLogOut);
            return ctx;
        }
        private void ShowTray()
        {
            Application.Run();
        }
        private void CloseOut(object sender, EventArgs e)
        {
            Program.CloseOut(null, null);
            mythread.Abort();
            this.Close();
        }
        /// <summary>
        /// Log out and also clear the key stored in the registry so that next time, you need to log in. 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        void LogOut(object sender, EventArgs e)
        {
            //clear the setting
            Authenticator.ClearLoginSettings();
            //end the process. consider not ending, but instead calling authenticator.login. 
            CloseOut(null, null);
        }
        /// <summary>
        /// If the softdesktop alert is set, how fast should it fade away? handle a change to the settings. 
        /// </summary>
        /// <param name="sender">can be null. i don't respect this parameter, but it's required by .net</param>
        /// <param name="e">can be null.  i don't respect this parameter, but it's required by .net</param>
        private void FadeSlownessClick(object sender, EventArgs e)
        {
            //the options must be convertable to numbers. Every 50ms, the alert will fade (1/slowness)%. 
            //So if the setting is 1, we'll fade 1% every 50ms 
            //if the setting is 10, we'll only fade .1% every 50ms
            MenuItem itm = (MenuItem)sender;
            try
            {
                Program.cursettings.fadeSlowness = Convert.ToDouble(itm.Text);
                Program.cursettings.Save();
                tray.ContextMenu = getContextMenu();
            }
            catch { Logger.LogLocal("An invalid menu option was selected for the fade slowness."); }
        }
        /// <summary>
        /// Where does the alert come up on the screen?
        /// </summary>
        /// <param name="sender">this can be null. i don't look at it, but it's required by .net</param>
        /// <param name="e">this can be null. i don't look at it, but .net wants it</param>
        private void LocationClick(object sender, EventArgs e)
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
                    Program.cursettings.location = "T" + Program.cursettings.location.Substring(1);
                    tray.ContextMenu = getContextMenu();
                    break;
                case "Middle":
                    Program.cursettings.location = "M" + Program.cursettings.location.Substring(1);
                    tray.ContextMenu = getContextMenu();
                    break;
                case "Bottom":
                    Program.cursettings.location = "B" + Program.cursettings.location.Substring(1);
                    tray.ContextMenu = getContextMenu();
                    break;
                //Next look at the horizontal settings. The horizontal settings can be L, C, or R and they comprise the SECOND character of the "setting" string
                case "Left":
                    Program.cursettings.location = Program.cursettings.location.Substring(0, 1) + "L";
                    tray.ContextMenu = getContextMenu();
                    break;
                case "Center":
                    Program.cursettings.location = Program.cursettings.location.Substring(0, 1) + "C";
                    tray.ContextMenu = getContextMenu();
                    break;
                case "Right":
                    Program.cursettings.location = Program.cursettings.location.Substring(0, 1) + "R";
                    tray.ContextMenu = getContextMenu();
                    break;
            }
            //Hey, it works. and it's well documented. Don't knock it. 
            //Once the setting is set, it will be handled (or ignored) by the forms themselves. 

            Program.cursettings.Save();//save it
        }
        /// <summary>
        /// replays the previous alert
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        void LastAlert(object sender, EventArgs e)
        {
            Program.alert("", "", Program.url);
        }
        /// <summary>
        /// Handle a change to the settings for the alert mode. 
        /// </summary>
        /// <param name="sender">can be null. i don't respect this parameter, but it's required by .net</param>
        /// <param name="e">can be null. i don't respect this parameter, but it's required by .net</param>
        private void AlertModeClick(object sender, EventArgs e)
        {
            MenuItem itm = (MenuItem)sender;
            switch (itm.Text)
            {
                //send a message to the clinians inbox in the EMR.
                case "Inbox":
                    Program.cursettings.mode = Settings.AlertMode.inbox;
                    SetAlertMode("ehrinbox", "off");
                    tray.ContextMenu = getContextMenu();
                    break;
                //send a message to the clinician's mobile app
                case "Mobile":
                    Program.cursettings.mode = Settings.AlertMode.mobile;
                    SetAlertMode("mobile", "off");
                    tray.ContextMenu = getContextMenu();
                    break;
                //send a message to the clinician's desktop, but don't pop up the big browser thing. 
                case "Desktop Soft Alert":
                    Program.cursettings.mode = Settings.AlertMode.deskSoft;
                    SetAlertMode("desktop", "off");
                    tray.ContextMenu = getContextMenu();
                    break;
                //send  the message to the desktop and go right to the full alert in the browser. 
                case "Desktop Hard Alert":
                    Program.cursettings.mode = Settings.AlertMode.deskHard;
                    SetAlertMode("desktop", "off");
                    tray.ContextMenu = getContextMenu();
                    break;
                //blast the clinician with reckless abandon.
                case "Combo":
                    Program.cursettings.mode = Settings.AlertMode.combo;
                    SetAlertMode("desktop", "off");
                    tray.ContextMenu = getContextMenu();
                    break;
                //if issue with displaying in the hard alert window, then drop to the browser. 
                case "Default Browser":
                    Program.cursettings.mode = Settings.AlertMode.browser;
                    SetAlertMode("desktop", "off");
                    tray.ContextMenu = getContextMenu();
                    break;
            }
            Program.cursettings.Save();
        }
        /// <summary>
        /// Tells the cloud what alert mode to use
        /// </summary>
        /// <param name="primary">"off", "desktop", "mobile", "ehrinbox"</param>
        /// <param name="secondary">Used if you stop polling. "off", "desktop", "mobile", "ehrinbox"</param>
        public void SetAlertMode(string primary, string secondary)
        {
            string rqstUrl = "https://" + Program.cursettings.pollingServer + "/broadcaster/notifypref?userAuth=" + WindowsDPAPI.Decrypt(Program.EncryptedKey)
                        + "&notify1=" + primary + "&notify2=" + secondary
                         + "&osUser=" + Program.cursettings.osUser + "&machine=" + Program.cursettings.machine + "&osVersion=" + Program.cursettings.os
                        + "&user=" + Authenticator.getMavenUserName() + "&customer_id=" + Program.cursettings.custId
                        + "&provider=" + Authenticator.getProviderId() + "&roles[]=notification&userid=" + Authenticator.getMavenUserID();
            try
            {
                WebRequest rqst = WebRequest.Create(rqstUrl);
                rqst.Timeout = 60000;
                rqst.GetResponse();
                rqst.Abort();
                rqst = null;
            }

            catch (Exception e)
            {
                Logger.Log("Error switching alert mode to \"" + primary + "\"\"\r\n" + e.Message, "ModeSwitch");
            }
        }
    }

}
