# CDK for Terraform Serverless Application in Python (Google Cloud Provider)

This repository contains an end to end serverless web app hosted on GCP and deployed with [CDK for Terraform](https://cdk.tf) in Python. In more application specific terms, we are deploying serverless infrastructure for a web app that has a list of posts and a modal to create a new post by specifying author and content. For more information regarding setup and the features of CDKTF [please refer to these docs](https://www.terraform.io/cdktf).

## Techstack

Frontend: React, Create React App, statically hosted via Google Cloud Storage
Backend API: GCP Cloud Function + Cloud SQL


## Application

### Stacks 

We will have two primary Stacks– PostsStack and FrontendStack

The Post and Frontend class encapsulate the finer details of infrastructure provisioned for each respective Stack. The first parameter denotes the scope of the infrastructure being provision– we use `self` to tie the infrastructure contained in Post/Frontend to the Stack in which it is contained, the same is true with `GoogleBetaProvider`. 

```python
class PostsStack(TerraformStack):

    http_trigger_url: str

    def __init__(self, scope: Construct, name: str, environment: str, project: str):
        super().__init__(scope, name)

        GoogleBetaProvider(self,
            id = "google-beta",
            region = "us-east1",
            project = project
        )
        posts = Posts(self, 
            id = "posts", 
            environment = environment, 
            project = project
        )

        self.http_trigger_url = posts.https_trigger_url
``` 

```python
class FrontendStack(TerraformStack):
    def __init__(self, scope: Construct, name: str, environment: str, project: str, http_trigger_url: str):
        super().__init__(scope, name)

        GoogleBetaProvider(self,
            id = "google-beta",
            region = "us-east1",
            project = project
        )
        LocalProvider(self, "local")
        Frontend(self,
            id = "frontend",
            project = project,
            environment = environment,
            https_trigger_url = http_trigger_url
        )
 
```

In using different Stacks to separate aspects of our infrastructure we allow for separation in state management of the frontend and backend– making alteration and redeployment of a specific piece of infrastructure a simpler process. Additionally, this allows for the instantiation of the same resource multiple times throughout.

For example…

```python
# In main.py
 
postsDev = PostsStack(app, "posts-dev", 
    environment="development", 
    project = "python-gcp-72926"
)
frontendDev = FrontendStack(app, "frontend-dev", 
    environment="development", 
    project="python-gcp-72926", 
    http_trigger_url=postsDev.http_trigger_url
)
postProd = PostsStack(app, "posts-prod", 
    environment="production", 
    project = "python-gcp-72926"
)
frontendProd = FrontendStack(app, "frontend-prod", 
    environment="production", 
    project="python-gcp-72926", 
    http_trigger_url=postsProd.http_trigger_url
)
```
Here we created separate instances of the infrastructure for the frontend and backend with different naming of the resources in each application environment (by ways of the environment param), with the ease of adding additional as needed. 

## Posts

The Posts class melds two elements together– the Cloud SQL DB and our Cloud Function that takes our new Cloud SQL DB for setting up the Cloud Function's environment. 

```python
class Posts(Resource):

    https_trigger_url: str

    def __init__(self, scope: Construct, id: str, environment: str, project: str):
        super().__init__(scope, id)

        #NETWORKING
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

        storage = Storage(self, "cloud-sql", environment, project, private_vpc_connection, vpc)

        cloud_function = CloudFunction(self, "cloud-function", environment, project, vpc, storage.db_instance, storage.db, storage.db_user)

        self.https_trigger_url = cloud_function.https_trigger_url
 
```

Additionally we provision a VPC for our Cloud SQL instance to reside.

### Storage

In the Storage class we create our Cloud SQL instance and DB user credentials for accessing the Cloud SQL instance. All attributes are made accessible as we will later use them in the creation of our Cloud Function

```python
class Storage(Resource):

    db_instance: GoogleSqlDatabaseInstance
    db: GoogleSqlDatabase
    db_user: GoogleSqlUser

    def __init__(self, scope: Construct, id: str, env: str, project: str, private_vpc_connection: GoogleServiceNetworkingConnection, vpc: GoogleComputeNetwork):
        super().__init__(scope,id)

        db_instance = GoogleSqlDatabaseInstance(self,
            id_ = "db-react-app-instance-{}".format(env),
            name = "db-react-app-instance-{}".format(env),
            project = project,
            region = "us-east4",
            depends_on = [private_vpc_connection],
            settings = GoogleSqlDatabaseInstanceSettings(
                tier = "db-f1-micro",
                availability_type =  "REGIONAL",
                user_labels = {
                    "environment": env
                },
                ip_configuration = GoogleSqlDatabaseInstanceSettingsIpConfiguration(
                    ipv4_enabled = False,
                    private_network = vpc.id
                )
            ),
            database_version = "POSTGRES_13",
            deletion_protection = False
        )

        db = GoogleSqlDatabase(self,
            id_ = "db-react-app-{}-2739".format(env),
            name = "db-react-app-{}-2739".format(env),
            project = project,
            instance = db_instance.id
        )
        
        db_user = GoogleSqlUser(self,
            id_ = "react-app-db-user-{}-28u402".format(env),
            name = "react-app-db-user-{}-28u402".format(env),
            project = project,
            instance= db_instance.id,
            password = "awsufjrkdn"

        )

        self.db_instance = db_instance
        self.db = db
        self.db_user = db_user
```

### CloudFunction

```python
class CloudFunction(Resource):

    https_trigger_url: str

    def __init__(self, scope: Construct, id: str, env: str, project: str, vpc: GoogleComputeNetwork, db_instance: GoogleSqlDatabaseInstance, db: GoogleSqlDatabase, db_user: GoogleSqlUser):
        super().__init__(scope, id)

        cloud_functions_storage = GoogleStorageBucket(self,
            #...
        )

        vpc_connector = GoogleVpcAccessConnector(self,
            #...
        )
        
        shutil.make_archive("func_archive", "zip", os.path.join(os.getcwd(),"posts/cloudfunctions/api"))

        func_archive = GoogleStorageBucketObject(self, 
            #...
        )

        api = GoogleCloudfunctionsFunction(self,
            #...
        )

        GoogleCloudfunctionsFunctionIamMember(self,
            #...
        )

        self.https_trigger_url = api.https_trigger_url
```

In our CloudFunction Class we first provision a Cloud Storage bucket to house the contents of the Cloud Function to be deployed. 

```python
cloud_functions_storage = GoogleStorageBucket(self,
    name = "cloud-functions-{}-89264".format(env,),
    id_ = "cloud-functions-{}-89264".format(env,),
    project = project,
    force_destroy = True,
    location = "us-east1",
    storage_class = "STANDARD"
)
```

We then zip the folder that contains our Cloud Function's implementation and create a Storage Bucket Object for the now zipped implementation

```python
shutil.make_archive("func_archive", "zip", os.path.join(os.getcwd(),"posts/cloudfunctions/api"))
func_archive = GoogleStorageBucketObject(self, 
    id_ = "functions-archiveea-{}".format(env),
    name = "functions-archiveea-{}".format(env),
    bucket = cloud_functions_storage.name,
    source = os.path.join(os.getcwd(), "./func_archive.zip")
)
```

The VPC connector that will handle traffic between our Cloud Function and Cloud SQL DB

```python
vpc_connector = GoogleVpcAccessConnector(self,
    id_  = "msvmxw-tzag9-a9k2jl45f3s",
    name = "msvmxw-tzag9-a9k2jl45f3s",
    project = project,
    region = "us-east4",
    ip_cidr_range = "10.8.0.0/28",
    network = vpc.id
)
```

We finally create the Cloud Function and associative IAM role

```python
api = GoogleCloudfunctionsFunction(self,
    id_ = "cloud-function-api-{}".format(env),
    name = "cloud-function-api-{}".format(env),
    project = project,
    region = "us-east4",
    runtime = "nodejs14",
    available_memory_mb = 128,
    source_archive_bucket = cloud_functions_storage.name,
    source_archive_object =  func_archive.name,
    trigger_http = True,
    entry_point = "app",
    environment_variables = {
        "DB_HOST": db_instance.private_ip_address+":5432",
        "DB_USER": db_user.name,
        "DB_PASS": db_user.password,
        "DB_NAME": db.name
    },
    vpc_connector = vpc_connector.id
)

GoogleCloudfunctionsFunctionIamMember(self,
    id_ = "cloud-func-iam-{}".format(env),
    cloud_function = api.name,
    project = project,
    region = "us-east4",
    role = "roles/cloudfunctions.invoker",
    member = "allUsers"
)
```

The trigger url for our Cloud Function is made accessible so we later hand it off to the Frontend of our react app 

```python
self.https_trigger_url = api.https_trigger_url
```


## Frontend

We will host the contents of our website statically in a Google Storage Bucket– permissions to accessing object in this bucket are then given

```python 
class Frontend(Resource):

    def __init__(self, scope: Construct, id: str, project: str, environment: str, https_trigger_url: str):
        super().__init__(scope, id)

        bucket = GoogleStorageBucket(self, 
            id_ = "cdktfpython-static-site-128u0",
            name = "cdktfpython-static-site-128u0",
            project = project,
            location = "us-east1",
            storage_class = "STANDARD",
            force_destroy = True,
            
            website = GoogleStorageBucketWebsite(
                main_page_suffix = "index.html",
                not_found_page   = "index.html"
            ),

        )
        GoogleStorageDefaultObjectAccessControl(self,
            id_ = "bucket-access-control-{}".format(environment),
            bucket = bucket.name,
            role = "READER",
            entity = "allUsers"
        )

        #NETWORK
        external_ip = GoogleComputeGlobalAddress(self,
            name = "external-react-app-ip-{}".format(environment),
            id_ = "external-react-app-ip-{}".format(environment),
            project = project,
            address_type = "EXTERNAL",
            ip_version = "IPV4",
            description  = "IP address for React app"
        )
        GoogleComputeProjectDefaultNetworkTier(self, 
            project = project,
            id_ = "networktier",
            network_tier = "PREMIUM"
        )
        static_site = GoogleComputeBackendBucket(self,
            name = "static-site-backend",
            id_ = "static-site-backend",
            project = project, 
            description = "Contains files needed by the website",
            bucket_name = bucket.name,
            enable_cdn = True
        )
        ssl_cert = GoogleComputeManagedSslCertificate(self,
            name = "ssl-certificate",
            id_ = "ssl-certificate",
            project = project,
            managed = 
                GoogleComputeManagedSslCertificateManaged(
                    domains = ["cdktfpython.com", "www.cdktfpython.com"] 
                )
        )
        web_https = GoogleComputeUrlMap(self,
            name = "web-url-map-https",
            id_ = "web-url-map-https",
            project = project,
            default_service = static_site.self_link
        )
        https_proxy = GoogleComputeTargetHttpsProxy(self,
            name = "web-target-proxy-https",
            id_ = "web-target-proxy-https",
            project = project,
            url_map = web_https.id,
            ssl_certificates = [ssl_cert.self_link]
        )
        GoogleComputeGlobalForwardingRule(self,
            name = "web-forwarding-rule-https",
            id_ = "web-forwarding-rule-https",
            project = project,
            load_balancing_scheme = "EXTERNAL",
            ip_address = external_ip.address,
            ip_protocol = "TCP", 
            port_range = "443",
            target = https_proxy.self_link
        )
        web_http = GoogleComputeUrlMap(self,
            name = "web-url-map-http",
            id_ = "web-url-map-http",
            project = project,
            description ="Web HTTP load balancer",
            default_url_redirect = GoogleComputeUrlMapDefaultUrlRedirect(
                https_redirect = True,
                strip_query = True
            )
        )
        http_proxy = GoogleComputeTargetHttpProxy(self,
            name = "web-target-proxy-http",
            id_ = "web-target-proxy-http",
            project = project,
            description = "HTTP target proxy",
            url_map = web_http.id,
        )
        GoogleComputeGlobalForwardingRule(self,
            name = "web-forwarding-rule-http",
            id_ = "web-forwarding-rule-http",
            project = project,
            load_balancing_scheme = "EXTERNAL",
            ip_address = external_ip.address,
            ip_protocol = "TCP",
            target = http_proxy.id,
            port_range = "80"
        )


        TerraformOutput(self, "load-balancer-ip",
            value = external_ip.address
        )

        File(self, "env",
            filename = Path.join(os.getcwd(), "frontend", "code", ".env.production.local"),
            content = "BUCKET_NAME={bucket}\nREACT_APP_API_ENDPOINT={endPoint}".format(bucket = bucket.name, endPoint = https_trigger_url)
        )
```