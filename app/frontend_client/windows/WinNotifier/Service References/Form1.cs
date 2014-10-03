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
        private int tix = 0;
        //where should i render myself?
        private Point downPoint = Point.Empty;
        //how fast should i [as mike tyson would say] "fade into Bolivia"
        private int timerspeed = 200;
        //let's start by assuming i will render in the bottom right
        private string loc = "BR";
        //I  store the place we're supposed to navigate to 
        private string url = "http://mavenmedical.net";
        /// <summary>
        /// Creates the form object.
        /// </summary>
        /// <param name="fadeslowness">Give me a number between 1 and 10ish to say how slowly to fade. 1 is fast.</param>
        /// <param name="location">give me a string that tells me where to render myself. See the documentation in Program.cs for valid strings. Invalid strings are handled gracefully, but don't be THAT guy...</param>
        /// <param name="inUrl">where do you want me to sent the doc on click?</param>
        public frmAlert(double fadeslowness,string location,string inUrl)
        {
            try
            {
                //set things up and initialize. 
                timerspeed = Convert.ToInt32(Math.Round(50 * fadeslowness, 0));
                loc = location;
                url = inUrl;
                InitializeComponent();
            }
            catch (System.Threading.ThreadAbortException ex)
            {
                Program.LogMessage("frmAlert Exception: " + ex.Message);
                this.Close();
                this.Dispose();
            }
        }
        /// <summary>
        /// Lights, camera, action
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void Form1_Load(object sender, EventArgs e)
        {
            //custom event handlers
            //the form should unfade on mouseover
            this.MouseEnter += new System.EventHandler(Form1_MouseEnter);
            //make the form dragable on the logo or the other picture
            imgLogo.MouseDown += new MouseEventHandler(MouseDown);
            imgLogo.MouseMove += new MouseEventHandler(MouseMove);
            imgLogo.MouseUp += new MouseEventHandler(MouseUp);
            imgAlertType.MouseDown += new MouseEventHandler(MouseDown);
            imgAlertType.MouseMove += new MouseEventHandler(MouseMove);
            imgAlertType.MouseUp += new MouseEventHandler(MouseUp);
           
            //double check a few important style things. 
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
                + " 		 <p style=\"color:#443361;font-family:verdana, sans-serif; font-size:small\">There is a standard of care for this patient.<br/> "
                + " 		<a href=\""+url+"\" "
                //onclick=\"jsfunction('"+url+"')\"
            +">Click</a> to view the pathway. </p>"
                +" </body></head>";
            browserDisplay.DocumentText = s;

            //This is actually very important. Capture the hyperlink and instead of launching in a browser, launch in the hard alert custom control. 
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
        /// <summary>
        /// close out if the x is clicked
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void pictureBox1_Click(object sender, EventArgs e)
        {
            timer.Stop();
            this.Close();
            this.Dispose();
        }
        /// <summary>
        /// keep ontop stuff. 
        /// </summary>
        protected override bool ShowWithoutActivation
        {
            //always display without focus. 
            get { return true; }
        }
        /// <summary>
        /// Stuff that we can do asynchronously as the form is being displayed. 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void timer_Tick(object sender, EventArgs e)
        {
            //you have to count the ticks
            tix++;
            //ensure we're topmost   
            //this.TopMost = true;
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
        /// <summary>
        /// Take the location string and convert it to a point that specifies where the form will be drawn. 
        /// </summary>
        /// <param name="locstring">A string that helps me figure out where to  draw the form.</param>
        /// <returns></returns>
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
        /// <summary>
        /// When the browser navigates (a url clicked) capture it here and handle it in a custom way. 
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
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
        /// <summary>
        /// launch the hard alert
        /// </summary>
        private void launchHardAlert()
        {
            Program.ShowAlertForm(Settings.AlertMode.deskHard);
        }
    }
}
