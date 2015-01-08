using System;
using System.Collections.Generic;
using System.Text;
using System.IO;
using System.Diagnostics;
//using System.Windows.Input;
using System.Threading;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using System.Collections;
using System.Management;

namespace MavenAsDemo
{
    class AllScriptsProLoginTracker
    {
        public bool isEmrUserLoggedIn = false;
        public int attachedEMRProcess = -99999;

        private string emrUser = "";
        private bool wasloggedin = false;
        private string curname = System.Security.Principal.WindowsIdentity.GetCurrent().Name;
        private ArrayList curchildren = new ArrayList();
        private bool keepgoing = true;
        private string loginkeys = "";
        private bool strangerLogin = false; //tracks whether a "stranger" is logged into the emr
        private DateTime firstattachtime = DateTime.MinValue; //tracks whether this is the first time we're attaching to something in this session

        public AllScriptsProLoginTracker(string emrUserName)
        {
            emrUser = emrUserName.ToUpper();
        }
        private void StartTracking()
        {
            while (keepgoing)
            {
                GetActiveEmrWindowState();
                Thread.Sleep(1000);
            }
        }
        public void Start()
        {
            keepgoing = true;
            ThreadStart start = new ThreadStart(StartTracking);
            Thread thrd = new Thread(start);
            thrd.IsBackground = true;
            thrd.Start();
        }
        public void Stop()
        {
            keepgoing = false;
        }
        private int CurEmrWindowProcess(int windowHandle)
        {
            int rtn = -1;
            int pid = 0;
            GetWindowThreadProcessId(new IntPtr(windowHandle), out pid);
            ManagementObjectSearcher procs = new ManagementObjectSearcher("SELECT * FROM Win32_Process where Name='EMR.exe' and ProcessId=" + pid.ToString());
            //TODO: Determine if this process has alread been attached by someone else...
            foreach (ManagementObject proc in procs.Get())
            {
                rtn = pid;
            }
            return rtn;
        }
        private void GetActiveEmrWindowState()
        {

            bool ProcessLoggedin = true; //seems safest to start by assuming we're logged in and ask for verification. Side effect of not being logged in is keylogging on the attached process id. 
            int handle = 0;
            handle = GetForegroundWindow();
            string active = writeWindoInfo(handle);
            //if you're not currently attached to a process then try to attach to the current emr window
            int curemrprocid = CurEmrWindowProcess(handle);
            if (curemrprocid > 0 && attachedEMRProcess == -99999)
            {
                attachedEMRProcess = curemrprocid;
                Logger.Log("Attaching to EMR process " + curemrprocid,"EmrTracking");
                //ok, you're attaching to an emr process. assume that it was logged in. if it turns out it isnt, we just treat it as an immediate logout
                //wasloggedin = true;
            }
            //if the Attached emr window has focus, see if it's logged in
            if (curemrprocid == attachedEMRProcess )
            {
                GetAllWindows(handle);
                ProcessLoggedin=getisEmrUserLoggedIn(curchildren, active);
                if (ProcessLoggedin & !strangerLogin)
                {
                    isEmrUserLoggedIn = true; //if it's logged in and not a stranger, then go for it. 
                }
                if (!ProcessLoggedin)
                {
                    strangerLogin = false;
                    isEmrUserLoggedIn = false;
                }
            }
            else //if the emr is not focussed, check if allscripts is even running
            {
                //look for EMR.exe
                if (!IsEmrRunning())
                {
                    isEmrUserLoggedIn = false;//if none then set isEmrUserLoggedIn=false;
                    strangerLogin = false;
                    attachedEMRProcess = -99999;
                }

            }
            //if the status of login has changed, do something about it
            if (isEmrUserLoggedIn != wasloggedin)
            {
                if (isEmrUserLoggedIn && firstattachtime == DateTime.MinValue)//we have logged in successfully, anything after this is nolonger the first attach
                {
                    firstattachtime = DateTime.Now;
                    Logger.Log("Initiated logging for the first time in this session.", "EmrTracking");
                }
                log(isEmrUserLoggedIn);
                if (isEmrUserLoggedIn)
                {
                    //first see if this is a login for the user we're polling for. If this is the first time we're attaching, let it slide (maven might be slow to launch and miss some login keys)
                    if (!closeEnough(loginkeys).Contains(closeEnough(emrUser)) && firstattachtime.AddSeconds(5)<DateTime.Now)
                    {
                        isEmrUserLoggedIn = false; //switch back. our user is still logged out
                        string msg = "We suspect that the user who logged into the EMR is not " + emrUser + ", therefore alerting will remain suspended for the time being. " + DateTime.Now.ToLongTimeString();
                        Logger.Log(msg, "EmrTracking");
                        strangerLogin = true;
                    }
                    //if this is a new login, wipe the login string
                    loginkeys = "";
                }

            }

            //check to see if we're in the process of logging in with the same user
            if (!ProcessLoggedin && curemrprocid == attachedEMRProcess)
            {
                //if we;re logged out and the emr has focus, see if the login is for our user
                string tst = logKeys(handle);
                loginkeys += tst;
            }
            wasloggedin = isEmrUserLoggedIn;//update wasloggedin to the current status

            curchildren = new ArrayList();

        }

