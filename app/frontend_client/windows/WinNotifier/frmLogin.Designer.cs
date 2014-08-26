namespace MavenAsDemo
{
    partial class frmLogin
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(frmLogin));
            this.pictureBox1 = new System.Windows.Forms.PictureBox();
            this.fileSystemWatcher1 = new System.IO.FileSystemWatcher();
            this.imgLogo = new System.Windows.Forms.PictureBox();
            this.imgKey = new System.Windows.Forms.PictureBox();
            this.txtUser = new System.Windows.Forms.TextBox();
            this.txtPass = new System.Windows.Forms.TextBox();
            this.lblUser = new System.Windows.Forms.Label();
            this.lblPass = new System.Windows.Forms.Label();
            this.chkAutoLogin = new System.Windows.Forms.CheckBox();
            this.btnLogin = new System.Windows.Forms.Button();
            this.lblErr = new System.Windows.Forms.Label();
            this.chkStay = new System.Windows.Forms.CheckBox();
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.fileSystemWatcher1)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.imgLogo)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.imgKey)).BeginInit();
            this.SuspendLayout();
            // 
            // pictureBox1
            // 
            this.pictureBox1.BackColor = System.Drawing.Color.White;
            this.pictureBox1.Image = ((System.Drawing.Image)(resources.GetObject("pictureBox1.Image")));
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
            // imgKey
            // 
            this.imgKey.BackColor = System.Drawing.Color.Transparent;
            this.imgKey.BackgroundImage = global::MavenAsDemo.Properties.Resources.key1;
            this.imgKey.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Stretch;
            this.imgKey.Location = new System.Drawing.Point(3, 48);
            this.imgKey.Name = "imgKey";
            this.imgKey.Size = new System.Drawing.Size(93, 44);
            this.imgKey.TabIndex = 2;
            this.imgKey.TabStop = false;
            // 
            // txtUser
            // 
            this.txtUser.Location = new System.Drawing.Point(182, 12);
            this.txtUser.Name = "txtUser";
            this.txtUser.Size = new System.Drawing.Size(165, 20);
            this.txtUser.TabIndex = 3;
            // 
            // txtPass
            // 
            this.txtPass.Location = new System.Drawing.Point(182, 41);
            this.txtPass.Name = "txtPass";
            this.txtPass.PasswordChar = '*';
            this.txtPass.Size = new System.Drawing.Size(165, 20);
            this.txtPass.TabIndex = 4;
            // 
            // lblUser
            // 
            this.lblUser.AutoSize = true;
            this.lblUser.BackColor = System.Drawing.Color.Transparent;
            this.lblUser.Location = new System.Drawing.Point(144, 17);
            this.lblUser.Name = "lblUser";
            this.lblUser.Size = new System.Drawing.Size(32, 13);
            this.lblUser.TabIndex = 5;
            this.lblUser.Text = "User:";
            // 
            // lblPass
            // 
            this.lblPass.AutoSize = true;
            this.lblPass.BackColor = System.Drawing.Color.Transparent;
            this.lblPass.Location = new System.Drawing.Point(120, 44);
            this.lblPass.Name = "lblPass";
            this.lblPass.Size = new System.Drawing.Size(56, 13);
            this.lblPass.TabIndex = 6;
            this.lblPass.Text = "Password:";
            // 
            // chkAutoLogin
            // 
            this.chkAutoLogin.AutoSize = true;
            this.chkAutoLogin.BackColor = System.Drawing.Color.Transparent;
            this.chkAutoLogin.Checked = true;
            this.chkAutoLogin.CheckState = System.Windows.Forms.CheckState.Checked;
            this.chkAutoLogin.Location = new System.Drawing.Point(182, 75);
            this.chkAutoLogin.Name = "chkAutoLogin";
            this.chkAutoLogin.Size = new System.Drawing.Size(127, 17);
            this.chkAutoLogin.TabIndex = 7;
            this.chkAutoLogin.Text = "Launch Automatically";
            this.chkAutoLogin.UseVisualStyleBackColor = false;
            // 
            // btnLogin
            // 
            this.btnLogin.BackColor = System.Drawing.SystemColors.Control;
            this.btnLogin.Location = new System.Drawing.Point(182, 116);
            this.btnLogin.Name = "btnLogin";
            this.btnLogin.Size = new System.Drawing.Size(75, 23);
            this.btnLogin.TabIndex = 8;
            this.btnLogin.Text = "Login";
            this.btnLogin.UseVisualStyleBackColor = false;
            this.btnLogin.Click += new System.EventHandler(this.btnLogin_Click_1);
            // 
            // lblErr
            // 
            this.lblErr.AutoSize = true;
            this.lblErr.BackColor = System.Drawing.Color.White;
            this.lblErr.ForeColor = System.Drawing.Color.DarkRed;
            this.lblErr.Location = new System.Drawing.Point(61, 121);
            this.lblErr.Name = "lblErr";
            this.lblErr.Size = new System.Drawing.Size(0, 13);
            this.lblErr.TabIndex = 9;
            // 
            // chkStay
            // 
            this.chkStay.AutoSize = true;
            this.chkStay.BackColor = System.Drawing.Color.Transparent;
            this.chkStay.Checked = true;
            this.chkStay.CheckState = System.Windows.Forms.CheckState.Checked;
            this.chkStay.Location = new System.Drawing.Point(182, 93);
            this.chkStay.Name = "chkStay";
            this.chkStay.Size = new System.Drawing.Size(98, 17);
            this.chkStay.TabIndex = 10;
            this.chkStay.Text = "Stay Logged In";
            this.chkStay.UseVisualStyleBackColor = false;
            // 
            // frmLogin
            // 
            this.AcceptButton = this.btnLogin;
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.Beige;
            this.BackgroundImage = ((System.Drawing.Image)(resources.GetObject("$this.BackgroundImage")));
            this.BackgroundImageLayout = System.Windows.Forms.ImageLayout.Stretch;
            this.ClientSize = new System.Drawing.Size(400, 150);
            this.Controls.Add(this.chkStay);
            this.Controls.Add(this.lblErr);
            this.Controls.Add(this.btnLogin);
            this.Controls.Add(this.chkAutoLogin);
            this.Controls.Add(this.lblPass);
            this.Controls.Add(this.lblUser);
            this.Controls.Add(this.txtPass);
            this.Controls.Add(this.txtUser);
            this.Controls.Add(this.imgKey);
            this.Controls.Add(this.imgLogo);
            this.Controls.Add(this.pictureBox1);
            this.DoubleBuffered = true;
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.None;
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "frmLogin";
            this.Text = "Maven";
            this.TransparencyKey = System.Drawing.Color.Beige;
            this.Load += new System.EventHandler(this.FormLogin_Load);
            ((System.ComponentModel.ISupportInitialize)(this.pictureBox1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.fileSystemWatcher1)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.imgLogo)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.imgKey)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.PictureBox pictureBox1;
        private System.IO.FileSystemWatcher fileSystemWatcher1;
        private System.Windows.Forms.PictureBox imgLogo;
        private System.Windows.Forms.PictureBox imgKey;
        private System.Windows.Forms.CheckBox chkAutoLogin;
        private System.Windows.Forms.Label lblPass;
        private System.Windows.Forms.Label lblUser;
        private System.Windows.Forms.TextBox txtPass;
        private System.Windows.Forms.TextBox txtUser;
        private System.Windows.Forms.Button btnLogin;
        private System.Windows.Forms.Label lblErr;
        private System.Windows.Forms.CheckBox chkStay;
    }
}

