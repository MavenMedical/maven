using System;
using System.Collections.Generic;
//using System.Linq;
using System.Text;
//using System.Threading.Tasks;
using Microsoft.Win32;
using System.Net;
using System.IO;

namespace MavenAsDemo
{
    /// <summary>
    /// handles authentication
    /// </summary>
    class Authenticator
    {
        public static bool quitLogin = false;
        private static byte[] encryptedSessionKey;
        /// <summary>
        /// Gets a key encrypted with DPAPI to use in calls to the cloud. 
        /// </summary>
        /// <returns>an encrypted byte array representing the key. call the windowsDPAPI decrypion method to use in a url.</returns>
        public static byte[] GetEncryptedAuthKey()
        {
            return GetEncryptedAuthKey("Please Login to Maven");
        }
        /// <summary>
        /// Gets a key encrypted with DPAPI to use in calls to the cloud. 
        /// </summary>
        /// <param name="promptMessage">a SHORT message to use in promping the user for credentials</param>
        /// <returns>an encrypted byte array representing the key. call the windowsDPAPI decrypion method to use in a url.</returns>
        public static byte[] GetEncryptedAuthKey(string promptMessage)
        {
            if (quitLogin)
            {
                //if we want to cancel out of the login process, this will stop the recursive login prompting
                ClearLoginSettings();
                return null;
            }
            byte[] key = null;
            //look to the registry which should be where this is usually stored
            RegistryKey authKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", false);
            if (authKey != null && authKey.GetValue("Auth") != null)
            {
                //if you found the key and it is ok to use it, then by all means use it
                key = (byte[])authKey.GetValue("Auth");

            }
            //if you found no key in the registry, or you found a key that isnt valid, then prompt for a login 
            if (!isKeyValidOnServer(key))
            {
                //prompt for a new login
                PromptNewLogin(promptMessage);
                //the login will save the key to the registry. 
                //come back here recursively until the key is valid
                key = GetEncryptedAuthKey();
                if (quitLogin)
                {
                    //if we want to cancel out of the login process, this will stop the recursive login prompting
                    ClearLoginSettings();
                    return null;
                }
            }
            //return the key
            return encryptedSessionKey;
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
            catch(Exception ex) {Logger.LogLocal("Authenticator Error: Could not clear the authkey or authkey registry item doesn't exist.\r\n"+ex.Message); }
        }
        /// <summary>
        /// Check with the maven cloud to see if the key is valid
        /// </summary>
        /// <param name="key">The encrypted byte array for the key</param>
        /// <returns>"True" if the key is valid. Else false.</returns>
        public static bool isKeyValidOnServer(byte[] key)
        {
            //if there's no token, automatically reprompt without asking the server. 
            //sort of client side validation. 
            if (key == null || key.Length == 0)
            {
                return false;
            }
            else
            {
                string oAuth = WindowsDPAPI.Decrypt(key);
                //you have the oauth token, use it to call back and get the session key ("userAuth")
                string oAuthSendString = GetDecryptedRegistryVaue("oAuthString");
                try
                {
                    encryptedSessionKey = WindowsDPAPI.Encrypt(trimKeyValue("userAuth",LoginResponse(oAuthSendString)));
                    return true;
                }
                catch { return false; }
            }
        }
        /// <summary>
        /// Show the login screen. 
        /// </summary>
        /// <param name="shortMessage">a SHORT message describing why the login prompt is presented</param>
        private static void PromptNewLogin(string shortMessage)
        {
            frmLogin f = new frmLogin(shortMessage);
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
        /// <summary>
        /// Gets the current logged in Maven username
        /// </summary>
        /// <returns></returns>
        public static string GetUserName()
        {
            return GetDecryptedRegistryVaue("User");
        }
        public static string getProviderId()
        {
            return GetDecryptedRegistryVaue("provider");
        }
        public static string getMavenUserName()
        {
            return GetDecryptedRegistryVaue("MavenUser").ToUpper();
        }
        public static string getMavenUserID()
        {
            return GetDecryptedRegistryVaue("mavenuserid");
        }
        private static string GetDecryptedRegistryVaue(string key)
        {
            string rtn = "";
            RegistryKey authKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", false);
            if (authKey != null && authKey.GetValue(key) != null)
            {


                //if you found the key and it is ok to use it, then by all means use it
                byte[] encUser = (byte[])authKey.GetValue(key);
                rtn = WindowsDPAPI.Decrypt(encUser);

            }
            return rtn;
        }
        public static string trimKeyValue(string key, string trimfrom)
        {
            string rtn = "";
            try
            {
                string findstr = "\"" + key + "\": \"";
                trimfrom = trimfrom.Substring(trimfrom.IndexOf(findstr));
                trimfrom = trimfrom.Replace("\"" + key + "\": \"", "");
                rtn = trimfrom.Substring(0, trimfrom.IndexOf("\"")).Replace("\"", "").Trim();

            }
            catch { }
            return rtn;
        }
        public static string LoginResponse(string dataToPost)
        {
            Settings set = new Settings();
            bool rtn = false;
            //TODO: HTTPS
            WebRequest rqst = WebRequest.Create("https://" + set.pollingServer + "/broadcaster/login");
            rqst.Method = "POST";
            Settings currsettings = new Settings();
            byte[] bytes = Encoding.UTF8.GetBytes(dataToPost);
            // Set the ContentType property of the WebRequest.
            rqst.ContentType = "application/x-www-form-urlencoded";
            // Set the ContentLength property of the WebRequest.
            rqst.ContentLength = bytes.Length;
            // Get the request stream.

            Stream dataStream = rqst.GetRequestStream();
            // Write the data to the request stream.
            dataStream.Write(bytes, 0, bytes.Length);
            // Close the Stream object.
            dataStream.Close();
            // Get the response.
            WebResponse response = rqst.GetResponse();
            // Display the status.
            string status = ((HttpWebResponse)response).StatusDescription;
            // Get the stream containing content returned by the server.
            dataStream = response.GetResponseStream();
            // Open the stream using a StreamReader for easy access.
            StreamReader reader = new StreamReader(dataStream);
            // Read the content.
            string responseFromServer = reader.ReadToEnd();
            // Clean up the streams.
            reader.Close();
            dataStream.Close();
            response.Close();

            return responseFromServer;
        }
    }
}
