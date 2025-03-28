---
icon: ball-pile
---

# Roles and permissions

**System Administrator (Super Admin)**

The **System Administrator** has the highest level of access and can:

* Delegate Area Administrators.
* Create user accounts.
* Change a user's role from a regular user to a Project Manager.
* Manage permission settings for projects.
* View the general project duration calendar.

**Area Administrator**

The **Area Administrator** has control over their assigned area and can:

* Create user accounts.
* Change a user's role from a regular user to a Project Manager.
* Receive and process requests for task modifications within their area’s projects.
* Manage permission settings for projects in their area.
* View the general project duration calendar.

**Project Manager**

The **Project Manager** is responsible for overseeing projects and has the ability to:

* Create new projects.
* Add users to a project.
* Remove users from a project.
* Perform full CRUD operations on tasks (modification permissions depend on project settings).
* Assign users to tasks.
* Attach files to tasks.
* Set task priorities.
* Access advanced project statistics.
* Review and approve/reject completed tasks.
* Access the project activity history.
* View the project task calendar.

**Regular User**

Regular users have limited access and can:

* Submit tasks for review.
* Mark task requirements as completed.
* Attach files when submitting tasks.
* View basic project statistics.
* View their personal task calendar.

***

#### **Project Permissions**

**Task Modification Rules:**

* **With approval request** (modifications require approval).
* **Free modification** (users can modify tasks without approval).
* **Free modification with a custom cooldown period** (users can modify tasks but with a time restriction).
* **Modification not allowed** (users cannot modify tasks).

**Additional Configuration:**

* Users can choose to receive **notifications for all events** or **only important ones**.
* Users can select whether to receive specific notification categories via email.
