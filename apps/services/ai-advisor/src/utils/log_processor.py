"""
Structlog Processor for PII Masking
معالج Structlog لإخفاء المعلومات الشخصية
"""

from typing import Any

from .pii_masker import PIIMasker


def pii_masking_processor(logger, method_name, event_dict: dict[str, Any]) -> dict[str, Any]:
    """
    Structlog processor that masks PII in all log events
    معالج Structlog يخفي المعلومات الشخصية في جميع أحداث السجل

    This processor should be added to structlog.configure() processors list
    before the final renderer (e.g., JSONRenderer).

    Args:
        logger: The logger instance
        method_name: The name of the log method being called
        event_dict: The event dictionary containing log data

    Returns:
        The event dictionary with PII masked
    """
    # Mask the main event message if it's a string
    if 'event' in event_dict and isinstance(event_dict['event'], str):
        event_dict['event'] = PIIMasker.mask_text(event_dict['event'])

    # Mask all other fields in the event dictionary
    masked_dict = {}
    for key, value in event_dict.items():
        if key == 'event':
            # Already masked above
            masked_dict[key] = event_dict[key]
        elif isinstance(value, str):
            masked_dict[key] = PIIMasker.mask_text(value)
        elif isinstance(value, dict):
            masked_dict[key] = PIIMasker.mask_dict(value)
        elif isinstance(value, list):
            masked_dict[key] = [
                PIIMasker.mask_dict(item) if isinstance(item, dict)
                else PIIMasker.mask_text(item) if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            masked_dict[key] = value

    return masked_dict
