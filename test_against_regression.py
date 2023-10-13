import json
import pytest
import snapshottest
from cdktf import Testing
from main import FrontendStack, PostsStack

def test_against_regression_frontend(snapshot):
    frontend_stack = FrontendStack(Testing.app(), "test-frontend",
        environment="test",
        user="regression-test", 
        project = "test",
        http_trigger_url= "N/A"
    )
    frontend_stack_synth = Testing.synth(frontend_stack)
    # remove version info from snapshot - tests will fail in CI when dependabot tries to upgrade any providers
    frontend_stack_synth_dict = json.loads(frontend_stack_synth)
    del frontend_stack_synth_dict["terraform"]
    snapshottest.assert_match_snapshot(json.dumps(frontend_stack_synth_dict))

def test_against_regression_posts(snapshot):
    posts_stack = PostsStack(Testing.app(), "test-posts",
        environment="test",
        user="regression-test", 
        project = "test"
    )
    posts_stack_synth = Testing.synth(posts_stack)
    # remove version info from snapshot - tests will fail in CI when dependabot tries to upgrade any providers
    posts_stack_synth_dict = json.loads(posts_stack_synth)
    del posts_stack_synth_dict["terraform"]
    snapshottest.assert_match_snapshot(json.dumps(posts_stack_synth_dict))