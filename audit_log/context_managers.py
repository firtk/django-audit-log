
def _is_creating_user_tracking_disabled(model_or_instance):
    return getattr(model_or_instance, '__creating_user_tracking_disabled_cnt', 0) == 0


def _is_last_user_tracking_disabled(model_or_instance):
    return getattr(model_or_instance, '__last_user_tracking_disabled_cnt', 0) == 0


def _incr_count(model_or_instance, field_name):
    count = getattr(model_or_instance, field_name, 0)
    setattr(model_or_instance, field_name, count + 1)


def _decr_count(model_or_instance, field_name):
    count = getattr(model_or_instance, field_name, 0)
    count -= 1 if count > 0 else 0
    setattr(model_or_instance, field_name, count)


def disable_creating_user_tracking(*model_or_instances):
    try:
        for model_or_instance in model_or_instances:
            _incr_count(model_or_instance, '__creating_user_tracking_disabled_cnt')
        yield
    finally:
        for model_or_instance in model_or_instances:
            _decr_count(model_or_instance, '__creating_user_tracking_disabled_cnt')


def disable_last_user_tracking(*model_or_instances):
    try:
        for model_or_instance in model_or_instances:
            _incr_count(model_or_instance, '__last_user_tracking_disabled_cnt')
        yield
    finally:
        for model_or_instance in model_or_instances:
            _decr_count(model_or_instance, '__last_user_tracking_disabled_cnt')


def disable_user_tracking(*model_or_instances):
    try:
        for model_or_instance in model_or_instances:
            _incr_count(model_or_instance, '__last_user_tracking_disabled_cnt')
            _incr_count(model_or_instance, '__creating_user_tracking_disabled_cnt')
        yield
    finally:
        for model_or_instance in model_or_instances:
            _decr_count(model_or_instance, '__creating_user_tracking_disabled_cnt')
            _decr_count(model_or_instance, '__last_user_tracking_disabled_cnt')
