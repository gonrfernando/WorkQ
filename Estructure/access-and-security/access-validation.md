---
icon: user-check
---

# Access Validation

#### **Sign-up**

**Functional Requirements**

1. **Duplicate Email Check**
   * The system must validate that the email address is not already in use before allowing the user to sign up.
2. **Empty Inputs Validation**
   * The system must validate empty inputs, such as the email and password fields, after submitting the form and show an error message to the user.
3. **Email Validation**
   * If the email format is incorrect (missing "@" or "."), the system will show an error message indicating the email format is wrong.
4. **Email Verification**
   * After the user enters their email, a first-time password will be sent via email.
5. **Password Validation**
   * When creating a password, it must meet the following format:
     * At least 8 characters
     * One uppercase letter
     * One lowercase letter
     * One number
     * One special character
6. **User Creation**
   * The new user must be successfully created and saved in the database.

**Non-Functional Requirements**

* The sign-up interface must be understandable, interactive, and visually pleasant.
* Ensure the sign-up process is quick and responsive.
