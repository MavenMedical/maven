﻿using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Win32;

namespace MavenAsDemo
{
    public partial class frmLogin : Form
    {
        public Point downPoint=Point.Empty;
        public string loc = "BR";

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

        private static void WriteKey(string key)
        {
            byte[] keyToSave = WindowsDPAPI.Encrypt(key);
            RegistryKey authKey = Registry.CurrentUser.OpenSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\", true);
            if (authKey == null)
            {
                authKey=Registry.CurrentUser.CreateSubKey("SOFTWARE\\Maven\\PathwaysDesktop\\Security\\",RegistryKeyPermissionCheck.ReadWriteSubTree);
            }
            authKey.SetValue("Auth", keyToSave);
        }

        private void btnLogin_Click_1(object sender, EventArgs e)
        {
            //TODO: Actually log in
            WriteKey(txtUser.Text);
            checkAutoStart();
            closeOut();
        }
    }
}