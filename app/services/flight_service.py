from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.flight_plan import FlightPlan, FlightPlanStatus
from app.models.drone import Drone, DroneStatus
from app.schemas.flight_plan import FlightPlanCreate
from app.crud import flight_plan as crud_flight_plan
from app.crud import drone as crud_drone
from app.services.nfz_service import NFZService # For NFZ checks
from app.services.telemetry_service import telemetry_service # To start simulation
from app.models.drone import DroneStatus

class FlightService:
    def __init__(self, nfz_service: NFZService = NFZService()): # Allow injecting for tests
        self.nfz_service = nfz_service

    def submit_flight_plan(
        self, 
        db: Session, 
        *, 
        flight_plan_in: FlightPlanCreate, 
        submitter: User
    ) -> FlightPlan:
        # 1. Validate Drone
        db_drone = crud_drone.get(db, id=flight_plan_in.drone_id)
        if not db_drone:
            raise ValueError("Drone not found.")
        
        # Check drone ownership/assignment based on submitter's role
        if submitter.role == UserRole.SOLO_PILOT:
            if db_drone.solo_owner_user_id != submitter.id:
                raise ValueError("Solo pilot can only submit flights for their own drones.")
            organization_id = None
        elif submitter.role == UserRole.ORGANIZATION_PILOT:
            if not submitter.organization_id or db_drone.organization_id != submitter.organization_id:
                raise ValueError("Organization pilot can only submit flights for drones in their organization.")
            # Check if pilot is assigned to this drone
            assignment = crud_drone.user_drone_assignment.get_assignment(db, user_id=submitter.id, drone_id=db_drone.id)
            if not assignment:
                # Or if org allows any pilot to use any org drone without explicit assignment
                # This rule needs clarification from requirements. Assuming explicit assignment for now.
                raise ValueError("Organization pilot is not assigned to this drone.")
            organization_id = submitter.organization_id
        else:
            raise ValueError("Invalid user role for submitting flight plans.")

        # 2. Perform NFZ Pre-check (Simplified)
        # This would involve checking waypoints against RestrictedZone geometries
        # For now, a placeholder
        nfz_violations = self.nfz_service.check_flight_plan_against_nfzs(db, flight_plan_in.waypoints)
        if nfz_violations:
            # For MVP, we might just raise an error or log it.
            # A real system might allow submission with warnings or require modification.
            raise ValueError(f"Flight plan intersects with No-Fly Zones: {', '.join(nfz_violations)}")

        # 3. Determine initial status
        initial_status: FlightPlanStatus
        if submitter.role == UserRole.SOLO_PILOT:
            initial_status = FlightPlanStatus.PENDING_AUTHORITY_APPROVAL
        elif submitter.role == UserRole.ORGANIZATION_PILOT:
            # Assuming two-step approval for organizations
            initial_status = FlightPlanStatus.PENDING_ORG_APPROVAL 
        else: # Should not happen due to earlier check
            raise ValueError("Cannot determine initial flight plan status for user role.")

        # 4. Create Flight Plan
        created_flight_plan = crud_flight_plan.create_with_waypoints(
            db, 
            obj_in=flight_plan_in, 
            user_id=submitter.id,
            organization_id=organization_id,
            initial_status=initial_status
        )
        return created_flight_plan

    def update_flight_plan_status(
        self,
        db: Session,
        *,
        flight_plan_id: int,
        new_status: FlightPlanStatus,
        actor: User, # User performing the action
        rejection_reason: str | None = None,
    ) -> FlightPlan:
        db_flight_plan = crud_flight_plan.get(db, id=flight_plan_id)
        if not db_flight_plan:
            raise ValueError("Flight plan not found.")

        current_status = db_flight_plan.status
        is_org_approval_step = False

        # State transition logic based on actor's role and current status
        if actor.role == UserRole.ORGANIZATION_ADMIN:
            if db_flight_plan.organization_id != actor.organization_id:
                raise ValueError("Organization Admin cannot modify flight plans outside their organization.")
            
            if current_status == FlightPlanStatus.PENDING_ORG_APPROVAL:
                if new_status == FlightPlanStatus.PENDING_AUTHORITY_APPROVAL: # Org Admin approves, sends to Authority
                    is_org_approval_step = True
                elif new_status == FlightPlanStatus.REJECTED_BY_ORG:
                    if not rejection_reason:
                        raise ValueError("Rejection reason required when rejecting by organization.")
                # Org admin might also directly approve if no authority step is needed (e.g. for certain flights)
                # elif new_status == FlightPlanStatus.APPROVED: # Org Admin self-approves
                #     is_org_approval_step = True 
                else:
                    raise ValueError(f"Invalid status transition from {current_status} to {new_status} by Organization Admin.")
            else:
                raise ValueError(f"Organization Admin cannot change status from {current_status}.")

        elif actor.role == UserRole.AUTHORITY_ADMIN:
            valid_previous_statuses_for_authority = [
                FlightPlanStatus.PENDING_AUTHORITY_APPROVAL,
                FlightPlanStatus.PENDING_ORG_APPROVAL # If solo pilot or orgs submit directly to authority
            ]
            if current_status in valid_previous_statuses_for_authority:
                if new_status == FlightPlanStatus.APPROVED:
                    pass # Authority approves
                elif new_status == FlightPlanStatus.REJECTED_BY_AUTHORITY:
                    if not rejection_reason:
                        raise ValueError("Rejection reason required when rejecting by authority.")
                else:
                    raise ValueError(f"Invalid status transition from {current_status} to {new_status} by Authority Admin.")
            else:
                raise ValueError(f"Authority Admin cannot change status from {current_status}.")
        else:
            raise ValueError("User role not authorized to update flight plan status.")

        return crud_flight_plan.update_status(
            db, 
            db_obj=db_flight_plan, 
            new_status=new_status, 
            rejection_reason=rejection_reason,
            approver_id=actor.id,
            is_org_approval=is_org_approval_step
        )

    def start_flight(self, db: Session, *, flight_plan_id: int, pilot: User) -> FlightPlan:
        db_flight_plan = crud_flight_plan.get(db, id=flight_plan_id)
        if not db_flight_plan:
            raise ValueError("Flight plan not found.")
        if db_flight_plan.user_id != pilot.id:
            raise ValueError("Only the submitting pilot can start the flight.")
        if db_flight_plan.status != FlightPlanStatus.APPROVED:
            raise ValueError(f"Flight plan must be APPROVED to start. Current status: {db_flight_plan.status}")

        started_flight = crud_flight_plan.start_flight(db, db_obj=db_flight_plan)
        
        # Start telemetry simulation for this flight
        telemetry_service.start_flight_simulation(db, flight_plan=started_flight)
        
        return started_flight

    def cancel_flight(
        self, 
        db: Session, 
        *, 
        flight_plan_id: int, 
        actor: User, 
        reason: str | None = None
    ) -> FlightPlan:
        db_flight_plan = crud_flight_plan.get(db, id=flight_plan_id)
        if not db_flight_plan:
            raise ValueError("Flight plan not found.")

        cancelled_by_role_type = "UNKNOWN" # For status CANCELLED_BY_ADMIN or CANCELLED_BY_PILOT

        if actor.role in [UserRole.SOLO_PILOT, UserRole.ORGANIZATION_PILOT]:
            if db_flight_plan.user_id != actor.id:
                raise ValueError("Pilot can only cancel their own flight plans.")
            if db_flight_plan.status not in [FlightPlanStatus.PENDING_ORG_APPROVAL, FlightPlanStatus.PENDING_AUTHORITY_APPROVAL, FlightPlanStatus.APPROVED]:
                raise ValueError(f"Pilot cannot cancel flight in status {db_flight_plan.status}.")
            cancelled_by_role_type = "PILOT"
        
        elif actor.role == UserRole.ORGANIZATION_ADMIN:
            if db_flight_plan.organization_id != actor.organization_id:
                raise ValueError("Organization Admin cannot cancel flights outside their organization.")
            # Org Admin can cancel flights in more states, e.g., PENDING_*, APPROVED, maybe even ACTIVE (emergency)
            # Add specific state checks if needed.
            cancelled_by_role_type = "ADMIN"

        elif actor.role == UserRole.AUTHORITY_ADMIN:
            # Authority Admin can cancel flights in most states
            cancelled_by_role_type = "ADMIN"
        else:
            raise ValueError("User role not authorized to cancel this flight plan.")

        # If flight was active, stop simulation
        if db_flight_plan.status == FlightPlanStatus.ACTIVE:
            telemetry_service.stop_flight_simulation(flight_plan_id)
            # Also update drone status if it was active
            db_drone = crud_drone.get(db, id=db_flight_plan.drone_id)
            if db_drone and db_drone.current_status == DroneStatus.ACTIVE:
                crud_drone.update(db, db_obj=db_drone, obj_in={"current_status": DroneStatus.IDLE})


        return crud_flight_plan.cancel_flight(db, db_obj=db_flight_plan, cancelled_by_role=cancelled_by_role_type, reason=reason)

flight_service = FlightService() # Singleton instance