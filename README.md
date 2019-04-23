# get s3 cloud trail log

A application to get s3 cloud trail log illustrating usage of the AWS SDK for Python (alsoreferred to as `boto3`).

## Requirements
  - [python3.7](https://www.python.org/)  
  - [AWS SDK for Python(boto3)]

```bash
    pip install boto3
```

## Basic Configuration

Set the aws_access_key_id and aws_secret_access_key to awsAccessKeyList.csv

[awsAccessKeyList.csv]
aws_access_key_id,aws_secret_access_key
<your access key id1>,<your secret key1>
<your access key id2>,<your secret key2>


## Running the get s3 cloud trail log sample


```bash
$ python get_S3_CloudTrailLog.py --access-key-list awsAccessKeyList.csv --start-time 2019-04-17T12:00:00 --end-time 2019-04-18T12:00:00 --filter-pattern 'SigV2' --region ap-northeast-1 --all-output Ture
  OR
$ python get_S3_CloudTrailLog.py --access-key AKIxxxxxx --secret-key pZxxxxxx --start-time 2019-04-17T12:00:00 --end-time 2019-04-18T12:00:00 --filter-pattern 'SigV2' --region ap-northeast-1 --all-output Ture
  OR
$ python get_S3_CloudTrailLog.py --access-key-list awsAccessKeyList.csv --filter-pattern 'SigV2' --region all
Namespace(access_key=None, access_key_list='awsAccessKeyList.csv', all_output=True, end_time=None, filter_pattern='SigV2', region='all', secret_key=None, start_time=None)
2019-04-21 09:39:30.355176
2019-04-22 09:39:30.355176
1555839570000
1555925970000
## Start output file [awsAccessKeyList_S3_CloudTrail_output.tsv] ##
---------------------------------------------------------
+++++ AccessKey:AKIXXXXXXXXXXXXXXX +++++
++++++++ region:eu-north-1 ++++++++
++ Error message:('An error occurred (ResourceNotFoundException) when calling the FilterLogEvents operation: The specified log group does not exist.',)
++++++++ region:ap-south-1 ++++++++
++ Error message:('An error occurred (ResourceNotFoundException) when calling the FilterLogEvents operation: The specified log group does not exist.',)
++++++++ region:eu-west-3 ++++++++
++ Error message:('An error occurred (ResourceNotFoundException) when calling the FilterLogEvents operation: The specified log group does not exist.',)
++++++++ region:eu-west-2 ++++++++
++ Error message:('An error occurred (ResourceNotFoundException) when calling the FilterLogEvents operation: The specified log group does not exist.',)
++++++++ region:eu-west-1 ++++++++
++ Error message:('An error occurred (ResourceNotFoundException) when calling the FilterLogEvents operation: The specified log group does not exist.',)
++++++++ region:ap-northeast-2 ++++++++
++ Error message:('An error occurred (ResourceNotFoundException) when calling the FilterLogEvents operation: The specified log group does not exist.',)
++++++++ region:ap-northeast-1 ++++++++
111111111111,AKIXXXXXXXXXXXXXXXXXX,dev-unyo-uat-ext,192.168.88.55,PutObject,2019-04-21T10:00:06Z,ap-northeast-1,uat-common-ap-northeast-1.s3.amazonaws.com,uat-common-ap-northeast-1,SigV2
222222222222,none,none,192.168.8.247,ListObjects,2019-04-21T10:10:05Z,ap-northeast-1,uat-common-ap-northeast-1.s3.amazonaws.com,uat-common-ap-northeast-1,SigV2
222222222222,none,none,192.168.8.247,ListObjects,2019-04-21T10:10:08Z,ap-northeast-1,uat-common-ap-northeast-1.s3.amazonaws.com,uat-common-ap-northeast-1,SigV2
222222222222,none,none,192.168.8.247,ListObjects,2019-04-21T10:11:08Z,ap-northeast-1,uat-common-ap-northeast-1.s3.amazonaws.com,uat-common-ap-northeast-1,SigV2
111111111111,AKIXXXXXXXXXXXXXXXXXX,dev-unyo-uat-ext,192.168.88.55,PutObject,2019-04-21T10:10:32Z,ap-northeast-1,uat-common-ap-northeast-1.s3.amazonaws.com,uat-common-ap-northeast-1,SigV2
：
## End output file  [out/awsAccessKeyList_S3_CloudTrail_output.tsv] ##

```

 - result (xxxx_S3_CloudTrail_output.tsv)    
```bash
aws_access_key_id	accountId	accessKeyId	userName	IPAddress	eventName	eventTime	awsRegion	hostName	bucketName	SignatureVersion
AKIXXXXXXXXXXXX	111111111111	AKIXXXXXXXXXXXX	dev-unyo-uat-ext	192.168.88.55	PutObject	2019-04-17T12:00:05Z	ap-northeast-1	uat-common-ap-northeast-1.s3.amazonaws.com	uat-common-ap-northeast-1	SigV2
AKIXXXXXXXXXXXX	222222222222	none	none	192.168.8.247	ListObjects	2019-04-17T12:10:09Z	ap-northeast-1	uat-common-ap-northeast-1.s3.amazonaws.com	uat-common-ap-northeast-1	SigV2
```
