import shutil
import os
from constructs import Construct
from cdktf_cdktf_provider_google_beta.google_storage_bucket import GoogleStorageBucket
from cdktf_cdktf_provider_google_beta.google_storage_bucket_object import GoogleStorageBucketObject
from cdktf_cdktf_provider_google_beta.google_vpc_access_connector import GoogleVpcAccessConnector
from cdktf_cdktf_provider_google_beta.google_cloudfunctions_function import GoogleCloudfunctionsFunction
from cdktf_cdktf_provider_google_beta.google_cloudfunctions_function_iam_member import GoogleCloudfunctionsFunctionIamMember

class CloudFunction(Construct):

    https_trigger_url: str
   
    def __init__(self, scope: Construct, id: str, environment: str, user: str, project: str, vpc_id: str, db_host: str, db_name: str, db_user: dict[str, str]):
        super().__init__(scope, id)

        cloud_functions_storage = GoogleStorageBucket(self,
            name = "cloud-functions-{}-{}".format(environment, user),
            id_ = "cloud-functions-{}-{}".format(environment, user),
            project = project,
            force_destroy = True,
            location = "us-east1",
            storage_class = "STANDARD"
        )

        vpc_connector = GoogleVpcAccessConnector(self,
            id_  = "msvmxw-tzag9-a9k2jl45f3s",
            name = "msvmxw-tzag9-a9k2jl45f3s",
            project = project,
            region = "us-east1",
            ip_cidr_range = "10.8.0.0/28",
            network = vpc_id
        )
        
        shutil.make_archive("func_archive", "zip", os.path.join(os.getcwd(),"posts/cloudfunctions/api"))

        func_archive = GoogleStorageBucketObject(self, 
            id_ = "functions-archive-{}-{}".format(environment, user),
            name = "functions-archive-{}-{}".format(environment, user),
            bucket = cloud_functions_storage.name,
            source = os.path.join(os.getcwd(), "./func_archive.zip")
        )

        api = GoogleCloudfunctionsFunction(self,
            id_ = "cloud-function-api-{}-{}".format(environment, user),
            name = "cloud-function-api-{}-{}".format(environment, user),
            project = project,
            region = "us-east1",
            runtime = "nodejs14",
            available_memory_mb = 128,
            source_archive_bucket = cloud_functions_storage.name,
            source_archive_object =  func_archive.name,
            trigger_http = True,
            entry_point = "app",
            environment_variables = {
                "DB_HOST": db_host,
                "DB_USER": db_user["name"],
                "DB_PASS": db_user["password"],
                "DB_NAME": db_name
            },
            vpc_connector = vpc_connector.id
        )

        GoogleCloudfunctionsFunctionIamMember(self,
            id_ = "cloud-function-iam-{}-{}".format(environment, user),
            cloud_function = api.name,
            project = project,
            region = "us-east1",
            role = "roles/cloudfunctions.invoker",
            member = "allUsers"
        )

        self.https_trigger_url = api.https_trigger_url



