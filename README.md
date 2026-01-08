## 🍽️ MessNet: web Based Mess Management System for Hostel Administration

🔗 **Live Website:** https://messnet.pythonanywhere.com/

MessNet is a web-based, all-in-one mess automation platform built using Django.
It modernizes hostel mess workflows by allowing students to manage their menu, leave requests, bills, feedback, and lost & found through an elegant, user-friendly interface.

The system also empowers administrators with full control over menu updates, leave approvals, billing, notifications, and more—all from a centralized backend.

## 🎨 Modern UI Experience

- **MessNet** ships with a clean, responsive UI featuring:

- **Sleek layout** built with Tailwind CSS

- **Sidebar navigation** with animated Lucide icons

- **Dashboard** with live updates using real-time polling

- **Seamless module switching** (Menu, Leave, Bills, Feedback, Lost & Found)

- **Mobile-first responsive design**

- **Toast-like** feedback messages

- **Feedback** with 1–5 rating


## ✨ Core Features
**👨‍🎓 Student Features**

* **Dashboard Overview**
   
   * Profile info (Name, Hostel ID, Department, Mobile)
      
   * Latest mess bill & payment status
      
   * Leave request status
      
   * Today’s food menu
      
   * Latest admin notifications

* **Weekly Food Menu**

* **Mess Leave Request**

   * Apply for leave
      
   * Auto bill adjustment based on approved days

* **Mess Bill Tracking**

   * Monthly bill list with paid/due status

* **Feedback & Rating System**

   * 1–5  rating + comment

* **Lost & Found Portal**

   * Submit item reports

   * View admin-approved posts

* **Real-Time Notification System**

**🛠️ Admin Features**

   * **Add/update** weekly Food Menu

* **Approve/Reject** Leave Requests

* **Auto-generate** bill adjustments

* **Activate/Deactivate** Admin Notifications

* **Approve** Lost & Found entries

* View feedback **(read-only)**

* Manage **student profiles**


## 🧰 Technology Stack 
* **Backend**

   * [Python](https://www.python.org/)

   * [Django](https://www.djangoproject.com/) (Web Framework)

   * [SQLite](https://www.sqlite.org/index.html) (Development Database)
     
* **Frontend**

   * [Tailwind CSS](https://tailwindcss.com/) (Styling)

   * [Lucide Icons](https://lucide.dev/)

   * [JavaScript (ES6)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

   * [HTML5](https://developer.mozilla.org/en-US/docs/Web/HTML)  
   
   * [CSS3](https://developer.mozilla.org/en-US/docs/Web/CSS)


## 🖼️ Screenshots


📌 Dashboard

![Dashboard](screenshots/Dashboard.png)

📌 Food Menu

![Menu](screenshots/Menu.png)

📌 Leave Request

![Leave](screenshots/Leave.png)

📌 Bills

![Bills](screenshots/Bills.png)

📌 Feedback

![Feedback](screenshots/Feedback.png)

📌 Lost & Found

![LostFound](screenshots/LostFound.png)


## 🚀 Getting Started
**Prerequisites**

* [Python 3.10+](https://www.python.org/downloads/)
* [Git](https://git-scm.com/downloads/)

**🔧 Installation (Django Backend)**
1. **Clone the Repository:**
      ```
      git clone https://github.com/Sriram-Ravisankar/mess_management_system.git
      cd mess-management-system
      ```
      

2.  **Create and activate a virtual environment:**
    ```
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Create a `requirements.txt` file:**
    Create a file named `requirements.txt` in the root of your project and paste the following:
    ```
    Django==3.2.25
    gunicorn
    twilio
    whitenoise
    psycopg2-binary
    python-decouple
    ```

4.  **Install the required packages:**
    ```
    pip install -r requirements.txt
    ```

5.  **Apply database migrations:**
    ```
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Create an admin superuser:**
    ```
    python manage.py createsuperuser
    ```
    (You'll be prompted to create a username and password.)

7.  **Run the development server:**
    ```
    python manage.py runserver
    ```

8. **You're all set!** Open your browser and go to `http://localhost:3000/`.

## 🌐 Live Demo  
Click below to view the running project:  
🔗 **https://messnet.pythonanywhere.com/**

## 🧑‍🏫 How to Use

Follow these steps to understand and use the MessNet system effectively.

1️⃣ **Login to Your Account**

After installation, open your browser and go to: http://127.0.0.1:8000/


Enter your Hostel ID and password to sign in.

2️⃣ **Explore Your Dashboard**

 * **Once logged in, you can see:**

   * Your profile details
   
   * Latest mess bill and due dates
   
   * Leave request status
   
   * Today’s menu
   
   * Admin notifications

* The left sidebar helps you navigate between modules.

3️⃣**Check the Weekly Food Menu**

* **Click Food Menu in the sidebar to view:**

* Breakfast

* Lunch

* Dinner

* Menu is shown for all 7 days in a clean weekly layout.

4️⃣ **Submit a Leave Request**

To apply for leave:

Go to Leave Request

* Fill your from/to date

* Enter a valid reason

* Submit the form

Your request will be shown in My Leave History and admin will approve or reject it.

5️⃣**View Your Mess Bills**

* **Go to Bill Details to see:**

* Monthly bills

* Leave-adjustment reductions

* Paid / Due status

* Last payment date

6️⃣ **Submit Mess Feedback**

* Click Feedback and:

* Select a rating (1 to 5 stars)

* Enter comments

* Submit feedback

This helps improve mess service quality.

7️⃣ **Use the Lost & Found Module**

* **Under Lost & Found, you can:**

* Report lost/found items

* Add a description & date

* See admin-approved items

* Find your belongings easily

8️⃣ **Logout Safely**

Click Logout at the bottom of the sidebar to sign out securely.

9️⃣ **Admin Usage (For Administrators)**

**Admins can visit:**

http://127.0.0.1:8000/admin/

* **Here they can manage:**

* Menu updates

* Leave approvals

* Bills & adjustments

* Notifications

* Lost & Found approvals

* Student accounts

  ---

<div align="center">

### 🔗 **Live Website**
https://messnet.pythonanywhere.com/

---

### 👨‍💻 **Developed By**
**Sriram**

---

### 🌐 Connect With Me
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/sriram55/)

 
</div>