        private void log(bool loggedin)
        {
            string msg = "";
            if (!loggedin)
            {
                msg = "The user logged out of the EMR at " + DateTime.Now.ToLongTimeString() + ". Alerting is paused.";
            }
            else
            {
                msg = "The user logged into the EMR at " + DateTime.Now.ToLongTimeString() + ". Alerting has been resumed.";

            }
            Logger.Log(msg, "EmrTracking");
        }

        private ArrayList GetAllWindows(int handle)
        {
            curchildren = new ArrayList();
            ArrayList windowHandles = new ArrayList();
            EnumedWindow callBackPtr = GetWindowHandle;
            EnumChildWindows(new IntPtr(handle), callBackPtr, windowHandles);

            return windowHandles;
        }
        private static bool getisEmrUserLoggedIn(ArrayList list, string WindowTitle)
        {
            if (WindowTitle=="Login")
            {//if it's an EMR.exe, but the window title doesnt says "Login" then you've just launched the EXE. You're not logged in. 
                return false;
            }
            int logincount = 0;
            foreach (string str in list)
            {
                if (str == "Login")
                {
                    logincount += 1;
                }
            }
            if (logincount == 2)
            {
                return false;
            }
            else { return true; }
        }
        private bool IsEmrRunning()
        {
            bool rtn = false;
            ManagementObjectSearcher procs = new ManagementObjectSearcher("SELECT * FROM Win32_Process where Name='EMR.exe'");
            foreach (ManagementObject proc in procs.Get())
            {
                if (proc["ExecutablePath"] != null)
                {
                    string ExecutablePath = proc["ExecutablePath"].ToString();

                    string[] OwnerInfo = new string[2];
                    proc.InvokeMethod("GetOwner", (object[])OwnerInfo);

                    string owner = OwnerInfo[1] + "\\" + OwnerInfo[0];
                    if (owner == curname)
                    {
                        rtn = true;
                    }
                }
            }

            return rtn;
        }
        private delegate bool EnumedWindow(IntPtr handleWindow, ArrayList handles);
        private string logKeys(int WindowhandleToLog)
        {
            string rtn = "";
            while (WindowhandleToLog == GetForegroundWindow())
            {

                string debug="";
                foreach (System.Int32 i in Enum.GetValues(typeof(Keys)))
                {
                    debug+="\r\n"+((Keys)i).ToString();;
                    int keyState = GetAsyncKeyState(i);
                    if (keyState == 1 || keyState == -32767)
                    {
                        if (i == 8)
                        {
                            try
                            {
                                rtn = rtn.Substring(0, rtn.Length - 1);
                            }
                            catch { /*you backspaced past the end of the string*/}
                            break;
                        }
                        else
                        {
                            string k = ((Keys)i).ToString();
                            /*if (k.Length == 2 && k.StartsWith("D"))
                            {
                                k = k.Substring(1);
                            }
                            else if (k.Contains("ShiftKey")) { k = ""; }//handle shift keys through the close-enough function. 
                            rtn += k.Replace("NumPad", "Oem");*/
                            rtn += keycatchFormat(k);
                            break;
                        }
                    }
                }
                Thread.Sleep(10);
            }
            return keycatchFormat(rtn);
        }
        /// for matching usernames, this gets a string that is "Close enough" to match on. 
        /// </summary>
        /// <param name="input"></param>
        /// <returns>A comparison string that is "Close enough"</returns>
        string closeEnough(string input)
        {
            string rtn = input.Replace("!", "1");
            rtn = rtn.Replace("@", "2");
            rtn = rtn.Replace("#", "3");
            rtn = rtn.Replace("$", "4");
            rtn = rtn.Replace("%", "5");
            rtn = rtn.Replace("^", "6");
            rtn = rtn.Replace("&", "7");
            rtn = rtn.Replace("*", "8");
            rtn = rtn.Replace("(", "9");
            rtn = rtn.Replace(")", "0");
            rtn = rtn.Replace("_", "-");
            rtn = rtn.Replace("+", "=");
            rtn = rtn.Replace("~", "`");
            rtn = rtn.Replace(">", ".");
            rtn = rtn.Replace("<", ",");
            rtn = rtn.Replace("?", "/");
            rtn = rtn.Replace("'", "\"");
            rtn = rtn.Replace("|", "\\");
            rtn = rtn.Replace("{", "[");
            rtn = rtn.Replace("}", "]");
            rtn = rtn.Replace(":", ";");
            return rtn;
        }
        /// <summary>
        /// do your best to convert the string we got back into an exact string that was typed. 
        /// This isnt perfect because of little things like uncommonly used characters, etc. And the fact that you might hold the shift key. 
        /// For example, if you hold the Shift key, This "TesT__123!!" might come through like this "TesT--123!1"
        /// </summary>
        /// <param name="input"></param>
        /// <returns>the best we can do to get the exact string.</returns>
        private string keycatchFormat(string input)
        {
            if (input == "None"
                || input == "LButton"
                || input == "RButton"
                || input == "Cancel"
                || input == "MButton"
                || input == "XButton1"
                || input == "XButton2"
                || input == "Tab"
                || input == "LineFeed"
                || input == "Clear"
                || input == "Return"
                || input == "Return"
                || input == "ShiftKey"
                || input == "ControlKey"
                || input == "Menu"
                || input == "Pause"
                || input == "Capital"
                || input == "Capital"
                || input == "KanaMode"
                || input == "KanaMode"
                || input == "KanaMode"
                || input == "JunjaMode"
                || input == "FinalMode"
                || input == "HanjaMode"
                || input == "HanjaMode"
                || input == "Escape"
                || input == "IMEConvert"
                || input == "IMENonconvert"
                || input == "IMEAceept"
                || input == "IMEAceept"
                || input == "IMEModeChange"
                || input == "PageUp"
                || input == "PageUp"
                || input == "Next"
                || input == "Next"
                || input == "End"
                || input == "Home"
                || input == "Left"
                || input == "Up"
                || input == "Right"
                || input == "Down"
                || input == "Select"
                || input == "Print"
                || input == "Execute"
                || input == "PrintScreen"
                || input == "PrintScreen"
                || input == "Insert"
                || input == "Help"
                || input == "LWin"
                || input == "RWin"
                || input == "Apps"
                || input == "Sleep"
                || input == "Separator"
                || input == "F1"
                || input == "F2"
                || input == "F3"
                || input == "F4"
                || input == "F5"
                || input == "F6"
                || input == "F7"
                || input == "F8"
                || input == "F9"
                || input == "F10"
                || input == "F11"
                || input == "F12"
                || input == "F13"
                || input == "F14"
                || input == "F15"
                || input == "F16"
                || input == "F17"
                || input == "F18"
                || input == "F19"
                || input == "F20"
                || input == "F21"
                || input == "F22"
                || input == "F23"
                || input == "F24"
                || input == "NumLock"
                || input == "Scroll"
                || input == "LShiftKey"
                || input == "RShiftKey"
                || input == "LControlKey"
                || input == "RControlKey"
                || input == "LMenu"
                || input == "RMenu"
                || input == "BrowserBack"
                || input == "BrowserForward"
                || input == "BrowserRefresh"
                || input == "BrowserStop"
                || input == "BrowserSearch"
                || input == "BrowserFavorites"
                || input == "BrowserHome"
                || input == "VolumeMute"
                || input == "VolumeDown"
                || input == "VolumeUp"
                || input == "MediaNextTrack"
                || input == "MediaPreviousTrack"
                || input == "MediaStop"
                || input == "MediaPlayPause"
                || input == "LaunchMail"
                || input == "SelectMedia"
                || input == "LaunchApplication1"
                || input == "LaunchApplication2"
                || input == "ProcessKey"
                || input == "Packet"
                || input == "Attn"
                || input == "Crsel"
                || input == "Exsel"
                || input == "EraseEof"
                || input == "Play"
                || input == "Zoom"
                || input == "NoName"
                || input == "Pa1"
                || input == "OemClear"
                || input == "KeyCode"
                || input == "Shift"
                || input == "Control"
                || input == "Alt"
                || input == "Modifiers"
            )
            {
                input = "";
            }
            else if (input == "Space") { input = " "; }
            else if (input == "Subtract") { input = "-"; }
            else if (input == "OemMinus") { input = "-"; }
            else if (input == "Multiply") { input = "*"; }
            else if (input == "Oemcomma") { input = ","; }
            else if (input == "Decimal") { input = "."; }
            else if (input == "OemPeriod") { input = "."; }
            else if (input == "Divide") { input = "/"; }
            else if (input == "OemQuestion") { input = "?"; }
            else if (input == "OemOpenBrackets") { input = "["; }
            else if (input == "OemBackslash") { input = "\\"; }
            else if (input == "OemBackslash") { input = "\\"; }
            else if (input == "Oemtilde") { input = "~"; }
            else if (input == "Add") { input = "+"; }
            else if (input == "Oemplus") { input = "+"; }
            else if (input == "D0") { input = "0"; }
            else if (input == "NumPad0") { input = "0"; }
            else if (input == "D1") { input = "1"; }
            else if (input == "NumPad1") { input = "1"; }
            else if (input == "Oem1") { input = ";"; }
            else if (input == "D2") { input = "2"; }
            else if (input == "NumPad2") { input = "2"; }
            else if (input == "D3") { input = "3"; }
            else if (input == "NumPad3") { input = "3"; }
            else if (input == "D4") { input = "4"; }
            else if (input == "NumPad4") { input = "4"; }
            else if (input == "D5") { input = "5"; }
            else if (input == "NumPad5") { input = "5"; }
            else if (input == "Oem5") { input = "\\"; }
            else if (input == "D6") { input = "6"; }
            else if (input == "NumPad6") { input = "6"; }
            else if (input == "Oem6") { input = "]"; }
            else if (input == "D7") { input = "7"; }
            else if (input == "NumPad7") { input = "7"; }
            else if (input == "Oem7") { input = "\""; }
            else if (input == "D8") { input = "8"; }
            else if (input == "NumPad8") { input = "8"; }
            else if (input == "Oem8") { input = "8"; }
            else if (input == "D9") { input = "9"; }
            else if (input == "NumPad9") { input = "9"; }

            return input;
        }
        private string writeWindoInfo(int handle)
        {

            string rtn = "";
            const int nChars = 256;
            StringBuilder Buff = new StringBuilder(nChars);
            if (GetWindowText(handle, Buff, nChars) > 0)
            {
                rtn = Buff.ToString();
                curchildren.Add(rtn);
            }
            return rtn;
        }

        private bool GetWindowHandle(IntPtr windowHandle, ArrayList windowHandles)
        {
            windowHandles.Add(windowHandle);
            writeWindoInfo(windowHandle.ToInt32());
            return true;
        }
        [DllImport("user32.dll")]
        [return: MarshalAs(UnmanagedType.Bool)]
        private static extern bool EnumChildWindows(IntPtr window, EnumedWindow callback, ArrayList lParam);

        [DllImport("user32.dll")]
        private static extern int GetForegroundWindow();

        [DllImport("user32.dll")]
        private static extern int GetWindowText(int hWnd, StringBuilder text, int count);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern uint GetWindowThreadProcessId(IntPtr hWnd, out int lpdwProcessId);

        [DllImport("user32.dll")]
        static extern short GetAsyncKeyState(int vKey);
    }
}
