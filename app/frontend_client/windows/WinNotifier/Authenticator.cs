using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Win32;

namespace MavenAsDemo
{
    class Authenticator
    {
        public static byte[] GetEncryptedAuthKey()
        {
            byte[] key = null;
            RegistryKey authKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", false);
            if (authKey != null && authKey.GetValue("Auth") != null)
            {
                key= (byte[])authKey.GetValue("Auth");
                
            }
            if (!isKeyValidOnServer(key))
            {
                PromptNewLogin();
                
                key = GetEncryptedAuthKey();
            }
            return key;
        }
        public static void ClearLoginSettings()
        {
            try
            {
                RegistryKey authKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", true);
                authKey.DeleteValue("Auth");
            }
            catch(Exception ex) {Program.LogMessage("Authenticator Error: Could not clear the authkey or authkey registry item doesn't exist.\r\n"+ex.Message); }
        }
        private static bool isKeyValidOnServer(byte[] key)
        {
            //TODO: Actually validate the key with the server
            return (key!=null);
        }
        private static void PromptNewLogin()
        {
            //TODO: Actually prompt the user for a user/password and save the key from the server to the registry
            frmLogin f = new frmLogin();
            f.Visible = true;
            System.Windows.Forms.Application.Run(f);
        }
    }
}
