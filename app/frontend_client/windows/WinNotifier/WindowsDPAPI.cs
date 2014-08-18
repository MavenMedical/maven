using System;
using System.Text;
using System.Security.Cryptography;

namespace MavenAsDemo
{
    /// <summary>
    /// A helper class for using windows Data Protection API (DPAPI)
    /// This is a safe way to encrypt/decrypt stuff (like auth keys) so that not even admins can access them.
    /// for more info, google DPAPI
    /// </summary>
    class WindowsDPAPI
    {
        public static byte[] Encrypt(string instr)
        {
            byte[] toEncrypt = UnicodeEncoding.ASCII.GetBytes(instr); 
            byte[] encrptedData = ProtectedData.Protect(toEncrypt, MavenEntropy(), DataProtectionScope.CurrentUser);
            return encrptedData;
        }
        /// <summary>
        /// Decrypt a maven-encrypted string using DPAPI
        /// </summary>
        /// <param name="inbytes">the thing to decrypt</param>
        /// <returns>The string that was originally encrypted</returns>
        public static string Decrypt(byte[] inbytes)
        {
            byte[] outbytes = ProtectedData.Unprotect(inbytes, MavenEntropy(), DataProtectionScope.CurrentUser);
            return System.Text.Encoding.Default.GetString(outbytes);
        }
        /// <summary>
        /// A "Maven-consistent entropy" to keep other programs running under this user from being able to decrypt the auth key. 
        /// Any program that wants to decrypt something using this API would need to be 1) started by this user and 2) know this secret string. 
        /// </summary>
        /// <returns>a byte array representing a maven-specific entropy</returns>
        private static byte[] MavenEntropy()
        {

            return UnicodeEncoding.ASCII.GetBytes("09vb87ws90xm55ed"); ;


        }
    }
}
