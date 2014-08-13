using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace MavenAsDemo
{
    public partial class frmHardAlert : Form
    {
        public int tix=0;
        public string url = "http://mavenmedical.net";
        public string loc = "TL";
        public Point downPoint=Point.Empty;
        public bool moveForm = false;

        public frmHardAlert(string inUrl, string location)
        {
            loc = location;
            url = inUrl;
            InitializeComponent();
        }

        private void frmHardAlert_Load(object sender, EventArgs e)
        {
            timer.Interval = 1000;
            timer.Start();
            browserDisplay.Navigate(url);
            browserDisplay.ScrollBarsEnabled = false;
            mover.MouseDown += MouseDown;
            mover.MouseUp += MouseUp;
            mover.MouseMove += MouseMove; 
            this.Location = getLocation(loc);
            this.TopMost = true;
        }
        private void pictureBox1_Click(object sender, EventArgs e)
        {
            this.Close();
            this.Dispose();
        }

        private void timer_Tick(object sender, EventArgs e)
        {
            tix += 1;
            this.TopMost = true;
            //automatically close out after 5 minutes. 
            //this is the case where the user doesnt close out, but just puts it behind  his EMR screen. 
            if (tix == 300)
            {
                this.Close();
                this.Dispose();
            }
            string tst=browserDisplay.DocumentText;
        }

        private Point getLocation(string locstring)
        {
            Rectangle workingArea = Screen.GetWorkingArea(this);
            int hpixels = workingArea.Right;
            int vpixels = workingArea.Bottom;
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
                    v = Convert.ToInt32(Math.Round((decimal)vpixels / 2, 0)) - Convert.ToInt32(Math.Round((decimal)Size.Height / 2, 0));
                    break;
                case "B":
                    v = vpixels - Size.Height - 15;
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
            return new Point(h, v);
        }
        private void MouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left)
            {
                return;
            }
            downPoint = new Point(e.X, e.Y);
            moveForm = true;
        }
        private void MouseMove(object sender, MouseEventArgs e)
        {
            if (moveForm)
            {
                this.Top = this.Top + e.Y - downPoint.Y;
                this.Left = this.Left + e.X - downPoint.X;   
            }
        }
        private void MouseUp(object sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left)
            {
                return;
            }
            downPoint = Point.Empty;
            moveForm = false;
        }
       
    }
}
