import os

app_token = os.environ.get("APP_TOKEN", "4c6d8d6e4c6d8d6e4c6d8d6e054c02301244c6d4c6d8d6e1224aadc8ad37bd1098d8a3f")
comunity_token = os.environ.get("COMUNITY_TOKEN", "1d05d5656b70b874e93a44b5821a378e12c48f7f249d5cdf10f81e0ca970394f144209f39480ccb02cc09")
screen_name = os.environ.get("SCREEN_NAME", "public193519310")
vk_api_version = os.environ.get("VK_API_VERSION", 5.103)
host = os.environ.get("API_HOST", "0.0.0.0")
port = os.environ.get("API_PORT", 8080)
collector_period = os.environ.get("COLLECTOR_PERIOD", 60)
init_posts_num = os.environ.get("INIT_POSTS_NUM", 100)
watch_posts_num = os.environ.get("WATCH_POSTS_NUM", 2)
