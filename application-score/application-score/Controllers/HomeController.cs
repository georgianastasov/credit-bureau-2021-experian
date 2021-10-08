using application_score.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using RestSharp;
using RestSharp.Serialization.Json;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Web;
using System.Web.Mvc;

namespace application_score.Controllers
{
    public class HomeController : Controller
    {
        public ActionResult Index()
        {


            var client = new RestClient("http://127.0.0.1:5000/");
            var res = new RestRequest("data",Method.GET, DataFormat.Json);
            res.AddHeader("User-Agent", "Nothing");
            //var contributors = client.Get(res);
            var contributors = client.Execute < List <Client>> (res);
            //contributors.Data.ForEach(Console.WriteLine);

            Client[] clients = JsonConvert.DeserializeObject<Client[]>(contributors.Content);

            //List<ScoreAccount> scorePerAccount = new List<ScoreAccount>();
            ScoreAccount[] scorePerAccount = new ScoreAccount[clients.Length-1];
            const int intercept = 304;

            for (int i = 1; i < clients.Length; i++)
            {
                int score = 0;

                string acountType = clients[i].AccountType;

                if (acountType == "VL")
                {
                    score -= 64;
                }


                int bureauScore = clients[i].BureauScore;

                if (bureauScore <= 850)
                {
                    score -= 48;
                }
                else if (bureauScore >= 925)
                {
                    score += 59;
                }


                string chequeCardFlag = clients[i].ChequeCard;

                if (chequeCardFlag == "N")
                {
                    score -= 51;
                }


                string insurance = clients[i].InsuaranceRequired;

                if (insurance == "Y")
                {
                    score -= 21;
                }


                string loanPaymentMethod = clients[i].LoanPaymentMethod;

                if (loanPaymentMethod == "Q" || loanPaymentMethod == "S" || loanPaymentMethod == "X")
                {
                    score -= 33;
                }


                int numberOfPayments = clients[i].NumbersOfPayments;

                if (numberOfPayments >= 0 && numberOfPayments <= 18)
                {
                    score += 65;
                }


                string residentialStatus = clients[i].ResidentialStatus;

                if (residentialStatus == "L" || residentialStatus == "O" || residentialStatus == "T")
                {
                    score -= 16;
                }


                int numberOfSearches = clients[i].NumberOfSearches;

                if (numberOfSearches >= 6)
                {
                    score -= 41;
                }


                int numberOfCCJ = clients[i].NumberOfCCJ;

                if (numberOfCCJ >= 1)
                {
                    score -= 42;
                }


                int timeAdress = clients[i].TimeAdress;

                if (timeAdress >= 0 && timeAdress <= 6)
                {
                    score -= 19;
                }
                else if (timeAdress >= 2500)
                {
                    score -= 23;
                }


                int timeEmployment = clients[i].TimeEmployment;

                if (timeEmployment >= 0 && timeEmployment <= 100)
                {
                    score -= 21;
                }
                else if (timeEmployment >= 1200)
                {
                    score += 12;
                }


                int timeWithBank = clients[i].TimeWithBank;

                if (timeWithBank >= 0 && timeWithBank <= 6)
                {
                    score -= 31;
                }
                else if (timeWithBank >= 6 && timeWithBank <= 200)
                {
                    score -= 10;
                }
                else if (timeWithBank >= 1000)
                {
                    score += 10;
                }


                decimal loanToIncome = clients[i].LoanToIncome;

                if (loanToIncome >= 0 && loanToIncome <= 10)
                {
                    score += 16;
                }
                else if (loanToIncome >= 30 && loanToIncome <= 60)
                {
                    score -= 12;
                }
                else if (loanToIncome >= 60 && loanToIncome <= 100)
                {
                    score -= 20;
                }
                else if (loanToIncome >= 100)
                {
                    score -= 34;
                }

                score += intercept;
                int br = i;

                ScoreAccount localScoreAcount = new ScoreAccount();
                localScoreAcount.Account = clients[i].Account;
                localScoreAcount.Score = score;

                if (score <= 137)
                {
                    localScoreAcount.Decision = "Reject";
                }
                else if (score >= 138 && score <= 301)
                {
                    localScoreAcount.Decision = "Refer";
                }
                else if(score >= 302)
                {
                    localScoreAcount.Decision = "Accept";
                }

                scorePerAccount[--br] = localScoreAcount;
            }

            FinalScoreAndDecision write = new FinalScoreAndDecision();
            write.WriteScoreDecision(scorePerAccount);

            Console.WriteLine();
            return View();

        }
    }
}
