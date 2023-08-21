
from cdktf import Testing
from main import FrontendStack, PostsStack

frontend_stack = FrontendStack(Testing.app(), "test-frontend",
    environment="test",
    user="regression-test", 
    project = "test",
    http_trigger_url= "N/A"
)
frontend_stack_synth = Testing.synth(frontend_stack)
print("frontend_stack_synth")
print(frontend_stack_synth)

posts_stack = PostsStack(Testing.app(), "test-posts",
    environment="test",
    user="regression-test", 
    project = "test"
)
posts_stack_synth = Testing.synth(posts_stack)
print("posts_stack_synth")
print(posts_stack_synth)