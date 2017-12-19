# Serverless EBS Volume Snapshots using Lambda Functions
Taking `EBS` snapshots is often a routine activity that is well suited to be automated using Lambda functions. So we are going to write a simple Boto3 script to trigger EBS Snapshots using AWS Lambda Functions

In 3 simple steps, we are going to setup our serverless backup automation,
- **Step 1** - Setup Lambda Function - _Copy & Paste `code` given below_
  - _Optional - Manually you can test your Lambda Function_
- **Step 2** - Configure Lambda Triggers
- **Step 3** - Verify EBS Snapshots in DashboardConfigure Lambda Triggers

![Fig : Valaxy-Automated-Backup](https://raw.githubusercontent.com/miztiik/serverless-backup/master/images/Serverless-Backup.jpg)

We will need the following pre-requisites to successfully complete this activity,
## Pre-Requisities
- EC2 Server(s) - with Tag "Key = Backup" _(Value can be null or anything)_
- IAM Lambda Role - _i.e_ `Lambda Service Role` - _with_ `EC2FullAccess` _permissions_


## Step 1 - Lambda Backup Code
This is what our `AWS Lambda` function is going to do in one region,
- Find out `Instances` in the current `Region`
  - Filter Instances based on `Tags` - In this case "**Backup** or "**backup**"
- Find mapped block devices attached to those instances
- Initiate Backup
- Add Tags to Snapshots
- Report Success
_Change the global variables at the top of the script to suit your needs._
```py
import boto3

# Set the global variables
globalVars  = {}
globalVars['Owner']                 = "Miztiik"
globalVars['Environment']           = "Test"
globalVars['REGION_NAME']           = "ap-south-1"
globalVars['tagName']               = "Valaxy-Serverless-Automated-Backup"
globalVars['findNeedle']            = ["backup", "Backup"]

ec2Client = boto3.client('ec2')


def lambda_handler(event, context):
    reservations = ec2Client.describe_instances( Filters=[ {'Name': 'tag-key', 'Values': globalVars['findNeedle'] }] ).get('Reservations', [] )

    print "Found {0} instances that need backing up".format( len(reservations) )

    instances = sum([[i for i in r['Instances']] for r in reservations], [])

    backupStatus=[]
    for instance in instances:
        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']

            print 'Found EBS volume {0} on instance {1}'.format( vol_id, instance['InstanceId'])

            snapShot = ec2Client.create_snapshot( VolumeId=vol_id )

            # Add tags to the snapshot
            ec2Client.create_tags(Resources=[snapShot['SnapshotId'], ],
                                  Tags=[{'Key': 'Name', 'Value': globalVars['tagName']}, ]
                                  )

            # Append to backup status update list
            backupStatus.append({'InstanceId':instance['InstanceId'],
                                 'VolumeId': vol_id,
                                 'SnapshotId':snapShot['SnapshotId'],
                                 'State':snapShot['State']
                                }
                               )
    # Return the status of the backups triggered to log
    return backupStatus
```

## Step 2 - Configure Lambda Triggers
We are going to use Cloudwatch Scheduled Events to take backup everyday.
```
rate(1 minute)
or
rate(5 minutes)
or
rate(1 day)
```
Ref: [CloudWatch - Schedule Expressions for Rules](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html#RateExpressions)

## Step 3 - Verify EBS Snapshots in Dashboard

## Customizations
You can use many of the lamdba configurations to customize it suit your needs,

- `Concurrency`:_Increase as necessary to manage all your instances_
- `Memory` & `Timeout`: _If you have a large number of instances, you want to increase the `Memory` & `Timeout`_
- `Security`: _Run your lambda inside your `VPC` for added security_
  - `CloudTrail` : _You can also enable `CloudTrail` for audit & governance_

