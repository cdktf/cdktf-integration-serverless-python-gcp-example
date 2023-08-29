from constructs import Construct
from typing import Dict
from cdktf_cdktf_provider_google_beta.google_service_networking_connection import GoogleServiceNetworkingConnection
from cdktf_cdktf_provider_google_beta.google_sql_database import GoogleSqlDatabase
from cdktf_cdktf_provider_google_beta.google_sql_user import GoogleSqlUser
from cdktf_cdktf_provider_google_beta.google_sql_database_instance import GoogleSqlDatabaseInstance, GoogleSqlDatabaseInstanceSettings, GoogleSqlDatabaseInstanceSettingsIpConfiguration

class Storage(Construct):

    db_host: str
    db_name: str
    db_user: Dict[str, str]

    def __init__(self, scope: Construct, id: str, environment: str, user: str, project: str, private_vpc_connection: GoogleServiceNetworkingConnection, vpc_id: str, db_pass: str):
        super().__init__(scope,id)

        db_instance = GoogleSqlDatabaseInstance(self,
            id_ = "db-react-application-instance-{}-{}".format(environment, user),
            name = "db-react-application-instance-{}-{}".format(environment, user),
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
            id_ = "db-react-application-{}-{}".format(environment, user),
            name = "db-react-application-{}-{}".format(environment, user),
            project = project,
            instance = db_instance.id
        )
        
        db_user = GoogleSqlUser(self,
            id_ = "react-application-db-user-{}-{}".format(environment, user),
            name = "react-application-db-user-{}-{}".format(environment, user),
            project = project,
            instance= db_instance.id,
            password = db_pass

        )
    
        self.db_host = db_instance.private_ip_address+":5432"
        self.db_name = db.name
        self.db_user = {
            "name": db_user.name,
            "password": db_pass
        }



    



