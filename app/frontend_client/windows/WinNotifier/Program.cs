using System;
using System.Collections.Generic;
using System.Threading;
using System.Windows.Forms;
using System.Data;
using System.Text.RegularExpressions;
using System.Net;
using System.IO;

namespace MavenAsDemo
{
    static class Program
    {
        //TODO: Move all of this stuff to a settings object
        public static string serviceUser = "MavenPathways";
        public static string servicePwd = "MavenPathways123!!";
        public static string appName = "MavenPathways.TestApp";
        public static string token = "";
        public static string appUserName = "cliffhux";
        public static DataTable quietlist = new DataTable();
        public static int priorityThreadId = 0;
        public static AlertMode mode = AlertMode.deskSoft;
        public static double fadeSlowness = 3;
        public static string location = "BR";
        public static string url = "https://23.251.150.28/broadcaster/poll?key=";
        public static bool continueOn = true;
        public static byte[] EncryptedKey = null;

        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            try
            {
                Application.SetCompatibleTextRenderingDefault(false);
                EncryptedKey = Authenticator.GetEncryptedAuthKey();
                Application.EnableVisualStyles();
                prepQuietList();
                ThreadStart startTray = new ThreadStart(prepTray);
                Thread traythread = new Thread(startTray);
                traythread.Start();
                Thread t = JobOffPollingThread();
                //stay alive until polling dies
                while (t.IsAlive && continueOn)
                {
                    Thread.Sleep(5000);
                }
            }
            catch (Exception ex)
            {
                //you've just failed at the highest possible level
                //kill yourself
                CommitSuicide(null, null);
            }
        }
        
