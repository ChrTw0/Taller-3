"""GPS distance calculation utilities."""

import math
from typing import Tuple
from loguru import logger

class GPSCalculator:
    """GPS distance and validation utilities."""

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float, earth_radius_km: float = 6371.0) -> float:
        """
        Calculate the great circle distance between two points on Earth using Haversine formula.

        Args:
            lat1, lon1: Latitude and longitude of point 1 (in decimal degrees)
            lat2, lon2: Latitude and longitude of point 2 (in decimal degrees)
            earth_radius_km: Earth radius in kilometers (default: 6371.0)

        Returns:
            Distance in meters
        """
        # Convert decimal degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)

        c = 2 * math.asin(math.sqrt(a))

        # Distance in kilometers
        distance_km = earth_radius_km * c

        # Convert to meters
        distance_meters = distance_km * 1000

        logger.debug(f"Distance calculated: {distance_meters:.2f}m between ({lat1}, {lon1}) and ({lat2}, {lon2})")

        return distance_meters

    @staticmethod
    def is_within_range(
        user_lat: float,
        user_lon: float,
        target_lat: float,
        target_lon: float,
        max_distance_meters: float,
        earth_radius_km: float = 6371.0
    ) -> Tuple[bool, float]:
        """
        Check if user is within specified range of target location.

        Args:
            user_lat, user_lon: User's GPS coordinates
            target_lat, target_lon: Target location coordinates
            max_distance_meters: Maximum allowed distance in meters
            earth_radius_km: Earth radius in kilometers

        Returns:
            Tuple of (is_within_range: bool, actual_distance: float)
        """
        distance = GPSCalculator.haversine_distance(
            user_lat, user_lon, target_lat, target_lon, earth_radius_km
        )

        is_within = distance <= max_distance_meters

        logger.info(f"Proximity check: {distance:.2f}m <= {max_distance_meters}m = {is_within}")

        return is_within, distance

    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """
        Validate GPS coordinates are within valid ranges.

        Args:
            latitude: Latitude in decimal degrees (-90 to 90)
            longitude: Longitude in decimal degrees (-180 to 180)

        Returns:
            True if coordinates are valid
        """
        if not (-90 <= latitude <= 90):
            logger.warning(f"Invalid latitude: {latitude}")
            return False

        if not (-180 <= longitude <= 180):
            logger.warning(f"Invalid longitude: {longitude}")
            return False

        return True

    @staticmethod
    def validate_accuracy(accuracy: float, threshold: float = 10.0) -> bool:
        """
        Validate GPS accuracy is acceptable.

        Args:
            accuracy: GPS accuracy in meters
            threshold: Maximum acceptable accuracy in meters

        Returns:
            True if accuracy is acceptable
        """
        is_valid = accuracy <= threshold

        if not is_valid:
            logger.warning(f"GPS accuracy too low: {accuracy}m > {threshold}m")

        return is_valid

    @staticmethod
    def find_nearest_classroom(
        user_lat: float,
        user_lon: float,
        classrooms: list,
        earth_radius_km: float = 6371.0
    ) -> Tuple[dict, float]:
        """
        Find the nearest classroom to user's location.

        Args:
            user_lat, user_lon: User's GPS coordinates
            classrooms: List of classroom dicts with 'latitude' and 'longitude'
            earth_radius_km: Earth radius in kilometers

        Returns:
            Tuple of (nearest_classroom: dict, distance: float)
        """
        if not classrooms:
            raise ValueError("No classrooms provided")

        nearest_classroom = None
        min_distance = float('inf')

        for classroom in classrooms:
            distance = GPSCalculator.haversine_distance(
                user_lat, user_lon,
                float(classroom['latitude']), float(classroom['longitude']),
                earth_radius_km
            )

            if distance < min_distance:
                min_distance = distance
                nearest_classroom = classroom

        logger.info(f"Nearest classroom: {nearest_classroom.get('room_number', 'Unknown')} at {min_distance:.2f}m")

        return nearest_classroom, min_distance