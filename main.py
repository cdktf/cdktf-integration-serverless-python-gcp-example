#!/usr/bin/env python
import os
from cdktf_cdktf_provider_local import LocalProvider
from constructs import Construct
from cdktf import App, TerraformStack
from posts.posts import Posts
from frontend.index import Frontend
from cdktf_cdktf_provider_google_beta import GoogleBetaProvider


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


app = App()

USE_REMOTE_BACKEND = os.getenv("USE_REMOTE_BACKEND") is not None

# Dev 
postsDev = PostsStack(app, "posts-dev", 
    environment="development", 
    project = "python-gcp-72926"
)
if(USE_REMOTE_BACKEND):
        RemoteBackend(postsDev,
            hostname= "app.terraform.io",
            organization = "terraform-demo-mad",
            workspaces=NamedRemoteWorkspace(name="cdktf-serverless-gcp-posts-dev")
        )

frontendDev = FrontendStack(app, "frontend-dev", 
    environment="development", 
    project="python-gcp-72926", 
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
    project = "python-gcp-72926"
)
if(USE_REMOTE_BACKEND):
        RemoteBackend(postsProd,
            hostname= "app.terraform.io",
            organization = "terraform-demo-mad",
            workspaces=NamedRemoteWorkspace(name="cdktf-serverless-gcp-posts-prod")
        )

frontendProd = FrontendStack(app, "frontend-prod", 
    environment="production", 
    project="python-gcp-72926", 
    http_trigger_url=postsProd.http_trigger_url
)
if(USE_REMOTE_BACKEND):
        RemoteBackend(frontendProd,
            hostname= "app.terraform.io",
            organization = "terraform-demo-mad",
            workspaces=NamedRemoteWorkspace(name="cdktf-serverless-gcp-frontend-prod")
        )

app.synth()
