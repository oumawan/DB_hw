from typing import List

VEHICLE_TYPES = [
    '大型客车',
    '重型牵引挂车',
    '城市公交车',
    '中型客车',
    '大型货车',
    '小型汽车',
    '小型自动挡汽车',
]

LICENSE_TYPES = ['A1', 'A2', 'A3', 'B1', 'B2', 'C1', 'C2']

_LICENSE_ALLOW = {
    'A1': [
        '大型客车',
        '城市公交车',
        '中型客车',
        '小型汽车',
        '小型自动挡汽车',
        '大型货车',
    ],
    'A2': [
        '重型牵引挂车',
        '大型货车',
        '中型客车',
        '小型汽车',
        '小型自动挡汽车',
    ],
    'A3': [
        '城市公交车',
        '小型汽车',
        '小型自动挡汽车',
    ],
    'B1': [
        '中型客车',
        '小型汽车',
        '小型自动挡汽车',
    ],
    'B2': [
        '大型货车',
        '小型汽车',
        '小型自动挡汽车',
    ],
    'C1': [
        '小型汽车',
        '小型自动挡汽车',
    ],
    'C2': [
        '小型自动挡汽车',
    ],
}




def can_drive(license_type: str, vehicle_type: str) -> bool:
    if license_type not in _LICENSE_ALLOW:
        raise ValueError(f'unknown license type: {license_type}')
    if vehicle_type not in VEHICLE_TYPES:
        raise ValueError(f'unknown vehicle type: {vehicle_type}')

    return vehicle_type in _LICENSE_ALLOW[license_type]


__all__ = [
    'can_drive',
]
