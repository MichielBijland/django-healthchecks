import json
from collections import OrderedDict

import pytest
import requests_mock
from django.http import Http404

from django_healthchecks import views


def check_int():
    return 2


def check_float():
    return 1.5


def test_index_view(rf, settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_true',
        'redis': 'django_healthchecks.contrib.check_dummy_false',
    }

    request = rf.get('/')
    view = views.HealthCheckView.as_view()
    result = view(request)

    data = json.loads(result.content.decode(result.charset))
    assert data == {
        'database': True,
        'redis': False,
    }
    assert result.has_header('Etag')

    request = rf.get('/', HTTP_IF_NONE_MATCH=result['ETag'])
    result = view(request)
    assert result.status_code == 304


def test_service_view_bool(rf, settings):
    settings.HEALTH_CHECKS = OrderedDict([
        ('redis', 'django_healthchecks.contrib.check_dummy_false'),
        ('database', 'django_healthchecks.contrib.check_dummy_true'),
    ])

    request = rf.get('/')
    view = views.HealthCheckServiceView.as_view()
    result = view(request, service='database')

    assert result.status_code == 200
    assert result.content == b'true'
    assert result.has_header('Etag')

    request = rf.get('/', HTTP_IF_NONE_MATCH=result['ETag'])
    result = view(request, service='database')
    assert result.status_code == 304


def test_service_view_bytes(rf, settings):
    # This tests the serilization contraints
    settings.HEALTH_CHECKS = OrderedDict([
        ('ip', 'django_healthchecks.contrib.check_remote_addr'),
    ])

    request = rf.get('/')
    view = views.HealthCheckServiceView.as_view()
    result = view(request, service='ip')

    assert result.status_code == 200
    assert result.content == b'127.0.0.1'
    assert result.has_header('Etag')

    request = rf.get('/', HTTP_IF_NONE_MATCH=result['ETag'])
    result = view(request, service='ip')
    assert result.status_code == 304


def test_service_view_int(rf, settings):
    # This tests the serilization contraints
    settings.HEALTH_CHECKS = OrderedDict([
        ('val', check_int),
    ])

    request = rf.get('/')
    view = views.HealthCheckServiceView.as_view()
    result = view(request, service='val')

    assert result.status_code == 200
    assert result['Content-Type'] == 'application/json'
    assert result.content == b'2'
    assert result.has_header('Etag')


def test_service_view_float(rf, settings):
    # This tests the serilization contraints
    settings.HEALTH_CHECKS = OrderedDict([
        ('val', check_float),
    ])

    request = rf.get('/')
    view = views.HealthCheckServiceView.as_view()
    result = view(request, service='val')

    assert result.status_code == 200
    assert result['Content-Type'] == 'application/json'
    assert result.content == b'1.5'
    assert result.has_header('Etag')


def test_service_view_remote(rf, settings):
    settings.HEALTH_CHECKS = {
        'remote_service': 'https://test.com/api/healthchecks/',
    }

    with requests_mock.Mocker() as mock:
        mock.get(
            'https://test.com/api/healthchecks/',
            json={"cache_default": True})

        request = rf.get('/')
        view = views.HealthCheckServiceView.as_view()
        result = view(request, service='remote_service')

    expected = {'cache_default': True}
    data = json.loads(result.content.decode(result.charset))

    assert result.status_code == 200
    assert result['Content-Type'] == 'application/json'
    assert data == expected
    assert result.has_header('Etag')


def test_service_view_err(rf, settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_false'
    }

    request = rf.get('/')
    view = views.HealthCheckServiceView.as_view()

    result = view(request, service='database')
    assert result.status_code == 200
    assert result.content == b'false'
    assert result.has_header('Etag')

    request = rf.get('/', HTTP_IF_NONE_MATCH=result['ETag'])
    result = view(request, service='database')
    assert result.status_code == 304


def test_service_view_err_custom_code(rf, settings):
    settings.HEALTH_CHECKS_ERROR_CODE = 500
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_false'
    }

    request = rf.get('/')
    view = views.HealthCheckServiceView.as_view()

    result = view(request, service='database')
    assert result.status_code == 500
    assert result.content == b'false'

    request = rf.get('/', HTTP_IF_NONE_MATCH=result['ETag'])
    result = view(request, service='database')
    assert result.status_code == 500


def test_service_view_404(rf):
    request = rf.get('/')
    view = views.HealthCheckServiceView.as_view()

    with pytest.raises(Http404):
        view(request, service='database')


def test_service_require_auth(rf, settings):
    settings.HEALTH_CHECKS = {
        'database': 'django_healthchecks.contrib.check_dummy_true'
    }
    settings.HEALTH_CHECKS_BASIC_AUTH = {
        '*': [('user', 'password')],
    }

    request = rf.get('/')
    view = views.HealthCheckServiceView.as_view()

    result = view(request, service='database')
    assert result.status_code == 401
    assert result.has_header('Etag')

    request = rf.get('/', HTTP_IF_NONE_MATCH=result['ETag'])
    result = view(request, service='database')
    assert result.status_code == 401
    assert result.has_header('Etag')

