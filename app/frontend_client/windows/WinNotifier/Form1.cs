using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace MavenAsDemo
{
    public partial class frmAlert : Form
    {
        //track how many ticks since the timer was reset
        public int tix = 0;
        public Point downPoint=Point.Empty;
        public int timerspeed = 200;

        public frmAlert(double fadeslowness)
        {
            try
            {
                timerspeed = Convert.ToInt32(Math.Round(50 * fadeslowness, 0));
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
           
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            //make the background transparent and whiteish so the white overlay is visible and the shadow appears to be ontop of white. 
            //this.BackColor = System.Drawing.Color.Gray;
            //this.TransparencyKey=System.Drawing.Color.Gray;
            //go to the bottom right + 15px vertical 
            Rectangle workingArea = Screen.GetWorkingArea(this);
            this.Location = new Point(workingArea.Right - Size.Width-10,
                                      workingArea.Bottom - Size.Height-15);
            //keep this on top
            this.TopMost = true;
            timer.Interval = timerspeed;
            timer.Start();
            browserDisplay.DocumentText = "<head><script language=\"JavaScript\">function jsfunction(strURL){window.open(strURL, \"_blank\",\"height=800 width=800 top=0 left=0 scrollbars=no titlebar=no\");} "
                +"</script></head><body>Click <a href=\"#\" onclick=\"jsfunction('http://mavenmedical.net')\">here</a> to see the Maven website</body>";
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
    }
}
