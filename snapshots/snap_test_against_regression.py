# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_against_regression_frontend 1'] = '''{
  "provider": {
    "google-beta": [
      {
        "project": "test",
        "region": "us-east1"
      }
    ],
    "local": [
      {
      }
    ]
  },
  "resource": {
    "google_compute_backend_bucket": {
      "frontend_static-site-backend-test-regression-test_43BA3AE1": {
        "bucket_name": "${google_storage_bucket.frontend_cdktfpython-static-site-test-regression-test_C640BFCE.name}",
        "description": "Contains files needed by the website",
        "enable_cdn": true,
        "name": "static-site-backend-test-regression-test",
        "project": "test"
      }
    },
    "google_compute_global_address": {
      "frontend_external-react-app-ip-test-regression-test_D0891BF2": {
        "address_type": "EXTERNAL",
        "description": "IP address for React app",
        "ip_version": "IPV4",
        "name": "external-react-app-ip-test-regression-test",
        "project": "test"
      }
    },
    "google_compute_global_forwarding_rule": {
      "frontend_web-forwarding-rule-http-test-regression-test_9E7C2941": {
        "ip_address": "${google_compute_global_address.frontend_external-react-app-ip-test-regression-test_D0891BF2.address}",
        "ip_protocol": "TCP",
        "load_balancing_scheme": "EXTERNAL",
        "name": "web-forwarding-rule-http-test-regression-test",
        "port_range": "80",
        "project": "test",
        "target": "${google_compute_target_http_proxy.frontend_web-target-proxy-http-test-regression-test_734A1017.id}"
      },
      "frontend_web-forwarding-rule-https-test-regression-test_0AD1F9E8": {
        "ip_address": "${google_compute_global_address.frontend_external-react-app-ip-test-regression-test_D0891BF2.address}",
        "ip_protocol": "TCP",
        "load_balancing_scheme": "EXTERNAL",
        "name": "web-forwarding-rule-https-test-regression-test",
        "port_range": "443",
        "project": "test",
        "target": "${google_compute_target_https_proxy.frontend_web-target-proxy-https-test-regression-test_A0DD0AC9.self_link}"
      }
    },
    "google_compute_managed_ssl_certificate": {
      "frontend_ssl-certificate-test-regression-test_0A09D97D": {
        "managed": {
          "domains": [
            "cdktfpython.com",
            "www.cdktfpython.com"
          ]
        },
        "name": "ssl-certificate-test-regression-test",
        "project": "test"
      }
    },
    "google_compute_project_default_network_tier": {
      "networktier": {
        "network_tier": "PREMIUM",
        "project": "test"
      }
    },
    "google_compute_target_http_proxy": {
      "frontend_web-target-proxy-http-test-regression-test_734A1017": {
        "description": "HTTP target proxy",
        "name": "web-target-proxy-http-test-regression-test",
        "project": "test",
        "url_map": "${google_compute_url_map.frontend_web-url-map-http-test-regression-test_CAFD6E5A.id}"
      }
    },
    "google_compute_target_https_proxy": {
      "frontend_web-target-proxy-https-test-regression-test_A0DD0AC9": {
        "name": "web-target-proxy-https-test-regression-test",
        "project": "test",
        "ssl_certificates": [
          "${google_compute_managed_ssl_certificate.frontend_ssl-certificate-test-regression-test_0A09D97D.self_link}"
        ],
        "url_map": "${google_compute_url_map.frontend_web-url-map-https-test-regression-test_192FE95B.id}"
      }
    },
    "google_compute_url_map": {
      "frontend_web-url-map-http-test-regression-test_CAFD6E5A": {
        "default_url_redirect": {
          "https_redirect": true,
          "strip_query": true
        },
        "description": "Web HTTP load balancer",
        "name": "web-url-map-http-test-regression-test",
        "project": "test"
      },
      "frontend_web-url-map-https-test-regression-test_192FE95B": {
        "default_service": "${google_compute_backend_bucket.frontend_static-site-backend-test-regression-test_43BA3AE1.self_link}",
        "name": "web-url-map-https-test-regression-test",
        "project": "test"
      }
    },
    "google_storage_bucket": {
      "frontend_cdktfpython-static-site-test-regression-test_C640BFCE": {
        "force_destroy": true,
        "location": "us-east1",
        "name": "cdktfpython-static-site-test-regression-test",
        "project": "test",
        "storage_class": "STANDARD",
        "website": {
          "main_page_suffix": "index.html",
          "not_found_page": "index.html"
        }
      }
    },
    "google_storage_default_object_access_control": {
      "frontend_bucket-access-control-test-regression-test_158F9F14": {
        "bucket": "${google_storage_bucket.frontend_cdktfpython-static-site-test-regression-test_C640BFCE.name}",
        "entity": "allUsers",
        "role": "READER"
      }
    },
    "local_file": {
      "frontend_env_FADFC9DB": {
        "content": "BUCKET_NAME=${google_storage_bucket.frontend_cdktfpython-static-site-test-regression-test_C640BFCE.name}\\nREACT_APP_API_ENDPOINT=N/A",
        "filename": "/Users/mark.decrane/cdktf-example-projects/cdktf-integration-serverless-python-gcp-example/frontend/code/.env.production.local"
      }
    }
  },
  "terraform": {
    "required_providers": {
      "google-beta": {
        "source": "google-beta",
        "version": "4.78.0"
      },
      "local": {
        "source": "hashicorp/local",
        "version": "2.4.0"
      }
    }
  }
}'''

snapshots['test_against_regression_posts 1'] = '''{
  "provider": {
    "google-beta": [
      {
        "project": "test",
        "region": "us-east1"
      }
    ]
  },
  "resource": {
    "google_cloudfunctions_function": {
      "posts_cloud-function_cloud-function-api-test-regression-test_4ADFFD59": {
        "available_memory_mb": 128,
        "entry_point": "app",
        "environment_variables": {
          "DB_HOST": "${google_sql_database_instance.posts_cloud-sql_db-react-application-instance-test-regression-test_5482FDD0.private_ip_address}:5432",
          "DB_NAME": "${google_sql_database.posts_cloud-sql_db-react-application-test-regression-test_5F20323B.name}",
          "DB_PASS": "${var.DB_PASS}",
          "DB_USER": "${google_sql_user.posts_cloud-sql_react-application-db-user-test-regression-test_80758EA7.name}"
        },
        "name": "cloud-function-api-test-regression-test",
        "project": "test",
        "region": "us-east1",
        "runtime": "nodejs14",
        "source_archive_bucket": "${google_storage_bucket.posts_cloud-function_cloud-functions-test-regression-test_1CDFFE1A.name}",
        "source_archive_object": "${google_storage_bucket_object.posts_cloud-function_functions-archive-test-regression-test_5F080BE5.name}",
        "trigger_http": true,
        "vpc_connector": "${google_vpc_access_connector.posts_cloud-function_msvmxw-tzag9-a9k2jl45f3s_F8049A5E.id}"
      }
    },
    "google_cloudfunctions_function_iam_member": {
      "posts_cloud-function_cloud-function-iam-test-regression-test_03638C21": {
        "cloud_function": "${google_cloudfunctions_function.posts_cloud-function_cloud-function-api-test-regression-test_4ADFFD59.name}",
        "member": "allUsers",
        "project": "test",
        "region": "us-east1",
        "role": "roles/cloudfunctions.invoker"
      }
    },
    "google_compute_global_address": {
      "posts_internal-ip-address-test-regression-test_02FEC0D0": {
        "address_type": "INTERNAL",
        "name": "internal-ip-address-test-regression-test",
        "network": "${google_compute_network.posts_vpc-test_193AFE9F.id}",
        "prefix_length": 16,
        "project": "test",
        "purpose": "VPC_PEERING"
      }
    },
    "google_compute_network": {
      "posts_vpc-test_193AFE9F": {
        "auto_create_subnetworks": false,
        "name": "vpc-test",
        "project": "test"
      }
    },
    "google_service_networking_connection": {
      "posts_vpc-connection-test-regression-test_9359A8C4": {
        "network": "${google_compute_network.posts_vpc-test_193AFE9F.id}",
        "reserved_peering_ranges": [
          "${google_compute_global_address.posts_internal-ip-address-test-regression-test_02FEC0D0.name}"
        ],
        "service": "servicenetworking.googleapis.com"
      }
    },
    "google_sql_database": {
      "posts_cloud-sql_db-react-application-test-regression-test_5F20323B": {
        "instance": "${google_sql_database_instance.posts_cloud-sql_db-react-application-instance-test-regression-test_5482FDD0.id}",
        "name": "db-react-application-test-regression-test",
        "project": "test"
      }
    },
    "google_sql_database_instance": {
      "posts_cloud-sql_db-react-application-instance-test-regression-test_5482FDD0": {
        "database_version": "POSTGRES_13",
        "deletion_protection": false,
        "depends_on": [
          "google_service_networking_connection.posts_vpc-connection-test-regression-test_9359A8C4"
        ],
        "name": "db-react-application-instance-test-regression-test",
        "project": "test",
        "region": "us-east4",
        "settings": {
          "availability_type": "REGIONAL",
          "ip_configuration": {
            "ipv4_enabled": false,
            "private_network": "${google_compute_network.posts_vpc-test_193AFE9F.id}"
          },
          "tier": "db-f1-micro",
          "user_labels": {
            "environment": "test"
          }
        }
      }
    },
    "google_sql_user": {
      "posts_cloud-sql_react-application-db-user-test-regression-test_80758EA7": {
        "instance": "${google_sql_database_instance.posts_cloud-sql_db-react-application-instance-test-regression-test_5482FDD0.id}",
        "name": "react-application-db-user-test-regression-test",
        "password": "${var.DB_PASS}",
        "project": "test"
      }
    },
    "google_storage_bucket": {
      "posts_cloud-function_cloud-functions-test-regression-test_1CDFFE1A": {
        "force_destroy": true,
        "location": "us-east1",
        "name": "cloud-functions-test-regression-test",
        "project": "test",
        "storage_class": "STANDARD"
      }
    },
    "google_storage_bucket_object": {
      "posts_cloud-function_functions-archive-test-regression-test_5F080BE5": {
        "bucket": "${google_storage_bucket.posts_cloud-function_cloud-functions-test-regression-test_1CDFFE1A.name}",
        "name": "functions-archive-test-regression-test",
        "source": "/Users/mark.decrane/cdktf-example-projects/cdktf-integration-serverless-python-gcp-example/./func_archive.zip"
      }
    },
    "google_vpc_access_connector": {
      "posts_cloud-function_msvmxw-tzag9-a9k2jl45f3s_F8049A5E": {
        "ip_cidr_range": "10.8.0.0/28",
        "name": "msvmxw-tzag9-a9k2jl45f3s",
        "network": "${google_compute_network.posts_vpc-test_193AFE9F.id}",
        "project": "test",
        "region": "us-east1"
      }
    }
  },
  "terraform": {
    "required_providers": {
      "google-beta": {
        "source": "google-beta",
        "version": "4.78.0"
      }
    }
  },
  "variable": {
    "DB_PASS": {
      "description": "DB password for the instance",
      "sensitive": true,
      "type": "string"
    }
  }
}'''
