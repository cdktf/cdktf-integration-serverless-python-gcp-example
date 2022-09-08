#!/usr/bin/env python
import os
from cdktf_cdktf_provider_local import LocalProvider
from constructs import Construct
from cdktf import App, NamedRemoteWorkspace, RemoteBackend, TerraformStack, TerraformVariable
from posts.posts import Posts
from frontend.index import Frontend
from cdktf_cdktf_provider_google_beta import GoogleBetaProvider, GoogleComputeProjectDefaultNetworkTier


class FrontendStack(TerraformStack):
    def __init__(self, scope: Construct, name: str, environment: str, user: str, project: str, http_trigger_url: str):
        super().__init__(scope, name)

        GoogleBetaProvider(self,
            id = "google-beta",
            region = "us-east1",
            project = project
        )
        GoogleComputeProjectDefaultNetworkTier(self, 
            project = project,
            id_ = "networktier",
            network_tier = "PREMIUM"
        )
        LocalProvider(self, "local")
        Frontend(self,
            id = "frontend",
            project = project,
            environment = environment,
            user = user,
            https_trigger_url = http_trigger_url
        )
    

class PostsStack(TerraformStack):

    http_trigger_url: str

    def __init__(self, scope: Construct, name: str, environment: str, user: str, project: str):
        super().__init__(scope, name)

        GoogleBetaProvider(self,
            id = "google-beta",
            region = "us-east1",
            project = project
        )

        db_pass = TerraformVariable(self, "DB_PASS",
            type = "string",
            description = "DB password for the instance",
            sensitive = True
        )

        posts = Posts(self, 
            id = "posts", 
            environment = environment,
            user = user, 
            project = project,
            db_pass = db_pass
        )

        self.http_trigger_url = posts.https_trigger_url


app = App()

USE_REMOTE_BACKEND = os.getenv("USE_REMOTE_BACKEND") is not None
CDKTF_USER = os.getenv("CDKTF_USER") if os.getenv("CDKTF_USER") is not None else "default"

if os.getenv("PROJECT_ID") is not None:
    PROJECT_ID = os.getenv("PROJECT_ID")
else:
    raise Exception("PROJECT_ID env variable must be set")

# Dev 
postsDev = PostsStack(app, "posts-dev", 
    environment="development",
    user=CDKTF_USER, 
    project = PROJECT_ID
)
if(USE_REMOTE_BACKEND):
        RemoteBackend(postsDev,
            hostname= "app.terraform.io",
            organization = "terraform-demo-mad",
            workspaces=NamedRemoteWorkspace(name="cdktf-serverless-gcp-posts-dev")
        )

frontendDev = FrontendStack(app, "frontend-dev", 
    environment="development",
    user=CDKTF_USER, 
    project=PROJECT_ID, 
    http_trigger_url=postsDev.http_trigger_url
)
if(USE_REMOTE_BACKEND):
        RemoteBackend(frontendDev,
            hostname= "app.terraform.io",
            organization = "terraform-demo-mad",
            workspaces=NamedRemoteWorkspace(name="cdktf-serverless-gcp-frontend-dev")
        )

# Prod
postsProd = PostsStack(app, "posts-prod", 
    environment="production",
    user=CDKTF_USER, 
    project = PROJECT_ID
)
if(USE_REMOTE_BACKEND):
        RemoteBackend(postsProd,
            hostname= "app.terraform.io",
            organization = "terraform-demo-mad",
            workspaces=NamedRemoteWorkspace(name="cdktf-serverless-gcp-posts-prod")
        )

frontendProd = FrontendStack(app, "frontend-prod", 
    environment="production",
    user=CDKTF_USER, 
    project=PROJECT_ID, 
    http_trigger_url=postsProd.http_trigger_url
)
if(USE_REMOTE_BACKEND):
        RemoteBackend(frontendProd,
            hostname= "app.terraform.io",
            organization = "terraform-demo-mad",
            workspaces=NamedRemoteWorkspace(name="cdktf-serverless-gcp-frontend-prod")
        )

app.synth()
