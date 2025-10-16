#!/bin/bash
export LIBRARY_PATH=$LIBRARY_PATH:/usr/lib/x86_64-linux-gnu
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib/x86_64-linux-gnu
export PYTHONPATH=~/project/local_coin/adaptive/commoncoin:~/project/local_coin/adaptive/ecdsa:~/project/local_coin/adaptive/threshenc:~/project/local_coin/adaptive/core:~/project/local_coin/adaptive:$PYTHONPATH

#rm -f thsig4_1.keys ecdsa1.keys thenc4_1.keys
#python3 -m adaptive.commoncoin.prf_generate_keys 4 2 > thsig4_1.keys
#python3 -m adaptive.ecdsa.generate_keys_ecdsa 4 > ecdsa.keys
#python3 -m adaptive.threshenc.generate_keys 4 2 > thenc4_1.keys
# python3 -m adaptive.test.honest_party_test -k thsig4_1.keys -e ecdsa.keys -b 40 -n 4 -t 1 -c thenc4_1.keys
#python3 -m adaptive.test.honest_party_test -k thsig4_1.keys -e ecdsakeys -b 40 -n 4 -t 1 -c thenc4_1.keys -v 1
# python3 -m adaptive.test.honest_party_test_EC2 -k thsig4_1.keys -e ecdsa.keys -a 3 -b 10 -n 7 -t 1 -c thenc4_1.keys -v 1
python3 -m adaptive.test.honest_party_test_EC2 -k thsig7_2.keys -e ecdsa2.keys -a 3 -b 10 -n 7 -t 2 -c thenc7_2.keys -v 1