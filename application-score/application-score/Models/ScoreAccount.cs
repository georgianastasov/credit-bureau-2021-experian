using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace application_score.Models
{
    public class ScoreAccount
    {
        public long Account { get; set; }
        public int Score { get; set; }
        public string Decision { get; set; }
    }
}