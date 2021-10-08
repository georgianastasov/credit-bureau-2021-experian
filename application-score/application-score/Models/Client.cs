using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;

namespace application_score.Models
{
    public class Client
    {
        [JsonProperty(PropertyName = "account")]
        public long Account { get; set; }

        [JsonProperty(PropertyName = "accountType")]
        public string AccountType { get; set; }

        [JsonProperty(PropertyName = "bureauScore")]
        public int BureauScore { get; set; }

        [JsonProperty(PropertyName = "chequeCard")]
        public string ChequeCard { get; set; }

        [JsonProperty(PropertyName = "insuaranceRequired")]
        public string InsuaranceRequired { get; set; }

        [JsonProperty(PropertyName = "loanPaymentMethod")]
        public string LoanPaymentMethod { get; set; }

        [JsonProperty(PropertyName = "loanToIncome")]
        public decimal LoanToIncome { get; set; }

        [JsonProperty(PropertyName = "numberOfCCJ")]
        public int NumberOfCCJ { get; set; }

        [JsonProperty(PropertyName = "numberOfSearches")]
        public int NumberOfSearches { get; set; }

        [JsonProperty(PropertyName = "numbersOfPayments")]
        public int NumbersOfPayments { get; set; }

        [JsonProperty(PropertyName = "residentialStatus")]
        public string ResidentialStatus { get; set; }

        [JsonProperty(PropertyName = "timeAdress")]
        public int TimeAdress { get; set; }

        [JsonProperty(PropertyName = "timeEmployment")]
        public int TimeEmployment { get; set; }

        [JsonProperty(PropertyName = "timeWithBank")]
        public int TimeWithBank { get; set; }
    }
}