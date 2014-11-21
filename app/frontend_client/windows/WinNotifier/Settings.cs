using System;
using System.Collections.Generic;
//using System.Linq;
using System.Text;
//using System.Threading.Tasks;
using Microsoft.Win32;
using System.Xml;
using System.Windows.Forms;

namespace MavenAsDemo
{
    class Settings
    {
        public AlertMode mode = AlertMode.deskSoft;
        public double fadeSlowness = 3;
        public string location = "BR";
        public string pollingServer = "qa.mavenmedical.net"; //TODO: Update this to be actual server default. Also install the default via the installer. 
        public string osUser = System.Uri.EscapeDataString(System.Environment.UserName);
        public string machine = System.Uri.EscapeDataString(System.Environment.MachineName);
        public string os = System.Uri.EscapeDataString(System.Environment.OSVersion.VersionString);
        public string custId = "";
        public string mavenuserid = "";
        public string softwareVersion = "";

        /// <summary>
        /// The different ways to alert people of stuff. 
        /// </summary>
        public enum AlertMode
        {
            inbox, mobile, deskSoft, deskHard, combo, browser
        };
        private void PrepBrowserSettings()
        {
            WebBrowser versTest = new WebBrowser();
            int ievers=versTest.Version.Major;
            int writeval = 0;
            if (ievers == 7) { writeval = 7000; }
            else if (ievers == 8) { writeval = 8888; }
            else if (ievers == 9) { writeval = 9999; }
            else if (ievers == 10) { writeval = 10001; }
            else if (ievers == 11) { writeval = 11001; }
            if (writeval > 0)
            {
                try
                {
                    RegistryKey iekey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_BROWSER_EMULATION", true);
                    if (iekey == null)
                    {
                        iekey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\Microsoft\\Internet Explorer\\Main\\FeatureControl\\FEATURE_BROWSER_EMULATION", RegistryKeyPermissionCheck.ReadWriteSubTree);
                    }
                    iekey.SetValue("MavenDesktop.exe", writeval);
                }
                catch
                {
                    Program.LogMessage("Unable to set default emulation mode for ie version "+ievers);
                }
            }

        }
        
        public Settings()
        {
            PrepBrowserSettings();
            getMode();
            getFadeSlowness();
            getLocation();
            getServer();
            getCustomer();
            getCurVers();
        }
        public void getCurVers()
        {
            //look to the registry which should be where this is stored
            RegistryKey settingKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", false);
            if (settingKey != null && settingKey.GetValue("version") != null)
            {
                //if you found the key, then by all means use it
                softwareVersion = (string)settingKey.GetValue("version");
            }
        }
        /// <summary>
        /// Saves the settings to the registry
        /// </summary>
        public void Save()
        {
            try
            {
                RegistryKey settingsKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", true);
                if (settingsKey == null)
                {
                    settingsKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", RegistryKeyPermissionCheck.ReadWriteSubTree);
                }
                settingsKey.SetValue("server", pollingServer);
                settingsKey.SetValue("location", location);
                settingsKey.SetValue("FadeSlowness", fadeSlowness);
                settingsKey.SetValue("mode", mode);
            }
            catch (Exception ex)
            {
                Program.LogMessage("Error savings settings.\r\n" + ex.Message);
            }
        }
        /// <summary>
        /// Gets the polling server from the registry
        /// </summary>
        private void getServer()
        {
            //look to the registry which should be where this is stored
            RegistryKey settingKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", false);
            if (settingKey != null && settingKey.GetValue("server") != null)
            {
                //if you found the key, then by all means use it
                pollingServer = (string)settingKey.GetValue("server");

            }
            //look for an override, else use the default
            try
            {
                XmlDocument xdoc = new XmlDocument();
                xdoc.Load(System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location) + "\\OverrideSettings.xml");//look to the current directory for the override
                XmlNode custnode = xdoc.GetElementsByTagName("server")[0];
                pollingServer = custnode.InnerText.Trim();
                //write to the registry
                RegistryKey custKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", RegistryKeyPermissionCheck.ReadWriteSubTree);
                custKey.SetValue("server", pollingServer);
            }
            catch { }
        }
        /// <summary>
        /// Gets the Location from the registry
        /// </summary>
        private void getLocation()
        {
            //look to the registry which should be where this is stored
            RegistryKey settingKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", false);
            if (settingKey != null && settingKey.GetValue("location") != null)
            {
                //if you found the key, then by all means use it
                location = (string)settingKey.GetValue("location");

            }
            //else, use the default
        }
        /// <summary>
        /// Gets the fadeSlowness from the registry
        /// </summary>
        private void getFadeSlowness()
        {
            //look to the registry which should be where this is stored
            RegistryKey settingKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", false);
            if (settingKey != null && settingKey.GetValue("FadeSlowness") != null)
            {
                //if you found the key, then by all means use it
                fadeSlowness = Convert.ToInt32((string) settingKey.GetValue("FadeSlowness"));

            }
            //else, use the default
        }
      
        /// <summary>
        /// Gets the alert mode from the registry
        /// </summary>
        private void getMode()
        {
            //look to the registry which should be where this is stored
            RegistryKey settingKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", false);
            if (settingKey != null && settingKey.GetValue("mode") != null)
            {
                //if you found the key, then by all means use it
                string strMode=(string)settingKey.GetValue("mode");
                mode = (AlertMode)Enum.Parse(typeof(AlertMode), strMode);
            }
            //else, use the default
        }
        /// <summary>
        /// sets the customer id
        /// </summary>
        private void getCustomer()
        {
            //look to the registry which should be where this is stored
            RegistryKey settingKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", false);
            if (settingKey != null && settingKey.GetValue("CustomerId") != null)
            {
                //if you found the key, then by all means use it
                custId = (string)settingKey.GetValue("CustomerId");
            }
            //if no customer in registry, and no override setting, then throw an exception and close out
            try
            {
                XmlDocument xdoc = new XmlDocument();
                xdoc.Load(System.IO.Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location) + "\\OverrideSettings.xml");//look to the current directory for the override
                XmlNode custnode = xdoc.GetElementsByTagName("customerId")[0];
                custId = custnode.InnerText.Trim();
                //write to the registry
                RegistryKey custKey = Registry.CurrentUser.CreateSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Settings\\", RegistryKeyPermissionCheck.ReadWriteSubTree);
                custKey.SetValue("CustomerId", custId);
            }
            
            catch 
            {
                //didnt get an override setting
            }
            //if there was nothing in the registry OR override settings, close out. can't continue. 
            if (custId == "")
            {
                Program.LogMessage("Error obtaining customer id");
                Exception ex = new Exception("No customer ID found in the registry or in OverrideSettings.xml");
                throw ex;
            }
        }
    }
}
