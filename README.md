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

    def __init__(self, scope: Construct, name: str, environment: str, user: str, project: str):
        super().__init__(scope, name)

        GoogleBetaProvider(self,
            id = "google-beta",
            region = "us-east1",
            project = project
        )
        posts = Posts(self,
            id = "posts",
            environment = environment,
            user = user,
            project = project
        )

        self.http_trigger_url = posts.https_trigger_url
```

```python
class FrontendStack(TerraformStack):
    def __init__(self, scope: Construct, name: str, environment: str, user: str, project: str, http_trigger_url: str):
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
            user = user,
            https_trigger_url = http_trigger_url
        )
```

In using different Stacks to separate aspects of our infrastructure we allow for separation in state management of the frontend and backend– making alteration and redeployment of a specific piece of infrastructure a simpler process. Additionally, this allows for the instantiation of the same resource multiple times throughout.

For example…

```python
# In main.py

postsDev = PostsStack(app, "posts-dev",
    environment="development",
    user=CDKTF_USER,
    project = "python-gcp-72926"
)
frontendDev = FrontendStack(app, "frontend-dev",
    environment="development",
    user=CDKTF_USER,
    project="python-gcp-72926",
    http_trigger_url=postsDev.http_trigger_url
)
postsProd = PostsStack(app, "posts-prod",
    environment="production",
    user=CDKTF_USER,
    project = "python-gcp-72926"
)
frontendProd = FrontendStack(app, "frontend-prod",
    environment="production",
    user=CDKTF_USER,
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
```

Additionally we provision a VPC for our Cloud SQL instance to reside.

### Storage

In the Storage class we create our Cloud SQL instance and DB user credentials for accessing the Cloud SQL instance. All attributes are made accessible as we will later use them in the creation of our Cloud Function

```python
class Storage(Resource):

    db_host: str
    db_name: str
    db_user: dict[str, str]

    def __init__(self, scope: Construct, id: str, environment: str, user: str, project: str, private_vpc_connection: GoogleServiceNetworkingConnection, vpc_id: str):
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

        db_pass = DataGoogleSecretManagerSecretVersion(self,
            id_ = "db_pass",
            project = project,
            secret = os.getenv("DB_PASS"),

        )

        db_user = GoogleSqlUser(self,
            id_ = "react-application-db-user-{}-{}".format(environment, user),
            name = "react-application-db-user-{}-{}".format(environment, user),
            project = project,
            instance= db_instance.id,
            password = db_pass.secret_data

        )

        self.db_host = db_instance.private_ip_address+":5432"
        self.db_name = db.name
        self.db_user = {
            "name": db_user.name,
            "password": db_pass.secret_data
        }
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
    name = "cloud-functions-{}-{}".format(environment, user),
    id_ = "cloud-functions-{}-{}".format(environment, user),
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
    id_ = "functions-archive-{}-{}".format(environment, user),
    name = "functions-archive-{}-{}".format(environment, user),
    bucket = cloud_functions_storage.name,
    source = os.path.join(os.getcwd(), "./func_archive.zip")
)
```

The VPC connector that will handle traffic between our Cloud Function and Cloud SQL DB

```python
vpc_connector = GoogleVpcAccessConnector(self,
    id_  = "vpc-access-connector-{}-{}".format(environment, user),
    name = "vpc-access-connector-{}-{}".format(environment, user),
    project = project,
    region = "us-east4",
    ip_cidr_range = "10.8.0.0/28",
    network = vpc.id
)
```

We finally create the Cloud Function and associative IAM role

```python
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
```

The trigger url for our Cloud Function is made accessible so we later hand it off to the Frontend of our react app

```python
self.https_trigger_url = api.https_trigger_url
```

## Frontend

We will host the contents of our website statically in a Google Storage Bucket– default permissions for accessing objects in this bucket are then given

```python
bucket = GoogleStorageBucket(self,
    id_ = "cdktfpython-static-site-{}-{}".format(environment, user),
    name = "cdktfpython-static-site-{}-{}".format(environment, user),
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
    id_ = "bucket-access-control-{}-{}".format(environment, user),
    bucket = bucket.name,
    role = "READER",
    entity = "allUsers"
)
```

Here we reserve a static external IP address– we will later attach it our URL Maps.

```python
external_ip = GoogleComputeGlobalAddress(self,
    name = "external-react-app-ip-{}-{}".format(environment, user),
    id_ = "external-react-app-ip-{}-{}".format(environment, user),
    project = project,
    address_type = "EXTERNAL",
    ip_version = "IPV4",
    description  = "IP address for React app"
)
```

A GoogleComputeBackendBucket is used to access the static site files with HTTPS load balancing

```python
static_site = GoogleComputeBackendBucket(self,
    name = "static-site-backend-{}-{}".format(environment, user),
    id_ = "static-site-backend-{}-{}".format(environment, user),
    project = project,
    description = "Contains files needed by the website",
    bucket_name = bucket.name,
    enable_cdn = True
)
```

We define URL Maps for both HTTPS and HTTP targets so as to use HTTPS redirect in our applications load balancer. Additionally we create a SSL certificate and attach it to our HTTPS target.

```python
ssl_cert = GoogleComputeManagedSslCertificate(self,
    name = "ssl-certificate-{}-{}".format(environment, user),
    id_ = "ssl-certificate-{}-{}".format(environment, user),
    project = project,
    managed =
        GoogleComputeManagedSslCertificateManaged(
            domains = ["cdktfpython.com", "www.cdktfpython.com"]
        )
)
web_https = GoogleComputeUrlMap(self,
    name = "web-url-map-https-{}-{}".format(environment, user),
    id_ = "web-url-map-https-{}-{}".format(environment, user),
    project = project,
    default_service = static_site.self_link
)
https_proxy = GoogleComputeTargetHttpsProxy(self,
    name = "web-target-proxy-https-{}-{}".format(environment, user),
    id_ = "web-target-proxy-https-{}-{}".format(environment, user),
    project = project,
    url_map = web_https.id,
    ssl_certificates = [ssl_cert.self_link]
)
GoogleComputeGlobalForwardingRule(self,
    name = "web-forwarding-rule-https-{}-{}".format(environment, user),
    id_ = "web-forwarding-rule-https-{}-{}".format(environment, user),
    project = project,
    load_balancing_scheme = "EXTERNAL",
    ip_address = external_ip.address,
    ip_protocol = "TCP",
    port_range = "443",
    target = https_proxy.self_link
)
web_http = GoogleComputeUrlMap(self,
    name = "web-url-map-http-{}-{}".format(environment, user),
    id_ = "web-url-map-http-{}-{}".format(environment, user),
    project = project,
    description ="Web HTTP load balancer",
    default_url_redirect = GoogleComputeUrlMapDefaultUrlRedirect(
        https_redirect = True,
        strip_query = True
    )
)
http_proxy = GoogleComputeTargetHttpProxy(self,
    name = "web-target-proxy-http-{}-{}".format(environment, user),
    id_ = "web-target-proxy-http-{}-{}".format(environment, user),
    project = project,
    description = "HTTP target proxy",
    url_map = web_http.id,
)
GoogleComputeGlobalForwardingRule(self,
    name = "web-forwarding-rule-http-{}-{}".format(environment, user),
    id_ = "web-forwarding-rule-http-{}-{}".format(environment, user),
    project = project,
    load_balancing_scheme = "EXTERNAL",
    ip_address = external_ip.address,
    ip_protocol = "TCP",
    target = http_proxy.id,
    port_range = "80"
)
```

Lastly, we create environment variables for our GoogleStorageBucket's name (for uploading the static site file) and our HTTPS trigger URL (for making requests to Cloud Function) to our Frontend implementation.

```python
File(self, "env",
    filename = Path.join(os.getcwd(), "frontend", "code", ".env.production.local"),
    content = "BUCKET_NAME={bucket}\nREACT_APP_API_ENDPOINT={endPoint}".format(bucket = bucket.name, endPoint = https_trigger_url)
)
```

## License

[Mozilla Public License v2.0](https://github.com/hashicorp/cdktf-integration-serverless-python-gcp-example/blob/main/LICENSE)
