import boto3

# AWS credentials and region
aws_access_key_id = 'XXXXXXXX'
aws_secret_access_key = 'XXXXXX'
session_token = 'XXXX'
aws_region = 'us-east-1'



# Initialize AWS EC2 client
ec2 = boto3.client('ec2', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, aws_session_token=session_token, region_name=aws_region)

# Function to delete snapshots
def delete_snapshot(snapshot_id):
    try:
        response = ec2.delete_snapshot(SnapshotId=snapshot_id)
        print("Snapshot deleted successfully:", snapshot_id)
    except Exception as e:
        print("Error deleting snapshot:", snapshot_id, e)

# Read snapshot IDs from a file
snapshot_file_path = 'snapshot_ids.txt'  # Replace with the path to your file

try:
    with open(snapshot_file_path, 'r') as file:
        for line in file:
            snapshot_id = line.strip()
            if snapshot_id:
                # Pass each snapshot ID as a string to the function
                delete_snapshot(snapshot_id)
except FileNotFoundError:
    print(f"File not found: {snapshot_file_path}")
    exit()

