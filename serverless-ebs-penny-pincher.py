import boto3

# Set the global variables
globalVars  = {}
globalVars['Owner']                 = "Miztiik"
globalVars['Environment']           = "Test"
globalVars['REGION_NAME']           = "ap-south-1"
globalVars['tagName']               = "Valaxy-Serverless-EBS-Penny-Pincher"
globalVars['findNeedle']            = "Name"
globalVars['tagsToExclude']         = "Do-Not-Delete"

ec2       = boto3.resource('ec2', region_name = globalVars['REGION_NAME'] )

def lambda_handler(event, context):

    deletedVolumes=[]

    # Get all the volumes in the region
    for vol in ec2.volumes.all():
        if  vol.state=='available':

            # Check for Tags
            if vol.tags is None:
                vid=vol.id
                v=ec2.Volume(vol.id)
                v.delete()

                deletedVolumes.append({'VolumeId': vol.id,'Status':'Delete Initiated'})
                print "Deleted Volume: {0} for not having Tags".format( vid )

                continue

            # Find Value for Tag with Key as "Name"
            for tag in vol.tags:
                if tag['Key'] == globalVars['findNeedle']:
                  value=tag['Value']
                  if value != globalVars['tagsToExclude'] and vol.state == 'available' :
                    vid = vol.id
                    v = ec2.Volume(vol.id)
                    v.delete()
                    deletedVolumes.append( {'VolumeId': vol.id,'Status':'Delete Initiated'} )
                    print "Deleted Volume: {0} for not having Tags".format( vid )

    # If no Volumes are deleted, to return consistent json output
    if not deletedVolumes:
        deletedVolumes.append({'VolumeId':None,'Status':None})

    # Return the list of status of the snapshots triggered by lambda as list
    return deletedVolumes
