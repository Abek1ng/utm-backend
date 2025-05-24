# app/services/nfz_service.py
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.crud import restricted_zone as crud_restricted_zone
from app.schemas.waypoint import WaypointCreate

class NFZService:
    def check_flight_plan_against_nfzs(self, db: Session, waypoints: List[WaypointCreate]) -> List[str]:
        """
        Check if flight plan waypoints intersect with No-Fly Zones.
        Returns list of NFZ names that are violated.
        """
        # For MVP, this is a placeholder implementation
        # In a real system, you'd check waypoint coordinates against NFZ geometries
        
        # Get all active NFZs
        active_nfzs = crud_restricted_zone.restricted_zone.get_all_active_zones(db)
        
        violations = []
        
        # Placeholder logic - you'd implement proper geometric intersection here
        for waypoint in waypoints:
            for nfz in active_nfzs:
                # Simple placeholder check - in reality you'd use proper geometry libraries
                # like Shapely to check if point is inside polygon/circle
                if self._simple_point_in_nfz_check(waypoint, nfz):
                    violations.append(nfz.name)
        
        return list(set(violations))  # Remove duplicates
    
    def check_point_against_nfzs(self, db: Session, lat: float, lon: float, alt: float) -> List[Dict[str, Any]]:
        """
        Check if a single point intersects with No-Fly Zones.
        Returns list of NFZ details that are breached.
        """
        active_nfzs = crud_restricted_zone.restricted_zone.get_all_active_zones(db)
        
        breaches = []
        for nfz in active_nfzs:
            if self._point_in_nfz(lat, lon, alt, nfz):
                breaches.append({
                    'name': nfz.name,
                    'id': nfz.id,
                    'description': nfz.description
                })
        
        return breaches
    
    def _simple_point_in_nfz_check(self, waypoint: WaypointCreate, nfz) -> bool:
        """
        Placeholder for geometric intersection check.
        In a real implementation, you'd use proper geometric calculations.
        """
        # This is a very basic placeholder - always returns False for now
        # Real implementation would:
        # 1. Parse nfz.definition_json based on nfz.geometry_type
        # 2. Use geometric libraries to check intersection
        # 3. Consider altitude constraints (min_altitude_m, max_altitude_m)
        return False
    
    def _point_in_nfz(self, lat: float, lon: float, alt: float, nfz) -> bool:
        """
        Check if a point is inside an NFZ.
        Placeholder implementation.
        """
        # Check altitude constraints first
        if nfz.min_altitude_m is not None and alt < nfz.min_altitude_m:
            return False
        if nfz.max_altitude_m is not None and alt > nfz.max_altitude_m:
            return False
        
        # Placeholder for geometric check
        # Real implementation would check if lat/lon is inside the NFZ geometry
        return False

nfz_service = NFZService()