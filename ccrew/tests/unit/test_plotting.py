from datetime import datetime, timedelta
from plotly.graph_objects import Figure, Scattermapbox
import pytest
from redis.commands.json.path import Path
from pytest_mock_resources import (
    create_redis_fixture,
    RedisConfig,
    create_postgres_fixture,
)
from ccrew.reporting import plotting
from ccrew.models import Base


redis = create_redis_fixture()
postgres = create_postgres_fixture(Base, session=True)


@pytest.fixture(scope="session")
def pmr_redis_config():
    return RedisConfig(image="redis/redis-stack")


def seed_mocked_redis(redis):
    boat_state_redis_entry = {
        "id": None,
        "server_timestamp": "2025-01-05T17:42:42.302549",
        "time_utc": "2025-01-05 16:42:42.096444364 +0000 UTC",
        "mmsi": 244650331,
        "ship_name": "TRADE NAVIGATOR",
        "cog": 56.8,
        "lat": 51.20706666666667,
        "lon": 1.9903333333333333,
        "msg_id": 1,
        "nav_status": 0,
        "pos_accuracy": True,
        "raim": False,
        "rate_of_turn": 12,
        "repeat_indicator": 0,
        "sog": 11.1,
        "spare": 0,
        "special_manoeuvre_indicator": 0,
        "time_stamp": 35,
        "true_heading": 61,
        "user_id": 244650331,
        "valid": True,
    }
    redis_key = f"state:BoatPositionReport:244650331-TRADE NAVIGATOR"
    redis.json().set(redis_key, Path.root_path(), boat_state_redis_entry)


def test_get_state_boat_position_reports_from_redis(redis):
    seed_mocked_redis(redis)
    plotting.redis_client = redis
    state = plotting.get_state_boat_position_reports()
    boat_state = state[0]
    print(state)
    assert boat_state["mmsi"] == 244650331


def test_to_default_dicts():
    dicts = [{"a": 1, "b": 3}, {"a": 1, "b": 2}]
    default_dicts = plotting.to_defaultdict(dicts)
    assert default_dicts == {"a": [1, 1], "b": [3, 2]}


def test_get_state_trace(redis):
    seed_mocked_redis(redis)
    plotting.redis_client = redis
    trace = plotting.get_state_trace()

    expected = Scattermapbox(
        {
            "lat": [51.20706666666667],
            "lon": [1.9903333333333333],
            "marker": {"size": 12},
            "mode": "markers+text",
            "name": "state_trace",
            "showlegend": False,
            "text": ["TRADE NAVIGATOR"],
            "textposition": "top right",
        }
    )
    assert trace == expected


def test_plot_state(redis):
    seed_mocked_redis(redis)
    plotting.redis_client = redis
    figure = plotting.plot_state()

    expected_data = (
        Scattermapbox(
            {
                "lat": [51.20706666666667],
                "lon": [1.9903333333333333],
                "marker": {"size": 12},
                "mode": "markers+text",
                "name": "state_trace",
                "showlegend": False,
                "text": ["TRADE NAVIGATOR"],
                "textposition": "top right",
            }
        ),
    )
    assert type(figure) == Figure
    assert figure["data"] == expected_data


def test_get_boat_tail_trace(postgres):
    print(type(postgres))
    # plotting.db = postgres
    tracked_boat = {"mmsi": 228070800, "ship_name": "F/V ARPEGE          "}
    # latest = datetime.strptime("2025-01-07 18:47:52.798473", "%Y-%m-%d %H:%M:%S")
    latest = datetime(year=2025, month=1, day=7, hour=18, minute=47, second=52)
    # boat_tail_trace = plotting.get_boat_tail_trace(tracked_boat)
    boat_tail_trace = plotting.get_boat_tail_data(tracked_boat, latest=latest)
    print(boat_tail_trace)
    assert False
