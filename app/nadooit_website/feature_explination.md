# Feature Explanation

## Overview

This website is designed to test the effectiveness of different sections and user interactions in an experimental setting. It allows the website owner to create multiple sections, each with different content, and track user interaction with those sections. The website then presents the sections to users in an experimental setting, tracking their interactions and generating statistics to help the website owner determine which sections are most effective.

## Models

### Section

This model represents a section of the website, which contains a unique identifier, a title, content, and a score. The score indicates the section's effectiveness based on user interaction.

### Session

This model represents a user session, which contains a unique identifier, a list of sections (in order), and a total interaction time. The total interaction time is the sum of interaction times for all sections in the session.

### SessionSignal

This model represents a signal sent by the user when interacting with a section. It contains a unique identifier, the session it belongs to, the section it is related to, and the signal type (mouseenter_once, mouseleave, revealed, or end_of_session_sections).

## Views

### index

Renders the starting page of the website.

### new_index

Renders a new session for the user, with the first section of the session.

### impressum

Renders the impressum page of the website.

### datenschutz

Renders the datenschutz page of the website.

### statistics

Renders the statistics page of the website, showing the effectiveness of each section based on user interaction.

### signal

Handles the signals sent by the client for different interaction types (mouseenter_once, mouseleave, revealed, and end_of_session_sections). It first checks if the session ID is valid. If it's valid, the function creates a session signal and updates the corresponding session.

For the mouseleave signal, the function also updates the total_interaction_time field for the corresponding session based on the interaction time received in the request body.

### end_of_session_sections

This view is triggered when the user reaches the end of the session sections. If the request is valid, it calls the get_next_best_section function to retrieve the next best section based on the user's category and the section scores. If a next section is found, it renders the section, otherwise, it returns an HTTP response indicating no more sections are available.

### get_next_section

This view retrieves the next section in the order specified by the session's section order. If the request is valid and a next section is found, it renders the section, otherwise, it returns an HTTP response indicating no more sections are available.

### session_is_active_signal

This view is called when a user sends a signal to check if their session is still active. If the session is active, it returns an HTTP response with a status of 200; otherwise, it returns an HTTP response with a status of 404.

## Services

### categorize_user

This function takes a session ID and categorizes the user as "fast" or "slow" based on their average interaction time. The average interaction time is calculated by dividing the total_interaction_time by the number of sections in the session.

### get_next_best_section

This function takes a session ID and the current section ID as input and returns the next best section based on the user category (fast or slow) and section scores. The implementation for the experimental group is missing and needs to be added.

### create_session_signal_for_session_id

This function creates a session signal for a given session ID, section ID, and signal type. It also updates the corresponding session and the section score based on the signal type.