from cdktf import Resource
from constructs import Construct
from imports.google_beta.google_compute_global_address import GoogleComputeGlobalAddress
from posts.cloudfunctions.index import CloudFunction
from posts.storage import Storage
from imports.google_beta.google_compute_network import GoogleComputeNetwork
from imports.google_beta.google_service_networking_connection import GoogleServiceNetworkingConnection



class Posts(Resource):

    https_trigger_url: str

    def __init__(self, scope: Construct, id: str, environment: str, user: str, project: str):
        super().__init__(scope, id)

        #NETWORK
        vpc = GoogleComputeNetwork(self,
            name = "vpc-{}".format(environment, user),
            id_ = "vpc-{}".format(environment, user),
            project = project,
            auto_create_subnetworks = False
        )
        private_ip = GoogleComputeGlobalAddress(self,
            name = "internal-ip-address-{}-{}".format(environment, user),
            id_ = "internal-ip-address-{}-{}".format(environment, user),
            project = project,
            purpose = "VPC_PEERING",
            address_type  = "INTERNAL",
            prefix_length = 16,
            network = vpc.id
        )
        private_vpc_connection = GoogleServiceNetworkingConnection(self,
            network = vpc.id,
            id_ = "vpc-connection-{}-{}".format(environment, user),
            service = "servicenetworking.googleapis.com",
            reserved_peering_ranges = [private_ip.name]
        )

        storage = Storage(self, "cloud-sql", 
            environment = environment,
            user = user, 
            project = project, 
            private_vpc_connection = private_vpc_connection, 
            vpc_id = vpc.id
        )

        cloud_function = CloudFunction(self, "cloud-function", 
            environment=environment,
            user = user, 
            project=project, 
            vpc_id = vpc.id, 
            db_host = storage.db_host, 
            db_name = storage.db_name, 
            db_user = storage.db_user
        )

        self.https_trigger_url = cloud_function.https_trigger_url
