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