#!/usr/bin/env bash
set -euo pipefail
aws service-quotas get-requested-service-quota-change --region us-east-2 --request-id 34e4c57dac714cf3a408e2ac78874ad2552AHGPA --query 'RequestedQuota.{status:Status,desired:DesiredValue,created:Created}' --output json
