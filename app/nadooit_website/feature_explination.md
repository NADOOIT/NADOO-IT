# NADOOIT Website

## Feature explination

The nadooit website is a website that is used to show information about nadooit.
Visitors learn about nadooit and how it works.

They only need to scroll down the page to see all the features.

They can also contact us and ask questions or directly register for a free consultation / make an appointment.

What is special is that it is not a static website, but a dynamic website that is build for each visitor.
Every time a visitor visits the website, the website is build for that visitor.

So even if the same visitor visits the website multiple times, the website will be different each time.

The goal of this mechanic is to make the website more personal and to make the visitor feel more welcome.
Also it automatically shows the visitor the features that are most interesting for him.
This is done by using machine learning to predict which features are most interesting for the visitor.
The final goal is to make visitors make an appointment with us
.
Eventually this mechanic should lead to everyone that visits to make an appointement.

## How it works

When a visitor visits nadooit.de a new session is started and the visitor is greeted with a landing page.
At the same time a timer is started on the server to keep track of how long the visitor is on the website.
This timer each second sends a signal to the server saying "I am still here".
This way it is possible to track how long the visitor spend on the webpage.
Longer time indecates that the visitor wanted to read more.
The final goal is to make the visitor spend as much time as possible on the website
but also as little time as possible until the visitor makes an appointment.

All landingpages start with an short expliantion of how the page works.
After that a question about the visitor is shown with a row of buttons that have the answers as lables.

Possible questions are:
Who the visitor might be: As options Copmany owner, a freelancer, developer, student, teacher, school kid.
What they might be looking for: As options: A job, a new project, a new client, a new employee, a new partner, a new investor, a new mentor.
...

After the visitor has answered the question or questions, the first section of the website is loaded.

For each answer to a question there are 5 different versions of the section that will be loaded.
There is a big list of possible sections.
All versions compete with each other to be the best version.

After the 5 visitors have left the website, which is detected by the timer, the 5 versions of the website are compared.
The version that has the highest score wins.
The next 5 versions of the website are build based on the winning version.
Important is that there are always at least 2 new version of the website being tested as long as the website does not have a high score or the score is falling.
This way new versions of the website are always tested and the website is always improving.

The score of a version is calculated by the following factors:

- How long the visitor spend on the website
- How many times the visitor clicked on a button
- How many times the visitor clicked on a link
- How many times the visitor scrolled down the page
- How many times the visitor scrolled up the page
- How many times the visitor scrolled to the bottom of the page
- How many times the visitor scrolled to the top of the page

- If the visitor made an appointment or not. Getting the visitor to make the appointment gets the most points.

Also the algorithem takes into account the time of day and the day of the week.
During the specific times of the day and days of the week the website should be different.
For example during the week the website should be more business oriented and during the weekend it should be more fun oriented.
All of this is done automatically by the algorithem and not by a human.

## Technology used

- htmx
- Bootstrap

## TodoList

- Create a url for getting the next section for a session
- Create a view that renders the next section for a session
- A service function that returns the next section for a session
- A service function that calculates the score of a section
- A service function that returns the best section for a session

- A model that stores the session data
- A model that stores the section data
- A model that stores the section_order data

## Current Todo

### urls.py

    /get_next_section/<session_id>/

### views.py

    get_next_section(request, session_id)

### services.py

    get_next_section(session_id)

    calculate_section_score(section_id, session_id)

    get_best_section(session_id)

### models.py

    Session
        session_id
        session_start_time
        session_end_time
        session_score
        session_duration
        session_section_order
    
    Section
        section_id
        section_name
        section_html
        section_score
        section_order
    
    SectionOrder
        section_order_id
        section_order_section_id
        section_order_session_id
        section_order_score
        section_order_order

### templates

    base.html
    landing_page.html
    section.html
