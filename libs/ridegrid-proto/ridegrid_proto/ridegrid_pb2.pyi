from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RideType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RIDE_TYPE_UNSPECIFIED: _ClassVar[RideType]
    RIDE_TYPE_ECONOMY: _ClassVar[RideType]
    RIDE_TYPE_PREMIUM: _ClassVar[RideType]
    RIDE_TYPE_LUXURY: _ClassVar[RideType]
    RIDE_TYPE_SHARED: _ClassVar[RideType]

class DriverStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DRIVER_STATUS_UNSPECIFIED: _ClassVar[DriverStatus]
    DRIVER_STATUS_OFFLINE: _ClassVar[DriverStatus]
    DRIVER_STATUS_IDLE: _ClassVar[DriverStatus]
    DRIVER_STATUS_ASSIGNED: _ClassVar[DriverStatus]
    DRIVER_STATUS_EN_ROUTE: _ClassVar[DriverStatus]
    DRIVER_STATUS_ARRIVED: _ClassVar[DriverStatus]
    DRIVER_STATUS_IN_RIDE: _ClassVar[DriverStatus]
    DRIVER_STATUS_COMPLETED: _ClassVar[DriverStatus]

class RideStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RIDE_STATUS_UNSPECIFIED: _ClassVar[RideStatus]
    RIDE_STATUS_REQUESTED: _ClassVar[RideStatus]
    RIDE_STATUS_DRIVER_ASSIGNED: _ClassVar[RideStatus]
    RIDE_STATUS_DRIVER_EN_ROUTE: _ClassVar[RideStatus]
    RIDE_STATUS_DRIVER_ARRIVED: _ClassVar[RideStatus]
    RIDE_STATUS_IN_PROGRESS: _ClassVar[RideStatus]
    RIDE_STATUS_COMPLETED: _ClassVar[RideStatus]
    RIDE_STATUS_CANCELLED: _ClassVar[RideStatus]

class RideEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RIDE_EVENT_TYPE_UNSPECIFIED: _ClassVar[RideEventType]
    RIDE_EVENT_TYPE_REQUESTED: _ClassVar[RideEventType]
    RIDE_EVENT_TYPE_DRIVER_ASSIGNED: _ClassVar[RideEventType]
    RIDE_EVENT_TYPE_DRIVER_EN_ROUTE: _ClassVar[RideEventType]
    RIDE_EVENT_TYPE_DRIVER_ARRIVED: _ClassVar[RideEventType]
    RIDE_EVENT_TYPE_RIDE_STARTED: _ClassVar[RideEventType]
    RIDE_EVENT_TYPE_RIDE_COMPLETED: _ClassVar[RideEventType]
    RIDE_EVENT_TYPE_RIDE_CANCELLED: _ClassVar[RideEventType]
    RIDE_EVENT_TYPE_DRIVER_ACCEPTED: _ClassVar[RideEventType]
    RIDE_EVENT_TYPE_DRIVER_DECLINED: _ClassVar[RideEventType]
RIDE_TYPE_UNSPECIFIED: RideType
RIDE_TYPE_ECONOMY: RideType
RIDE_TYPE_PREMIUM: RideType
RIDE_TYPE_LUXURY: RideType
RIDE_TYPE_SHARED: RideType
DRIVER_STATUS_UNSPECIFIED: DriverStatus
DRIVER_STATUS_OFFLINE: DriverStatus
DRIVER_STATUS_IDLE: DriverStatus
DRIVER_STATUS_ASSIGNED: DriverStatus
DRIVER_STATUS_EN_ROUTE: DriverStatus
DRIVER_STATUS_ARRIVED: DriverStatus
DRIVER_STATUS_IN_RIDE: DriverStatus
DRIVER_STATUS_COMPLETED: DriverStatus
RIDE_STATUS_UNSPECIFIED: RideStatus
RIDE_STATUS_REQUESTED: RideStatus
RIDE_STATUS_DRIVER_ASSIGNED: RideStatus
RIDE_STATUS_DRIVER_EN_ROUTE: RideStatus
RIDE_STATUS_DRIVER_ARRIVED: RideStatus
RIDE_STATUS_IN_PROGRESS: RideStatus
RIDE_STATUS_COMPLETED: RideStatus
RIDE_STATUS_CANCELLED: RideStatus
RIDE_EVENT_TYPE_UNSPECIFIED: RideEventType
RIDE_EVENT_TYPE_REQUESTED: RideEventType
RIDE_EVENT_TYPE_DRIVER_ASSIGNED: RideEventType
RIDE_EVENT_TYPE_DRIVER_EN_ROUTE: RideEventType
RIDE_EVENT_TYPE_DRIVER_ARRIVED: RideEventType
RIDE_EVENT_TYPE_RIDE_STARTED: RideEventType
RIDE_EVENT_TYPE_RIDE_COMPLETED: RideEventType
RIDE_EVENT_TYPE_RIDE_CANCELLED: RideEventType
RIDE_EVENT_TYPE_DRIVER_ACCEPTED: RideEventType
RIDE_EVENT_TYPE_DRIVER_DECLINED: RideEventType

