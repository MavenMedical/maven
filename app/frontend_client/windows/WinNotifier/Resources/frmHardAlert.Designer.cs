namespace MavenAsDemo
{
    partial class frmHardAlert
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.browserDisplay = new System.Windows.Forms.WebBrowser();
            this.timer = new System.Windows.Forms.Timer(this.components);
            this.shapeContainer1 = new Microsoft.VisualBasic.PowerPacks.ShapeContainer();
            this.mover = new Microsoft.VisualBasic.PowerPacks.RectangleShape();
            this.boxHeader = new Microsoft.VisualBasic.PowerPacks.RectangleShape();
            this.btnMinMax = new System.Windows.Forms.PictureBox();
            this.btnclose = new System.Windows.Forms.PictureBox();
            ((System.ComponentModel.ISupportInitialize)(this.btnMinMax)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.btnclose)).BeginInit();
            this.SuspendLayout();
            // 
            // browserDisplay
            // 
            this.browserDisplay.Location = new System.Drawing.Point(2, 21);
            this.browserDisplay.MinimumSize = new System.Drawing.Size(20, 20);
            this.browserDisplay.Name = "browserDisplay";
            this.browserDisplay.ScriptErrorsSuppressed = true;
            this.browserDisplay.Size = new System.Drawing.Size(1020, 745);
            this.browserDisplay.TabIndex = 2;
            this.browserDisplay.DocumentCompleted += new System.Windows.Forms.WebBrowserDocumentCompletedEventHandler(this.browserDisplay_DocumentCompleted);
            // 
            // timer
            // 
            this.timer.Interval = 1000;
            this.timer.Tick += new System.EventHandler(this.timer_Tick);
            // 
            // shapeContainer1
            // 
            this.shapeContainer1.Location = new System.Drawing.Point(0, 0);
            this.shapeContainer1.Margin = new System.Windows.Forms.Padding(0);
            this.shapeContainer1.Name = "shapeContainer1";
            this.shapeContainer1.Shapes.AddRange(new Microsoft.VisualBasic.PowerPacks.Shape[] {
            this.mover,
            this.boxHeader});
            this.shapeContainer1.Size = new System.Drawing.Size(1024, 768);
            this.shapeContainer1.TabIndex = 3;
            this.shapeContainer1.TabStop = false;
            // 
            // mover
            // 
            this.mover.BackColor = System.Drawing.Color.Transparent;
            this.mover.BorderColor = System.Drawing.Color.Transparent;
            this.mover.Location = new System.Drawing.Point(-1, -95);
            this.mover.Name = "mover";
            this.mover.Size = new System.Drawing.Size(1024, 200);
            // 
            // boxHeader
            // 
            this.boxHeader.BorderColor = System.Drawing.Color.WhiteSmoke;
            this.boxHeader.FillColor = System.Drawing.Color.WhiteSmoke;
            this.boxHeader.FillGradientColor = System.Drawing.Color.Gainsboro;
            this.boxHeader.FillStyle = Microsoft.VisualBasic.PowerPacks.FillStyle.Solid;
            this.boxHeader.Location = new System.Drawing.Point(2, 2);
            this.boxHeader.Name = "boxHeader";
            this.boxHeader.Size = new System.Drawing.Size(1019, 18);
            // 
            // btnMinMax
            // 
            this.btnMinMax.BackColor = System.Drawing.Color.WhiteSmoke;
            this.btnMinMax.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom;
            this.btnMinMax.ErrorImage = null;
            this.btnMinMax.Image = global::MavenAsDemo.Properties.Resources.minmax;
            this.btnMinMax.InitialImage = null;
            this.btnMinMax.Location = new System.Drawing.Point(979, 3);
            this.btnMinMax.Name = "btnMinMax";
            this.btnMinMax.Size = new System.Drawing.Size(25, 15);
            this.btnMinMax.TabIndex = 4;
            this.btnMinMax.TabStop = false;
            this.btnMinMax.Click += new System.EventHandler(this.btnMinMax_Click);
            // 
            // btnclose
            // 
            this.btnclose.BackColor = System.Drawing.Color.WhiteSmoke;
            this.btnclose.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Zoom;
            this.btnclose.ErrorImage = null;
            this.btnclose.Image = global::MavenAsDemo.Properties.Resources.icon_close_small;
            this.btnclose.InitialImage = null;
            this.btnclose.Location = new System.Drawing.Point(1007, 3);
            this.btnclose.Name = "btnclose";
            this.btnclose.Size = new System.Drawing.Size(15, 15);
            this.btnclose.TabIndex = 1;
            this.btnclose.TabStop = false;
            this.btnclose.Click += new System.EventHandler(this.pictureBox1_Click);
            // 
            // frmHardAlert
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.LightGray;
            this.ClientSize = new System.Drawing.Size(1024, 768);
            this.Controls.Add(this.btnMinMax);
            this.Controls.Add(this.btnclose);
            this.Controls.Add(this.browserDisplay);
            this.Controls.Add(this.shapeContainer1);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            this.Name = "frmHardAlert";
            this.Text = "Maven Pathways";
            this.Load += new System.EventHandler(this.frmHardAlert_Load);
            ((System.ComponentModel.ISupportInitialize)(this.btnMinMax)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.btnclose)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.PictureBox btnclose;
        private System.Windows.Forms.WebBrowser browserDisplay;
        private System.Windows.Forms.Timer timer;
        private Microsoft.VisualBasic.PowerPacks.ShapeContainer shapeContainer1;
        private Microsoft.VisualBasic.PowerPacks.RectangleShape boxHeader;
        private Microsoft.VisualBasic.PowerPacks.RectangleShape mover;
        private System.Windows.Forms.PictureBox btnMinMax;
    }
}