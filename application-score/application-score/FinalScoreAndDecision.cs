using application_score.Models;
using CsvHelper;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Web;

namespace application_score
{
    public class FinalScoreAndDecision
    {
        public void WriteScoreDecision(ScoreAccount[] scorePerAccount)
        {

            StringBuilder csvContent = new StringBuilder();
            csvContent.AppendLine("Account,Final_Score,Final_Decision");

            for (int i = 0; i < scorePerAccount.Length; i++)
            {
                csvContent.AppendLine($"{scorePerAccount[i].Account},{scorePerAccount[i].Score},{scorePerAccount[i].Decision}");
            }

            string csvpath = $"D:\\Programing\\Work\\credit-bureau-2021\\score-model\\result.csv";
            File.AppendAllText(csvpath, csvContent.ToString());

        }
    }
}