        public static void JobOffAlertThread()
        {
            ThreadStart start = new ThreadStart(ShowAlertForm);
            Thread thrd = new Thread(start);
            thrd.IsBackground = true;
            thrd.SetApartmentState(ApartmentState.STA);
            priorityThreadId =thrd.ManagedThreadId;
            thrd.Start();
        }
        public static Thread JobOffPollingThread()
        {
            ThreadStart start = new ThreadStart(startPolling);
            Thread thrd = new Thread(start);
            thrd.IsBackground = true;
            thrd.SetApartmentState(ApartmentState.STA);
            priorityThreadId = thrd.ManagedThreadId;
            thrd.Start();
            return thrd;
        }
        public static void ShowAlertForm()
        {
            if (mode == AlertMode.combo || mode == AlertMode.deskSoft)
            {
                frmAlert frm = new frmAlert(fadeSlowness, location, url);
                frm.ShowInTaskbar = false;
                frm.Visible = true;
                Application.Run(frm);
            }
            else if (mode == AlertMode.deskHard)
            {
                frmHardAlert frm = new frmHardAlert(url,location);
                frm.ShowInTaskbar = false;
                frm.Visible = true;
                Application.Run(frm);
            }
        }
        public static void prepTray()
        {
            NotifyIcon tray = new NotifyIcon();
            tray.Icon = new System.Drawing.Icon("Maven256.ico");
            ContextMenu ctx = new ContextMenu();

            MenuItem modeitm = new MenuItem("Alert Mode");
            modeitm.MenuItems.Add("Inbox", AlertModeClick);
            modeitm.MenuItems.Add("Mobile", AlertModeClick);
            modeitm.MenuItems.Add("Desktop Soft Alert", AlertModeClick);
            modeitm.MenuItems.Add("Desktop Hard Alert", AlertModeClick);
            modeitm.MenuItems.Add("Combo", AlertModeClick);
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
            ctx.MenuItems.Add(speeditm);

            MenuItem locitm = new MenuItem("Alert Location");
            MenuItem vitm = new MenuItem("Vertical");
            vitm.MenuItems.Add("Top", LocationClick);
            vitm.MenuItems.Add("Middle", LocationClick);
            vitm.MenuItems.Add("Bottom", LocationClick);
            locitm.MenuItems.Add(vitm);
            MenuItem hitm = new MenuItem("Horizontal");
            hitm.MenuItems.Add("Left", LocationClick);
            hitm.MenuItems.Add("Center", LocationClick);
            hitm.MenuItems.Add("Right", LocationClick);
            locitm.MenuItems.Add(hitm);
            ctx.MenuItems.Add(locitm);

            MenuItem itm6 = new MenuItem("Replay Last Alert", DummyAlert);
            ctx.MenuItems.Add(itm6);

            MenuItem itmClose = new MenuItem("Exit Maven Tray", CommitSuicide);
            ctx.MenuItems.Add(itmClose);

            MenuItem itmLogOut = new MenuItem("Log Out", LogOut);
            ctx.MenuItems.Add(itmLogOut);

            tray.ContextMenu = ctx;
            tray.Visible = true;
            Application.Run();
        }
        public static void startPolling()
        {

            ServicePointManager.ServerCertificateValidationCallback = new System.Net.Security.RemoteCertificateValidationCallback(AcceptAllCertifications);
            while (continueOn)
            {
                try
                {
                    WebRequest rqst = WebRequest.Create("https://23.251.150.28/broadcaster/poll?key=" + WindowsDPAPI.Decrypt(EncryptedKey));
                    rqst.Timeout = 60000;
                    HttpWebResponse rsp = (HttpWebResponse)rqst.GetResponse();
                    HttpStatusCode status = rsp.StatusCode;
                    if (status == HttpStatusCode.OK)
                    {
                        Stream dataStream = rsp.GetResponseStream();
                        StreamReader reader = new StreamReader(dataStream);
                        string responseFromServer = reader.ReadToEnd();
                        if (responseFromServer != "[]")
                        {
                            string alertUrl = responseFromServer.Split(',')[0].Replace("[{\"LINK\": \"", "").Replace("\"", "");
                            alert("1", "66556", alertUrl);
                        }
                    }
                }
                catch (Exception e)
                {
                }
            }
            
        }
        public static bool AcceptAllCertifications(object sender, System.Security.Cryptography.X509Certificates.X509Certificate certification, System.Security.Cryptography.X509Certificates.X509Chain chain, System.Net.Security.SslPolicyErrors sslPolicyErrors)
        {
            return true;
        }
        public static void alert(string documentId,string patId, string inUrl)
        {
            DataRow row = quietlist.NewRow();
            row["documentId"] = documentId;
            url = inUrl;
            try
            {
                quietlist.Rows.Add(row);
            }
            catch { }
            //Console.WriteLine("Alert now!");
            if (mode == AlertMode.deskSoft || mode == AlertMode.deskHard || mode == AlertMode.combo)
            {
                JobOffAlertThread();
            }
            if (mode == AlertMode.mobile || mode == AlertMode.combo)
            {
                //mobile alert
            }
            if (mode == AlertMode.inbox || mode == AlertMode.combo)
            {
                mail(patId);
            }
        }
        public static bool isEnabled(string documentId)
        {
            bool rtn = true;
            DataRow[] dr = quietlist.Select("documentId=" + documentId);
            if (dr.Length > 0)
            {
                rtn = false;
            }
            return rtn;

        }
        public static void prepQuietList()
        {
            quietlist.Columns.Add("documentId");
            quietlist.PrimaryKey = new DataColumn[] { quietlist.Columns["documentId"] };

        }
        public static DataSet getSchedule(string day)
        {
            Unity.UnityServiceClient unitySvc = new Unity.UnityServiceClient();
            return unitySvc.Magic("GetSchedule",       // Action    
                                     appUserName,            // UserID    
                                     appName,                // Appname   
                                     "",                     // PatientID 
                                     token,                  // Token     
                                     day,   // Parameter1 @SINCE
                                     "",                     // Parameter2
                                     "",                     // Parameter3
                                     "",                     // Parameter4
                                     "",                     // Parameter5
                                     "",                     // Parameter6
                                     null);                  // data                // data    
        }
        public static string getIcdFromKeywords(string keywords)
        {
            string pattern = @"\(V?\d+\.?\d*\)";
            Regex rex = new Regex(pattern);
            Match m = rex.Match(keywords);
            return m.Value.Replace("(", "").Replace(")", "");
        }
        public static DataSet getDocuments(string pat, string day)
        {
            Unity.UnityServiceClient unitySvc = new Unity.UnityServiceClient();
            return unitySvc.Magic("GetDocuments",       // Action    
                                     appUserName,            // UserID    
                                     appName,                // Appname   
                                     pat,                     // PatientID 
                                     token,                  // Token     
                                     day,   // Parameter1 @SINCE
                                     day,                     // Parameter2
                                     "",                     // Parameter3
                                     "",                     // Parameter4
                                     "",                     // Parameter5
                                     "",                     // Parameter6
                                     null);                  // data                // data    
        }
        public static DataSet getPatientsBySomething(string strSince)
        {
            Unity.UnityServiceClient unitySvc = new Unity.UnityServiceClient();
            return unitySvc.Magic("GetPatientsBySomething",       // Action    
                                     appUserName,            // UserID    
                                     appName,                // Appname   
                                     "",                     // PatientID 
                                     token,                  // Token     
                                     "VisitType",   // Parameter1 @SINCE
                                     "Outpatient",                     // Parameter2
                                     strSince,                     // Parameter3
                                     "",                     // Parameter4
                                     "",                     // Parameter5
                                     "",                     // Parameter6
                                     null);                  // data    
        }
        /// <summary>
        /// Just saving off some useful stuff to dump an entire row to the console
        /// </summary>
        /// <param name="reader"></param>
        static void DumpToConsole(DataSet ds)
        {

            DataTableReader reader = ds.CreateDataReader();
            int i = 0;
            while (reader.Read())
            {
                Console.WriteLine("Record " + i.ToString() + ": ");
                object[] stuff = new object[100];
                reader.GetValues(stuff);
                foreach (object obj in stuff)
                {
                    if (obj != null)
                    {
                        Console.WriteLine("   " + obj.ToString());
                        //System.Windows.Forms.Clipboard.SetText(obj.ToString());
                    }
                }
                i++;
            }
        }
        public enum AlertMode
        {
            inbox,mobile,deskSoft,deskHard,combo
        };
        static void AlertModeClick(object sender, EventArgs e)
        {
            MenuItem itm = (MenuItem)sender;
            switch (itm.Text)
            {
                case "Inbox":
                    mode = AlertMode.inbox;
                    break;
                case "Mobile":
                    mode = AlertMode.mobile;
                    break;
                case "Desktop Soft Alert":
                    mode = AlertMode.deskSoft;
                    break;
                case "Desktop Hard Alert":
                    mode = AlertMode.deskHard;
                    break;
                case "Combo":
                    mode = AlertMode.combo;
                    break;
            }
        }
        static void FadeSlownessClick(object sender, EventArgs e)
        {
            MenuItem itm = (MenuItem)sender;
            try
            {
                fadeSlowness = Convert.ToDouble(itm.Text);
            }
            catch { }
        }
        static void LocationClick(object sender, EventArgs e)
        {
            MenuItem itm = (MenuItem)sender;
            switch (itm.Text)
            {
                case "Top":
                    location="T"+location.Substring(1);
                    break;
                case "Middle":
                    location = "M" + location.Substring(1);
                    break;
                case "Bottom":
                    location = "B" + location.Substring(1);
                    break;
                case "Left":
                    location =location.Substring(0,1)+"L";
                    break;
                case "Center":
                    location = location.Substring(0, 1) + "C";
                    break;
                case "Right":
                    location = location.Substring(0, 1) + "R";
                    break;
            }
        }
        static void DummyAlert(object sender, EventArgs e)
        {
            alert("0","66556","http://mavenmedical.net");
        }
        static void mail(string patId)
        {
            string namepro=getPatientNameAndPronoun(patId);
            string name=namepro.Split('|')[0];
            string pronoun=namepro.Split('|')[1];
            Unity.UnityServiceClient unitySvc = new Unity.UnityServiceClient();
            DataSet ds = unitySvc.Magic("SaveTask",       // Action    
                                     appUserName,            // UserID    
                                     appName,                // Appname   
                                     patId,                     // PatientID 
                                     token,                  // Token     
                                     "Send Chart",   // Parameter1 @SINCE
                                     appUserName,                     // Parameter2
                                     "",                     // Parameter3
                                     "During your appointment with "+name+" today, Maven detected that "+pronoun+" matched a pathway from the AUA.\r\nPlease log into Maven to view the protocol.",                     // Parameter4
                                     "AUA Pathway detected for your patient. Please review.",                     // Parameter5
                                     "",                     // Parameter6
                                     null);                  // data                // data 
        }
        static string getPatientNameAndPronoun(string patId)
        {
            Unity.UnityServiceClient unitySvc = new Unity.UnityServiceClient();
            DataSet ds = unitySvc.Magic("GetPatient",       // Action    
                                     appUserName,            // UserID    
                                     appName,                // Appname   
                                     patId,                     // PatientID 
                                     token,                  // Token     
                                     "",   // Parameter1 @SINCE
                                     "",                     // Parameter2
                                     "",                     // Parameter3
                                     "",
                                     "",
                                     "",                     // Parameter6
                                     null);                  // data                // data 
            DataTableReader reader=ds.CreateDataReader();
            reader.Read();
            string name= reader.GetString(2)+" "+reader.GetString(1);
            string pronoun = "he";
            try
            {
                if (reader.GetString(4) == "F")
                {
                    pronoun = "she";
                }

            }
            catch { }
            return name + "|" + pronoun;
        }
        static void CommitSuicide(object sender, EventArgs e)
        {
            try
            {
                continueOn = false;
                Application.Exit();
            }
            catch { }
           
        }
        static void LogOut(object sender, EventArgs e)
        {
            Authenticator.ClearLoginSettings();
            CommitSuicide(null, null);
        }
    }
}
