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
    snapshottest.assert_match_snapshot(frontend_stack_synth)

def test_against_regression_posts(snapshot):
    posts_stack = PostsStack(Testing.app(), "test-posts",
        environment="test",
        user="regression-test", 
        project = "test"
    )
    posts_stack_synth = Testing.synth(posts_stack)
    snapshottest.assert_match_snapshot(posts_stack_synth)