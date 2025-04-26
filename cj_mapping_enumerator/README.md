# CoinJoin mappings enumerator

This tool serves for enumeration of Wasabi 2.x CoinJoin mappings. Use `run.py` to learn the number of mappings of a specified coinjoin. 

### Running 
Example of how the emulation can be run:

``$ python run.py ./data/emulated_cjs.json``


Help:

```
$ python run.py --help
usage: CoinJoin mapping enumerator [-h] [-m MINING_FEE_RATE] [-c COORDINATION_FEE_RATE] [-d MAX_DECOMPOSITION_FEE] [--min_mining_fee MIN_MINING_FEE]
                                   [--max_mining_fee MAX_MINING_FEE] [-t TIMEOUT] [--mode MODE] [--linked_addresses LINKED_ADDRESSES]
                                   json_filename

positional arguments:
  json_filename

options:
  -h, --help            show this help message and exit
  -m MINING_FEE_RATE, --mining_fee_rate MINING_FEE_RATE
  -c COORDINATION_FEE_RATE, --coordination_fee_rate COORDINATION_FEE_RATE
  -d MAX_DECOMPOSITION_FEE, --max_decomposition_fee MAX_DECOMPOSITION_FEE
  --min_mining_fee MIN_MINING_FEE
  --max_mining_fee MAX_MINING_FEE
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout for one transaction in seconds
  --mode MODE           Choose mode 'numerical' or 'all' mappings
  --linked_addresses LINKED_ADDRESSES
                        Provide groups of linked addresses, e.g. [['address1', 'address2'], ['address3', 'address4', 'address5']]
```
