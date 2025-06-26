---
icon: square-plus
---

# Creation

**Functional Requirements**

1. **Create New Project**
   * The system must allow the creation of a new project with success, including saving the project data in the database.
   * The project data must include:
     * Project name
     * Description
     * Start date
     * End date
2. **Empty Inputs Validation**
   * The system must validate empty inputs for fields like project name, description, icon, start date, and end date, showing an error message if any required fields are left empty.
3. **Valid Date Range**
   * The system must ensure that the project’s start date is before the end date, and it should show an error message if the date range is invalid.

**Non-Functional Requirements**

* The project creation interface must be understandable, interactive, and visually pleasant.
* Ensure the project creation process is quick and responsive.
