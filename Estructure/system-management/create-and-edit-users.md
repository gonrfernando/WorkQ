---
description: Roles and Permissions
icon: user-gear
---

# Create and Edit users

**User Management Requirements**\
This section outlines the system requirements for creating and editing users, specifically focusing on administrative functionality. Admins must be able to manage user information, assign roles and permissions, and update existing user profiles efficiently through an intuitive interface.**Functional Requirements**

**User Creation with Roles and Permissions**\
The system must allow an admin to create and edit users, as well as assign roles and permissions.

* The admin must be able to fill in the necessary registration fields for a new user.
* The admin should be able to edit checkboxes related to user permissions.
* A list of available departments and roles should be provided for selection.
* The admin must have the option to either confirm the registration or go back to make changes.

**User Editing with Roles**\
The system must allow an admin to edit an existing user's information, including roles and permissions.

* The admin should be able to enter the user's email, with an auto-suggest feature to show matching options as the email is typed.
* Once the email is fully typed or selected, the admin can continue editing the user's details.
* The admin must be able to modify both personal and work-related information for the user.
* The admin should have the ability to edit checkboxes for the user’s permissions.
* The admin must have the option to either confirm the changes or go back to make adjustments.

***

**Non-Functional Requirements**

* The user creation and editing interface must be intuitive and user-friendly, ensuring smooth navigation for the admin.
* The process should be efficient, with clear feedback at each step to confirm actions.



**Justification**\
During the development of this module, it became clear that administrators would spend a significant amount of time manually creating and configuring new user accounts. To streamline this process and reduce administrative workload, we decided to implement a **self-sign-in module**. With this enhancement, admins can simply enter a user’s email address, and the system will automatically send a registration link or temporary password via email. This approach improves efficiency, enhances security, and simplifies onboarding for new users.
