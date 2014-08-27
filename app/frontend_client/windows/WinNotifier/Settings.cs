using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Win32;

namespace MavenAsDemo
{
    class Settings
    {
        public AlertMode mode = AlertMode.deskSoft;
        public double fadeSlowness = 3;
        public string location = "BR";
        public string pollingServer = "162.222.177.174"; //TODO: Update this to be actual server default. Also install the default via the installer. 
        public string user = System.Uri.EscapeDataString(System.Environment.UserName);
        public string machine = System.Uri.EscapeDataString(System.Environment.MachineName);
        public string os = System.Uri.EscapeDataString(System.Environment.OSVersion.VersionString);

        /// <summary>
        /// The different ways to alert people of stuff. 
        /// </summary>
        public enum AlertMode
        {
            inbox, mobile, deskSoft, deskHard, combo
        };

        public Settings()
        {
            getMode();
            getFadeSlowness();
            getLocation();
            getServer();
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
            //else, use the default
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
    }
}
