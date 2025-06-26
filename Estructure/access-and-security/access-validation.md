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
5. **User Creation**
   * The new user must be successfully created and saved in the database.

**Log-in**

**Functional Requirements**

1. **Email and Password Validation**\
   The system must check that both fields are filled. If not, an appropriate error message will be displayed.
2. **Credential Verification**\
   The system must verify that the email and password entered match an existing user in the database. If the credentials are incorrect, an error message will be shown.
3. **Forgot Your Password**\
   Users who forget their password can request a password reset. The system will send a new password to their registered email, allowing them to securely log in and update their password.

**Non-Functional Requirements**

* The sign-up interface must be understandable, interactive, and visually pleasant.
* Ensure the sign-up process is quick and responsive.
