# constants/chat_constants.py

class ChatLimits:
    FREE_TIER_MESSAGE_LIMIT = 5
    PREMIUM_TIER_MESSAGE_LIMIT = 100  # For future use

class ErrorMessages:
    LIMIT_EXCEEDED = "You have reached the limit of {limit} messages in the free version. Please upgrade to continue."
    INVALID_SESSION = "Invalid session ID"

class ResponseMessages:
    REMAINING_MESSAGES = "{count} messages remaining in your free tier"