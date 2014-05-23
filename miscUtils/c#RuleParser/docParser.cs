using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Collections;
using Microsoft.Office.Interop.Word;
using System.Text.RegularExpressions;
using Npgsql;

namespace ChoosingWiselyDocParser
{
    class Program
    {
        public static NpgsqlConnection db=new NpgsqlConnection("Server=192.168.40.133;Port=5432;Database=maven;User Id=maven;Password=temporary;");
        static void Main(string[] args)
        {
            DirectoryInfo di=new DirectoryInfo(@"C:\Users\dave\MavenDrive\Choosing Wisely Review\technical encoding");
            Application word = new Application();
            Document doc = new Document();
            object missing = System.Type.Missing;
            object tru = true;
            foreach (FileInfo fi in di.GetFiles("*.docx"))
            {
                object fn = fi.FullName;
                doc = word.Documents.Open(ref fn,
                    ref missing, ref tru, ref missing, ref missing,
                    ref missing, ref missing, ref missing, ref missing,
                    ref missing, ref missing, ref missing, ref missing,
                    ref missing, ref missing, ref missing);
                string doctext = "";
                foreach (Paragraph para in doc.Paragraphs)
                {

                    doctext += para.Range.Text;
                }
                ArrayList remlines = new ArrayList();
                string codetype="CPT";
                string[] trigs = GetTrigcodes(doctext, ref remlines,ref codetype);
                string[] encdx = GetEncDxcodes(ref remlines);
                string[] problist = GetPLDxcodes(ref remlines);
                decimal minage = -1;
                decimal maxage = -1;
                string rulename = fi.Name.Replace(".docx", "");
                getAges(ref remlines, ref minage, ref maxage);
                string sex=getSex(ref remlines);
                string details = getDetails(remlines);
                doc.Close();
                InsertRule(rulename, minage, maxage, sex, codetype, details, trigs, encdx, problist);
            }
            
        }
        public static string getDetails(ArrayList remlines)
        {
            string rtn = "{\"details\":[";
            string pattern = "\\{.*\\}";
            int id = 0;
            foreach (string cur in remlines)
            {
                if (cur.Contains("{"))
                {
                    rtn += Regex.Match(cur, pattern).Value.Replace("”", "\"").Replace("“", "\"").Replace("{","{\"id\":"+id+",") + ",";
                    id += 1;
                }
            }
            return rtn.TrimEnd(',')+"]}";
        }
        public static string[] GetTrigcodes(string doctxt, ref ArrayList RemainingLines,ref string codetype)
        {
            codetype="CPT";
            RemainingLines = new ArrayList();
            ArrayList al = new ArrayList();
            doctxt = doctxt.Replace("\r", "|");
            string[] lines = doctxt.Split('|');
            int i = 0;
            bool inPtrigBlock = false;
            while (i < lines.Count())
            {
                string cur = lines[i];
                if (cur.Contains("ptrig")) inPtrigBlock=true;
                if (cur.Contains("/ptrig")) inPtrigBlock=false;
                if (inPtrigBlock && !cur.Contains("ptrig") && cur.Contains("{"))
                {
                    string trigcode = cur.Split('{')[1].Replace("trigcode:", "").Replace("}", "").Trim();
                    al.Add(trigcode);
                }
                else if (inPtrigBlock && cur.Contains("CODETYPE"))
                {
                    codetype=cur.Split(':')[1].Trim();
                }
                else
                {
                    RemainingLines.Add(cur);
                }
                i++;
            }

            string[] rtn=new string[al.Count];
            al.CopyTo(rtn);
            return rtn;
        }
        public static string[] GetEncDxcodes(ref ArrayList RemainingLines)
        {

            ArrayList al = new ArrayList();
            string[] lines=new string[RemainingLines.Count];
            RemainingLines.CopyTo(lines);
            RemainingLines = new ArrayList();
            int i = 0;
            bool inPtrigBlock = false;
            while (i < lines.Count())
            {
                string cur = lines[i];
                if (cur.Contains("dxor")) inPtrigBlock = true;
                if (cur.Contains("/dxor")) inPtrigBlock = false;
                if (inPtrigBlock && !cur.Contains("dxor") && cur.Contains("{"))
                {
                    string trigcode = cur.Split('{')[1].Replace("\"", "").Replace("type:encounter_dx","").Replace("exists:true","").Replace("snomed:","").Replace(",","").Replace("}", "").Trim();
                    al.Add(trigcode);
                }
                else
                {
                    RemainingLines.Add(cur);
                }
                i++;
            }

            string[] rtn = new string[al.Count];
            al.CopyTo(rtn);
            return rtn;
        }
        public static string[] GetPLDxcodes(ref ArrayList RemainingLines)
        {

            ArrayList al = new ArrayList();
            string[] lines = new string[RemainingLines.Count];
            RemainingLines.CopyTo(lines);
            RemainingLines = new ArrayList();
            int i = 0;
            bool inPtrigBlock = false;
            while (i < lines.Count())
            {
                string cur = lines[i];
                if (cur.Contains("plor")) inPtrigBlock = true;
                if (cur.Contains("/plor")) inPtrigBlock = false;
                if (inPtrigBlock && !cur.Contains("plor")&&cur.Contains("{"))
                {
                    string trigcode = cur.Split('{')[1].Replace("\"", "").Replace("type:problem_list", "").Replace("exists:true", "").Replace("snomed:", "").Replace(",", "").Replace("}", "").Trim();
                    al.Add(trigcode);
                }
                else
                {
                    RemainingLines.Add(cur);
                }
                i++;
            }

            string[] rtn = new string[al.Count];
            al.CopyTo(rtn);
            return rtn;
        }
        public static string getSex(ref ArrayList RemainngLines)
        {
            string rtn="*";
            ArrayList newRemLine = new ArrayList();
            foreach (string line in RemainngLines)
            {
                if (line.Contains("{SEX"))
                {
                    string[] parts = line.Split(':');
                    rtn = parts[1].Substring(0,1).ToUpper();
                }
                else { newRemLine.Add(line); }
            }
            RemainngLines = newRemLine;
            return rtn;
        }
        public static void getAges(ref ArrayList RemainngLines, ref decimal min, ref decimal max)
        {
            min = 0;
            max = 200;
            ArrayList newRemLine = new ArrayList();
            foreach (string line in RemainngLines)
            {
                if (line.Contains("{AGE"))
                {
                    string[] parts = line.Split(':');
                    min = Convert.ToDecimal(parts[1]);
                    max = Convert.ToDecimal(parts[2].Replace("}", "").Trim());
                }
                else { newRemLine.Add(line); }
            }
            RemainngLines = newRemLine;
        }
        public static int getRuleId(string name)
        {
            int rtn = -1;;
            NpgsqlCommand sql = new NpgsqlCommand("select ruleid from eviRule where name=@nm", db);
            sql.Parameters.Add("@nm", name);
            db.Open();
            NpgsqlDataReader reader= sql.ExecuteReader();
            if (reader.Read())
            {
                rtn = reader.GetInt32(0);
            }
            else
            {
                sql.CommandText = "select 1+coalesce(max(ruleid),0) from evirule";
                reader = sql.ExecuteReader();
                while (reader.Read())
                {
                    rtn = reader.GetInt32(0);
                }
            }
            db.Close();
            return rtn;
        }
        public static void InsertRule(string name, decimal minage, decimal maxage, string sex, string codetype, string details, string[] trigcodes, string[] encdx, string[] plist)
        {
            int ruleid = getRuleId(name);
            deleteRule(ruleid);
            string cmd = "insert into evirule (ruleid,name,minage,maxage,sex,codetype,details) values(@id,@name,@minage,@maxage,@sex,@codetype,@details)";
            NpgsqlCommand sql = new NpgsqlCommand(cmd, db);
            sql.Parameters.Add("@id", ruleid);
            sql.Parameters.Add("@name", name);
            sql.Parameters.Add("@minage", minage);
            sql.Parameters.Add("@maxage", maxage);
            sql.Parameters.Add("@sex", sex);
            sql.Parameters.Add("@codetype", codetype);
            sql.Parameters.Add("@details", details);
            db.Open();
            sql.ExecuteNonQuery();
            sql.CommandText = "insert into ruletrigcodes values(@id,@trigcode)";
            foreach(string code in trigcodes)
            {
                sql.Parameters.Add("@trigcode", code);
                sql.ExecuteNonQuery();
            }
            sql.CommandText = "insert into ruleencdx values(@id,@snomed)";
            foreach (string code in encdx)
            {
                sql.Parameters.Add("@snomed", code);
                sql.ExecuteNonQuery();
            }
            sql.CommandText = "insert into ruleproblist values(@id,@pl)";
            foreach (string code in plist)
            {
                sql.Parameters.Add("@pl", code);
                sql.ExecuteNonQuery();
            }
            db.Close();

        }
        public static void deleteRule(int ruleid)
        {
            NpgsqlCommand sql = new NpgsqlCommand("delete from evirule where ruleId=@id", db);
            sql.Parameters.Add("@id", ruleid);
            db.Open();
            sql.ExecuteNonQuery();
            sql.CommandText = "delete from ruletrigcodes where ruleId=@id";
            sql.ExecuteNonQuery();
            sql.CommandText = "delete from ruleencdx where ruleId=@id";
            sql.ExecuteNonQuery();
            sql.CommandText = "delete from ruleproblist where ruleId=@id";
            sql.ExecuteNonQuery();
            db.Close();
        }
    }
}

