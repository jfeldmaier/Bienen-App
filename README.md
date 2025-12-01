# Bienen-App 🐝

A simple yet powerful web application to help beekeepers manage their bee colonies and track inspections with ease.

---

## Features

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

---

## Getting Started

Follow these instructions to get the application running on your local machine.

### Prerequisites

Make sure you have Python 3 and `pip` installed.

### Installation & Setup

1.  **Clone the repository and navigate into the project directory.**

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```
    
    The database will be created automatically on first run.

The application will be available at `http://127.0.0.1:5000`.

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
