---
icon: square-check
---

# Permission management

**Functional Requirements**

**Project Permissions Configuration**\
The system must allow an admin to configure project permissions within their designated area.

* The admin should have access to a small menu displaying various checkboxes for permissions.
* The admin must be able to select or deselect options based on the required project permissions.
* The system should immediately update the permissions based on the admin's selections.

***

**Non-Functional Requirements**

* The permissions configuration interface should be clear and easy to navigate.
* The process of selecting and deselecting permissions must be quick and responsive.



#### **Justification: Omission of Project Permissions Configuration**

We chose not to implement a custom project permissions configuration module with checkbox-based controls, as originally proposed. Instead, we opted for a **role-based access control (RBAC)** system to ensure more consistent, scalable, and manageable access across the platform.

Using predefined roles such as **Admin**, **Project Manager**, and **Regular User** simplifies permission management while still covering the necessary access distinctions. This approach reduces complexity, minimizes the risk of misconfiguration, and provides a more intuitive experience for both users and administrators.

Additionally, enforcing access rules through roles aligns better with our existing system architecture and ensures cleaner integration with other features like task management and project creation. This decision helps guarantee more predictable behavior and more secure project oversight, especially as the platform scales.
