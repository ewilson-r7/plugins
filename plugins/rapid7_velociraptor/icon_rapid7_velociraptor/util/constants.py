TIMEOUT = 60

BASE_URL_TEMPLATE = "https://{region}.api.insight.rapid7.com/insight-velociraptor/v1/orgs/{org_id}"

HTTP_ERROR_MAP = {
    400: {"cause": "Bad request", "assistance": "Verify the inputs are correct."},
    401: {"cause": "Unauthorized", "assistance": "Verify the API key is valid and active."},
    403: {"cause": "Insufficient permissions", "assistance": "Verify the API key has the required permissions."},
    404: {"cause": "Resource not found", "assistance": "Verify the ID or resource name is correct."},
    429: {"cause": "Rate limit exceeded", "assistance": "Too many requests. Wait and try again."},
    500: {
        "cause": "Internal server error",
        "assistance": "The Velociraptor service encountered an error. Try again later.",
    },
    503: {
        "cause": "Service unavailable",
        "assistance": "The Velociraptor service is temporarily unavailable. Try again later.",
    },
}