class Location(_message.Message):
    __slots__ = ("latitude", "longitude")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float
    def __init__(self, latitude: _Optional[float] = ..., longitude: _Optional[float] = ...) -> None: ...

class Timestamp(_message.Message):
    __slots__ = ("seconds", "nanos")
    SECONDS_FIELD_NUMBER: _ClassVar[int]
    NANOS_FIELD_NUMBER: _ClassVar[int]
    seconds: int
    nanos: int
    def __init__(self, seconds: _Optional[int] = ..., nanos: _Optional[int] = ...) -> None: ...

class Rider(_message.Message):
    __slots__ = ("rider_id", "location", "name", "phone")
    RIDER_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    rider_id: str
    location: Location
    name: str
    phone: str
    def __init__(self, rider_id: _Optional[str] = ..., location: _Optional[_Union[Location, _Mapping]] = ..., name: _Optional[str] = ..., phone: _Optional[str] = ...) -> None: ...

class RideRequest(_message.Message):
    __slots__ = ("ride_id", "rider_id", "origin", "destination", "ride_type", "passenger_count", "payment_method_id", "requested_at", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    RIDER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    RIDE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PASSENGER_COUNT_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_METHOD_ID_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ride_id: str
    rider_id: str
    origin: Location
    destination: Location
    ride_type: RideType
    passenger_count: int
    payment_method_id: str
    requested_at: Timestamp
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, ride_id: _Optional[str] = ..., rider_id: _Optional[str] = ..., origin: _Optional[_Union[Location, _Mapping]] = ..., destination: _Optional[_Union[Location, _Mapping]] = ..., ride_type: _Optional[_Union[RideType, str]] = ..., passenger_count: _Optional[int] = ..., payment_method_id: _Optional[str] = ..., requested_at: _Optional[_Union[Timestamp, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Driver(_message.Message):
    __slots__ = ("driver_id", "name", "phone", "vehicle_make", "vehicle_model", "vehicle_color", "license_plate", "status", "location", "heading", "speed_kmh", "last_seen", "capacity", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_MAKE_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_MODEL_FIELD_NUMBER: _ClassVar[int]
    VEHICLE_COLOR_FIELD_NUMBER: _ClassVar[int]
    LICENSE_PLATE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    HEADING_FIELD_NUMBER: _ClassVar[int]
    SPEED_KMH_FIELD_NUMBER: _ClassVar[int]
    LAST_SEEN_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    driver_id: str
    name: str
    phone: str
    vehicle_make: str
    vehicle_model: str
    vehicle_color: str
    license_plate: str
    status: DriverStatus
    location: Location
    heading: float
    speed_kmh: float
    last_seen: Timestamp
    capacity: int
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, driver_id: _Optional[str] = ..., name: _Optional[str] = ..., phone: _Optional[str] = ..., vehicle_make: _Optional[str] = ..., vehicle_model: _Optional[str] = ..., vehicle_color: _Optional[str] = ..., license_plate: _Optional[str] = ..., status: _Optional[_Union[DriverStatus, str]] = ..., location: _Optional[_Union[Location, _Mapping]] = ..., heading: _Optional[float] = ..., speed_kmh: _Optional[float] = ..., last_seen: _Optional[_Union[Timestamp, _Mapping]] = ..., capacity: _Optional[int] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class DriverTelemetry(_message.Message):
    __slots__ = ("driver_id", "location", "heading", "speed_kmh", "status", "timestamp", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    HEADING_FIELD_NUMBER: _ClassVar[int]
    SPEED_KMH_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    driver_id: str
    location: Location
    heading: float
    speed_kmh: float
    status: DriverStatus
    timestamp: Timestamp
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, driver_id: _Optional[str] = ..., location: _Optional[_Union[Location, _Mapping]] = ..., heading: _Optional[float] = ..., speed_kmh: _Optional[float] = ..., status: _Optional[_Union[DriverStatus, str]] = ..., timestamp: _Optional[_Union[Timestamp, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Ride(_message.Message):
    __slots__ = ("ride_id", "rider_id", "driver_id", "origin", "destination", "ride_type", "status", "surge_multiplier", "estimated_fare", "eta_seconds", "created_at", "updated_at", "driver_assigned_at", "driver_arrived_at", "ride_started_at", "ride_completed_at", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    RIDER_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    RIDE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SURGE_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_FARE_FIELD_NUMBER: _ClassVar[int]
    ETA_SECONDS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    DRIVER_ASSIGNED_AT_FIELD_NUMBER: _ClassVar[int]
    DRIVER_ARRIVED_AT_FIELD_NUMBER: _ClassVar[int]
    RIDE_STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    RIDE_COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ride_id: str
    rider_id: str
    driver_id: str
    origin: Location
    destination: Location
    ride_type: RideType
    status: RideStatus
    surge_multiplier: float
    estimated_fare: str
    eta_seconds: int
    created_at: Timestamp
    updated_at: Timestamp
    driver_assigned_at: Timestamp
    driver_arrived_at: Timestamp
    ride_started_at: Timestamp
    ride_completed_at: Timestamp
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, ride_id: _Optional[str] = ..., rider_id: _Optional[str] = ..., driver_id: _Optional[str] = ..., origin: _Optional[_Union[Location, _Mapping]] = ..., destination: _Optional[_Union[Location, _Mapping]] = ..., ride_type: _Optional[_Union[RideType, str]] = ..., status: _Optional[_Union[RideStatus, str]] = ..., surge_multiplier: _Optional[float] = ..., estimated_fare: _Optional[str] = ..., eta_seconds: _Optional[int] = ..., created_at: _Optional[_Union[Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[Timestamp, _Mapping]] = ..., driver_assigned_at: _Optional[_Union[Timestamp, _Mapping]] = ..., driver_arrived_at: _Optional[_Union[Timestamp, _Mapping]] = ..., ride_started_at: _Optional[_Union[Timestamp, _Mapping]] = ..., ride_completed_at: _Optional[_Union[Timestamp, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CandidateMatch(_message.Message):
    __slots__ = ("ride_id", "driver_id", "eta_seconds", "distance_km", "surge_multiplier", "estimated_fare", "rank", "matched_at", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    ETA_SECONDS_FIELD_NUMBER: _ClassVar[int]
    DISTANCE_KM_FIELD_NUMBER: _ClassVar[int]
    SURGE_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_FARE_FIELD_NUMBER: _ClassVar[int]
    RANK_FIELD_NUMBER: _ClassVar[int]
    MATCHED_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ride_id: str
    driver_id: str
    eta_seconds: int
    distance_km: float
    surge_multiplier: float
    estimated_fare: str
    rank: int
    matched_at: Timestamp
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, ride_id: _Optional[str] = ..., driver_id: _Optional[str] = ..., eta_seconds: _Optional[int] = ..., distance_km: _Optional[float] = ..., surge_multiplier: _Optional[float] = ..., estimated_fare: _Optional[str] = ..., rank: _Optional[int] = ..., matched_at: _Optional[_Union[Timestamp, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Assignment(_message.Message):
    __slots__ = ("ride_id", "driver_id", "eta_seconds", "surge_multiplier", "estimated_fare", "accepted", "assigned_at", "accepted_at", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    ETA_SECONDS_FIELD_NUMBER: _ClassVar[int]
    SURGE_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    ESTIMATED_FARE_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    ASSIGNED_AT_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_AT_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ride_id: str
    driver_id: str
    eta_seconds: int
    surge_multiplier: float
    estimated_fare: str
    accepted: bool
    assigned_at: Timestamp
    accepted_at: Timestamp
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, ride_id: _Optional[str] = ..., driver_id: _Optional[str] = ..., eta_seconds: _Optional[int] = ..., surge_multiplier: _Optional[float] = ..., estimated_fare: _Optional[str] = ..., accepted: bool = ..., assigned_at: _Optional[_Union[Timestamp, _Mapping]] = ..., accepted_at: _Optional[_Union[Timestamp, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RideEvent(_message.Message):
    __slots__ = ("ride_id", "event_type", "payload", "timestamp", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    ride_id: str
    event_type: RideEventType
    payload: str
    timestamp: Timestamp
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, ride_id: _Optional[str] = ..., event_type: _Optional[_Union[RideEventType, str]] = ..., payload: _Optional[str] = ..., timestamp: _Optional[_Union[Timestamp, _Mapping]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CancelRideRequest(_message.Message):
    __slots__ = ("ride_id", "reason")
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    ride_id: str
    reason: str
    def __init__(self, ride_id: _Optional[str] = ..., reason: _Optional[str] = ...) -> None: ...

class GetRideRequest(_message.Message):
    __slots__ = ("ride_id",)
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    ride_id: str
    def __init__(self, ride_id: _Optional[str] = ...) -> None: ...

class GetRiderRidesRequest(_message.Message):
    __slots__ = ("rider_id", "limit", "offset")
    RIDER_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    rider_id: str
    limit: int
    offset: int
    def __init__(self, rider_id: _Optional[str] = ..., limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class GetRiderRidesResponse(_message.Message):
    __slots__ = ("rides", "total")
    RIDES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    rides: _containers.RepeatedCompositeFieldContainer[Ride]
    total: int
    def __init__(self, rides: _Optional[_Iterable[_Union[Ride, _Mapping]]] = ..., total: _Optional[int] = ...) -> None: ...

class UpdateDriverStatusRequest(_message.Message):
    __slots__ = ("driver_id", "status", "location")
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    driver_id: str
    status: DriverStatus
    location: Location
    def __init__(self, driver_id: _Optional[str] = ..., status: _Optional[_Union[DriverStatus, str]] = ..., location: _Optional[_Union[Location, _Mapping]] = ...) -> None: ...

class GetDriverStatusRequest(_message.Message):
    __slots__ = ("driver_id",)
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    driver_id: str
    def __init__(self, driver_id: _Optional[str] = ...) -> None: ...

class GetDriverLocationRequest(_message.Message):
    __slots__ = ("driver_id",)
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    driver_id: str
    def __init__(self, driver_id: _Optional[str] = ...) -> None: ...

class StreamTelemetryResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class FindMatchesResponse(_message.Message):
    __slots__ = ("matches",)
    MATCHES_FIELD_NUMBER: _ClassVar[int]
    matches: _containers.RepeatedCompositeFieldContainer[CandidateMatch]
    def __init__(self, matches: _Optional[_Iterable[_Union[CandidateMatch, _Mapping]]] = ...) -> None: ...

class UpdateDriverLocationResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class ProcessCandidateMatchesResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class DriverResponse(_message.Message):
    __slots__ = ("ride_id", "driver_id", "accepted", "responded_at")
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    RESPONDED_AT_FIELD_NUMBER: _ClassVar[int]
    ride_id: str
    driver_id: str
    accepted: bool
    responded_at: Timestamp
    def __init__(self, ride_id: _Optional[str] = ..., driver_id: _Optional[str] = ..., accepted: bool = ..., responded_at: _Optional[_Union[Timestamp, _Mapping]] = ...) -> None: ...

class HandleDriverResponseResponse(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...

class GetRiderRequest(_message.Message):
    __slots__ = ("rider_id",)
    RIDER_ID_FIELD_NUMBER: _ClassVar[int]
    rider_id: str
    def __init__(self, rider_id: _Optional[str] = ...) -> None: ...

class GetRiderStateResponse(_message.Message):
    __slots__ = ("rider", "active_rides")
    RIDER_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_RIDES_FIELD_NUMBER: _ClassVar[int]
    rider: Rider
    active_rides: _containers.RepeatedCompositeFieldContainer[Ride]
    def __init__(self, rider: _Optional[_Union[Rider, _Mapping]] = ..., active_rides: _Optional[_Iterable[_Union[Ride, _Mapping]]] = ...) -> None: ...

class GetDriverRequest(_message.Message):
    __slots__ = ("driver_id",)
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    driver_id: str
    def __init__(self, driver_id: _Optional[str] = ...) -> None: ...

class GetDriverStateResponse(_message.Message):
    __slots__ = ("driver", "active_assignments")
    DRIVER_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    driver: Driver
    active_assignments: _containers.RepeatedCompositeFieldContainer[Assignment]
    def __init__(self, driver: _Optional[_Union[Driver, _Mapping]] = ..., active_assignments: _Optional[_Iterable[_Union[Assignment, _Mapping]]] = ...) -> None: ...

class StreamRideUpdatesRequest(_message.Message):
    __slots__ = ("ride_id", "rider_id")
    RIDE_ID_FIELD_NUMBER: _ClassVar[int]
    RIDER_ID_FIELD_NUMBER: _ClassVar[int]
    ride_id: str
    rider_id: str
    def __init__(self, ride_id: _Optional[str] = ..., rider_id: _Optional[str] = ...) -> None: ...

class StreamDriverUpdatesRequest(_message.Message):
    __slots__ = ("driver_id",)
    DRIVER_ID_FIELD_NUMBER: _ClassVar[int]
    driver_id: str
    def __init__(self, driver_id: _Optional[str] = ...) -> None: ...
