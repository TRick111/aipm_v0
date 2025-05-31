## Overview

Implement the backend and frontend logic for handling the notificationReadStatus table, which manages the many-to-many relationship between store groups and notifications. This table also tracks whether a notification has been archived (i.e., hidden) for a specific store group.

## Requirements

-   The notificationReadStatus table should represent the relationship between store groups and notifications, and include a flag (e.g., `archived`) to indicate whether a notification has been archived for a particular store group.
-   First make some changes to the database schema.
    -   In the Notification table, The type, priority, and isglobal properties aren't needed. Delete them.
    -   In the Notification table, Add a show property which is a boolean.
    -   Change the table name of notificationreadstatus into ArchivedNotification. Remove the readAt property.
-   When a store manager accesses the store group's dashboard (http://localhost:3000/manager/1), notifications should be displayed according to the following logic:
    1. The notification's `show` flag is true.
    2. The current date is within the notification's `startDate` and `endDate` range.
    3. The ArchivedNotification table is checked for a record matching the current store group and notification.
        - If no record exists, the notification is considered active and should be shown.
        - If a record exists, the notification should not be shown.
-   The default behavior is to show all notifications that are active (per the above logic) and not archived for the current store group.
-   Provide API endpoints to:
    -   Mark a notification as archived for a store group (i.e., create or update a ArchivedNotification record).
-   Update the frontend to:
    -   Show all Notification that needs to be shown as above.
    -   Remove dummy data from code
    -   Allow store managers to archive notifications from their dashboard. The button already exists.

## Major Steps

1. Design or update the `ArchivedNotification` table/model to include the necessary fields (e.g., `storeGroupId`, `notificationId`, `archived`).
2. Implement API endpoints for archiving/unarchiving notifications for a store group.
3. Update the notification fetching logic to apply the display rules described above.
4. Update the frontend to allow archiving/unarchiving and to hide archived notifications.

## References

-   Database schema documents and `schema.prisma`
-   Existing notification and store group implementations

## Open Questions

-   If you have any questions about the logic or requirements, please ask before proceeding.

## Submission

-   Test your code before submitting a pull request.
