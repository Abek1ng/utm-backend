#!/usr/bin/env python3
"""
Comprehensive Database Test Suite for UTM Backend

This script tests all database operations, relationships, and business logic
at full scale, then cleans up all test data.

Run with: python test_database_full.py
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import SessionLocal
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.drone import Drone, DroneOwnerType, DroneStatus
from app.models.flight_plan import FlightPlan, FlightPlanStatus
from app.models.waypoint import Waypoint
from app.models.telemetry_log import TelemetryLog
from app.models.restricted_zone import RestrictedZone, NFZGeometryType
from app.models.user_drone_assignment import UserDroneAssignment
from app.crud import user as crud_user
from app.crud import organization as crud_organization
from app.crud import drone as crud_drone
from app.crud import flight_plan as crud_flight_plan
from app.schemas.user import UserCreate
from app.schemas.organization import OrganizationCreate
from app.schemas.drone import DroneCreate
from app.schemas.flight_plan import FlightPlanCreate
from app.schemas.waypoint import WaypointCreate
from app.schemas.telemetry import TelemetryLogCreate
from app.schemas.restricted_zone import RestrictedZoneCreate
from app.core.security import get_password_hash


class DatabaseTestSuite:
    def __init__(self):
        self.db = SessionLocal()
        self.test_data_ids = {
            'users': [],
            'organizations': [],
            'drones': [],
            'flight_plans': [],
            'waypoints': [],
            'telemetry_logs': [],
            'restricted_zones': [],
            'user_drone_assignments': []
        }
        print(f"🔗 Connected to database: {settings.DATABASE_URL}")

    def log_test(self, test_name: str, status: str = "RUNNING"):
        """Log test progress"""
        symbols = {"RUNNING": "⏳", "PASS": "✅", "FAIL": "❌", "INFO": "ℹ️"}
        print(f"{symbols.get(status, '📝')} {test_name}")

    def create_test_data(self):
        """Create comprehensive test data"""
        self.log_test("Creating comprehensive test data", "RUNNING")
        
        try:
            # 1. Create Authority Admin
            authority_admin = User(
                full_name="Test Authority Admin",
                email="authority@test.com",
                phone_number="+77012345001",
                iin="123456789001",
                hashed_password=get_password_hash("testpass123"),
                role=UserRole.AUTHORITY_ADMIN,
                is_active=True
            )
            self.db.add(authority_admin)
            self.db.flush()
            self.test_data_ids['users'].append(authority_admin.id)

            # 2. Create Organizations
            organizations = []
            for i in range(3):
                org = Organization(
                    name=f"Test Organization {i+1}",
                    bin=f"12345678901{i}",
                    company_address=f"Test Address {i+1}",
                    city=f"Test City {i+1}",
                    is_active=True
                )
                self.db.add(org)
                self.db.flush()
                organizations.append(org)
                self.test_data_ids['organizations'].append(org.id)

            # 3. Create Organization Admins
            org_admins = []
            for i, org in enumerate(organizations):
                admin = User(
                    full_name=f"Org Admin {i+1}",
                    email=f"org_admin_{i+1}@test.com",
                    phone_number=f"+7701234500{i+2}",
                    iin=f"12345678900{i+2}",
                    hashed_password=get_password_hash("testpass123"),
                    role=UserRole.ORGANIZATION_ADMIN,
                    organization_id=org.id,
                    is_active=True
                )
                self.db.add(admin)
                self.db.flush()
                org_admins.append(admin)
                self.test_data_ids['users'].append(admin.id)
                
                # Link admin to organization
                org.admin_id = admin.id
                self.db.add(org)

            # 4. Create Organization Pilots
            org_pilots = []
            for i, org in enumerate(organizations):
                for j in range(2):  # 2 pilots per organization
                    pilot = User(
                        full_name=f"Org Pilot {i+1}-{j+1}",
                        email=f"org_pilot_{i+1}_{j+1}@test.com",
                        phone_number=f"+770123451{i}{j}",
                        iin=f"1234567891{i}{j}",
                        hashed_password=get_password_hash("testpass123"),
                        role=UserRole.ORGANIZATION_PILOT,
                        organization_id=org.id,
                        is_active=True
                    )
                    self.db.add(pilot)
                    self.db.flush()
                    org_pilots.append(pilot)
                    self.test_data_ids['users'].append(pilot.id)

            # 5. Create Solo Pilots
            solo_pilots = []
            for i in range(5):
                pilot = User(
                    full_name=f"Solo Pilot {i+1}",
                    email=f"solo_pilot_{i+1}@test.com",
                    phone_number=f"+7701234520{i}",
                    iin=f"12345678920{i}",
                    hashed_password=get_password_hash("testpass123"),
                    role=UserRole.SOLO_PILOT,
                    is_active=True
                )
                self.db.add(pilot)
                self.db.flush()
                solo_pilots.append(pilot)
                self.test_data_ids['users'].append(pilot.id)

            # 6. Create Drones
            drones = []
            
            # Organization drones
            for i, org in enumerate(organizations):
                for j in range(3):  # 3 drones per organization
                    drone = Drone(
                        brand=f"DJI",
                        model=f"Phantom {i+1}{j+1}",
                        serial_number=f"ORG{i+1}_DRONE_{j+1}_SN{i:03d}{j:03d}",
                        owner_type=DroneOwnerType.ORGANIZATION,
                        organization_id=org.id,
                        current_status=DroneStatus.IDLE
                    )
                    self.db.add(drone)
                    self.db.flush()
                    drones.append(drone)
                    self.test_data_ids['drones'].append(drone.id)

            # Solo pilot drones
            for i, pilot in enumerate(solo_pilots):
                for j in range(2):  # 2 drones per solo pilot
                    drone = Drone(
                        brand="Autel",
                        model=f"EVO {i+1}{j+1}",
                        serial_number=f"SOLO{i+1}_DRONE_{j+1}_SN{i:03d}{j:03d}",
                        owner_type=DroneOwnerType.SOLO_PILOT,
                        solo_owner_user_id=pilot.id,
                        current_status=DroneStatus.IDLE
                    )
                    self.db.add(drone)
                    self.db.flush()
                    drones.append(drone)
                    self.test_data_ids['drones'].append(drone.id)

            # 7. Create User-Drone Assignments
            org_drones = [d for d in drones if d.owner_type == DroneOwnerType.ORGANIZATION]
            for i, pilot in enumerate(org_pilots):
                # Assign 2 drones to each org pilot
                org_id = pilot.organization_id
                available_drones = [d for d in org_drones if d.organization_id == org_id]
                for j in range(min(2, len(available_drones))):
                    assignment = UserDroneAssignment(
                        user_id=pilot.id,
                        drone_id=available_drones[j].id
                    )
                    self.db.add(assignment)
                    self.db.flush()
                    self.test_data_ids['user_drone_assignments'].append((pilot.id, available_drones[j].id))

            # 8. Create Restricted Zones
            nfz_data = [
                {
                    "name": "Airport NFZ",
                    "description": "Major airport restricted area",
                    "geometry_type": NFZGeometryType.CIRCLE,
                    "definition": {"center_lat": 43.23, "center_lon": 76.95, "radius_m": 5000},
                    "min_alt": 0, "max_alt": 500
                },
                {
                    "name": "Military Base NFZ",
                    "description": "Military installation restricted area",
                    "geometry_type": NFZGeometryType.POLYGON,
                    "definition": {"coordinates": [[[76.90, 43.20], [76.92, 43.20], [76.92, 43.22], [76.90, 43.22], [76.90, 43.20]]]},
                    "min_alt": 0, "max_alt": 1000
                },
                {
                    "name": "City Center NFZ",
                    "description": "Downtown restricted flying area",
                    "geometry_type": NFZGeometryType.CIRCLE,
                    "definition": {"center_lat": 43.24, "center_lon": 76.93, "radius_m": 2000},
                    "min_alt": 0, "max_alt": 150
                }
            ]

            for nfz in nfz_data:
                zone = RestrictedZone(
                    name=nfz["name"],
                    description=nfz["description"],
                    geometry_type=nfz["geometry_type"],
                    definition_json=nfz["definition"],
                    min_altitude_m=nfz["min_alt"],
                    max_altitude_m=nfz["max_alt"],
                    is_active=True,
                    created_by_authority_id=authority_admin.id
                )
                self.db.add(zone)
                self.db.flush()
                self.test_data_ids['restricted_zones'].append(zone.id)

            # 9. Create Flight Plans
            flight_plans = []
            base_time = datetime.now(timezone.utc)
            
            # Solo pilot flight plans
            for i, pilot in enumerate(solo_pilots):
                pilot_drones = [d for d in drones if d.solo_owner_user_id == pilot.id]
                if pilot_drones:
                    for j in range(2):  # 2 flight plans per solo pilot
                        waypoints_data = [
                            {"lat": 43.20 + (j*0.01), "lon": 76.90 + (j*0.01), "alt": 50 + (j*10), "order": 0},
                            {"lat": 43.21 + (j*0.01), "lon": 76.91 + (j*0.01), "alt": 60 + (j*10), "order": 1},
                            {"lat": 43.22 + (j*0.01), "lon": 76.92 + (j*0.01), "alt": 70 + (j*10), "order": 2},
                        ]
                        
                        flight_plan = FlightPlan(
                            user_id=pilot.id,
                            drone_id=pilot_drones[0].id,
                            planned_departure_time=base_time + timedelta(hours=i*2 + j),
                            planned_arrival_time=base_time + timedelta(hours=i*2 + j + 1),
                            status=FlightPlanStatus.PENDING_AUTHORITY_APPROVAL,
                            notes=f"Solo pilot test flight {i+1}-{j+1}"
                        )
                        self.db.add(flight_plan)
                        self.db.flush()
                        flight_plans.append(flight_plan)
                        self.test_data_ids['flight_plans'].append(flight_plan.id)
                        
                        # Add waypoints
                        for wp_data in waypoints_data:
                            waypoint = Waypoint(
                                flight_plan_id=flight_plan.id,
                                latitude=wp_data["lat"],
                                longitude=wp_data["lon"],
                                altitude_m=wp_data["alt"],
                                sequence_order=wp_data["order"]
                            )
                            self.db.add(waypoint)
                            self.db.flush()
                            self.test_data_ids['waypoints'].append(waypoint.id)

            # Organization pilot flight plans
            for i, pilot in enumerate(org_pilots):
                assigned_drones = [a for a in self.test_data_ids['user_drone_assignments'] if a[0] == pilot.id]
                if assigned_drones:
                    drone_id = assigned_drones[0][1]  # Use first assigned drone
                    waypoints_data = [
                        {"lat": 43.25 + (i*0.01), "lon": 76.95 + (i*0.01), "alt": 80 + (i*5), "order": 0},
                        {"lat": 43.26 + (i*0.01), "lon": 76.96 + (i*0.01), "alt": 90 + (i*5), "order": 1},
                    ]
                    
                    flight_plan = FlightPlan(
                        user_id=pilot.id,
                        drone_id=drone_id,
                        organization_id=pilot.organization_id,
                        planned_departure_time=base_time + timedelta(hours=24 + i),
                        planned_arrival_time=base_time + timedelta(hours=25 + i),
                        status=FlightPlanStatus.PENDING_ORG_APPROVAL,
                        notes=f"Organization pilot test flight {i+1}"
                    )
                    self.db.add(flight_plan)
                    self.db.flush()
                    flight_plans.append(flight_plan)
                    self.test_data_ids['flight_plans'].append(flight_plan.id)
                    
                    # Add waypoints
                    for wp_data in waypoints_data:
                        waypoint = Waypoint(
                            flight_plan_id=flight_plan.id,
                            latitude=wp_data["lat"],
                            longitude=wp_data["lon"],
                            altitude_m=wp_data["alt"],
                            sequence_order=wp_data["order"]
                        )
                        self.db.add(waypoint)
                        self.db.flush()
                        self.test_data_ids['waypoints'].append(waypoint.id)

            # 10. Create Telemetry Data
            for flight_plan in flight_plans[:5]:  # Add telemetry for first 5 flights
                drone = next(d for d in drones if d.id == flight_plan.drone_id)
                waypoints = [w for w in self.db.query(Waypoint).filter_by(flight_plan_id=flight_plan.id).all()]
                
                for i, waypoint in enumerate(waypoints):
                    telemetry = TelemetryLog(
                        flight_plan_id=flight_plan.id,
                        drone_id=drone.id,
                        timestamp=flight_plan.planned_departure_time + timedelta(minutes=i*10),
                        latitude=waypoint.latitude,
                        longitude=waypoint.longitude,
                        altitude_m=waypoint.altitude_m,
                        speed_mps=15.0 + (i * 2),
                        heading_degrees=90.0 + (i * 45),
                        status_message="ON_SCHEDULE"
                    )
                    self.db.add(telemetry)
                    self.db.flush()
                    self.test_data_ids['telemetry_logs'].append(telemetry.id)
                    
                    # Update drone's last telemetry
                    drone.last_telemetry_id = telemetry.id
                    drone.last_seen_at = telemetry.timestamp

            self.db.commit()
            self.log_test("Test data creation completed", "PASS")
            
        except Exception as e:
            self.db.rollback()
            self.log_test(f"Test data creation failed: {str(e)}", "FAIL")
            raise

    def test_crud_operations(self):
        """Test all CRUD operations"""
        self.log_test("Testing CRUD operations", "RUNNING")
        
        try:
            # Test user CRUD
            users = crud_user.user.get_multi(self.db, limit=100)
            assert len(users) >= 11, f"Expected at least 11 users, got {len(users)}"
            
            # Test organization CRUD
            orgs = crud_organization.organization.get_multi(self.db, limit=100)
            assert len(orgs) >= 3, f"Expected at least 3 organizations, got {len(orgs)}"
            
            # Test drone CRUD
            drones = crud_drone.drone.get_multi(self.db, limit=100)
            assert len(drones) >= 19, f"Expected at least 19 drones, got {len(drones)}"  # 9 org + 10 solo
            
            # Test flight plan CRUD
            flight_plans = crud_flight_plan.flight_plan.get_multi(self.db, limit=100)
            assert len(flight_plans) >= 16, f"Expected at least 16 flight plans, got {len(flight_plans)}"
            
            self.log_test("CRUD operations test", "PASS")
            
        except Exception as e:
            self.log_test(f"CRUD operations test failed: {str(e)}", "FAIL")
            raise

    def test_relationships(self):
        """Test database relationships"""
        self.log_test("Testing database relationships", "RUNNING")
        
        try:
            # Test User-Organization relationship
            org_admin = self.db.query(User).filter_by(role=UserRole.ORGANIZATION_ADMIN).first()
            assert org_admin.organization is not None, "Organization admin should have an organization"
            assert org_admin.organization.admin_id == org_admin.id, "Organization should reference admin"
            
            # Test Drone ownership relationships
            org_drone = self.db.query(Drone).filter_by(owner_type=DroneOwnerType.ORGANIZATION).first()
            assert org_drone.organization_owner is not None, "Org drone should have organization owner"
            
            solo_drone = self.db.query(Drone).filter_by(owner_type=DroneOwnerType.SOLO_PILOT).first()
            assert solo_drone.solo_owner_user is not None, "Solo drone should have user owner"
            
            # Test Flight Plan relationships
            flight_plan = self.db.query(FlightPlan).first()
            assert flight_plan.submitter_user is not None, "Flight plan should have submitter"
            assert flight_plan.drone is not None, "Flight plan should have drone"
            assert len(flight_plan.waypoints) > 0, "Flight plan should have waypoints"
            
            # Test User-Drone assignments
            assignment = self.db.query(UserDroneAssignment).first()
            assert assignment.user is not None, "Assignment should have user"
            assert assignment.drone is not None, "Assignment should have drone"
            
            # Test Telemetry relationships
            telemetry = self.db.query(TelemetryLog).first()
            if telemetry:
                assert telemetry.drone is not None, "Telemetry should have drone"
                assert telemetry.flight_plan is not None, "Telemetry should have flight plan"
            
            self.log_test("Database relationships test", "PASS")
            
        except Exception as e:
            self.log_test(f"Database relationships test failed: {str(e)}", "FAIL")
            raise

    def test_business_logic(self):
        """Test business logic constraints"""
        self.log_test("Testing business logic constraints", "RUNNING")
        
        try:
            # Test user roles and permissions
            authority_admins = self.db.query(User).filter_by(role=UserRole.AUTHORITY_ADMIN).all()
            assert len(authority_admins) >= 1, "Should have at least one authority admin"
            
            # Test organization constraints
            org_admins = self.db.query(User).filter_by(role=UserRole.ORGANIZATION_ADMIN).all()
            for admin in org_admins:
                assert admin.organization_id is not None, "Org admin must have organization"
                assert admin.organization.admin_id == admin.id, "Organization must reference admin"
            
            # Test drone ownership constraints
            org_drones = self.db.query(Drone).filter_by(owner_type=DroneOwnerType.ORGANIZATION).all()
            for drone in org_drones:
                assert drone.organization_id is not None, "Org drone must have organization"
                assert drone.solo_owner_user_id is None, "Org drone cannot have solo owner"
            
            solo_drones = self.db.query(Drone).filter_by(owner_type=DroneOwnerType.SOLO_PILOT).all()
            for drone in solo_drones:
                assert drone.solo_owner_user_id is not None, "Solo drone must have user owner"
                assert drone.organization_id is None, "Solo drone cannot have organization"
            
            # Test flight plan status workflow
            pending_org = self.db.query(FlightPlan).filter_by(status=FlightPlanStatus.PENDING_ORG_APPROVAL).all()
            pending_auth = self.db.query(FlightPlan).filter_by(status=FlightPlanStatus.PENDING_AUTHORITY_APPROVAL).all()
            
            for fp in pending_org:
                assert fp.organization_id is not None, "Org approval flight must have organization"
            
            # Test waypoint ordering
            flight_plans_with_waypoints = self.db.query(FlightPlan).join(Waypoint).all()
            for fp in flight_plans_with_waypoints:
                waypoints = sorted(fp.waypoints, key=lambda w: w.sequence_order)
                for i, wp in enumerate(waypoints):
                    assert wp.sequence_order == i, f"Waypoint order should be sequential, expected {i}, got {wp.sequence_order}"
            
            self.log_test("Business logic constraints test", "PASS")
            
        except Exception as e:
            self.log_test(f"Business logic constraints test failed: {str(e)}", "FAIL")
            raise

    def test_data_integrity(self):
        """Test data integrity and constraints"""
        self.log_test("Testing data integrity", "RUNNING")
        
        try:
            # Test unique constraints
            emails = [user.email for user in self.db.query(User).all()]
            assert len(emails) == len(set(emails)), "User emails should be unique"
            
            serial_numbers = [drone.serial_number for drone in self.db.query(Drone).all()]
            assert len(serial_numbers) == len(set(serial_numbers)), "Drone serial numbers should be unique"
            
            org_names = [org.name for org in self.db.query(Organization).all()]
            assert len(org_names) == len(set(org_names)), "Organization names should be unique"
            
            org_bins = [org.bin for org in self.db.query(Organization).all()]
            assert len(org_bins) == len(set(org_bins)), "Organization BINs should be unique"
            
            # Test foreign key integrity
            flight_plans = self.db.query(FlightPlan).all()
            for fp in flight_plans:
                assert self.db.query(User).filter_by(id=fp.user_id).first() is not None, "Flight plan user must exist"
                assert self.db.query(Drone).filter_by(id=fp.drone_id).first() is not None, "Flight plan drone must exist"
            
            # Test cascade constraints
            waypoints = self.db.query(Waypoint).all()
            for wp in waypoints:
                assert self.db.query(FlightPlan).filter_by(id=wp.flight_plan_id).first() is not None, "Waypoint flight plan must exist"
            
            self.log_test("Data integrity test", "PASS")
            
        except Exception as e:
            self.log_test(f"Data integrity test failed: {str(e)}", "FAIL")
            raise

    def test_performance(self):
        """Test database performance with complex queries"""
        self.log_test("Testing database performance", "RUNNING")
        
        try:
            import time
            
            # Test complex join query performance
            start_time = time.time()
            complex_query = self.db.query(FlightPlan)\
                .join(User)\
                .join(Drone)\
                .outerjoin(Organization)\
                .outerjoin(Waypoint)\
                .outerjoin(TelemetryLog)\
                .limit(100).all()
            query_time = time.time() - start_time
            
            assert query_time < 5.0, f"Complex query took too long: {query_time:.2f}s"
            
            # Test pagination performance
            start_time = time.time()
            paginated_users = crud_user.user.get_multi(self.db, skip=0, limit=50)
            pagination_time = time.time() - start_time
            
            assert pagination_time < 1.0, f"Pagination query took too long: {pagination_time:.2f}s"
            
            # Test aggregation performance
            start_time = time.time()
            user_count = self.db.query(User).count()
            drone_count = self.db.query(Drone).count()
            flight_count = self.db.query(FlightPlan).count()
            aggregation_time = time.time() - start_time
            
            assert aggregation_time < 1.0, f"Aggregation queries took too long: {aggregation_time:.2f}s"
            
            self.log_test(f"Performance test (Query: {query_time:.2f}s, Pagination: {pagination_time:.2f}s, Aggregation: {aggregation_time:.2f}s)", "PASS")
            
        except Exception as e:
            self.log_test(f"Performance test failed: {str(e)}", "FAIL")
            raise

    def print_test_summary(self):
        """Print summary of created test data"""
        self.log_test("Test Data Summary", "INFO")
        
        summary = {
            'Users': len(self.test_data_ids['users']),
            'Organizations': len(self.test_data_ids['organizations']),
            'Drones': len(self.test_data_ids['drones']),
            'Flight Plans': len(self.test_data_ids['flight_plans']),
            'Waypoints': len(self.test_data_ids['waypoints']),
            'Telemetry Logs': len(self.test_data_ids['telemetry_logs']),
            'Restricted Zones': len(self.test_data_ids['restricted_zones']),
            'User-Drone Assignments': len(self.test_data_ids['user_drone_assignments'])
        }
        
        for entity, count in summary.items():
            print(f"  📊 {entity}: {count} records")
        
        # Print some sample data
        print("\n📋 Sample Data:")
        
        # Sample users by role
        users_by_role = {}
        for user in self.db.query(User).all():
            role = user.role.value
            if role not in users_by_role:
                users_by_role[role] = []
            users_by_role[role].append(user.email)
        
        for role, emails in users_by_role.items():
            print(f"  👤 {role}: {len(emails)} users")
            if emails:
                print(f"      Example: {emails[0]}")
        
        # Sample flight plans by status
        fp_by_status = {}
        for fp in self.db.query(FlightPlan).all():
            status = fp.status.value
            if status not in fp_by_status:
                fp_by_status[status] = 0
            fp_by_status[status] += 1
        
        print(f"\n  ✈️  Flight Plans by Status:")
        for status, count in fp_by_status.items():
            print(f"      {status}: {count}")

    def cleanup_test_data(self):
        """Clean up all test data"""
        self.log_test("Cleaning up test data", "RUNNING")
        
        try:
            # Order matters due to foreign key constraints
            cleanup_order = [
                ('telemetry_logs', TelemetryLog),
                ('waypoints', Waypoint),
                ('flight_plans', FlightPlan),
                ('user_drone_assignments', UserDroneAssignment),
                ('drones', Drone),
                ('restricted_zones', RestrictedZone),
                ('users', User),
                ('organizations', Organization)
            ]
            
            for table_name, model_class in cleanup_order:
                if table_name == 'user_drone_assignments':
                    # Special handling for composite key
                    for user_id, drone_id in self.test_data_ids[table_name]:
                        assignment = self.db.query(UserDroneAssignment).filter_by(
                            user_id=user_id, drone_id=drone_id
                        ).first()
                        if assignment:
                            self.db.delete(assignment)
                else:
                    ids_to_delete = self.test_data_ids[table_name]
                    if ids_to_delete:
                        # Delete in batches for better performance
                        for i in range(0, len(ids_to_delete), 100):
                            batch = ids_to_delete[i:i+100]
                            self.db.query(model_class).filter(model_class.id.in_(batch)).delete(synchronize_session=False)
                        
                print(f"  🗑️  Cleaned {len(self.test_data_ids[table_name])} {table_name}")
            
            self.db.commit()
            self.log_test("Test data cleanup completed", "PASS")
            
        except Exception as e:
            self.db.rollback()
            self.log_test(f"Test data cleanup failed: {str(e)}", "FAIL")
            raise

    def verify_cleanup(self):
        """Verify that all test data has been cleaned up"""
        self.log_test("Verifying cleanup", "RUNNING")
        
        try:
            # Check that test data is gone
            remaining_counts = {}
            
            # Count remaining test users (by email pattern)
            remaining_counts['test_users'] = self.db.query(User).filter(
                User.email.like('%@test.com')
            ).count()
            
            # Count remaining test organizations (by name pattern)
            remaining_counts['test_orgs'] = self.db.query(Organization).filter(
                Organization.name.like('Test Organization%')
            ).count()
            
            # Count remaining test drones (by serial number pattern)
            remaining_counts['test_drones'] = self.db.query(Drone).filter(
                Drone.serial_number.like('%_SN%')
            ).count()
            
            # Count remaining test flight plans (by notes pattern)
            remaining_counts['test_flights'] = self.db.query(FlightPlan).filter(
                FlightPlan.notes.like('%test flight%')
            ).count()
            
            # Count remaining test NFZs (by name pattern)
            remaining_counts['test_nfz'] = self.db.query(RestrictedZone).filter(
                RestrictedZone.name.like('%NFZ')
            ).count()
            
            total_remaining = sum(remaining_counts.values())
            
            if total_remaining == 0:
                self.log_test("Cleanup verification passed - no test data remaining", "PASS")
            else:
                self.log_test(f"Cleanup verification warning - {total_remaining} test records may remain", "INFO")
                for entity, count in remaining_counts.items():
                    if count > 0:
                        print(f"  ⚠️  {entity}: {count} remaining")
            
        except Exception as e:
            self.log_test(f"Cleanup verification failed: {str(e)}", "FAIL")

    def generate_test_report(self):
        """Generate a comprehensive test report"""
        self.log_test("Generating test report", "INFO")
        
        report = {
            "test_suite": "UTM Database Comprehensive Test",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database_url": settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else "hidden",
            "test_data_created": self.test_data_ids,
            "database_schema_info": {}
        }
        
        try:
            # Get table information
            tables_info = {}
            table_names = ['users', 'organizations', 'drones', 'flight_plans', 'waypoints', 
                          'telemetry_logs', 'restricted_zones', 'user_drone_assignments']
            
            for table_name in table_names:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                count_result = self.db.execute(count_query).scalar()
                tables_info[table_name] = {"total_records": count_result}
            
            report["database_schema_info"] = tables_info
            
            # Save report to file
            report_filename = f"db_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📄 Test report saved to: {report_filename}")
            
        except Exception as e:
            self.log_test(f"Report generation failed: {str(e)}", "FAIL")

    def run_stress_test(self):
        """Run stress tests with high volume data"""
        self.log_test("Running stress test", "RUNNING")
        
        try:
            import time
            stress_test_ids = []
            
            # Create many users quickly
            start_time = time.time()
            for i in range(100):
                user = User(
                    full_name=f"Stress Test User {i}",
                    email=f"stress_test_{i}@test.com",
                    phone_number=f"+77000000{i:03d}",
                    iin=f"99999999{i:03d}",
                    hashed_password=get_password_hash("stresstest"),
                    role=UserRole.SOLO_PILOT,
                    is_active=True
                )
                self.db.add(user)
                if i % 20 == 0:  # Commit in batches
                    self.db.flush()
                    
            self.db.commit()
            creation_time = time.time() - start_time
            
            # Test bulk query performance
            start_time = time.time()
            stress_users = self.db.query(User).filter(User.email.like('stress_test_%')).all()
            query_time = time.time() - start_time
            
            # Cleanup stress test data
            start_time = time.time()
            self.db.query(User).filter(User.email.like('stress_test_%')).delete()
            self.db.commit()
            cleanup_time = time.time() - start_time
            
            self.log_test(f"Stress test (Create: {creation_time:.2f}s, Query: {query_time:.2f}s, Cleanup: {cleanup_time:.2f}s)", "PASS")
            
        except Exception as e:
            self.db.rollback()
            self.log_test(f"Stress test failed: {str(e)}", "FAIL")
            raise

    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 Starting Comprehensive Database Test Suite")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Create test data
            self.create_test_data()
            
            # Print summary of created data
            self.print_test_summary()
            
            print("\n" + "=" * 60)
            print("🧪 Running Database Tests")
            print("=" * 60)
            
            # Run all tests
            self.test_crud_operations()
            self.test_relationships()
            self.test_business_logic()
            self.test_data_integrity()
            self.test_performance()
            self.run_stress_test()
            
            print("\n" + "=" * 60)
            print("✅ All tests completed successfully!")
            
            end_time = datetime.now()
            duration = end_time - start_time
            print(f"⏱️  Total test duration: {duration.total_seconds():.2f} seconds")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {str(e)}")
            raise
        
        finally:
            # Always clean up, even if tests fail
            print("\n" + "=" * 60)
            print("🧹 Cleaning Up Test Data")
            print("=" * 60)
            self.cleanup_test_data()
            self.verify_cleanup()
            self.generate_test_report()
            self.db.close()
            print("🎉 Database test suite completed!")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db:
            self.db.close()


def main():
    """Main function to run the test suite"""
    try:
        with DatabaseTestSuite() as test_suite:
            test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite failed with error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())