# -*- coding: utf-8 -*-
import sys
import argparse
import pprint
import csv
import re
import json
import time
import calendar
from datetime import datetime, date, timedelta
from boto3.session import Session
from botocore.exceptions import ClientError
from botocore.exceptions import EndpointConnectionError

ACCESS_KEY = 0
SECRET_KEY = 1
CLOUDWATCH_LOG_GROUP = "CloudTrail/S3_CloudTrail"
CLOUDWATCH_LIMIT = 100


def dateTimeToEpoc(now):
    return int(calendar.timegm(now.timetuple()) * 1000)
  
def get_args():
    # parserを生成
    parser = argparse.ArgumentParser(description='引数のアクセスキーリストを元に、S3_CloudTrailLogを取得し、ファイル(*_S3_CloudTrail_output.tsv)に書き出す')
    # python get_S3_CloudTrailLog.py --access-key-list awsAccessKeyList.csv --start-time 2019-04-17T12:00:00 --end-time 2019-04-18T12:00:00 --filter-pattern SigV --region ap-northeast-1 --all-output False

    # 引数設定   
    parser.add_argument('--access-key-list', default = None, help='aws Access Key List')
    parser.add_argument('--access-key'     , default = None, help='aws access-key')
    parser.add_argument('--secret-key'     , default = None, help='aws secret-key')

    # オプションの引数を設定
    parser.add_argument('--start-time'     , help = 'Date Format(ex:2019-04-17T12:00:00, defult:yesterday[UTC])') 
    parser.add_argument('--end-time'       , help = 'Date Format(ex:2019-04-18T12:00:00, defult:today[UTC]') 
    parser.add_argument('--filter-pattern' , default = 'SigV2', help = 'The filter pattern to use.(defult: --filter-pattern SigV2)') 
    parser.add_argument('--region'         , default = 'ap-northeast-1', help = 'region.(defult: ap-northeast-1) all:all region') 
    parser.add_argument('--all-output'     , default = True, help = 'True:all output: , False: Except those without accountId') 

    # 結果を受ける
    args = parser.parse_args()

    print(args)
    return(args)

def validation(args):
    
    ## --access-key-list OR --access-key --secret-key
    if args.access_key_list is None:
        if args.access_key is None or args.secret_key is None:
            print('[ ERROR ] Set access-key-list or set access-key and secret-key')
            sys.exit()
    
    ## --start-time --end-timeの判定
    try:
        # UTCの現在日時
        utcNow = datetime.utcnow()

        if args.start_time:
          inStartTime = dateTimeToEpoc(datetime.strptime(args.start_time, '%Y-%m-%dT%H:%M:%S'))
        else:
          # UTCの昨日日時
          utcYesterday = utcNow - timedelta(days=1)
          inStartTime = dateTimeToEpoc(utcYesterday)
          print(utcYesterday)

        if args.end_time:
          inEndTime = dateTimeToEpoc(datetime.strptime(args.end_time, '%Y-%m-%dT%H:%M:%S'))
        else:
           # UTCの現在日時
          inEndTime = dateTimeToEpoc(utcNow)
          print(utcNow)

        print(inStartTime)
        print(inEndTime)

        durationtime = inEndTime - inStartTime

        # 1日より大きい期間はエラーとする
        if 86400000 < durationtime:
            print('[ ERROR ] Too long duration.')
            print('Max duration is 1 day.')
            sys.exit()

        # 変更した値をArgsに戻す
        args.start_time = inStartTime
        args.end_time = inEndTime

    except  (ValueError, TypeError) as e:
        print('[ ERROR ] Failed StartTime or EndTime format.')
        print('Date Format is "%Y-%m-%dT%H:%M:%S" (ex:2019-04-18T12:00:00).')
        sys.exit()

