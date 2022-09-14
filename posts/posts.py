from cdktf import Resource, TerraformVariable
from constructs import Construct
from cdktf_cdktf_provider_google_beta import GoogleComputeGlobalAddress, GoogleComputeNetwork, GoogleServiceNetworkingConnection
from posts.cloudfunctions.index import CloudFunction
from posts.storage import Storage


class Posts(Resource):

    https_trigger_url: str

    def __init__(self, scope: Construct, id: str, environment: str, user: str, project: str, db_pass: str):
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
            vpc_id = vpc.id,
            db_pass = db_pass
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
