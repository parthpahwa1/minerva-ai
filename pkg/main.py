import os
from game_sdk.hosted_game.agent import Agent, Function, FunctionArgument, FunctionConfig
from pkg.services.twitter_plugin import TwitterPlugin

agent = Agent(
    api_key=os.environ.get("VIRTUALS_API_KEY"),
    goal="search for best songs",
    description="Test Description",
    world_info="Test World Info",
)

# applicable only for platform twitter
agent.list_available_default_twitter_functions()
agent.use_default_twitter_functions(["wait", "reply_tweet"])

# adding custom functions only for platform twitter
agent.add_custom_function(
    Function(
        fn_name="custom_search_internet",
        fn_description="search the internet for the best songs",
        args=[
            FunctionArgument(
                name="query", type="string", description="The query to search for"
            )
        ],
        config=FunctionConfig(
            method="get",
            url="https://google.com",
            # specify which platform this function is for, in this case this function is for twitter only
            platform="twitter",
            success_feedback="I found the best songs",
            error_feedback="I couldn't find the best songs",
        ),
    )
)

# Define your options with the necessary credentials
options = {
    "id": "test_twitter_worker",
    "name": "Test Twitter Worker",
    "description": "An example Twitter Plugin for testing.",
    "credentials": {
        "apiKey": os.environ.get("TWITTER_API_KEY"),
        "apiSecretKey": os.environ.get("TWITTER_API_SECRET_KEY"),
        "accessToken": os.environ.get("TWITTER_ACCESS_TOKEN"),
        "accessTokenSecret": os.environ.get("TWITTER_ACCESS_TOKEN_SECRET"),
    },
}

# Initialize the TwitterPlugin with your options
twitter_plugin = TwitterPlugin(options)

print("Running Test Case 1: Post a Tweet")
post_tweet_fn = twitter_plugin.get_function("reply_tweet_long")
post_tweet_fn(tweet_id=123, reply_list=["Hello, world!", "This is a test tweet."])
print("Posted tweet!")
