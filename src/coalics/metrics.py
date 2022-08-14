from prometheus_client import CollectorRegistry, Summary, Counter, Gauge

push_registry = CollectorRegistry()

update_duration = Summary(
    "coalics_update_duration",
    "Time taken to complete update job",
    registry=push_registry,
    unit="seconds",
)

update_source_count = Summary(
    "coalics_update_num_sources",
    "Number of source to be updated",
    registry=push_registry,
)

update_count = Counter(
    "coalics_update_num",
    "Number of updates",
    registry=push_registry,
)

update_error_counter = Counter(
    "coalics_update_num_errors",
    "Number of errors encountered during update",
    registry=push_registry,
)

update_success_time = Gauge(
    "coalics_update_success_unixtime",
    "Last time the update job succeeded",
    registry=push_registry,
)
