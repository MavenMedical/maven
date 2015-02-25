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
        //public static NpgsqlConnection db = new NpgsqlConnection("Server=23.251.149.125;Port=5432;Database=maven;User Id=maven;Password=mavendevel;");
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
                string codetype="";
                string[] trigs = GetTrigcodes(doctext, ref remlines,ref codetype);
                string[] encdx = GetDxCodeLists(doctext);
                string[] prochist = GetPxcodes(doctext);
                string[] labcrit = GetLabCriteria(doctext);
                decimal minage = -1;
                decimal maxage = 200;
                string rulename = fi.Name.Replace(".docx", "");
                getAges(ref remlines, ref minage, ref maxage);
                string sex=getSex(ref remlines);
                string details = getDetails(remlines);
                doc.Close();
                InsertRule(rulename, minage, maxage, sex, codetype, details, trigs, encdx,prochist,labcrit);
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
            string routeclause="1=1";
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
                if (inPtrigBlock && !cur.Contains("ptrig") && cur.Contains("{trigcode"))
                {
                    string trigcode = cur.Split('{')[1].Replace("trigcode:", "").Replace("}", "").Trim();
                    al.Add(trigcode);
                }
                else if (inPtrigBlock && !cur.Contains("ptrig") && cur.Contains("{route"))
                {
                    routeclause="routename in (";
                    string[] list=cur.Replace("{route:","").Replace("}","").Split(',');
                    foreach (string route in list)
                    {
                        routeclause+="'"+route.Trim()+"',";
                    }
                    routeclause=routeclause.TrimEnd(',')+")";
                    
                }
                else if (inPtrigBlock && cur.Contains("CODETYPE"))
                {
                    codetype=cur.Split(':')[2].Trim();
                }
                else
                {
                    RemainingLines.Add(cur);
                }
                i++;
            }
            if (codetype == "MED")
            {
                al = expandMedList(al,routeclause);
            }
            string[] rtn=new string[al.Count];
            al.CopyTo(rtn);
            return rtn;
        }
        public static ArrayList expandMedList(ArrayList snomeds,string routeclause)
        {
            string sql="select distinct ndc from terminology.drugclassancestry a inner join terminology.drugclass b on a.classaui=b.rxaui "
                        +"inner join terminology.conceptancestry c on b.snomedid=c.child where c.ancestor=@snomed and "+routeclause;
            NpgsqlCommand cmd = new NpgsqlCommand(sql, db);
            ArrayList rtn = new ArrayList();
            db.Open();
            foreach (string sno in snomeds)
            {
                cmd.Parameters.Add("@snomed", Convert.ToInt64(sno));
                NpgsqlDataReader reader = cmd.ExecuteReader();
                while (reader.Read())
                {
                    string ndc=reader.GetString(0);
                    if(!rtn.Contains(ndc))
                    {
                        rtn.Add(ndc);
                    }
                }
            }
            db.Close();
            return rtn;
        }
        /// <summary>
        /// Expects a list of codes like this
        ///     dxor:ENC:false
        ///     snomed: 312117008
        ///     snomed: 255320000
        ///     /dxor
        /// </summary>
        /// <param name="doctext"></param>
        /// <returns></returns>
        public static string[] GetDxCodeLists(string doctext)
        {
            ArrayList al = new ArrayList();
            string pattern = @"dxor.*?/dxor"; //.*? matches the shortest possible string wrapped in dxor.../dxor
            MatchCollection matches= Regex.Matches(doctext, pattern,RegexOptions.Multiline);
            foreach (Match mch in matches)
            {
                string txt = mch.ToString();
                string type = "'"+txt.Split('\r')[0].Split(':')[1].Trim()+"'";
                string isintersect = "'"+txt.Split('\r')[0].Split(':')[2].Trim()+"'";
                string framemin = "-99999";
                string framemax = "0";
                string intlist="array[]";
                try
                {
                    framemin = txt.Split('\r')[0].Split(':')[3].Trim();
                    framemax = txt.Split('\r')[0].Split(':')[4].Trim();
                }
                catch{/*whatever, just use the default fram if not specified*/}
                string a = "insert into rules.codelists (ruleid, listtype,isintersect,intlist,strlist,framemin,framemax) values(<<ruleid>>,"+type
                    +","+isintersect+",<<intlist>>,null,"+framemin+","+framemax+")";
                string[] splitter = { "snomed:"};
                string[] snomedlist=txt.Replace("/dxor","").Split(splitter,StringSplitOptions.None);
                bool isfirst = true;
                foreach (string sno in snomedlist)
                {
                    if (!isfirst) { intlist = snomedToArraySyntax(sno.Trim(), intlist); }
                    isfirst = false;
                }
                a = a.Replace("<<intlist>>", intlist);
                al.Add(a);
            }
            string[] rtn = new string[al.Count];
            al.CopyTo(rtn);
            return rtn;
        }
        public static string snomedToArraySyntax(string snomed, string addto)
        {
            string rtn = addto.TrimEnd(']');
            if (!rtn.EndsWith("[")) {rtn+=",";} //if we already have stuff in the array, append it with a comma to continue adding values
            string sql = "select distinct child from terminology.conceptancestry where ancestor=@sno";
            NpgsqlCommand cmd = new NpgsqlCommand(sql, db);
            cmd.Parameters.Add("@sno", Convert.ToInt64(snomed));
            db.Open();
            NpgsqlDataReader reader = cmd.ExecuteReader();
            while (reader.Read())
            {
                string child = Convert.ToString(reader.GetDecimal(0));
                if (!rtn.Contains(","+child+","))
                {
                    rtn+=child+",";
                }
            }
            db.Close();
            rtn = rtn.TrimEnd(',') + "]";
            return rtn;
        }
        public static string stringsToArraySyntax(string cpts, string addto)
        {
            string rtn = addto.TrimEnd(']');
            if (!rtn.EndsWith("[")) { rtn += ","; } //if we already have stuff in the array, append it with a comma to continue adding values
            string[] cptlist = cpts.Split(',');
            foreach ( string cpt in cptlist)
            {
                string child = "'"+cpt.Trim()+"'";
                if (!rtn.Contains("," + child + ","))
                {
                    rtn += child + ",";
                }
            }
            db.Close();
            rtn = rtn.TrimEnd(',') + "]";
            return rtn;
        }
        public static string[] oldGetEncDxcodes(ref ArrayList RemainingLines)
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
        /// <summary>
        /// Expects the following to denote a historic procedure list
        ///     pxor:HXPX:true
        ///     cpt:1,2,3a,4
        ///     cpt:5.1a,6
        ///     /pxor
        /// </summary>
        /// <param name="doctext"></param>
        /// <returns></returns>
        public static string[] GetPxcodes(string doctext)
        {

            ArrayList al = new ArrayList();
            string pattern = @"pxor.*?/pxor"; //.*? matches the shortest possible string wrapped in dxor.../dxor
            MatchCollection matches = Regex.Matches(doctext, pattern, RegexOptions.Multiline);
            foreach (Match mch in matches)
            {
                string txt = mch.ToString();
                string type = "'" + txt.Split('\r')[0].Split(':')[1].Trim() + "'";
                string isintersect = "'" + txt.Split('\r')[0].Split(':')[2].Trim() + "'";
                string framemin = "-99999";
                string framemax = "0";
                string intlist = "array[]";
                try
                {
                    framemin = txt.Split('\r')[0].Split(':')[3].Trim();
                    framemax = txt.Split('\r')[0].Split(':')[4].Trim();
                }
                catch {/*whatever, just use the default fram if not specified*/}
                string a = "insert into rules.codelists (ruleid, listtype,isintersect,intlist,strlist,framemin,framemax) values(<<ruleid>>," + type
                    + "," + isintersect + ",null,<<strlist>>," + framemin + "," + framemax + ")";
                string[] splitter = { "cpt:" };
                string[] pxlist = txt.Replace("/pxor", "").Split(splitter, StringSplitOptions.None);
                bool isfirst = true;
                foreach (string px in pxlist)
                {
                    if (!isfirst) { intlist = stringsToArraySyntax(px.Trim(), intlist); }
                    isfirst = false;
                }
                a = a.Replace("<<strlist>>", intlist);
                al.Add(a);
            }
            string[] rtn = new string[al.Count];
            al.CopyTo(rtn);
            return rtn;
        }
        /// <summary>
        /// Expects the following to denote a historic procedure list (case sensitive)
        ///     labcrit:treshold:relation:defaultbool:framemin,framemax
        ///     loincs:1,2,3a,4
        ///     /labcrit
        /// 
        /// for example:
        ///     labcrit:10000:>:true:-99999:0
        ///     loincs:123,234,455
        ///     /labcrit
        /// </summary>
        /// <param name="doctext"></param>
        /// <returns></returns>
        public static string[] GetLabCriteria(string doctext)
        {

            ArrayList al = new ArrayList();
            string pattern = @"labcrit.*?/labcrit"; //.*? matches the shortest possible string wrapped in dxor.../dxor
            MatchCollection matches = Regex.Matches(doctext, pattern, RegexOptions.Multiline);
            foreach (Match mch in matches)
            {
                string txt = mch.ToString();
                string thresh =  txt.Split('\r')[0].Split(':')[1].Trim() ;
                string rel = "'" + txt.Split('\r')[0].Split(':')[2].Trim() + "'";
                string dflt =  txt.Split('\r')[0].Split(':')[3].Trim() ;
                string framemin = "-99999";
                string framemax = "0";
                string intlist = "array[]";
                try
                {
                    framemin = txt.Split('\r')[0].Split(':')[4].Trim();
                    framemax = txt.Split('\r')[0].Split(':')[5].Trim();
                }
                catch {/*whatever, just use the default fram if not specified*/}
                string a = "insert into rules.labeval (ruleid, loinc_codes,threshold,relation,framemin,framemax,defaultval) values(<<ruleid>>,<<loincs>>," + thresh
                    + "," + rel + "," + framemin + "," + framemax +","+dflt+ ")";
                string[] splitter = { "loincs:" };
                string[] pxlist = txt.Replace("/labcrit", "").Split(splitter, StringSplitOptions.None);
                bool isfirst = true;
                foreach (string px in pxlist)
                {
                    if (!isfirst) { intlist = stringsToArraySyntax(px.Trim(), intlist); }
                    isfirst = false;
                }
                a = a.Replace("<<loincs>>", intlist);
                al.Add(a);
            }
            string[] rtn = new string[al.Count];
            al.CopyTo(rtn);
            return rtn;
        }
        public static string getSex(ref ArrayList RemainngLines)
        {
            string rtn="%";
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
        public static void InsertRule(string name, decimal minage, decimal maxage, string sex, string codetype, string details, string[] trigcodes, string[] encdx,string[] prochist, string[] labcrit)
        {
            int ruleid = getRuleId(name);
            deleteRule(ruleid);
            string cmd = "insert into rules.evirule (ruleid,name,minage,maxage,sex,codetype,remainingdetails) values(@id,@name,@minage,@maxage,@sex,@codetype,@details)";
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
            sql.CommandText = "insert into rules.trigcodes values(@id,@trigcode)";
            foreach(string code in trigcodes)
            {
                sql.Parameters.Add("@trigcode", code);
                sql.ExecuteNonQuery();
            }
            foreach (string insrt in encdx)
            {
                sql.CommandText = insrt.Replace("<<ruleid>>",ruleid.ToString());
                sql.ExecuteNonQuery();
            }
            foreach (string insrt in prochist)
            {
                sql.CommandText = insrt.Replace("<<ruleid>>", ruleid.ToString());
                sql.ExecuteNonQuery();
            }
            foreach (string insrt in labcrit)
            {
                sql.CommandText = insrt.Replace("<<ruleid>>", ruleid.ToString());
                sql.ExecuteNonQuery();
            }
            db.Close();

        }
        public static void deleteRule(int ruleid)
        {
            NpgsqlCommand sql = new NpgsqlCommand("delete from rules.evirule where ruleId=@id", db);
            sql.Parameters.Add("@id", ruleid);
            db.Open();
            sql.ExecuteNonQuery();
            sql.CommandText = "delete from rules.trigcodes where ruleId=@id";
            sql.ExecuteNonQuery();
            sql.CommandText = "delete from rules.codelists where ruleId=@id";
            sql.ExecuteNonQuery();
            sql.CommandText = "delete from rules.labeval where ruleId=@id";
            sql.ExecuteNonQuery();
            db.Close();
        }
    }
}
