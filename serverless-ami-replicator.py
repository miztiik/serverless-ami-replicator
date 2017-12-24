#This script copies the AMI to other region and tag copied AMI 'DeleteOnCopy' with retention  days specified.
import boto3

# Set the global variables
globalVars  = {}
globalVars['Owner']                 = "Miztiik"
globalVars['Environment']           = "Test"
globalVars['SourceRegionName']      = "ap-south-1"
globalVars['destRegionName']        = "us-east-1"
globalVars['amiRetentionDays']      = int(5)                 # AMI Rentention days in DR/Destination Region.



# Create the Boto Resources and Clients
srcEC2Resource  = boto3.resource('ec2', region_name = globalVars['SourceRegionName'])
destEC2Client   = boto3.client('ec2',   region_name = globalVars['destRegionName'])
destEC2Resource = boto3.resource('ec2', region_name = globalVars['destRegionName'])

# Get the Account ID of the Lambda Runner Account - Assuming this is the source account
globalVars['awsAccountId']          = boto3.client('sts').get_caller_identity()['Account']

def copy_latest_image():
    images = srcEC2Resource.images.filter(Owners=[ globalVars['awsAccountId'] ]) # Specify your AWS account owner id in place of "XXXXX" at all the places in this script
       
    to_tag = collections.defaultdict(list)
    
    for image in images:
        image_date = parser.parse(image.creation_date)
        
        # Copy ONLY today's images
        if image_date.date() == (datetime.datetime.today()).date(): 
        
        #To Copy previous day images
        #if image_date.date() == (datetime.datetime.today()-datetime.timedelta(1)).date(): 
                    
            if not destEC2Client.describe_images(Owners=[ globalVars['awsAccountId'] ], Filters=[{'Name':'name', 'Values':[image.name]}])['Images']:
            
                print "Copying Image {name} - {id} to Virginia".format(name=image.name,id=image.id)
                
                new_ami = destEC2Client.copy_image(
                    DryRun=False,
                    SourceRegion=globalVars['SourceRegionName'],
                    SourceImageId=image.id,
                    Name=image.name,
                    Description=image.description
                )
                
                to_tag[ globalVars['amiRetentionDays'] ].append(new_ami['ImageId'])
                
                print "New Image Id {new_id} for Mumbai Image {name} - {id}".format(new_id=new_ami, name=image.name, id=image.id)

                print "Retaining AMI %s for %d days" % (
                        new_ami['ImageId'],
                        globalVars['amiRetentionDays'],
                    )
                    
                for ami_retention_days in to_tag.keys():
                    delete_date = datetime.date.today() + datetime.timedelta(days=globalVars['amiRetentionDays'])
                    delete_fmt = delete_date.strftime('%d-%m-%Y')
                    print "Will delete %d AMIs on %s" % (len(to_tag[globalVars['amiRetentionDays']]), delete_fmt)
                    
                    #To create a tag to an AMI when it can be deleted after retention period expires
                    destEC2Client.create_tags(
                        Resources=to_tag[globalVars['amiRetentionDays']],
                        Tags=[
                            {'Key': 'DeleteOnCopy', 'Value': delete_fmt},
                            ]
                        )
            else:
                print "Image {name} - {id} already present in Singapore Region".format(name=image.name,id=image.id)

def lambda_handler(event, context):
    copy_latest_image()

if __name__ == '__main__':
    lambda_handler(None, None)
