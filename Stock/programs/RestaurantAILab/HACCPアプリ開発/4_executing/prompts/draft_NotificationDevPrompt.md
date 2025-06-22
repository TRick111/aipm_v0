# AI Coder Instruction Draft: Notification API Implementation

## Overview

Please develop backend API routes for managing Notification objects and integrate them with the existing frontend application. The goal is to replace any dummy notification data with data fetched from the database, ensuring full CRUD (Create, Read, Update, Delete) functionality for notifications.

## Requirements

-   Develop API routes for notification management, following the database specifications outlined in the provided documents and schema (see `schema.prisma`).
-   Integrate the new API routes with the existing frontend components. Do not add any new pages to the frontend; only connect and enhance the current notification-related UI.
-   On the relevant notification management page, ensure that:
    -   The "Add Notification" button triggers a form for creating a new notification. (http://localhost:3000/admin/notifications)
    -   The notification list displays all relevant fields (e.g., title, message, createdAt, etc.). (http://localhost:3000/admin/notifications)
    -   Each notification item is clickable. Clicking an item opens the same form, pre-populated for editing.
    -   Users can edit and delete notifications from the list.
    -   Currently, the Edit Notification and Add Notification card shows an area where you can select which groups to show the notification to. Delete this area since the notification should be shown to all the store groups.
    -   There's a toggle in the edit or add notification card. Next to the toggle, change the displayed text on the following condition. Set the default toggle to true. If the toggle is set to false, show that the notification won't be displayed because the toggle is turned off. If the toggle is turned on and today's date is within the start date and the end date, show next to the toggle that the notification will be shown. And stop shown when the end date comes. If the toggle is true, but the date is out of the start date and end date, show that the notification won't be shown because the date is out of displaying date range. It's a little bit different than the way to the toggle. It's not an even test.
-   Follow the established implementation patterns for similar features (e.g., stores, equipment) in both the frontend and API.
-   Below are out of scope
    -   Displaying Notifications on the Manager app

## Major Steps

1. Study the existing implementation of similar features (e.g., stores, equipment) to understand the code structure and patterns.
2. Implement the necessary API endpoints for creating, reading, updating, and deleting notifications.
3. Modify the frontend components to fetch notification data from the new API endpoints instead of using dummy data.
4. Implement the notification editing and deletion functionality as described above.
5. Ensure the notification list displays all required fields.

## References

-   Documents and memos describing the API and database specifications
-   `schema.prisma` file for database schema configuration
-   Existing implementation of stores, equipment, and other similar features in both the frontend and API

## Open Questions

-   If anything is unclear, please ask before proceeding.

## Submission

-   Test your code before submitting a pull request.

Add Sample data once everything is complete.
