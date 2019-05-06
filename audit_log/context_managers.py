
def _is_creating_user_tracking_disabled(model_or_instance):
    return getattr(model_or_instance, '__is_creating_user_tracking_disabled', False)


def _is_last_user_tracking_disabled(model_or_instance):
    return getattr(model_or_instance, '__is_last_user_tracking_disabled', False)


def disable_creating_user_tracking(model_or_instance):
    try:
        setattr(model_or_instance, '__is_creating_user_tracking_disabled', True)
        yield
    finally:
        setattr(model_or_instance, '__is_creating_user_tracking_disabled', False)


def disable_last_user_tracking(model_or_instance):
    try:
        setattr(model_or_instance, '__is_last_user_tracking_disabled', True)
        yield
    finally:
        setattr(model_or_instance, '__is_last_user_tracking_disabled', False)


def disable_user_tracking(model_or_instance):
    try:
        setattr(model_or_instance, '__is_last_user_tracking_disabled', True)
        setattr(model_or_instance, '__is_creating_user_tracking_disabled', True)
        yield
    finally:
        setattr(model_or_instance, '__is_last_user_tracking_disabled', False)
        setattr(model_or_instance, '__is_creating_user_tracking_disabled', False)
