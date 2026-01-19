# TaskHub


TaskHub is an intuitive and modern task management web application built with Python and Flask. It provides a clean, responsive interface with a glassmorphism design for managing your daily tasks. The application supports user authentication, task creation and management, profile customization, and personalized settings like a dark mode.

## Features

-   **User Authentication**: Secure sign-up, login, and logout functionality using Flask-Login and password hashing.
-   **Task Management (CRUD)**: Create, edit, update status, and delete tasks seamlessly.
-   **Interactive Dashboard**: A central hub to view, add, and manage all your tasks. Includes an overview panel summarizing total, completed, and pending tasks.
-   **Profile Management**: Users can view and update their profile information (name, email) and change their password.
-   **Customizable Settings**:
    -   **Dark Mode**: Easily toggle between light and dark themes for comfortable viewing.
    -   **Email Notifications**: Enable or disable email notifications (preference saved via AJAX).
-   **Dual Database Support**: Connects to a MongoDB Atlas cluster for persistent cloud storage or automatically falls back to a local `data.json` file if a MongoDB URI is not provided.
-   **Responsive UI**: Built with Tailwind CSS, the interface is fully responsive and features creative animations and a glassmorphism aesthetic.
-   **Account Management**: Users have the ability to securely delete their own account and all associated data.

## Tech Stack

-   **Backend**: Python, Flask, Flask-Login, Flask-Bcrypt, Werkzeug
-   **Database**: MongoDB (with Pymongo), JSON (local fallback)
-   **Frontend**: HTML, Tailwind CSS, JavaScript

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) 
![Flask-Login](https://img.shields.io/badge/Flask--Login-000000?style=for-the-badge) 
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white) 
![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white) 
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) 
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwind-css&logoColor=white) 
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

## Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

-   Python 3.x
-   `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/aryanwadhonkar/TaskHub.git
    cd TaskHub
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the required packages:**
    ```sh
    pip install -r requirements.txt
    ```

### Configuration

The application can run with either MongoDB or a local JSON file.

-   **MongoDB (Recommended)**:
    1.  Obtain a MongoDB connection string (URI) from MongoDB Atlas or your local instance.
    2.  Open the `app.py` file.
    3.  Replace the placeholder URI in the `MONGO_URI` variable with your own:
        ```python
        MONGO_URI = "your_mongodb_connection_string_here"
        ```

-   **Local JSON File**:
    -   If the `MONGO_URI` variable in `app.py` is left empty, the application will automatically create and use a `data.json` file in the root directory for data storage. No further setup is needed.

### Running the Application

1.  **Start the Flask server:**
    ```sh
    python app.py
    ```

2.  **Open your web browser** and navigate to `http://127.0.0.1:5000` to use the application.

## Usage

1.  **Sign Up**: Create a new account by providing your name, email, and a password.
2.  **Login**: Access your dashboard using your email and password.
3.  **Dashboard**:
    -   Add new tasks using the form at the top.
    -   View your pending and completed tasks.
    -   Mark tasks as "Done", edit their title and description, or delete them.
4.  **Profile Page**: Navigate to the Profile section to update your personal details or change your password.
5.  **Settings Page**:
    -   Toggle the "Dark Mode" switch to change the application's theme.
    -   Manage your notification preferences.
    -   If needed, you can delete your account from this page.
