# (C) Datadog, Inc. 2022-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import os

import pytest

from datadog_checks.aerospike import AerospikeCheck
from datadog_checks.dev.utils import get_metadata_metrics

from .common import (
    EXPECTED_PROMETHEUS_METRICS_6,
    EXPECTED_PROMETHEUS_METRICS_7,
    EXPECTED_PROMETHEUS_METRICS_LEGACY,
    HERE,
    PROMETHEUS_XDR_METRICS,
    VERSION,
)

pytestmark = [pytest.mark.unit]


def get_fixture_path(filename):
    return os.path.join(HERE, 'fixtures', filename)


def test_openmetricsv2_check(aggregator, dd_run_check, instance_openmetrics_v2, mock_http_response):
    version_parts = [int(p) for p in VERSION.split('.')]
    mock_http_response(file_path=get_fixture_path('prometheus.txt'))

    check = AerospikeCheck('aerospike', {}, [instance_openmetrics_v2])
    dd_run_check(check)

    all_metrics = PROMETHEUS_XDR_METRICS

    if version_parts >= [7]:
        all_metrics.extend(EXPECTED_PROMETHEUS_METRICS_7)
    elif version_parts >= [6, 1]:
        all_metrics.extend(EXPECTED_PROMETHEUS_METRICS_6)
    else:
        all_metrics.extend(EXPECTED_PROMETHEUS_METRICS_LEGACY)

    for metric_name in all_metrics:
        aggregator.assert_metric(metric_name)

        aggregator.assert_metric_has_tag(
            metric_name, 'endpoint:{}'.format(instance_openmetrics_v2.get('openmetrics_endpoint'))
        )
        aggregator.assert_metric_has_tag(metric_name, 'aerospike_cluster:null')
        aggregator.assert_metric_has_tag(metric_name, 'aerospike_service:192.168.32.3:3000')

    aggregator.assert_all_metrics_covered()
    aggregator.assert_metrics_using_metadata(get_metadata_metrics(), check_submission_type=True)
