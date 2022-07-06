from constructs import Construct
from cdktf import Resource
from cdktf_cdktf_provider_google_beta import GoogleComputeNetwork, GoogleSecretManagerSecretReplication, GoogleServiceNetworkingConnection, GoogleSqlDatabase, 
from cdktf_cdktf_provider_google_beta import GoogleSqlUser, GoogleSqlDatabaseInstance, GoogleSqlDatabaseInstanceSettings, GoogleSqlDatabaseInstanceSettingsBackupConfiguration, GoogleSqlDatabaseInstanceSettingsIpConfiguration

class Storage(Resource):

    db_host: str
    db_name: str
    db_user: dict[str, str]

    def __init__(self, scope: Construct, id: str, environment: str, project: str, private_vpc_connection: GoogleServiceNetworkingConnection, vpc_id: str):
        super().__init__(scope,id)

        db_instance = GoogleSqlDatabaseInstance(self,
            id_ = "db-react-app-instance-{}".format(environment),
            name = "db-react-app-instance-{}".format(environment),
            project = project,
            region = "us-east4",
            depends_on = [private_vpc_connection],
            settings = GoogleSqlDatabaseInstanceSettings(
                tier = "db-f1-micro",
                availability_type =  "REGIONAL",
                user_labels = {
                    "environment": environment
                },
                ip_configuration = GoogleSqlDatabaseInstanceSettingsIpConfiguration(
                    ipv4_enabled = False,
                    private_network = vpc_id
                )
            ),
            database_version = "POSTGRES_13",
            deletion_protection = False
        )

        db = GoogleSqlDatabase(self,
            id_ = "db-react-app-{}-2739".format(environment),
            name = "db-react-app-{}-2739".format(environment),
            project = project,
            instance = db_instance.id
        )
        
        db_user = GoogleSqlUser(self,
            id_ = "react-app-db-user-{}-28u402".format(environment),
            name = "react-app-db-user-{}-28u402".format(environment),
            project = project,
            instance= db_instance.id,
            password = "awsufjrkdn"

        )
    
        self.db_host = db_instance.private_ip_address+":5432"
        self.db_name = db.name
        self.db_user = {
            "name": db_user.name,
            "password": db_user.password
        }



    



