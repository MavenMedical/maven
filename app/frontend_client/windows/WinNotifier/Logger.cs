using System;
using System.Collections.Generic;
using System.Text;
using System.Net;
using System.IO;
using System.Diagnostics;

namespace MavenAsDemo
{
    class Logger
    {
        public static bool Log(string message, string categories)
        {
            bool rtn = true;
            LogLocal(message);
            try
            {
                logWeb(message, categories);
            }
            catch (Exception ex){
                LogLocal(ex.Message);
            }
            return rtn;
        }
        private static bool logWeb(string message, string categories)
        {
            /*In the URL (however it's being sent now, don't use labels below literally):
                1.) customer_id
                2.) username
                3.) user role (notification)

                In the BODY via JSON:
                1.) "tags" (list of strings)
                2.) "log_body" (string)
                3.) "device" (string)             */
            message = message.Replace("\\", "/").Replace("\"", "'");
            Settings cursettings = new Settings();
            string device = cursettings.machine;
            string body = "{\"message\":\"" + message + "\",\"tags\":\"" + categories + ","+Program.serialnum+"\",\"device\":\"" + device + "\"}";
            bool rtn = false;
            //TODO: HTTPS
             string rqstUrl = "https://" + cursettings.pollingServer + "/broadcaster/log?userAuth=" + WindowsDPAPI.Decrypt(Program.EncryptedKey)
                            + "&osUser=" + cursettings.osUser + "&machine=" + cursettings.machine + "&osVersion=" + cursettings.os
                            + "&user=" + Authenticator.getMavenUserName() + "&customer_id=" + cursettings.custId
                            + "&provider=" + Authenticator.getProviderId() + "&roles[]=notification&userid=" + Authenticator.getMavenUserID()+"&ver="+cursettings.softwareVersion;
                        
            WebRequest rqst = WebRequest.Create(rqstUrl);
            rqst.Method = "POST";
            byte[] bytes = Encoding.UTF8.GetBytes(body);
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
            rqst.Abort();
            rqst = null;

            return rtn;
        }
        /// <summary>
        /// handle logging debug messages
        /// </summary>
        /// <param name="msg">the entire message that should be logged.</param>
        public static void LogLocal(string msg)
        {
            try
            {
                //HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\eventlog\Application\MavenDesktop must exist  
                //Created during install
                EventLog el = new EventLog("Application");
                el.Source = "MavenDesktop";
                el.WriteEntry(msg, System.Diagnostics.EventLogEntryType.Information, 234);
                //TODO: handle an actual registered event id. now it's event 0 which is getting a "desc cannot be found" message
                //codeproject.com/Articles/4153/Getting-the-most-out-of-Event-Viewer
            }
            catch
            {
                //TODO: Call this function recursively if writing to the error log fails. Just kidding...
            }
        }
        /// <summary>
        /// handle logging debug messages
        /// </summary>
        /// <param name="msg">the entire message that should be logged.</param>
        private static void LogMessage(string msg, System.Diagnostics.EventLogEntryType type)
        {
            try
            {
                //HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\services\eventlog\Application\MavenDesktop must exist  
                //Created during install
                EventLog el = new EventLog("Application");
                el.Source = "MavenDesktop";
                el.WriteEntry(msg, type);
                //TODO: handle an actual registered event id. now it's event 0 which is getting a "desc cannot be found" message
                //codeproject.com/Articles/4153/Getting-the-most-out-of-Event-Viewer
            }
            catch
            {
                //TODO: Call this function recursively if writing to the error log fails. Just kidding...
            }
        }
        
    }
}
