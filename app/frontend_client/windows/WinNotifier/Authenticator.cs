using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Win32;

namespace MavenAsDemo
{
    /// <summary>
    /// handles authentication
    /// </summary>
    class Authenticator
    {
        /// <summary>
        /// Gets a key encrypted with DPAPI to use in calls to the cloud. 
        /// </summary>
        /// <returns>an encrypted byte array representing the key. call the windowsDPAPI decrypion method to use in a url.</returns>
        public static byte[] GetEncryptedAuthKey()
        { 
            byte[] key = null;
            //look to the registry which should be where this is usually stored
            RegistryKey authKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", false);
            if (authKey != null && authKey.GetValue("Auth") != null)
            {
                

                //if you found the key and it is ok to use it, then by all means use it
                key= (byte[])authKey.GetValue("Auth");
                
            }
            //if you found no key in the registry, or you found a key that isnt valid, then prompt for a login 
            if (!isKeyValidOnServer(key))
            {
                //prompt for a new login
                PromptNewLogin();
                //the login will save the key to the registry. 
                //come back here recursively until the key is valid
                key = GetEncryptedAuthKey();
            }
            //return the key
            return key;
            //TODO: clear the auth registry on exit if the user doesnt want to "stay signed in" 
        }
        /// <summary>
        /// clear the login settings to log out. 
        /// </summary>
        public static void ClearLoginSettings()
        {
            try
            {
                RegistryKey authKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", true);
                authKey.DeleteValue("Auth");
            }
            catch(Exception ex) {Program.LogMessage("Authenticator Error: Could not clear the authkey or authkey registry item doesn't exist.\r\n"+ex.Message); }
        }
        /// <summary>
        /// Check with the maven cloud to see if the key is valid
        /// </summary>
        /// <param name="key">The encrypted byte array for the key</param>
        /// <returns>"True" if the key is valid. Else false.</returns>
        private static bool isKeyValidOnServer(byte[] key)
        {
            //if there's no token, automatically reprompt without asking the server. 
            //sort of client side validation. 
            if (key == null || key.Length == 0)
            {
                return false;
            }
            else
            {
                //TODO: Actually validate the key with the server
                return true;
            }
        }
        /// <summary>
        /// show the login screen. 
        /// </summary>
        private static void PromptNewLogin()
        {
            //currently just saving the username to the registry. 
            //TODO: Actually check the user/password with the cloud and save the returned key to the registry
            frmLogin f = new frmLogin("Please Login to Maven");
            f.Visible = true;
            System.Windows.Forms.Application.Run(f);
        }
        public static void HandleLoginStickiness()
        {
            //look to the registry which should be where this is usually stored
            RegistryKey authKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", false);
            if (authKey != null && authKey.GetValue("Auth") != null)
            {
                //the first thing to do is check if we're supposed to use the saved login. If not, clear whatever's there.
                try
                {
                    string stick = (string)authKey.GetValue("LoginStick");
                    if (stick == "False")
                    {
                        ClearLoginSettings();
                    }
                }
                catch
                {
                    //if no instructions provided, assume logout otherwise, keep whatever's there. 
                    ClearLoginSettings();
                }
            }
        }
    }
}
