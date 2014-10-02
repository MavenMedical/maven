namespace MavenAsDemo
{
    partial class frmAlert
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
        /// 
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(frmAlert));
            this.pictureBox1 = new System.Windows.Forms.PictureBox();
            this.fileSystemWatcher1 = new System.IO.FileSystemWatcher();
            this.timer = new System.Windows.Forms.Timer(this.components);
            this.imgLogo = new System.Windows.Forms.PictureBox();
            this.browserDisplay = new System.Windows.Forms.WebBrowser();
            this.imgAlertType = new System.Windows.Forms.PictureBox();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.fileSystemWatcher1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.imgLogo)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.imgAlertType)).BeginInit();
            this.SuspendLayout();
            // 
            // pictureBox1
            // 
            this.pictureBox1.BackColor = System.Drawing.Color.White;
            this.pictureBox1.Image = global::MavenAsDemo.Properties.Resources.icon_close_small;
            this.pictureBox1.InitialImage = ((System.Drawing.Image)(resources.GetObject("pictureBox1.InitialImage")));
            this.pictureBox1.Location = new System.Drawing.Point(375, 13);
            this.pictureBox1.Name = "pictureBox1";
            this.pictureBox1.Size = new System.Drawing.Size(15, 15);
            this.pictureBox1.TabIndex = 0;
            this.pictureBox1.TabStop = false;
            this.pictureBox1.Click += new System.EventHandler(this.pictureBox1_Click);
            // 
            // fileSystemWatcher1
            // 
            this.fileSystemWatcher1.EnableRaisingEvents = true;
            this.fileSystemWatcher1.SynchronizingObject = this;
            // 
            // timer
            // 
            this.timer.Tick += new System.EventHandler(this.timer_Tick);
            // 
            // imgLogo
            // 
            this.imgLogo.BackColor = System.Drawing.Color.Transparent;
            this.imgLogo.Image = ((System.Drawing.Image)(resources.GetObject("imgLogo.Image")));
            this.imgLogo.Location = new System.Drawing.Point(342, 109);
            this.imgLogo.Name = "imgLogo";
            this.imgLogo.Size = new System.Drawing.Size(60, 40);
            this.imgLogo.SizeMode = System.Windows.Forms.PictureBoxSizeMode.StretchImage;
            this.imgLogo.TabIndex = 1;
            this.imgLogo.TabStop = false;
            this.imgLogo.Click += new System.EventHandler(this.pictureBox2_Click);
            // 
            // browserDisplay
            // 
            this.browserDisplay.IsWebBrowserContextMenuEnabled = false;
            this.browserDisplay.Location = new System.Drawing.Point(68, 25);
            this.browserDisplay.MinimumSize = new System.Drawing.Size(20, 20);
            this.browserDisplay.Name = "browserDisplay";
            this.browserDisplay.ScrollBarsEnabled = false;
            this.browserDisplay.Size = new System.Drawing.Size(320, 113);
            this.browserDisplay.TabIndex = 2;
            // 
            // imgAlertType
            // 
            this.imgAlertType.BackColor = System.Drawing.Color.Transparent;
            this.imgAlertType.BackgroundImage = global::MavenAsDemo.Properties.Resources.flowdarkblue;
            this.imgAlertType.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Stretch;
            this.imgAlertType.Location = new System.Drawing.Point(7, 46);
            this.imgAlertType.Name = "imgAlertType";
            this.imgAlertType.Size = new System.Drawing.Size(52, 50);
            this.imgAlertType.TabIndex = 3;
            this.imgAlertType.TabStop = false;
            // 
            // frmAlert
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.Beige;
            this.BackgroundImage = ((System.Drawing.Image)(resources.GetObject("$this.BackgroundImage")));
            this.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Stretch;
            this.ClientSize = new System.Drawing.Size(400, 150);
            this.Controls.Add(this.imgAlertType);
            this.Controls.Add(this.imgLogo);
            this.Controls.Add(this.pictureBox1);
            this.Controls.Add(this.browserDisplay);
            this.DoubleBuffered = true;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "frmAlert";
            this.Text = "Maven";
            this.TransparencyKey = System.Drawing.Color.Beige;
            this.Load += new System.EventHandler(this.Form1_Load);
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.fileSystemWatcher1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.imgLogo)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.imgAlertType)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion

        private System.Windows.Forms.PictureBox pictureBox1;
        private System.IO.FileSystemWatcher fileSystemWatcher1;
        private System.Windows.Forms.Timer timer;
        private System.Windows.Forms.PictureBox imgLogo;
        private System.Windows.Forms.WebBrowser browserDisplay;
        private System.Windows.Forms.PictureBox imgAlertType;
    }
}

