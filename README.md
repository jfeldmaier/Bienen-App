# Bienen-App 🐝

A simple yet powerful web application to help beekeepers manage their bee colonies and track inspections with ease.

**Production-ready** with user authentication, security hardening, and Cloudflare Tunnel support for secure remote access.

---

## Features

### 🐝 Colony & Inspection Management
*   **Colony Management:** Create, edit, and track all your bee colonies with queen marking colors and numbers.
*   **Inspection Logs:** Record detailed inspection data for each colony, including:
    *   Queen status (seen/not seen)
    *   Colony ratings (strength, gentleness, vitality, brood quality)
    *   Frame counts (foundation, brood, food frames)
    *   Varroa checks and drone brood removal
    *   Honey yield tracking
*   **Image Uploads:** Attach multiple photos to your inspections for a visual record.
*   **Batch Inspections:** Efficiently log inspections for multiple colonies at once.
*   **Status Tracking:** Keep track of the status of each colony (strong, medium, weak).
*   **Multi-Select Delete:** Select and delete multiple inspections at once with a confirmation dialog.
*   **Detailed Views:** Click on any inspection to view comprehensive details.

### 🔐 User Management & Security
*   **Multi-User Support:** Separate databases for each user with isolated data
*   **Secure Authentication:** pbkdf2:sha256 password hashing, 10+ character requirements
*   **Account Lockout:** Protection against brute-force attacks (3 attempts = 30min lock)
*   **Rate Limiting:** 10 login attempts per minute, 200 requests per day
*   **Admin Interface:** User management for admins at `/admin/users`
*   **Session Management:** 10-day sessions with automatic renewal on activity

### 🚀 Production-Ready Deployment
*   **Gunicorn WSGI Server:** Multi-worker production server
*   **Security Headers:** HSTS, X-Frame-Options, CSP, X-XSS-Protection via Flask-Talisman
*   **Environment Configuration:** `.env` file support for flexible deployment
*   **Structured Logging:** Rotating log files with configurable levels
*   **Health Check Endpoint:** `/health` for monitoring and load balancers
*   **Systemd Integration:** Automatic start/stop/restart with crash recovery
*   **Cloudflare Tunnel:** Secure access without port-forwarding or public IP

---

## Quick Start (Development)

### Prerequisites

*   Python 3.9+
*   pip and virtualenv

### Installation

1.  **Clone and setup:**
    ```bash
    git clone https://github.com/yourusername/BeeHiveTracker.git
    cd BeeHiveTracker
    source bin/activate  # Activate existing venv
    pip install -r requirements.txt
    ```

2.  **Configure environment:**
    ```bash
    cp .env.example .env
    # Edit .env for development settings (DEBUG=True is default)
    ```

3.  **Setup admin user:**
    ```bash
    cp default_user.example.txt default_user.txt
    nano default_user.txt  # Set USERNAME and PASSWORD
    python setup_user.py
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```
    
    Access at `http://127.0.0.1:5000`

---

## Production Deployment

**For production deployment on a server with Gunicorn, Systemd, and optional Cloudflare Tunnel:**

📘 **See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step instructions**

📋 **Local Production Setup:** See [.github/PRODUCTION_SETUP.md](.github/PRODUCTION_SETUP.md) for locally-managed files

Quick overview:
1. Clone repo and install dependencies: `pip install -r requirements.txt`
2. Configure `.env` with production settings (`DEBUG=False`, `SESSION_COOKIE_SECURE=True`)
3. Setup admin user: `python setup_user.py`
4. Install systemd service: `sudo cp beehivetracker.service /etc/systemd/system/` (local file, not in repo)
5. Start service: `sudo systemctl start beehivetracker`
6. (Optional) Setup Cloudflare Tunnel for secure remote access

**Important:** Production-specific files (`.env`, `beehivetracker.service`, credentials, databases, logs) are kept locally and NOT committed to the repository for security.

---

## Project Structure

The project is organized as follows:

| File/Folder | Description |
|---|---|
| `app.py` | The main Flask application file containing all routes and core logic. |
| `models.py` | Defines the database models (`BeeColony`, `Inspection`, `InspectionImage`) using SQLAlchemy. |
| `forms.py` | Defines the data entry forms using Flask-WTF (`BeeColonyForm`, `InspectionForm`, `BatchInspectionForm`). |
| `upload_utils.py` | Contains utility functions for handling inspection image uploads and deletion. |
| `templates/` | Contains all HTML templates for rendering the user interface. |
| `static/` | Contains static assets like CSS (`styles.css`), JavaScript, and images. |
| `var/` | Contains variable data, such as the SQLite database and uploaded files. |

### Templates

The `templates/` directory includes the following HTML files:

*   `base.html`: The main layout template that other templates extend.
*   `index.html`: The application's home page showing all colonies in card view.
*   `voelker_liste.html`: Renders the list of all bee colonies.
*   `volk_detail.html`: Displays the detailed view of a single colony with all inspections.
*   `volk_form.html`: Provides the form for creating or editing a colony (with queen color/number).
*   `inspektionen_liste.html`: Renders the list of all inspections grouped by date with multi-select delete.
*   `inspektion_detail.html`: Displays the detailed view of a single inspection with all ratings and images.
*   `inspektion_form.html`: Provides the form for creating or editing an inspection with star ratings.
*   `batch_inspektion_form.html`: A specialized form for creating inspections for multiple colonies at once.

### Database Models

**BeeColony:**
*   `name`, `location`, `status` (stark/mittel/schwach)
*   `queen_birth`, `queen_color`, `queen_number`
*   Relationship: `inspections` (one-to-many with cascade delete)

**Inspection:**
*   `colony_id`, `date`, `notes`, `varroa_check`
*   Ratings (1-5 stars): `volksstaerke`, `sanftmut`, `vitalitaet`, `brut`
*   Frame counts: `mittelwaende`, `brutwaben`, `futterwaben`
*   Booleans: `queen_seen`, `drohnenbrut_geschnitten`
*   `honey_yield` (kg)
*   Relationship: `images` (one-to-many with cascade delete)

**InspectionImage:**
*   `inspection_id`, `filename`, `uploaded_at`
