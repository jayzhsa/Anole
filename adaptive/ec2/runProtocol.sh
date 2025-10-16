#!/bin/bash

fab -i ~/.ssh/Sisi_Ubuntu -H ubuntu@18.222.25.87 runProtocolth 4 1 10 1 3 &
fab -i ~/.ssh/Sisi_Ubuntu -H ubuntu@3.19.229.97 runProtocolth 4 1 10 1 3 &
fab -i ~/.ssh/Sisi_Ubuntu -H ubuntu@13.59.188.142 runProtocolth 4 1 10 1 3 &
fab -i ~/.ssh/Sisi_Ubuntu -H ubuntu@13.59.237.113 runProtocolth 4 1 10 1 3 &
