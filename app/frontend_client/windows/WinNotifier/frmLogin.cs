using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Win32;
using System.Net;
using System.IO;

namespace MavenAsDemo
{
    public partial class frmLogin : Form
    {
        protected Point downPoint=Point.Empty;
        protected string loc = "BR";
        protected string errtext = "";
        
        /// <summary>
        /// Call this if you want to display the form with an error message displayed
        /// </summary>
        /// <param name="errmsg">a message to display in a red label</param>
        public frmLogin(string errmsg)
        {
            try
            {
                errtext = errmsg;
                InitializeComponent();
            }
            catch (Exception ex)
            {
                Program.LogMessage("Error Launching Login Form: \r\n" + ex.Message);
                this.Close();
                this.Dispose();
            }
        }
        public frmLogin()
        {
            try
            {
                InitializeComponent();
            }
            catch (System.Threading.ThreadAbortException ex)
            {
                Program.LogMessage("Error Launching Login Form: \r\n" + ex.Message);
                this.Close();
                this.Dispose();
            }
        }

        private void FormLogin_Load(object sender, EventArgs e)
        {
            imgLogo.MouseDown += new MouseEventHandler(MouseDown);
            imgLogo.MouseMove += new MouseEventHandler(MouseMove);
            imgLogo.MouseUp += new MouseEventHandler(MouseUp);
            imgKey.MouseDown += new MouseEventHandler(MouseDown);
            imgKey.MouseMove += new MouseEventHandler(MouseMove);
            imgKey.MouseUp += new MouseEventHandler(MouseUp);

            lblErr.Text = errtext;

            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            //make the background transparent and whiteish so the white overlay is visible and the shadow appears to be ontop of white. 
            //this.BackColor = System.Drawing.Color.Gray;
            //this.TransparencyKey=System.Drawing.Color.Gray;
            //go to the bottom right + 15px vertical 
            Rectangle workingArea = Screen.GetWorkingArea(this);
            this.Location = getLocation(loc);
            //keep this on top
            this.TopMost = true;
        }
        /// <summary>
        /// On mouse enter of the form, reset the timer and become opaque
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void pictureBox1_Click(object sender, EventArgs e)
        {
            Authenticator.quitLogin = true;
            closeOut();
        }
        protected override bool ShowWithoutActivation
        {
            //always display without focus. 
            get { return true; }
        }

        private new void MouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left)
            {
                return;
            }
            downPoint = new Point(e.X, e.Y);
        }
        private new void MouseMove(object sender, MouseEventArgs e)
        {
            if (downPoint == Point.Empty)
            {
                return;
            }
            Point location = new Point(
                this.Left + e.X - downPoint.X,
                this.Top + e.Y - downPoint.Y);
            this.Location = location;
        }
        private new void MouseUp(object sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left)
            {
                return;
            }
            downPoint = Point.Empty;
        }
        private void pictureBox2_Click(object sender, EventArgs e)
        {

        }
        private Point getLocation(string locstring)
        {
            Rectangle workingArea = Screen.GetWorkingArea(this);
            int hpixels=workingArea.Right;
            int vpixels=workingArea.Bottom;
            int v = 0;
            int h = 0;
            string strV = locstring.Substring(0, 1);
            string strH = locstring.Substring(1, 1);
            switch (strV)
            {
                case "T":
                    v = 0;
                    break;
                case "M":
                    v = Convert.ToInt32( Math.Round((decimal)vpixels / 2, 0))-Convert.ToInt32(Math.Round((decimal)Size.Height/2,0));
                    break;
                case "B":
                    v=vpixels - Size.Height - 15;
                    break;
            }
            switch (strH)
            {
                case "L":
                    h = 0;
                    break;
                case "C":
                    h = Convert.ToInt32(Math.Round((decimal)hpixels / 2, 0)) - Convert.ToInt32(Math.Round((decimal)Size.Width / 2, 0));
                    break;
                case "R":
                    h = hpixels - Size.Width - 10;
                    break;
            }
            return new Point(h,v);
        }

        private void closeOut()
        {
            this.Close();
        }
        private void checkAutoStart()
        {
            RegistryKey registryKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run", true);
            if (chkAutoLogin.Checked)
            {
                registryKey.SetValue("MavenPathways", Application.ExecutablePath);
            }
            else
            {
                try
                {
                    registryKey.DeleteValue("MavenPathways");
                }
                catch
                {
                    //I guess it didnt exist to begin with. 
                }
            }
        }

        private void WriteKey(string value,string key)
        {
            byte[] keyToSave = WindowsDPAPI.Encrypt(value);
            RegistryKey authKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", true);
            if (authKey == null)
            {
                authKey=Registry.CurrentUser.CreateSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\",RegistryKeyPermissionCheck.ReadWriteSubTree);
            }
            authKey.SetValue(key, keyToSave);
        }
        private static void WriteSaveLogin(bool shouldStick)
        {
            RegistryKey Stick = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", true); 
            if (Stick == null)
            {
                Stick = Registry.CurrentUser.CreateSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", RegistryKeyPermissionCheck.ReadWriteSubTree);
            }
            Stick.SetValue("LoginStick", shouldStick);

        }

        private void btnLogin_Click_1(object sender, EventArgs e)
        {
            string user = txtUser.Text.Trim();
            string pass = txtPass.Text.Trim();
            if (user=="" || pass==""||!loginSuccess())
            {
                lblErr.Text = "Specify Valid Credentials";
                return;
            }
            //save the login stickiness
            WriteSaveLogin(chkStay.Checked);
            checkAutoStart(); //save the autostart setting
            closeOut();
        }
        private bool loginSuccess()
        {
            Settings set = new Settings();
            bool rtn = false;
            //TODO: HTTPS
            WebRequest rqst= WebRequest.Create("http://"+set.pollingServer+"/broadcaster/login");
            rqst.Method = "POST";
            string postData = "{\"user\":\""+txtUser.Text+"\",\"password\":\""+txtPass.Text+"\"}";
            byte[] bytes = Encoding.UTF8.GetBytes(postData);
            // Set the ContentType property of the WebRequest.
            rqst.ContentType = "application/x-www-form-urlencoded";
            // Set the ContentLength property of the WebRequest.
            rqst.ContentLength = bytes.Length;
            // Get the request stream.
            try
            {
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

                //get the provider id and auth key
                string provider = trimKeyValue("provider", responseFromServer);
                string Auth = trimKeyValue("userAuth", responseFromServer);

                //write the provider id and auth key, etc
                WriteKey(provider, "provider");
                WriteKey(Auth, "Auth");
                WriteKey(trimKeyValue("user", responseFromServer), "MavenUser");

                rtn = true;
            }
            catch (Exception ex)
            {
                //this gets hit if the login fails. 
                Program.LogMessage("Login Failure: \r\n" + ex.Message);  
            }
            
            return rtn;
        }
        private string trimKeyValue(string key,string trimfrom)
        {
            string rtn = "";
            try
            {
                trimfrom = trimfrom.Substring(trimfrom.IndexOf("\"" + key + "\": \""));
                trimfrom = trimfrom.Replace("\"" + key + "\": \"", "");
                rtn = trimfrom.Substring(0, trimfrom.IndexOf("\"")).Replace("\"","").Trim();

            }
            catch { }
            return rtn;
        }
    }
}
