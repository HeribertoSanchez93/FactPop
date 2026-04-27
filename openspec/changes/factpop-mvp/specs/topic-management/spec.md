## ADDED Requirements

### Requirement: User can create a learning topic
The system SHALL allow the user to create a new learning topic by providing a name. The name SHALL be a non-empty string. Duplicate topic names SHALL be rejected.

#### Scenario: Create a valid topic
- **WHEN** the user provides a non-empty, unique topic name (e.g., "Java")
- **THEN** the system saves the topic as active and confirms creation

#### Scenario: Reject duplicate topic name
- **WHEN** the user provides a topic name that already exists (case-insensitive)
- **THEN** the system rejects the request with a clear error message and does not create a duplicate

#### Scenario: Reject empty topic name
- **WHEN** the user submits an empty or whitespace-only topic name
- **THEN** the system rejects the request with a validation error

### Requirement: User can list all topics
The system SHALL display all existing topics with their current active/inactive status.

#### Scenario: List topics when topics exist
- **WHEN** the user requests the topic list and at least one topic exists
- **THEN** the system displays all topics with name and status (active/inactive)

#### Scenario: List topics when no topics exist
- **WHEN** the user requests the topic list and no topics have been created
- **THEN** the system displays an empty list with a hint to add topics

### Requirement: User can activate and deactivate topics
The system SHALL allow the user to toggle a topic between active and inactive states. Only active topics SHALL be considered for random selection during popup scheduling.

#### Scenario: Deactivate an active topic
- **WHEN** the user deactivates a topic that is currently active
- **THEN** the topic status changes to inactive and it is excluded from future random selection

#### Scenario: Activate an inactive topic
- **WHEN** the user activates a topic that is currently inactive
- **THEN** the topic status changes to active and it becomes eligible for random selection

#### Scenario: Deactivate the last active topic
- **WHEN** the user attempts to deactivate the only remaining active topic
- **THEN** the system warns that no active topics remain and popups will not fire until at least one topic is active; the deactivation MAY proceed but the system SHALL suppress popup generation while no active topics exist

### Requirement: User can delete a topic
The system SHALL allow the user to permanently delete a topic. Deleting a topic SHALL NOT delete associated fact history; historical facts retain their topic label for reference.

#### Scenario: Delete an existing topic
- **WHEN** the user deletes a topic
- **THEN** the topic is removed from the topic list and excluded from all future selections; associated historical facts remain in fact history

#### Scenario: Delete a non-existent topic
- **WHEN** the user attempts to delete a topic that does not exist
- **THEN** the system returns an error indicating the topic was not found
