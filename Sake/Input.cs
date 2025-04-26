using System.Diagnostics.CodeAnalysis;
using NBitcoin;
using WalletWasabi.Extensions;

namespace Sake;

public class Input
{

	static long cf(long a){
		if (a <= 1000000) {
			return 0l;
		}
		return (long)(0.003m*(decimal)a);
	}
	public Input(Money amount, ScriptType scriptType, FeeRate feeRate, Money coordFee)
	{
		ScriptType = scriptType;
		Fee = feeRate.GetFee(scriptType.EstimateInputVsize());
		Amount = amount;
		CoordFee = coordFee;
	}
	
	public Money Amount { get; }
	public ScriptType ScriptType { get; }
	public Money EffectiveValue => Amount - Fee - CoordFee;
	public Money ObservedEffectiveValue => Amount - Fee - new Money(cf(Amount.Satoshi));
	public Money Fee { get; }

	public Money CoordFee {get;}

}
