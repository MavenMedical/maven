using System;
using System.Text;
using System.Security.Cryptography;

namespace MavenAsDemo
{
    class WindowsDPAPI
    {
        public static byte[] Encrypt(string instr)
        {
            byte[] toEncrypt = UnicodeEncoding.ASCII.GetBytes(instr);
            //byte[] entropy = CreateRandomEntropy();
            // Encrypt the data in memory. The result is stored in the same same array as the original data. 
            byte[] encrptedData = ProtectedData.Protect(toEncrypt, MavenEntropy(), DataProtectionScope.CurrentUser);
            return encrptedData;
        }
        public static string Decrypt(byte[] inbytes)
        {
            byte[] outbytes = ProtectedData.Unprotect(inbytes, MavenEntropy(), DataProtectionScope.CurrentUser);
            return System.Text.Encoding.Default.GetString(outbytes);
        }
        private static byte[] MavenEntropy()
        {

            return UnicodeEncoding.ASCII.GetBytes("09vb87ws90xm55ed"); ;


        }
    }
}
