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
        //the number of ticks of the timer
        private int tix=0;
        //a url to go to 
        private string url = "http://mavenmedical.net";
        //a valid string indicating where the form should render. 
        private string loc = "TL";
        //a point representing the upper left of the form
        private Point downPoint=Point.Empty;
        //a boolean to specify if the form should be moving
        private bool moveForm = false;

        /// <summary>
        /// Call to show the form
        /// </summary>
        /// <param name="inUrl">where do you want to send the browser</param>
        /// <param name="location">the string representing where on the screen this should go. See Program.cs for more info on this string.</param>
        public frmHardAlert(string inUrl, string location)
        {
            loc = location;
            url = inUrl;
            InitializeComponent();
        }

        private void frmHardAlert_Load(object sender, EventArgs e)
        {
            //timer ticks every second
            timer.Interval = 1000;
            timer.Start(); //go
            //navigate to where the user should go
            browserDisplay.Navigate(url);
            //disable the scrollbars
            browserDisplay.ScrollBarsEnabled = false;
            //make the form movable my grabbing the mover
            mover.MouseDown += MouseDown;
            mover.MouseUp += MouseUp;
            mover.MouseMove += MouseMove; 
            //put the form at the right part of the screen and keep it on top
            this.Location = getLocation(loc);
            this.TopMost = true;
        }
        /// <summary>
        /// Close out on clicking the x
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
        /// Do some stuff asynchronously on timer ticks. (Like keeping track of whether we should close out. And managing the clipboard)
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void timer_Tick(object sender, EventArgs e)
        {
            tix += 1;
            this.TopMost = true;
            //automatically close out after 5 minutes. 
            //this is the case where the user doesnt close out, but just puts it behind  his EMR screen. 
            if (tix == 300)
            {
                timer.Stop();
                this.Close();
                this.Dispose();
                return;
            }
            //Take the clipboard text and get it to the clipboard. Then get rid of the clipboard text from the document
            HtmlElement elm = browserDisplay.Document.GetElementById("copiedText");
            if (elm != null) //check to see if the clipboard element is there
            { 
                string copytext = elm.InnerHtml; //if the clipboard element is there, then check the inner text
                if (copytext!=null&&copytext.Length > 0) //if it has inner text, then grab it and remove it so we don't re-copy on future runs 
                {
                    Clipboard.SetText(copytext);
                    elm.InnerText = "";
                }
            }
        }
        /// <summary>
        /// Figure out where to put the form
        /// </summary>
        /// <param name="locstring">The locstring. See Program.cs for more info on this string. </param>
        /// <returns></returns>
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
        /// <summary>
        /// Handle moving the form
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private new void MouseDown(object sender, MouseEventArgs e)
        {
            if (e.Button != MouseButtons.Left)
            {
                return;
            }
            downPoint = new Point(e.X, e.Y);
            moveForm = true;
        }
        /// <summary>
        /// Handle Moving the form
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private new void MouseMove(object sender, MouseEventArgs e)
        {
            if (moveForm)
            {
                this.Top = this.Top + e.Y - downPoint.Y;
                this.Left = this.Left + e.X - downPoint.X;   
            }
        }
        /// <summary>
        /// Handle Moving the form
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private new void MouseUp(object sender, MouseEventArgs e)
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