def readAwsAccessKeyList(args):
    global csv_file
    csv_file = open(args.access_key_list, 'r', encoding='utf-8', errors='ignore')
    readf = csv.reader(csv_file, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    # ヘッダの読出して捨てる
    next(readf)
    return(readf)

def openOutputFile(args):
    global output_f
    global outFileName
   
    outFileName = ('.').join(args.access_key_list.split('.')[:-1]) + '_S3_CloudTrail_output_' + datetime.now().strftime("%Y%m%d%H%M%S") +'.tsv'
    output_f = open('out/' + outFileName, 'w', errors='ignore')
    writer = csv.writer(output_f, delimiter='\t', lineterminator='\n')

    print('## Start output file [' + outFileName + '] ##')
    # ヘッダの書き込み
    writer.writerow([
        'aws_access_key_id'
       ,'accountId'
       ,'accessKeyId'
       ,'userName'
       ,'IPAddress'
       ,'eventName'
       ,'eventTime'
       ,'awsRegion'
       ,'hostName'
       ,'bucketName'
       ,'SignatureVersion'
    ])
    return writer

def getRegions(args, accesskey, secretkey):
    global errorMessageInfo
    regions = []
    if args.region == 'all':
        try:
          session = Session(aws_access_key_id=accesskey,
                            aws_secret_access_key=secretkey)
          ec2 = session.client('ec2')
          regions = map(lambda x: x['RegionName'], ec2.describe_regions()['Regions'])
        except ClientError as e:
            errorMessageInfo = e.args;
            print("++ Error message:{0}".format(e.args))
        except EndpointConnectionError as e:
            errorMessageInfo = e.args;
            print("++ Error message:{0}".format(errorMessageInfo))
    else:
      regions = [args.region]
    
    return regions


def getFilterLogEvents(args, client, token):
    global errorMessageInfo
    errorMessageInfo = ""
    response = None

    if token is not None:
       tokenArgs = {'nextToken': token}
    else:
       tokenArgs = {}

    try:
        response = client.filter_log_events(
             logGroupName  = CLOUDWATCH_LOG_GROUP      #ロググループ名
            ,filterPattern = args.filter_pattern       #フィルターパターン
            ,startTime     = args.start_time           #対象期間　開始タイムスタンプ(ミリ秒)
            ,endTime       = args.end_time             #対象期間　終了タイムスタンプ(ミリ秒)
            ,limit         = CLOUDWATCH_LIMIT          #取得件数　デフォルトは10000
            ,**tokenArgs                               #次の結果セットを取得するためのトークン
        )

    except ClientError as e:
        errorMessageInfo = e.args;
        print("++ Error message:{0}".format(e.args))
    except EndpointConnectionError as e:
        errorMessageInfo = e.args;
        print("++ Error message:{0}".format(errorMessageInfo))

    return response


def getMessageToOutputItem(args, accesskey, msg):

    try:
      accountId = msg['userIdentity']['accountId']
    except KeyError as e:
      accountId = "none"
      if args.all_output == 'False' and msg['additionalEventData']['SignatureVersion'] == 'SigV4':
          return ""

    try:
      accessKeyId = msg['userIdentity']['accessKeyId']
    except KeyError as e:
      accessKeyId = "none"

    try:
      userName = msg['userIdentity']['userName']
    except KeyError as e:
      userName = "none"

    ipAddress = msg['sourceIPAddress'] 
    eventName = msg['eventName'] 
    eventTime = msg['eventTime'] 
    awsRegion = msg['awsRegion']
    hostName = msg['requestParameters']['Host']
    bucketName = msg['requestParameters']['bucketName']
    sigVer = msg['additionalEventData']['SignatureVersion']

    print(accountId + "," + accessKeyId + "," + userName + "," + ipAddress + "," + eventName + "," + eventTime + "," + awsRegion + "," + hostName + "," + bucketName + "," + sigVer)

    return [
       accesskey
      ,accountId
      ,accessKeyId
      ,userName
      ,ipAddress
      ,eventName
      ,eventTime
      ,awsRegion
      ,hostName 
      ,bucketName
      ,sigVer 
    ]

def outputErrorMsg(writer, accesskey):
  writer.writerow([
    accesskey
    ,"レスポンスなし"
    ,errorMessageInfo
    ,""
    ,""
    ,""
    ,""
    ,""
  ])


def main():
    # パラメータの取得
    args = get_args()
    # パラメータのバリデーション
    validation(args)

    # --access-key-listが設定されている場合
    if args.access_key_list is not None:
      # 読み込みファイルをオープンする
      readf = readAwsAccessKeyList(args)
    # --access-key --secret-keyが設定されている場合
    else:
      # パラメータをリストとする
      readf=[[args.access_key, args.secret_key]]
      args.access_key_list = "setParam.csv"

    # 書き込みファイルオープン
    writer = openOutputFile(args)

    # 読み込んだCSVファイル(args.awsAccessKeyList)の分だけ実行
    for row in readf:
      print('---------------------------------------------------------')
      print('+++++ AccessKey:' + row[ACCESS_KEY] + ' +++++')
      accesskey = row[ACCESS_KEY]
      secretkey = row[SECRET_KEY]

      regions = getRegions(args, accesskey, secretkey)
      for region in regions:
        print('++++++++ region:' + region + ' ++++++++')
        session = Session(aws_access_key_id=accesskey,
                    aws_secret_access_key=secretkey,
                    region_name=region)

        client = session.client('logs')
        next_token = None
        while True:
            response = getFilterLogEvents(args, client, next_token)

            if response:
                for event in response['events']:
                    msg = json.loads(event.get("message"));
                    # print(msg)
                    # メッセージの必要項目をファイルに出力
                    items = getMessageToOutputItem(args, accesskey, msg)

                    if items:
                      writer.writerow(items)
                    else:
                      print("++ not enough items(accountId)")

                if response.get('nextToken'):
                    next_token = response['nextToken']
                else:
                    break
            else:
                # エラーの場合に以下をファイルに出力
                outputErrorMsg(writer, accesskey)
                break
      else:
        # エラーの場合に以下をファイルに出力
        outputErrorMsg(writer, accesskey)

    # ファイルをクローズする
    if 'csv_file' in globals(): csv_file.close()
    if 'output' in globals(): output_f.close()
    print('## End output file  [' + outFileName + '] ##')

if __name__ == '__main__':
    main()


