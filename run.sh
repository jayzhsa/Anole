#!/bin/bash

python3 -m adaptive.commoncoin.prf_generate_keys 4 2 > thsig4_1.keys
python3 -m adaptive.ecdsa.generate_keys_ecdsa 4 > ecdsa1.keys
python3 -m adaptive.threshenc.generate_keys 4 2 > thenc4_1.keys

python3 -m adaptive.commoncoin.prf_generate_keys 7 3 thsig7_2.keys
python3 -m adaptive.ecdsa.generate_keys_ecdsa 7 ecdsa2.keys
python3 -m adaptive.threshenc.generate_keys 7 3 thenc7_2.keys

python -m adaptive.commoncoin.prf_generate_keys 16 6 > thsig16_5.keys
python -m adaptive.ecdsa.generate_keys_ecdsa 16 > ecdsa5.keys
python -m adaptive.threshenc.generate_keys 16 6 > thenc16_5.keys

python -m adaptive.commoncoin.prf_generate_keys 31 11 > thsig31_10.keys
python -m adaptive.ecdsa.generate_keys_ecdsa 31 > ecdsa10.keys
python -m adaptive.threshenc.generate_keys 31 11 > thenc31_10.keys

python -m adaptive.commoncoin.prf_generate_keys 46 16 > thsig46_15.keys
python -m adaptive.ecdsa.generate_keys_ecdsa 46 > ecdsa15.keys
python -m adaptive.threshenc.generate_keys 46 16 > thenc46_15.keys

python -m adaptive.commoncoin.prf_generate_keys 61 21 > thsig61_20.keys
python -m adaptive.ecdsa.generate_keys_ecdsa 61 > ecdsa20.keys
python -m adaptive.threshenc.generate_keys 61 21 > thenc61_20.keys

python -m adaptive.commoncoin.prf_generate_keys 91 31 > thsig91_30.keys
python -m adaptive.ecdsa.generate_keys_ecdsa 91 > ecdsa30.keys
python -m adaptive.threshenc.generate_keys 91 31 > thenc91_30.keys

python -m adaptive.commoncoin.prf_generate_keys 121 41 > thsig121_40.keys
python -m adaptive.ecdsa.generate_keys_ecdsa 121 > ecdsa40.keys
python -m adaptive.threshenc.generate_keys 121 41 > thenc121_40.keys

