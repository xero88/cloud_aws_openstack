import sys
import boto3
from botocore.exceptions import ClientError

client = boto3.client('ec2',region_name='eu-central-1')



def get_credentials(provider, filename):

    """

        The config file should have the follwing format

        [switch]

        project = <your_project_name>

        username = <your_username>

        region = <region>

        keypair = <your_keypair>

        secgrp  = <your_secgrp>

        [aws]

        keypair = <your_keypair>

        secgrp  = <your_secgrp>

    """



    import configparser

    cp = configparser.ConfigParser()

    cp.read(filename)

    provider = "aws"

    return cp.get(provider, 'keypair'), cp.get(provider, 'secgrp')





def create_connection():
	"""To complete"""
	ec2 = boto3.resource('ec2')
	return ec2


def delete_server(conn, instance):
	"""To complete"""
	conn.terminate_instances(
    InstanceIds=instance,
    DryRun=True|False)





def create_server(conn, ami_id, flv, key, grp, userdata=""):
	"""To complete"""
	response = conn.create_instances(
		ImageId=ami_id,
		InstanceType = flv,
		KeyName = key,
		SecurityGroups = grp
	)
	
	instance = response[0]
	instance.wait_until_running()
	instance.load()
	id = instance.instance_id
	return conn.Instance(id)


def main():

    SPOTIFY_ID="c56e035497e14c67b9bceb5e4ffbb973"
    SPOTIFY_SECRET="378b3b723b874c28b454452c60f8c802"
    EVENTFUL="To Fill"
    GMAP = "AIzaSyCF79khefmHjh6aG2QEfPP4XqGsn5oAe8c"



    MONGO_IMG = 'ami-0b7b8324315a7884f'
    BACKEND_IMG = 'ami-0e63983166a412821'
    FRONTEND_IMG = 'ami-01bbd4e258949b5f7'



    print("Login phase...")



    keypair, secgrp = get_credentials('aws', 'provider.conf')

    conn = create_connection()

    print("Create MongoDB instance: ")

    mongo = create_server(conn, MONGO_IMG, 't2.micro', keypair, secgrp)



    mongo_ip = mongo["PrivateDnsName"]

    import time

    time.sleep(10)

    database = "mongodb://%s:%d/festivaldb" % (mongo_ip, 27017)



    print("Create BackEnd instance: ")



    userdata = '''#!/usr/bin/env bash

cd /home/ubuntu/FSEArchive/server

echo "SPOTIFY_ID=%s" >> /home/ubuntu/FSEArchive/server/keys.env

echo "SPOTIFY_SECRET=%s" >> /home/ubuntu/FSEArchive/server/keys.env

echo "EVENTFUL=%s" >> /home/ubuntu/FSEArchive/server/keys.env

echo "DATABASE=%s" >> /home/ubuntu/FSEArchive/server/keys.env

nohup /home/ubuntu/FSEArchive/node-v8.11.4-linux-x64/bin/node start.js > /dev/null &

''' % (SPOTIFY_ID, SPOTIFY_SECRET, EVENTFUL, database)



    backend = create_server(conn, BACKEND_IMG, 't2.micro', keypair, secgrp, userdata)



    print("Create FrontEnd instance: ")

    userdata = '''#!/usr/bin/env bash

cd /home/ubuntu/FSEArchive/client

echo "GMAP=%s" >> /home/ubuntu/FSEArchive/client/keys.env

nohup /home/ubuntu/FSEArchive/node-v8.11.4-linux-x64/bin/node start.js --serverPublic=%s > /dev/null &

''' % (GMAP, "http://%s:3000" % backend["PublicDnsName"])

    front = create_server(conn, FRONTEND_IMG, 't2.micro', keypair, secgrp, userdata)



    delete = 'N'



    while delete != 'A':

        delete = input('Abort (A) ?')



    delete_server(conn, mongo)

    delete_server(conn, backend)

    delete_server(conn, front)





if __name__ == "__main__":

    main()

