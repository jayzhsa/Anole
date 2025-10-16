##!/bin/bash
#
#
#
#python -m epic.commoncoin.prf_generate_keys $1 $(( $2+1 )) > thsig$(($1))_$(($2)).keys
#python -m epic.ecdsa.generate_keys_ecdsa $1 >ecdsa$(($2)).keys
#python -m epic.threshenc.generate_keys $1 $(( $1-2*$2 )) > thenc$(($1))_$(($2)).keys
#
#
#python -m epic.test.honest_party_test -k thsig$(($1))_$(($2)).keys -e ecdsa$(($2)).keys -b $3 -n $1 -t $2 -c thenc$(($1))_$(($2)).keys -v $4
#!/bin/bash
python -m adaptive.commoncoin.prf_generate_keys $1 $(( $2+1 )) > thsig$(($1))_$(($2)).keys
python -m adaptive.ecdsa.generate_keys_ecdsa $1 >ecdsa$(($2)).keys
python -m adaptive.threshenc.generate_keys $1 $(( $1-2*$2 )) > thenc$(($1))_$(($2)).keys
python -m adaptive.test.honest_party_test -k thsig$(($1))_$(($2)).keys -e ecdsa$(($2)).keys -b $3 -n $1 -t $2 -c thenc$(($1))_$(($2)).keys -v $4