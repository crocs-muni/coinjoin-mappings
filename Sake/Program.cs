using NBitcoin;
using Sake;
using WalletWasabi.Extensions;
using Newtonsoft.Json.Linq;

static (int, int) MatchedOutputs(List<ulong> outputs1, List<ulong> outputs2) {
    int ol = outputs1.Count();
    outputs2.ForEach(v => outputs1.Remove(v));
    int nl = outputs1.Count();
    return (ol-nl, ol);
}

static bool compareOutputs(List<ulong> outputs1, List<ulong> outputs2) {
    if (outputs1.Count() != outputs2.Count()) 
        return false;
    
    outputs1.Sort();
    outputs2.Sort();

    bool change_found = false;

    for (var i = 0; i < outputs1.Count(); i++) {
        if (outputs1[i] == outputs2[i]) {
            continue;
        }
        if (change_found) { // at most one change output
            return false;
        }
        ulong difference = outputs1[i] > outputs2[i] ? outputs1[i]-outputs2[i] : outputs2[i]-outputs1[i];
        if (difference < 100) { // allow a small error in the change output
            change_found = true;
            continue;
        }
        return false;
    }
    return true;
}

static void sake_vs_emulations() {
    string path = "./data/coinjoins.json";

    long matched_outputs = 0;
    long total_outputs = 0;
    long wallet_matches = 0;
    long total_wallets = 0;
    long perfect_matches = 0;
    long total_coinjoins = 0;

    long same_out_len = 0;

    StreamWriter emuoutputs = new StreamWriter("emuoutputs");
    StreamWriter sakeoutputs = new StreamWriter("sakeoutputs");

    var parser = new JsonParser(path);

    bool cj_exists = true;

    while (cj_exists)
    {   
        if (parser.IsBlame()) {
            cj_exists = parser.NextCJ();
            continue;
        }

        var allowedOutputTypes = new List<ScriptType> {ScriptType.P2WPKH};

        var min = Money.Satoshis(5000m);
        var max = Money.Coins(43000m);

        var random = new Random();
        var fee_rate = parser.GetFeeRate();
        (var groups, var feeRate, _) = parser.GetInputGroups(fee_rate); 

        var mixer = new Mixer(feeRate, min, max, allowedOutputTypes, random);

        ulong [][] outputGroups = Array.Empty<ulong[]>();

        outputGroups = mixer.CompleteMix(groups).Select(x => x.ToArray()).ToArray();

        (var real_output_groups, _) = parser.GetOutputGroups();
        bool cj_match = true;
        for (int i = 0; i < outputGroups.Count(); i++) {
            if (outputGroups[i].Count() == real_output_groups[i].Count()) {
                same_out_len++;
            }
            string str_sakeoutputs = string.Join(", ", outputGroups[i].Select(d => d));
            sakeoutputs.WriteLine(str_sakeoutputs);
            string str_realoutputs = string.Join(", ", real_output_groups[i].Select(d => d));
            emuoutputs.WriteLine(str_realoutputs);


            var (matched, all) = MatchedOutputs(outputGroups[i].ToList(), real_output_groups[i]);
            if (matched == all) {
                wallet_matches++;
            } else {
                cj_match = false;
            }
            total_wallets++;
            total_outputs += all;
            matched_outputs += matched;
        }
        sakeoutputs.WriteLine();
        emuoutputs.WriteLine();
        if (cj_match) {
            perfect_matches++;
        }
        total_coinjoins++;

        cj_exists = parser.NextCJ();
    }
    
    var out_perc = (matched_outputs*100)/total_outputs;
    var wall_perc = (wallet_matches*100)/total_wallets;
    var perfect_perc = (perfect_matches*100)/total_coinjoins;
    var len_perc = (same_out_len*100)/total_wallets;
    Console.WriteLine($"Single output matches {matched_outputs} of {total_outputs}, i.e., {out_perc} %");
    Console.WriteLine($"Wallet matches {wallet_matches} of {total_wallets}, i.e., {wall_perc} %");
    Console.WriteLine($"Full CoinJoin matches {perfect_matches} of {total_coinjoins}, i.e., {perfect_perc} %");
    Console.WriteLine($"Length matches {same_out_len} of {total_wallets}, i.e., {len_perc} %");
}

static void decomposition_options() {
    StreamWriter options = new StreamWriter("options");
    StreamWriter topk = new StreamWriter("topk");

    string path = "./data/coinjoins.json";

    var parser = new JsonParser(path);
    bool cj_exists = true;

    while (cj_exists)
    {   
        if (parser.IsBlame()) {
            cj_exists = parser.NextCJ();
            continue;
        }

        var allowedOutputTypes = new List<ScriptType> {ScriptType.P2WPKH, ScriptType.Taproot}; 

        var min = Money.Satoshis(5000m);
        var max = Money.Coins(43000m);
        var fee_rate = parser.GetFeeRate();
        Console.Write("fee rate:");
        Console.WriteLine(fee_rate.SatoshiPerByte);
        (var groups, var feeRate, var in_group_names) = parser.GetInputGroups(fee_rate); 
        
        var random = new Random();
        foreach (var w in in_group_names) {
            var countingList = new Dictionary<string, int>();
            var str_to_list = new Dictionary<string, List<ulong>>();

            for (var i = 1; i < 100; i++) {
                var mixer = new Mixer(feeRate, min, max, allowedOutputTypes, random);
                var w_index = in_group_names.IndexOf(w);
                var outputs = mixer.SingleWalletMix(groups[w_index], groups.Where((v,j) => j != w_index).SelectMany(v => v).ToList());

                foreach (var o in outputs) {
                    var output = o.ToList();
                    output.Sort((x, y) => y.CompareTo(x));
                    var str_output = string.Join(",", output);
                    if( countingList.ContainsKey(str_output))
                        countingList[str_output]++;
                    else {
                        countingList.Add(str_output, 1 );
                        str_to_list.Add(str_output, output);
                    }
                }
            }

            (var real_output_groups, var out_group_names) = parser.GetOutputGroups();
            var w_out_index = out_group_names.IndexOf(w);

            var real_gr = real_output_groups[w_out_index];
            real_gr.Sort((x, y) => y.CompareTo(x));

            var counts = countingList.ToList();
            counts.Sort((x, y) => y.Value.CompareTo(x.Value));
            Console.Write("Options:");
            Console.WriteLine(counts.Count());
            options.WriteLine(counts.Count());
            var j = 1;
            var top = 99999;
            Console.WriteLine(string.Join(",", real_gr));
            foreach ((var x, var y) in counts){
                Console.WriteLine(x);
                if (compareOutputs(real_gr, str_to_list[x])) {
                    top = j;
                    break;
                }
                j++;
            }
            Console.Write("top ");
            Console.WriteLine(top);
            topk.WriteLine(top);

        }

        cj_exists = parser.NextCJ();
    }
    
    topk.Flush();
    topk.Close();
    options.Flush();
    topk.Close();
}

sake_vs_emulations();
decomposition_options();
