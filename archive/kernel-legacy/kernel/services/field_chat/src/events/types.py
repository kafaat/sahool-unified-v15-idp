"""
Chat Event Type Constants
"""

# Thread lifecycle events
CHAT_THREAD_CREATED = "chat_thread_created"
CHAT_THREAD_ARCHIVED = "chat_thread_archived"

# Message events
CHAT_MESSAGE_SENT = "chat_message_sent"
CHAT_MESSAGE_EDITED = "chat_message_edited"
CHAT_MESSAGE_DELETED = "chat_message_deleted"

# Participant events
CHAT_PARTICIPANT_JOINED = "chat_participant_joined"
CHAT_PARTICIPANT_LEFT = "chat_participant_left"

# Read receipt events
CHAT_MESSAGES_READ = "chat_messages_read"

# Subject prefixes
SUBJECT_PREFIX = "chat"

# Subject patterns
SUBJECTS = {
    CHAT_THREAD_CREATED: f"{SUBJECT_PREFIX}.chat_thread_created",
    CHAT_THREAD_ARCHIVED: f"{SUBJECT_PREFIX}.chat_thread_archived",
    CHAT_MESSAGE_SENT: f"{SUBJECT_PREFIX}.chat_message_sent",
    CHAT_MESSAGE_EDITED: f"{SUBJECT_PREFIX}.chat_message_edited",
    CHAT_MESSAGE_DELETED: f"{SUBJECT_PREFIX}.chat_message_deleted",
    CHAT_PARTICIPANT_JOINED: f"{SUBJECT_PREFIX}.chat_participant_joined",
    CHAT_PARTICIPANT_LEFT: f"{SUBJECT_PREFIX}.chat_participant_left",
    CHAT_MESSAGES_READ: f"{SUBJECT_PREFIX}.chat_messages_read",
}
