#!/usr/bin/env python3

import boto3
from get import getjson

query = "http://evolutiva.mx/getip/"
data = getjson(query)

if not data:
    exit()

new_ip = dict(data)['ip']
old_ip = None

r53 = boto3.client('route53') #.connect_to_region('us-west-2')

try:
    for res in r53.list_resource_record_sets(HostedZoneId='/hostedzone/Z2XLK91YNO8JY8')['ResourceRecordSets']:
        if res['Type'] == 'A' and res['Name'] == 'cuchulainn.evolutiva.mx.':
            old_ip = res['ResourceRecords'][0]['Value']
except:
    pass

if new_ip == old_ip:
    print('Sin Cambios')
else:
    # Ex: {'ResourceRecords': [{'Value': '187.207.0.253'}], 'TTL': 300, 'Name': 'cuchulainn.evolutiva.mx.', 'Type': 'A'}
    CB = {
        'Changes':[{
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                            'Name':     'cuchulainn.evolutiva.mx',
                                'Type': 'A',
                                'TTL':300,
                                'ResourceRecords': [
                                        {
                                                'Value': new_ip
                                        }
                                ]
            }
                }]
    }
    response = r53.change_resource_record_sets(HostedZoneId='/hostedzone/Z2XLK91YNO8JY8', ChangeBatch=CB)
    print(response)
