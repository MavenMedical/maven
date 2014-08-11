using System;
using System.Collections.Generic;
using System.Threading;
using System.Windows.Forms;
using System.Data;
using System.Text.RegularExpressions;

namespace MavenAsDemo
{
    static class Program
    {
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

        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            prepQuietList();
            ThreadStart startTray = new ThreadStart(prepTray);
            Thread traythread = new Thread(startTray);
            traythread.Start();
            Thread t=JobOffPollingThread();
            //stay alive until polling dies
            while (t.IsAlive)
            {
                Thread.Sleep(5000);
            }
        }

        public static void JobOffAlertThread()
        {
            ThreadStart start = new ThreadStart(ShowAlertForm);
            Thread thrd = new Thread(start);
            thrd.SetApartmentState(ApartmentState.STA);
            priorityThreadId =thrd.ManagedThreadId;
            thrd.Start();
        }
        public static Thread JobOffPollingThread()
        {
            ThreadStart start = new ThreadStart(startPolling);
            Thread thrd = new Thread(start);
            thrd.SetApartmentState(ApartmentState.STA);
            priorityThreadId = thrd.ManagedThreadId;
            thrd.Start();
            return thrd;
        }
        public static void ShowAlertForm()
        {
            frmAlert frm = new frmAlert(fadeSlowness,location);
            frm.ShowInTaskbar = false;
            frm.Visible = true;
            Application.Run(frm);
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

            MenuItem locitm = new MenuItem("Soft Alert Location");
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

            tray.ContextMenu = ctx;
            tray.Visible = true;
            Application.Run();
        }
        public static void startPolling()
        {

            Unity.UnityServiceClient unitySvc = new Unity.UnityServiceClient();
            try
            {
                //get a token and write it to the console
                token = unitySvc.GetSecurityToken(serviceUser, servicePwd);
                Console.WriteLine(token);
                while (true) //loop forever 
                {
                    DateTime Today = DateTime.Now;
                    //string strToday = Today.ToString("yyyy-MM-dd");
                    string strToday = Today.ToString("dd-MMM-yyyy");
                    DataSet ds = getSchedule(strToday);
                    DataTableReader reader = ds.CreateDataReader();
                    int i = 1;
                    while (reader.Read())
                    {
                        string patId = reader.GetString(15);
                        DataSet docDs = getDocuments(patId, strToday);
                        //DumpToConsole(docDs);
                        DataTableReader docreader = docDs.CreateDataReader();
                        while (docreader.Read())
                        {
                            string documentId = docreader.GetString(0);
                            string keywords = docreader.GetString(10);
                            string icd9 = getIcdFromKeywords(keywords);
                            DateTime filedt = Convert.ToDateTime(docreader.GetString(2));
                            double timeSinceCreate = DateTime.Now.Subtract(filedt).TotalSeconds;
                            bool mine = docreader.GetString(9) == "Y";
                            //if you got in in the past 20 minutes 
                            //and the diagnosis is there and this is indeed your note
                            // check the quiet list and then continue with alerting logic if you're good  to go
                            if (icd9.Length > 0 && timeSinceCreate < 1200 && isEnabled(documentId))
                            {
                                alert(documentId);
                            }
                        }
                    }
                    //Console.WriteLine(strToday);
                    //Console.ReadLine();
                    System.Threading.Thread.Sleep(2000);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                Console.ReadLine();
            }
        }
        public static void alert(string documentId)
        {
            DataRow row = quietlist.NewRow();
            row["documentId"] = documentId;
            try
            {
                quietlist.Rows.Add(row);
            }
            catch { }
            //Console.WriteLine("Alert now!");
            if (mode == AlertMode.deskSoft)
            {
                JobOffAlertThread();
            }
            if (mode == AlertMode.deskHard || mode == AlertMode.combo)
            {
                System.Diagnostics.Process.Start("https://onedrive.live.com/fullscreen?cid=fff6838d9ae151c8&id=documents&resid=FFF6838D9AE151C8%219693&filename=PathwaysFakeApp.pptx&wx=p&wv=s&wc=officeapps.live.com&wy=y&wdModeSwitchTime=1407356909440");
            }
            if (mode == AlertMode.mobile || mode == AlertMode.combo)
            {
                //mobile alert
            }
            if (mode == AlertMode.inbox || mode == AlertMode.combo)
            {
                //send inbasket notice
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
            alert("0");
        }
    }
}
