import os
import os.path as Path
from constructs import Construct
from cdktf import Resource, TerraformOutput
from imports.local import File
from imports.google_beta import GoogleStorageBucket, GoogleStorageBucketWebsite, GoogleStorageDefaultObjectAccessControl, GoogleComputeBackendBucket
from imports.google_beta import GoogleComputeProjectDefaultNetworkTier, GoogleComputeManagedSslCertificate, GoogleComputeManagedSslCertificateManaged, GoogleComputeTargetHttpsProxy
from imports.google_beta import GoogleComputeUrlMap, GoogleComputeTargetHttpProxy, GoogleComputeGlobalForwardingRule, GoogleComputeUrlMapDefaultUrlRedirect, GoogleComputeGlobalAddress


class Frontend(Resource):

    def __init__(self, scope: Construct, id: str, project: str, environment: str, user: str, https_trigger_url: str):
        super().__init__(scope, id)

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

        #NETWORKING
        external_ip = GoogleComputeGlobalAddress(self,
            name = "external-react-app-ip-{}-{}".format(environment, user),
            id_ = "external-react-app-ip-{}-{}".format(environment, user),
            project = project,
            address_type = "EXTERNAL",
            ip_version = "IPV4",
            description  = "IP address for React app"
        )
        
        static_site = GoogleComputeBackendBucket(self,
            name = "static-site-backend-{}-{}".format(environment, user),
            id_ = "static-site-backend-{}-{}".format(environment, user),
            project = project, 
            description = "Contains files needed by the website",
            bucket_name = bucket.name,
            enable_cdn = True
        )
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

        File(self, "env",
            filename = Path.join(os.getcwd(), "frontend", "code", ".env.production.local"),
            content = "BUCKET_NAME={bucket}\nREACT_APP_API_ENDPOINT={endPoint}".format(bucket = bucket.name, endPoint = https_trigger_url)
        )
