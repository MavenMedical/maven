using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Threading;

namespace MavenAsDemo
{
    public partial class frmAlert : Form
    {
        //track how many ticks since the timer was reset
        public int tix = 0;
        public Point downPoint=Point.Empty;
        public int timerspeed = 200;
        public string loc = "BR";
        public string url = "http://mavenmedical.net";

        public frmAlert(double fadeslowness,string location,string inUrl)
        {
            try
            {
                timerspeed = Convert.ToInt32(Math.Round(50 * fadeslowness, 0));
                loc = location;
                url = inUrl;
                InitializeComponent();
            }
            catch (System.Threading.ThreadAbortException ex)
            {
                this.Close();
                this.Dispose();
            }
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            this.MouseEnter += new System.EventHandler(Form1_MouseEnter);
            imgLogo.MouseDown += new MouseEventHandler(MouseDown);
            imgLogo.MouseMove += new MouseEventHandler(MouseMove);
            imgLogo.MouseUp += new MouseEventHandler(MouseUp);
            imgAlertType.MouseDown += new MouseEventHandler(MouseDown);
            imgAlertType.MouseMove += new MouseEventHandler(MouseMove);
            imgAlertType.MouseUp += new MouseEventHandler(MouseUp);
           
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            Rectangle workingArea = Screen.GetWorkingArea(this);
            this.Location = getLocation(loc);
            //keep this on top
            this.TopMost = true;
            timer.Interval = timerspeed;
            timer.Start();
            //TODO: Get the html from the maven cloud
            string s = "<head><script language=\"JavaScript\">function jsfunction(strURL){window.open(strURL, \"_blank\",\"height=800 width=800 top=0 left=0 scrollbars=no titlebar=no\");} "
                 +"</script></head><body> "
                + " 		 <p style=\"color:#443361;font-family:verdana, sans-serif; font-size:small\"> Patient matches an AUA Pathway.<br/> "
                + " 		<a href=\"http://mavenmedical.net\" "
                //onclick=\"jsfunction('"+url+"')\"
            +">Click</a> to view the pathway. </p>"
                +" </body></head>";
            browserDisplay.DocumentText = s;
            browserDisplay.Navigating += browser_navigate;
        }
        /// <summary>
        /// On mouse enter of the form, reset the timer and become opaque
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Form1_MouseEnter(object sender, EventArgs e)
        {
            this.Opacity = 1;
            tix = 0;
        }
        private void pictureBox1_Click(object sender, EventArgs e)
        {
            timer.Stop();
            this.Close();
            this.Dispose();
        }
        protected override bool ShowWithoutActivation
        {
            //always display without focus. 
            get { return true; }
        }

        private void timer_Tick(object sender, EventArgs e)
        {
            //you have to count the ticks
            tix++;
            //ensure we're topmost   
            this.TopMost = true;
            //tick the opacity down if we've been counting past 10
            if (tix > 10)
            {
                this.Opacity -= .01;
            }
            if (this.Opacity == 0)
            {
                this.Close();
                this.Dispose();
            }
        }
        private void MouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left)
            {
                return;
            }
            downPoint = new Point(e.X, e.Y);
        }
        private void MouseMove(object sender, MouseEventArgs e)
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
        private void MouseUp(object sender, MouseEventArgs e)
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
        private void browser_navigate(object sender, WebBrowserNavigatingEventArgs e)
        {
            Program.url= e.Url.AbsoluteUri;
            ThreadStart ts = new ThreadStart(launchHardAlert);
            Thread t = new Thread(ts);
            t.SetApartmentState(ApartmentState.STA);
            t.Start();
            this.Visible = false;
            this.Close();
        }
        private void launchHardAlert()
        {
            Program.ShowAlertForm(Program.AlertMode.deskHard);
        }
    }
}
