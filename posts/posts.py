from cdktf import Resource
from constructs import Construct
from cdktf_cdktf_provider_google_beta import GoogleComputeGlobalAddress, GoogleComputeNetwork, GoogleServiceNetworkingConnection
from posts.cloudfunctions.index import CloudFunction
from posts.storage import Storage


class Posts(Resource):

    https_trigger_url: str

    def __init__(self, scope: Construct, id: str, environment: str, project: str):
        super().__init__(scope, id)

        #NETWORK
        vpc = GoogleComputeNetwork(self,
            name = "vpc-{}".format(environment),
            id_ = "vpc-{}".format(environment),
            project = project,
            auto_create_subnetworks = False
        )
        private_ip = GoogleComputeGlobalAddress(self,
            name = "internal-ip-address-{}".format(environment),
            id_ = "internal-ip-address-{}".format(environment),
            project = project,
            purpose = "VPC_PEERING",
            address_type  = "INTERNAL",
            prefix_length = 16,
            network = vpc.id
        )
        private_vpc_connection = GoogleServiceNetworkingConnection(self,
            network = vpc.id,
            id_ = "vpc-connection-{}".format(environment),
            service = "servicenetworking.googleapis.com",
            reserved_peering_ranges = [private_ip.name]
        )

        storage = Storage(self, "cloud-sql", 
            environment = environment, 
            project = project, 
            private_vpc_connection = private_vpc_connection, 
            vpc_id = vpc.id
        )

        cloud_function = CloudFunction(self, "cloud-function", 
            environment=environment, 
            project=project, 
            vpc_id = vpc.id, 
            db_host = storage.db_host, 
            db_name = storage.db_name, 
            db_user = storage.db_user
        )

        self.https_trigger_url = cloud_function.https_trigger_url
