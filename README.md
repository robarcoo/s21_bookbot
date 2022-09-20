# Weeklython
# Description
Due to upcoming anniversary of School 21, administration decided to organize a hackathon for students to create a telegram bot for school's needs in a timespan of a week (15-22 August). Participants were presented with 4 options:
1. Bookbot. Bot books inventory (like books, table games, sport equipment) or school spaces like meeting rooms or kitchens. 
2. Votebot. Bot creates polls that can have different types of options to vote for.
3. Passbot. Bot makes a request for inviting a guest to school. 
4. Checkinbot. Bot checks if user is present on school event. 

Winners in each category will get a chance to finish their bots and integrate into school's system. 
# Our team
- robarcoo (brittnyc) - Teamlead, Python developer.
- donnlind (leggeedi) - Analytics.
- julietta (williamc) - Frontend.
- margretr (meadowse) - Database Administrator. 
---
# Development
- Project
- Prototype
- Presentation
- Bugs
- Not implemented

## Project
This is our first big project and first serious practice with making a Telegram bot. Certain mistakes were made and I would like discuss it alongside with our development way. I'm writing this as an example for anyone who happens to stumble upon this project, merely as a beginning of our portfolios and a chance to reflect on own actions. 

Our team decided to implement the first option as we personally felt a need in a bot like this, additional features were even added (like peer raiting system, school zone map, access to logs for adm). There are two types of menu:
1. Administration panel
2. Student/Abiturient panel

### ADM 
ADM can book (meeting rooms, table games, books, inventory and kitchens), change zones, see reports, add inventory, check own bookings and cancel a booking (own or someone else's). The main concept is ADM unlike other users can book more spaces (kitchens are not available for students and abiturients), can see reports, see and change peer's raiting (if raiting becomes low then it's not possible to book something with a high value (ex: expensive book or game) and with negative one you are completely unallowed to book anything). 

### Student/Abiturient
Abiturient participates in an intensive school program for 26 days upon which will be decided if this person will continue to study in the school or not. They have less variety of choice (can't book anything except meeting rooms) as abiturients are still not students of the school.

Students are the ones who have passed the intensive program and will be studying in school for the next 1.5-3 years. It should be mentioned that students and abiturients are not allowed to interact, they can't book the same meeting rooms and study next to each other (in order to prevent cheating). That's why we decided to add a zones feature where everyone can look which meeting rooms are allowed for them. As these zones change every time (students can allowed on the 2nd floor and next intensive program they will be forced to move to the 3rd floor) ADM can manually change them and even make meeting rooms unavailable for both parties.

donnlind (leggeedi) through discussions and brainstorming gathered all the informations and wrote texts for analytics, tables and drew mindmaps. julietta (williamc) made a good Figma layout that we tried to stick to during next steps for development.

## Prototype
We were given four days to make a working prototype. Some of functions were finished after these 4 days as we were lacking some functionality needed by requirements. Due to our little experience half of the time was wasted on learning how to pass data from one function to another in Telegram bot and understanding how we are supposed to organize our project. I figured it out but couldn't implement it in practice, so I was left with 1000+ lines of code and bad architecture that needed to be rewritten. Because of this we tried to separate functions but failed and managed to only get database functions in its own file (thanks margretr (meadowse) for that). Later I tried to do something with that but I ran into a circular import problem (sign of a bad code architecture), I tried to fix that but it for some reason code couldn't reach functions in another file but wouldn't say anything about it, so bot just didn't work properly and I gave up. If I started project from beginning, I would write all functions separately beforehand.

julietta (williamc) implemented the web page where you can see school map (only for Kazan as others couldn't provide their maps for us) and list of books available for booking (we didn't want to throw this big list as a single message by a bot and at the same time couldn't implement multiple page list because of the said lack of experience and button limitation). 

margretr (meadowse) performed part with database functions. The database has 4 tables: 
- Bookings. It has user's id, start and end of a booking and object id. 
- Objects. It has a list of all objects and info about them that will be shown to user.
- Reports. All reports that were send by students and abiturients. Peers can see their own reports and their status (checked by ADM or not) while ADM see all active (not checked) reports. 
- Users. List of users and info about them (role, campus, status (if person was fired or expelled) and raiting).

## Presentation

Thanks to julietta (williamc) and donnlind (leggeedi) for working on this part, they did a good job. Unfortunately, the public hasn't seen our work as we didn't get to Final. Due to lack of communication we weren't prepared for experts to check our projects the way they did (task didn't state how log in should be implemented and ADM didn't say when we have to start deploying our bots). I think that we could have competed with some finalists.

## Bugs

- Time check for booking wasn't tested properly, so sometimes it doesn't accept valid values.
- Sometimes bot can get stuck and it can be fixed only with turning bot off and back on.

## Not implemented

- Abiturients shouldn't be able book meeting rooms available for students and vice versa.
- Objects must have a different value status (based on how rare and expensive it is).
- Bot has to check if user's raiting is enough to book an object (currently it checks only if user has a negative raiting).
- Different type of authorization in bot with mail.
- Add photos to objects (column for it is present in the database but empty).
- Add maps for other campuses.
- Add all objects to database.
- We couldn't deploy our bot anywhere because any free options weren't available (and without use of a card). 
